"""T003b — ferramenta local de transcrição: servidor HTTP só em 127.0.0.1 que mostra a foto, os
recortes e o texto lido pelo motor, e grava a referência (``raw/exp-027/referencia/pNN.txt``) e a
classificação manual (``raw/exp-027/classificacao/pNN.json``). Sem rede externa, sem dependências.

Uso: ``python transcribe_server.py [--port 8765]`` e abrir http://127.0.0.1:8765/ no navegador.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from paths import CLASSIFICATION, MANIFEST, MOTOR_OUT, PROCESSED, REFERENCE, SPLITS, TOOL

STATIC = Path(__file__).resolve().parent / "tool"
TEACHER: dict[str, object] = {
    "system": None,
    "on_test": False,
}  # --teacher: rascunho de outro sistema
CLASSES = {
    "escrita": ["cursiva", "forma", "mista"],
    "formulas": ["nenhuma", "poucas", "muitas"],
    "foto": ["boa", "media", "ruim"],
    "papel": ["branco", "pautado", "quadriculado", "outro"],
    "layout": ["uma_coluna", "notas_laterais", "diagramas_tabelas", "misto"],
}


def read_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def test_ids() -> set[str]:
    split = read_json(SPLITS / "test-manifest.json", None)
    return set(split["pages"]) if split else set()


def page_list() -> list[dict]:
    manifest = read_json(MANIFEST, {"pages": {}})
    quality = read_json(PROCESSED / "quality.json", {})
    tests = test_ids()
    out = []
    for pid, page in manifest["pages"].items():
        classification = read_json(CLASSIFICATION / f"{pid}.json", {})
        out.append(
            {
                "id": pid,
                "width": page["width"],
                "height": page["height"],
                "motor_lines": quality.get(pid, {}).get("motor_lines"),
                "has_reference": (REFERENCE / f"{pid}.txt").is_file(),
                "done": bool(classification.get("done")),
                "second_pass": bool(classification.get("second_pass")),
                "classified": all(classification.get(key) for key in CLASSES),
                "is_test": pid in tests,
            }
        )
    return out


def page_detail(pid: str) -> dict | None:
    manifest = read_json(MANIFEST, {"pages": {}})
    if pid not in manifest["pages"]:
        return None
    motor = read_json(MOTOR_OUT / f"{pid}.json", {"lines": []})
    quality = read_json(PROCESSED / "quality.json", {}).get(pid, {})
    reference_file = REFERENCE / f"{pid}.txt"
    is_test = pid in test_ids()
    draft_source, draft_text = "motor", "\n".join(line["text"] for line in motor["lines"])
    teacher = TEACHER["system"]
    if teacher and (not is_test or TEACHER["on_test"]):  # teste só com --teacher-on-test
        taught = read_json(PROCESSED / teacher / f"{pid}.json", None)
        if taught:
            draft_source = f"teacher:{teacher}"
            draft_text = "\n".join(line["text"] for line in taught["lines"])
    return {
        "id": pid,
        "image": f"/pages/{pid}.jpg",
        "display_factor": quality.get("display_factor", 1.0),
        "lines": [
            {"text": line["text"], "bbox": line["bbox"], "confidence": line["confidence"]}
            for line in motor["lines"]
        ],
        "draft_text": draft_text,
        "draft_source": draft_source,
        "reference": reference_file.read_text(encoding="utf-8")
        if reference_file.is_file()
        else None,
        "classification": read_json(CLASSIFICATION / f"{pid}.json", {}),
        "classes": CLASSES,
        "is_test": is_test,
    }


def save_page(pid: str, payload: dict) -> dict:
    REFERENCE.mkdir(parents=True, exist_ok=True)
    CLASSIFICATION.mkdir(parents=True, exist_ok=True)
    text = payload.get("reference")
    if isinstance(text, str):
        normalized = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n"))
        (REFERENCE / f"{pid}.txt").write_text(normalized.strip("\n") + "\n", encoding="utf-8")
    classification = {key: payload.get(key) for key in CLASSES if payload.get(key) in CLASSES[key]}
    classification["draft_source"] = str(payload.get("draft_source") or "")
    classification["done"] = bool(payload.get("done"))
    classification["second_pass"] = bool(payload.get("second_pass"))
    classification["saved_at"] = datetime.now(UTC).isoformat()
    (CLASSIFICATION / f"{pid}.json").write_text(
        json.dumps(classification, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"ok": True, "saved_at": classification["saved_at"]}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def log_message(self, format, *args):  # noqa: A002 — assinatura da biblioteca
        pass  # nada de caminhos nem texto no console

    def _json(self, payload, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path: Path, content_type: str) -> None:
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802 — nome da biblioteca
        url = urlparse(self.path)
        parts = url.path.strip("/").split("/")
        if url.path == "/api/pages":
            self._json(page_list())
        elif len(parts) == 3 and parts[:2] == ["api", "page"]:
            detail = page_detail(parts[2])
            self._json(detail) if detail else self.send_error(HTTPStatus.NOT_FOUND)
        elif len(parts) == 2 and parts[0] == "pages" and parts[1].endswith(".jpg"):
            self._file(TOOL / "pages" / parts[1], "image/jpeg")
        elif len(parts) == 3 and parts[0] == "crops" and parts[2].endswith(".jpg"):
            self._file(TOOL / "crops" / parts[1] / parts[2], "image/jpeg")
        elif url.path in ("/", "/index.html"):
            self._file(STATIC / "index.html", "text/html; charset=utf-8")
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):  # noqa: N802 — nome da biblioteca
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) == 3 and parts[:2] == ["api", "page"]:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if page_detail(parts[2]) is None:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self._json(save_page(parts[2], payload))
        else:
            self.send_error(HTTPStatus.NOT_FOUND)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ferramenta local de transcrição do EXP-027")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--teacher", default=None, help="sistema cujo rascunho preenche as páginas")
    parser.add_argument(
        "--teacher-on-test",
        action="store_true",
        help="também nas páginas de teste (decisão do usuário; exige revisão humana e 2ª passada)",
    )
    args = parser.parse_args(argv)
    TEACHER["system"] = args.teacher
    TEACHER["on_test"] = args.teacher_on_test
    sys.stdout.reconfigure(encoding="utf-8")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Transcrição: http://127.0.0.1:{args.port}/  (Ctrl+C para parar)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
