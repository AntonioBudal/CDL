"""EXP-028B — testes com dados fictícios. Rodar a partir de ``document-intelligence/``:
``uv run pytest experiments/EXP-028B-decomposicao-512/tests -q``"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1] / "harness"
sys.path.insert(0, str(HARNESS))
sys.path.append(str(Path(__file__).resolve().parents[3]))  # document-intelligence/

import decompose  # noqa: E402

from tools.anotar.paths import DI_ROOT, MOTOR_PYTHON  # noqa: E402


def test_parts_add_up():
    pages = {
        "p01": {
            "ref": {"L001": "abcde", "L002": "fghij"},
            "order": ["L001", "L002"],
            "a": ["abcde"],  # a 2ª linha nem foi achada: erro de detecção
            "b": {"L001": "abcde", "L002": "fghiX"},  # leitor erra 1 caractere
            "c": ["fghiX", "abcde"],  # ordem trocada
            "original": ["abcde fghij"],
        }
    }
    result = decompose.decompose(pages)
    cer = result["cer"]
    assert cer["b_caixas_autor"] == round(1 / 11, 4)
    assert cer["a_produto"] == round(6 / 11, 4)  # a linha perdida (5) + o espaço
    assert cer["c_caixas_autor_ordem_produto"] == round(10 / 11, 4)  # trocar a ordem custa caro
    parts = result["parts"]
    # A decomposição é um caminho (A → C → B): uma parte pode sair negativa, e as partes somam A.
    assert parts["deteccao_pontos"] < 0 < parts["ordem_pontos"]
    total = parts["deteccao_pontos"] + parts["ordem_pontos"] + parts["leitor_pontos"]
    assert abs(total - cer["a_produto"] * 100) < 0.2
    assert result["lines_b"]["distribution"]["ate_10"] == 1
    assert result["lines_b"]["distribution"]["10_a_30"] == 1
    assert result["resolution"]["original_photos"] == 0.0
    assert result["resolution"]["cost_points"] == round(cer["a_produto"] * 100, 1)


def test_reference_marks_are_removed():
    pages = {
        "p01": {
            "ref": {"L001": "área $x^2$ [?]"},
            "order": ["L001"],
            "a": ["área x^2"],
            "b": {"L001": "área x^2"},
            "c": ["área x^2"],
            "original": None,
        }
    }
    result = decompose.decompose(pages)
    assert result["cer"]["b_caixas_autor"] == 0.0
    assert result["resolution"]["cost_points"] is None


@pytest.mark.skipif(not MOTOR_PYTHON.is_file(), reason="ambiente do motor ausente")
def test_read_boxes_runs_the_product_reader(tmp_path):
    data = tmp_path / "dataset"
    photos = tmp_path / "fotos"
    run = subprocess.run(
        [str(MOTOR_PYTHON), "-m", "tests.tools.make_photos", str(photos), "1"],
        cwd=DI_ROOT, capture_output=True, text=True, timeout=300,
    )
    assert run.returncode == 0, run.stderr
    images = data / "processed" / "anotacao" / "imagens"
    images.mkdir(parents=True)
    image = images / "p01.jpg"
    image.write_bytes(next(photos.iterdir()).read_bytes())
    (data / "processed" / "anotacao" / "pages.json").write_text(
        json.dumps({"pages": {"p01": {"work_sha256": hashlib.sha256(image.read_bytes())
                                                    .hexdigest()}}}),
        encoding="utf-8",
    )
    lines = [
        {"line_id": f"L00{i + 1}", "order": i + 1,
         "polygon": [[110, 112 + 90 * k], [900, 112 + 90 * k],
                     [900, 170 + 90 * k], [110, 170 + 90 * k]]}
        for i, k in enumerate([1, 0, 2])  # ordem do autor diferente da de cima para baixo
    ]
    (data / "raw" / "anotacao").mkdir(parents=True)
    (data / "raw" / "anotacao" / "p01.json").write_text(json.dumps({"lines": lines}), "utf-8")
    env = {**os.environ, "EXP028B_DATA_ROOT": str(data),
           "EXP028B_MOTOR_DIR": str(MOTOR_PYTHON.parents[2])}
    script = HARNESS / "read_boxes.py"
    outputs = []
    for _ in range(2):  # determinístico: duas rodadas, o mesmo resultado
        done = subprocess.run([str(MOTOR_PYTHON), str(script), "--pages", "p01"], cwd=DI_ROOT,
                              env=env, capture_output=True, text=True, timeout=600)
        assert done.returncode == 0, done.stderr
        outputs.append({c: json.loads((data / "processed" / "exp-028b" / c / "p01.json")
                                      .read_text(encoding="utf-8"))["lines"] for c in "abc"})
    assert outputs[0] == outputs[1]
    b, c = outputs[0]["b"], outputs[0]["c"]
    assert [ln["line_id"] for ln in b] == ["L001", "L002", "L003"]
    assert [ln["line_id"] for ln in c] == ["L002", "L001", "L003"]  # de cima para baixo
    assert sorted(ln["text"] for ln in b) == sorted(ln["text"] for ln in c)
