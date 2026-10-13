"""Correções humanas do LDF 2.0.

Cada correção aponta para um elemento pelo ``id`` (ou para uma coleção inteira) e traz operações
RFC 6902 com caminhos relativos a esse alvo. A posição do elemento no vetor só é resolvida na hora
de aplicar, de modo que uma correção continua válida depois que outra insere ou remove elementos.

O documento guardado é sempre a saída original do pipeline mais a lista de correções. A versão
corrigida é uma visão calculada por ``apply_corrections``; não deve ser gravada como documento LDF.
"""

from __future__ import annotations

import copy
from typing import Any

from leitorum_di.contracts.ldf.schema import pointer

# coleção → (caminho no documento, os itens têm ``id``?)
COLLECTIONS: dict[str, tuple[tuple[str, ...], bool]] = {
    "recognition.lines": (("recognition", "lines"), True),
    "structure.regions": (("structure", "regions"), True),
    "structure.reading_order": (("structure", "reading_order"), False),
    "structure.diagrams": (("structure", "diagrams"), True),
    "semantics.sections": (("semantics", "sections"), True),
    "semantics.entities": (("semantics", "entities"), True),
}


class CorrectionError(ValueError):
    """Uma correção não pôde ser aplicada; ``index`` é a posição em ``human_corrections``."""

    def __init__(self, index: int, message: str) -> None:
        super().__init__(f"correção {index}: {message}")
        self.index = index
        self.reason = message


def _tokens(path: str) -> list[str]:
    if path == "":
        return []
    if not path.startswith("/"):
        raise ValueError(f"caminho inválido: {path!r}")
    return [part.replace("~1", "/").replace("~0", "~") for part in path.split("/")[1:]]


def _index(token: str, size: int, *, allow_end: bool = False) -> int:
    if allow_end and token == "-":
        return size
    if not token.isdigit() or (len(token) > 1 and token[0] == "0"):
        raise LookupError(f"índice inválido: {token!r}")
    index = int(token)
    if index > size or (index == size and not allow_end):
        raise LookupError(f"índice fora do vetor: {token}")
    return index


def _get(document: Any, tokens: list[str]) -> Any:
    node = document
    for token in tokens:
        if isinstance(node, list):
            node = node[_index(token, len(node))]
        elif isinstance(node, dict):
            if token not in node:
                raise LookupError(f"campo inexistente: {token}")
            node = node[token]
        else:
            raise LookupError(f"caminho atravessa valor simples em {token!r}")
    return node


def _parent(document: Any, tokens: list[str]) -> tuple[Any, str]:
    if not tokens:
        raise ValueError("operação sobre a raiz do documento não é permitida")
    return _get(document, tokens[:-1]), tokens[-1]


def _add(document: Any, tokens: list[str], value: Any) -> None:
    parent, key = _parent(document, tokens)
    if isinstance(parent, list):
        parent.insert(_index(key, len(parent), allow_end=True), value)
    elif isinstance(parent, dict):
        parent[key] = value
    else:
        raise LookupError("o destino não é objeto nem vetor")


def _remove(document: Any, tokens: list[str]) -> Any:
    parent, key = _parent(document, tokens)
    if isinstance(parent, list):
        return parent.pop(_index(key, len(parent)))
    if isinstance(parent, dict) and key in parent:
        return parent.pop(key)
    raise LookupError(f"campo inexistente: {key}")


def _required(operation: dict[str, Any], field: str) -> Any:
    if field not in operation:
        raise ValueError(f"operação {operation['op']} exige o campo {field}")
    return operation[field]


def apply_operation(document: Any, operation: dict[str, Any]) -> None:
    """Aplica, no próprio ``document``, uma operação RFC 6902 de caminho absoluto."""
    op = operation["op"]
    tokens = _tokens(operation["path"])
    if op == "add":
        _add(document, tokens, copy.deepcopy(_required(operation, "value")))
    elif op == "remove":
        _remove(document, tokens)
    elif op == "replace":
        value = copy.deepcopy(_required(operation, "value"))
        _remove(document, tokens)
        _add(document, tokens, value)
    elif op == "move":
        origin = _tokens(_required(operation, "from"))
        if tokens[: len(origin)] == origin and len(tokens) > len(origin):
            raise ValueError("move para dentro do próprio elemento")
        _add(document, tokens, _remove(document, origin))
    elif op == "copy":
        _add(document, tokens, copy.deepcopy(_get(document, _tokens(_required(operation, "from")))))
    elif op == "test":
        if _get(document, tokens) != _required(operation, "value"):
            raise ValueError(f"teste falhou em {operation['path']}")
    else:
        raise ValueError(f"operação desconhecida: {op}")


def _prefix(document: dict[str, Any], target: dict[str, Any]) -> list[str]:
    """Caminho absoluto atual do alvo de uma correção."""
    keys, has_ids = COLLECTIONS[target["collection"]]
    node: Any = document
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            raise LookupError(f"coleção ausente no documento: {target['collection']}")
        node = node[key]
    if "id" not in target:
        return list(keys)
    if not has_ids:
        raise LookupError(f"{target['collection']} não tem elementos com id")
    for index, item in enumerate(node):
        if item.get("id") == target["id"]:
            return [*keys, str(index)]
    raise LookupError(f"alvo inexistente: {target['id']}")


def _run(document: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    working = copy.deepcopy(document)
    working["human_corrections"] = []
    patch: list[dict[str, Any]] = []
    for index, correction in enumerate(document["human_corrections"]):
        target = correction["target"]
        try:
            for operation in correction["ops"]:
                # O alvo é resolvido a cada operação: a anterior pode tê-lo movido ou removido.
                base = pointer(_prefix(working, target))
                if (
                    "id" in target
                    and operation["path"] == ""
                    and operation["op"]
                    in (
                        "add",
                        "move",
                        "copy",
                    )
                ):
                    raise ValueError(f"{operation['op']} não se aplica ao elemento inteiro")
                absolute: dict[str, Any] = {
                    "op": operation["op"],
                    "path": base + operation["path"],
                }
                if "from" in operation:
                    absolute["from"] = base + operation["from"]
                if "value" in operation:
                    absolute["value"] = copy.deepcopy(operation["value"])
                apply_operation(working, absolute)
                patch.append(absolute)
        except (LookupError, ValueError, TypeError) as error:
            raise CorrectionError(index, str(error)) from error
    return working, patch


def apply_corrections(document: dict[str, Any]) -> dict[str, Any]:
    """Devolve a visão corrigida (cópia); o documento recebido não é alterado.

    A visão sai com ``human_corrections`` vazio. Levanta ``CorrectionError`` se alguma correção
    não puder ser aplicada.
    """
    return _run(document)[0]


def to_json_patch(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Converte as correções em um JSON Patch RFC 6902 comum, de caminhos absolutos.

    Aplicar o resultado, em ordem, sobre a saída original produz a mesma visão corrigida.
    """
    return _run(document)[1]
