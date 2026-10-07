# Data Model: F0.7.12 — Backlinks e Menções entre Estudos

## Entidades e Esquemas de Dados

### 1. Modelo Relacional: `study_mentions`

Tabela dedicada para persistir as referências textuais extraídas entre estudos.

```sql
CREATE TABLE study_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_study_id INTEGER NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    target_study_id INTEGER NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    section VARCHAR(30) NOT NULL,
    mention_text TEXT NOT NULL,
    context_snippet TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_study_mentions_target_user ON study_mentions (target_study_id, user_id);
CREATE INDEX ix_study_mentions_source_user ON study_mentions (source_study_id, user_id);
```

#### Atributos da Entidade `StudyMention`:

| Campo | Tipo | Nulo? | Descrição |
|---|---|---|---|
| `id` | INTEGER | Não | Chave primária autoincrementada |
| `user_id` | VARCHAR(36) | Não | ID do usuário proprietário (isolamento multiusuário) |
| `source_study_id` | INTEGER | Não | Estudo de origem onde a menção foi escrita (FK studies) |
| `target_study_id` | INTEGER | Não | Estudo de destino referenciado pela menção (FK studies) |
| `section` | VARCHAR(30) | Não | Seção do estudo (`summary`, `explanation`, `concepts`, `references`) |
| `mention_text` | TEXT | Não | Texto literal contido nos colchetes (ex.: "Crítica da Razão Pura") |
| `context_snippet` | TEXT | Não | Trecho contextual extraído ao redor da menção (até 180 chars) |
| `created_at` | UTCDateTime | Não | Timestamp da criação da menção |

---

### 2. Esquemas Pydantic (`backend/app/schemas/study_mention.py`)

#### `BacklinkItemRead`
Representa um estudo que menciona o estudo atual, retornado no endpoint de backlinks:

```python
class BacklinkItemRead(OutputModel):
    id: RecordId
    source_study_id: RecordId
    source_study_title: str
    book_id: RecordId
    book_title: str
    chapter_id: RecordId
    chapter_name: str
    section: str
    mention_text: str
    context_snippet: str
    created_at: datetime
```

#### `BacklinksResponse`
Envelope de resposta para a lista de backlinks:

```python
class BacklinksResponse(OutputModel):
    items: list[BacklinkItemRead]
    total: int
```

#### `StudyCandidateOption`
Opção retornada para alimentação do menu de autocomplete no editor:

```python
class StudyCandidateOption(OutputModel):
    id: RecordId
    title: str
    book_id: RecordId
    book_title: str
    chapter_id: RecordId
    chapter_name: str
```

---

### 3. Tipos TypeScript (`frontend/src/types.ts`)

```typescript
export interface BacklinkItem {
  id: number
  source_study_id: number
  source_study_title: string
  book_id: number
  book_title: string
  chapter_id: number
  chapter_name: string
  section: string
  mention_text: string
  context_snippet: string
  created_at: string
}

export interface BacklinksResponse {
  items: BacklinkItem[]
  total: number
}

export interface StudyCandidateOption {
  id: number
  title: string
  book_id: number
  book_title: string
  chapter_id: number
  chapter_name: string
}
```
