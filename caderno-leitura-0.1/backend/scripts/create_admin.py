#!/usr/bin/env python3
"""Script CLI para provisionamento e inicialização segura de administradores no Caderno de Leitura.

Suporta:
1. Criação interativa de nova conta de administrador com senha protegida via getpass.
2. Criação não-interativa via flags (--username, --email, --password, --display-name).
3. Promoção determinística de usuário existente para o papel 'admin' (--promote @username).
"""

from __future__ import annotations

import argparse
import getpass
import logging
import sys
from pathlib import Path

# Garante que o diretório backend esteja no sys.path mesmo se executado diretamente
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import get_session
from app.models.local_credential import LocalCredential
from app.models.user import User
from app.services.persistence import commit_changes

logger = logging.getLogger("create_admin")


def run_create_admin(
    session: Session,
    username: str | None = None,
    email: str | None = None,
    password: str | None = None,
    display_name: str | None = None,
    target_username: str | None = None,
) -> User:
    """Executa a lógica de criação ou promoção de administrador."""
    # Cenário 1: Promoção de usuário existente
    promote_target = target_username or (username if not password and not email else None)

    if target_username:
        clean_target = target_username.lstrip("@").strip()
        user = session.scalar(select(User).where(User.username == clean_target))
        if user is None:
            raise ValueError(f"Usuário '@{clean_target}' não encontrado no sistema.")

        user.role = "admin"
        user.status = "ativo"
        commit_changes(session)
        logger.info("Usuário '@%s' promovido a administrador com sucesso.", clean_target)
        return user

    # Cenário 2: Criação de nova conta de administrador
    if not username:
        raise ValueError("O nome de usuário (username) é obrigatório.")

    clean_username = username.lstrip("@").strip()
    if len(clean_username) < 3:
        raise ValueError("O nome de usuário deve ter pelo menos 3 caracteres.")

    # Verifica se username já existe
    existing_user = session.scalar(select(User).where(User.username == clean_username))
    if existing_user is not None:
        # Se já existe e foi solicitado criar sem senha, promove
        if not password and not email:
            existing_user.role = "admin"
            existing_user.status = "ativo"
            commit_changes(session)
            return existing_user
        raise ValueError(f"O nome de usuário '@{clean_username}' já está em uso.")

    if email:
        clean_email = email.strip().lower()
        existing_email = session.scalar(select(User).where(User.email == clean_email))
        if existing_email is not None:
            raise ValueError(f"O e-mail '{clean_email}' já está associado a outra conta.")
    else:
        clean_email = None

    if not password or len(password.strip()) < 8:
        raise ValueError("A senha deve conter no mínimo 8 caracteres.")

    clean_display_name = (display_name or clean_username).strip()

    new_admin = User(
        username=clean_username,
        email=clean_email,
        display_name=clean_display_name,
        role="admin",
        status="ativo",
    )
    session.add(new_admin)
    session.flush()

    pwd_hash = hash_password(password.strip())
    credential = LocalCredential(
        user_id=new_admin.id,
        password_hash=pwd_hash,
    )
    session.add(credential)
    commit_changes(session)

    logger.info("Administrador '@%s' criado com sucesso.", clean_username)
    return new_admin


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Provisiona ou promove um usuário para a função de Administrador no Caderno de Leitura."
    )
    parser.add_argument("-u", "--username", help="Nome de usuário (@username)")
    parser.add_argument("-e", "--email", help="Endereço de e-mail do administrador")
    parser.add_argument("-p", "--password", help="Senha de acesso (opcional via CLI, solicitada via prompt seguro)")
    parser.add_argument("-d", "--display-name", help="Nome de exibição completo")
    parser.add_argument(
        "--promote",
        metavar="USERNAME",
        help="Promove um usuário existente ao papel de administrador",
    )

    args = parser.parse_args()

    # Se --promote foi especificado
    if args.promote:
        target = args.promote.lstrip("@").strip()
        print(f"\n[*] Promovendo usuário @{target} a Administrador...")
        for session in get_session():
            try:
                user = run_create_admin(session=session, target_username=target)
                print(f"[✓] Sucesso: Usuário @{user.username} agora é Administrador (role='admin').\n")
                return 0
            except ValueError as err:
                print(f"[!] Erro: {err}", file=sys.stderr)
                return 1

    # Criação de novo usuário (interativo ou flags)
    username = args.username
    if not username:
        username = input("Nome de usuário para o Administrador: ").strip()

    if not username:
        print("[!] Erro: Nome de usuário não pode ser vazio.", file=sys.stderr)
        return 1

    email = args.email
    if email is None:
        email_input = input("E-mail do Administrador (opcional, pressione Enter para pular): ").strip()
        email = email_input if email_input else None

    display_name = args.display_name
    if not display_name:
        dn_input = input(f"Nome de exibição [{username}]: ").strip()
        display_name = dn_input if dn_input else username

    password = args.password
    if not password:
        while True:
            p1 = getpass.getpass("Senha de acesso (mínimo 8 caracteres): ")
            if len(p1) < 8:
                print("[!] A senha deve conter pelo menos 8 caracteres. Tente novamente.")
                continue
            p2 = getpass.getpass("Confirme a senha: ")
            if p1 != p2:
                print("[!] As senhas não conferem. Tente novamente.")
                continue
            password = p1
            break

    print(f"\n[*] Criando conta de Administrador @{username}...")
    for session in get_session():
        try:
            admin = run_create_admin(
                session=session,
                username=username,
                email=email,
                password=password,
                display_name=display_name,
            )
            print(f"[✓] Administrador @{admin.username} criado com sucesso!\n")
            return 0
        except ValueError as err:
            print(f"[!] Erro ao provisionar administrador: {err}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
