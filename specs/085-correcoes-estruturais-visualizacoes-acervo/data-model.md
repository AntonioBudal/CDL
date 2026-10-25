# Modelo de Dados e Estados: Correções Estruturais nas Visualizações do Acervo

**Feature**: `085-correcoes-estruturais-visualizacoes-acervo`
**Data**: 2026-10-24
**Status**: Concluída

---

## 1. Visão Geral

Esta feature opera estritamente na camada de apresentação (Frontend Vue 3 / TypeScript), não criando nem modificando tabelas ou colunas no banco de dados SQLite (`caderno.db`).

Os modelos e tipos de dados utilizados são os já consolidados no sistema em `src/types/index.ts`.

---

## 2. Tipos e Entidades de Frontend

### 2.1 StudySummary (Resumo de Estudo para Listagem)
```typescript
export interface StudySummary {
  id: number
  book_id: number
  chapter_id?: number | null
  title: string
  location?: string | null
  reading_status?: ReadingStatus | string
  created_at: string
  updated_at?: string | null
  has_summary?: boolean
  has_explanation?: boolean
  has_concepts?: boolean
  has_references?: boolean
  highlights_count?: number
  relations_count?: number
  summary_preview?: string | null
}
```

### 2.2 ReadingStatus (Estados de Leitura Suportados)
```typescript
export type ReadingStatus = 'rascunho' | 'em_andamento' | 'em_estudo' | 'revisado' | 'concluido'
```

### 2.3 SortColumn e SortDirection (Controle de Ordenação)
```typescript
export type SortColumn = 'title' | 'status' | 'date'
export type SortDirection = 'asc' | 'desc'
```

---

## 3. Estados Locais dos Componentes

### 3.1 StudyListView.vue
- `activeDropdownStudyId: Ref<number | null>`: Armazena o ID do estudo cuja linha está com o menu suspenso de status aberto, elevando seu índice de sobreposição (`z-index: 1000`).
- `isMobileFilterOpen: Ref<boolean>`: Alterna a visualização da gaveta móvel de filtros de status.
- `sortColumn: Ref<SortColumn>`: Coluna atualmente ordenada.
- `sortDirection: Ref<SortDirection>`: Direção (`asc` ou `desc`).

### 3.2 StudyGridView.vue
- `activeDropdownStudyId: Ref<number | null>`: Armazena o ID do estudo cujo cartão está com o menu suspenso de status aberto, aplicando `z-index: 50` para sobreposição fluida.
- `currentCriteria: Ref<GroupByCriteria>`: Critério de agrupamento ('chapter', 'status', 'none').

### 3.3 StudyStatusBadge.vue
- `isOpen: Ref<boolean>`: Controla a exibição do menu suspenso de opções de status.
- `opensUpward: Ref<boolean>`: Flag booleana recalculada dinamicamente via `getBoundingClientRect()`, determinando se o menu se expande para cima (`bottom: calc(100% + 4px)`) ou para baixo (`top: calc(100% + 4px)`).
- `isUpdating: Ref<boolean>`: Flag de carregamento enquanto a chamada de API assíncrona de atualização de status é realizada.
