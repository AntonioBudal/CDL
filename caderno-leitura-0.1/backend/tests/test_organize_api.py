"""Feature 089: API de organização nas 4 seções, com banco descartável em tmp_path e textos fictícios.

O cliente é criado sem ``with`` para não rodar a manutenção de inicialização (lifespan).
"""

import json
import time
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import text as sql
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.services.organizer import loader

FIXTURE = Path(__file__).with_name("fixtures") / "organizer-parity-v1.json"
PAGE = (
    "O capítulo trata de um tema de teste e apresenta a ideia central do autor fictício.\n"
    "Leitura de teste: leitura feita para conferir a organização automática.\n"
    "Isso importa porque mostra se o texto vai para a seção certa, ou seja, se a regra funciona.\n"
    "p. 42 — achei confuso o exemplo, preciso reler com calma\n"
    "“Uma citação fictícia escrita só para o teste.”\n"
    "SOBRENOME, Nome. Livro de Teste. Cidade: Editora Fictícia, 2020."
)


@pytest.fixture
def client(tmp_path):
    path = tmp_path / "acervo-organizar.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session
    loader.reset_cache()
    try:
        yield TestClient(application), engine
    finally:
        loader.reset_cache()
        engine.dispose()


def post(client, text, lines=None):
    payload = {"text": text}
    if lines is not None:
        payload["lines"] = lines
    return client.post("/api/imports/organize", json=payload)


def by_text(body):
    return {s["text"]: s["section"] for s in body["segments"]}


def test_status_available(client):
    response = client[0].get("/api/imports/organize/status")
    assert response.status_code == 200
    assert response.json() == {"available": True, "reason": None, "version": "1"}
    assert response.headers["cache-control"] == "no-store"


def test_missing_artifact_makes_feature_unavailable(client, monkeypatch, tmp_path):
    monkeypatch.setattr(loader, "ARTIFACT", tmp_path / "ausente.json")
    loader.reset_cache()
    assert client[0].get("/api/imports/organize/status").json() == {"available": False, "reason": "not_installed", "version": None}
    response = post(client[0], PAGE)
    assert response.status_code == 503
    assert response.json()["code"] == "unavailable"


def test_corrupted_artifact_fails_integrity(client, monkeypatch, tmp_path):
    fake = tmp_path / "organizer-v1.json"
    fake.write_text('{"versao": "adulterada"}', encoding="utf-8")
    monkeypatch.setattr(loader, "ARTIFACT", fake)
    loader.reset_cache()
    assert client[0].get("/api/imports/organize/status").json()["reason"] == "integrity_failed"


def test_organize_is_lossless_and_sections_are_original_text(client):
    response = post(client[0], PAGE)
    assert response.status_code == 200, response.text
    body = response.json()
    marks = [0] * len(PAGE)
    for seg in body["segments"]:
        assert seg["text"] == PAGE[seg["start"]:seg["end"]]
        for i in range(seg["start"], seg["end"]):
            marks[i] += 1
    assert all(m == 1 for ch, m in zip(PAGE, marks, strict=True) if not ch.isspace())
    for section, content in body["sections"].items():
        assert content == "\n".join(s["text"] for s in body["segments"] if s["section"] == section)
    assert body["review_count"] == sum(s["review"] for s in body["segments"])
    assert body["warnings"][0]["code"] == "suggestion"
    assert body["engine"]["name"] == "leitorum-organizer"
    assert response.headers["cache-control"] == "no-store"


def test_reference_policy_from_the_spec(client):
    sections = by_text(post(client[0], PAGE).json())
    assert sections["SOBRENOME, Nome. Livro de Teste. Cidade: Editora Fictícia, 2020."] == "references"
    assert sections["“Uma citação fictícia escrita só para o teste.”"] == "references"
    assert sections["p. 42 — achei confuso o exemplo, preciso reler com calma"] == "explanation"


def test_inline_citation_stays_with_its_sentence(client):
    text = "Leitura de teste: conceito fictício definido pelo autor (SOBRENOME, 2020, p. 12) para o exemplo."
    body = post(client[0], text).json()
    assert len(body["segments"]) == 1
    assert body["segments"][0]["text"] == text


def test_explicit_headings_win(client):
    text = (
        "Conceitos:\nTermo de teste: definição fictícia.\n"
        "Resumo:\nO capítulo trata de um tema fictício.\n"
        "Referências\nSOBRENOME, Nome. Livro de Teste. Cidade: Editora, 2020."
    )
    body = post(client[0], text).json()
    assert body["explicit_headings"] is True
    sections = by_text(body)
    assert sections["Termo de teste: definição fictícia."] == "concepts"
    assert sections["O capítulo trata de um tema fictício."] == "summary"


def test_accepts_layout_lines(client):
    lines = [{"text": line, "bbox": [120, 140 + 80 * i, 1400, 200 + 80 * i], "confidence": 0.9} for i, line in enumerate(PAGE.split("\n"))]
    lines[1]["bbox"] = None
    lines[2]["confidence"] = None
    assert post(client[0], PAGE, lines).status_code == 200


def test_single_section_warning(client):
    body = post(client[0], "SOBRENOME, Nome. Livro de Teste. Cidade: Editora, 2020.\nOUTRO, Nome. Outro Livro. Cidade: Editora, 2019.").json()
    assert [w["code"] for w in body["warnings"]] == ["suggestion", "single_section"]


def test_limits_and_validation(client):
    c = client[0]
    too_long = post(c, "a" * 50_001)
    assert too_long.status_code == 413 and too_long.json()["code"] == "too_large"
    too_many = post(c, "\n".join(f"Linha de teste número {i}." for i in range(401)))
    assert too_many.status_code == 413 and too_many.json()["code"] == "too_large"
    empty = post(c, "   \n ")
    assert empty.status_code == 422 and empty.json()["code"] == "empty_text"
    assert c.post("/api/imports/organize", json={}).status_code == 422
    assert c.post("/api/imports/organize", json={"text": "x", "extra": 1}).status_code == 422
    assert post(c, "Texto de teste.", [{"text": "x", "bbox": [1, 2, 3]}]).status_code == 422


def test_requires_authentication(client, monkeypatch):
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    assert client[0].get("/api/imports/organize/status").status_code == 401
    assert post(client[0], PAGE).status_code == 401


def test_no_database_writes_and_no_text_in_logs(client, caplog):
    c, engine = client
    with engine.connect() as conn:
        before = conn.execute(sql("SELECT COUNT(*) FROM studies")).scalar()
    with caplog.at_level("DEBUG"):
        assert post(c, PAGE).status_code == 200
    with engine.connect() as conn:
        assert conn.execute(sql("SELECT COUNT(*) FROM studies")).scalar() == before
    assert "Livro de Teste" not in caplog.text
    assert "fictícia" not in caplog.text


def test_latency_regression_guard(client):
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]
    times = []
    for case in cases:
        started = time.perf_counter()
        loader.organize(case["text"], case["lines"])
        times.append(time.perf_counter() - started)
    times.sort()
    assert times[int(len(times) * 0.95)] < 1.0
