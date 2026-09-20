# Data Model: F08 — Busca Global Contextual

**Feature Branch**: `025-busca-global-contextual`  
**Date**: 2026-09-19  
**Specification**: [spec.md](./spec.md)  

---

## 1. Entidades de Banco de Dados

### Tabela `search_history`

Persiste os termos pesquisados recentemente pelo leitor, centralizando o histórico no SQLite e permitindo sincronização entre o PC e dispositivos móveis na rede local, além de preparar o schema para sincronismo em nuvem futura.

```sql
CREATE TABLE search_history (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    query VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE UNIQUE INDEX ix_search_history_query ON search_history (query);
CREATE INDEX ix_search_history_updated_at ON search_history (updated_at DESC);
```

#### Regras de Negócio do Modelo
1. **Unicidade de Termos (`query`)**: Se o leitor pesquisar novamente um termo já presente na tabela, o registro tem seu `updated_at` atualizado para o instante corrente, movendo o termo para o topo da lista de recentes sem duplicar linhas.
2. **Política de Retenção Ativa**: O sistema mantém no máximo os 10 termos mais recentes. Ao inserir um novo termo, registros que excederem o limite de 10 são expurgados automaticamente.
3. **Limpeza e Exclusão Atômica**: O leitor pode remover um termo específico (`DELETE /api/search/history/{id}`) ou esvaziar todo o histórico (`DELETE /api/search/history`).

---

## 2. Entidades em Memória e DTOs (Data Transfer Objects)

### Schemas Pydantic v2 (Backend)

```python
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class SearchMatchItem(BaseModel):
    """Representação de um resultado de estudo localizado."""
    model_config = ConfigDict(from_attributes=True)

    study_id: int
    study_title: str
    book_id: int
    book_title: str
    chapter_id: int | None = None
    chapter_name: str | None = None
    reading_status: str = "rascunho"
    matched_field: str  # ex: "Título", "Resumo", "Conceitos", "Notas", "Explicação"
    snippet: str  # Trecho de ~140 caracteres sanitizado com <mark class="search-highlight">
    updated_at: datetime


class SearchResponse(BaseModel):
    """Resposta consolidada da consulta de busca transversal."""
    query: str
    mode: Literal["and", "or"] = "and"
    total: int
    results: list[SearchMatchItem]
    suggest_or: bool = False  # True quando busca AND não retorna resultados, mas modo OR teria correspondências


class SearchHistoryItem(BaseModel):
    """Item do histórico de buscas recentes."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    query: str
    created_at: datetime
    updated_at: datetime


class SearchHistoryResponse(BaseModel):
    """Listagem ordenada do histórico recente."""
    items: list[SearchHistoryItem]
```

### Tipagens TypeScript (Frontend)

```typescript
export interface SearchMatchItem {
  study_id: number;
  study_title: string;
  book_id: number;
  book_title: string;
  chapter_id: number | null;
  chapter_name: string | null;
  reading_status: string;
  matched_field: string;
  snippet: string;
  updated_at: string;
}

export interface SearchResponse {
  query: string;
  mode: 'and' | 'or';
  total: number;
  results: SearchMatchItem[];
  suggest_or: boolean;
}

export interface SearchHistoryItem {
  id: number;
  query: string;
  created_at: string;
  updated_at: string;
}

export interface SearchHistoryResponse {
  items: SearchHistoryItem[];
}
```

---

## 3. Regras de Isolamento e Soft Delete

1. **Filtro Estrito de Exclusão**:
   - `studies.deleted_at IS NULL`
   - `books.deleted_at IS NULL`
   - Se o livro estiver na lixeira, nenhum dos seus estudos ou capítulos pode aparecer nos resultados da busca, mesmo que o termo coincida perfeitamente.
2. **Tratamento de Strings e Normalização**:
   - Normalização prévia no SQLite via UDF `unaccent` registrada na conexão.
   - Higienização estrita contra XSS: caracteres `<`, `>`, `&`, `"`, `'` no snippet são codificados antes da injeção segura da tag `<mark class="search-highlight">`.
