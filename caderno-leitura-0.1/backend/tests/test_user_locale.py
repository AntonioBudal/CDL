"""F0.12.09 (spec 122): idioma da interface salvo nas preferências. Banco descartável em tmp_path."""
from __future__ import annotations

import sqlite3
from contextlib import closing

from alembic import command
from alembic.config import Config

from app.core.config import BACKEND_DIR
from tests.test_sharing_and_permissions import sharing_harness  # noqa: F401  (fixture com vários usuários)


def test_locale_defaults_saves_and_is_per_user(sharing_harness):  # noqa: F811
    alice, bob = sharing_harness.client_alice, sharing_harness.client_bob
    assert alice.get("/api/preferences").json()["locale"] == "pt-BR"
    saved = alice.put("/api/preferences", json={"locale": "en"})
    assert saved.status_code == 200, saved.text
    assert saved.json()["locale"] == "en"
    assert alice.get("/api/preferences").json()["locale"] == "en"
    assert bob.get("/api/preferences").json()["locale"] == "pt-BR", "cada leitor tem o seu"
    assert alice.put("/api/preferences", json={"locale": "fr"}).status_code == 422
    # Outra preferência não mexe no idioma.
    assert alice.put("/api/preferences", json={"theme_mode": "light"}).json()["locale"] == "en"


def test_migration_0043_up_and_down(tmp_path):
    db = tmp_path / "migracao" / "caderno.db"
    db.parent.mkdir()
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["database_path"] = db
    command.upgrade(cfg, "head")
    with closing(sqlite3.connect(db)) as conn:
        columns = {row[1]: row for row in conn.execute("PRAGMA table_info(user_preferences)")}
    assert "locale" in columns and columns["locale"][4] == "'pt-BR'"
    command.downgrade(cfg, "0042_reading_circles")
    with closing(sqlite3.connect(db)) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(user_preferences)")}
    assert "locale" not in columns
