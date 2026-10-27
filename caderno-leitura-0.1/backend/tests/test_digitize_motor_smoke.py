"""Feature 086: o motor real lê uma página sintética fictícia pela linha de comando.

Pulado quando o motor não está instalado (``instalar.py --motor``) ou quando o serviço também recusaria
a leitura por memória (feature 088: no Windows, memória comprometível abaixo do mínimo).
"""

import json
import subprocess

from PIL import Image, ImageDraw, ImageFont
import pytest

from app.core.config import get_digitize_min_free_bytes, get_motor_config, get_motor_python
from app.services.digitize_service import _creation_flags, available_memory

pytestmark = pytest.mark.skipif(not get_motor_python().is_file(), reason="motor de leitura não instalado")
_memory = available_memory()
needs_memory = pytest.mark.skipif(
    _memory is not None and _memory.available < get_digitize_min_free_bytes(),
    reason="pouca memória livre para o motor (mesma regra do serviço)",
)


def synthetic_page(path):
    image = Image.new("RGB", (1240, 900), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=56)
    for row, text in enumerate(["Livro de Teste", "Capitulo 1", "Linha de exemplo"]):
        draw.text((90, 120 + row * 200), text, fill="black", font=font)
    image.save(path, format="PNG")


def motor(*arguments):
    return subprocess.run(
        [str(get_motor_python()), "-I", "-m", "leitorum_motor", *arguments, "--config", str(get_motor_config())],
        capture_output=True,
        timeout=180,
        creationflags=_creation_flags(),
    )


def test_motor_check_passes():
    completed = motor("check")
    assert completed.returncode == 0, completed.stderr
    engine = json.loads(completed.stdout)["engine"]
    assert engine["license_status"] == "VERIFIED"
    assert engine["reader"] == "PP-OCRv6 small"


@needs_memory
def test_motor_reads_synthetic_page(tmp_path):
    page, out = tmp_path / "pagina.png", tmp_path / "leitura.json"
    synthetic_page(page)
    completed = motor("read", "--image", str(page), "--out", str(out))
    assert completed.returncode == 0, completed.stderr
    result = json.loads(out.read_text(encoding="utf-8"))
    assert result["schema"] == "leitorum-motor/1"
    assert result["image"] == {"width": 1240, "height": 900}
    assert len(result["lines"]) >= 3
    tops = [line["bbox"][1] for line in result["lines"]]
    assert tops == sorted(tops), "linhas em ordem de leitura"
    assert all(0 <= line["confidence"] <= 1 for line in result["lines"])
    assert "Teste" in " ".join(line["text"] for line in result["lines"])


def test_motor_rejects_unverified_reader(tmp_path):
    config = json.loads(get_motor_config().read_text(encoding="utf-8"))
    config["reader"]["license_status"] = "NEEDS VALIDATION"
    unverified = tmp_path / "config.json"
    unverified.write_text(json.dumps(config), encoding="utf-8")
    completed = subprocess.run(
        [str(get_motor_python()), "-I", "-m", "leitorum_motor", "check", "--config", str(unverified)],
        capture_output=True,
        timeout=180,
        creationflags=_creation_flags(),
    )
    assert completed.returncode == 3
    assert json.loads(completed.stdout) == {"ok": False, "reason": "integrity_failed"}
