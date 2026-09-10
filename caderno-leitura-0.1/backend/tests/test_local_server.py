from contextlib import contextmanager
from html.parser import HTMLParser
import os
import socket
import subprocess
import sys
import time

from alembic import command
from alembic.config import Config
import httpx
import pytest

from app.core.config import BACKEND_DIR, get_frontend_dist_path


class BuildAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'script' and attrs.get('src'):
            self.urls.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in {'stylesheet', 'modulepreload'} and attrs.get('href'):
            self.urls.append(attrs['href'])


@contextmanager
def python_server(database_path, working_directory):
    # Porta efêmera para coexistir com o caderno real do usuário, sem tocá-lo.
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    environment = os.environ.copy()
    environment['CADERNO_DATABASE_PATH'] = str(database_path)
    environment.pop('WEB_CONCURRENCY', None)
    log_path = working_directory / 'uvicorn-test.log'
    with log_path.open('a', encoding='utf-8') as log:
        process = subprocess.Popen(
            [sys.executable, '-m', 'uvicorn', 'app.main:app', '--app-dir', str(BACKEND_DIR),
             '--host', '127.0.0.1', '--port', str(port), '--workers', '1', '--log-level', 'warning'],
            cwd=working_directory, env=environment, stdout=log, stderr=subprocess.STDOUT,
        )
        try:
            with httpx.Client(base_url=f'http://127.0.0.1:{port}', timeout=3, trust_env=False) as client:
                deadline = time.monotonic() + 15
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        pytest.fail(f'Servidor de teste encerrou: {log_path.read_text(encoding="utf-8")}')
                    try:
                        if client.get('/api/health').status_code == 200:
                            break
                    except httpx.TransportError:
                        pass
                    time.sleep(0.05)
                else:
                    pytest.fail(f'Servidor de teste não iniciou: {log_path.read_text(encoding="utf-8")}')
                yield client
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


def test_compiled_interface_and_api_work_in_one_python_server_and_persist_after_restart(tmp_path):
    index = get_frontend_dist_path() / 'index.html'
    if not index.is_file():
        pytest.skip('Gere frontend/dist com npm run build para executar a integração com o servidor real.')
    pytest.importorskip('uvicorn', reason='Instale as dependências de backend/requirements-dev.txt.')
    database_path = tmp_path / 'acervo-teste.db'
    config = Config(str(BACKEND_DIR / 'alembic.ini'))
    config.attributes['database_path'] = database_path
    command.upgrade(config, 'head')
    navigation = {'Accept': 'text/html'}
    with python_server(database_path, tmp_path) as client:
        page = client.get('/')
        assert page.status_code == 200
        assert page.content == index.read_bytes()
        assets = BuildAssets()
        assets.feed(page.text)
        assert any(url.endswith('.js') for url in assets.urls)
        assert any(url.endswith('.css') for url in assets.urls)
        assert '/src/main.ts' not in page.text
        assert '@vite/client' not in page.text
        for url in assets.urls:
            assert url.startswith('/assets/'), url
            response = client.get(url)
            assert response.status_code == 200
            assert response.content == (get_frontend_dist_path() / url.lstrip('/')).read_bytes()
            expected_type = 'javascript' if url.endswith('.js') else 'text/css'
            assert expected_type in response.headers['content-type']

        book_response = client.post('/api/books', json={'title': 'Livro de integração — atenção'})
        assert book_response.status_code == 201
        book = book_response.json()
        chapter_response = client.post(f'/api/books/{book["id"]}/chapters', json={'name': 'Capítulo 1'})
        assert chapter_response.status_code == 201
        chapter = chapter_response.json()
        source = '## Resumo\r\n**Atenção** ao texto.\r\n## Explicação\r\nTexto original.\r\n## Conceitos\r\n- Leitura\r\n## Referências\r\nSem fontes externas.\r\n'
        preview_response = client.post('/api/imports/preview', json={'source_response': source})
        assert preview_response.status_code == 200
        preview = preview_response.json()
        create_response = client.post('/api/studies', json={
            'chapter_id': chapter['id'], 'title': 'Estudo de integração', 'location': 'p. 12–14',
            'source_response': preview['source_response'],
            **{field: preview[field] for field in ('summary', 'explanation', 'concepts', 'references')},
            'notes': 'Minha interpretação.\nSegunda linha.',
        })
        assert create_response.status_code == 201
        original = create_response.json()
        study_url = f'/api/studies/{original["id"]}'
        reader_url = f'/livros/{book["id"]}/estudos/{original["id"]}'
        assert client.get(reader_url, headers=navigation).content == page.content
        assert client.get(reader_url + '/editar', headers=navigation).content == page.content
        changed = client.patch(study_url, json={'explanation': 'Explicação revisada.\nOutro parágrafo.'})
        assert changed.status_code == 200
        saved = changed.json()
        for field in ('summary', 'concepts', 'references', 'source_response', 'notes', 'location', 'title'):
            assert saved[field] == original[field]
        assert saved['explanation'] == 'Explicação revisada.\nOutro parágrafo.'
        assert client.get(study_url).json() == saved
        missing = client.get('/api/rota-inexistente', headers=navigation)
        assert missing.status_code == 404
        assert missing.json() == {'detail': 'Not Found'}
        assert client.get('/docs').status_code == 200

    # Novo processo, mesmo arquivo SQLite temporário; o Vite não participa do teste.
    with python_server(database_path, tmp_path) as client:
        assert client.get(study_url).json() == saved
        assert client.get(reader_url, headers=navigation).content == index.read_bytes()
