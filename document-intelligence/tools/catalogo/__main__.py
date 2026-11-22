"""Linha de comando do catálogo de procedência. Saída em JSON, sem texto dos itens.

Uso (a partir de ``document-intelligence/``)::

    uv run python -m tools.catalogo fontes
    uv run python -m tools.catalogo uso
    uv run python -m tools.catalogo pendentes
    uv run python -m tools.catalogo revisar --fonte teklia-belfort --para APPROVED \
        --motivo "..." [--evidencia URL]
    uv run python -m tools.catalogo revisar --item teklia-belfort:train-12 --para REJECTED \
        --motivo "..."
    uv run python -m tools.catalogo ciclo --finalidade experimento --fontes a,b \
        [--divisoes train] \\
        --receita R --commit C --semente 0
    uv run python -m tools.catalogo promover-conferir RUN
    uv run python -m tools.catalogo resumo-treino RUN
    uv run python -m tools.catalogo verificar
    uv run python -m tools.catalogo importar-exp043 [--amostras D:/Leitorum-DI/amostras/exp-043]

A raiz dos dados é ``D:/Leitorum-DI`` (ou ``LEITORUM_DI_DATA``).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .catalog import Catalog
from .importar_exp043 import import_samples


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.catalogo")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fontes")
    sub.add_parser("uso")
    sub.add_parser("pendentes")
    sub.add_parser("verificar")
    review = sub.add_parser("revisar")
    target = review.add_mutually_exclusive_group(required=True)
    target.add_argument("--fonte")
    target.add_argument("--item")
    review.add_argument("--para", required=True)
    review.add_argument("--motivo", required=True)
    review.add_argument("--evidencia")
    run = sub.add_parser("ciclo")
    run.add_argument("--finalidade", required=True, choices=["experimento", "produto"])
    run.add_argument("--fontes", required=True)
    run.add_argument("--divisoes", default="")
    run.add_argument("--receita", required=True)
    run.add_argument("--commit", required=True)
    run.add_argument("--semente", type=int, required=True)
    for name in ("promover-conferir", "resumo-treino"):
        sub.add_parser(name).add_argument("run_id")
    imp = sub.add_parser("importar-exp043")
    imp.add_argument("--amostras", default="D:/Leitorum-DI/amostras/exp-043")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    catalog = Catalog()
    try:
        if args.command == "fontes":
            out = [
                {k: s[k] for k in ("source_id", "license", "conditions", "status", "access")}
                for s in catalog.sources()
            ]
        elif args.command == "uso":
            out = catalog.usage()
        elif args.command == "pendentes":
            out = catalog.pending()
        elif args.command == "verificar":
            out = {"com_problema": catalog.verify()}
        elif args.command == "revisar":
            scope, target_id = ("source", args.fonte) if args.fonte else ("item", args.item)
            out = {
                "itens": catalog.review(
                    scope, target_id, args.para, reason=args.motivo, evidence=args.evidencia
                )
            }
        elif args.command == "ciclo":
            out = {
                "run_id": catalog.start_run(
                    args.finalidade,
                    sources=args.fontes.split(","),
                    splits=[s for s in args.divisoes.split(",") if s] or None,
                    recipe=args.receita,
                    commit=args.commit,
                    seed=args.semente,
                )
            }
        elif args.command == "promover-conferir":
            ok, problems = catalog.check_promotion(args.run_id)
            out = {"pode_promover": ok, "problemas": problems}
        elif args.command == "resumo-treino":
            out = catalog.training_summary(args.run_id)
        else:
            out = import_samples(catalog, Path(args.amostras))
            out["_totais"] = catalog.counts()
    finally:
        catalog.close()
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
