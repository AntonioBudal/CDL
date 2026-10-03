# Contracts: Contratos do Composable e Componente da List View

**Feature**: F 0.7.5 — Redesenho da List View  
**Status**: Completed  
**Artifact**: `contracts/study-list-filters.md`

---

## 1. Contrato do Composable `useStudyListFilters`

### 1.1 Assinatura

```typescript
export interface UseStudyListFiltersOptions {
  studies: Ref<StudySummary[]>
  bookId: number
  chapterId?: number | null
}

export interface UseStudyListFiltersReturn {
  searchQuery: Ref<string>
  statusFilter: Ref<ReadingStatus | 'all'>
  sortColumn: Ref<SortColumn>
  sortDirection: Ref<SortDirection>
  filteredAndSortedStudies: ComputedRef<StudySummary[]>
  totalCount: ComputedRef<number>
  filteredCount: ComputedRef<number>
  isFilterActive: ComputedRef<boolean>
  toggleSort: (column: SortColumn) => void
  resetFilters: () => void
}
```

### 1.2 Regras de Ordenação

- `natural`: ordena por `study.position` (asc) e desempate por `study.id`.
- `title`: ordenação alfabética insensível a maiúsculas/minúsculas usando `localeCompare('pt-BR')`.
- `status`: ordenação baseada no peso ordinal do status:
  `rascunho (1) -> em_andamento (2) -> revisado (3) -> concluido (4)`.
- `date`: ordenação por data de atualização (`study.updated_at` ou fallback `study.created_at`).

### 1.3 Ciclo Tripartite de Alternância (`toggleSort(column)`)

- Se a coluna clicada for diferente da coluna atual:
  - Define `sortColumn = column`
  - Define `sortDirection = 'asc'`
- Se for a mesma coluna:
  - Se `sortDirection === 'asc'` → muda para `'desc'`
  - Se `sortDirection === 'desc'` → muda para `'default'` e `sortColumn = 'natural'`
  - Se `sortDirection === 'default'` → muda para `'asc'`

---

## 2. Contrato do Componente `StudyListView.vue`

### 2.1 Props e Emits

```typescript
interface StudyListViewProps {
  studies: StudySummary[]
  bookId: number
  chapterId?: number | null
  chapters?: { id: number; name: string }[]
  activeStudyId?: number | null
  loading?: boolean
}

interface StudyListViewEmits {
  (e: 'select-study', studyId: number): void
  (e: 'trash-study', study: StudySummary): void
}
```

### 2.2 Estrutura e Acessibilidade WAI-ARIA

- Container da tabela: `<div class="study-tabular-list" role="table" aria-label="Tabela de Estudos">`.
- Cabeçalhos: `<div role="row" class="list-header-row">` com células `<button role="columnheader" :aria-sort="getAriaSort(col)">`.
- Linha de estudo: `<div role="row" class="study-row-item" tabindex="0" @click="emit('select-study', study.id)" @keydown.enter="emit('select-study', study.id)">`.
- Micro-chips de seções:
  - Contêiner: `<div class="section-presence-chips" aria-label="Seções preenchidas">`
  - Cada chip: `<span class="presence-chip" :class="{ 'is-filled': study.has_summary }" title="Resumo Analítico">R</span>`
- Quando `loading === true`: 8 linhas de esqueleto animado (`skeleton-row`) substituem os dados tabulares.
