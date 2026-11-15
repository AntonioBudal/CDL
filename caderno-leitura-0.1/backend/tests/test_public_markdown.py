"""F0.12.02 (spec 115): Markdown restrito das páginas públicas — escape primeiro."""
from __future__ import annotations

from app.services.public_markdown import excerpt, render_public_markdown


def link_for(study_id: int):
    return "/compartilhado/7" if study_id == 7 else None


def test_escapes_html_and_attributes():
    out = render_public_markdown('Olá <script>alert(1)</script> <img src=x onerror="alert(1)"> & "aspas"')
    assert "<script" not in out and "<img" not in out and "onerror=\"" not in out
    assert "&lt;script&gt;" in out and "&amp;" in out and "&quot;aspas&quot;" in out


def test_only_http_links():
    out = render_public_markdown("[bom](https://exemplo.invalid/a?b=1&c=2) [ruim](javascript:alert(1)) [rel](/estudos/1) [d](data:text/html,x)")
    assert '<a href="https://exemplo.invalid/a?b=1&amp;c=2" rel="nofollow ugc noopener noreferrer">bom</a>' in out
    assert "javascript:" not in out.split("ruim")[0] + "x" and 'href="javascript' not in out
    assert 'href="/estudos/1"' not in out and 'href="data:' not in out
    assert "ruim" in out and "rel" in out


def test_blocks():
    out = render_public_markdown("# Título\n\nParágrafo **forte** e *ênfase* e `código <b>`.\n\n- um\n- dois\n\n1. a\n2. b\n\n> citação\n\n```\n<b>x</b>\n```\n\n---")
    assert "<h3>Título</h3>" in out
    assert "<strong>forte</strong>" in out and "<em>ênfase</em>" in out and "<code>código &lt;b&gt;</code>" in out
    assert "<ul><li>um</li><li>dois</li></ul>" in out and "<ol><li>a</li><li>b</li></ol>" in out
    assert "<blockquote><p>citação</p></blockquote>" in out
    assert "<pre><code>&lt;b&gt;x&lt;/b&gt;</code></pre>" in out and "<hr>" in out


def test_mentions_and_images():
    out = render_public_markdown("Ver [[conceito:Mímese]], [[Outro|5]], [[Publicado|7]] e [[Livre]]. ![foto](/api/media/1)", link_for)
    assert "Mímese" in out and "conceito:" not in out
    assert '<a href="/compartilhado/7">Publicado</a>' in out
    assert "Outro" in out and "/5" not in out and "Livre" in out
    assert "/api/media" not in out and "<img" not in out


def test_excerpt():
    assert excerpt("**Resumo** com [[conceito:Mímese]] e [link](https://x.invalid).") == "Resumo com Mímese e link."
    long = "palavra " * 50
    assert len(excerpt(long, 40)) <= 40 and excerpt(long, 40).endswith("…")
