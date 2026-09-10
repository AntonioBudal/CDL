import json
import os
import subprocess
import sys

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app


def make_client(engine):
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session
    return TestClient(application)


@pytest.fixture
def api(tmp_path):
    path = tmp_path / "acervo-api.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def create_parents(client):
    response = client.post('/api/books', json={"title": "Livro de teste", "author": "Autor de teste"})
    assert response.status_code == 201, response.text
    book = response.json()
    response = client.post(f'/api/books/{book["id"]}/chapters', json={"name": "Capítulo 1"})
    assert response.status_code == 201, response.text
    return book, response.json()


def create_study(client, chapter_id, **changes):
    payload = {
        "chapter_id": chapter_id,
        "location": "p. 32–34",
        "source_response": "  ## Resumo\nTexto original com ação e atenção.\n",
        "summary": "Resumo preservado.",
        "explanation": "Explicação original.\nSegunda linha.",
        "concepts": "Conceito importante.",
        "references": "Nenhuma referência externa verificada.",
        "notes": "  Minha interpretação.\nQuero revisar amanhã.  ",
        **changes,
    }
    response = client.post('/api/studies', json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_api_workflow_persists_after_new_process(api, tmp_path):
    client, engine, path = api
    book, chapter = create_parents(client)
    study = create_study(client, chapter['id'])
    assert study['title'] == 'Capítulo 1 — p. 32–34'
    assert study['created_at'].endswith('Z')
    assert client.get('/api/books').json() == [book]
    assert client.get(f'/api/books/{book["id"]}/chapters').json() == [chapter]
    listed = client.get(f'/api/chapters/{chapter["id"]}/studies').json()
    assert [item['id'] for item in listed] == [study['id']]
    assert 'source_response' not in listed[0]
    assert 'notes' not in listed[0]

    response = client.patch(f'/api/studies/{study["id"]}', json={"explanation": "Explicação corrigida.\nOutra linha."})
    assert response.status_code == 200, response.text
    edited = response.json()
    for field in ('summary', 'concepts', 'references', 'notes', 'source_response', 'location', 'created_at'):
        assert edited[field] == study[field]
    assert edited['explanation'] != study['explanation']
    assert client.get(f'/api/studies/{study["id"]}').json() == edited
    assert client.get('/api/health').json()['status'] == 'ok'
    assert client.get('/docs').status_code == 200

    # Nova aplicacao em outro processo, usando a dependencia real da sessao.
    engine.dispose()
    environment = os.environ.copy()
    environment['CADERNO_DATABASE_PATH'] = str(path)
    environment['PYTHONPATH'] = str(BACKEND_DIR)
    script = """
import json, sys
from fastapi.testclient import TestClient
from app.main import create_app
from app.db.session import get_engine
with TestClient(create_app()) as client:
    response = client.get('/api/studies/' + sys.argv[1])
    assert response.status_code == 200, response.text
    print(json.dumps(response.json()))
get_engine().dispose()
"""
    result = subprocess.run(
        [sys.executable, '-c', script, str(study['id'])],
        cwd=tmp_path, env=environment, check=True, capture_output=True, text=True, encoding='utf-8',
    )
    assert json.loads(result.stdout) == edited


def test_lists_respect_parent_and_chapter_order(api):
    client, _, _ = api
    assert client.get('/api/books').json() == []
    first_book, first_chapter = create_parents(client)
    second_book, second_chapter = create_parents(client)
    assert first_chapter['position'] == second_chapter['position'] == 0
    explicit = client.post(f'/api/books/{first_book["id"]}/chapters', json={"name": "Mais tarde", "position": 4}).json()
    appended = client.post(f'/api/books/{first_book["id"]}/chapters', json={"name": "Último"}).json()
    assert appended['position'] == 5
    assert client.get(f'/api/books/{first_book["id"]}/chapters').json() == [first_chapter, explicit, appended]
    assert client.get(f'/api/books/{second_book["id"]}/chapters').json() == [second_chapter]
    assert client.get(f'/api/chapters/{first_chapter["id"]}/studies').json() == []
    first_study = create_study(client, first_chapter['id'])
    create_study(client, second_chapter['id'])
    assert [item['id'] for item in client.get(f'/api/chapters/{first_chapter["id"]}/studies').json()] == [first_study['id']]


def test_missing_records_and_parents_return_404(api):
    client, _, _ = api
    requests = (
        ('GET', '/api/books/99999/chapters', None),
        ('POST', '/api/books/99999/chapters', {'name': 'Capítulo'}),
        ('GET', '/api/chapters/99999/studies', None),
        ('POST', '/api/studies', {'chapter_id': 99999, 'summary': 'Texto'}),
        ('GET', '/api/studies/99999', None),
        ('PATCH', '/api/studies/99999', {'notes': 'Anotação'}),
    )
    for method, url, payload in requests:
        response = client.request(method, url, json=payload)
        assert response.status_code == 404, response.text
        assert 'não encontrado' in response.json()['detail']
    assert client.get('/api/books').json() == []


def test_invalid_book_and_chapter_payloads_are_rejected(api):
    client, _, _ = api
    for payload in ({}, {'title': ' \n\t '}, {'title': 123}, {'title': 'Livro', 'unknown': True}):
        assert client.post('/api/books', json=payload).status_code == 422
    book = client.post('/api/books', json={'title': '  Livro  ', 'author': '  '}).json()
    assert book['title'] == 'Livro'
    assert book['author'] is None
    for payload in ({'name': '\t '}, {'name': 'Capítulo', 'position': -1}, {'name': 'Capítulo', 'position': True}):
        response = client.post(f'/api/books/{book["id"]}/chapters', json=payload)
        assert response.status_code == 422, response.text
    assert client.get(f'/api/books/{book["id"]}/chapters').json() == []


def test_invalid_study_payloads_do_not_write(api):
    client, _, _ = api
    _, chapter = create_parents(client)
    payloads = (
        {'chapter_id': chapter['id']},
        {'chapter_id': chapter['id'], 'summary': ' \n\t ', 'notes': 'Só notas'},
        {'chapter_id': chapter['id'], 'summary': 'Texto', 'notes': None},
        {'chapter_id': str(chapter['id']), 'summary': 'Texto'},
        {'chapter_id': True, 'summary': 'Texto'},
    )
    for payload in payloads:
        response = client.post('/api/studies', json=payload)
        assert response.status_code == 422, response.text
    assert client.get(f'/api/chapters/{chapter["id"]}/studies').json() == []


def test_optional_title_location_and_notes(api):
    client, _, _ = api
    _, chapter = create_parents(client)
    response = client.post('/api/studies', json={'chapter_id': chapter['id'], 'title': '  ', 'summary': '  Texto\n  '})
    assert response.status_code == 201, response.text
    study = response.json()
    assert study['title'] == chapter['name']
    assert study['location'] == study['notes'] == study['source_response'] == ''
    assert study['summary'] == '  Texto\n  '
    assert study['explanation'] == study['concepts'] == study['references'] == ''
    custom = create_study(client, chapter['id'], title='  Título próprio  ')
    assert custom['title'] == 'Título próprio'


def test_patch_rejects_null_empty_and_protected_fields(api):
    client, _, _ = api
    _, chapter = create_parents(client)
    original = create_study(client, chapter['id'])
    url = f'/api/studies/{original["id"]}'
    payloads = ({}, {'notes': None}, {'title': '\t '}, {'source_response': 'Substituição'}, {'chapter_id': chapter['id']}, {'id': 45})
    for payload in payloads:
        response = client.patch(url, json=payload)
        assert response.status_code == 422, response.text
        assert client.get(url).json() == original


def test_patch_cannot_clear_all_analysis_or_partially_apply(api):
    client, _, _ = api
    _, chapter = create_parents(client)
    original = create_study(client, chapter['id'])
    url = f'/api/studies/{original["id"]}'
    changes = {name: ' \n\t ' for name in ('summary', 'explanation', 'concepts', 'references')}
    changes['notes'] = 'Também não deve ser gravado'
    response = client.patch(url, json=changes)
    assert response.status_code == 422, response.text
    assert client.get(url).json() == original


def test_patch_can_clear_optional_fields_while_other_analysis_remains(api):
    client, _, _ = api
    _, chapter = create_parents(client)
    original = create_study(client, chapter['id'])
    response = client.patch(f'/api/studies/{original["id"]}', json={'notes': '', 'location': '', 'summary': ''})
    assert response.status_code == 200, response.text
    changed = response.json()
    assert changed['notes'] == changed['location'] == changed['summary'] == ''
    for field in ('explanation', 'concepts', 'references', 'source_response', 'title'):
        assert changed[field] == original[field]


def test_database_write_failure_is_not_reported_as_success(api):
    client, engine, _ = api
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TRIGGER reject_test_insert AFTER INSERT ON books BEGIN SELECT RAISE(ABORT, 'detalhe interno de teste'); END;")
    response = client.post('/api/books', json={'title': 'Não pode permanecer gravado'})
    assert response.status_code == 409, response.text
    assert 'detalhe interno' not in response.text
    assert client.get('/api/books').json() == []
    with engine.begin() as connection:
        connection.exec_driver_sql('DROP TRIGGER reject_test_insert')
    assert client.post('/api/books', json={'title': 'Nova tentativa válida'}).status_code == 201


def test_missing_migration_returns_controlled_database_error(tmp_path):
    engine = create_sqlite_engine(tmp_path / 'sem-migracao.db')
    try:
        with make_client(engine) as client:
            assert client.get('/api/health').status_code == 200
            response = client.get('/api/books')
            assert response.status_code == 503, response.text
            assert 'migrações' in response.json()['detail']
            assert 'SELECT' not in response.text
    finally:
        engine.dispose()


def test_invalid_path_identifiers_return_422(api):
    client, _, _ = api
    for value in ('0', '-1', 'abc', str(2**63)):
        assert client.get(f'/api/studies/{value}').status_code == 422


def test_preview_review_and_save_keep_original_and_manual_corrections(api):
    client, engine, _ = api
    _, chapter = create_parents(client)
    source = (
        "Observação fora das seções.\r\n## Resumo\r\nResumo inicial.\r\n"
        "## Resumo\r\nComplemento.\r\n## Referências\r\nSem fontes externas.\r\n"
    )
    preview_response = client.post('/api/imports/preview', json={"source_response": source})
    assert preview_response.status_code == 200, preview_response.text
    preview = preview_response.json()
    assert client.get(f'/api/chapters/{chapter["id"]}/studies').json() == []

    # A conferência distribui o texto não associado e corrige a prévia antes de salvar.
    payload = {
        "chapter_id": chapter['id'], "location": "p. 15", "source_response": preview['source_response'],
        "summary": "Resumo corrigido pelo usuário.",
        "explanation": preview['unassigned_text'], "concepts": preview['concepts'],
        "references": preview['references'], "notes": "Minha interpretação pessoal.",
    }
    saved_response = client.post('/api/studies', json=payload)
    assert saved_response.status_code == 201, saved_response.text
    saved = saved_response.json()
    assert saved['summary'] == payload['summary']
    assert saved['source_response'] == source
    assert saved['explanation'] == "Observação fora das seções.\r\n"
    assert saved['notes'] == payload['notes']
    assert saved['concepts'] == ''

    # Outra prévia não altera o registro; uma nova conexão encontra a revisão salva.
    assert client.post('/api/imports/preview', json={"source_response": "## Resumo\nOutro texto."}).status_code == 200
    engine.dispose()
    with make_client(engine) as reopened:
        assert reopened.get(f'/api/studies/{saved["id"]}').json() == saved
        assert len(reopened.get(f'/api/chapters/{chapter["id"]}/studies').json()) == 1
