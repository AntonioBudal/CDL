"""EXP-044 — registra as fontes novas no catálogo, com a evidência de licença guardada.

Uso (ambiente do subprojeto, PYTHONPATH no ``document-intelligence/``): ``python sources.py``
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from tools.catalogo import Catalog

_COMMON = Path(__file__).resolve().parents[2] / "EXP-043-amostragem-de-fontes/harness/common.py"
_spec = importlib.util.spec_from_file_location("exp043_common", _COMMON)
net = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(net)

TRAPRINQ_API = "https://zenodo.org/api/records/13986218"
BFL_PAGE = "https://web.inf.ufpr.br/vri/databases/brazilian-forensic-letter-database/"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    traprinq_terms = net.fetch(TRAPRINQ_API)
    bfl_terms = net.fetch(BFL_PAGE)
    cat = Catalog()
    try:
        cat.add_source(
            "zenodo-traprinq",
            name="TraPrInq — Portuguese Handwriting 16th-19th c.",
            url="https://zenodo.org/records/13986218",
            license="CC-BY-4.0",
            conditions=["atribuicao"],
            status="APPROVED",
            access="download",
            terms=traprinq_terms,
            terms_url=TRAPRINQ_API,
            notes="EXP-044: licença lida no registro do Zenodo (cc-by-4.0, acesso aberto).",
        )
        cat.add_source(
            "ufpr-bfl",
            name="Brazilian Forensic Letter Database (BFL)",
            url=BFL_PAGE,
            license="CC-BY-4.0 (conflitante: 'may be used for non-commercial research')",
            conditions=["atribuicao", "citar Freitas et al. 2008", "licenca_conflitante"],
            status="EXPERIMENT_ONLY",
            access="download",
            terms=bfl_terms,
            terms_url=BFL_PAGE,
            notes=(
                "EXP-044: selo CC BY 4.0 e frase de pesquisa não comercial na mesma página; vale a"
                " mais restritiva até a resposta dos autores (estratégia v3, §3)."
            ),
        )
        cat.flush()
        for source_id in ("zenodo-traprinq", "ufpr-bfl"):
            row = cat.source(source_id)
            print(source_id, row["status"], row["license"], row["terms_sha256"][:12])
    finally:
        cat.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
