"""Testes automatizados isolados para o serviço de exportação (Markdown e TXT)."""
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models import Book, Chapter, ResourcePermission, Study, StudyHighlight, User
from app.schemas.export import ExportFormat, ExportOptions, ExportType
from app.services.export_service import (
    format_book_markdown,
    format_book_text,
    format_study_markdown,
    format_study_text,
    inject_highlights_into_text,
    sanitize_filename,
)


@pytest.fixture
def client_and_db(tmp_path, monkeypatch):
    """Configura base SQLite temporária e TestClient 100% isolado em tmp_path."""
    monkeypatch.setenv("REQUIRE_AUTH", "false")
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
    assert 'app: "Leitorum"' in body
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
    assert 'app: "Leitorum"' in body
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


# ==============================================================================
# Helpers e Testes Fundacionais para Destaques e Caderno de Revisão (F0.6.4)
# ==============================================================================

def create_study_with_synthetic_highlights(client):
    """Cria livro, capítulo, estudo e 4 destaques sintéticos para testes."""
    res_b = client.post("/api/books", json={"title": "Livro com Grifos", "author": "Autor dos Grifos"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo I"})
    assert res_c.status_code == 201
    chap_id = res_c.json()["id"]

    res_s = client.post(
        "/api/studies",
        json={
            "chapter_id": chap_id,
            "title": "Estudo de Leitura Ativa",
            "summary": "A imaginação é mais importante que o conhecimento científico formal.",
            "explanation": "O conhecimento é limitado enquanto a imaginação abraça o mundo inteiro.",
            "concepts": "Imaginação; Conhecimento; Epistemologia",
            "references": "Einstein, 1929",
            "notes": "Reflexão sobre a criatividade.",
        },
    )
    assert res_s.status_code == 201
    study_id = res_s.json()["id"]

    # 1. Destaque simples na seção summary
    client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 2,
            "end_offset": 12,
            "selected_text": "imaginação",
            "color": "yellow",
            "kind": "highlight",
            "note": "",
        },
    )

    # 2. Nota pessoal na seção summary
    client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 37,
            "end_offset": 60,
            "selected_text": "conhecimento científico",
            "color": "blue",
            "kind": "note",
            "note": "Ponto central da tese sobre heurística.",
        },
    )

    # 3. Pergunta de retenção na seção explanation
    client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "explanation",
            "start_offset": 19,
            "end_offset": 27,
            "selected_text": "limitado",
            "color": "purple",
            "kind": "question",
            "note": "Por que o conhecimento formal é considerado limitado?",
        },
    )

    # 4. Termo ocluído na seção explanation
    client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "explanation",
            "start_offset": 40,
            "end_offset": 50,
            "selected_text": "imaginação",
            "color": "pink",
            "kind": "hidden",
            "note": "Conceito que abraça o mundo inteiro",
        },
    )

    return book_id, chap_id, study_id


def test_inject_highlights_into_text_markdown():
    text = "O conhecimento é limitado enquanto a imaginação abraça o mundo."
    h1 = StudyHighlight(
        id=1,
        study_id=1,
        section="summary",
        start_offset=2,
        end_offset=14,
        selected_text="conhecimento",
        kind="highlight",
        note="",
    )
    h2 = StudyHighlight(
        id=2,
        study_id=1,
        section="summary",
        start_offset=17,
        end_offset=25,
        selected_text="limitado",
        kind="note",
        note="Nota sobre limitação",
    )
    h3 = StudyHighlight(
        id=3,
        study_id=1,
        section="summary",
        start_offset=37,
        end_offset=47,
        selected_text="imaginação",
        kind="question",
        note="Qual a faculdade central?",
    )

    modified, footnotes, next_idx = inject_highlights_into_text(text, [h1, h2, h3], ExportFormat.MARKDOWN, note_start_index=1)

    assert "==conhecimento==" in modified
    assert "==limitado==[^1]" in modified
    assert "==imaginação==[^2]" in modified
    assert len(footnotes) == 2
    assert footnotes[0] == (1, "**[Anotação]** Nota sobre limitação")
    assert footnotes[1] == (2, "**[Pergunta]** Qual a faculdade central?")
    assert next_idx == 3


def test_inject_highlights_into_text_text_pure():
    text = "O conhecimento é limitado enquanto a imaginação abraça o mundo."
    h1 = StudyHighlight(
        id=1,
        study_id=1,
        section="summary",
        start_offset=2,
        end_offset=14,
        selected_text="conhecimento",
        kind="highlight",
        note="",
    )
    h2 = StudyHighlight(
        id=2,
        study_id=1,
        section="summary",
        start_offset=17,
        end_offset=25,
        selected_text="limitado",
        kind="note",
        note="Nota sobre limitação",
    )

    modified, footnotes, next_idx = inject_highlights_into_text(text, [h1, h2], ExportFormat.TEXT, note_start_index=1)

    assert "«conhecimento»" in modified
    assert "«limitado» [1]" in modified
    assert len(footnotes) == 1
    assert footnotes[0] == (1, "[Anotação] Nota sobre limitação")
    assert next_idx == 2


def test_export_study_with_highlights_markdown_success(client_and_db):
    client, _ = client_and_db
    book_id, chap_id, study_id = create_study_with_synthetic_highlights(client)

    # 1. Com include_highlights=true (padrão)
    res = client.get(f"/api/studies/{study_id}/export?include_highlights=true")
    assert res.status_code == 200
    assert "text/markdown" in res.headers["content-type"]
    body = res.content.decode("utf-8")

    assert "total_highlights: 4" in body
    assert "total_questions: 1" in body
    assert "==imaginação==" in body
    assert "==conhecimento científico==[^1]" in body
    assert "[^1]: **[Anotação]** Ponto central da tese sobre heurística." in body
    assert "==limitado==[^1]" in body
    assert "[^1]: **[Pergunta]** Por que o conhecimento formal é considerado limitado?" in body
    assert "==imaginação==[^2]" in body
    assert "[^2]: **[Termo Ocluído]** Conceito que abraça o mundo inteiro" in body

    # 2. Com include_highlights=false
    res_clean = client.get(f"/api/studies/{study_id}/export?include_highlights=false")
    assert res_clean.status_code == 200
    body_clean = res_clean.content.decode("utf-8")
    assert "==imaginação==" not in body_clean
    assert "[^1]:" not in body_clean


def test_export_study_with_highlights_text_success(client_and_db):
    client, _ = client_and_db
    book_id, chap_id, study_id = create_study_with_synthetic_highlights(client)

    res = client.get(f"/api/studies/{study_id}/export?format=text&include_highlights=true")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    body = res.content.decode("utf-8")

    assert "«imaginação»" in body
    assert "«conhecimento científico» [1]" in body
    assert "NOTAS DA SEÇÃO:" in body
    assert "[1] [Anotação] Ponto central da tese sobre heurística." in body


def test_export_book_with_highlights_markdown_success(client_and_db):
    client, _ = client_and_db
    book_id, chap_id, study_id = create_study_with_synthetic_highlights(client)

    res = client.get(f"/api/books/{book_id}/export?include_highlights=true")
    assert res.status_code == 200
    body = res.content.decode("utf-8")

    assert "total_highlights: 4" in body
    assert "==imaginação==" in body
    assert "==conhecimento científico==[^1]" in body
    assert "[^1]: **[Anotação]** Ponto central da tese sobre heurística." in body


# ==============================================================================
# T013 / T014: Testes de Caderno de Revisão (Digest) e Casos de Borda (US2)
# ==============================================================================

def test_export_study_digest_markdown_study_mode_success(client_and_db):
    """Valida exportação do Caderno de Revisão de estudo individual em Markdown (Modo Estudo)."""
    client, _ = client_and_db
    book_id, chap_id, study_id = create_study_with_synthetic_highlights(client)

    res = client.get(f"/api/studies/{study_id}/export?export_type=digest&exercise_mode=false&format=markdown")
    assert res.status_code == 200
    assert "text/markdown" in res.headers["content-type"]
    assert "caderno-revisao-" in res.headers["content-disposition"]
    body = res.content.decode("utf-8")

    assert 'type: "digest"' in body
    assert 'mode: "study"' in body
    assert "total_questions: 1" in body
    assert "total_occlusions: 1" in body
    assert "total_notes: 2" in body
    assert "# Caderno de Revisão — Estudo de Leitura Ativa" in body
    assert "## 1. Perguntas de Retenção (Active Recall)" in body
    assert "Por que o conhecimento formal é considerado limitado?" in body
    assert "**Resposta:** limitado" in body
    assert "## 2. Termos Ocluídos (Cloze Deletion)" in body
    assert "==imaginação==" in body
    assert "(Dica: Conceito que abraça o mundo inteiro)" in body
    assert "## 3. Notas Marginais & Citações" in body
    assert "conhecimento científico" in body
    assert "Ponto central da tese sobre heurística." in body


def test_export_book_digest_markdown_study_mode_success(client_and_db):
    """Valida exportação do Caderno de Revisão de livro completo em Markdown."""
    client, _ = client_and_db
    book_id, chap_id, study_id = create_study_with_synthetic_highlights(client)

    res = client.get(f"/api/books/{book_id}/export?export_type=digest&exercise_mode=false&format=markdown")
    assert res.status_code == 200
    assert "text/markdown" in res.headers["content-type"]
    assert "caderno-revisao-" in res.headers["content-disposition"]
    body = res.content.decode("utf-8")

    assert 'type: "digest"' in body
    assert 'mode: "study"' in body
    assert "## Sumário da Obra" in body
    assert "Capítulo I" in body
    assert "Estudo de Leitura Ativa" in body
    assert "1. **[Capítulo I / Estudo de Leitura Ativa]**" in body
    assert "**Resposta:** limitado" in body


def test_export_study_digest_text_mode_success(client_and_db):
    """Valida exportação do Caderno de Revisão de estudo individual em Texto Puro."""
    client, _ = client_and_db
    book_id, chap_id, study_id = create_study_with_synthetic_highlights(client)

    res = client.get(f"/api/studies/{study_id}/export?export_type=digest&format=text")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    body = res.content.decode("utf-8")

    assert "CADERNO DE REVISÃO" in body
    assert "1. PERGUNTAS DE RETENÇÃO (ACTIVE RECALL)" in body
    assert "2. TERMOS OCLUÍDOS (CLOZE DELETION)" in body
    assert "3. NOTAS MARGINAIS E CITAÇÕES" in body
    assert "Resposta: limitado" in body


def test_export_study_digest_empty_highlights(client_and_db):
    """Valida mensagem informativa quando estudo não possui nenhum destaque."""
    client, _ = client_and_db

    res_b = client.post("/api/books", json={"title": "Livro Vazio", "author": "Autor"})
    b_id = res_b.json()["id"]
    res_c = client.post(f"/api/books/{b_id}/chapters", json={"name": "Cap 1", "position": 0})
    c_id = res_c.json()["id"]
    res_s = client.post(
        "/api/studies",
        json={
            "chapter_id": c_id,
            "title": "Estudo Sem Destaques",
            "summary": "Apenas texto corrido.",
        },
    )
    s_id = res_s.json()["id"]

    res = client.get(f"/api/studies/{s_id}/export?export_type=digest")
    assert res.status_code == 200
    body = res.content.decode("utf-8")
    assert "Este estudo não possui destaques, perguntas ou anotações registradas até o momento." in body


def test_export_book_digest_empty_highlights(client_and_db):
    """Valida mensagem informativa quando livro não possui nenhum destaque."""
    client, _ = client_and_db

    res_b = client.post("/api/books", json={"title": "Livro Inteiro Vazio", "author": "Autor"})
    b_id = res_b.json()["id"]
    res_c = client.post(f"/api/books/{b_id}/chapters", json={"name": "Cap 1", "position": 0})
    c_id = res_c.json()["id"]
    client.post(
        "/api/studies",
        json={
            "chapter_id": c_id,
            "title": "Estudo Limpo",
            "summary": "Sem notas.",
        },
    )

    res = client.get(f"/api/books/{b_id}/export?export_type=digest")
    assert res.status_code == 200
    body = res.content.decode("utf-8")
    assert "Este livro não possui destaques, perguntas ou anotações registradas até o momento." in body


# ==============================================================================
# T019: Testes de Modo Exercício e Gabarito de Revisão (US3)
# ==============================================================================

def test_export_study_digest_exercise_mode_markdown(client_and_db):
    """Valida omissão de respostas no corpo e inclusão de Gabarito ao final no Modo Exercício."""
    client, _ = client_and_db
    book_id, chap_id, study_id = create_study_with_synthetic_highlights(client)

    res = client.get(f"/api/studies/{study_id}/export?export_type=digest&exercise_mode=true&format=markdown")
    assert res.status_code == 200
    assert "caderno-revisao-exercicio-" in res.headers["content-disposition"]
    body = res.content.decode("utf-8")

    assert 'mode: "exercise"' in body
    assert "*Resposta:* __________________________________________________" in body
    assert "## 1. Perguntas de Retenção (Active Recall)" in body
    assert "[ _______ ]" in body

    assert "## Gabarito de Revisão" in body
    assert "### Perguntas de Retenção" in body
    assert "**Resposta:** limitado" in body
    assert "### Termos Ocluídos" in body
    assert "**Termo Ocluído:** imaginação" in body


def test_export_book_digest_exercise_mode_markdown(client_and_db):
    """Valida Modo Exercício consolidado para livro completo."""
    client, _ = client_and_db
    book_id, chap_id, study_id = create_study_with_synthetic_highlights(client)

    res = client.get(f"/api/books/{book_id}/export?export_type=digest&exercise_mode=true&format=markdown")
    assert res.status_code == 200
    assert "caderno-revisao-exercicio-" in res.headers["content-disposition"]
    body = res.content.decode("utf-8")

    assert 'mode: "exercise"' in body
    assert "*Resposta:* __________________________________________________" in body
    assert "[ _______ ]" in body
    assert "## Gabarito de Revisão" in body
    assert "**Resposta:** limitado" in body
    assert "**Termo Ocluído:** imaginação" in body


# ==============================================================================
# T023: Teste de Integração para Estudos Compartilhados em Modo Somente Leitura (US4)
# ==============================================================================

def test_export_shared_study_readonly_permission(client_and_db):
    """Garante que usuário convidado com permissão somente leitura consegue exportar."""
    client, engine = client_and_db
    user_alice_id = "11111111-1111-1111-1111-111111111111"
    user_bob_id = "22222222-2222-2222-2222-222222222222"
    user_carlos_id = "33333333-3333-3333-3333-333333333333"

    with Session(engine) as session:
        alice = User(id=user_alice_id, username="alice", email="alice@test.com", display_name="Alice", role="user", status="ativo")
        bob = User(id=user_bob_id, username="bob", email="bob@test.com", display_name="Bob", role="user", status="ativo")
        carlos = User(id=user_carlos_id, username="carlos", email="carlos@test.com", display_name="Carlos", role="user", status="ativo")
        session.add_all([alice, bob, carlos])
        session.commit()

        book = Book(title="Livro da Alice", author="Alice Autora", user_id=user_alice_id)
        session.add(book)
        session.commit()

        chapter = Chapter(book_id=book.id, name="Capítulo Compartilhado", position=0)
        session.add(chapter)
        session.commit()

        study = Study(
            chapter_id=chapter.id,
            title="Estudo da Alice Compartilhado",
            summary="Texto que Alice sintetizou com muito cuidado.",
            notes="Minhas notas privadas que viram exportação",
            visibility="custom",
            user_id=user_alice_id,
        )
        session.add(study)
        session.commit()
        study_id = study.id

        hl = StudyHighlight(
            study_id=study_id,
            section="summary",
            start_offset=6,
            end_offset=9,
            selected_text="que",
            color="yellow",
            kind="highlight",
        )
        session.add(hl)

        perm = ResourcePermission(
            resource_type="study",
            resource_id=study_id,
            granted_to_user_id=user_bob_id,
            can_view=True,
        )
        session.add(perm)
        session.commit()

    res_bob = client.get(f"/api/studies/{study_id}/export?include_highlights=true", headers={"X-User-Id": user_bob_id})
    assert res_bob.status_code == 200
    body_bob = res_bob.content.decode("utf-8")
    assert "Livro da Alice" in body_bob
    assert "==que==" in body_bob

    res_bob_digest = client.get(f"/api/studies/{study_id}/export?export_type=digest", headers={"X-User-Id": user_bob_id})
    assert res_bob_digest.status_code == 200

    res_carlos = client.get(f"/api/studies/{study_id}/export", headers={"X-User-Id": user_carlos_id})
    assert res_carlos.status_code == 404


