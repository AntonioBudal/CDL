#!/usr/bin/env python3
r"""Remonta o estado do adaptador do organizador a partir dos registros ``leitorum-feedback/1`` (feature 091-C, FR-015).

Para quando o estado se corromper ou o artefato do organizador mudar. Só com o serviço parado: recusa se a porta
8000 estiver ouvindo. Por padrão só simula (``--dry-run``); com ``--execute``, grava depois do snapshot pela mesma
barreira das migrações. A saída tem só contagens: nenhum texto, título ou id de estudo.

Uso (a partir de ``caderno-leitura-0.1/backend``, com o ``.env`` de sempre):
    .venv\Scripts\python scripts\rebuild_organizer_state.py --all
    .venv\Scripts\python scripts\rebuild_organizer_state.py --all --execute
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_database_path  # noqa: E402
from app.db.session import create_sqlite_engine  # noqa: E402
from app.models.organizer_feedback import OrganizerFeedback  # noqa: E402
from app.services.maintenance import ensure_pre_upgrade_snapshot  # noqa: E402
from app.services.organizer import adapter_service  # noqa: E402

PORT = 8000


def port_in_use(port: int = PORT) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.5)
        return probe.connect_ex(("127.0.0.1", port)) == 0


def run(database: Path, user_id: str | None, execute: bool) -> dict:
    engine = create_sqlite_engine(database)
    try:
        with Session(engine) as session:
            if user_id is not None:
                users = [user_id]
            else:
                users = list(session.scalars(select(OrganizerFeedback.user_id).distinct()))
            total = {"users": len(users), "records": 0, "codes": {}, "bytes": 0, "pruned_books": 0, "written": execute}
            for uid in users:
                report = adapter_service.rebuild(session, uid, execute=execute)
                total["records"] += report["records"]
                total["bytes"] += report["bytes"]
                total["pruned_books"] += int(report.get("pruned_books", False))
                for code, n in report["codes"].items():
                    total["codes"][code] = total["codes"].get(code, 0) + n
            return total
    finally:
        engine.dispose()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    who = parser.add_mutually_exclusive_group(required=True)
    who.add_argument("--user", help="id do usuário")
    who.add_argument("--all", action="store_true", help="todos os usuários com registros")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="só simula (padrão)")
    mode.add_argument("--execute", action="store_true", help="grava o estado novo")
    args = parser.parse_args(argv)
    if port_in_use():
        print("Recusado: o servidor está ouvindo na porta 8000. Pare o serviço Leitorum antes.", file=sys.stderr)
        return 2
    database = get_database_path()
    if args.execute:
        ensure_pre_upgrade_snapshot(database)
    print(json.dumps(run(database, args.user, args.execute), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
