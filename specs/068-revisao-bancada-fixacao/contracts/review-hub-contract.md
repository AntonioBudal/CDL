# Interface & Component Contracts: F0.8.03 — Revisão: Bancada de Fixação Cognitiva

**Feature Branch**: `068-revisao-bancada-fixacao` | **Date**: 2026-10-11 | **Spec**: [spec.md](../spec.md)

Este documento especifica os contratos de comunicação entre a API REST de backend e os componentes visuais do frontend para a Central de Revisão.

---

## 1. Contratos da API REST (Backend)

### 1.1 `GET /api/review/stats`
Retorna as métricas consolidadas da Central de Revisão para o usuário logado.

**Resposta de Sucesso (`HTTP 200 OK`)**:
```json
{
  "total_eligible": 24,
  "total_questions": 14,
  "total_hidden": 10,
  "reviewed_today": 6,
  "pending_review": 18,
  "books": [
    {
      "id": 1,
      "title": "A República",
      "count": 12
    },
    {
      "id": 2,
      "title": "Ética a Nicômaco",
      "count": 6
    }
  ]
}
```

### 1.2 `GET /api/review/items`
Retorna a lista priorizada de cartões de estudo agendados para revisão.

**Query Parameters**:
- `book_id` (opcional, `int`): Filtrar por obra específica.
- `chapter_id` (opcional, `int`): Filtrar por capítulo específico.
- `kind` (opcional, `string`): Filtrar por tipo (`"question"` ou `"hidden"`).
- `limit` (opcional, `int`, padrão: 10, max: 50): Tamanho do lote da rodada.

**Resposta de Sucesso (`HTTP 200 OK`)**:
```json
[
  {
    "id": 101,
    "kind": "question",
    "prompt": "Qual é a definição platônica de justiça segundo Sócrates no Livro IV?",
    "answer": "A justiça consiste em cada parte da alma exercer a sua própria função sem usurpar a função das outras.",
    "book_id": 1,
    "book_title": "A República",
    "chapter_id": 4,
    "chapter_title": "Livro IV: As Quatro Virtudes",
    "study_id": 12,
    "study_title": "Estrutura da Alma Tripartite",
    "location": "p. 138",
    "review_count": 2,
    "last_rating": "medium",
    "last_reviewed_at": "2026-10-09T14:20:00Z",
    "next_review_at": "2026-10-11T00:00:00Z"
  }
]
```

### 1.3 `POST /api/review/items/{highlight_id}/record`
Registra a resposta de um item e atualiza seu intervalo de repetição espaçada.

**Request Body**:
```json
{
  "rating": "easy"
}
```

**Resposta de Sucesso (`HTTP 200 OK`)**:
```json
{
  "id": 101,
  "last_reviewed_at": "2026-10-11T16:50:00Z",
  "review_count": 3,
  "last_rating": "easy"
}
```

---

## 2. Contratos de Componentes Vue (Frontend)

### 2.1 `ReviewStatsHeader.vue` (Barra de Prontidão Intelectual)

Substitui as 5 caixas antigas por uma barra editorial contínua.

**Props**:
```typescript
interface Props {
  stats: ReviewStatsResponse
  loading?: boolean
  selectedBookId?: number | null
}
```

**Emits**:
```typescript
interface Emits {
  (e: 'start-practice'): void
  (e: 'filter-change', filters: { bookId: number | null }): void
}
```

---

### 2.2 `ReviewCard.vue` (Cartão Imersivo de Prática)

Executa a apresentação de frente e verso do cartão com controles de revelação e classificação.

**Props**:
```typescript
interface Props {
  item: ReviewItemRead
  isRevealed: boolean
  progress: { current: number; total: number; percent: number }
  submitting?: boolean
}
```

**Emits**:
```typescript
interface Emits {
  (e: 'reveal'): void
  (e: 'rate', rating: ReviewRating): void
  (e: 'cancel'): void
}
```

---

### 2.3 `ReviewPedagogicalEmpty.vue` (Estado Vazio Instrutivo)

Exibido quando não há itens pendentes ou o acervo de revisão é zero.

**Props**:
```typescript
interface Props {
  hasEligibleItems: boolean // true se tem cartões no acervo mas já concluiu hoje; false se acervo está vazio
}
```

**Emits**:
```typescript
interface Emits {
  (e: 'go-to-library'): void
  (e: 'review-again'): void
}
```

---

### 2.4 `ReviewSummaryModal.vue` (Resumo Sereno de Conclusão)

Apresenta o balanço da sessão concluída.

**Props**:
```typescript
interface Props {
  isOpen: boolean
  summary: {
    total: number
    easy: number
    medium: number
    hard: number
  }
  elapsedSeconds?: number
}
```

**Emits**:
```typescript
interface Emits {
  (e: 'close'): void
  (e: 'restart'): void
  (e: 'view-history'): void
}
```
