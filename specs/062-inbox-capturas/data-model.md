# Data Model: F0.7.13 — Caixa de Entrada de Capturas (Inbox de Conhecimento)

## 1. Esquema Relacional de Banco de Dados

### Tabela `inbox_captures`

| Coluna | Tipo SQLite / SQLAlchemy | Modificadores | Descrição |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Identificador único numérico da captura |
| `user_id` | `VARCHAR(36)` | `NOT NULL, FK users(id) ON DELETE CASCADE` | ID do usuário proprietário da captura |
| `book_id` | `INTEGER` | `NULLABLE, FK books(id) ON DELETE SET NULL` | ID opcional do livro associado à captura |
| `content` | `TEXT` | `NOT NULL` | Texto principal da ideia, trecho ou citação em Markdown |
| `source_hint` | `TEXT` | `NULLABLE` | Descrição de origem/fonte (ex.: "Capítulo 2, p. 45" ou URL/citação) |
| `status` | `VARCHAR(20)` | `NOT NULL, DEFAULT 'inbox'` | Estado da captura: `inbox`, `promoted`, `linked`, `archived` |
| `promoted_study_id` | `INTEGER` | `NULLABLE, FK studies(id) ON DELETE SET NULL` | ID do estudo criado ou associado após promoção/vinculação |
| `created_at` | `DATETIME` | `NOT NULL, DEFAULT CURRENT_TIMESTAMP` | Data e hora de criação |
| `updated_at` | `DATETIME` | `NOT NULL, DEFAULT CURRENT_TIMESTAMP` | Data e hora da última modificação |

### Índices

- `ix_inbox_captures_user_status`: `(user_id, status)` — otimiza `GET /api/inbox/count` e listagens filtradas.
- `ix_inbox_captures_user_created`: `(user_id, created_at DESC)` — otimiza ordenação cronológica reversa da caixa de entrada.
- `ix_inbox_captures_book_id`: `(book_id)` — otimiza busca de capturas por livro.
- `ix_inbox_captures_promoted_study`: `(promoted_study_id)` — otimiza consulta de estudos de origem.

---

## 2. Esquemas Pydantic (Backend)

```python
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

InboxStatus = Literal["inbox", "promoted", "linked", "archived"]

class InboxCaptureBase(BaseModel):
    content: str = Field(..., min_length=1, description="Texto da captura em markdown")
    source_hint: str | None = Field(default=None, max_length=500, description="Origem da citação ou trecho")
    book_id: int | None = Field(default=None, description="ID do livro associado opcional")

class InboxCaptureCreate(InboxCaptureBase):
    pass

class InboxCapturePatch(BaseModel):
    content: str | None = Field(default=None, min_length=1)
    source_hint: str | None = Field(default=None, max_length=500)
    book_id: int | None = None
    status: InboxStatus | None = None

class InboxCaptureRead(InboxCaptureBase):
    id: int
    user_id: str
    status: InboxStatus
    promoted_study_id: int | None = None
    created_at: datetime
    updated_at: datetime
    book_title: str | None = None
    promoted_study_title: str | None = None

    model_config = ConfigDict(from_attributes=True)

class InboxCountResponse(BaseModel):
    count: int = Field(..., ge=0, description="Total de capturas com status 'inbox'")

class InboxPromoteRequest(BaseModel):
    study_id: int = Field(..., description="ID do estudo recém-criado a partir da captura")

class InboxLinkRequest(BaseModel):
    target_study_id: int = Field(..., description="ID do estudo que receberá o trecho")
    target_section: Literal["summary", "explanation", "concepts", "references", "notes"] = Field(
        default="references", description="Seção do estudo onde a nota será anexada"
    )
```

---

## 3. Tipos TypeScript (Frontend)

```typescript
export type InboxStatus = 'inbox' | 'promoted' | 'linked' | 'archived'

export interface InboxCapture {
  id: number
  user_id: string
  book_id: number | null
  book_title?: string | null
  content: string
  source_hint: string | null
  status: InboxStatus
  promoted_study_id: number | null
  promoted_study_title?: string | null
  created_at: string
  updated_at: string
}

export interface InboxCaptureCreatePayload {
  content: string
  source_hint?: string | null
  book_id?: number | null
}

export interface InboxCapturePatchPayload {
  content?: string
  source_hint?: string | null
  book_id?: number | null
  status?: InboxStatus
}

export interface InboxCountResponse {
  count: number
}

export interface InboxPromotePayload {
  study_id: number
}

export interface InboxLinkPayload {
  target_study_id: number
  target_section?: 'summary' | 'explanation' | 'concepts' | 'references' | 'notes'
}
```

---

## 4. Transições de Estado

```text
       [ Nova Captura ]
              │
              ▼
           ( inbox ) ──[ Descartar / Arquivar ]──> ( archived )
              │
      ┌───────┴───────────────────────┐
      │                               │
[ Promover para Estudo ]    [ Vincular a Estudo ]
      │                               │
      ▼                               ▼
 ( promoted )                     ( linked )
```
