"""EXP-024 (F02): fluxos longitudinais e simulador de feedback. Só dados fictícios."""

from __future__ import annotations

import hashlib
import json
import re
from functools import cache

import pytest
import simulator as sim
import streams


@cache
def measured(split: str, cer: float) -> dict:
    """CER e confiança medidos sobre as páginas de adaptação de um split."""
    flagged = [0, 0, 0]
    other = [0, 0, 0]
    for st in streams.all_streams(split).values():
        for page in st["adapt"]:
            for line in sim.read_page(page, cer):
                errors = sim.levenshtein(line["truth"], line["text"])
                bucket = flagged if line["confidence"] < sim.LOW_CONFIDENCE else other
                bucket[0] += 1
                bucket[1] += errors
                bucket[2] += len(line["truth"])
    return {
        "cer": (flagged[1] + other[1]) / (flagged[2] + other[2]),
        "flagged_share": flagged[0] / (flagged[0] + other[0]),
        "flagged_cer": flagged[1] / max(1, flagged[2]),
        "other_cer": other[1] / max(1, other[2]),
    }


def word_grams(text: str, n: int = 4) -> set[tuple[str, ...]]:
    words = streams.fold(text).split()
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


# --- dados e fluxos ------------------------------------------------------------------------------


def test_frozen_data_is_intact():
    streams.verify_frozen()


@pytest.mark.parametrize("split", streams.SPLITS)
def test_stream_shape(split):
    all_streams = streams.all_streams(split)
    assert sorted(all_streams) == ["P1", "P2", "P3", "P4"]
    for st in all_streams.values():
        assert [p["t"] for p in st["adapt"]] == list(range(1, streams.ADAPT_PAGES + 1))
        assert {p["book_id"] for p in st["adapt"]} == set(st["books"])
        assert len(st["books"]) == 2
        for book_id, pages in st["holdout"].items():
            assert len(pages) == streams.HOLDOUT_PER_BOOK
            assert {p["book_id"] for p in pages} == {book_id}
            assert all(p["role"] == "holdout" for p in pages)


def test_validation_and_test_streams_use_different_books():
    val = {b for st in streams.all_streams("val").values() for b in st["books"]}
    test = {b for st in streams.all_streams("test").values() for b in st["books"]}
    assert val.isdisjoint(test) and len(val) == len(test) == 8


@pytest.mark.parametrize("split", streams.SPLITS)
def test_no_leakage_between_adaptation_and_holdout(split):
    for st in streams.all_streams(split).values():
        adapt = {u["text"] for p in st["adapt"] for u in p["source_units"]}
        holdout = {
            u["text"] for pages in st["holdout"].values() for p in pages for u in p["source_units"]
        }
        assert adapt.isdisjoint(holdout), f"trecho repetido em {st['profile']}"
        adapt_grams = [g for g in (word_grams(t) for t in adapt) if g]
        for text in holdout:
            grams = word_grams(text)
            if not grams:
                continue
            for other in adapt_grams:
                jaccard = len(grams & other) / len(grams | other)
                assert jaccard < 0.5, (st["profile"], text)


def test_pages_are_deterministic():
    profile = streams.load()["profiles"]["P2"]
    book = streams.load()["books"]["b05"]
    first = streams.make_page(profile, book, "val", "adapt", 7)
    second = streams.make_page(profile, book, "val", "adapt", 7)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_profiles_carry_their_reference_formats():
    def references(profile: str) -> list[str]:
        return [
            u["text"]
            for p in streams.stream(profile, "val")["adapt"]
            for u in p["source_units"]
            if u["section"] == "r"
        ]

    p1 = references("P1")
    assert sum(t.startswith("- ") for t in p1) / len(p1) > 0.8
    assert any("](https://exemplo.org/" in t for t in p1) and any(" — " in t for t in p1)
    p3 = references("P3")
    assert any(re.match(r"^[A-ZÁ-Ú]{2,}, [A-ZÁ-Ú]", t) for t in p3)
    assert any(t.startswith('"') and "(p. " in t for t in p3)


def test_canary_matches_exp023_test_pages():
    import pages as base_pages

    built = {p["id"]: p for p in base_pages.build_pages()["test"]}
    canary = streams.load()["canary"]["pages"]
    assert len(canary) == 8
    for item in canary:
        text, _labels, _units = base_pages.page_text(built[item["page_id"]])
        assert hashlib.sha256(text.encode("utf-8")).hexdigest() == item["sha256"]


# --- leitura ruidosa e confiança ---------------------------------------------------------------


@pytest.mark.parametrize("target", [0.10, 0.25])
def test_reading_cer_close_to_target(target):
    assert abs(measured("val", target)["cer"] - target) <= 0.02


def test_confidence_reproduces_feature_086():
    m = measured("val", 0.27)
    assert 0.17 <= m["flagged_share"] <= 0.25
    assert m["flagged_cer"] >= 1.6 * m["other_cer"]


def test_writer_confusions_are_recurrent():
    page = streams.stream("P1", "val")["adapt"][0]
    stream_pages = streams.stream("P1", "val")["adapt"]
    cedillas = sum(line["text"].count("ç") for p in stream_pages for line in p["lines"])
    kept = sum(line["text"].count("ç") for p in stream_pages for line in sim.read_page(p, 0.25))
    assert cedillas > 20 and kept < 0.3 * cedillas  # W1 troca ç por c em ~85 % das vezes
    assert sim.read_page(page, 0.0)[0]["text"] == page["lines"][0]["text"]


# --- sessões e regimes ---------------------------------------------------------------------------


@cache
def run(regime: str, profile: str = "P1") -> list[tuple[dict, dict]]:
    pages = streams.stream(profile, "val")["adapt"]
    plan = sim.noisy_plan(pages, regime)
    return [sim.session(p, regime, sim.static_organize, noisy=plan.get(p["id"])) for p in pages]


def test_sessions_are_deterministic():
    page = streams.stream("P3", "val")["adapt"][5]
    first = sim.session(page, "R2", sim.static_organize)
    second = sim.session(page, "R2", sim.static_organize)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_regime_r1_is_implicit_only():
    out = run("R1")
    assert all(f["rating"] is None for f, _ in out)
    assert all(t["noisy"] is None for _, t in out)
    assert sum(len(f["organizer"]["clicks"]) for f, _ in out) > 0


def test_regime_r2_has_consistent_ratings():
    out = run("R2")
    ratings = [f["rating"] for f, _ in out]
    assert all(r in (1, 2, 3, 4, 5) for r in ratings)
    good = [f["rating"] for f, t in out if t["quality"] >= 0.75]
    bad = [f["rating"] for f, t in out if t["quality"] < 0.4]
    if good and bad:
        assert sum(good) / len(good) > sum(bad) / len(bad)


def test_regime_r3_has_exactly_twenty_percent_noisy_pages():
    out = run("R3")
    kinds = [t["noisy"] for _, t in out if t["noisy"]]
    assert len(kinds) == round(sim.NOISY_SHARE * len(out)) == 8
    assert set(kinds) == set(sim.NOISY_KINDS)
    for feedback, truth in out:
        if truth["noisy"] == "blind":
            assert feedback["organizer"]["clicks"] == [] and not feedback["organizer"]["reverted"]
            assert truth["final_sections"] == [
                s["section"] for s in feedback["organizer"]["suggested"]["segments"]
            ]
            assert truth["user_lines"] == feedback["reading"]["shown_lines"]
        if truth["noisy"] == "rewrite" and not feedback["organizer"]["reverted"]:
            rewrites = streams.load()["rewrites"]
            saved = "\n".join(feedback["saved"].values())
            assert any(r in saved for r in rewrites)


def test_feedback_package_is_consistent():
    for feedback, truth in run("R1", "P4"):
        assert feedback["schema"] == "leitorum-feedback/1"
        assert feedback["user_id"] == "u-P4-val"
        assert len(feedback["reading"]["source_lines"]) == len(
            feedback["reading"]["line_confidence"]
        )
        text = feedback["organizer"]["text"]
        if feedback["organizer"]["reverted"]:
            assert (
                feedback["saved"]["explanation"] == text and feedback["organizer"]["clicks"] == []
            )
            continue
        segments = feedback["organizer"]["suggested"]["segments"]
        pieces = "".join(text[s["start"] : s["end"]] for s in segments).replace("\n", "")
        saved = "".join(feedback["saved"].values()).replace("\n", "")
        assert sorted(pieces) == sorted(
            saved
        )  # nada se perde, nada se inventa (trechos podem ter quebras)
        assert len(truth["truth_sections"]) == len(segments)
