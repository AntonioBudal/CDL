"""EXP-024 (F04): avaliação prequencial nos estudos reais do usuário (D-usuário), só números.

Para cada usuário, em ordem de criação, o estudo t é previsto com o estado aprendido só dos estudos
1..t-1 do mesmo usuário, e depois aprendido. Compara com o V4 estático do EXP-023.

Travas de privacidade (spec §9; decisões do usuário no EXP-023 §11 e na revisão da F01 do EXP-024):
- a origem é aberta em ``mode=ro`` e copiada pela API de backup do SQLite para uma pasta temporária;
- a cópia é aberta em ``mode=ro`` e apagada no fim, em qualquer desfecho;
- nenhum texto, título, palavra ou n-grama legível é impresso, gravado ou registrado;
- o estado aprendido fica só em memória;
- a saída tem só números e chaves fixas (``check_numeric`` confere antes de imprimir).

``T_user`` fica desligado: as pseudo-páginas estão na ordem canônica das colunas (ganho falso).

Uso (banco ativo do D:, escolhido pelo usuário na revisão da F01):
    uv run --frozen --project experiments/EXP-023/envs/organizer python \\
        experiments/EXP-024/harness/dusuario_continual.py \
        --db "D:/Leitorum/db/caderno.db" --out <json>
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import adaptive_ocr_corrector as aoc  # noqa: E402
import adaptive_organizer as ao  # noqa: E402
import diff_signal  # noqa: E402
import metrics  # noqa: E402  (EXP-023)
import simulator as sim  # noqa: E402

SECTIONS = ao.SECTIONS
CODES = ("s", "e", "c", "r")
ALLOWED_KEYS = {
    "studies_total",
    "studies_eligible",
    "users",
    "users_with_2_or_more",
    "v4_static",
    "adaptive",
    "gain_macro_f1",
    "macro_f1",
    "per_section_f1",
    "summary",
    "explanation",
    "concepts",
    "references",
    "windowdiff",
    "chars_to_move",
    "prequential_evaluated",
    "digitized_studies",
    "reading",
    "cer_raw",
    "cer_corrected",
    "lines",
    "elapsed_s",
    "update_ms_p95",
    "organizer_params_sha256",
    "note_code",
    "studies_after_first",
    "first_studies_excluded",
}


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


def load_studies(copy: Path) -> list[dict]:
    conn = sqlite3.connect(f"{copy.as_uri()}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            'SELECT s.user_id, c.book_id, s.summary, s.explanation, s.concepts, s."references",'
            " s.source_response FROM studies s JOIN chapters c ON c.id = s.chapter_id"
            " WHERE s.deleted_at IS NULL ORDER BY s.user_id, s.created_at, s.id"
        ).fetchall()
    finally:
        conn.close()
    return [
        {
            "user": str(r[0]),
            "book": f"b{r[1]}",
            "columns": {s: str(v or "") for s, v in zip(SECTIONS, r[2:6], strict=False)},
            "source": str(r[6] or ""),
        }
        for r in rows
    ]


def pseudo_page(columns: dict[str, str]) -> tuple[str, list[str], list[int]]:
    parts, labels, units = [], [], []
    for k, (code, section) in enumerate(zip(CODES, SECTIONS, strict=False)):
        body = columns[section].strip()
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


def summarize(scores: metrics.Scores) -> dict:
    r = scores.report()
    return {
        "macro_f1": r["macro_f1_chars"],
        "per_section_f1": {s: r["per_section_chars"][s]["f1"] for s in SECTIONS},
        "windowdiff": r["windowdiff"],
        "chars_to_move": r["char_error_effort"],
    }


def reading_cer(
    source_lines: list[str], saved: dict[str, str], corrected: list[str]
) -> tuple[int, int, int]:
    """Erros (bruto, corrigido) e caracteres, por linha lida casada com o trecho salvo."""
    edits = diff_signal.align_reading(source_lines, saved)
    raw = fixed = chars = 0
    by_line = {e.line: e for e in edits}
    for k, line in enumerate(source_lines):
        edit = by_line.get(k)
        if edit is None or edit.kind == "rewrite" or not edit.revised:
            continue
        raw += sim.levenshtein(edit.revised, line)
        fixed += sim.levenshtein(edit.revised, corrected[k])
        chars += len(edit.revised)
    return raw, fixed, chars


def evaluate(studies: list[dict], org_params: dict, reader_params: dict) -> dict:
    params = {**org_params, "use_T": False}
    engine = ao.AdaptiveOrganizer(params)
    reader = aoc.AdaptiveReader(engine.state_for, reader_params)
    by_user: dict[str, list[dict]] = defaultdict(list)
    for s in studies:
        by_user[s["user"]].append(s)
    eligible = [s for s in studies if sum(bool(v.strip()) for v in s["columns"].values()) >= 2]
    static, adaptive = metrics.Scores(), metrics.Scores()
    raw = fixed = chars = digitized = evaluated = first_excluded = 0
    update_ms = []
    for user, items in by_user.items():
        for t, study in enumerate(items):
            is_eligible = sum(bool(v.strip()) for v in study["columns"].values()) >= 2
            if is_eligible and t == 0:
                first_excluded += 1  # sem estudo anterior, o adaptativo é idêntico ao estático
            if is_eligible and t > 0:
                text, labels, units = pseudo_page(study["columns"])
                static.add(
                    text,
                    labels,
                    units,
                    engine.organize(user, text, None, study["book"], adaptive=False),
                )
                adaptive.add(
                    text,
                    labels,
                    units,
                    engine.organize(user, text, None, study["book"], use_T=False),
                )
                evaluated += 1
            source_lines = [ln for ln in study["source"].split("\n") if ln.strip()]
            if source_lines and t > 0:
                corrected = reader.correct_lines(user, study["book"], source_lines)
                r, f, c = reading_cer(source_lines, study["columns"], corrected)
                raw, fixed, chars, digitized = raw + r, fixed + f, chars + c, digitized + 1
            t0 = time.perf_counter()
            engine.learn_study(user, study["book"], study["columns"])
            update_ms.append((time.perf_counter() - t0) * 1000)
            if source_lines:
                reader.learn(
                    {
                        "user_id": user,
                        "book_id": study["book"],
                        "page_id": "p",
                        "reading": {"source_lines": source_lines, "line_confidence": []},
                        "saved": study["columns"],
                    }
                )
            reader.learn_text(user, study["book"], "\n".join(study["columns"].values()))
    report = {
        "studies_total": len(studies),
        "studies_eligible": len(eligible),
        "users": len(by_user),
        "users_with_2_or_more": sum(len(v) >= 2 for v in by_user.values()),
        "prequential_evaluated": evaluated,
        "first_studies_excluded": first_excluded,
        "update_ms_p95": round(sorted(update_ms)[max(0, int(0.95 * len(update_ms)) - 1)], 2)
        if update_ms
        else None,
        "digitized_studies": digitized,
    }
    if evaluated:
        report["v4_static"] = summarize(static)
        report["adaptive"] = summarize(adaptive)
        report["gain_macro_f1"] = round(
            report["adaptive"]["macro_f1"] - report["v4_static"]["macro_f1"], 4
        )
    if chars:
        report["reading"] = {
            "cer_raw": round(raw / chars, 4),
            "cer_corrected": round(fixed / chars, 4),
        }
    return report


def check_numeric(obj, path="") -> None:
    """Falha se a saída tiver qualquer coisa além de números, None ou booleanos sob chaves fixas."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key not in ALLOWED_KEYS:
                raise ValueError(f"chave não permitida na saída: {path}/{key}")
            check_numeric(value, f"{path}/{key}")
    elif not (obj is None or isinstance(obj, (int, float, bool))):
        raise ValueError(f"valor não numérico na saída: {path}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="D-usuário prequencial do EXP-024 (só números)")
    parser.add_argument("--db", required=True)
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    thresholds = json.loads(
        (HERE.parent / "artifacts" / "thresholds.json").read_text(encoding="utf-8")
    )
    started = time.perf_counter()
    studies: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="exp024-dusuario-") as folder:
        copy = copy_database(Path(args.db), Path(folder))
        try:
            studies = load_studies(copy)
            report = evaluate(studies, thresholds["organizer"], thresholds["reader"])
        finally:
            studies.clear()
            copy.unlink(missing_ok=True)
    report["elapsed_s"] = round(time.perf_counter() - started, 2)
    check_numeric(report)
    text = json.dumps(report, indent=1)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
