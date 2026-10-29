"""Feature 091, fatia A: as 4 pistas de referência do organizador v2 (EXP-025, ADR-011), com textos fictícios."""

import hashlib
import json

import pytest

from app.services.organizer import engine_v2, loader

EXAMPLES = {
    "ref_md_title_author": "- A margem e o centro — Lúcia Dantas",
    "ref_md_link": "- [Chuva e cidade](https://exemplo.org/chuva)",
    "ref_url_line": "https://exemplo.org/chuva",
    "ref_title_author_year": "Céus de outros povos (Patrícia Moura, 2012)",
}
PAGE = (
    "O capítulo trata de um tema de teste e apresenta a ideia central do autor fictício.\n"
    "Isso importa porque mostra se o texto vai para a seção certa, ou seja, se a regra funciona.\n"
    "- A margem e o centro — Lúcia Dantas"
)


@pytest.fixture(autouse=True)
def fresh_cache():
    loader.reset_cache()
    yield
    loader.reset_cache()


def installed_artifact() -> dict:
    return json.loads(loader.ARTIFACT.read_text(encoding="utf-8"))


def test_cues_are_the_ones_in_the_installed_artifact():
    data = installed_artifact()
    assert data["extra_cues"] == {name: {"pattern": p, "mode": m} for name, (p, m) in engine_v2.EXTRA_CUES.items()}
    assert data["feature_names"][-4:] == engine_v2.EXTRA_NAMES


@pytest.mark.parametrize("name", list(EXAMPLES))
def test_each_cue_fires_on_its_example(name):
    values = dict(zip(engine_v2.EXTRA_NAMES, engine_v2.cue_values(EXAMPLES[name]), strict=True))
    assert values[name] == 1.0


def test_no_cue_fires_on_a_plain_sentence():
    assert engine_v2.cue_values("O autor fictício defende que a leitura lenta muda o leitor.") == [0.0] * 4


def test_list_reference_goes_to_references():
    result = loader.organize(PAGE)
    sections = {s["text"]: s["section"] for s in result["segments"]}
    assert sections["- A margem e o centro — Lúcia Dantas"] == "references"
    assert result["engine"]["version"] == "2"


def tampered(monkeypatch, tmp_path, change) -> None:
    data = installed_artifact()
    change(data)
    body = json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")
    fake = tmp_path / "organizer-v2.json"
    fake.write_bytes(body)
    monkeypatch.setattr(loader, "ARTIFACT", fake)
    monkeypatch.setattr(loader, "EXPECTED_SHA256", hashlib.sha256(body).hexdigest())


def test_unknown_cue_pattern_fails_integrity(monkeypatch, tmp_path):
    def change(data):
        data["extra_cues"]["ref_url_line"]["pattern"] = r"^https?://\S+$"

    tampered(monkeypatch, tmp_path, change)
    assert loader.status() == {"available": False, "reason": "integrity_failed", "version": None}


def test_new_columns_out_of_place_fail_integrity(monkeypatch, tmp_path):
    def change(data):
        names = data["feature_names"]
        names.insert(0, names.pop())

    tampered(monkeypatch, tmp_path, change)
    assert loader.status() == {"available": False, "reason": "integrity_failed", "version": None}


def test_untampered_copy_loads(monkeypatch, tmp_path):
    tampered(monkeypatch, tmp_path, lambda data: None)
    assert loader.status() == {"available": True, "reason": None, "version": "2"}
