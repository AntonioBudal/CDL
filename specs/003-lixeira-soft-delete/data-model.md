# Data Model: Lixeira e Restauração de Itens (Soft Delete)

**Feature**: `003-lixeira-soft-delete`  
**Date**: 2026-09-18  
**Status**: Draft  

---

## Entidades e Schema

### 1. Livro (`Book` / tabela `books`)

Representa a obra no acervo. Ganha a coluna `deleted_at` para controle de descarte lógico.

| Campo | Tipo | Nulo | Padrão | Descrição |
|---|---|---|---|---|
| `id` | `INTEGER` | Não | Autoincremento | Chave primária |
| `title` | `TEXT` | Não | — | Título da obra (não vazio) |
| `author` | `TEXT` | Sim | `NULL` | Nome do autor |
| `subtitle` | `TEXT` | Não | `''` | Subtítulo da obra |
| `year` | `INTEGER` | Sim | `NULL` | Ano de publicação (1000–2100) |
| `created_at` | `DATETIME (UTC)` | Não | `CURRENT_TIMESTAMP` | Data/hora de inclusão |
| `updated_at` | `DATETIME (UTC)` | Não | `CURRENT_TIMESTAMP` | Data/hora da última alteração |
| `deleted_at` | `DATETIME (UTC)` | Sim | `NULL` | Data/hora do descarte para lixeira (UTC). Se `NULL`, livro está ativo. |

**Índices e Constraints**:
- `CheckConstraint("length(trim(title)) > 0", name="title_not_blank")`
- `CheckConstraint("year IS NULL OR (year >= 1000 AND year <= 2100)", name="year_range")`
- `Index("ix_books_deleted_at", "deleted_at")` — Otimiza consultas do acervo ativo (`WHERE deleted_at IS NULL`) e da lixeira (`WHERE deleted_at IS NOT NULL`).

---

### 2. Capítulo (`Chapter` / tabela `chapters`)

Representa o sumário/estrutura de capítulos de um livro. Não possui soft delete independente; segue o ciclo do livro pai.

| Campo | Tipo | Nulo | Padrão | Descrição |
|---|---|---|---|---|
| `id` | `INTEGER` | Não | Autoincremento | Chave primária |
| `book_id` | `INTEGER` | Não | — | FK para `books.id` (`ondelete="RESTRICT"`) |
| `name` | `TEXT` | Não | — | Nome do capítulo |
| `position` | `INTEGER` | Não | `0` | Posição ordinal no sumário (>= 0) |
| `created_at` | `DATETIME (UTC)` | Não | `CURRENT_TIMESTAMP` | Data/hora de criação |
| `updated_at` | `DATETIME (UTC)` | Não | `CURRENT_TIMESTAMP` | Data/hora da última alteração |

**Relacionamento**:
- `book = relationship("Book", back_populates="chapters")`
- `studies = relationship("Study", back_populates="chapter", order_by="Study.id", passive_deletes="all")`

---

### 3. Estudo (`Study` / tabela `studies`)

Representa uma anotação de leitura e análise textual. Ganha a coluna `deleted_at` para descarte individual.

| Campo | Tipo | Nulo | Padrão | Descrição |
|---|---|---|---|---|
| `id` | `INTEGER` | Não | Autoincremento | Chave primária |
| `chapter_id` | `INTEGER` | Não | — | FK para `chapters.id` (`ondelete="RESTRICT"`) |
| `title` | `TEXT` | Não | — | Título do estudo |
| `location` | `TEXT` | Não | `''` | Localização no livro (página, porcentagem, etc.) |
| `source_response` | `TEXT` | Não | `''` | Resposta original importada (estritamente imutável) |
| `summary` | `TEXT` | Não | `''` | Resumo analítico |
| `explanation` | `TEXT` | Não | `''` | Explicação detalhada |
| `concepts` | `TEXT` | Não | `''` | Conceitos-chave |
| `references` | `TEXT` | Não | `''` | Referências |
| `notes` | `TEXT` | Não | `''` | Anotações pessoais do leitor |
| `created_at` | `DATETIME (UTC)` | Não | `CURRENT_TIMESTAMP` | Data/hora de criação |
| `updated_at` | `DATETIME (UTC)` | Não | `CURRENT_TIMESTAMP` | Data/hora da última alteração |
| `deleted_at` | `DATETIME (UTC)` | Sim | `NULL` | Data/hora do descarte individual para lixeira (UTC). |

**Índices e Constraints**:
- `CheckConstraint("length(trim(title)) > 0", name="title_not_blank")`
- `CheckConstraint('length(trim(summary || explanation || concepts || "references")) > 0', name="analysis_not_blank")`
- `Index("ix_studies_chapter_id", "chapter_id")`
- `Index("ix_studies_deleted_at", "deleted_at")` — Otimiza filtragem de estudos ativos e recuperação de estudos na lixeira.

---

## Máquina de Estados e Transições

```text
[Livro / Estudo Ativo]
   │
   ├─► POST /trash ──► [Na Lixeira] (deleted_at = utc_now())
   │                       │
   │                       ├─► POST /restore ──► [Ativo] (deleted_at = NULL)
   │                       │
   │                       ├─► DELETE /permanent ──► [Excluído Definitivo] (DELETE)
   │                       │
   │                       └─► Purga 30 dias (startup/rotina) ──► [Excluído Definitivo] (DELETE)
```

### Regras de Visibilidade e Hierarquia

1. **Estudo Ativo**:
   - Critério: `study.deleted_at IS NULL` AND `parent_book.deleted_at IS NULL`.
2. **Estudo na Lixeira Individual**:
   - Critério: `study.deleted_at IS NOT NULL`.
   - Visível na tela da Lixeira como item independente.
3. **Livro na Lixeira**:
   - Critério: `book.deleted_at IS NOT NULL`.
   - Visível na tela da Lixeira. Todos os seus estudos associados são ocultados do acervo ativo.
4. **Restauração em Cascata Ascendente**:
   - Restaurar um estudo onde `parent_book.deleted_at IS NOT NULL` seta simultaneamente:
     `study.deleted_at = NULL` E `parent_book.deleted_at = NULL`.
5. **Restauração Seletiva de Livro**:
   - Restaurar um livro seta `book.deleted_at = NULL`. Estudos com `study.deleted_at IS NULL` voltam a ser exibidos. Estudos que possuíam `study.deleted_at IS NOT NULL` continuam na lixeira até restauração explícita.
