"""EXP-024: simulador determinístico de leitura ruidosa e de sessões de revisão do leitor.

Uma sessão segue o fluxo do produto (features 086 e 089):

1. a página é lida com erro: primeiro os confundidores recorrentes do escritor (SINTÉTICOS,
   declarados em ``data/confusoes-escritores.json``), depois o modelo global por caractere do
   EXP-015 (via EXP-023);
2. cada linha recebe uma confiança, mais baixa quanto mais erros tem (calibrada na 086);
3. o motor pode pós-corrigir a leitura (``reader``); o leitor simulado corrige parte das palavras
   erradas;
4. o Organizador sugere as 4 seções (``organize``); o leitor move parte dos trechos errados;
5. o leitor salva. O pacote ``leitorum-feedback/1`` é o que o motor pode ver; a verdade fica à
   parte.

Regimes: R1 (implícito puro), R2 (R1 + nota 1–5 coerente), R3 (R2 com 20 % de páginas ruidosas: nota
contraditória, salva sem revisar ou com reescrita autoral livre).
"""

from __future__ import annotations

import difflib
import json
import math
import random
import sys
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import streams  # noqa: E402  (também põe o harness do EXP-023 no caminho)
from noise import corrupt  # noqa: E402

DI = streams.EXP.parents[1]
NOISE_MODEL = DI / "dataset" / "processed" / "exp-023" / "noise-model.json"
LABEL = {"s": "summary", "e": "explanation", "c": "concepts", "r": "references"}
REGIMES = ("R1", "R2", "R3")
NOISY_SHARE = 0.2
NOISY_KINDS = ("contradict", "blind", "rewrite")
LOW_CONFIDENCE = 0.75  # limiar da 086

# Confiança da linha: Beta com média CONF_BASE - CONF_SLOPE * (erro da linha), concentração CONF_K.
# Calibrada só nos fluxos de validação (grade de 36 pontos, 2026-10-28) para reproduzir a 086
# (20,7 % das linhas abaixo de 0,75; CER 43,5 % nelas contra 23,7 % nas demais): ficou 20,0 %,
# 40,5 % e 21,8 % (test_simulator.py).
CONF_BASE = 1.0
CONF_SLOPE = 0.6
CONF_K = 16.0
# Dificuldade por linha: na leitura real, algumas linhas saem muito piores que outras. O erro
# global de cada linha é multiplicado por um fator log-normal de média 1 (desvio LINE_SPREAD no
# log), preso em [0,15; 3].
LINE_SPREAD = 0.6


@dataclass(frozen=True)
class Behaviour:
    """Probabilidades do leitor simulado (R1); R2 e R3 partem destas."""

    move_review: float = 0.85  # trecho marcado "conferir" e errado: move para a seção certa
    move_other: float = 0.45  # trecho errado sem marcação
    fix_flagged: float = 0.9  # palavra lida errada numa linha de baixa confiança
    fix_other: float = 0.55  # palavra lida errada nas demais linhas
    revert_base: float = 0.03  # "Voltar para texto único" sem motivo aparente
    revert_bad: float = 0.3  # ... quando a sugestão acerta menos da metade
    rating_noise: float = 0.35


# --- leitura ruidosa -----------------------------------------------------------------------------


@lru_cache(maxsize=1)
def noise_model() -> dict:
    return json.loads(NOISE_MODEL.read_text(encoding="utf-8"))


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def apply_writer(text: str, tags: list, rules: list[dict], rng: random.Random) -> tuple[str, list]:
    """Confundidores recorrentes do escritor; ``tags`` acompanham cada caractere."""
    out_text, out_tags, i = [], [], 0
    while i < len(text):
        for rule in rules:
            src = rule["src"]
            if not text.startswith(src, i):
                continue
            after = text[i + len(src) : i + len(src) + 1]
            if rule["where"] == "end" and after.isalpha():
                continue
            if rng.random() < rule["p"]:
                out_text.append(rule["dst"])
                out_tags.extend([tags[i]] * len(rule["dst"]))
                i += len(src)
                break
        else:
            out_text.append(text[i])
            out_tags.append(tags[i])
            i += 1
    return "".join(out_text), out_tags


@cache
def writer_rate(writer: str, split: str) -> float:
    """CER médio causado só pelos confundidores do escritor, no split (determinístico)."""
    rules = streams.load()["writers"][writer]
    errors = chars = 0
    for st in streams.all_streams(split).values():
        if streams.load()["profiles"][st["profile"]]["writer"] != writer:
            continue
        for page in st["adapt"]:
            rng = random.Random(f"writer-rate-{page['id']}")
            for line in page["lines"]:
                noisy, _ = apply_writer(line["text"], [None] * len(line["text"]), rules, rng)
                errors += levenshtein(line["text"], noisy)
                chars += len(line["text"])
    return errors / max(1, chars)


def read_page(page: dict, cer: float, seed: str = "") -> list[dict]:
    """Linhas lidas com erro: ``text`` (lido), ``truth`` (limpo), rótulos, caixas e confiança."""
    profile = streams.load()["profiles"][page["profile"]]
    rules = streams.load()["writers"][profile["writer"]]
    rng = random.Random(f"read-{page['id']}-{cer}-{seed}")
    global_cer = max(0.0, cer - writer_rate(profile["writer"], page["split"])) if cer > 0 else 0.0
    out = []
    for line in page["lines"]:
        tags = list(zip(line["labels"], line["units"], strict=False))
        text, tags = (
            apply_writer(line["text"], tags, rules, rng) if cer > 0 else (line["text"], tags)
        )
        spread = math.exp(rng.gauss(-(LINE_SPREAD**2) / 2, LINE_SPREAD)) if global_cer > 0 else 1.0
        text, tags = corrupt(
            text, tags, noise_model(), global_cer * min(3.0, max(0.15, spread)), rng
        )
        line_cer = levenshtein(line["text"], text) / max(1, len(line["text"]))
        mean = min(0.98, max(0.05, CONF_BASE - CONF_SLOPE * line_cer))
        confidence = rng.betavariate(mean * CONF_K, (1 - mean) * CONF_K)
        out.append(
            {
                "text": text,
                "truth": line["text"],
                "truth_labels": line["labels"],
                "bbox": line["bbox"],
                "confidence": round(confidence, 4),
            }
        )
    return out


# --- alinhamentos usados pelo leitor simulado ----------------------------------------------------


def fix_words(shown: str, truth: str, probability: float, rng: random.Random) -> str:
    """O leitor corrige cada trecho de palavras errado com a probabilidade dada."""
    a, b = shown.split(" "), truth.split(" ")
    out: list[str] = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal" or rng.random() >= probability:
            out.extend(a[i1:i2])
        else:
            out.extend(b[j1:j2])
    return " ".join(out)


def transfer_labels(truth: str, labels: list[str], text: str) -> list[str]:
    """Rótulo de cada caractere de ``text`` pelo alinhamento com a linha verdadeira."""
    out: list[str] = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(
        None, truth, text, autojunk=False
    ).get_opcodes():
        if op in ("equal", "replace"):
            span = labels[i1:i2] or [labels[min(i1, len(labels) - 1)]]
            out.extend(
                span[min(k * len(span) // max(1, j2 - j1), len(span) - 1)] for k in range(j2 - j1)
            )
        elif op == "insert":
            near = labels[i1 - 1] if i1 > 0 else labels[0]
            out.extend([near] * (j2 - j1))
    return out


def majority(labels: list[str]) -> str:
    return Counter(labels).most_common(1)[0][0] if labels else "e"


def char_accuracy(segments: list[dict], sections: list[str], char_labels: list[str]) -> float:
    right = total = 0
    for seg, section in zip(segments, sections, strict=False):
        for k in range(seg["start"], seg["end"]):
            total += 1
            right += LABEL[char_labels[k]] == section
    return right / max(1, total)


# --- sessão -------------------------------------------------------------------------------------


def noisy_plan(pages: list[dict], regime: str, seed: str = "") -> dict[str, str]:
    """Páginas ruidosas do R3: exatamente 20 % das páginas, com os 3 tipos em rodízio."""
    if regime != "R3":
        return {}
    rng = random.Random(f"noisy-{seed}-{len(pages)}-{pages[0]['id'] if pages else ''}")
    chosen = sorted(rng.sample(range(len(pages)), round(NOISY_SHARE * len(pages))))
    return {pages[i]["id"]: NOISY_KINDS[k % len(NOISY_KINDS)] for k, i in enumerate(chosen)}


def session(
    page: dict,
    regime: str,
    organize: Callable[[str, list[dict], str], dict],
    reader: Callable[[list[dict], str], list[str]] | None = None,
    cer: float = 0.25,
    noisy: str | None = None,
    behaviour: Behaviour | None = None,
    seed: str = "",
) -> tuple[dict, dict]:
    """Uma página revisada e salva. Devolve (pacote de feedback, verdade para as métricas)."""
    if regime not in REGIMES:
        raise ValueError(f"regime desconhecido: {regime}")
    behaviour = behaviour or Behaviour()
    rng = random.Random(f"session-{page['id']}-{regime}-{cer}-{seed}")
    lines = read_page(page, cer, seed)
    shown = reader(lines, page["book_id"]) if reader else [ln["text"] for ln in lines]
    blind = noisy == "blind"

    # 1. o leitor corrige a leitura (antes de organizar, como a tela sugere)
    user_lines = []
    for line, text in zip(lines, shown, strict=False):
        p = behaviour.fix_flagged if line["confidence"] < LOW_CONFIDENCE else behaviour.fix_other
        user_lines.append(text if blind else fix_words(text, line["truth"], p, rng))
    char_labels: list[str] = []
    for k, (line, text) in enumerate(zip(lines, user_lines, strict=False)):
        if k:
            char_labels.append(char_labels[-1] if char_labels else "e")
        char_labels.extend(transfer_labels(line["truth"], line["truth_labels"], text))
    user_text = "\n".join(user_lines)
    layout = [
        {"text": t, "bbox": ln["bbox"], "confidence": ln["confidence"]}
        for ln, t in zip(lines, user_lines, strict=False)
    ]

    # 2. o Organizador sugere; o leitor confere e move
    result = organize(user_text, layout, page["book_id"])
    segments = result["segments"]
    truth_sections = [LABEL[majority(char_labels[s["start"] : s["end"]])] for s in segments]
    suggested = [s["section"] for s in segments]
    quality = char_accuracy(segments, suggested, char_labels)
    final, clicks = list(suggested), []
    if not blind:
        for k, seg in enumerate(segments):
            if suggested[k] == truth_sections[k]:
                continue
            p = behaviour.move_review if seg["review"] else behaviour.move_other
            if rng.random() < p:
                final[k] = truth_sections[k]
                if seg["review"]:
                    clicks.append({"index": seg["index"], "to": final[k]})
    reverted = not blind and rng.random() < (
        behaviour.revert_bad if quality < 0.5 else behaviour.revert_base
    )

    # 3. reescrita autoral (R3): o leitor troca trechos por texto seu
    texts = [user_text[s["start"] : s["end"]] for s in segments]
    rewritten: list[int] = []
    if noisy == "rewrite" and segments:
        rewrites = streams.load()["rewrites"]
        for k in sorted(rng.sample(range(len(segments)), min(2, len(segments)))):
            texts[k] = rng.choice(rewrites)
            rewritten.append(k)

    # 4. salvar
    if reverted:
        saved = dict.fromkeys(streams.SECTIONS, "")
        saved["explanation"] = user_text
        clicks = []
    else:
        parts: dict[str, list[str]] = {s: [] for s in streams.SECTIONS}
        for k in range(len(segments)):
            parts[final[k]].append(texts[k])
        saved = {s: "\n".join(v) for s, v in parts.items()}
    rating = None
    if regime in ("R2", "R3"):
        rating = max(1, min(5, round(1 + 4 * quality + rng.gauss(0, behaviour.rating_noise))))
        if noisy == "contradict":
            rating = 6 - rating
    user_id = f"u-{page['profile']}-{page['split']}"
    feedback = {
        "schema": "leitorum-feedback/1",
        "user_id": user_id,
        "book_id": page["book_id"],
        "page_id": page["id"],
        "organizer": {
            "suggested": {
                "segments": [
                    {k: s[k] for k in ("index", "start", "end", "section", "review")}
                    for s in segments
                ]
            },
            "reverted": reverted,
            "clicks": clicks,
            "text": user_text,
            "layout": layout,
        },
        "reading": {
            "source_lines": [ln["text"] for ln in lines],
            "shown_lines": list(shown),
            "line_confidence": [ln["confidence"] for ln in lines],
        },
        "saved": saved,
        "rating": rating,
    }
    truth = {
        "noisy": noisy,
        "quality": quality,
        "truth_sections": truth_sections,
        "final_sections": final,
        "rewritten": rewritten,
        "clean_lines": [ln["truth"] for ln in lines],
        "user_lines": user_lines,
        "char_labels": char_labels,
    }
    return feedback, truth


# --- organizador estático (V4 do EXP-023) para os testes e a linha de base ------------------


@lru_cache(maxsize=1)
def static_organizer():
    import organizer as org

    path = streams.EXP.parent / "EXP-023" / "artifacts" / "organizer-v1.json"
    return org.Organizer(org.Model.from_json(json.loads(path.read_text(encoding="utf-8"))))


def static_organize(text: str, layout: list[dict], _book_id: str) -> dict:
    return static_organizer().organize(text, layout)
