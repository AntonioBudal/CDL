"""Testes automatizados isolados para o serviço de exportação (Markdown e TXT)."""
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models import Book, Chapter, Study
from app.schemas.export import ExportFormat, ExportOptions
from app.services.export_service import (
    format_book_markdown,
    format_book_text,
    format_study_markdown,
    format_study_text,
    sanitize_filename,
)


@pytest.fixture
def client_and_db(tmp_path):
    """Configura base SQLite temporária e TestClient 100% isolado em tmp_path."""
    db_path = tmp_path / "acervo_export" / "caderno.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

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
            yield client, engine
    finally:
        engine.dispose()


# ==============================================================================
# T005: Testes Unitários de Sanitização e Formatação
# ==============================================================================

def test_sanitize_filename_windows_illegal_chars():
    """Valida substituição de caracteres proibidos no Windows."""
    title = 'Livro: "Memórias" / Capítulos <1> & * ? |'
    result = sanitize_filename(title, "md")
    assert "<" not in result
    assert ">" not in result
    assert ":" not in result
    assert '"' not in result
    assert "/" not in result
    assert "\\" not in result
    assert "|" not in result
    assert "?" not in result
    assert "*" not in result
    assert result.endswith(".md")
    assert not result.startswith("-")


def test_sanitize_filename_accents_and_spaces():
    """Valida normalização de acentos e espaços."""
    title = "Memórias Póstumas de Brás Cubas"
    result = sanitize_filename(title, ".md")
    assert result == "memorias-postumas-de-bras-cubas.md"


def test_sanitize_filename_max_length_truncation():
    """Valida truncamento de nomes de arquivo muito longos."""
    very_long_title = "A" * 150
    result = sanitize_filename(very_long_title, "txt", max_length=50)
    assert len(result) == 50 + len(".txt")
    assert result.endswith(".txt")


def test_sanitize_filename_empty_or_special_only():
    """Valida fallback gracioso quando o título consiste apenas de caracteres proibidos."""
    result = sanitize_filename('???***:::"', "md")
    assert result == "export.md"


def test_format_book_markdown_empty_book():
    """Valida mensagem graciosa para livro sem estudos em Markdown."""
    book = Book(id=1, title="Livro Vazio", author="Autor Teste", subtitle="", year=2024)
    options = ExportOptions(format=ExportFormat.MARKDOWN)
    md = format_book_markdown(book, [], [], options)

    assert "# Livro Vazio" in md
    assert "---" in md
    assert "title: \"Livro Vazio\"" in md
    assert "Nenhum estudo registrado para este livro até o momento." in md


def test_format_book_text_empty_book():
    """Valida mensagem graciosa para livro sem estudos em Texto Puro."""
    book = Book(id=1, title="Livro Vazio", author="Autor Teste", subtitle="Subtítulo", year=2024)
    options = ExportOptions(format=ExportFormat.TEXT)
    txt = format_book_text(book, [], ["Filosofia"], options)

    assert "LIVRO VAZIO" in txt
    assert "Autor: Autor Teste" in txt
    assert "Categorias: Filosofia" in txt
    assert "(Nenhum estudo registrado para este livro até o momento.)" in txt


def test_format_book_options_filtering():
    """Valida opções de inclusão e exclusão de notas e seções."""
    book = Book(id=1, title="Livro Teste", author="Autor")
    chapter = Chapter(id=1, book_id=1, name="Capítulo 1", position=0)
    study = Study(
        id=1,
        chapter_id=1,
        title="Estudo 1",
        location="p. 42",
        notes="Minha anotação pessoal importante.",
        summary="Resumo da IA.",
        explanation="Explicação detalhada.",
        concepts="Conceito A; Conceito B",
        references="Ref 1",
        source_response="Resposta bruta do LLM",
    )

    # 1. Com notas e seções ativadas, sem source
    options_default = ExportOptions(
        format=ExportFormat.MARKDOWN,
        include_notes=True,
        include_sections=True,
        include_source=False,
    )
    md_default = format_book_markdown(book, [(chapter, [study])], [], options_default)
    assert "#### Minhas Anotações" in md_default
    assert "Minha anotação pessoal importante." in md_default
    assert "#### Resumo" in md_default
    assert "#### Explicação" in md_default
    assert "#### Resposta Original de Importação" not in md_default

    # 2. Com source ativado, sem seções
    options_with_source = ExportOptions(
        format=ExportFormat.MARKDOWN,
        include_notes=True,
        include_sections=False,
        include_source=True,
    )
    md_with_source = format_book_markdown(book, [(chapter, [study])], [], options_with_source)
    assert "#### Minhas Anotações" in md_with_source
    assert "#### Resumo" not in md_with_source
    assert "#### Explicação" not in md_with_source
    assert "#### Resposta Original de Importação" in md_with_source
    assert "Resposta bruta do LLM" in md_with_source


# ==============================================================================
# T008 / T020: Testes de Integração para GET /api/books/{book_id}/export
# ==============================================================================

def test_export_book_markdown_success(client_and_db):
    client, _ = client_and_db

    # Cria Livro
    res_b = client.post("/api/books", json={"title": "Memórias Póstumas de Brás Cubas", "author": "Machado de Assis"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    # Cria Capítulo
    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo I - Do Óbito", "position": 0})
    assert res_c.status_code == 201
    chap_id = res_c.json()["id"]

    # Cria Estudo
    res_s = client.post(
        "/api/studies",
        json={
            "chapter_id": chap_id,
            "title": "A Dedicatória aos Vermes",
            "location": "p. 15",
            "notes": "Minha reflexão sobre a ironia machadiana.",
            "summary": "Resumo do primeiro capítulo.",
            "explanation": "Explicação da estrutura.",
            "concepts": "Ironia; Pessimismo",
            "references": "Schopenhauer",
            "source_response": "Bruta",
        },
    )
    assert res_s.status_code == 201

    # Faz exportação em Markdown (padrão)
    res_exp = client.get(f"/api/books/{book_id}/export")
    assert res_exp.status_code == 200
    assert "text/markdown" in res_exp.headers["content-type"]
    assert "memorias-postumas-de-bras-cubas.md" in res_exp.headers["content-disposition"]

    body = res_exp.content.decode("utf-8")
    assert "---" in body
    assert 'title: "Memórias Póstumas de Brás Cubas"' in body
    assert "# Memórias Póstumas de Brás Cubas" in body
    assert "## Capítulo I - Do Óbito" in body
    assert "### A Dedicatória aos Vermes" in body
    assert "Minha reflexão sobre a ironia machadiana." in body
    assert "#### Resumo" in body


def test_export_book_text_success(client_and_db):
    client, _ = client_and_db

    # Cria Livro
    res_b = client.post("/api/books", json={"title": "Grande Sertão: Veredas", "author": "Guimarães Rosa"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    # Cria Capítulo
    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Travessia", "position": 0})
    assert res_c.status_code == 201
    chap_id = res_c.json()["id"]

    # Cria Estudo
    res_s = client.post(
        "/api/studies",
        json={
            "chapter_id": chap_id,
            "title": "O Sertão e o Mundo",
            "location": "Início",
            "notes": "O sertão está em toda parte.",
            "summary": "Resumo.",
            "explanation": "Explicação.",
            "concepts": "Jagunços",
            "references": "Fausto",
        },
    )
    assert res_s.status_code == 201

    # Faz exportação em Texto Puro
    res_exp = client.get(f"/api/books/{book_id}/export?format=text")
    assert res_exp.status_code == 200
    assert "text/plain" in res_exp.headers["content-type"]
    assert "grande-sertao-veredas.txt" in res_exp.headers["content-disposition"]

    body = res_exp.content.decode("utf-8")
    assert "GRANDE SERTÃO: VEREDAS" in body
    assert "CAPÍTULO: TRAVESSIA" in body
    assert "ESTUDO: O Sertão e o Mundo" in body
    assert "[MINHAS ANOTAÇÕES]" in body
    assert "O sertão está em toda parte." in body


def test_export_book_not_found(client_and_db):
    client, _ = client_and_db
    res = client.get("/api/books/99999/export")
    assert res.status_code == 404
    assert res.json()["detail"] == "Livro não encontrado."


def test_export_book_in_trash_returns_404(client_and_db):
    client, _ = client_and_db

    # Cria livro e move para a lixeira
    res_b = client.post("/api/books", json={"title": "Livro Deletado", "author": "Autor"})
    book_id = res_b.json()["id"]
    res_trash = client.post(f"/api/books/{book_id}/trash")
    assert res_trash.status_code == 200

    # Tenta exportar
    res_exp = client.get(f"/api/books/{book_id}/export")
    assert res_exp.status_code == 404
    assert res_exp.json()["detail"] == "Livro não encontrado."


def test_export_book_excludes_trashed_studies(client_and_db):
    client, _ = client_and_db

    # Cria Livro
    res_b = client.post("/api/books", json={"title": "Livro com Estudos", "author": "Autor"})
    book_id = res_b.json()["id"]

    # Cria Capítulo
    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo Único", "position": 0})
    chap_id = res_c.json()["id"]

    # Cria Estudo Ativo
    res_s1 = client.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Estudo Ativo", "notes": "Anotação ativa", "summary": "Resumo ativo"},
    )
    assert res_s1.status_code == 201

    # Cria Estudo a Deletar
    res_s2 = client.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Estudo na Lixeira", "notes": "Anotação lixeira", "summary": "Resumo lixeira"},
    )
    assert res_s2.status_code == 201
    study2_id = res_s2.json()["id"]

    # Move Estudo 2 para a lixeira
    res_trash_s2 = client.post(f"/api/studies/{study2_id}/trash")
    assert res_trash_s2.status_code == 200

    # Exporta livro
    res_exp = client.get(f"/api/books/{book_id}/export")
    assert res_exp.status_code == 200
    body = res_exp.content.decode("utf-8")

    assert "Estudo Ativo" in body
    assert "Anotação ativa" in body
    assert "Estudo na Lixeira" not in body
    assert "Anotação lixeira" not in body


# ==============================================================================
# T013 / T020: Testes de Integração para GET /api/studies/{study_id}/export
# ==============================================================================

def test_export_study_markdown_success(client_and_db):
    client, _ = client_and_db

    # Cria Livro, Capítulo e Estudo
    res_b = client.post("/api/books", json={"title": "Ensaio sobre a Cegueira", "author": "José Saramago"})
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1", "position": 0})
    chap_id = res_c.json()["id"]

    res_s = client.post(
        "/api/studies",
        json={
            "chapter_id": chap_id,
            "title": "O Primeiro Cego no Semáforo",
            "location": "p. 1-10",
            "notes": "Trecho com ==destaque importante== e notas pessoais.",
            "summary": "Um motorista fica subitamente cego de uma luz branca.",
            "explanation": "A metáfora da cegueira branca.",
            "concepts": "Cegueira moral; Solidariedade",
            "references": "Kafka",
            "source_response": "Texto bruto",
        },
    )
    assert res_s.status_code == 201
    study_id = res_s.json()["id"]

    # Exporta o estudo em Markdown
    res_exp = client.get(f"/api/studies/{study_id}/export")
    assert res_exp.status_code == 200
    assert "text/markdown" in res_exp.headers["content-type"]
    assert "ensaio-sobre-a-cegueira-capitulo-1-o-primeiro-cego-no-semaforo.md" in res_exp.headers["content-disposition"]

    body = res_exp.content.decode("utf-8")
    assert "---" in body
    assert 'title: "O Primeiro Cego no Semáforo"' in body
    assert 'book: "Ensaio sobre a Cegueira"' in body
    assert 'chapter: "Capítulo 1"' in body
    assert "# O Primeiro Cego no Semáforo" in body
    assert "*Livro: Ensaio sobre a Cegueira | Capítulo: Capítulo 1*" in body
    assert "*Localização: p. 1-10*" in body
    assert "==destaque importante==" in body
    assert "#### Minhas Anotações" in body
    assert "#### Resumo" in body


def test_export_study_text_success(client_and_db):
    client, _ = client_and_db

    # Cria Livro, Capítulo e Estudo
    res_b = client.post("/api/books", json={"title": "A Hora da Estrela", "author": "Clarice Lispector"})
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Início", "position": 0})
    chap_id = res_c.json()["id"]

    res_s = client.post(
        "/api/studies",
        json={
            "chapter_id": chap_id,
            "title": "A Culpa é Minha",
            "location": "p. 11",
            "notes": "Tudo no mundo começou com um sim.",
            "summary": "Apresentação do narrador Rodrigo S.M.",
            "explanation": "Narrativa metalinguística.",
            "concepts": "Existencialismo; Metalinguagem",
            "references": "Macabéa",
        },
    )
    assert res_s.status_code == 201
    study_id = res_s.json()["id"]

    # Exporta em Texto Puro
    res_exp = client.get(f"/api/studies/{study_id}/export?format=text")
    assert res_exp.status_code == 200
    assert "text/plain" in res_exp.headers["content-type"]
    assert "a-hora-da-estrela-inicio-a-culpa-e-minha.txt" in res_exp.headers["content-disposition"]

    body = res_exp.content.decode("utf-8")
    assert "ESTUDO: A CULPA É MINHA" in body
    assert "Livro: A Hora da Estrela" in body
    assert "Capítulo: Início" in body
    assert "Localização: p. 11" in body
    assert "[MINHAS ANOTAÇÕES]" in body
    assert "Tudo no mundo começou com um sim." in body


def test_export_study_not_found(client_and_db):
    client, _ = client_and_db
    res = client.get("/api/studies/99999/export")
    assert res.status_code == 404
    assert res.json()["detail"] == "Estudo não encontrado."


def test_export_study_in_trash_returns_404(client_and_db):
    client, _ = client_and_db

    # Cria Livro, Capítulo e Estudo
    res_b = client.post("/api/books", json={"title": "Livro X", "author": "Autor"})
    book_id = res_b.json()["id"]
    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Cap 1", "position": 0})
    chap_id = res_c.json()["id"]
    res_s = client.post("/api/studies", json={"chapter_id": chap_id, "title": "Estudo Lixeira", "notes": "Notas", "summary": "Resumo"})
    study_id = res_s.json()["id"]

    # Move estudo para lixeira
    res_trash = client.post(f"/api/studies/{study_id}/trash")
    assert res_trash.status_code == 200

    # Tenta exportar
    res_exp = client.get(f"/api/studies/{study_id}/export")
    assert res_exp.status_code == 404
    assert res_exp.json()["detail"] == "Estudo não encontrado."


def test_export_study_when_parent_book_in_trash_returns_404(client_and_db):
    client, _ = client_and_db

    # Cria Livro, Capítulo e Estudo
    res_b = client.post("/api/books", json={"title": "Livro a Deletar", "author": "Autor"})
    book_id = res_b.json()["id"]
    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Cap 1", "position": 0})
    chap_id = res_c.json()["id"]
    res_s = client.post("/api/studies", json={"chapter_id": chap_id, "title": "Estudo Órfão", "notes": "Notas", "summary": "Resumo"})
    study_id = res_s.json()["id"]

    # Move Livro para a lixeira
    res_trash_book = client.post(f"/api/books/{book_id}/trash")
    assert res_trash_book.status_code == 200

    # Tenta exportar o estudo
    res_exp = client.get(f"/api/studies/{study_id}/export")
    assert res_exp.status_code == 404
    assert res_exp.json()["detail"] == "Livro não encontrado."
