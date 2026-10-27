"""EXP-023, D-usuário (spec §8.1 e decisão 1 da §11): medida nos estudos do próprio usuário, só
números.

Travas de privacidade (aprovadas pelo usuário em 2026-10-27):

* o banco ativo é aberto **só para leitura** (``mode=ro``) e apenas como origem da API de backup do
  SQLite;
* a cópia vai para uma pasta temporária, é aberta em ``mode=ro`` e é apagada no fim, em qualquer
  desfecho;
* nada de texto sai deste processo: sem impressão, log ou arquivo com conteúdo dos estudos; erros
  mostram só o tipo da exceção; o relatório tem apenas contagens e métricas agregadas.

Para cada estudo elegível (não apagado, com pelo menos 2 das 4 seções preenchidas), as seções viram
uma pseudo-página na ordem canônica, sem cabeçalhos, e a pipeline tenta devolver cada trecho à sua
seção. V4: só centróides-semente. V6: centróides misturados com os dos outros estudos do mesmo
usuário (deixa o estudo avaliado de fora), com kappa em {25, 50, 100}; 50 é o valor principal
fixado na spec.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sqlite3
import sys
import tempfile
import time
import traceback
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

import organizer as org
from evaluate import git_state, load_model
from metrics import Scores

ROOT = Path(__file__).resolve().parents[4]
ACTIVE_DB = ROOT / "caderno-leitura-0.1" / "backend" / "data" / "caderno.db"
CODES = ("s", "e", "c", "r")
MAX_STUDIES = 300
KAPPAS = (25.0, 50.0, 100.0)


def copy_database(source: Path, folder: Path) -> Path:
    target = folder / "copia.db"
    src = sqlite3.connect(f"{source.resolve().as_uri()}?mode=ro", uri=True)
    try:
        dst = sqlite3.connect(target)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()
    return target


def load_studies(copy: Path) -> list[tuple[str, list[str]]]:
    conn = sqlite3.connect(f"{copy.as_uri()}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            'SELECT user_id, summary, explanation, concepts, "references" FROM studies'
            " WHERE deleted_at IS NULL"
        ).fetchall()
    finally:
        conn.close()
    return [(row[0], [str(v or "") for v in row[1:]]) for row in rows]


def pseudo_page(sections: list[str]) -> tuple[str, list[str], list[int]]:
    parts, labels, units = [], [], []
    for k, (code, body) in enumerate(zip(CODES, sections, strict=False)):
        body = body.strip()
        if not body:
            continue
        if parts:
            parts.append("\n")
            labels.append(labels[-1])
            units.append(units[-1])
        parts.append(body)
        labels.extend(code * len(body))
        units.extend([k] * len(body))
    return "".join(parts), labels, units


def section_vectors(
    engine: org.Organizer, sections: list[str]
) -> dict[str, tuple[dict[int, float], int]]:
    out = {}
    for name, body in zip(org.SECTIONS, sections, strict=False):
        if not body.strip():
            continue
        units, _ = org.segment(body)
        total: dict[int, float] = defaultdict(float)
        for u in units:
            for h, v in org.tfidf(u.text, engine.model.idf, engine.model.default_idf).items():
                total[h] += v
        out[name] = (dict(total), len(units))
    return out


def minus(total: dict[int, float], part: dict[int, float] | None) -> dict[int, float]:
    if not part:
        return total
    out = dict(total)
    for h, v in part.items():
        left = out.get(h, 0.0) - v
        if left > 1e-12:
            out[h] = left
        else:
            out.pop(h, None)
    return out


def evaluate(studies, engine: org.Organizer) -> dict:
    by_user: dict[str, list[list[str]]] = defaultdict(list)
    for user, sections in studies:
        by_user[user].append(sections)
    eligible = [(u, s) for u, s in studies if sum(bool(x.strip()) for x in s) >= 2]
    rng = random.Random(23)
    sample = rng.sample(eligible, min(MAX_STUDIES, len(eligible)))
    report = {
        "studies_total": len(studies),
        "studies_eligible": len(eligible),
        "studies_evaluated": len(sample),
        "users_with_eligible": len({u for u, _ in eligible}),
    }
    if not sample:
        return report
    # centróides do usuário: somas por seção de todos os estudos dele
    # (cada estudo fica guardado para o "deixa um de fora")
    started = time.perf_counter()
    per_study = {}
    totals: dict[str, dict[str, dict[int, float]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float))
    )
    counts: dict[str, Counter] = defaultdict(Counter)
    for user, sections_list in by_user.items():
        for sections in sections_list:
            vecs = section_vectors(engine, sections)
            per_study[id(sections)] = vecs
            for name, (vec, n) in vecs.items():
                bucket = totals[user][name]
                for h, v in vec.items():
                    bucket[h] += v
                counts[user][name] += n
    build_s = time.perf_counter() - started
    report["centroid_build_s_all_studies"] = round(build_s, 2)
    report["centroid_build_s_per_100_studies"] = round(build_s / max(1, len(studies)) * 100, 3)
    seed = Scores()
    user_scores = {k: Scores() for k in KAPPAS}
    char_share = Counter()
    for user, sections in sample:
        text, labels, units = pseudo_page(sections)
        char_share.update(lab for lab, ch in zip(labels, text, strict=False) if not ch.isspace())
        t0 = time.perf_counter()
        result = engine.organize(text)
        seed.add(text, labels, units, result, (time.perf_counter() - t0) * 1000)
        own = per_study[id(sections)]
        for kappa in KAPPAS:
            engine.model.params["kappa"] = kappa
            user_data = {}
            for name in org.SECTIONS:
                rest = minus(dict(totals[user][name]), own.get(name, (None, 0))[0])
                n = counts[user][name] - own.get(name, (None, 0))[1]
                if n > 0 and rest:
                    user_data[name] = (rest, n)
            cents = engine.centroids(user_data)
            user_scores[kappa].add(text, labels, units, engine.organize(text, centroids=cents))
    engine.model.params["kappa"] = 50.0
    report["section_char_share"] = {
        org.LABEL_OF[k]: round(v / max(1, sum(char_share.values())), 4)
        for k, v in char_share.items()
    }
    report["V4_seed"] = seed.report()
    report["V6_user"] = {f"kappa_{int(k)}": s.report() for k, s in user_scores.items()}
    v4, v6 = report["V4_seed"], report["V6_user"]["kappa_50"]
    minority = sorted(report["section_char_share"], key=report["section_char_share"].get)[:2]
    drops = {
        s: round(v4["per_section_chars"][s]["f1"] - v6["per_section_chars"][s]["f1"], 4)
        for s in minority
    }
    report["h4"] = {
        "gain_macro_f1": round(v6["macro_f1_chars"] - v4["macro_f1_chars"], 4),
        "minority_sections": minority,
        "minority_f1_drop": drops,
        "met": v6["macro_f1_chars"] - v4["macro_f1_chars"] >= 0.03
        and all(d <= 0.01 for d in drops.values()),
    }
    report["note"] = (
        "Coluna de cada estudo como gabarito; pseudo-página na ordem canônica e sem cabeçalhos. "
        "unit_boundary_f1 aqui mede só as fronteiras entre colunas."
    )
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="EXP-023: medida nos estudos do usuário (só números)"
    )
    parser.add_argument(
        "--db", default=str(ACTIVE_DB), help="banco de origem (lido só pela API de backup)"
    )
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    folder = Path(tempfile.mkdtemp(prefix="exp023-dusuario-"))
    try:
        copy = copy_database(Path(args.db), folder)
        studies = load_studies(copy)
        model, _ = load_model()
        report = evaluate(studies, org.Organizer(model))
        del studies
    except Exception as error:  # noqa: BLE001 — só o tipo: a mensagem poderia conter texto dos estudos
        frames = traceback.extract_tb(error.__traceback__)
        where = f"{Path(frames[-1].filename).name}:{frames[-1].lineno}" if frames else "?"
        print(f"falhou: {type(error).__name__} em {where}", file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(folder, ignore_errors=True)
        if folder.exists():
            print("aviso: a pasta temporária não pôde ser apagada", file=sys.stderr)
    full = {
        "schema": "leitorum-di-organizer-dusuario/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-023",
        "git": git_state(),
        "privacy": (
            "só números agregados; cópia temporária via API de backup, origem e cópia em mode=ro,"
            " apagada no fim"
        ),
        **report,
    }
    Path(args.out).write_text(
        json.dumps(full, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    keys = ("studies_total", "studies_eligible", "studies_evaluated", "users_with_eligible")
    print({k: full.get(k) for k in keys})
    if "V4_seed" in full:
        print(
            "V4 semente:",
            full["V4_seed"]["macro_f1_chars"],
            "| V6 kappa 50:",
            full["V6_user"]["kappa_50"]["macro_f1_chars"],
            "| H4:",
            full["h4"]["met"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
