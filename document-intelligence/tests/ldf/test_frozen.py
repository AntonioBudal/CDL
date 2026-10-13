"""O que já foi aceito não muda: schema do LDF 1.0 e diretórios dos EXP-001 a EXP-003.

Os conversores dos EXP-002 e EXP-003 leem ``docs/schemas/ldf-1.0.schema.json`` pelo caminho;
alterar esse arquivo quebraria a reprodução dos experimentos aceitos (spec 001, FR-014).
"""

import hashlib
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LDF_1_0_SHA256 = "3c0f0ac349feb0fcfd411ea8188c4f04ead9f84913e86874354accc86d651306"
# Árvores Git registradas em 2026-10-12, no commit 1774563 (antes do LDF 2.0).
FROZEN_TREES = {
    "experiments/EXP-001": "307f794c141147c676e7cea9494efa4b8212050b",
    "experiments/EXP-002": "d3d402ff39a0937f3b4fb58bf9daa8bb467c4108",
    "experiments/EXP-003": "45d3a8ba8747a7fd8e9ba9a8a7ae7675a6dd1cb3",
}


def git(*arguments: str) -> str:
    try:
        return subprocess.run(
            ["git", *arguments], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git indisponível")


def test_ldf_1_0_schema_is_unchanged():
    content = (ROOT / "docs" / "schemas" / "ldf-1.0.schema.json").read_bytes()
    digest = hashlib.sha256(content.replace(b"\r\n", b"\n")).hexdigest()
    assert digest == LDF_1_0_SHA256


@pytest.mark.parametrize(("directory", "tree"), sorted(FROZEN_TREES.items()))
def test_accepted_experiment_is_unchanged(directory, tree):
    assert git("rev-parse", f"HEAD:./{directory}") == tree
    assert git("status", "--porcelain", "--", directory) == ""
