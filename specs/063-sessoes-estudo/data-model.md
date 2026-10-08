# Data Model: F0.7.14 — Sessões Estruturadas de Estudo e Auditoria de Aprendizado

**Feature**: F0.7.14 — Sessões Estruturadas de Estudo  
**Branch**: `063-sessoes-estudo`  
**Date**: 2026-10-10  

---

## 1. Esquema Relacional (SQLite)

### Tabela `study_sessions`
Registra a sessão de estudo executada por um leitor.

| Coluna | Tipo SQLite | Restrições | Descrição |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único da sessão |
| `user_id` | VARCHAR(36) | NOT NULL, REFERENCES users(id) | Dono da sessão (isolamento multiusuário) |
| `book_id` | INTEGER | NULL, REFERENCES books(id) | Obra vinculada (se sessão filtrada por livro) |
| `scope_type` | VARCHAR(30) | NOT NULL DEFAULT 'quick' | Escopo: `'quick'`, `'book'`, `'all'` |
| `status` | VARCHAR(20) | NOT NULL DEFAULT 'in_progress' | Status: `'in_progress'`, `'completed'`, `'interrupted'` |
| `started_at` | DATETIME | NOT NULL | Data e hora de início em UTC |
| `completed_at` | DATETIME | NULL | Data e hora de encerramento em UTC |
| `total_items` | INTEGER | NOT NULL DEFAULT 0 | Total de itens previstos para a sessão |
| `completed_items` | INTEGER | NOT NULL DEFAULT 0 | Total de itens respondidos até o momento |
| `easy_count` | INTEGER | NOT NULL DEFAULT 0 | Contagem de itens avaliados como Fácil |
| `medium_count` | INTEGER | NOT NULL DEFAULT 0 | Contagem de itens avaliados como Médio |
| `hard_count` | INTEGER | NOT NULL DEFAULT 0 | Contagem de itens avaliados como Difícil |
| `duration_seconds` | INTEGER | NOT NULL DEFAULT 0 | Duração total líquida da sessão em segundos |
| `created_at` | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | Data de criação do registro |
| `updated_at` | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | Data de última atualização do registro |

**Índices**:
- `ix_study_sessions_user_id` em (`user_id`)
- `ix_study_sessions_book_id` em (`book_id`)
- `ix_study_sessions_status` em (`status`)
- `ix_study_sessions_started_at` em (`started_at` DESC)

---

### Tabela `study_session_items`
Registra a avaliação individual de cada cartão respondido dentro da sessão.

| Coluna | Tipo SQLite | Restrições | Descrição |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único do item |
| `session_id` | INTEGER | NOT NULL, REFERENCES study_sessions(id) ON DELETE CASCADE | Sessão proprietária |
| `highlight_id` | INTEGER | NOT NULL, REFERENCES study_highlights(id) | Destaque/cartão revisado |
| `rating` | VARCHAR(20) | NOT NULL | Avaliação: `'easy'`, `'medium'`, `'hard'` |
| `time_spent_seconds`| INTEGER | NOT NULL DEFAULT 0 | Segundos dedicados a este cartão |
| `answered_at` | DATETIME | NOT NULL | Timestamp da resposta |

**Índices**:
- `ix_study_session_items_session_id` em (`session_id`)
- `ix_study_session_items_highlight_id` em (`highlight_id`)

---

## 2. Schemas Pydantic (Backend)

```python
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

SessionScopeType = Literal["quick", "book", "all"]
SessionStatus = Literal["in_progress", "completed", "interrupted"]
ItemRating = Literal["easy", "medium", "hard"]

class StudySessionStartRequest(BaseModel):
    scope_type: SessionScopeType = "quick"
    book_id: Optional[int] = None
    limit: Optional[int] = Field(default=10, ge=1, le=100)

class StudySessionItemAnswerRequest(BaseModel):
    highlight_id: int
    rating: ItemRating
    time_spent_seconds: int = 0

class StudySessionItemResponse(BaseModel):
    id: int
    session_id: int
    highlight_id: int
    rating: ItemRating
    time_spent_seconds: int
    answered_at: datetime

    class Config:
        from_attributes = True

class StudySessionResponse(BaseModel):
    id: int
    user_id: str
    book_id: Optional[int] = None
    book_title: Optional[str] = None
    scope_type: SessionScopeType
    status: SessionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_items: int
    completed_items: int
    easy_count: int
    medium_count: int
    hard_count: int
    duration_seconds: int

    class Config:
        from_attributes = True

class StudySessionDetailResponse(StudySessionResponse):
    items: list[StudySessionItemResponse] = []
    # Lista de cartões de highlights a responder (quando in_progress)
    pending_cards: list[dict] = []

class StudySessionSummaryResponse(BaseModel):
    session: StudySessionResponse
    accuracy_rate: float
    next_reviews_summary: dict[str, int]
```

---

## 3. Tipos TypeScript (Frontend)

```typescript
export type SessionScopeType = 'quick' | 'book' | 'all'
export type SessionStatus = 'in_progress' | 'completed' | 'interrupted'
export type SessionRating = 'easy' | 'medium' | 'hard'

export interface StudySessionItem {
  id: number
  session_id: number
  highlight_id: number
  rating: SessionRating
  time_spent_seconds: number
  answered_at: string
}

export interface StudySession {
  id: number
  user_id: string
  book_id?: number | null
  book_title?: string | null
  scope_type: SessionScopeType
  status: SessionStatus
  started_at: string
  completed_at?: string | null
  total_items: number
  completed_items: number
  easy_count: number
  medium_count: number
  hard_count: number
  duration_seconds: number
}

export interface StudySessionDetail extends StudySession {
  items: StudySessionItem[]
  pending_cards: HighlightCard[]
}

export interface StudySessionSummary {
  session: StudySession
  accuracy_rate: number
  next_reviews_summary: Record<string, number>
}
```
