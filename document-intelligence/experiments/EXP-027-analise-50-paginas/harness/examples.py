"""T004b — exemplos concretos de falha (recorte + saída + esperado), fora do Git, em
``processed/exp-027/exemplos/``: um ``index.html`` local com até N exemplos por origem de erro
(linha não detectada, linhas unidas, linhas partidas, leitura ruim em texto, leitura ruim em
fórmula, leitura espúria). O ``report.md`` cita só o número e a categoria de cada exemplo.
Roda no ambiente do motor (OpenCV).
"""

from __future__ import annotations

import argparse
import html
import json
import sys

import align
import cv2
import textnorm
from paths import EXAMPLES, MANIFEST, PHOTOS, PROCESSED, REFERENCE, SPLITS

CONVERTED = PROCESSED / "fotos-png"


def load_image(path, pid):
    if path.suffix.lower() in {".heic", ".heif"}:
        path = CONVERTED / f"{pid}.png"
    return cv2.imread(str(path), cv2.IMREAD_COLOR)


def crop(image, bboxes, pad_ratio=0.3):
    h, w = image.shape[:2]
    x0 = min(b[0] for b in bboxes)
    y0 = min(b[1] for b in bboxes)
    x1 = max(b[2] for b in bboxes)
    y1 = max(b[3] for b in bboxes)
    pad = max(4, int((y1 - y0) * pad_ratio))
    return image[max(0, y0 - pad) : min(h, y1 + pad), max(0, x0 - pad) : min(w, x1 + pad)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Exemplos de falha do EXP-027")
    parser.add_argument("--per-kind", type=int, default=2)
    parser.add_argument("--system", default="motor")
    parser.add_argument("--dev-only", action="store_true", help="só páginas de desenvolvimento")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    split_path = SPLITS / "test-manifest.json"
    tests = (
        set(json.loads(split_path.read_text(encoding="utf-8"))["pages"])
        if split_path.is_file()
        else set()
    )
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    found: dict[str, list[dict]] = {
        "linha_nao_detectada": [],
        "linhas_unidas": [],
        "linhas_partidas": [],
        "leitura_texto": [],
        "leitura_formula": [],
        "leitura_espuria": [],
    }
    for pid, page in manifest["pages"].items():
        if args.dev_only and pid in tests:
            continue
        ref_path = REFERENCE / f"{pid}.txt"
        motor_path = PROCESSED / args.system / f"{pid}.json"
        if not ref_path.is_file() or not motor_path.is_file():
            continue
        refs = textnorm.text_lines(textnorm.parse_reference(ref_path.read_text(encoding="utf-8")))
        motor = json.loads(motor_path.read_text(encoding="utf-8"))["lines"]
        hyps = [textnorm.page_text(m["text"]) for m in motor]
        matching = align.match_lines([r.text for r in refs], hyps)
        image = None

        def add(kind, bboxes, expected, got, note, pid=pid, page=page):
            nonlocal image
            if len(found[kind]) >= args.per_kind or not bboxes:
                return
            if image is None:
                image = load_image(PHOTOS / page["file"], pid)
            number = sum(len(v) for v in found.values()) + 1
            name = f"ex{number:02d}-{kind}.jpg"
            piece = crop(image, bboxes)
            if piece.size:
                cv2.imwrite(str(EXAMPLES / name), piece, [cv2.IMWRITE_JPEG_QUALITY, 90])
                found[kind].append(
                    {
                        "n": number,
                        "page": pid,
                        "file": name,
                        "expected": expected,
                        "got": got,
                        "note": note,
                    }
                )

        for refs_g, hyps_g in matching.groups:
            ref_text = " ".join(refs[i].text for i in refs_g)
            hyp_text = " ".join(hyps[j] for j in hyps_g)
            bboxes = [motor[j]["bbox"] for j in hyps_g]
            if len(refs_g) > 1:
                add(
                    "linhas_unidas",
                    bboxes,
                    "\n".join(refs[i].text for i in refs_g),
                    hyp_text,
                    "uma caixa para várias linhas",
                )
            elif len(hyps_g) > 1:
                add(
                    "linhas_partidas",
                    bboxes,
                    ref_text,
                    "\n".join(hyps[j] for j in hyps_g),
                    "uma linha em várias caixas",
                )
            else:
                group = align.merge_ref(refs, refs_g)
                detail = align.recognition_breakdown(group, hyp_text)
                if (
                    detail["errors_formula"] >= 3
                    and detail["errors_formula"] >= detail["errors_text"]
                ):
                    add(
                        "leitura_formula",
                        bboxes,
                        ref_text,
                        hyp_text,
                        f"{detail['errors_formula']} erros em fórmula",
                    )
                elif align.cer(ref_text, hyp_text) >= 0.3 and detail["errors_text"] >= 5:
                    add(
                        "leitura_texto",
                        bboxes,
                        ref_text,
                        hyp_text,
                        f"CER {align.cer(ref_text, hyp_text):.0%}",
                    )
        for j in matching.spurious:
            if len(hyps[j]) >= 4:
                add(
                    "leitura_espuria",
                    [motor[j]["bbox"]],
                    "",
                    hyps[j],
                    "caixa sem linha na referência",
                )
        if matching.missing and len(found["linha_nao_detectada"]) < args.per_kind:
            # sem caixa para a linha perdida: mostra a página reduzida com as caixas lidas
            if image is None:
                image = load_image(PHOTOS / page["file"], pid)
            number = sum(len(v) for v in found.values()) + 1
            name = f"ex{number:02d}-linha_nao_detectada.jpg"
            canvas = image.copy()
            for m in motor:
                x0, y0, x1, y1 = m["bbox"]
                cv2.rectangle(canvas, (x0, y0), (x1, y1), (0, 140, 255), 3)
            h, w = canvas.shape[:2]
            f = min(1.0, 1400 / max(h, w))
            canvas = cv2.resize(canvas, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
            cv2.imwrite(str(EXAMPLES / name), canvas, [cv2.IMWRITE_JPEG_QUALITY, 85])
            found["linha_nao_detectada"].append(
                {
                    "n": number,
                    "page": pid,
                    "file": name,
                    "expected": "\n".join(refs[i].text for i in matching.missing),
                    "got": "",
                    "note": (
                        f"{len(matching.missing)} linha(s) da referência sem caixa; "
                        "caixas lidas em laranja"
                    ),
                }
            )
    rows = []
    for kind, items in found.items():
        for item in items:
            expected = html.escape(item["expected"]) or "—"
            got = html.escape(item["got"]) or "—"
            rows.append(
                f"<section><h2>Exemplo {item['n']} — {kind.replace('_', ' ')} ({item['page']})</h2>"
                f"<p class='note'>{html.escape(item['note'])}</p>"
                f"<img src='{item['file']}' alt='recorte'>"
                f"<div class='pair'><div><h3>Esperado</h3><pre>{expected}</pre></div>"
                f"<div><h3>Saída do motor</h3><pre>{got}</pre></div></div></section>"
            )
    style = (
        "body{font:15px system-ui;margin:20px;max-width:1100px}"
        "img{max-width:100%;border:1px solid #ccc}"
        ".pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}"
        "pre{white-space:pre-wrap;background:#f6f4ee;padding:8px}"
        ".note{color:#666}section{margin-bottom:32px;border-bottom:1px solid #ddd}"
    )
    page_html = (
        "<!doctype html><html lang='pt-BR'><meta charset='utf-8'><title>Exemplos EXP-027</title>"
        f"<style>{style}</style>"
        "<h1>EXP-027 — exemplos de falha (local, fora do Git)</h1>" + "".join(rows) + "</html>"
    )
    (EXAMPLES / "index.html").write_text(page_html, encoding="utf-8")
    summary = {kind: [(i["n"], i["page"]) for i in items] for kind, items in found.items()}
    (EXAMPLES / "index.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: len(v) for k, v in found.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
