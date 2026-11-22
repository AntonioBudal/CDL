"""Catálogo de procedência (F-DI-13.03, spec ``specs/004-catalogo-de-procedencia``).

SQLite local + armazenamento por conteúdo. Situações de uso da estratégia de dados v2:
``APPROVED``, ``EXPERIMENT_ONLY``, ``PENDING_REVIEW`` (só metadados), ``REJECTED`` (apagado,
bloqueado), ``BLOCKED``. Ciclos de treino com a lista exata de itens; rejeição posterior
contamina o ciclo.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from . import images

STATUSES = ("APPROVED", "EXPERIMENT_ONLY", "PENDING_REVIEW", "REJECTED", "BLOCKED")
WITH_FILES = ("APPROVED", "EXPERIMENT_ONLY")
RUN_ALLOWED = {"produto": {"APPROVED"}, "experimento": {"APPROVED", "EXPERIMENT_ONLY"}}
GB = 1024**3
DEFAULT_BUDGETS = {
    "linhas": 45 * GB,
    "originais": 30 * GB,
    "modelos": 10 * GB,
    "trabalho": 10 * GB,
    "termos": 1 * GB,
    "catalogo": 1 * GB,
}
TOTAL_BUDGET = 100 * GB
SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY, name TEXT NOT NULL, url TEXT, license TEXT,
    conditions TEXT NOT NULL, status TEXT NOT NULL, access TEXT NOT NULL, terms_sha256 TEXT,
    terms_url TEXT, terms_saved_at TEXT,
    notes TEXT, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS files (
    sha256 TEXT PRIMARY KEY, kind TEXT NOT NULL, bytes INTEGER NOT NULL, format TEXT,
    width INTEGER, height INTEGER, phash TEXT, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS items (
    item_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(source_id),
    native_id TEXT NOT NULL, kind TEXT NOT NULL, source_url TEXT, creator TEXT, rights_holder TEXT,
    license TEXT, conditions TEXT NOT NULL, status TEXT NOT NULL, status_reason TEXT,
    language TEXT, era TEXT, script TEXT, writer TEXT, split TEXT, transcription_type TEXT,
    text TEXT,
    sha256 TEXT, phash TEXT, near_duplicate_of TEXT, acquired_at TEXT NOT NULL, acquired_via TEXT,
    extra TEXT
);
CREATE INDEX IF NOT EXISTS items_source ON items(source_id, status);
CREATE INDEX IF NOT EXISTS items_sha ON items(sha256);
CREATE TABLE IF NOT EXISTS item_files (
    item_id TEXT NOT NULL REFERENCES items(item_id), sha256 TEXT NOT NULL, role TEXT NOT NULL,
    PRIMARY KEY (item_id, sha256)
);
CREATE INDEX IF NOT EXISTS item_files_sha ON item_files(sha256);
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT, scope TEXT NOT NULL, target TEXT NOT NULL,
    from_status TEXT, to_status TEXT NOT NULL, reason TEXT NOT NULL, evidence TEXT, items INTEGER,
    reviewed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS blocklist (
    kind TEXT NOT NULL, value TEXT NOT NULL, reason TEXT, added_at TEXT NOT NULL,
    PRIMARY KEY (kind, value)
);
CREATE TABLE IF NOT EXISTS training_runs (
    run_id TEXT PRIMARY KEY, purpose TEXT NOT NULL, recipe TEXT, code_commit TEXT, seed INTEGER,
    notes TEXT, created_at TEXT NOT NULL, tainted INTEGER NOT NULL DEFAULT 0, tainted_reason TEXT
);
CREATE TABLE IF NOT EXISTS run_items (
    run_id TEXT NOT NULL REFERENCES training_runs(run_id), item_id TEXT NOT NULL, sha256 TEXT,
    status TEXT NOT NULL, license TEXT, PRIMARY KEY (run_id, item_id)
);
CREATE INDEX IF NOT EXISTS run_items_item ON run_items(item_id);
"""


class CatalogError(Exception):
    """Operação inválida no catálogo."""


class BudgetExceededError(CatalogError):
    """O teto de espaço seria ultrapassado."""


@dataclass
class IngestResult:
    item_id: str
    created: bool
    stored: bool
    sha256: str | None
    reason: str | None = None
    near_duplicate_of: str | None = None


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_root() -> Path:
    return Path(os.environ.get("LEITORUM_DI_DATA") or "D:/Leitorum-DI")


class Catalog:
    def __init__(self, root: Path | str | None = None, budgets: dict[str, int] | None = None):
        self.root = Path(root) if root else default_root()
        self.objects = self.root / "objetos"
        (self.root / "catalogo").mkdir(parents=True, exist_ok=True)
        self.objects.mkdir(parents=True, exist_ok=True)
        self.budgets = {**DEFAULT_BUDGETS, **(budgets or {})}
        self.db = sqlite3.connect(self.root / "catalogo" / "catalogo.sqlite")
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript(SCHEMA)
        if not self.db.execute("SELECT 1 FROM schema_version").fetchone():
            self.db.execute("INSERT INTO schema_version VALUES (?)", (SCHEMA_VERSION,))
        self.db.commit()
        self._pending_writes = 0
        self._kind_totals = {
            row[0]: row[1]
            for row in self.db.execute("SELECT kind, SUM(bytes) FROM files GROUP BY kind")
        }

    BATCH = 500  # itens ingeridos por transação (um commit por item é lento num HD)

    def flush(self) -> None:
        self.db.commit()
        self._pending_writes = 0

    def close(self) -> None:
        self.flush()
        self.db.close()

    # ------------------------------------------------------------ arquivos

    def file_path(self, sha256: str) -> Path:
        return self.objects / sha256[:2] / sha256

    def _kind_bytes(self, kind: str) -> int:
        return self._kind_totals.get(kind, 0)

    def _store(self, data: bytes, kind: str, fmt: str, width=None, height=None, phash=None) -> str:
        sha = hashlib.sha256(data).hexdigest()
        if self.db.execute("SELECT 1 FROM files WHERE sha256 = ?", (sha,)).fetchone():
            return sha
        budget = self.budgets.get(kind, TOTAL_BUDGET)
        total = sum(self._kind_totals.values())
        if self._kind_bytes(kind) + len(data) > budget or total + len(data) > TOTAL_BUDGET:
            raise BudgetExceededError(f"teto de {kind} ({budget} bytes) ou total atingido")
        path = self.file_path(sha)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_bytes(data)
        os.replace(temporary, path)
        self.db.execute(
            "INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (sha, kind, len(data), fmt, width, height, phash, _now()),
        )
        self._kind_totals[kind] = self._kind_bytes(kind) + len(data)
        return sha

    # ------------------------------------------------------------ fontes

    def add_source(
        self,
        source_id,
        *,
        name,
        url,
        license,
        conditions,
        status,
        access,
        terms: bytes | None = None,
        terms_url: str | None = None,
        notes: str | None = None,
    ):
        if status not in STATUSES:
            raise CatalogError(f"situação desconhecida: {status}")
        terms_sha = self._store(terms, "termos", "html") if terms else None
        existing = self.source(source_id, required=False)
        values = (
            name,
            url,
            license,
            ",".join(conditions),
            status,
            access,
            terms_sha or (existing or {}).get("terms_sha256"),
            terms_url,
            _now() if terms else (existing or {}).get("terms_saved_at"),
            notes,
        )
        if existing:
            self.db.execute(
                "UPDATE sources SET name=?, url=?, license=?, conditions=?, status=?, access=?,"
                " terms_sha256=?, terms_url=?, terms_saved_at=?, notes=? WHERE source_id=?",
                (*values, source_id),
            )
        else:
            self.db.execute(
                "INSERT INTO sources VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (source_id, *values, _now()),
            )
        self.db.commit()

    def source(self, source_id: str, required: bool = True) -> dict | None:
        row = self.db.execute("SELECT * FROM sources WHERE source_id = ?", (source_id,)).fetchone()
        if row is None and required:
            raise CatalogError(f"fonte desconhecida: {source_id}")
        return dict(row) if row else None

    def sources(self) -> list[dict]:
        return [dict(r) for r in self.db.execute("SELECT * FROM sources ORDER BY source_id")]

    # ------------------------------------------------------------ bloqueio

    def is_blocked(self, *, sha256=None, url=None, item_id=None) -> bool:
        for kind, value in (("sha256", sha256), ("url", url), ("item_id", item_id)):
            if (
                value
                and self.db.execute(
                    "SELECT 1 FROM blocklist WHERE kind = ? AND value = ?", (kind, value)
                ).fetchone()
            ):
                return True
        return False

    def _block(self, kind: str, value: str | None, reason: str) -> None:
        if value:
            self.db.execute(
                "INSERT OR IGNORE INTO blocklist VALUES (?, ?, ?, ?)", (kind, value, reason, _now())
            )

    # ------------------------------------------------------------ ingestão

    def _pending_reason(self, source: dict) -> str:
        return "sem_licenca" if not source["license"] else "licenca_a_confirmar"

    def _ingest(
        self,
        source_id,
        native_id,
        kind,
        image,
        prepare,
        *,
        text=None,
        license=None,
        conditions=None,
        status=None,
        url=None,
        **meta,
    ) -> IngestResult:
        source = self.source(source_id)
        item_id = f"{source_id}:{native_id}"
        existing = self.item(item_id, required=False)
        if existing:
            return IngestResult(
                item_id,
                False,
                bool(existing["sha256"]),
                existing["sha256"],
                "ja_existe",
                existing["near_duplicate_of"],
            )
        if self.is_blocked(item_id=item_id, url=url):
            return IngestResult(item_id, False, False, None, "bloqueado")
        status = status or source["status"]
        if status in ("REJECTED", "BLOCKED"):
            return IngestResult(item_id, False, False, None, "fonte_bloqueada")
        sha = phash = near = None
        stored = False
        if image is not None and status in WITH_FILES:
            data, fmt, width, height, phash = prepare(image)
            sha_candidate = hashlib.sha256(data).hexdigest()
            if self.is_blocked(sha256=sha_candidate):
                return IngestResult(item_id, False, False, None, "bloqueado")
            if phash:
                for other in self.db.execute(
                    "SELECT item_id, phash FROM items WHERE kind = ? AND phash IS NOT NULL", (kind,)
                ):
                    if images.hamming(other["phash"], phash) <= images.PHASH_NEAR:
                        near = other["item_id"]
                        break
            sha = self._store(
                data, "linhas" if kind == "line" else "originais", fmt, width, height, phash
            )
            stored = True
        reason = self._pending_reason(source) if status == "PENDING_REVIEW" else None
        self.db.execute(
            "INSERT INTO items (item_id, source_id, native_id, kind, source_url, creator,"
            " rights_holder, license, conditions, status, status_reason, language, era, script,"
            " writer, split, transcription_type, text, sha256, phash, near_duplicate_of,"
            " acquired_at, acquired_via, extra)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                item_id,
                source_id,
                str(native_id),
                kind,
                url,
                meta.get("creator"),
                meta.get("rights_holder"),
                license or source["license"],
                ",".join(conditions) if conditions is not None else source["conditions"],
                status,
                reason,
                meta.get("language"),
                meta.get("era"),
                meta.get("script"),
                meta.get("writer"),
                meta.get("split"),
                meta.get("transcription_type"),
                text,
                sha,
                phash,
                near,
                _now(),
                meta.get("acquired_via"),
                json.dumps(meta.get("extra"), ensure_ascii=False) if meta.get("extra") else None,
            ),
        )
        if sha:
            self.db.execute(
                "INSERT OR IGNORE INTO item_files VALUES (?, ?, ?)",
                (item_id, sha, "linha" if kind == "line" else "pagina"),
            )
        self._pending_writes += 1
        if self._pending_writes >= self.BATCH:
            self.flush()
        return IngestResult(item_id, True, stored, sha, reason, near)

    def ingest_line(
        self, source_id, native_id, *, image: bytes | None, text, **meta
    ) -> IngestResult:
        def prepare(data):
            out, width, height = images.to_line_format(data)
            return out, images.LINE_FORMAT, width, height, None

        meta.setdefault("transcription_type", "line")
        return self._ingest(source_id, native_id, "line", image, prepare, text=text, **meta)

    def ingest_page(self, source_id, native_id, *, image: bytes | None, text=None, **meta):
        def prepare(data):
            fmt, width, height = images.describe(data)
            return data, fmt, width, height, images.dhash(data)

        return self._ingest(source_id, native_id, "page", image, prepare, text=text, **meta)

    # ------------------------------------------------------------ itens

    def item(self, item_id: str, required: bool = True) -> dict | None:
        row = self.db.execute("SELECT * FROM items WHERE item_id = ?", (item_id,)).fetchone()
        if row is None and required:
            raise CatalogError(f"item desconhecido: {item_id}")
        return dict(row) if row else None

    def counts(self) -> dict:
        q = self.db.execute
        return {
            "sources": q("SELECT COUNT(*) FROM sources").fetchone()[0],
            "items": q("SELECT COUNT(*) FROM items").fetchone()[0],
            "files": q("SELECT COUNT(*) FROM files WHERE kind != 'termos'").fetchone()[0],
            "runs": q("SELECT COUNT(*) FROM training_runs").fetchone()[0],
        }

    def needs_download(self) -> list[str]:
        rows = self.db.execute(
            "SELECT item_id FROM items WHERE sha256 IS NULL AND status IN (?, ?) ORDER BY item_id",
            WITH_FILES,
        )
        return [r[0] for r in rows]

    def pending(self) -> list[dict]:
        rows = self.db.execute(
            "SELECT source_id, status_reason AS reason, COUNT(*) AS items FROM items"
            " WHERE status = 'PENDING_REVIEW' GROUP BY source_id, status_reason"
            " ORDER BY source_id, status_reason"
        )
        return [dict(r) for r in rows]

    # ------------------------------------------------------------ revisão e remoção

    def _purge(self, item: dict, reason: str) -> None:
        item_id = item["item_id"]
        for row in self.db.execute(
            "SELECT sha256 FROM item_files WHERE item_id = ?", (item_id,)
        ).fetchall():
            sha = row[0]
            self.db.execute(
                "DELETE FROM item_files WHERE item_id = ? AND sha256 = ?", (item_id, sha)
            )
            if not self.db.execute("SELECT 1 FROM item_files WHERE sha256 = ?", (sha,)).fetchone():
                path = self.file_path(sha)
                if path.exists():
                    path.unlink()
                row_bytes = self.db.execute(
                    "SELECT kind, bytes FROM files WHERE sha256 = ?", (sha,)
                ).fetchone()
                if row_bytes:
                    self._kind_totals[row_bytes[0]] -= row_bytes[1]
                self.db.execute("DELETE FROM files WHERE sha256 = ?", (sha,))
                self._block("sha256", sha, reason)
        self._block("item_id", item_id, reason)
        self._block("url", item["source_url"], reason)
        self.db.execute(
            "UPDATE items SET status = 'REJECTED', status_reason = ?, sha256 = NULL, text = NULL"
            " WHERE item_id = ?",
            (reason, item_id),
        )
        self.db.execute(
            "UPDATE training_runs SET tainted = 1, tainted_reason ="
            " COALESCE(tainted_reason || '; ', '') || ? WHERE run_id IN"
            " (SELECT run_id FROM run_items WHERE item_id = ?)",
            (f"{item_id} rejeitado ({reason})", item_id),
        )

    def review(
        self, scope: str, target: str, to_status: str, *, reason: str, evidence: str | None = None
    ) -> int:
        if to_status not in STATUSES:
            raise CatalogError(f"situação desconhecida: {to_status}")
        if scope == "source":
            source = self.source(target)
            items = [
                dict(r)
                for r in self.db.execute(
                    "SELECT * FROM items WHERE source_id = ? AND status != 'REJECTED'", (target,)
                )
            ]
            from_status = source["status"]
            self.db.execute(
                "UPDATE sources SET status = ? WHERE source_id = ?", (to_status, target)
            )
        elif scope == "item":
            item = self.item(target)
            items, from_status = [item], item["status"]
        else:
            raise CatalogError(f"escopo desconhecido: {scope}")
        for item in items:
            if to_status == "REJECTED":
                self._purge(item, reason)
            else:
                self.db.execute(
                    "UPDATE items SET status = ?, status_reason = ? WHERE item_id = ?",
                    (to_status, reason if to_status == "PENDING_REVIEW" else None, item["item_id"]),
                )
        self.db.execute(
            "INSERT INTO reviews (scope, target, from_status, to_status, reason, evidence, items,"
            " reviewed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (scope, target, from_status, to_status, reason, evidence, len(items), _now()),
        )
        self.db.commit()
        return len(items)

    # ------------------------------------------------------------ ciclos de treino

    def start_run(
        self,
        purpose: str,
        *,
        sources: list[str],
        splits: list[str] | None = None,
        recipe: str,
        commit: str,
        seed: int,
        notes: str | None = None,
    ) -> str:
        if purpose not in RUN_ALLOWED:
            raise CatalogError(f"finalidade desconhecida: {purpose}")
        allowed = RUN_ALLOWED[purpose]
        marks = ",".join("?" * len(sources))
        query = f"SELECT * FROM items WHERE source_id IN ({marks}) AND sha256 IS NOT NULL"
        params: list = list(sources)
        if splits:
            query += f" AND split IN ({','.join('?' * len(splits))})"
            params += splits
        rows = [dict(r) for r in self.db.execute(query + " ORDER BY item_id", params)]
        bad = sorted({r["status"] for r in rows} - allowed)
        if bad:
            raise CatalogError(f"ciclo de {purpose} não aceita itens {bad}")
        number = self.db.execute("SELECT COUNT(*) FROM training_runs").fetchone()[0] + 1
        run_id = f"run-{number:04d}-{datetime.now(UTC):%Y%m%d}"
        self.db.execute(
            "INSERT INTO training_runs (run_id, purpose, recipe, code_commit, seed, notes,"
            " created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, purpose, recipe, commit, seed, notes, _now()),
        )
        self.db.executemany(
            "INSERT INTO run_items VALUES (?, ?, ?, ?, ?)",
            [(run_id, r["item_id"], r["sha256"], r["status"], r["license"]) for r in rows],
        )
        self.db.commit()
        return run_id

    def run(self, run_id: str) -> dict:
        row = self.db.execute("SELECT * FROM training_runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            raise CatalogError(f"ciclo desconhecido: {run_id}")
        out = dict(row)
        out["tainted"] = bool(out["tainted"])
        return out

    def run_items(self, run_id: str) -> list[dict]:
        rows = self.db.execute(
            "SELECT item_id, sha256, status, license FROM run_items WHERE run_id = ?"
            " ORDER BY item_id",
            (run_id,),
        )
        return [dict(r) for r in rows]

    def check_promotion(self, run_id: str) -> tuple[bool, list[str]]:
        run = self.run(run_id)
        problems = []
        if run["tainted"]:
            problems.append(f"ciclo contaminado: {run['tainted_reason']}")
        for row in self.db.execute(
            "SELECT r.item_id, r.status AS at_run, i.status AS current FROM run_items r"
            " JOIN items i ON i.item_id = r.item_id WHERE r.run_id = ?",
            (run_id,),
        ):
            if row["at_run"] != "APPROVED":
                problems.append(f"{row['item_id']} era {row['at_run']} no ciclo")
            elif row["current"] != "APPROVED":
                problems.append(f"{row['item_id']} agora é {row['current']}")
        return (not problems, problems)

    def training_summary(self, run_id: str) -> dict:
        run = self.run(run_id)
        by_source: dict[str, dict] = defaultdict(lambda: {"items": 0, "licenses": set()})
        for row in self.db.execute(
            "SELECT i.source_id, r.license FROM run_items r JOIN items i ON i.item_id = r.item_id"
            " WHERE r.run_id = ?",
            (run_id,),
        ):
            entry = by_source[row["source_id"]]
            entry["items"] += 1
            entry["licenses"].add(row["license"] or "?")
        sources = []
        for source_id in sorted(by_source):
            source = self.source(source_id)
            sources.append(
                {
                    "source_id": source_id,
                    "name": source["name"],
                    "url": source["url"],
                    "licenses": sorted(by_source[source_id]["licenses"]),
                    "conditions": [c for c in source["conditions"].split(",") if c],
                    "items": by_source[source_id]["items"],
                }
            )
        return {
            "run_id": run_id,
            "purpose": run["purpose"],
            "created_at": run["created_at"],
            "tainted": run["tainted"],
            "items": sum(s["items"] for s in sources),
            "sources": sources,
            "attributions": [
                f"{s['name']} — {s['url']} ({', '.join(s['licenses'])})" for s in sources
            ],
        }

    # ------------------------------------------------------------ espaço e integridade

    def usage(self) -> list[dict]:
        rows = []
        for kind, budget in self.budgets.items():
            used = self._kind_bytes(kind)
            if kind == "catalogo":
                used = sum(
                    p.stat().st_size for p in (self.root / "catalogo").glob("*") if p.is_file()
                )
            rows.append({"kind": kind, "bytes": used, "budget": budget})
        rows.append(
            {"kind": "total", "bytes": sum(r["bytes"] for r in rows), "budget": TOTAL_BUDGET}
        )
        return rows

    def verify(self) -> list[str]:
        bad = []
        for row in self.db.execute("SELECT sha256 FROM files"):
            path = self.file_path(row[0])
            if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != row[0]:
                bad.append(row[0])
        return bad
