"""Saída do EXP-007 em LDF 2.0, pelo conversor de referência do pacote principal.

Cada página vira um documento com as etapas ``layout`` e ``reading_order`` concluídas e as demais
não executadas. Fotos em que a retificação achou a folha levam o metadado ``rectification``; a
geometria já está nas coordenadas da foto original.

Limitação do contrato encontrada aqui: o LDF 2.0 aceita **um** componente por etapa, e o layout usa
dois modelos (linhas e blocos). Os dois são descritos num único componente composto.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from leitorum_di.contracts.ldf import (
    LDFValidationError,
    build_document,
    component,
    rectification_from_corners,
    validate,
)

CREATED_AT = "2026-10-12T00:00:00Z"


def layout_component(registry: dict[str, Any]) -> dict[str, str]:
    """Componente composto da etapa de layout, a partir de ``candidates.json``."""
    by_id = {c["id"]: c for c in registry["candidates"]}
    lines, blocks = by_id["docufcn-norhand-line"], by_id["heron"]
    statuses = {lines["license_status"], blocks["license_status"]}
    return component(
        "doc-ufcn norhand (linhas) + docling heron (blocos)",
        "ADR-002",
        revision=f"{lines['weights']['revision'][:8]}+{blocks['weights']['revision'][:8]}",
        license="BSD-3-Clause e MIT (Doc-UFCN); Apache-2.0 (Heron)",
        license_status="VERIFIED" if statuses == {"VERIFIED"} else "NEEDS VALIDATION",
    )


def order_component(method: str) -> dict[str, str]:
    return component(f"ordenador {method}", "ADR-003")


def page_document(
    page: dict[str, Any],
    lines: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
    order: list[int],
    layout: dict[str, str],
    orderer: dict[str, str],
    rectification: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Monta o documento LDF 2.0 de uma página; levanta ``ValueError`` se não for representável."""
    metadata = None
    if rectification and rectification.get("found"):
        metadata = rectification_from_corners(
            rectification["quad"], rectification["size"], "contorno da folha (OpenCV)"
        )
    return build_document(
        image={
            "filename": Path(page["image"]).name,
            "width": page["width"],
            "height": page["height"],
            "sha256": page["sha256"],
        },
        lines=[
            {"bbox": ln["bbox"], "polygon": ln.get("polygon"), "score": ln.get("score")}
            for ln in lines
        ],
        regions=[{"type": b["type"], "bbox": b["bbox"], "score": b.get("score")} for b in blocks],
        reading_order=order,
        stages={"layout": {"component": layout}, "reading_order": {"component": orderer}},
        rectification=metadata,
        created_at=CREATED_AT,
    )


def convert_all(items: list[dict[str, Any]], layout: dict[str, str], orderer: dict[str, str]):
    """Converte páginas; devolve contagens (documentos, válidos, não representáveis, regiões)."""
    counts = {"documents": 0, "valid": 0, "not_representable": 0, "regions": 0, "lines": 0}
    reasons: dict[str, int] = {}
    for item in items:
        counts["documents"] += 1
        try:
            document = page_document(layout=layout, orderer=orderer, **item)
        except (LDFValidationError, ValueError) as error:
            counts["not_representable"] += 1
            key = type(error).__name__
            if isinstance(error, LDFValidationError):
                key = "+".join(sorted({issue.code for issue in error.issues}))
            reasons[key] = reasons.get(key, 0) + 1
            continue
        if not validate(document):
            counts["valid"] += 1
        counts["regions"] += len(document["structure"]["regions"])
        counts["lines"] += len(document["recognition"]["lines"])
    return {**counts, "reasons": reasons}
