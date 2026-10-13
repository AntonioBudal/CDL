"""Avaliação da ordem de leitura sobre layout verdadeiro e sobre layout detectado.

Layout verdadeiro: blocos e linhas do manifesto (com a que bloco cada linha pertence).
Layout detectado: blocos e linhas preditos; os blocos são casados com os verdadeiros (IoU ≥ 0,5,
sem olhar o tipo) e a sequência prevista é reescrita com os ids verdadeiros. Blocos previstos sem
par viram ids ``x<n>`` (sobras) e blocos verdadeiros sem par simplesmente faltam na sequência —
ambos entram na distância de edição.

Decomposição da perda (por página, agregada por soma): ``full`` usa a sequência inteira;
``matched`` restringe as duas sequências aos blocos casados (isola o erro de ordenação).
"""

from __future__ import annotations

import statistics
import time
from typing import Any

from orderers import OrderParams, assign_lines, order_blocks, order_lines

from leitorum_di.metrics.detection import match_detections
from leitorum_di.metrics.ordering import kendall_tau, order_edit_counts, out_of_order


def true_layout(page: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    """Blocos e linhas verdadeiros, com o índice do bloco em cada linha."""
    index = {block["id"]: i for i, block in enumerate(page["blocks"])}
    blocks = [{"id": b["id"], "type": b["type"], "bbox": b["bbox"]} for b in page["blocks"]]
    lines = [
        {
            "id": ln["id"],
            "bbox": ln["bbox"],
            "polygon": ln["polygon"],
            "block": index[ln["block_id"]],
        }
        for ln in page["lines"]
    ]
    return blocks, lines


def true_line_order(page: dict[str, Any]) -> list[str]:
    by_id = {block["id"]: block for block in page["blocks"]}
    return [line for block_id in page["reading_order"] for line in by_id[block_id]["line_ids"]]


def predict_sequences(
    blocks: list[dict], lines: list[dict], params: OrderParams
) -> tuple[list[int], list[int]]:
    """Ordem dos blocos e ordem global das linhas (índices), seguindo a ordem dos blocos."""
    block_order = order_blocks(blocks, lines, params)
    membership = assign_lines(blocks, lines)
    line_order: list[int] = []
    for block_index in block_order:
        members = [i for i, owner in enumerate(membership) if owner == block_index]
        line_order.extend(members[k] for k in order_lines([lines[i] for i in members]))
    orphans = [i for i, owner in enumerate(membership) if owner is None]
    line_order.extend(sorted(orphans, key=lambda i: (lines[i]["bbox"][1], lines[i]["bbox"][0])))
    return block_order, line_order


def _rewrite(order: list[int], predicted: list[dict], truths: list[dict], prefix: str):
    """Reescreve índices previstos com ids verdadeiros; devolve (sequência, ids casados)."""
    matches = match_detections([t["bbox"] for t in truths], [p["bbox"] for p in predicted], 0.5)
    to_truth = {pi: truths[ti]["id"] for ti, pi, _ in matches}
    sequence = [to_truth.get(i, f"{prefix}{i}") for i in order]
    return sequence, set(to_truth.values())


def evaluate_page(
    page: dict[str, Any],
    params: OrderParams,
    detected: dict[str, Any] | None = None,
    repeats: int = 3,
) -> dict[str, Any]:
    """Avalia uma página. Sem ``detected``, usa o layout verdadeiro."""
    truth_blocks = page["reading_order"]
    truth_lines = true_line_order(page)
    if detected is None:
        blocks, lines = true_layout(page)
    else:
        blocks = [{"type": b["type"], "bbox": b["bbox"]} for b in detected["blocks"]]
        lines = [{"bbox": ln["bbox"], "polygon": ln.get("polygon")} for ln in detected["lines"]]

    timings = []
    for _ in range(repeats):
        started = time.perf_counter_ns()
        block_order, line_order = predict_sequences(blocks, lines, params)
        timings.append((time.perf_counter_ns() - started) / 1e6)

    if detected is None:
        block_sequence = [blocks[i]["id"] for i in block_order]
        line_sequence = [lines[i]["id"] for i in line_order]
        matched_blocks = set(truth_blocks)
        matched_lines = set(truth_lines)
    else:
        block_sequence, matched_blocks = _rewrite(block_order, blocks, page["blocks"], "x")
        line_sequence, matched_lines = _rewrite(line_order, lines, page["lines"], "y")

    def restricted(sequence, truth, matched):
        return [s for s in sequence if s in matched], [t for t in truth if t in matched]

    blocks_matched = restricted(block_sequence, truth_blocks, matched_blocks)
    lines_matched = restricted(line_sequence, truth_lines, matched_lines)
    types = {block["id"]: block["type"] for block in page["blocks"]}
    anchored = {block["id"] for block in page["blocks"] if block.get("anchor")}
    displaced = out_of_order(block_sequence, truth_blocks)
    return {
        "id": page["id"],
        "family": page.get("family", "single"),
        "level": page["level"],
        "blocks_full": order_edit_counts(block_sequence, truth_blocks),
        "blocks_matched": order_edit_counts(*blocks_matched),
        "lines_full": order_edit_counts(line_sequence, truth_lines),
        "lines_matched": order_edit_counts(*lines_matched),
        "tau_blocks": kendall_tau(block_sequence, truth_blocks),
        "truth_blocks": len(truth_blocks),
        "predicted_blocks": len(block_sequence),
        "unmatched_predicted": sum(1 for s in block_sequence if s not in matched_blocks),
        "unmatched_truth": len(truth_blocks) - len(matched_blocks),
        "displaced_types": [("lateral:" if b in anchored else "") + types[b] for b in displaced],
        "order_ms": statistics.median(timings),
    }


def _ratio(pages: list[dict], key: str) -> float | None:
    distance = sum(p[key][0] for p in pages)
    total = sum(p[key][1] for p in pages)
    return None if total == 0 else 1.0 - distance / total


def summarize(pages: list[dict]) -> dict[str, Any]:
    """Agrega páginas: acurácias (soma das distâncias / soma dos comprimentos) e contagens."""
    if not pages:
        return {"pages": 0}
    taus = [p["tau_blocks"] for p in pages if p["tau_blocks"] is not None]
    return {
        "pages": len(pages),
        "blocks_accuracy": _ratio(pages, "blocks_full"),
        "blocks_accuracy_matched": _ratio(pages, "blocks_matched"),
        "lines_accuracy": _ratio(pages, "lines_full"),
        "lines_accuracy_matched": _ratio(pages, "lines_matched"),
        "perfect_pages": sum(1 for p in pages if p["blocks_full"][0] == 0) / len(pages),
        "tau_blocks_mean": statistics.fmean(taus) if taus else None,
        "unmatched_predicted": sum(p["unmatched_predicted"] for p in pages),
        "unmatched_truth": sum(p["unmatched_truth"] for p in pages),
        "truth_blocks": sum(p["truth_blocks"] for p in pages),
        "order_ms_median": statistics.median(p["order_ms"] for p in pages),
        "order_ms_max": max(p["order_ms"] for p in pages),
    }


def evaluate_manifest(
    manifest: dict[str, Any],
    params: OrderParams,
    detected: dict[str, dict[str, Any]] | None = None,
    repeats: int = 3,
) -> dict[str, Any]:
    pages = [
        evaluate_page(page, params, None if detected is None else detected[page["id"]], repeats)
        for page in manifest["pages"]
        if detected is None or page["id"] in detected
    ]
    groups: dict[str, dict[str, list[dict]]] = {"family": {}, "level": {}}
    for page in pages:
        groups["family"].setdefault(page["family"], []).append(page)
        groups["level"].setdefault(page["level"], []).append(page)
    return {
        "overall": summarize(pages),
        "by_family": {k: summarize(v) for k, v in sorted(groups["family"].items())},
        "by_level": {k: summarize(v) for k, v in sorted(groups["level"].items())},
        "per_page": pages,
    }
