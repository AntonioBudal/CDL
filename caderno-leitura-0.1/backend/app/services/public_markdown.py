"""F0.12.02 (spec 115): Markdown restrito para as páginas públicas (`/compartilhado/{id}`).

Regra de segurança: **tudo é escapado antes**; só depois entram marcações conhecidas (títulos, parágrafos, listas,
citações, código, negrito, itálico e links `http(s)`). Nada do texto vira HTML ativo; imagens não saem (as do acervo
são privadas). Menções: `[[conceito:X]]` vira só o termo; `[[Título|id]]` só vira link se o estudo citado estiver
publicado (o chamador decide por `link_for_study`).
"""
from __future__ import annotations

import html
import re
from collections.abc import Callable

LinkForStudy = Callable[[int], str | None]

FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
QUOTE = re.compile(r"^\s{0,3}>\s?(.*)$")
UL_ITEM = re.compile(r"^\s{0,3}[-*+]\s+(.*)$")
OL_ITEM = re.compile(r"^\s{0,3}\d{1,9}[.)]\s+(.*)$")
RULE = re.compile(r"^\s{0,3}([-*_])(\s*\1){2,}\s*$")

IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
CONCEPT = re.compile(r"\[\[\s*conceito\s*:\s*([^\]|]+?)\s*\]\]", re.IGNORECASE)
MENTION = re.compile(r"\[\[([^\]|]+?)(?:\s*\|\s*(\d+))?\s*\]\]")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
CODE_SPAN = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"(\*\*|__)(?=\S)(.+?)(?<=\S)\1")
ITALIC = re.compile(r"(?<![*\w])([*_])(?=\S)(.+?)(?<=\S)\1(?![*\w])")
SAFE_URL = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)
LINK_REL = 'rel="nofollow ugc noopener noreferrer"'


def _inline(raw: str, link_for_study: LinkForStudy) -> str:
    text = IMAGE.sub("", raw)
    text = html.escape(text, quote=True)  # escape primeiro: daqui em diante só entram marcações conhecidas
    protected: list[str] = []

    def keep(fragment: str) -> str:
        protected.append(fragment)
        return f"\x00{len(protected) - 1}\x00"

    text = CODE_SPAN.sub(lambda m: keep(f"<code>{m.group(1)}</code>"), text)
    text = CONCEPT.sub(lambda m: m.group(1), text)

    def mention(m: re.Match) -> str:
        title = m.group(1).strip()
        target = int(m.group(2)) if m.group(2) else None
        url = link_for_study(target) if target else None
        return keep(f'<a href="{html.escape(url, quote=True)}">{title}</a>') if url else title

    text = MENTION.sub(mention, text)

    def link(m: re.Match) -> str:
        label, url = m.group(1), html.unescape(m.group(2))
        if not SAFE_URL.match(url):
            return label  # javascript:, data:, relativo… → só o texto
        return keep(f'<a href="{html.escape(url, quote=True)}" {LINK_REL}>{label}</a>')

    text = LINK.sub(link, text)
    text = BOLD.sub(lambda m: f"<strong>{m.group(2)}</strong>", text)
    text = ITALIC.sub(lambda m: f"<em>{m.group(2)}</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: protected[int(m.group(1))], text)


def render_public_markdown(source: str | None, link_for_study: LinkForStudy | None = None) -> str:
    """Markdown → HTML seguro, com escape antes de qualquer marcação."""
    linker: LinkForStudy = link_for_study or (lambda _id: None)
    lines = (source or "").replace("\r\n", "\n").split("\n")
    out: list[str] = []
    paragraph: list[str] = []
    i = 0

    def flush_paragraph():
        if paragraph:
            out.append("<p>" + _inline(" ".join(p.strip() for p in paragraph), linker) + "</p>")
            paragraph.clear()

    while i < len(lines):
        line = lines[i]
        if FENCE.match(line):
            flush_paragraph()
            code: list[str] = []
            i += 1
            while i < len(lines) and not FENCE.match(lines[i]):
                code.append(lines[i])
                i += 1
            i += 1  # pula a cerca de fechamento
            out.append("<pre><code>" + html.escape("\n".join(code), quote=True) + "</code></pre>")
            continue
        if not line.strip():
            flush_paragraph()
            i += 1
            continue
        if RULE.match(line):
            flush_paragraph()
            out.append("<hr>")
            i += 1
            continue
        heading = HEADING.match(line)
        if heading:
            flush_paragraph()
            level = min(6, len(heading.group(1)) + 2)  # o título da página é h1 e cada seção é h2
            out.append(f"<h{level}>{_inline(heading.group(2), linker)}</h{level}>")
            i += 1
            continue
        if QUOTE.match(line):
            flush_paragraph()
            quoted: list[str] = []
            while i < len(lines) and QUOTE.match(lines[i]):
                quoted.append(QUOTE.match(lines[i]).group(1))
                i += 1
            out.append("<blockquote>" + render_public_markdown("\n".join(quoted), linker) + "</blockquote>")
            continue
        for pattern, tag in ((UL_ITEM, "ul"), (OL_ITEM, "ol")):
            if pattern.match(line):
                flush_paragraph()
                items: list[str] = []
                while i < len(lines) and pattern.match(lines[i]):
                    items.append("<li>" + _inline(pattern.match(lines[i]).group(1), linker) + "</li>")
                    i += 1
                out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
                break
        else:
            paragraph.append(line)
            i += 1
    flush_paragraph()
    return "\n".join(out)


def plain_text(source: str | None) -> str:
    text = IMAGE.sub("", source or "")
    text = CONCEPT.sub(lambda m: m.group(1), text)
    text = MENTION.sub(lambda m: m.group(1).strip(), text)
    text = LINK.sub(lambda m: m.group(1), text)
    text = re.sub(r"^\s{0,3}(#{1,6}|>|[-*+]|\d+[.)])\s+", "", text, flags=re.M)
    text = re.sub(r"[*_`~]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def excerpt(source: str | None, limit: int = 160) -> str:
    text = plain_text(source)
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:")
    return f"{cut}…"
