"""Leitura, validação e gravação das anotações ``di-annotation/1``.

Toda regra de integridade mora aqui (o navegador só edita): schema, ``$`` equilibrado, ``line_id``
estável e nunca reaproveitado, polígono dentro da imagem, foto com hash registrado pelo EXP-027,
versão (conflito entre abas), gravação atômica com a versão anterior em ``pNN.prev.json``.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
from datetime import UTC, datetime
from functools import cache
from pathlib import Path

from jsonschema import Draft202012Validator

from .paths import SCHEMA_FILE, Paths

SCHEMA_ID = "di-annotation/1"
PAGE_ID = re.compile(r"^p[0-9]{2,3}$")
LINE_ID = re.compile(r"^L([0-9]{3,})$")
SECONDS = ("boxes", "pass1", "pass2")
EDGE_TOLERANCE = 2.0  # px: arredondamento do arrasto na borda da foto


class NotFoundError(Exception):
    """Página inexistente ou identificador inválido."""


class BlockedError(Exception):
    """Foto sem hash conferido: não é comprovadamente a página registrada pelo EXP-027."""


class ConflictError(Exception):
    def __init__(self, current_version: int) -> None:
        super().__init__(f"versão atual {current_version}")
        self.current_version = current_version


class InvalidError(Exception):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


# ---------------------------------------------------------------- utilidades


@cache
def _validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _read_json(path: Path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(doc: dict) -> bytes:
    """JSON canônico do conteúdo, sem o próprio ``content_sha256``."""
    body = {key: value for key, value in doc.items() if key != "content_sha256"}
    return json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def content_hash(doc: dict) -> str:
    return hashlib.sha256(canonical(doc)).hexdigest()


def dollar_balanced(text: str) -> bool:
    """``$`` sem barra antes contam como delimitadores de fórmula; precisam vir aos pares."""
    return len(re.findall(r"(?<!\\)\$", text)) % 2 == 0


def line_number(line_id: str) -> int:
    match = LINE_ID.match(line_id)
    return int(match.group(1)) if match else -1


def format_line_id(number: int) -> str:
    return f"L{number:03d}"


# ---------------------------------------------------------------- páginas


def _check_page_id(page_id: str) -> None:
    if not isinstance(page_id, str) or not PAGE_ID.match(page_id):
        raise NotFoundError(page_id)


def _splits(paths: Paths) -> dict[str, str]:
    """Divisão de cada página: teste congelado, ``dev-val`` e ``dev-train`` (quando o EXP-028A
    tiver criado o manifesto de validação); antes disso, as de desenvolvimento ficam sem divisão."""
    out: dict[str, str] = {}
    test = _read_json(paths.splits / "test-manifest-v3.json") or _read_json(
        paths.splits / "test-manifest.json", {}
    )
    for pid in (test or {}).get("pages", {}):
        out[pid] = "test"
    dev_val = _read_json(paths.splits / "dev-val-manifest.json")
    if dev_val:
        for pid in dev_val.get("pages", {}):
            out.setdefault(pid, "dev-val")
    return out


def _index(paths: Paths) -> dict:
    return (_read_json(paths.index, {}) or {}).get("pages", {})


def _registered(paths: Paths) -> dict:
    return (_read_json(paths.registered, {}) or {}).get("pages", {})


@cache
def _cached_sha(path_str: str, mtime_ns: int, size: int) -> str:
    return file_sha256(Path(path_str))


def _work_hash_ok(paths: Paths, page_id: str, entry: dict) -> bool:
    image = paths.images / f"{page_id}.jpg"
    if not image.is_file():
        return False
    stat = image.stat()
    return _cached_sha(str(image), stat.st_mtime_ns, stat.st_size) == entry.get("work_sha256")


def hash_ok(paths: Paths, page_id: str) -> bool:
    entry = _index(paths).get(page_id)
    registered = _registered(paths).get(page_id)
    return bool(
        entry
        and registered
        and entry.get("sha256") == registered.get("sha256")
        and _work_hash_ok(paths, page_id, entry)
    )


def list_pages(paths: Paths) -> list[dict]:
    splits = _splits(paths)
    has_dev_val = (paths.splits / "dev-val-manifest.json").is_file()
    registered = _registered(paths)
    second_pass = (_read_json(paths.splits / "second-pass.json", {}) or {}).get("pages", {})
    pages = []
    for pid in sorted(_index(paths)):
        saved = _read_json(paths.annotations / f"{pid}.json")
        split = splits.get(pid, "dev-train" if has_dev_val else "sem-split")
        pages.append(
            {
                "id": pid,
                "split": split,
                "hash_ok": hash_ok(paths, pid),
                "low_resolution": bool(registered.get(pid, {}).get("low_resolution")),
                "second_pass": "cego" if pid in second_pass else None,
                "last_pass1_at": max(
                    (line["pass1"]["at"] for line in saved["lines"] if line["pass1"]),
                    default=None,
                )
                if saved
                else None,
                "lines": len(saved["lines"]) if saved else None,
                "pass1_lines": sum(1 for line in saved["lines"] if line["pass1"]) if saved else 0,
                "pass2_lines": sum(1 for line in saved["lines"] if line["pass2"]) if saved else 0,
                "status": saved["status"] if saved else None,
                "seconds": saved["seconds"] if saved else None,
                "version": saved["version"] if saved else 0,
            }
        )
    return pages


def image_path(paths: Paths, page_id: str) -> Path:
    _check_page_id(page_id)
    if page_id not in _index(paths):
        raise NotFoundError(page_id)
    if not hash_ok(paths, page_id):
        raise BlockedError(page_id)
    return paths.images / f"{page_id}.jpg"


def _initial_doc(paths: Paths, page_id: str, entry: dict) -> dict:
    motor = _read_json(paths.motor / f"{page_id}.json", {"lines": []}) or {"lines": []}
    scale = float(entry.get("scale", 1.0))
    lines = []
    for number, motor_line in enumerate(
        (line for line in motor.get("lines", []) if line.get("bbox")), start=1
    ):
        x0, y0, x1, y1 = (round(value * scale) for value in motor_line["bbox"])
        text = motor_line.get("text")
        lines.append(
            {
                "line_id": format_line_id(number),
                "order": number,
                "polygon": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]],
                "box_origin": "motor",
                "motor_text": text,
                "draft": text,
                "pass1": None,
                "pass2": None,
            }
        )
    split = list_split(paths, page_id)
    return {
        "schema": SCHEMA_ID,
        "page_id": page_id,
        "image": {
            "sha256": entry["sha256"],
            "width": int(entry["width"]),
            "height": int(entry["height"]),
            "scale": scale,
        },
        "split": split,
        "draft_source": "motor",
        "next_line_id": len(lines) + 1,
        "lines": lines,
        "draft_leftover": [],
        "status": {"boxes_done": False, "pass1_done": False, "pass2_done": False},
        "seconds": dict.fromkeys(SECONDS, 0),
        "version": 0,
        "updated_at": _now(),
        "content_sha256": "0" * 64,
    }


def list_split(paths: Paths, page_id: str) -> str:
    split = _splits(paths).get(page_id)
    if split:
        return split
    return "dev-train" if (paths.splits / "dev-val-manifest.json").is_file() else "sem-split"


def load_page(paths: Paths, page_id: str) -> dict:
    """Anotação gravada, ou a inicial montada das caixas do motor (``version`` 0)."""
    _check_page_id(page_id)
    entry = _index(paths).get(page_id)
    if entry is None:
        raise NotFoundError(page_id)
    if not hash_ok(paths, page_id):
        raise BlockedError(page_id)
    saved = _read_json(paths.annotations / f"{page_id}.json")
    return saved if saved else _initial_doc(paths, page_id, entry)


# ---------------------------------------------------------------- validação


def validate(doc: dict, previous: dict | None = None) -> list[str]:
    errors = [
        f"{'/'.join(str(p) for p in error.absolute_path) or 'documento'}: {error.message}"
        for error in sorted(_validator().iter_errors(doc), key=lambda e: list(e.absolute_path))
    ]
    if errors:
        return errors
    width, height = doc["image"]["width"], doc["image"]["height"]
    seen_ids: set[str] = set()
    orders = []
    for line in doc["lines"]:
        line_id = line["line_id"]
        if line_id in seen_ids:
            errors.append(f"{line_id}: line_id repetido")
        seen_ids.add(line_id)
        if line_number(line_id) >= doc["next_line_id"]:
            errors.append(f"{line_id}: maior ou igual a next_line_id ({doc['next_line_id']})")
        orders.append(line["order"])
        for x, y in line["polygon"]:
            if not (
                -EDGE_TOLERANCE <= x <= width + EDGE_TOLERANCE
                and -EDGE_TOLERANCE <= y <= height + EDGE_TOLERANCE
            ):
                errors.append(f"{line_id}: ponto ({x}, {y}) fora da imagem {width}×{height}")
                break
        for field in ("pass1", "pass2"):
            value = line[field]
            if value and not dollar_balanced(value["text"]):
                errors.append(f"{line_id}: {field} com $ desequilibrado (fórmula sem fechar)")
    if sorted(orders) != list(range(1, len(orders) + 1)):
        errors.append("order: as posições precisam ser 1..n, sem repetir")
    if previous:
        if doc["next_line_id"] < previous["next_line_id"]:
            errors.append("next_line_id: não pode diminuir")
        old_ids = {line["line_id"] for line in previous["lines"]}
        for line_id in seen_ids - old_ids:
            if line_number(line_id) < previous["next_line_id"]:
                errors.append(f"{line_id}: identificador já usado nesta página; use um novo")
    status = doc["status"]
    lines = doc["lines"]
    if status["pass1_done"] and not (lines and all(line["pass1"] for line in lines)):
        errors.append("status: pass1_done sem texto em todas as linhas")
    if status["pass2_done"] and not (lines and all(line["pass2"] for line in lines)):
        errors.append("status: pass2_done sem texto em todas as linhas")
    return errors


# ---------------------------------------------------------------- gravação


def _write_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def save_page(
    paths: Paths,
    page_id: str,
    doc: dict,
    *,
    expected_version: int,
    seconds_delta: dict | None = None,
) -> dict:
    """Valida e grava. Identidade da imagem, divisão, tempos, estado das passadas, versão, data e
    hash são definidos aqui, nunca pelo navegador."""
    current = load_page(paths, page_id)
    if current["version"] != expected_version:
        raise ConflictError(current["version"])
    if not isinstance(doc, dict):
        raise InvalidError(["documento: não é um objeto JSON"])
    delta = seconds_delta or {}
    if any(
        not isinstance(delta.get(key, 0), (int, float)) or delta.get(key, 0) < 0
        for key in SECONDS
    ) or set(delta) - set(SECONDS):
        raise InvalidError(["seconds_delta: só boxes, pass1 e pass2, com valores ≥ 0"])

    out = copy.deepcopy(doc)
    out["schema"] = SCHEMA_ID
    out["page_id"] = page_id
    out["image"] = copy.deepcopy(current["image"])
    out["split"] = list_split(paths, page_id)
    if isinstance(out.get("lines"), list) and all(isinstance(x, dict) for x in out["lines"]):
        out["lines"] = sorted(out["lines"], key=lambda line: line.get("order", 0))
        lines = out["lines"]
        has_lines = bool(lines)
        out["status"] = {
            "boxes_done": bool((out.get("status") or {}).get("boxes_done")) and has_lines,
            "pass1_done": has_lines and all(line.get("pass1") for line in lines),
            "pass2_done": has_lines and all(line.get("pass2") for line in lines),
        }
    out["seconds"] = {
        key: round(current["seconds"][key] + float(delta.get(key, 0)), 1) for key in SECONDS
    }
    out["version"] = current["version"] + 1
    out["updated_at"] = _now()
    out["content_sha256"] = "0" * 64
    out["content_sha256"] = content_hash(out)

    previous = current if current["version"] > 0 else None
    errors = validate(out, previous)
    if errors:
        raise InvalidError(errors)

    target = paths.annotations / f"{page_id}.json"
    if target.is_file():
        _write_atomic(paths.annotations / f"{page_id}.prev.json", target.read_bytes())
    payload = json.dumps(out, ensure_ascii=False, indent=2).encode() + b"\n"
    _write_atomic(target, payload)
    return out


def import_draft(doc: dict, text: str, label: str) -> dict:
    """Distribui um rascunho de página (uma linha do papel por linha de texto) pelas caixas, na
    ordem de leitura. Linhas vazias são ignoradas; o que sobrar fica em ``draft_leftover``."""
    label = re.sub(r"[\r\n]+", " ", (label or "rascunho").strip())[:80] or "rascunho"
    drafts = [row.strip() for row in text.splitlines() if row.strip()]
    out = copy.deepcopy(doc)
    lines = sorted(out["lines"], key=lambda line: line["order"])
    for line, draft in zip(lines, drafts, strict=False):
        line["draft"] = draft
    for line in lines[len(drafts) :]:
        line["draft"] = None
    out["lines"] = lines
    out["draft_leftover"] = drafts[len(lines) :]
    out["draft_source"] = f"importado:{label}"
    return out
