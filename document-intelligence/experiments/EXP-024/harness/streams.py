"""EXP-024: fluxos longitudinais de páginas fictícias por perfil de leitor.

Cada perfil tem dois fluxos independentes, um de validação e um de teste, com livros diferentes.
Cada fluxo tem 40 páginas de adaptação (em ordem, t = 1..40, intercalando os 2 livros) e 12 páginas
*holdout* por livro.

Para não haver vazamento entre adaptação e *holdout*, os modelos de frase, os termos definidos em
Conceitos, as obras citadas e as citações são divididos por *hash* em dois grupos (70/30). O livro
principal só aparece como referência na adaptação. A quebra em linhas e as caixas simuladas
reaproveitam ``render`` do EXP-023.

Tudo é determinístico: a mesma semente monta as mesmas páginas.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import sys
import unicodedata
from functools import cache, lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
DATA = EXP / "data"
EXP023_HARNESS = EXP.parent / "EXP-023" / "harness"
if str(EXP023_HARNESS) not in sys.path:
    sys.path.insert(0, str(EXP023_HARNESS))

import pages as base_pages  # noqa: E402  (render, page_text e layout do EXP-023)

SECTIONS = ("summary", "explanation", "concepts", "references")
CODE = {"summary": "s", "explanation": "e", "concepts": "c", "references": "r"}
SPLITS = ("val", "test")
ADAPT_PAGES = 40
HOLDOUT_PER_BOOK = 12
ADAPT_SHARE = 7  # em 10: fração de modelos, termos, obras e citações reservados à adaptação
HOLDOUT_TERMS = 3  # de 8 termos por livro, os definidos em Conceitos no holdout
HOLDOUT_WORKS = 2  # de 5 obras relacionadas por livro
RENDER_STYLE = {"corrido": "corrido", "telegrafico": "telegrafico", "lista": "linhas"}
MAIN_BOOK_REFERENCE = 0.3


def verify_frozen() -> None:
    """Confere o SHA-256 dos dados congelados (quebras de linha normalizadas para LF)."""
    for line in (DATA / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        content = (DATA / name).read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError(f"dado congelado alterado: {name}")


def _json(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load() -> dict:
    verify_frozen()
    return {
        "books": {b["id"]: b for b in _json("livros.json")["books"]},
        "profiles": {p["id"]: p for p in _json("perfis.json")["profiles"]},
        "phrases": _json("frases/secoes.json"),
        "references": _json("frases/referencias.json"),
        "rewrites": _json("frases/reescritas.json")["rewrites"],
        "writers": _json("confusoes-escritores.json")["writers"],
        "canary": _json("canario.json"),
    }


def _digest(*parts: object) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()


def pool_of(*parts: object) -> str:
    return "adapt" if int(_digest(*parts)[:8], 16) % 10 < ADAPT_SHARE else "holdout"


def _split_by_hash(items: list, key, holdout: int, salt: str) -> dict[str, list]:
    ranked = sorted(items, key=lambda item: _digest(salt, key(item)))
    return {"holdout": ranked[:holdout], "adapt": ranked[holdout:]}


def fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", fold(text)).strip("-")


def pick(weights: dict[str, float], rng: random.Random) -> str:
    names = sorted(weights)
    return rng.choices(names, weights=[weights[n] for n in names])[0]


# --- vocabulário de cada livro, dividido entre adaptação e holdout -----------------------------


@cache
def book_pools(book_id: str) -> dict:
    book = load()["books"][book_id]
    terms = [tuple(t) for t in book["terms"]]
    works = [tuple(w) for w in book["related"]]
    return {
        "terms": _split_by_hash(terms, lambda t: t[0], HOLDOUT_TERMS, f"term-{book_id}"),
        "works": _split_by_hash(works, lambda w: w[0], HOLDOUT_WORKS, f"work-{book_id}"),
        "all_terms": terms,
    }


@cache
def template_pools() -> dict:
    """Modelos de frase por seção, registro e grupo (adapt/holdout), com recuo se faltar."""
    phrases = load()["phrases"]
    out: dict = {}
    for section in ("summary", "explanation", "concepts"):
        by: dict = {}
        for register, template in phrases[section]:
            by.setdefault((register, pool_of(section, register, template)), []).append(template)
        out[section] = by
    quotes = phrases["quotes"]
    out["quotes"] = {
        pool: [q for q in quotes if pool_of("quote", q) == pool] for pool in ("adapt", "holdout")
    }
    return out


def _templates(section: str, register: str, pool: str) -> list[str]:
    by = template_pools()[section]
    found = by.get((register, pool))
    if found:
        return found
    # sem modelo daquele registro no grupo: usa outro registro do mesmo grupo (nunca o outro grupo)
    return [t for (_reg, grp), items in sorted(by.items()) if grp == pool for t in items]


def _capitalize(text: str) -> str:
    return text[:1].upper() + text[1:]


def fill(
    template: str, book: dict, terms: list[tuple[str, str]], all_terms, rng: random.Random
) -> str:
    term, gloss = rng.choice(terms)
    others = [t for t, _ in all_terms if t != term]
    second = rng.choice(others) if others else term
    surname = book["author"].split()[-1]
    values = {
        "termo": term,
        "Termo": _capitalize(term),
        "termo2": second,
        "glosa": gloss,
        "titulo": book["title"],
        "autor": book["author"],
        "sobrenome": surname,
        "capitulo": str(rng.randint(1, len(book["chapters"]))),
        "pag": str(rng.randint(9, 280)),
    }
    return re.sub(r"\{(\w+)\}", lambda m: values[m.group(1)], template)


def reference_line(profile: dict, book: dict, pool: str, rng: random.Random) -> str:
    refs = load()["references"]
    fmt = pick(profile["references"], rng)
    pools = book_pools(book["id"])
    if fmt == "quote":
        quote = rng.choice(template_pools()["quotes"][pool])
        return fill(quote, book, pools["all_terms"], pools["all_terms"], rng)
    if pool == "adapt" and rng.random() < MAIN_BOOK_REFERENCE:
        title, author, year = book["title"], book["author"], book["year"]
        city, publisher = book["city"], book["publisher"]
    else:
        title, author, year = rng.choice(pools["works"][pool])
        k = int(_digest("editora", title)[:8], 16)
        city = refs["cities"][k % len(refs["cities"])]
        publisher = refs["publishers"][(k // 7) % len(refs["publishers"])]
    names = author.split()
    values = {
        "titulo": title,
        "autor": author,
        "ano": str(year),
        "SOBRENOME": names[-1].upper(),
        "prenome": " ".join(names[:-1]),
        "cidade": city,
        "editora": publisher,
        "url": f"https://exemplo.org/{slug(title)}",
        "pag": str(rng.randint(9, 280)),
    }
    return re.sub(r"\{(\w+)\}", lambda m: values[m.group(1)], refs["formats"][fmt])


# --- composição e montagem da página ---------------------------------------------------------


def _order(pattern: str, units: dict[str, list], rng: random.Random) -> list:
    summ, expl, conc, refs = (units[s] for s in SECTIONS)
    if pattern == "canonical":
        return summ + expl + conc + refs
    if pattern == "summary_concepts_first":
        return summ + conc + expl + refs
    if pattern == "concepts_first":
        return conc + summ + expl + refs
    if pattern == "interleaved":
        seq, e, c = list(summ), list(expl), list(conc)
        while e or c:
            if e:
                k = rng.randint(1, min(2, len(e)))
                seq, e = seq + e[:k], e[k:]
            if c:
                k = rng.randint(1, min(2, len(c)))
                seq, c = seq + c[:k], c[k:]
        return seq + refs
    if pattern == "refs_inline":
        seq, r = list(summ), list(refs)
        for item in expl:
            seq.append(item)
            if r and rng.random() < 0.5:
                seq.append(r.pop(0))
        return seq + conc + r
    raise ValueError(f"padrão desconhecido: {pattern}")


def compose(profile: dict, book: dict, pool: str, rng: random.Random) -> tuple[list, str]:
    pools = book_pools(book["id"])
    units: dict[str, list] = {s: [] for s in SECTIONS}
    for section in SECTIONS:
        low, high = profile["counts"][section]
        for _ in range(rng.randint(low, high)):
            if section == "references":
                text = reference_line(profile, book, pool, rng)
            else:
                register = pick(profile["style"], rng)
                if section == "explanation" and rng.random() < profile["reflexao"]:
                    register = "reflexao"
                template = rng.choice(_templates(section, register, pool))
                terms = pools["terms"][pool] if section == "concepts" else pools["all_terms"]
                text = fill(template, book, terms, pools["all_terms"], rng)
            units[section].append((CODE[section], text))
    pattern = pick(profile["order"], rng)
    return _order(pattern, units, rng), pattern


def make_page(profile: dict, book: dict, split: str, role: str, index: int) -> dict:
    rng = random.Random(f"exp024-{split}-{profile['id']}-{role}-{book['id']}-{index}")
    seq, pattern = compose(profile, book, "adapt" if role == "adapt" else "holdout", rng)
    style = pick(profile["style"], rng)
    page = base_pages.render(seq, RENDER_STYLE[style], False, rng)
    page.update(
        id=f"{split}-{profile['id']}-{role}-{book['id']}-{index:03d}",
        profile=profile["id"],
        book_id=book["id"],
        split=split,
        role=role,
        pattern=pattern,
        style=style,
        source_units=[
            {"uid": uid, "section": label, "text": text} for uid, (label, text) in enumerate(seq)
        ],
    )
    return page


def books_of(profile_id: str, split: str) -> list[dict]:
    books = [
        b for b in load()["books"].values() if b["profile"] == profile_id and b["split"] == split
    ]
    return sorted(books, key=lambda b: b["id"])


@cache
def stream(profile_id: str, split: str) -> dict:
    """Fluxo de um perfil: 40 páginas de adaptação em ordem e 12 holdout por livro."""
    if split not in SPLITS:
        raise ValueError(f"split desconhecido: {split}")
    profile = load()["profiles"][profile_id]
    books = books_of(profile_id, split)
    order = [b for b in books for _ in range(ADAPT_PAGES // len(books))]
    random.Random(f"exp024-order-{split}-{profile_id}").shuffle(order)
    adapt = []
    for t, book in enumerate(order, start=1):
        page = make_page(profile, book, split, "adapt", t)
        page["t"] = t
        adapt.append(page)
    holdout = {
        b["id"]: [make_page(profile, b, split, "holdout", k) for k in range(HOLDOUT_PER_BOOK)]
        for b in books
    }
    return {
        "profile": profile_id,
        "split": split,
        "books": [b["id"] for b in books],
        "adapt": adapt,
        "holdout": holdout,
    }


def all_streams(split: str) -> dict[str, dict]:
    return {pid: stream(pid, split) for pid in sorted(load()["profiles"])}


def page_text(page: dict) -> tuple[str, list[str], list[int]]:
    return base_pages.page_text(page)


def layout(page: dict) -> list[dict]:
    return base_pages.layout(page)
