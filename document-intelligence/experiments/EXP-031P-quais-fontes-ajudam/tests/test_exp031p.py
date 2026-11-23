"""EXP-031P — testes com dados fictícios: cotas, seleção determinística com descarte de caracteres
fora do dicionário, gerador sintético determinístico. Rodar a partir de ``document-intelligence/``:
``uv run pytest experiments/EXP-031P-quais-fontes-ajudam/tests -q``"""

from __future__ import annotations

import io
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1] / "harness"
sys.path.insert(0, str(HARNESS))
sys.path.append(str(Path(__file__).resolve().parents[3]))

import groups  # noqa: E402
import synth  # noqa: E402
from PIL import Image  # noqa: E402

from tools.catalogo import Catalog  # noqa: E402


def png(seed: int) -> bytes:
    image = Image.new("L", (200 + seed, 40), 240)
    out = io.BytesIO()
    image.save(out, "PNG")
    return out.getvalue()


def test_allocate_equal_capped_and_redistributed():
    quota = groups.allocate(100, {"a": 1000, "b": 10, "c": 1000, "d": 1000}, {"d": 0.2})
    assert quota["b"] == 10 and quota["d"] == 20
    assert sum(quota.values()) == 100 and quota["a"] + quota["c"] == 70


def test_allocate_when_not_enough():
    assert groups.allocate(100, {"a": 5, "b": 7}) == {"a": 5, "b": 7}


def test_valid_text_requires_known_characters():
    charset = set("abc ã")
    assert groups.valid_text("abc ã", charset)
    assert not groups.valid_text("abc ø", charset)
    assert not groups.valid_text("   ", charset)


def test_select_is_deterministic_and_filters(tmp_path, monkeypatch):
    catalog = Catalog(tmp_path / "dados")
    for source in ("s1", "s2"):
        catalog.add_source(
            source,
            name=source,
            url="u",
            license="CC0",
            conditions=[],
            status="APPROVED",
            access="api",
        )
    for n in range(30):
        catalog.ingest_line("s1", str(n), image=png(n), text="texto bom" if n % 3 else "ruim ø")
        catalog.ingest_line("s2", str(n), image=png(n + 40), text="outro texto")
    catalog.flush()
    monkeypatch.setitem(groups.GROUPS, "T", ["s1", "s2"])
    charset = set("texto bomruiouts ")
    first, quota = groups.select(catalog, "T", 20, charset, "semente")
    second, _ = groups.select(catalog, "T", 20, charset, "semente")
    assert first == second and len(first) == 20 and quota == {"s1": 10, "s2": 10}
    assert all(catalog.item(i)["text"] != "ruim ø" for i in first)
    catalog.close()


def test_synthetic_is_deterministic(tmp_path, monkeypatch):
    corpus = "Era uma vez um caderno de capa azul com anotações sobre a leitura atenta de páginas"
    a = synth.generate(6, tmp_path / "a", "s", corpus)
    b = synth.generate(6, tmp_path / "b", "s", corpus)
    assert [x["text"] for x in a] == [x["text"] for x in b]
    assert Path(a[0]["image"]).read_bytes() == Path(b[0]["image"]).read_bytes()
    with Image.open(a[0]["image"]) as image:
        assert image.mode == "L" and image.height > 20
