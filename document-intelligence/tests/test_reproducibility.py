"""Testes do congelamento de sementes e do registro de ambiente."""

import random

from leitorum_di.reproducibility import DEFAULT_SEED, environment_snapshot, freeze_seeds


def test_freeze_seeds_makes_random_deterministic():
    record_a = freeze_seeds(42)
    first = [random.random() for _ in range(5)]
    record_b = freeze_seeds(42)
    second = [random.random() for _ in range(5)]
    assert first == second
    assert record_a["seed"] == record_b["seed"] == 42
    assert "random" in record_a["seeded"]


def test_freeze_seeds_default_and_different_seed_differs():
    assert freeze_seeds()["seed"] == DEFAULT_SEED
    freeze_seeds(1)
    a = random.random()
    freeze_seeds(2)
    b = random.random()
    assert a != b


def test_environment_snapshot_has_expected_keys():
    snap = environment_snapshot()
    for key in ("python", "implementation", "platform", "machine", "cpu_count"):
        assert key in snap
