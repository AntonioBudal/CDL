"""Testes automatizados isolados para capas de livros (upload, URL, SSRF, ciclo de vida e lixeira)."""
import io
from pathlib import Path
from unittest.mock import patch

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.book import Book


@pytest.fixture
def client_and_covers(tmp_path, monkeypatch):
    """Configura ambiente hermético com banco SQLite e diretório de capas efêmeros em tmp_path."""
    db_path = tmp_path / "acervo_test" / "caderno.db"
    covers_path = tmp_path / "acervo_test" / "covers"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    covers_path.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("CADERNO_DATABASE_PATH", str(db_path))
    monkeypatch.setenv("CADERNO_COVERS_DIR", str(covers_path))

    # Executa todas as migrações no banco temporário
    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.attributes["database_path"] = db_path
    command.upgrade(alembic_cfg, "head")

    engine = create_sqlite_engine(db_path)
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session

    try:
        with TestClient(application) as client:
            yield client, covers_path, db_path
    finally:
        engine.dispose()


def generate_synthetic_image(width: int = 1000, height: int = 1500, format: str = "JPEG") -> bytes:
    """Cria imagem sintética em memória para testes."""
    img = Image.new("RGB", (width, height), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# US1: Upload Local, Redimensionamento WebP e Servir Arquivo Controlado
# ---------------------------------------------------------------------------


def test_upload_cover_success_and_resize(client_and_covers):
    """Testa upload de imagem local de 1200px, redimensionamento para max 800px WebP e rota controlada."""
    client, covers_dir, _ = client_and_covers

    # 1. Cria livro
    res_book = client.post("/api/books", json={"title": "Livro com Capa", "author": "Autor de Teste"})
    assert res_book.status_code == 201
    book_id = res_book.json()["id"]

    # 2. Gera imagem de 1200x1800
    img_data = generate_synthetic_image(width=1200, height=1800, format="JPEG")

    # 3. Envia via upload multipart
    res_upload = client.post(
        f"/api/books/{book_id}/cover",
        files={"file": ("minha_capa.jpg", img_data, "image/jpeg")},
    )
    assert res_upload.status_code == 200
    payload = res_upload.json()
    assert payload["book_id"] == book_id
    assert payload["cover_image"].endswith(".webp")
    assert payload["cover_url"] == f"/api/covers/{payload['cover_image']}"

    # 4. Verifica arquivo gerado em disco
    saved_file = covers_dir / payload["cover_image"]
    assert saved_file.is_file()

    with Image.open(saved_file) as img:
        assert img.format == "WEBP"
        assert img.width == 800
        assert img.height == 1200  # Proporção mantida

    # 5. Acessa rota controlada GET /api/covers/{filename}
    res_get = client.get(payload["cover_url"])
    assert res_get.status_code == 200
    assert res_get.headers["content-type"] == "image/webp"
    assert "max-age=86400" in res_get.headers.get("cache-control", "")
    assert len(res_get.content) > 0


def test_upload_cover_supports_various_formats_and_color_modes(client_and_covers):
    """Testa que upload aceita com sucesso .jpg, BMP, GIF, TIFF e JPEG em modo CMYK, convertendo todos para WebP."""
    client, covers_dir, _ = client_and_covers

    test_cases = [
        ("capa.jpg", "JPEG", "RGB", (100, 150), (10, 20, 30), "image/jpeg"),
        ("capa.bmp", "BMP", "RGB", (120, 180), (40, 50, 60), "image/bmp"),
        ("capa.gif", "GIF", "P", (80, 120), None, "image/gif"),
        ("capa.tiff", "TIFF", "RGB", (150, 220), (70, 80, 90), "image/tiff"),
        ("capa_cmyk.jpg", "JPEG", "CMYK", (200, 300), (0, 50, 100, 0), "image/jpeg"),
    ]

    for filename, fmt, mode, size, color, mime in test_cases:
        res_book = client.post("/api/books", json={"title": f"Livro {fmt} {mode}"})
        assert res_book.status_code == 201
        b_id = res_book.json()["id"]

        buf = io.BytesIO()
        if mode == "P":
            img = Image.new("RGB", size, (100, 120, 140)).convert("P")
            img.save(buf, format=fmt)
        elif color is not None:
            img = Image.new(mode, size, color)
            img.save(buf, format=fmt)
        raw_bytes = buf.getvalue()

        res_upload = client.post(
            f"/api/books/{b_id}/cover",
            files={"file": (filename, raw_bytes, mime)},
        )
        assert res_upload.status_code == 200, f"Falha para formato {fmt} ({mode}): {res_upload.text}"
        payload = res_upload.json()
        assert payload["cover_image"].endswith(".webp")

        saved_file = covers_dir / payload["cover_image"]
        assert saved_file.is_file()

        with Image.open(saved_file) as saved_img:
            assert saved_img.format == "WEBP"
            assert saved_img.width <= 800


def test_upload_cover_rejects_invalid_file(client_and_covers):
    """Testa rejeição de arquivos não-imagem ou corrompidos."""
    client, _, _ = client_and_covers

    res_book = client.post("/api/books", json={"title": "Livro Teste"})
    book_id = res_book.json()["id"]

    # Arquivo de texto disfarçado de imagem
    fake_img = b"Not a real image file content"
    res = client.post(
        f"/api/books/{book_id}/cover",
        files={"file": ("fake.jpg", fake_img, "image/jpeg")},
    )
    assert res.status_code == 400
    assert "Formato de imagem não suportado" in res.json()["detail"] or "processar" in res.json()["detail"]


def test_upload_cover_rejects_oversized_file(client_and_covers):
    """Testa rejeição de arquivo com tamanho superior a 5 MB."""
    client, _, _ = client_and_covers

    res_book = client.post("/api/books", json={"title": "Livro Teste"})
    book_id = res_book.json()["id"]

    huge_file = b"x" * (5 * 1024 * 1024 + 100)
    res = client.post(
        f"/api/books/{book_id}/cover",
        files={"file": ("huge.png", huge_file, "image/png")},
    )
    assert res.status_code == 400
    assert "5 MB" in res.json()["detail"]


def test_cover_route_path_traversal_protection(client_and_covers):
    """Testa proteção contra path traversal na rota de servir capas."""
    client, _, _ = client_and_covers

    res = client.get("/api/covers/..%2F..%2Fcaderno.db")
    assert res.status_code in (400, 404)

    res2 = client.get("/api/covers/invalid_name.exe")
    assert res2.status_code == 400


# ---------------------------------------------------------------------------
# US2: Importação por URL Externa e Proteção Anti-SSRF
# ---------------------------------------------------------------------------


def test_ssrf_protection_blocks_private_and_loopback_ips(client_and_covers):
    """Testa bloqueio estrito de URLs apontando para localhost ou redes privadas locais."""
    client, _, _ = client_and_covers

    res_book = client.post("/api/books", json={"title": "Livro SSRF"})
    book_id = res_book.json()["id"]

    malicious_urls = [
        "http://127.0.0.1:8000/secret.jpg",
        "http://localhost:8000/capa.png",
        "http://192.168.1.1/router.jpg",
        "http://10.0.0.1/internal.webp",
        "http://169.254.169.254/latest/meta-data",
    ]

    for bad_url in malicious_urls:
        res = client.post(f"/api/books/{book_id}/cover/url", json={"url": bad_url})
        assert res.status_code == 400
        assert "segurança" in res.json()["detail"].lower() or "não é permitido" in res.json()["detail"].lower()


def test_import_cover_from_url_success(client_and_covers):
    """Testa importação bem-sucedida de capa por URL simulada."""
    client, covers_dir, _ = client_and_covers

    res_book = client.post("/api/books", json={"title": "Livro URL"})
    book_id = res_book.json()["id"]

    sample_img = generate_synthetic_image(width=500, height=750, format="PNG")

    # Mock do httpx.Client para retornar a imagem sem chamada externa real
    class MockResponse:
        status_code = 200
        url = "https://public-cdn.example.com/books/capa.png"
        headers = {"content-type": "image/png"}
        content = sample_img

    with patch("app.services.cover_service.validate_safe_url", return_value="https://public-cdn.example.com/books/capa.png"):
        with patch("httpx.Client.get", return_value=MockResponse()):
            res = client.post(
                f"/api/books/{book_id}/cover/url",
                json={"url": "https://public-cdn.example.com/books/capa.png"},
            )
            assert res.status_code == 200
            payload = res.json()
            assert payload["book_id"] == book_id
            assert payload["cover_image"].endswith(".webp")

            # Verifica integridade no disco
            cover_file = covers_dir / payload["cover_image"]
            assert cover_file.is_file()


# ---------------------------------------------------------------------------
# US3: Remoção, Substituição, Lixeira (Soft Delete) e Expurgo Físico
# ---------------------------------------------------------------------------


def test_remove_cover_cleans_file(client_and_covers):
    """Testa que remover a capa desassocia o livro e exclui o arquivo órfão."""
    client, covers_dir, _ = client_and_covers

    res_book = client.post("/api/books", json={"title": "Livro Remover Capa"})
    book_id = res_book.json()["id"]

    # 1. Faz upload
    img = generate_synthetic_image()
    res_up = client.post(f"/api/books/{book_id}/cover", files={"file": ("c.jpg", img, "image/jpeg")})
    filename = res_up.json()["cover_image"]
    file_path = covers_dir / filename
    assert file_path.is_file()

    # 2. Remove capa
    res_del = client.delete(f"/api/books/{book_id}/cover")
    assert res_del.status_code == 200
    assert res_del.json()["cover_image"] is None

    # 3. Verifica livro no banco
    res_check = client.get(f"/api/books/{book_id}")
    assert res_check.json()["cover_image"] is None

    # 4. Arquivo físico foi removido do disco
    assert not file_path.exists()


def test_replace_cover_deletes_old_file(client_and_covers):
    """Testa que substituir uma capa por outra exclui a imagem anterior."""
    client, covers_dir, _ = client_and_covers

    res_book = client.post("/api/books", json={"title": "Livro Substituir"})
    book_id = res_book.json()["id"]

    # Upload da capa 1
    res1 = client.post(f"/api/books/{book_id}/cover", files={"file": ("c1.jpg", generate_synthetic_image(), "image/jpeg")})
    file1 = covers_dir / res1.json()["cover_image"]
    assert file1.is_file()

    # Upload da capa 2
    res2 = client.post(f"/api/books/{book_id}/cover", files={"file": ("c2.jpg", generate_synthetic_image(), "image/jpeg")})
    file2 = covers_dir / res2.json()["cover_image"]
    assert file2.is_file()

    # file1 deve ter sido apagado, file2 deve existir
    assert not file1.exists()
    assert file2.exists()


def test_trash_preserves_cover_file_and_permanent_delete_purges_it(client_and_covers):
    """Testa que mover para lixeira retém a capa física e exclusão definitiva a expurga."""
    client, covers_dir, _ = client_and_covers

    res_book = client.post("/api/books", json={"title": "Livro Lixeira Capa"})
    book_id = res_book.json()["id"]

    res_up = client.post(f"/api/books/{book_id}/cover", files={"file": ("c.jpg", generate_synthetic_image(), "image/jpeg")})
    filename = res_up.json()["cover_image"]
    file_path = covers_dir / filename
    assert file_path.is_file()

    # 1. Move para a lixeira
    res_trash = client.post(f"/api/books/{book_id}/trash")
    assert res_trash.status_code == 200

    # 2. O arquivo DEVE continuar existindo no disco (FR-010 e Q3:A)
    assert file_path.is_file()

    # 3. Restaura da lixeira
    res_restore = client.post(f"/api/books/{book_id}/restore")
    assert res_restore.status_code == 200
    assert res_restore.json()["cover_image"] == filename
    assert file_path.is_file()

    # 4. Move novamente para lixeira e exclui permanentemente
    client.post(f"/api/books/{book_id}/trash")
    res_perm = client.delete(f"/api/books/{book_id}/permanent")
    assert res_perm.status_code == 204

    # 5. Agora o arquivo físico DEVE ter sido removido
    assert not file_path.exists()
