import sqlite3

from alembic import command
from alembic.config import Config

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME


def test_legacy_data_migrates_to_canonical_owner(tmp_path):
    """US1 (T010, T012): Valida que uma base legada da v0.4 é migrada para a v0.5

    atribuindo 100% dos dados pré-existentes ao proprietário canônico soberano sem perdas,
    e que o processo é idempotente e reversível.
    """
    db_path = tmp_path / "legacy_migration_test.db"
    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.attributes["database_path"] = db_path

    # 1. Aplica migrações até a última da v0.4 (0010_add_search_history)
    command.upgrade(alembic_cfg, "0010_add_search_history")

    # 2. Popula dados legados sintéticos representativos de todas as tabelas
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (id, title, author, subtitle, year) VALUES (?, ?, ?, ?, ?)",
            (1, "Crítica da Razão Pura", "Immanuel Kant", "Filosofia Teórica", 1781),
        )
        cursor.execute(
            "INSERT INTO chapters (id, book_id, name, position) VALUES (?, ?, ?, ?)",
            (1, 1, "Prefácio à Primeira Edição", 0),
        )
        cursor.execute(
            """INSERT INTO studies (id, chapter_id, position, reading_status, title, summary,
               explanation, concepts, "references", notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (1, 1, 0, "concluido", "Síntese a Priori", "Resumo", "Explicação", "Conceitos", "Refs", "Notas"),
        )
        cursor.execute(
            """INSERT INTO studies (id, chapter_id, position, reading_status, title, summary,
               explanation, concepts, "references", notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (2, 1, 1, "em_leitura", "Estética Transcendental", "Resumo 2", "Exp 2", "Conceitos 2", "Refs 2", "Notas 2"),
        )
        cursor.execute(
            "INSERT INTO study_relations (id, source_study_id, target_study_id, relation_type, description) VALUES (?, ?, ?, ?, ?)",
            (1, 1, 2, "relacionado_com", "Conexão epistemológica"),
        )
        cursor.execute(
            "INSERT INTO study_canvas_nodes (id, study_id, book_id, pos_x, pos_y, z_index) VALUES (?, ?, ?, ?, ?, ?)",
            (1, 1, 1, 120.0, 240.0, 1),
        )
        cursor.execute(
            "INSERT INTO canvas_frames (id, book_id, title, color, pos_x, pos_y, width, height) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (1, 1, "Quadro Epistêmico", "neutral", 50.0, 50.0, 400.0, 300.0),
        )
        cursor.execute(
            "INSERT INTO search_history (id, query) VALUES (?, ?)",
            (1, "Kant sintético"),
        )
        cursor.execute(
            "INSERT INTO categories (id, name, path) VALUES (?, ?, ?)",
            ("categoria_legada_customizada", "Categoria Legada", "Categoria Legada"),
        )
        cursor.execute(
            "INSERT INTO book_categories (book_id, category_id) VALUES (?, ?)",
            (1, "categoria_legada_customizada"),
        )
        conn.commit()

    # 3. Executa a migração da Feature 01 (head)
    command.upgrade(alembic_cfg, "head")

    # 4. Verifica integridade e vinculação ao proprietário canônico
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Usuário canônico provisionado
        user = cursor.execute("SELECT * FROM users WHERE id = ?", (DEFAULT_OWNER_ID,)).fetchone()
        assert user is not None
        assert user["username"] == DEFAULT_OWNER_USERNAME
        assert user["status"] == "ativo"

        # Livros
        book = cursor.execute("SELECT * FROM books WHERE id = 1").fetchone()
        assert book["user_id"] == DEFAULT_OWNER_ID
        assert book["title"] == "Crítica da Razão Pura"

        # Estudos
        study1 = cursor.execute("SELECT * FROM studies WHERE id = 1").fetchone()
        assert study1["user_id"] == DEFAULT_OWNER_ID
        assert study1["title"] == "Síntese a Priori"

        study2 = cursor.execute("SELECT * FROM studies WHERE id = 2").fetchone()
        assert study2["user_id"] == DEFAULT_OWNER_ID

        # Relações
        rel = cursor.execute("SELECT * FROM study_relations WHERE id = 1").fetchone()
        assert rel["user_id"] == DEFAULT_OWNER_ID
        assert rel["relation_type"] == "relacionado_com"

        # Nós de canvas
        node = cursor.execute("SELECT * FROM study_canvas_nodes WHERE id = 1").fetchone()
        assert node["user_id"] == DEFAULT_OWNER_ID
        assert node["pos_x"] == 120.0

        # Quadros de canvas
        frame = cursor.execute("SELECT * FROM canvas_frames WHERE id = 1").fetchone()
        assert frame["user_id"] == DEFAULT_OWNER_ID
        assert frame["title"] == "Quadro Epistêmico"

        # Histórico de busca
        search = cursor.execute("SELECT * FROM search_history WHERE id = 1").fetchone()
        assert search["user_id"] == DEFAULT_OWNER_ID
        assert search["query"] == "Kant sintético"

        # Categoria legada (permanece global com user_id IS NULL)
        cat = cursor.execute("SELECT * FROM categories WHERE id = 'categoria_legada_customizada'").fetchone()
        assert cat["user_id"] is None
        assert cat["name"] == "Categoria Legada"

    # 5. Valida reversibilidade (downgrade) e re-aplicação (idempotência)
    command.downgrade(alembic_cfg, "0010_add_search_history")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        book_cols = [col[1] for col in cursor.execute("PRAGMA table_info(books)").fetchall()]
        assert "user_id" not in book_cols

    # Re-aplica upgrade para garantir idempotência
    command.upgrade(alembic_cfg, "head")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        book_cols = [col[1] for col in cursor.execute("PRAGMA table_info(books)").fetchall()]
        assert "user_id" in book_cols
