from fastapi.testclient import TestClient

from app.db import session as database_session
from app.main import create_app


def test_preview_contract_works_without_accessing_or_creating_database(tmp_path, monkeypatch):
    database_path = tmp_path / "nao-criar" / "acervo.db"
    monkeypatch.setenv("CADERNO_DATABASE_PATH", str(database_path))

    def forbidden_database_access(*args, **kwargs):
        raise AssertionError("A prévia não deve acessar o banco.")

    monkeypatch.setattr(database_session, "get_engine", forbidden_database_access)
    application = create_app()
    application.dependency_overrides[database_session.get_session] = forbidden_database_access
    source = "Introdução.\r\n## Resumo\r\nPrimeiro.\r\n## RESUMO\r\nSegundo.\r\n"
    with TestClient(application) as client:
        response = client.post("/api/imports/preview", json={"source_response": source})
        assert response.status_code == 200, response.text
        assert response.headers["Cache-Control"] == "no-store"
        preview = response.json()
        assert set(preview) == {
            "source_response", "summary", "explanation", "concepts", "references", "unassigned_text", "warnings",
        }
        assert preview["source_response"] == source
        assert preview["summary"] == "Primeiro.\r\nSegundo.\r\n"
        assert preview["unassigned_text"] == "Introdução.\r\n"
        assert preview["explanation"] == preview["concepts"] == preview["references"] == ""
        assert {(w["code"], w["section"]) for w in preview["warnings"]} == {
            ("unassigned_text", None), ("repeated_section", "summary"),
            ("missing_section", "explanation"), ("missing_section", "concepts"), ("missing_section", "references"),
        }
        # A documentação oferece um exemplo que já pode ser executado.
        schema = client.get("/openapi.json").json()
        assert "/api/imports/preview" in schema["paths"]
        example = schema["components"]["schemas"]["ImportPreviewRequest"]["examples"][0]
        valid = client.post("/api/imports/preview", json=example)
        assert valid.status_code == 200, valid.text
        assert valid.json()["warnings"] == []
    assert not database_path.parent.exists()


def test_invalid_preview_requests_return_422_but_incomplete_format_can_be_reviewed():
    with TestClient(create_app()) as client:
        for payload in (
            {}, {"source_response": ""}, {"source_response": " \n\t "},
            {"source_response": None}, {"source_response": 123}, {"source_response": True},
            {"source_response": []}, {"source_response": "Texto", "chapter_id": 1},
        ):
            response = client.post("/api/imports/preview", json=payload)
            assert response.status_code == 422, response.text
        response = client.post("/api/imports/preview", json={"source_response": "Resposta sem títulos."})
        assert response.status_code == 200, response.text
        assert response.json()["unassigned_text"] == "Resposta sem títulos."
        assert any(w["code"] == "no_sections_found" for w in response.json()["warnings"])
