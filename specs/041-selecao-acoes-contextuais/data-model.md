# Data Model: F0.6.2 — Seleção e Ações Contextuais

**Feature**: F0.6.2 — Seleção e Ações Contextuais  
**Directory**: `specs/041-selecao-acoes-contextuais/`  
**Date**: 2026-09-27  

---

## 1. Entidade Relacional SQLite (SQLAlchemy 2.0)

### Tabela: `study_highlights`

```python
class StudyHighlight(Base):
    __tablename__ = "study_highlights"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('highlight', 'note', 'quote', 'hidden', 'question')",
            name="chk_highlight_kind",
        ),
        CheckConstraint(
            "section IN ('summary', 'explanation', 'concepts', 'references', 'source_response')",
            name="chk_highlight_section",
        ),
        CheckConstraint("length(trim(selected_text)) > 0", name="chk_highlight_text_not_blank"),
        CheckConstraint("start_offset >= 0", name="chk_highlight_start_offset_non_negative"),
        CheckConstraint("end_offset >= start_offset", name="chk_highlight_offsets_valid"),
        Index("ix_study_highlights_study_id", "study_id"),
        Index("ix_study_highlights_user_id", "user_id"),
        Index("ix_study_highlights_study_section", "study_id", "section"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        ForeignKey("studies.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        default=DEFAULT_OWNER_ID,
        server_default=text(f"'{DEFAULT_OWNER_ID}'"),
        nullable=False,
    )
    section: Mapped[str] = mapped_column(String(30), nullable=False)
    start_offset: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    end_offset: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    selected_text: Mapped[str] = mapped_column(Text, nullable=False)
    prefix: Mapped[str] = mapped_column(String(150), default="", server_default=text("''"), nullable=False)
    suffix: Mapped[str] = mapped_column(String(150), default="", server_default=text("''"), nullable=False)
    color: Mapped[str] = mapped_column(String(30), default="yellow", server_default=text("'yellow'"), nullable=False)
    kind: Mapped[str] = mapped_column(String(30), default="highlight", server_default=text("'highlight'"), nullable=False)
    note: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, onupdate=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    # Relacionamentos
    study: Mapped["Study"] = relationship("Study", backref="highlights")
    user: Mapped["User"] = relationship("User")
```

---

## 2. Schemas Pydantic v2 (Backend)

```python
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

HighlightKind = Literal["highlight", "note", "quote", "hidden", "question"]
HighlightColor = Literal["yellow", "green", "blue", "pink", "purple"]
SectionName = Literal["summary", "explanation", "concepts", "references", "source_response"]

class StudyHighlightBase(BaseModel):
    section: SectionName
    start_offset: int = Field(default=0, ge=0)
    end_offset: int = Field(default=0, ge=0)
    selected_text: str = Field(min_length=1, max_length=50000)
    prefix: str = Field(default="", max_length=150)
    suffix: str = Field(default="", max_length=150)
    color: HighlightColor = "yellow"
    kind: HighlightKind = "highlight"
    note: str = Field(default="", max_length=10000)

class StudyHighlightCreate(StudyHighlightBase):
    pass

class StudyHighlightUpdate(BaseModel):
    color: HighlightColor | None = None
    kind: HighlightKind | None = None
    note: str | None = Field(default=None, max_length=10000)

class StudyHighlightRead(StudyHighlightBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    study_id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
```

---

## 3. Tipos TypeScript (Frontend)

```typescript
export type HighlightColor = 'yellow' | 'green' | 'blue' | 'pink' | 'purple'
export type HighlightKind = 'highlight' | 'note' | 'quote' | 'hidden' | 'question'
export type StudySectionKey = 'summary' | 'explanation' | 'concepts' | 'references' | 'source_response'

export interface StudyHighlight {
  id: number
  study_id: number
  user_id: string
  section: StudySectionKey
  start_offset: number
  end_offset: number
  selected_text: string
  prefix: string
  suffix: string
  color: HighlightColor
  kind: HighlightKind
  note: string
  created_at: string
  updated_at: string
}

export interface StudyHighlightCreatePayload {
  section: StudySectionKey
  start_offset: number
  end_offset: number
  selected_text: string
  prefix?: string
  suffix?: string
  color?: HighlightColor
  kind?: HighlightKind
  note?: string
}

export interface StudyHighlightUpdatePayload {
  color?: HighlightColor
  kind?: HighlightKind
  note?: string
}

export interface TextSelectionContext {
  section: StudySectionKey
  selected_text: string
  prefix: string
  suffix: string
  start_offset: number
  end_offset: number
  boundingRect: DOMRect
}
```

---

## 4. Ciclo de Vida e Transições de Estado do Trecho

```
[Seleção de Texto no DOM]
         │
         ▼
[Barra Flutuante Aberta]
         │
         ├───▶ Ação: Destacar ───────▶ POST /highlights (kind: 'highlight', color: '...')
         ├───▶ Ação: Anotar ─────────▶ POST /highlights (kind: 'note', note: '...')
         ├───▶ Ação: Copiar Citação ─▶ Formata texto + clipboard (sem salvar destaque)
         ├───▶ Ação: Ocultar ────────▶ POST /highlights (kind: 'hidden')
         └───▶ Ação: Pergunta ───────▶ POST /highlights (kind: 'question', note: 'enunciado')

[Destaque Renderizado no Texto]
         │
         ▼ (Clique sobre o trecho marcado)
[Popover de Gestão do Destaque]
         ├───▶ Alterar Cor ──────────▶ PATCH /highlights/{id} (color: '...')
         ├───▶ Editar Nota / Pergunta▶ PATCH /highlights/{id} (note: '...')
         ├───▶ Revelar / Ocultar ────▶ Alternância local instantânea no DOM
         └───▶ Remover Destaque ─────▶ DELETE /highlights/{id} (Desfaz o elemento <mark>)
```
