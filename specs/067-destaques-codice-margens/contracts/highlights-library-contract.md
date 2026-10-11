# Interface & API Contract: F0.8.02 — Destaques: Códice e Margens Vivas

**Feature**: `067-destaques-codice-margens` | **Date**: 2026-10-11 | **Status**: Complete

---

## 1. Contratos de API REST (Backend Existente)

### 1.1 Consulta Paginada da Biblioteca de Destaques
- **Método / Rota:** `GET /api/highlights/library`
- **Parâmetros de Consulta (Query Params):**
  - `q` (string, opcional): Termo de busca textual para filtrar no trecho citado ou anotação.
  - `book_id` (integer, opcional): ID da obra para filtragem restrita.
  - `kind` (string, opcional): Tipo de destaque (`highlight`, `note`, `quote`, `question`, `hidden`).
  - `color` (string, opcional): Cor do grifo (`yellow`, `green`, `blue`, `pink`, `purple`).
  - `view_mode` (string, opcional): Modo de visualização (`recent` ou `by_book`).
  - `page` (integer, padrão: `1`): Número da página.
  - `per_page` (integer, padrão: `15`): Quantidade de itens por página.

- **Resposta de Sucesso (`200 OK`):**
```json
{
  "items": [
    {
      "id": 101,
      "study_id": 42,
      "study_title": "Capítulo 3 - A República das Letras",
      "book_id": 7,
      "book_title": "História da Leitura",
      "book_author": "Alberto Manguel",
      "chapter_id": 14,
      "chapter_title": "O Leitor Silencioso",
      "chapter_order": 3,
      "selected_text": "Ler em silêncio era uma proeza tão extraordinária na Antiguidade que Santo Agostinho registrou seu espanto ao ver Ambrósio folhear as páginas sem mover os lábios.",
      "note": "Reflexão seminal sobre a evolução cognitiva da leitura autônoma.",
      "color": "yellow",
      "kind": "quote",
      "created_at": "2026-10-06T20:30:00Z",
      "updated_at": "2026-10-06T20:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 15,
  "pages": 1,
  "available_books": [
    {
      "id": 7,
      "title": "História da Leitura",
      "author": "Alberto Manguel",
      "count": 1
    }
  ],
  "summary": {
    "total_highlights": 1,
    "total_notes": 1,
    "total_quotes": 1,
    "total_questions": 0,
    "total_hidden": 0,
    "by_color": {
      "yellow": 1,
      "green": 0,
      "blue": 0,
      "pink": 0,
      "purple": 0
    },
    "by_kind": {
      "quote": 1
    }
  }
}
```

---

### 1.2 Atualização Rápida de Nota In-Card
- **Método / Rota:** `PATCH /api/studies/{study_id}/highlights/{id}`
- **Corpo da Requisição (JSON):**
```json
{
  "note": "Nota pessoal atualizada diretamente na ficha literária."
}
```
- **Resposta de Sucesso (`200 OK`):**
Retorna o objeto `StudyHighlightResponse` atualizado.

---

### 1.3 Exclusão de Destaque
- **Método / Rota:** `DELETE /api/studies/{study_id}/highlights/{id}`
- **Resposta de Sucesso:** `204 No Content`

---

## 2. Contratos de Componentes e Eventos (Frontend)

### 2.1 Componente `HighlightCard.vue` (Ficha Literária)

#### Props
```typescript
interface Props {
  item: HighlightLibraryItem
}
```

#### Eventos Emitidos (Emits)
```typescript
interface Emits {
  (e: 'edit-note', id: number, studyId: number, note: string): void
  (e: 'delete', id: number, studyId: number): void
}
```

#### Regras de Comportamento e Formatação
1. Citação renderizada com classe `.editorial-quote` (`--font-serif`, entrelinha 1.6, aspas tipográficas).
2. Nota pessoal renderizada com classe `.reader-note` (`--font-sans`, fundo translúcido `--bg-subtle`, ícone `edit-3`).
3. Botão de cópia rápida no cabeçalho/ação da ficha com suporte aos formatos ABNT e Markdown.
4. Truncamento defensivo em 260 caracteres com botão "Expandir contexto" e transição suave $\le 180$ms.

---

### 2.2 Componente `HighlightFilterToolbar.vue` (Barra de Filtros Semânticos)

#### Props
```typescript
interface Props {
  searchQuery?: string
  selectedBookId?: number | null
  selectedKind?: string | null
  selectedColor?: string | null
  viewMode?: HighlightViewMode // 'recent' | 'by_book'
  availableBooks?: HighlightLibraryFilterOption[]
  summary?: HighlightLibrarySummary | null
  totalCount?: number
}
```

#### Eventos Emitidos (Emits)
```typescript
interface Emits {
  (e: 'update:searchQuery', val: string): void
  (e: 'update:selectedBookId', val: number | null): void
  (e: 'update:selectedKind', val: string | null): void
  (e: 'update:selectedColor', val: string | null): void
  (e: 'update:viewMode', val: HighlightViewMode): void
  (e: 'reset-filters'): void
}
```

#### Regras de Apresentação
1. O seletor de cores utiliza pílulas semânticas com nome cognitivo legível:
   - Amarelo: Ideia Central
   - Verde: Citação-chave
   - Azul: Dúvida
   - Rosa: Refutação
   - Roxo: Síntese
2. Cada pílula exibe indicador cromático, texto da categoria e contagem de itens (`(N)`).
3. Zero ocorrências de valores hexadecimais estáticos.

---

## 3. Contrato do Utilitário de Exportação de Citação (`citationFormatter.ts`)

```typescript
export function formatCitationABNT(item: HighlightLibraryItem): string {
  const author = item.book_author ? `${item.book_author.toUpperCase()}, ` : ''
  const chapter = item.chapter_title ? `, cap. ${item.chapter_title}` : ''
  return `"${item.selected_text}" (${author}${item.book_title}${chapter}).`
}

export function formatCitationMarkdown(item: HighlightLibraryItem): string {
  const author = item.book_author ? `— ${item.book_author}, ` : '— '
  const chapter = item.chapter_title ? ` (${item.chapter_title})` : ''
  return `> ${item.selected_text}\n>\n${author}*${item.book_title}*${chapter}`
}
```
