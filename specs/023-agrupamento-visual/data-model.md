# Data Model: F05 — Agrupamento Visual

**Feature Branch**: `023-agrupamento-visual`  
**Date**: 2026-09-19  
**Specification**: [spec.md](./spec.md)  
**Research**: [research.md](./research.md)  

---

## 1. Esquema Relacional e Migrações (SQLite / SQLAlchemy)

### A. Evolução da Tabela `studies` (Migração Alembic `0009_add_reading_status_and_canvas_frames.py`)

Adição da coluna `reading_status` para persistência do estado editorial de maturação de cada estudo:

```sql
ALTER TABLE studies ADD COLUMN reading_status VARCHAR(20) NOT NULL DEFAULT 'rascunho';

CREATE INDEX ix_studies_reading_status ON studies (reading_status);

-- Constraint canônica de domínio
-- CHECK (reading_status IN ('rascunho', 'em_estudo', 'revisado', 'concluido'))
```

#### Mapeamento SQLAlchemy (`app/models/study.py`):
```python
reading_status: Mapped[str] = mapped_column(
    String(20),
    default="rascunho",
    server_default=text("'rascunho'"),
    nullable=False,
)
```

---

### B. Criação da Tabela `canvas_frames`

Persistência das molduras manuais delimitadoras associadas ao Canvas 2D de um determinado livro:

```sql
CREATE TABLE canvas_frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    color VARCHAR(32) NOT NULL DEFAULT 'neutral',
    pos_x FLOAT NOT NULL DEFAULT 0.0,
    pos_y FLOAT NOT NULL DEFAULT 0.0,
    width FLOAT NOT NULL DEFAULT 400.0,
    height FLOAT NOT NULL DEFAULT 300.0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_canvas_frames_dimensions CHECK (width >= 100.0 AND height >= 80.0)
);

CREATE INDEX ix_canvas_frames_book_id ON canvas_frames (book_id);
```

#### Mapeamento SQLAlchemy (`app/models/canvas_frame.py`):
```python
class CanvasFrame(Base):
    __tablename__ = "canvas_frames"
    __table_args__ = (
        CheckConstraint("width >= 100.0 AND height >= 80.0", name="ck_canvas_frames_dimensions"),
        Index("ix_canvas_frames_book_id", "book_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(32), default="neutral", server_default=text("'neutral'"), nullable=False)
    pos_x: Mapped[float] = mapped_column(Float, default=0.0, server_default=text("0.0"), nullable=False)
    pos_y: Mapped[float] = mapped_column(Float, default=0.0, server_default=text("0.0"), nullable=False)
    width: Mapped[float] = mapped_column(Float, default=400.0, server_default=text("400.0"), nullable=False)
    height: Mapped[float] = mapped_column(Float, default=300.0, server_default=text("300.0"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=utc_now,
        onupdate=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    book: Mapped[Book] = relationship("Book", backref=backref("canvas_frames", cascade="all, delete-orphan", passive_deletes=True), passive_deletes=True)
```

---

## 2. Schemas de Validação Pydantic v2 (`app/schemas/study_grouping.py`)

```python
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class ReadingStatus(str, Enum):
    RASCUNHO = "rascunho"
    EM_ESTUDO = "em_estudo"
    REVISADO = "revisado"
    CONCLUIDO = "concluido"

class StudyStatusUpdate(BaseModel):
    reading_status: ReadingStatus
    expected_updated_at: datetime | None = None

class StudyStatusResponse(BaseModel):
    id: int
    reading_status: ReadingStatus
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CanvasFrameCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    color: str = Field(default="neutral", max_length=32)
    pos_x: float = 0.0
    pos_y: float = 0.0
    width: float = Field(default=400.0, ge=100.0)
    height: float = Field(default=300.0, ge=80.0)

class CanvasFrameUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, max_length=32)
    pos_x: float | None = None
    pos_y: float | None = None
    width: float | None = Field(default=None, ge=100.0)
    height: float | None = Field(default=None, ge=80.0)

class CanvasFrameItem(BaseModel):
    id: int
    book_id: int
    title: str
    color: str
    pos_x: float
    pos_y: float
    width: float
    height: float
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

---

## 3. Tipagem TypeScript Frontend (`frontend/src/types.ts`)

```typescript
export type ReadingStatus = 'rascunho' | 'em_estudo' | 'revisado' | 'concluido'

export type StudyGroupByCriteria = 'chapter' | 'status' | 'category' | 'date' | 'manual'

export interface CanvasFrameItem {
  id: number
  book_id: number
  title: string
  color: string
  pos_x: number
  pos_y: number
  width: number
  height: number
  created_at: string
  updated_at: string
}

export interface CreateCanvasFramePayload {
  title: string
  color?: string
  pos_x: number
  pos_y: number
  width?: number
  height?: number
}

export interface UpdateCanvasFramePayload {
  title?: string
  color?: string
  pos_x?: number
  pos_y?: number
  width?: number
  height?: number
}

export interface StudyGroup<T = any> {
  id: string
  title: string
  badgeLabel?: string
  badgeClass?: string
  count: number
  isCollapsed: boolean
  studies: T[]
}
```
