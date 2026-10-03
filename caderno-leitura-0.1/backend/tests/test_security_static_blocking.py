from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from app.main import create_app

INDEX = '<!doctype html><html lang="pt-BR"><div id="app">Caderno de teste</div></html>'


@pytest.fixture
def sensitive_public_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "frontend" / "dist"
    (directory / "assets").mkdir(parents=True)
    (directory / "index.html").write_text(INDEX, encoding="utf-8")
    (directory / "assets" / "app.js").write_text('console.log("ok");', encoding="utf-8")
    
    # Arquivos que jamais deveriam estar expostos ou acessíveis
    (directory / ".env").write_text("SECRET=segredo_exposto", encoding="utf-8")
    (directory / ".git").mkdir()
    (directory / ".git" / "config").write_text("dummy git", encoding="utf-8")
    (directory / "caderno.db").write_text("sqlite dummy data", encoding="utf-8")
    (directory / "backup.sqlite").write_text("sqlite dummy backup", encoding="utf-8")
    (directory / "server.py").write_text("print('hello')", encoding="utf-8")
    (directory / "config.ini").write_text("[section]\nkey=val", encoding="utf-8")
    
    return directory


@pytest.fixture
def client(sensitive_public_dir: Path):
    with TestClient(create_app(frontend_dist=sensitive_public_dir)) as c:
        yield c


@pytest.mark.parametrize("blocked_path", [
    "/.env",
    "/.git",
    "/.git/config",
    "/caderno.db",
    "/backup.sqlite",
    "/server.py",
    "/config.ini",
    "/../sensitive.txt",
    "/..%2F..%2Fetc/passwd",
    "/assets/../../caderno.db",
])
def test_sensitive_files_and_traversal_are_blocked_with_404(client: TestClient, blocked_path: str):
    """Garante que qualquer requisição a arquivos sensíveis ou tentativas de directory traversal retorne 404."""
    response = client.get(blocked_path)
    assert response.status_code == 404


def test_legitimate_assets_remain_accessible(client: TestClient):
    """Garante que assets legítimos (HTML, JS) continuem funcionando normalmente."""
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert root_res.text == INDEX

    js_res = client.get("/assets/app.js")
    assert js_res.status_code == 200
    assert js_res.text == 'console.log("ok");'
