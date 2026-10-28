"""Chave mestra do cofre de imagens (feature 090-B): gerar ou restaurar. Rode pelo instalar.py:

    py -3.13 instalar.py --media-key            # gera a chave e mostra o código de recuperação UMA vez
    py -3.13 instalar.py --media-key --restore  # recria a chave a partir do código de recuperação

A chave fica no disco do sistema, protegida pelo Windows (DPAPI), nunca no HD de armazenamento. O código de
recuperação aparece só neste terminal: anote e guarde fora do computador. Sem ele, perder o Windows significa
perder as imagens cifradas.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "backend"))

from app.core.media_key import (  # noqa: E402
    MediaKeyError,
    fingerprint,
    generate_key,
    key_file_path,
    key_from_recovery,
    recovery_code,
    write_key_file,
)


def registered_fingerprint() -> str | None:
    """Impressão digital já registrada no acervo (só leitura), se houver."""
    from app.core.config import get_database_path

    database = get_database_path()
    if not database.is_file():
        return None
    try:
        conn = sqlite3.connect(f"{database.resolve().as_uri()}?mode=ro", uri=True)
        try:
            row = conn.execute("SELECT media_key_fingerprint FROM storage_settings WHERE id = 1").fetchone()
        finally:
            conn.close()
    except sqlite3.Error:
        return None
    return row[0] if row else None


def generate() -> int:
    registered = registered_fingerprint()
    if registered:
        print("Este acervo já tem uma chave registrada. Para reinstalá-la, use --media-key --restore com o código "
              "de recuperação.", file=sys.stderr)
        return 1
    key = generate_key()
    path = write_key_file(key)
    print(f"Chave do cofre criada e protegida pelo Windows em: {path}")
    print()
    print("CÓDIGO DE RECUPERAÇÃO (aparece só agora; anote e guarde fora do computador):")
    print()
    print("    " + recovery_code(key))
    print()
    print("Sem este código, se o Windows for reinstalado ou o arquivo da chave se perder, as imagens cifradas")
    print("não podem ser abertas. Ninguém consegue recuperá-lo depois.")
    return 0


def restore() -> int:
    code = input("Digite o código de recuperação: ")
    key = key_from_recovery(code)
    registered = registered_fingerprint()
    if registered and registered != fingerprint(key):
        print("Este código não corresponde à chave registrada neste acervo. Nada foi gravado.", file=sys.stderr)
        return 1
    path = write_key_file(key)
    print(f"Chave restaurada e protegida pelo Windows em: {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chave mestra do cofre de imagens do Leitorum")
    parser.add_argument("--restore", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        if key_file_path().exists():
            print(f"Já existe um arquivo de chave em {key_file_path()}; nada foi alterado.", file=sys.stderr)
            return 1
        return restore() if args.restore else generate()
    except MediaKeyError as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
