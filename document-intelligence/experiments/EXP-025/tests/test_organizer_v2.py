"""EXP-025: ``organizer-v2`` (só pistas novas sobre o v1 congelado). Só dados fictícios."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1] / "harness"
EXPS = HARNESS.parents[1]
for path in (HARNESS, EXPS / "EXP-023" / "harness", EXPS / "EXP-024" / "harness"):
    if str(path) not in sys.path:
        sys.path.append(str(path))

import adaptive_organizer as ao  # noqa: E402  (EXP-024)
import organizer as org  # noqa: E402
import organizer_v2 as v2  # noqa: E402
import pages  # noqa: E402

ART = HARNESS.parent / "artifacts"
V1 = EXPS / "EXP-023" / "artifacts" / "organizer-v1.json"


@pytest.fixture(scope="module")
def engines():
    v1 = org.Organizer(org.Model.from_json(json.loads(V1.read_text(encoding="utf-8"))))
    return v1, v2.load()


def test_artifact_hash_and_cues_match_the_reference_implementation():
    body = (ART / "organizer-v2.json").read_text(encoding="utf-8")
    assert (
        hashlib.sha256(body.encode("utf-8")).hexdigest()
        == (ART / "organizer-v2.sha256").read_text().strip()
    )
    data = json.loads(body)
    assert data["version"] == "2" and data["feature_names"][-4:] == v2.EXTRA_NAMES
    v2.load()  # confere extra_cues


def test_cues_are_the_ones_from_exp024():
    pairs = {
        "ref_md_title_author": ao.REF_MD_TITLE_AUTHOR,
        "ref_md_link": ao.REF_MD_LINK,
        "ref_url_line": ao.REF_URL_LINE,
        "ref_title_author_year": ao.REF_TITLE_AUTHOR_YEAR,
    }
    for name, regex in pairs.items():
        assert v2.EXTRA_CUES[name][0] == regex.pattern


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("- A margem e o centro — Lúcia Pereira Dantas", [1.0, 0.0, 0.0, 0.0]),
        ("- [Chuva e cidade](https://exemplo.org/chuva-e-cidade)", [0.0, 1.0, 0.0, 0.0]),
        ("https://exemplo.org/chuva-e-cidade", [0.0, 0.0, 1.0, 0.0]),
        ("Céus de outros povos (Patrícia Moura, 2012)", [0.0, 0.0, 0.0, 1.0]),
        ("Isso importa porque fixa as ideias.", [0.0, 0.0, 0.0, 0.0]),
    ],
)
def test_cue_values(text, expected):
    assert v2.cue_values(text) == expected


def test_v1_weights_are_frozen(engines):
    v1, new = engines
    n = len(v1.model.feature_names)
    assert [row[:n] for row in new.model.weights] == v1.model.weights
    assert new.model.bias == v1.model.bias and new.model.params == v1.model.params


def test_identical_to_v1_where_no_cue_fires(engines):
    v1, new = engines
    for page in pages.build_pages()["val"][:8]:
        text, _labels, _units = pages.page_text(page)
        if any(any(v2.cue_values(line)) for line in text.split("\n")):
            continue
        for layout in (pages.layout(page), None):
            a, b = v1.organize(text, layout), new.organize(text, layout)
            assert a["segments"] == b["segments"]


def test_reference_lines_go_to_references(engines):
    _v1, new = engines
    text = "O capítulo trata da leitura ativa.\n- A margem e o centro — Lúcia Pereira Dantas"
    result = new.organize(text)
    assert result["segments"][-1]["section"] == "references"
