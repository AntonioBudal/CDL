from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.core.config import BACKEND_DIR, get_frontend_dist_path
from app.main import create_app

INDEX = '<!doctype html><html lang="pt-BR"><div id="app">Caderno de teste</div></html>'
HTML_HEADERS = {"Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"}


@pytest.fixture
def public_dir(tmp_path):
    directory = tmp_path / "projeto ação 100%" / "frontend" / "dist"
    (directory / "assets").mkdir(parents=True)
    (directory / "index.html").write_text(INDEX, encoding="utf-8")
    (directory / "assets" / "app-123.js").write_text('console.log("caderno");', encoding="utf-8")
    (directory / "assets" / "app-123.css").write_text('body { color: navy; }', encoding="utf-8")
    return directory


@pytest.fixture
def client(public_dir):
    with TestClient(create_app(frontend_dist=public_dir)) as client:
        yield client


def test_root_and_build_files_have_correct_content_types_and_cache(client):
    root = client.get('/')
    assert root.status_code == 200
    assert root.text == INDEX
    assert root.headers['content-type'].startswith('text/html')
    assert root.headers['cache-control'] == 'no-store'
    assert client.get('/index.html').text == INDEX
    script = client.get('/assets/app-123.js')
    assert script.status_code == 200
    assert 'javascript' in script.headers['content-type']
    assert script.text == 'console.log("caderno");'
    assert script.headers['cache-control'] == 'no-cache'
    assert script.headers['x-content-type-options'] == 'nosniff'
    style = client.get('/assets/app-123.css')
    assert style.status_code == 200
    assert style.headers['content-type'].startswith('text/css')
    head = client.head('/assets/app-123.js')
    assert head.status_code == 200
    assert head.content == b''
    assert head.headers['content-length'] == script.headers['content-length']
    unchanged = client.get('/assets/app-123.js', headers={'If-None-Match': script.headers['etag']})
    assert unchanged.status_code == 304
    assert unchanged.content == b''


@pytest.mark.parametrize('path', [
    '/livros/1', '/livros/1?chapter=2', '/livros/1/estudos/2',
    '/livros/1/estudos/2/editar', '/importar?book=1&chapter=2', '/conexao', '/pagina-inexistente',
])
def test_refresh_of_frontend_routes_serves_index(client, path):
    response = client.get(path, headers=HTML_HEADERS)
    assert response.status_code == 200
    assert response.text == INDEX
    assert response.headers['cache-control'] == 'no-store'
    head = client.head(path, headers=HTML_HEADERS)
    assert head.status_code == 200
    assert head.content == b''


@pytest.mark.parametrize('path', ['/api', '/api/inexistente', '/api/books/1/inexistente', '/docs/inexistente', '/redoc/inexistente', '/openapi.json/inexistente'])
def test_unknown_api_and_docs_paths_keep_json_404_even_when_accepting_html(client, path):
    for method in ('GET', 'POST'):
        response = client.request(method, path, headers=HTML_HEADERS)
        assert response.status_code == 404
        assert response.headers['content-type'].startswith('application/json')
        assert response.json() == {'detail': 'Not Found'}


def test_api_docs_methods_and_redirects_keep_priority(client):
    assert client.get('/api/health').json()['status'] == 'ok'
    wrong_method = client.delete('/api/health', headers=HTML_HEADERS)
    assert wrong_method.status_code == 405
    assert wrong_method.headers['content-type'].startswith('application/json')
    assert 'GET' in wrong_method.headers['allow']
    assert client.get('/api/health/', follow_redirects=False).status_code == 307
    assert 'swagger-ui' in client.get('/docs').text
    assert 'redoc' in client.get('/redoc').text
    schema = client.get('/openapi.json').json()
    assert '/api/imports/preview' in schema['paths']
    assert all(path.startswith('/api/') for path in schema['paths'])


@pytest.mark.parametrize('path', ['/assets/ausente.js', '/assets/ausente.css', '/assets/sem-extensao', '/favicon.ico', '/nao-existe.json'])
def test_missing_assets_do_not_receive_index_html(client, path):
    response = client.get(path, headers=HTML_HEADERS)
    assert response.status_code == 404
    assert response.headers['content-type'].startswith('application/json')


def test_fallback_is_only_for_html_navigation(client):
    for accept in ('application/json', '*/*', 'text/html;q=0', 'text/html;q=invalid'):
        assert client.get('/livros/1', headers={'Accept': accept}).status_code == 404
    assert client.post('/livros/1', headers=HTML_HEADERS).status_code == 404


def test_server_starts_without_build_and_api_still_works(tmp_path):
    directory = tmp_path / 'frontend' / 'dist'
    with TestClient(create_app(frontend_dist=directory)) as client:
        assert client.get('/api/health').status_code == 200
        assert client.get('/docs').status_code == 200
        for path in ('/', '/livros/1/estudos/2'):
            response = client.get(path, headers=HTML_HEADERS)
            assert response.status_code == 503
            assert 'npm run build' in response.json()['detail']
        assert client.get('/assets/missing.js', headers=HTML_HEADERS).status_code == 404
        # Um build criado depois passa a ser servido sem criar banco nem diretório automaticamente.
        assert not directory.exists()
        directory.mkdir(parents=True)
        (directory / 'index.html').write_text(INDEX, encoding='utf-8')
        assert client.get('/').text == INDEX


def test_missing_index_in_incomplete_build_is_a_controlled_error(public_dir):
    (public_dir / 'index.html').unlink()
    with TestClient(create_app(frontend_dist=public_dir)) as client:
        assert client.get('/').status_code == 503
        assert client.get('/api/health').status_code == 200


def test_only_public_files_are_accessible_and_hidden_files_are_rejected(client, public_dir):
    project = public_dir.parents[1]
    (project / 'backend' / 'data').mkdir(parents=True)
    (project / 'backend' / 'data' / 'caderno.db').write_bytes(b'PRIVATE_DATABASE')
    (project / 'backend' / 'main.py').write_text('PRIVATE_PYTHON', encoding='utf-8')
    (public_dir / '.env').write_text('PRIVATE_CONFIG', encoding='utf-8')
    for path in (
        '/backend/data/caderno.db', '/backend/main.py', '/.env',
        '/%2e%2e/%2e%2e/backend/data/caderno.db', '/assets/%2e%2e/%2e%2e/backend/main.py',
        '/..%5c..%5cbackend%5cdata%5ccaderno.db', '/C:%5cWindows%5cwin.ini', '/bad%00name.js',
    ):
        response = client.get(path, headers=HTML_HEADERS)
        assert response.status_code == 404, (path, response.text)
        assert 'PRIVATE_' not in response.text


def test_symlink_cannot_expose_files_outside_public_directory(client, public_dir, tmp_path):
    outside = tmp_path / 'private.db'
    outside.write_bytes(b'PRIVATE_DATABASE')
    try:
        (public_dir / 'exposed.db').symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip('Este ambiente não permite criar links simbólicos.')
    response = client.get('/exposed.db', headers=HTML_HEADERS)
    assert response.status_code == 404
    assert b'PRIVATE_DATABASE' not in response.content


def test_database_cannot_be_configured_inside_the_public_build(public_dir, monkeypatch):
    monkeypatch.setenv('CADERNO_DATABASE_PATH', str(public_dir / 'acervo.db'))
    with pytest.raises(ValueError, match='fora de frontend/dist'):
        create_app(frontend_dist=public_dir)


def test_frontend_default_path_is_independent_of_working_directory(tmp_path, monkeypatch):
    expected = BACKEND_DIR.parent / 'frontend' / 'dist'
    monkeypatch.chdir(tmp_path)
    assert get_frontend_dist_path() == expected
    assert get_frontend_dist_path().is_absolute()


def test_build_changes_are_seen_without_restarting(client, public_dir):
    assert client.get('/').text == INDEX
    new_index = INDEX.replace('Caderno de teste', 'Caderno atualizado')
    (public_dir / 'index.html').write_text(new_index, encoding='utf-8')
    response = client.get('/')
    assert response.status_code == 200
    assert response.text == new_index
