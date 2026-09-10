"""Prepara uma instalacao local sem depender de Node.js ou das entregas anteriores."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
ENVIRONMENT = BACKEND / ".venv"


def run(*arguments: str | Path, cwd: Path = ROOT) -> None:
    subprocess.run([str(argument) for argument in arguments], cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Instalar o Caderno de Leitura Alpha 0.1.")
    parser.add_argument("--dev", action="store_true", help="Instalar também as dependências dos testes Python.")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 13):
        print("Use Python 3.13: no Windows, execute py -3.13 instalar.py.", file=sys.stderr)
        return 1

    requirements = BACKEND / ("requirements-dev.txt" if args.dev else "requirements.txt")
    for required in (requirements, BACKEND / "alembic.ini", ROOT / "frontend" / "dist" / "index.html"):
        if not required.is_file():
            print(f"Arquivo necessário ausente: {required.relative_to(ROOT)}. Extraia o ZIP completo.", file=sys.stderr)
            return 1

    python = ENVIRONMENT / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    try:
        if not python.is_file():
            print("Criando o ambiente Python deste projeto…", flush=True)
            run(sys.executable, "-m", "venv", ENVIRONMENT)
        run(python, "-c", "import sys; assert sys.version_info[:2] == (3, 13), 'O ambiente existente precisa usar Python 3.13.'")
        print("Instalando as dependências…", flush=True)
        run(python, "-m", "pip", "install", "--disable-pip-version-check", "-r", requirements)
        # Esta verificação também rejeita um banco configurado dentro da pasta pública.
        run(python, "-c", "from app.main import app", cwd=BACKEND)
        print("Aplicando as migrações pendentes…", flush=True)
        run(python, "-m", "alembic", "upgrade", "head", cwd=BACKEND)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Instalação interrompida: {error}", file=sys.stderr)
        print("Corrija o erro indicado e execute novamente. Não apague o arquivo do banco.", file=sys.stderr)
        return 1
    print("Instalação concluída. No Windows, abra INICIAR.cmd.")
    print("Endereço do caderno: http://127.0.0.1:8000")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInstalação interrompida pelo usuário.", file=sys.stderr)
        raise SystemExit(130)
