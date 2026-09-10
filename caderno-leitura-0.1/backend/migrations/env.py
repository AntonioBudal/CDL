from logging.config import fileConfig
from pathlib import Path

from alembic import context

import app.models  # Registra Book, Chapter e Study no metadata.
from app.core.config import get_database_path
from app.db.base import Base
from app.db.session import create_sqlite_engine, sqlite_url
from app.db.types import UTCDateTime

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def render_item(type_, obj, autogen_context):
    if type_ == "type" and isinstance(obj, UTCDateTime):
        # O comportamento UTC pertence ao ORM; a coluna SQLite e DATETIME.
        return "sa.DateTime()"
    return False


def database_path() -> Path:
    # Os testes passam um arquivo temporario sem tocar no acervo real.
    override = config.attributes.get("database_path")
    return Path(override) if override is not None else get_database_path()


def run_migrations_offline() -> None:
    context.configure(
        url=sqlite_url(database_path()),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        render_item=render_item,
        transactional_ddl=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_sqlite_engine(database_path())
    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True,
                render_as_batch=True,
                render_item=render_item,
                transactional_ddl=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
