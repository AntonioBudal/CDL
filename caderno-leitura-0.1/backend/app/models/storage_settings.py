from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now


class StorageSettings(Base):
    """Identidade da pasta de armazenamento (feature 090-A; tabela singleton).

    ``storage_id`` tem de bater com o marcador ``.leitorum-storage.json`` da raiz configurada em
    ``LEITORUM_STORAGE_ROOT``. As colunas da chave de mídia são usadas pela fatia B (cofre); nunca guardam a
    chave, só a impressão digital.
    """

    __tablename__ = "storage_settings"
    __table_args__ = (CheckConstraint("id = 1", name="ck_storage_settings_singleton"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    storage_id: Mapped[str] = mapped_column(String(36), nullable=False)
    media_key_fingerprint: Mapped[str | None] = mapped_column(String(16), nullable=True)
    media_key_epoch: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, server_default=text("CURRENT_TIMESTAMP"), onupdate=utc_now, nullable=False
    )
