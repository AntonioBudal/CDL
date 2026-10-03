<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { StudySummary, ReadingStatus, SortColumn } from '../../types'
import Icon from '../ui/Icon.vue'
import EmptyState from '../ui/EmptyState.vue'
import StudyStatusBadge from '../StudyStatusBadge.vue'
import { useStudyListFilters } from '../../composables/useStudyListFilters'

interface Props {
  studies: StudySummary[]
  bookId: number
  chapterId?: number | null
  chapters?: { id: number; name: string }[]
  activeStudyId?: number | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  chapterId: null,
  chapters: () => [],
  activeStudyId: null,
  loading: false,
})

const emit = defineEmits<{
  (e: 'select-study', studyId: number): void
  (e: 'trash-study', study: StudySummary): void
}>()

const {
  searchQuery,
  statusFilter,
  sortColumn,
  sortDirection,
  filteredAndSortedStudies,
  totalCount,
  filteredCount,
  isFilterActive,
  toggleSort,
  resetFilters,
} = useStudyListFilters({
  studies: computed(() => props.studies),
  bookId: computed(() => props.bookId),
  chapterId: computed(() => props.chapterId),
})

const STATUS_OPTIONS: { value: ReadingStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'Todos' },
  { value: 'rascunho', label: 'Rascunho' },
  { value: 'em_andamento', label: 'Em Andamento' },
  { value: 'revisado', label: 'Revisado' },
  { value: 'concluido', label: 'Concluído' },
]

const isMobileFilterOpen = ref(false)

function onStatusChange(study: StudySummary, newStatus: ReadingStatus) {
  study.reading_status = newStatus
}

function formatDate(isoStr?: string | null): string {
  if (!isoStr) return '—'
  try {
    return new Date(isoStr).toLocaleDateString('pt-BR')
  } catch {
    return isoStr
  }
}

function getAriaSort(col: SortColumn): 'ascending' | 'descending' | 'none' {
  if (sortColumn.value === col) {
    if (sortDirection.value === 'asc') return 'ascending'
    if (sortDirection.value === 'desc') return 'descending'
  }
  return 'none'
}
</script>

<template>
  <div class="study-list-view" role="region" aria-label="Visualização em Lista de Estudos">
    <!-- Estado vazio do capítulo (sem nenhum estudo importado) -->
    <EmptyState
      v-if="studies.length === 0 && !loading"
      icon="book-open"
      title="Nenhum estudo neste capítulo"
      description="Importe o texto-base de um fichamento para registrar reflexões e análises sobre este trecho da leitura."
      heading-level="h3"
    >
      <RouterLink
        v-if="chapterId"
        class="button primary"
        :to="{ name: 'import', query: { book: bookId, chapter: chapterId } }"
      >
        Importar estudo
      </RouterLink>
    </EmptyState>

    <div v-else class="study-list-container">
      <!-- Barra de Ferramentas: Busca Rápida + Pílulas de Status + Contador -->
      <div class="list-toolbar">
        <div class="search-bar-row">
          <div class="search-input-wrapper">
            <Icon name="search" :size="16" class="search-icon" />
            <input
              v-model="searchQuery"
              type="search"
              placeholder="Buscar por título, localização ou conteúdo..."
              class="list-search-input"
              aria-label="Buscar estudos"
            />
            <button
              v-if="searchQuery"
              type="button"
              class="clear-search-btn"
              aria-label="Limpar texto da busca"
              @click="searchQuery = ''"
            >
              <Icon name="x" :size="14" />
            </button>
          </div>

          <!-- Botão expansível no mobile para gaveta de filtros -->
          <button
            type="button"
            class="mobile-filter-toggle"
            aria-label="Alternar filtros de status"
            @click="isMobileFilterOpen = !isMobileFilterOpen"
          >
            <span>Filtros</span>
            <Icon :name="isMobileFilterOpen ? 'chevron-up' : 'chevron-down'" :size="16" />
          </button>
        </div>

        <!-- Seletor de Pílulas de Status -->
        <div class="status-filters-pills" :class="{ 'is-mobile-open': isMobileFilterOpen }">
          <button
            v-for="opt in STATUS_OPTIONS"
            :key="opt.value"
            type="button"
            class="status-pill"
            :class="{ 'is-active': statusFilter === opt.value }"
            @click="statusFilter = opt.value"
          >
            {{ opt.label }}
          </button>
        </div>

        <!-- Linha de Metadados: Contador e Reset -->
        <div class="list-meta-bar">
          <span class="results-counter">
            {{ isFilterActive ? `Exibindo ${filteredCount} de ${totalCount} estudos` : `${totalCount} estudos` }}
          </span>

          <button
            v-if="isFilterActive"
            type="button"
            class="reset-filters-btn"
            @click="resetFilters"
          >
            Limpar filtros
          </button>
        </div>
      </div>

      <!-- Estado de Carregamento: Skeleton Screens Animados -->
      <div
        v-if="loading"
        class="study-tabular-list skeleton-table"
        role="table"
        aria-label="Carregando estudos"
      >
        <div v-for="i in 8" :key="i" class="skeleton-row shimmer">
          <div class="skeleton-cell col-title"></div>
          <div class="skeleton-cell col-status"></div>
          <div class="skeleton-cell col-location"></div>
          <div class="skeleton-cell col-date"></div>
          <div class="skeleton-cell col-sections"></div>
          <div class="skeleton-cell col-actions"></div>
        </div>
      </div>

      <!-- Estado Vazio de Busca / Filtro Sem Resultados -->
      <div
        v-else-if="filteredAndSortedStudies.length === 0"
        class="empty-search-state"
      >
        <Icon name="search" :size="36" class="empty-search-icon" />
        <h4 class="empty-search-title">Nenhum estudo encontrado</h4>
        <p class="empty-search-desc">
          Nenhum estudo corresponde aos critérios de busca ou filtros aplicados.
        </p>
        <button
          type="button"
          class="button primary"
          @click="resetFilters"
        >
          Limpar filtros
        </button>
      </div>

      <!-- Tabela Semântica de Alta Densidade -->
      <div
        v-else
        class="study-tabular-list"
        role="table"
        aria-label="Tabela de Estudos"
      >
        <!-- Cabeçalho de Colunas Ordenáveis -->
        <div role="row" class="list-header-row">
          <button
            type="button"
            role="columnheader"
            class="header-sort-btn col-title"
            :aria-sort="getAriaSort('title')"
            @click="toggleSort('title')"
          >
            <span>Título</span>
            <span v-if="sortColumn === 'title'" class="sort-indicator">
              {{ sortDirection === 'asc' ? '↑' : '↓' }}
            </span>
          </button>

          <button
            type="button"
            role="columnheader"
            class="header-sort-btn col-status"
            :aria-sort="getAriaSort('status')"
            @click="toggleSort('status')"
          >
            <span>Status</span>
            <span v-if="sortColumn === 'status'" class="sort-indicator">
              {{ sortDirection === 'asc' ? '↑' : '↓' }}
            </span>
          </button>

          <span role="columnheader" class="header-cell col-location">
            Localização
          </span>

          <button
            type="button"
            role="columnheader"
            class="header-sort-btn col-date"
            :aria-sort="getAriaSort('date')"
            @click="toggleSort('date')"
          >
            <span>Data</span>
            <span v-if="sortColumn === 'date'" class="sort-indicator">
              {{ sortDirection === 'asc' ? '↑' : '↓' }}
            </span>
          </button>

          <span role="columnheader" class="header-cell col-sections">
            Seções
          </span>

          <span role="columnheader" class="header-cell col-actions">
            Ações
          </span>
        </div>

        <!-- Linhas de Estudos -->
        <div
          v-for="study in filteredAndSortedStudies"
          :key="study.id"
          role="row"
          class="study-row-item"
          :class="{ 'is-focused': activeStudyId === study.id }"
          tabindex="0"
          @click="emit('select-study', study.id)"
          @keydown.enter="emit('select-study', study.id)"
        >
          <!-- Coluna 1: Título -->
          <div class="col-title cell">
            <RouterLink
              :to="{ name: 'study', params: { bookId, studyId: study.id } }"
              class="row-title-link"
              @click.stop="emit('select-study', study.id)"
            >
              {{ study.title }}
            </RouterLink>
          </div>

          <!-- Coluna 2: Status -->
          <div class="col-status cell">
            <StudyStatusBadge
              :status="study.reading_status || 'rascunho'"
              :study-id="study.id"
              :interactive="true"
              @change="(newSt) => onStatusChange(study, newSt)"
            />
          </div>

          <!-- Colunas 3 e 4 agrupadas: Localização e Data -->
          <div class="col-meta-group">
            <div class="col-location cell">
              <span v-if="study.location" class="location-tag">
                <Icon name="book-open" :size="12" class="mr-1 inline" />
                {{ study.location }}
              </span>
              <span v-else class="text-muted">—</span>
            </div>

            <div class="col-date cell">
              <time
                :datetime="study.updated_at || study.created_at"
                class="row-date"
              >
                {{ formatDate(study.updated_at || study.created_at) }}
              </time>
            </div>
          </div>

          <!-- Coluna 5: Micro-Chips de Seções Analíticas -->
          <div class="col-sections cell">
            <div class="section-presence-chips" aria-label="Seções preenchidas">
              <span
                class="presence-chip chip-summary"
                :class="{ 'is-filled': study.has_summary }"
                :title="study.has_summary ? 'Resumo Analítico (Preenchido)' : 'Resumo Analítico (Vazio)'"
              >R</span>
              <span
                class="presence-chip chip-explanation"
                :class="{ 'is-filled': study.has_explanation }"
                :title="study.has_explanation ? 'Explicação Contextualizada (Preenchida)' : 'Explicação Contextualizada (Vazia)'"
              >E</span>
              <span
                class="presence-chip chip-concepts"
                :class="{ 'is-filled': study.has_concepts }"
                :title="study.has_concepts ? 'Conceitos-Chave (Preenchidos)' : 'Conceitos-Chave (Vazios)'"
              >C</span>
              <span
                class="presence-chip chip-references"
                :class="{ 'is-filled': study.has_references }"
                :title="study.has_references ? 'Referências e Conexões (Preenchidas)' : 'Referências e Conexões (Vazias)'"
              >Ref</span>
            </div>
          </div>

          <!-- Coluna 6: Ações -->
          <div class="col-actions cell">
            <button
              type="button"
              class="row-trash-btn"
              title="Mover estudo para a lixeira"
              aria-label="Mover estudo para a lixeira"
              @click.stop="emit('trash-study', study)"
            >
              <Icon name="trash" :size="15" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.study-list-view {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.study-list-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* -------------------------------------------------------------------------- */
/* Barra de Ferramentas: Busca + Pílulas de Status + Metadados                */
/* -------------------------------------------------------------------------- */

.list-toolbar {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background-color: var(--color-surface, #ffffff);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-card, 8px);
  padding: 0.85rem 1rem;
}

.search-bar-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: var(--color-muted, #64748b);
  pointer-events: none;
}

.list-search-input {
  width: 100%;
  padding: 0.45rem 2rem 0.45rem 2.25rem;
  font-size: 0.875rem;
  color: var(--color-text, #0f172a);
  background-color: var(--color-surface-soft, #f8fafc);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control, 6px);
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.list-search-input:focus {
  border-color: var(--color-accent, #1d4ed8);
  box-shadow: 0 0 0 2px rgba(29, 78, 216, 0.15);
}

.clear-search-btn {
  position: absolute;
  right: 0.5rem;
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--color-muted, #64748b);
  cursor: pointer;
  border-radius: 50%;
  font-size: 0.75rem;
}

.clear-search-btn:hover {
  color: var(--color-text);
  background-color: var(--color-surface-hover);
}

.mobile-filter-toggle {
  display: none;
  align-items: center;
  gap: 0.35rem;
  padding: 0 0.75rem;
  min-width: 44px;
  min-height: 44px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text);
  background-color: var(--color-surface-soft);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control);
  cursor: pointer;
}

.status-filters-pills {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.status-pill {
  padding: 0.3rem 0.7rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-meta, #556984);
  background-color: var(--color-surface-soft, #f1f5f9);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control, 6px);
  cursor: pointer;
  transition: all 0.15s ease;
}

.status-pill:hover {
  background-color: var(--color-surface-hover, #e2e8f0);
  color: var(--color-text);
}

.status-pill.is-active {
  background-color: var(--color-accent, #1d4ed8);
  color: #ffffff;
  border-color: var(--color-accent, #1d4ed8);
}

.list-meta-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.25rem;
  border-top: 1px solid var(--color-border-divider);
  font-size: 0.78rem;
  color: var(--color-muted, #64748b);
}

.results-counter {
  font-variant-numeric: tabular-nums;
}

.reset-filters-btn {
  background: transparent;
  border: none;
  color: var(--color-accent, #1d4ed8);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.2rem 0.4rem;
  border-radius: var(--radius-control);
}

.reset-filters-btn:hover {
  text-decoration: underline;
}

/* -------------------------------------------------------------------------- */
/* Tabela Semântica e Linhas                                                  */
/* -------------------------------------------------------------------------- */

.study-tabular-list {
  display: flex;
  flex-direction: column;
  background: var(--color-surface, #ffffff);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-card, 8px);
  overflow: hidden;
}

.list-header-row {
  display: flex;
  align-items: center;
  padding: 0.6rem 1rem;
  background-color: var(--color-surface-soft, #f8fafc);
  border-bottom: 1px solid var(--color-border-divider);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-meta, #556984);
}

.header-sort-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: transparent;
  border: none;
  padding: 0;
  font: inherit;
  color: inherit;
  text-transform: inherit;
  letter-spacing: inherit;
  cursor: pointer;
  text-align: left;
}

.header-sort-btn:hover {
  color: var(--color-accent, #1d4ed8);
}

.sort-indicator {
  font-size: 0.85rem;
  color: var(--color-accent, #1d4ed8);
  font-weight: bold;
}

.header-cell {
  display: inline-flex;
  align-items: center;
}

.study-row-item {
  display: flex;
  align-items: center;
  padding: 0.65rem 1rem;
  border-bottom: 1px solid var(--color-border-divider);
  transition: background-color 0.15s ease;
  cursor: pointer;
}

.study-row-item:last-child {
  border-bottom: none;
}

.study-row-item:hover {
  background-color: var(--color-surface-hover, #f1f5f9);
}

.study-row-item:hover .row-title-link {
  color: var(--color-hover-text, #0284c7);
}

.study-row-item:hover .location-tag {
  color: var(--color-hover-text);
  opacity: 0.85;
}

.study-row-item:hover .row-date {
  color: var(--color-hover-text);
  opacity: 0.85;
}

.study-row-item.is-focused {
  background-color: var(--color-selected-bg, #eaf0ff);
  border-left: 3px solid var(--color-accent, #1d4ed8);
}

/* Colunas Tabulares no Desktop */
.col-title {
  flex: 2 1 0%;
  min-width: 0;
}

.col-status {
  flex: 0.9 1 0%;
  min-width: 105px;
}

.col-meta-group {
  display: contents;
}

.col-location {
  flex: 1.1 1 0%;
  min-width: 0;
}

.col-date {
  flex: 0.8 1 0%;
  min-width: 80px;
}

.col-sections {
  flex: 0 0 116px;
  display: flex;
  align-items: center;
}

.col-actions {
  flex: 0 0 44px;
  display: flex;
  justify-content: flex-end;
}

.row-title-link {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.row-title-link:hover {
  color: var(--color-accent);
  text-decoration: underline;
}

.location-tag {
  font-size: 0.82rem;
  color: var(--color-muted, #64748b);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-date {
  font-size: 0.8rem;
  color: var(--color-muted, #64748b);
  font-variant-numeric: tabular-nums;
}

.text-muted {
  color: var(--color-muted, #64748b);
  font-size: 0.85rem;
}

/* Micro-Chips Analíticos Fixos (R, E, C, Ref) */
.section-presence-chips {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.presence-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 18px;
  padding: 0 3px;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: 3px;
  background-color: var(--color-surface-soft, #f1f5f9);
  color: var(--color-muted, #94a3b8);
  opacity: 0.35;
  transition: all 0.15s ease;
  user-select: none;
}

.presence-chip.is-filled {
  opacity: 1;
}

.chip-summary.is-filled {
  background-color: rgba(37, 99, 235, 0.15);
  color: #1d4ed8;
}

.chip-explanation.is-filled {
  background-color: rgba(5, 150, 105, 0.15);
  color: #047857;
}

.chip-concepts.is-filled {
  background-color: rgba(124, 58, 237, 0.15);
  color: #6d28d9;
}

.chip-references.is-filled {
  background-color: rgba(217, 119, 6, 0.15);
  color: #b45309;
}

.row-trash-btn {
  min-width: 44px;
  min-height: 44px;
  padding: 0;
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-muted);
  border-radius: var(--radius-control);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.row-trash-btn:hover {
  color: var(--color-danger, #b91c1c);
  background: var(--color-surface-hover);
  border-color: var(--color-border);
}

/* -------------------------------------------------------------------------- */
/* Estado Vazio de Busca                                                      */
/* -------------------------------------------------------------------------- */

.empty-search-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 1.5rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-card, 8px);
  gap: 0.75rem;
}

.empty-search-icon {
  color: var(--color-muted);
}

.empty-search-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text);
}

.empty-search-desc {
  margin: 0;
  font-size: 0.88rem;
  color: var(--color-muted);
  max-width: 420px;
}

/* -------------------------------------------------------------------------- */
/* Skeleton Screens Shimmer                                                   */
/* -------------------------------------------------------------------------- */

.skeleton-row {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  gap: 1rem;
  border-bottom: 1px solid var(--color-border-divider);
}

.skeleton-cell {
  height: 16px;
  background-color: var(--color-surface-soft, #e2e8f0);
  border-radius: 4px;
}

.skeleton-row.shimmer {
  position: relative;
  overflow: hidden;
}

.skeleton-row.shimmer::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.4) 50%,
    transparent 100%
  );
  animation: shimmer-animation 1.5s infinite;
}

@keyframes shimmer-animation {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* -------------------------------------------------------------------------- */
/* Responsividade Móvel (< 768px): 2 Níveis sem Rolagem Horizontal           */
/* -------------------------------------------------------------------------- */

@media (max-width: 767px) {
  .list-header-row {
    display: none;
  }

  .mobile-filter-toggle {
    display: inline-flex;
  }

  .status-filters-pills {
    display: none;
    padding-top: 0.5rem;
    border-top: 1px solid var(--color-border-divider);
  }

  .status-filters-pills.is-mobile-open {
    display: flex;
  }

  .status-pill {
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    padding: 0.5rem 0.85rem;
  }

  .study-row-item {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    padding: 0.75rem 1rem;
    gap: 0.4rem;
  }

  /* Nível 1: Título, Status e Ação */
  .col-title {
    width: 100%;
    margin-bottom: 0.2rem;
  }

  .col-status {
    flex: initial;
    min-width: auto;
  }

  /* Nível 2: Metadados (Localização, Data) e Chips de Seções */
  .col-meta-group {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    flex-wrap: wrap;
    gap: 0.4rem;
  }

  .col-location {
    flex: initial;
  }

  .col-date {
    flex: initial;
    min-width: auto;
  }

  .col-sections {
    width: 100%;
    margin-top: 0.25rem;
  }

  .col-actions {
    position: absolute;
    right: 0.75rem;
    top: 0.5rem;
  }

  .study-row-item {
    position: relative;
    padding-right: 3.5rem;
  }
}
</style>
