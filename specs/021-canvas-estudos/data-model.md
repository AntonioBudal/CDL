# Data Model: F03 — Canvas de Estudos

**Feature Branch**: `021-canvas-estudos`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Schema Relacional (SQLite)

### Nova Tabela: `study_canvas_nodes`

A persistência espacial é isolada na tabela `study_canvas_nodes` através da migração Alembic `0007_add_study_canvas_nodes.py`:

```sql
CREATE TABLE study_canvas_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    study_id INTEGER NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    pos_x REAL NOT NULL DEFAULT 0.0,
    pos_y REAL NOT NULL DEFAULT 0.0,
    width REAL NULL,
    height REAL NULL,
    z_index INTEGER NOT NULL DEFAULT 0,
    color_tag TEXT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_canvas_node_study_book UNIQUE (study_id, book_id)
);

CREATE INDEX ix_canvas_nodes_book_study ON study_canvas_nodes (book_id, study_id);
```

### Detalhamento dos Campos

| Campo | Tipo | Nulidade | Valor Padrão | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Não (`PK`) | Autoincrement | Identificador único do registro de layout espacial. |
| `study_id` | `INTEGER` | Não (`FK`) | — | ID do estudo projetado no canvas (`studies.id`). Deleção em cascata. |
| `book_id` | `INTEGER` | Não (`FK`) | — | ID da obra à qual o canvas pertence (`books.id`). Deleção em cascata. |
| `pos_x` | `REAL` | Não | `0.0` | Posição horizontal no espaço contínuo do mundo 2D (em pixels lógicos). |
| `pos_y` | `REAL` | Não | `0.0` | Posição vertical no espaço contínuo do mundo 2D (em pixels lógicos). |
| `width` | `REAL` | Sim | `NULL` | Largura personalizada do card em pixels (se omitido, usa padrão de 280px). |
| `height` | `REAL` | Sim | `NULL` | Altura personalizada em pixels (se omitido, ajusta ao conteúdo). |
| `z_index` | `INTEGER` | Não | `0` | Ordem de empilhamento visual (maior valor sobrepõe visualmente). |
| `color_tag` | `TEXT` | Sim | `NULL` | Identificador de matiz visual para diferenciação temática de cards. |
| `updated_at` | `DATETIME` | Não | `now()` | Carimbo de data/hora para controle de concorrência e sincronização. |

---

## 2. Modelo SQLAlchemy (Backend)

```python
# Em app/models/study_canvas_node.py
from datetime import datetime, timezone
from sqlalchemy import Integer, Float, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class StudyCanvasNode(Base):
    __tablename__ = "study_canvas_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )
    pos_x: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    pos_y: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    width: Mapped[float | None] = mapped_column(Float, nullable=True)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)
    z_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    color_tag: Mapped[str | None] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    study = relationship("Study", backref="canvas_node", uselist=False)
    book = relationship("Book", backref="canvas_nodes")

    __table_args__ = (
        UniqueConstraint("study_id", "book_id", name="uq_canvas_node_study_book"),
        Index("ix_canvas_nodes_book_study", "book_id", "study_id"),
    )
```

---

## 3. Schemas Pydantic (Backend)

```python
# Em app/schemas/study_canvas_node.py
from datetime import datetime
from pydantic import BaseModel, Field

class CanvasNodeItem(BaseModel):
    study_id: int
    pos_x: float
    pos_y: float
    width: float | None = None
    height: float | None = None
    z_index: int = 0
    color_tag: str | None = None

class CanvasNodeRead(CanvasNodeItem):
    id: int
    book_id: int
    updated_at: datetime

    model_config = {"from_attributes": True}

class CanvasBatchUpdateRequest(BaseModel):
    nodes: list[CanvasNodeItem] = Field(..., min_length=1, description="Lista de coordenadas a sincronizar")

class BookCanvasResponse(BaseModel):
    book_id: int
    nodes: list[CanvasNodeRead]
```

---

## 4. Tipos e Modelos no Frontend (TypeScript)

```typescript
// Em frontend/src/types.ts

export interface StudyCanvasNode {
  id: number
  study_id: number
  book_id: number
  pos_x: number
  pos_y: number
  width: number | null
  height: number | null
  z_index: number
  color_tag: string | null
  updated_at: string
}

export interface CanvasViewportState {
  pan_x: number
  pan_y: number
  zoom_level: number
}

export interface CanvasPositionedCard {
  study_id: number
  x: number
  y: number
  width?: number
  height?: number
  z_index: number
  color_tag?: string | null
  is_persisted: boolean
}

export interface CanvasBoundingBox {
  min_x: number
  min_y: number
  max_x: number
  max_y: number
  width: number
  height: number
}

export interface CanvasSelectionState {
  selected_ids: Set<number>
  marquee_active: boolean
  marquee_start_x: number
  marquee_start_y: number
  marquee_current_x: number
  marquee_current_y: number
}
```

---

## 5. Regras de Integridade e Validação

### Regra V-01: Isolamento de Paternidade e Capítulos
- A criação ou modificação de registros em `study_canvas_nodes` não executa nenhuma mutação nas colunas `parent_study_id`, `position` ou `chapter_id` da tabela `studies`.
- A separação entre layout espacial e estrutura de dados canônica é absoluta.

### Regra V-02: Coordenadas Numéricas Finitas
- Os campos `pos_x`, `pos_y`, `width` e `height` devem ser números reais finitos (rejeitando `NaN`, `+Infinity` e `-Infinity`).
- Se recebido valor inválido, o backend rejeita a requisição com `HTTP 422 Unprocessable Entity`.

### Regra V-03: Consistência de Pertencimento à Obra
- O `study_id` informado deve pertencer a um capítulo vinculado ao `book_id` da rota.
- Tentativa de associar um estudo a um livro diferente no canvas resulta em `HTTP 400 Bad Request` ("Estudo não pertence a este livro").

### Regra V-04: Transacionalidade no Batch Update
- A operação `PUT /api/books/{id}/canvas` é executada dentro de uma única transação atômica do SQLite. Se a atualização de qualquer nó falhar, toda a operação sofre rollback.
