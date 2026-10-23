"""Sorteio por página do EXP-018, com identificadores fictícios."""

from subset import page_of, pick_pages

ITEMS = [{"id": f"{p:04d}-001-01-{n:02d}"} for p in range(10) for n in range(3)]


def test_page_of_drops_paragraph_and_line():
    assert page_of("0214-006-01-01") == "0214-006"


def test_pick_pages_keeps_whole_pages_and_is_reproducible():
    chosen = pick_pages(ITEMS, 4, seed=1)
    assert len(chosen) == 12
    assert len({page_of(it["id"]) for it in chosen}) == 4
    assert chosen == pick_pages(ITEMS, 4, seed=1)
    assert chosen != pick_pages(ITEMS, 4, seed=2)


def test_pick_pages_nests_when_seed_is_shared():
    small = {page_of(it["id"]) for it in pick_pages(ITEMS, 3, seed=7)}
    large = {page_of(it["id"]) for it in pick_pages(ITEMS, 6, seed=7)}
    assert len(small) == 3 and len(large) == 6 and small <= large


def test_asking_for_all_pages_returns_everything():
    assert pick_pages(ITEMS, 99, seed=1) == ITEMS
