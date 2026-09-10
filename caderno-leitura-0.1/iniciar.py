"""Inicia apenas o servidor Python na interface de loopback deste PC."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))


def main() -> int:
    if not (ROOT / "frontend" / "dist" / "index.html").is_file():
        print("A interface compilada está ausente. Extraia o ZIP completo ou gere o build.", file=sys.stderr)
        return 1
    try:
        import uvicorn
        from app.main import app
    except ModuleNotFoundError as error:
        print(f"Dependência ausente: {error.name}. Execute INSTALAR.cmd primeiro.", file=sys.stderr)
        return 1
    print("Abra http://127.0.0.1:8000 no navegador. Para encerrar, use Ctrl+C.", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8000, workers=1, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
