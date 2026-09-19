# Modelo de Dados: Capas de Livros

**Feature**: Capas de Livros por Upload e URL  
**Branch**: `004-capas-livros` | **Data**: 2026-09-18  
**Status**: Concluído

Este documento descreve as alterações de schema, entidades, tipos Pydantic e o ciclo de vida do arquivo de capa e sua persistência.

---

## 1. Entidade e Schema do Banco de Dados

### Tabela: `books` (Evolução Incremental)

A tabela `books` é estendida com a nova coluna `cover_image`, que armazena a referência textual (nome do arquivo seguro no servidor) para o arquivo físico de imagem.

```sql
ALTER TABLE books ADD COLUMN cover_image TEXT NULL;
```

#### Definição Declarativa no SQLAlchemy (`app/models/book.py`)

```python
class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),
        CheckConstraint("year IS NULL OR (year >= 1000 AND year <= 2100)", name="year_range"),
        Index("ix_books_deleted_at", "deleted_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    subtitle: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    cover_image: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, onupdate=utc_now,
        server_default=text("CURRENT_TIMESTAMP"), nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime(), default=None, server_default=None, nullable=True
    )

    chapters: Mapped[list[Chapter]] = relationship(
        back_populates="book",
        order_by="(Chapter.position, Chapter.id)",
        passive_deletes="all",
    )
```

---

## 2. Migração Incremental do Alembic

**Arquivo**: `backend/migrations/versions/0004_add_book_cover_image.py`  
**Revision**: `0004_add_book_cover_image`  
**Revises**: `0003_add_trash_soft_delete`

```python
"""Adicionar cover_image em books.

Revision ID: 0004_add_book_cover_image
Revises: 0003_add_trash_soft_delete
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_add_book_cover_image"
down_revision = "0003_add_trash_soft_delete"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("books") as batch_op:
        batch_op.add_column(sa.Column("cover_image", sa.Text(), nullable=True))
    op.execute("PRAGMA optimize")


def downgrade() -> None:
    with op.batch_alter_table("books") as batch_op:
        batch_op.drop_column("cover_image")
```

---

## 3. Schemas Pydantic (Entrada e Saída)

### Atualização em `app/schemas/book.py`

```python
class BookRead(OutputModel):
    id: int
    title: str
    author: str | None = None
    subtitle: str | None = None
    year: int | None = None
    cover_image: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class BookPatch(InputModel):
    title: NonBlankText | None = None
    author: str | None = None
    subtitle: str | None = None
    year: int | None = Field(default=None, ge=1000, le=2100)
    cover_image: str | None = None
    expected_updated_at: datetime | None = Field(default=None, strict=False)
```

### Novos Schemas para Capas em `app/schemas/cover.py`

```python
from pydantic import BaseModel, Field, HttpUrl

from app.schemas.common import InputModel, OutputModel


class CoverUrlRequest(InputModel):
    url: str = Field(..., min_length=10, max_length=2048, description="URL pública direta da imagem")


class CoverResponse(OutputModel):
    book_id: int
    cover_image: str
    cover_url: str
    message: str = "Capa atualizada com sucesso."
```

---

## 4. Tipos Frontend (`frontend/src/types.ts`)

```typescript
export interface Book {
  id: number
  title: string
  author: string | null
  subtitle: string | null
  year: number | null
  cover_image: string | null
  created_at: string | null
  updated_at: string | null
  deleted_at: string | null
}

export interface CoverResponse {
  book_id: number
  cover_image: string
  cover_url: string
  message: string
}
```

---

## 5. Máquina de Estados e Ciclo de Vida da Capa

```
                 ┌─────────────────────────────┐
                 │   Livro sem capa            │
                 │   cover_image = NULL        │
                 └──────────────┬──────────────┘
                                │
               Upload / Download por URL
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │   Livro com capa ativa      │◄──────────┐
                 │   cover_image = "{uuid}.webp"│          │
                 └──────┬───────────────┬──────┘          │
                        │               │                 │
           Mover p/     │               │ Remover Capa /  │
           Lixeira      │               │ Substituir      │
                        │               ▼                 │
                        │        Exclui arquivo antigo    │
                        │        se órfão no disco        │
                        ▼                                 │
                 ┌─────────────────────────────┐          │
                 │   Livro na Lixeira          │          │
                 │   (arquivo físico retido    │──────────┘
                 │    para restauração)        │    Restaurar
                 └──────────────┬──────────────┘    da lixeira
                                │
                      Exclusão Definitiva /
                      Esvaziar Lixeira
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │   Livro Excluído            │
                 │   (arquivo unlinked         │
                 │    do disco se órfão)       │
                 └─────────────────────────────┘
```

### Regras de Integridade
1. **Nome Único**: Todo arquivo salvo recebe um nome aleatório e seguro derivado de UUID v4 (`uuid4().hex + ".webp"`), impedindo sobrescritas acidentais ou colisões.
2. **Isolamento de Diretório**: Todos os arquivos ficam confinados dentro do diretório resolvido por `get_covers_dir()`. Qualquer tentativa de ler ou salvar fora desse diretório gera erro imediato.
3. **Limpeza Concorrente Segura**: Antes de deletar qualquer arquivo do disco físico (`cover_path.unlink()`), o sistema verifica se nenhum outro livro ainda referencia o mesmo `cover_image`.
