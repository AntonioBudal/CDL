"""F0.12.01 (spec 114): versão única (VERSION) no padrão SemVer, lida pelo backend e igual à do frontend."""
from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

import app
from app.main import create_app

ROOT = Path(app.__file__).resolve().parents[2]
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def test_version_file_is_semver_and_shared():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert SEMVER.match(version), version
    assert app.__version__ == version
    package = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
    assert package["version"] == version, "package.json acompanha o VERSION"
    lock = json.loads((ROOT / "frontend" / "package-lock.json").read_text(encoding="utf-8"))
    assert lock["version"] == version and lock["packages"][""]["version"] == version


def test_health_reports_the_version(tmp_path, monkeypatch):
    monkeypatch.setenv("CADERNO_DATABASE_PATH", str(tmp_path / "versao.db"))
    with TestClient(create_app()) as client:
        data = client.get("/api/health").json()
    assert data["version"] == app.__version__
