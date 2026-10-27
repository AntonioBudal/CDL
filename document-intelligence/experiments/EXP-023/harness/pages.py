# ruff: noqa: N803, N806, N815 — nomes em maiúscula seguem a notação da spec (A, S, T, F, W, X)
"""EXP-023: páginas de anotação compostas a partir dos trechos fictícios congelados (D-sintético).

Cada página sorteia trechos de um tema, escolhe um padrão de ordem das seções e um estilo de
escrita, e quebra o texto em linhas físicas como no caderno (sem linhas em branco, como sai do
leitor). A geometria (caixas das linhas) é simulada: passo de linha com variação, intervalo maior e
recuo em parágrafo novo.

Divisão por tema (semente fixa): 12 temas de treino, 4 de validação, 4 de teste; 6 páginas por tema.
Cada caractere carrega o rótulo da seção e o número do trecho de origem (para as métricas de
fronteira).
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from noise import corrupt

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
PAGES_PER_TOPIC = 6
HEADINGS = {
    "s": ["Resumo:", "## Resumo", "RESUMO"],
    "e": ["Explicação:", "## Explicação", "Desenvolvimento:"],
    "c": ["Conceitos:", "## Conceitos", "Termos-chave"],
    "r": ["Referências:", "## Referências", "Bibliografia"],
}
PATTERNS = [
    ("canonical", 0.35),
    ("summary_concepts_first", 0.15),
    ("interleaved", 0.2),
    ("concepts_first", 0.1),
    ("refs_inline", 0.2),
]
STYLES = [("corrido", 0.4), ("linhas", 0.35), ("telegrafico", 0.25)]


def verify_frozen() -> None:
    """Confere o SHA-256 dos dados congelados (com quebras de linha normalizadas para LF)."""
    for line in (DATA / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        content = (DATA / name).read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError(f"dado congelado alterado: {name}")


def load_topics() -> list[dict]:
    verify_frozen()
    topics = []
    for f in sorted((DATA / "sintetico").glob("temas-*.json")):
        topics.extend(json.loads(f.read_text(encoding="utf-8"))["topics"])
    return topics


def split_topics(topics: list[dict]) -> dict[str, list[dict]]:
    order = list(topics)
    random.Random(23).shuffle(order)
    return {"train": order[:12], "val": order[12:16], "test": order[16:20]}


def pick(weighted, rng):
    names, weights = zip(*weighted, strict=False)
    return rng.choices(names, weights=weights)[0]


def compose(topic: dict, rng: random.Random) -> list[tuple[str, str]]:
    """Sequência (rótulo, texto) da página, já no padrão de ordem sorteado."""
    pool = {lab: [text for tag, text in topic["units"] if tag == lab] for lab in "secr"}
    take = {
        "s": rng.randint(1, min(3, len(pool["s"]))),
        "e": rng.randint(2, min(6, len(pool["e"]))),
        "c": rng.randint(1, min(5, len(pool["c"]))),
        "r": rng.randint(0, min(3, len(pool["r"]))),
    }
    if rng.random() < 0.1:
        take["s"] = 0
    chosen = {lab: rng.sample(pool[lab], take[lab]) for lab in "secr"}
    S, E, C, R = ([(lab, t) for t in chosen[lab]] for lab in "secr")
    pattern = pick(PATTERNS, rng)
    if pattern == "canonical":
        seq = S + E + C + R
    elif pattern == "summary_concepts_first":
        seq = S + C + E + R
    elif pattern == "concepts_first":
        seq = C + S + E + R
    elif pattern == "interleaved":
        seq, e, c = list(S), list(E), list(C)
        while e or c:
            if e:
                k = rng.randint(1, min(2, len(e)))
                seq += e[:k]
                e = e[k:]
            if c:
                k = rng.randint(1, min(2, len(c)))
                seq += c[:k]
                c = c[k:]
        seq += R
    else:  # refs_inline: referências logo depois de explicações
        seq, r = list(S), list(R)
        for item in E:
            seq.append(item)
            if r and rng.random() < 0.5:
                seq.append(r.pop(0))
        seq += C + r
    return seq, pattern


def restyle(text: str, label: str, style: str, rng: random.Random) -> str:
    if style == "telegrafico" and label in "sec":
        if text.endswith(".") and rng.random() < 0.6:
            text = text[:-1]
        if rng.random() < 0.3 and text[:1].isupper() and not text[:2].isupper():
            text = text[0].lower() + text[1:]
        if rng.random() < 0.2:
            text = text.replace(",", "")
    if (
        style != "corrido"
        and label == "c"
        and rng.random() < 0.3
        and not text.lstrip().startswith(("-", "•"))
    ):
        text = "- " + text
    return text


def wrap(text: str, width: int) -> list[str]:
    lines, current = [], ""
    for word in text.split(" "):
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}" if current else word
    if current:
        lines.append(current)
    return lines


def render(seq, style: str, headings: bool, rng: random.Random) -> dict:
    """Quebra a página em linhas físicas, com rótulos por caractere e caixas simuladas."""
    width = rng.randint(40, 65)
    paragraphs: list[list[tuple[str, str, int]]] = []  # parágrafo = trechos (rótulo, texto, id)
    last_label = None
    for uid, (label, text) in enumerate(seq):
        text = restyle(text, label, style, rng)
        new_group = label != last_label
        if headings and new_group:
            paragraphs.append([(label, rng.choice(HEADINGS[label]), -1)])
        joinable = (
            style == "corrido"
            and label in "se"
            and not new_group
            and paragraphs
            and paragraphs[-1][-1][2] >= 0
        )
        if joinable and rng.random() < 0.8:
            paragraphs[-1].append((label, text, uid))
        else:
            paragraphs.append([(label, text, uid)])
        last_label = label
    lines, y = [], 140.0
    pitch = rng.uniform(68, 82)
    for p_index, para in enumerate(paragraphs):
        chars, labs, ids = [], [], []
        for k, (label, text, uid) in enumerate(para):
            if k:
                chars.append(" ")
                labs.append(label)
                ids.append(uid)
            chars.extend(text)
            labs.extend(label * len(text))
            ids.extend([uid] * len(text))
        flat = "".join(chars)
        pos = 0
        new_paragraph = p_index > 0
        indent = 60.0 if (style == "corrido" and new_paragraph and rng.random() < 0.4) else 0.0
        if new_paragraph:
            y += pitch * (rng.uniform(0.7, 1.4) if style == "corrido" else rng.uniform(0.0, 0.5))
        for k, piece in enumerate(wrap(flat, width)):
            start = flat.index(piece, pos)
            x0 = 120 + (indent if k == 0 else 0) + rng.uniform(-10, 10)
            x1 = min(1560.0, x0 + len(piece) * 23 * rng.uniform(0.9, 1.1))
            lines.append(
                {
                    "text": piece,
                    "labels": labs[start : start + len(piece)],
                    "units": ids[start : start + len(piece)],
                    "bbox": [round(x0), round(y), round(x1), round(y + pitch * 0.8)],
                }
            )
            pos = start + len(piece)
            y += pitch * rng.uniform(0.94, 1.06)
    return {"lines": lines}


def build_pages() -> dict[str, list[dict]]:
    topics = load_topics()
    out = {}
    for split, items in split_topics(topics).items():
        pages = []
        for topic in items:
            for k in range(PAGES_PER_TOPIC):
                rng = random.Random(f"{topic['id']}-{k}")
                seq, pattern = compose(topic, rng)
                style = pick(STYLES, rng)
                headings = pattern == "canonical" and rng.random() < 0.25
                page = render(seq, style, headings, rng)
                page.update(
                    id=f"{topic['id']}-p{k}",
                    topic=topic["id"],
                    pattern=pattern,
                    style=style,
                    headings=headings,
                )
                pages.append(page)
        out[split] = pages
    return out


def with_noise(page: dict, model: dict | None, cer: float) -> dict:
    """Página com erros de leitura aplicados linha a linha (rótulos e trechos acompanham)."""
    if not model or cer <= 0:
        return page
    rng = random.Random(f"{page['id']}-{cer}")
    lines = []
    for line in page["lines"]:
        tags = list(zip(line["labels"], line["units"], strict=False))
        text, out = corrupt(line["text"], tags, model, cer, rng)
        lines.append(
            {**line, "text": text, "labels": [a for a, _ in out], "units": [b for _, b in out]}
        )
    return {**page, "lines": lines}


def page_text(page: dict) -> tuple[str, list[str], list[int]]:
    """Texto da página (linhas unidas por quebra de linha) e rótulo/trecho por caractere."""
    text, labels, units = [], [], []
    for k, line in enumerate(page["lines"]):
        if k:
            text.append("\n")
            labels.append(labels[-1] if labels else "e")
            units.append(units[-1] if units else -1)
        text.append(line["text"])
        labels.extend(line["labels"])
        units.extend(line["units"])
    return "".join(text), labels, units


def layout(page: dict) -> list[dict]:
    return [{"text": ln["text"], "bbox": ln["bbox"], "confidence": None} for ln in page["lines"]]
