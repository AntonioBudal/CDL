"""EXP-024 (F04): o script do D-usuário só lê uma cópia e só devolve números (banco fictício)."""

from __future__ import annotations

import sqlite3

import dusuario_continual as du
import pytest

STUDIES = [
    (
        "u1",
        1,
        "O capítulo trata da leitura ativa.",
        "Isso importa porque fixa as ideias.",
        "Leitura ativa: ler fazendo perguntas.",
        "- A margem e o centro — Lúcia Pereira Dantas",
        "O capitulo trata da leitura ativa.\nIsso irnporta porque fixa as ideias.",
    ),
    (
        "u1",
        1,
        "O texto aborda a releitura.",
        "Por isso o autor volta ao tema.",
        "Releitura: voltar ao texto com outra pergunta.",
        "- Perguntar ao livro — Rui Cavalcante",
        "",
    ),
    (
        "u1",
        2,
        "Em síntese, a cidade respira.",
        "Eu acho que a sombra importa.",
        "Microclima: clima de um lugar pequeno.",
        "https://exemplo.org/chuva-e-cidade",
        "",
    ),
    ("u2", 3, "Resumo de teste.", "", "", "", ""),
]


@pytest.fixture
def fake_db(tmp_path):
    path = tmp_path / "ficticio.db"
    conn = sqlite3.connect(path)
    conn.executescript(
        "CREATE TABLE chapters (id INTEGER PRIMARY KEY, book_id INTEGER);"
        "CREATE TABLE studies (id INTEGER PRIMARY KEY, user_id TEXT, chapter_id INTEGER,"
        ' summary TEXT, explanation TEXT, concepts TEXT, "references" TEXT,'
        " source_response TEXT, created_at TEXT,"
        " deleted_at TEXT);"
    )
    for book in (1, 2, 3):
        conn.execute("INSERT INTO chapters (id, book_id) VALUES (?, ?)", (book, book))
    for k, (user, chapter, *cols, source) in enumerate(STUDIES):
        conn.execute(
            "INSERT INTO studies (user_id, chapter_id, summary, explanation, concepts,"
            ' "references",'
            " source_response, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user, chapter, *cols, source, f"2026-10-0{k + 1}"),
        )
    conn.commit()
    conn.close()
    return path


def test_copy_is_made_through_backup_and_source_is_untouched(fake_db, tmp_path):
    before = fake_db.read_bytes()
    folder = tmp_path / "copia"
    folder.mkdir()
    copy = du.copy_database(fake_db, folder)
    assert len(du.load_studies(copy)) == len(STUDIES)
    assert fake_db.read_bytes() == before


def test_report_has_only_numbers(fake_db, tmp_path):
    folder = tmp_path / "copia"
    folder.mkdir()
    report = du.evaluate(du.load_studies(du.copy_database(fake_db, folder)), {}, {})
    du.check_numeric(report)
    assert report["studies_total"] == 4 and report["users"] == 2
    assert report["prequential_evaluated"] == 2  # os 2 estudos de u1 depois do primeiro
    serialized = str(report)
    for study in STUDIES:
        for value in study[2:]:
            for word in value.split():
                if len(word) > 4 and not word.replace(".", "").isdigit():
                    assert word not in serialized


def test_check_numeric_rejects_text():
    with pytest.raises(ValueError):
        du.check_numeric({"studies_total": "três"})
    with pytest.raises(ValueError):
        du.check_numeric({"titulo": 1})
