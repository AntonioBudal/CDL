# Contratos de Interface: F 0.7.10 — Central de Revisão de Perguntas e Clozes

**Feature**: F 0.7.10 — Central de Revisão de Perguntas e Clozes  
**Branch**: `059-central-de-revisao`  
**Date**: 2026-10-04  

---

## 1. Contratos da API REST (Backend FastAPI)

### 1.1. `GET /api/review/stats`
Retorna as estatísticas consolidadas para montagem da página inicial da Central de Revisão.

- **Headers**: `Authorization: Bearer <token>` ou cookie de sessão ativo.
- **Resposta Sucesso (200 OK)**:
  ```json
  {
    "total_eligible": 45,
    "total_questions": 28,
    "total_hidden": 17,
    "reviewed_today": 12,
    "pending_review": 33,
    "books": [
      {
        "book_id": 1,
        "title": "A República",
        "items_count": 15
      },
      {
        "book_id": 2,
        "title": "Ética a Nicômaco",
        "items_count": 30
      }
    ]
  }
  ```

---

### 1.2. `GET /api/review/items`
Retorna a lista ordenada dos próximos cards de estudo conforme os filtros aplicados.

- **Query Parameters**:
  - `book_id` (opcional, inteiro): filtra itens pertencentes a um livro específico.
  - `chapter_id` (opcional, inteiro): filtra itens pertencentes a um capítulo específico.
  - `kind` (opcional, string): `'all'` (padrão), `'question'` ou `'hidden'`.
  - `limit` (opcional, inteiro, padrão `10`, máx `50`): tamanho do lote da rodada.
- **Resposta Sucesso (200 OK)**:
  ```json
  [
    {
      "id": 104,
      "study_id": 12,
      "study_title": "O Mito da Caverna",
      "book_id": 1,
      "book_title": "A República",
      "chapter_id": 3,
      "chapter_name": "Livro VII",
      "kind": "question",
      "section": "explanation",
      "question_text": "O que representam as sombras projetadas na parede?",
      "expected_answer": "As aparências ilusórias do mundo sensível.",
      "context_prefix": "No interior da caverna escura,",
      "context_suffix": "que os prisioneiros tomavam por realidade.",
      "last_reviewed_at": null,
      "review_count": 0,
      "last_rating": null
    }
  ]
  ```

---

### 1.3. `POST /api/review/items/{highlight_id}/record`
Registra a avaliação do usuário sobre um card específico após a revelação da resposta.

- **Path Parameter**: `highlight_id` (inteiro positivo).
- **Request Body**:
  ```json
  {
    "rating": "easy" // ou "medium" ou "hard"
  }
  ```
- **Resposta Sucesso (200 OK)**:
  ```json
  {
    "id": 104,
    "last_reviewed_at": "2026-10-04T19:30:00Z",
    "review_count": 1,
    "last_rating": "easy"
  }
  ```
- **Erros Possíveis**:
  - `404 Not Found`: Se o item não existir ou pertencer a outro usuário.
  - `422 Unprocessable Entity`: Se `rating` não for um dos valores permitidos.

---

## 2. Contratos do Frontend (Vue 3 / TypeScript)

### 2.1. Composable `useReviewSession.ts`

```typescript
export interface ReviewSessionState {
  items: ReviewItemRead[]
  currentIndex: number
  isRevealed: boolean
  isCompleted: boolean
  ratings: Record<number, 'easy' | 'medium' | 'hard'>
  loading: boolean
  submitting: boolean
  error: string | null
}

export function useReviewSession(): {
  state: DeepReadonly<ReviewSessionState>
  currentItem: ComputedRef<ReviewItemRead | null>
  progress: ComputedRef<{ current: number; total: number; percent: number }>
  summary: ComputedRef<{ easy: number; medium: number; hard: number; total: number }>
  loadItems: (filters?: { bookId?: number; chapterId?: number; kind?: string; limit?: number }) => Promise<void>
  revealAnswer: () => void
  submitRating: (rating: 'easy' | 'medium' | 'hard') => Promise<void>
  restartOrContinue: (limit?: number) => Promise<void>
  reset: () => void
}
```

---

### 2.2. Componente `ReviewCard.vue`

```typescript
interface ReviewCardProps {
  item: ReviewItemRead
  isRevealed: boolean
  busy?: boolean
}

const emit = defineEmits<{
  (e: 'reveal'): void
  (e: 'rate', rating: 'easy' | 'medium' | 'hard'): void
}>()
```

- **Acessibilidade**:
  - Container com `role="region"` e `aria-label="Card de revisão atual"`.
  - Botão de revelação: alvos táteis $\ge 44 \times 44$px e tecla `Espaço`.
  - Botões de classificação: teclas numéricas `1` (Difícil), `2` (Médio), `3` (Fácil).
  - Anúncio sonoro/leitor de tela via elemento com `aria-live="polite"` na revelação.

---

### 2.3. Rota Principal e Menu de Navegação

- **Caminho**: `/review`
- **Nome da Rota**: `review`
- **Componente**: `ReviewHubView.vue`
- **Item no Menu Global (`App.vue`)**: Ícone `<Icon name="rotate-ccw" :size="18" />` com rótulo "Revisão".
