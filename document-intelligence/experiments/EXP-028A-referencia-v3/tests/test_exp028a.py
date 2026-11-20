"""EXP-028A — testes com páginas fictícias: rascunho por alinhamento, sorteios, exportação da v3 e
medidas H1–H4. Rodar a partir de ``document-intelligence/``:
``uv run pytest experiments/EXP-028A-referencia-v3/tests -q``"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1] / "harness"
sys.path.insert(0, str(HARNESS))

import common  # noqa: E402
import draws  # noqa: E402
import export_v3  # noqa: E402
import measure  # noqa: E402
import seed_drafts  # noqa: E402

from tests.tools.synthetic import make_dataset  # noqa: E402
from tools.anotar import store  # noqa: E402

GEMINI = "Capítulo 1 de teste linha fictícia $x^2$ Livro de Teste, p. 3"


@pytest.fixture
def env(tmp_path, monkeypatch):
    paths = make_dataset(tmp_path, pages=2, split_test=("p01", "p02"))
    data = paths.data_root
    monkeypatch.setattr(common, "DATA_ROOT", data)
    monkeypatch.setattr(common, "SPLITS", paths.splits)
    raw027 = data / "raw" / "exp-027"
    monkeypatch.setattr(common, "RAW027", raw027)
    monkeypatch.setattr(common, "GEMINI_REFERENCE", raw027 / "referencia")
    monkeypatch.setattr(common, "CLASSIFICATION", raw027 / "classificacao")
    monkeypatch.setattr(common, "PRODUCT_READING", data / "processed" / "exp-027" / "motor")
    monkeypatch.setattr(common, "RAW", data / "raw" / "exp-028a")
    monkeypatch.setattr(common, "REFERENCE_V3", data / "raw" / "exp-028a" / "referencia-v3")
    monkeypatch.setattr(common, "PROCESSED", data / "processed" / "exp-028a")
    (raw027 / "referencia").mkdir(parents=True)
    for pid in ("p01", "p02"):
        (raw027 / "referencia" / f"{pid}.txt").write_text(GEMINI + "\n", encoding="utf-8")
    return paths


# ---------------------------------------------------------------- alinhamento


def test_tokens_keep_formula_whole():
    assert seed_drafts.tokens("a $x + y$ b \\$ 5") == ["a", "$x + y$", "b", "\\$", "5"]


def test_distribute_follows_motor_boxes():
    assigned, stats = seed_drafts.distribute("a bb cc dd ee ff", ["a b8", "cx dd", "ee"])
    assert assigned == [["a", "bb"], ["cc", "dd"], ["ee", "ff"]]
    assert stats == {"words": 6, "aligned": 5, "carried": 1}


def test_distribute_keeps_order_and_empty_box():
    assigned, _ = seed_drafts.distribute("um dois três", ["um", None, "dois três"])
    assert assigned == [["um"], [], ["dois", "três"]]


def test_distribute_without_motor_text_goes_to_first_box():
    assigned, stats = seed_drafts.distribute("um dois", [None, None])
    assert assigned == [["um", "dois"], []] and stats["carried"] == 2


# ---------------------------------------------------------------- sorteios


def test_draws_are_stratified_reproducible_and_frozen(tmp_path, monkeypatch):
    splits, classes = tmp_path / "splits", tmp_path / "cls"
    splits.mkdir()
    classes.mkdir()
    monkeypatch.setattr(common, "SPLITS", splits)
    monkeypatch.setattr(common, "CLASSIFICATION", classes)
    test_ids = [f"p{i:02d}" for i in range(1, 21)]
    dev_ids = [f"p{i:02d}" for i in range(21, 52)]
    for n, pid in enumerate(test_ids + dev_ids):
        cls = {
            "escrita": ["cursiva", "mista", "forma"][n % 3],
            "formulas": ["nenhuma", "poucas"][n % 2],
        }
        (classes / f"{pid}.json").write_text(json.dumps(cls), encoding="utf-8")
    (splits / "test-manifest.json").write_text(
        json.dumps({"pages": dict.fromkeys(test_ids, {}), "dev_pages": dev_ids}), "utf-8"
    )
    assert draws.main([]) == 0
    second = json.loads((splits / "second-pass.json").read_text(encoding="utf-8"))
    dev_val = json.loads((splits / "dev-val-manifest.json").read_text(encoding="utf-8"))
    assert second["size"] == 5 and set(second["pages"]) <= set(test_ids)
    assert dev_val["size"] == 10 and set(dev_val["pages"]) <= set(dev_ids)
    assert len({tuple(v.values()) for v in dev_val["pages"].values()}) == 6  # todos os estratos
    before = (splits / "dev-val-manifest.json").read_bytes()
    assert draws.main([]) == 0
    assert (splits / "dev-val-manifest.json").read_bytes() == before
    assert draws.main(["--force"]) == 0
    again = json.loads((splits / "dev-val-manifest.json").read_text(encoding="utf-8"))
    assert again["pages"] == dev_val["pages"]


# ---------------------------------------------------------------- rascunho na ferramenta


def test_seed_drafts_writes_through_store(env):
    assert seed_drafts.main([]) == 0
    doc = store.load_page(env, "p01")
    assert doc["version"] == 1 and doc["draft_source"] == "importado:gemini-alinhado"
    assert [line["draft"] for line in doc["lines"]] == [
        "Capítulo 1 de teste",
        "linha fictícia $x^2$",
        "Livro de Teste, p. 3",
    ]
    assert all(line["pass1"] is None for line in doc["lines"])


def test_seed_skips_page_with_confirmed_line(env):
    doc = store.load_page(env, "p02")
    doc["lines"][0]["pass1"] = {"text": "já conferida", "at": "2026-11-20T12:00:00Z"}
    store.save_page(env, "p02", doc, expected_version=0)
    assert seed_drafts.main([]) == 0
    report = json.loads((common.PROCESSED / "seed-drafts.json").read_text(encoding="utf-8"))
    assert report["skipped_confirmed"] == ["p02"] and report["seeded"] == ["p01"]
    assert store.load_page(env, "p02")["draft_source"] == "motor"


# ---------------------------------------------------------------- exportação e medidas


def _confirm(env, pid, second_pass=None):
    doc = store.load_page(env, pid)
    for line in doc["lines"]:
        line["pass1"] = {"text": line["draft"], "at": "2026-11-20T12:00:00Z"}
        if second_pass is not None:
            text = second_pass.get(line["line_id"], line["draft"])
            line["pass2"] = {"text": text, "at": "2026-11-23T12:00:00Z", "mode": "cego"}
    doc["status"]["boxes_done"] = True
    store.save_page(env, pid, doc, expected_version=doc["version"])


def test_export_refuses_incomplete_then_exports(env):
    seed_drafts.main([])
    _confirm(env, "p01")
    assert export_v3.main([]) == 1
    assert export_v3.main(["--partial"]) == 0
    partial = json.loads((env.splits / "test-manifest-v3-parcial.json").read_text(encoding="utf-8"))
    assert partial["status"] == "parcial" and list(partial["pages"]) == ["p01"]
    assert not (env.splits / "test-manifest-v3.json").exists()
    assert store.load_page(env, "p02")["split"] == "test"  # a parcial não tira páginas do teste
    _confirm(env, "p02")
    assert export_v3.main([]) == 0
    manifest = json.loads((env.splits / "test-manifest-v3.json").read_text(encoding="utf-8"))
    assert manifest["size"] == 2 and manifest["pages"]["p01"]["lines"] == 3
    text = (common.REFERENCE_V3 / "p01.txt").read_text(encoding="utf-8")
    assert text.count("\n") == 3


def test_measures(env):
    seed_drafts.main([])
    _confirm(env, "p01", second_pass={"L002": "linha ficticia $x^2$"})  # 1 acento a menos
    _confirm(env, "p02")
    export_v3.main([])
    (env.splits / "second-pass.json").write_text(json.dumps({"pages": {"p01": {}}}), "utf-8")
    reading = common.PRODUCT_READING
    reading.mkdir(parents=True)
    for pid in ("p01", "p02"):
        lines = [{"text": "Capitulo 1 de teste"}, {"text": "Livro de Teste, p. 3"}]
        (reading / f"{pid}.json").write_text(json.dumps({"lines": lines}), encoding="utf-8")
    assert measure.main([]) == 0
    result = json.loads((common.PROCESSED / "results.json").read_text(encoding="utf-8"))
    assert result["h1_gemini_vs_v3"]["cer_micro"] == 0.0  # v3 = Gemini, só com quebras
    assert result["h4_line_breaks"]["breaks_v3"] == 4
    assert result["h4_line_breaks"]["breaks_lost_share"] == 1.0  # Gemini em um parágrafo
    h2 = result["h2_human_noise"]
    assert h2["lines"] == 3 and h2["lines_identical"] == 2 and 0 < h2["cer_micro"] < 0.1
    h3 = result["h3_product_vs_v3"]
    assert h3["lines"]["missing"] == 2 and h3["lines"]["ref"] == 6
    assert 0 < h3["cer_micro"] < 1 and h3["delta_points"] is not None
