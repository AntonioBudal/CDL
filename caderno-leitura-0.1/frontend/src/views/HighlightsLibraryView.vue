<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  deleteStudyHighlight,
  getHighlightLibrary,
  updateStudyHighlight,
} from '../services/api'
import type {
  HighlightColor,
  HighlightKind,
  HighlightLibraryFilterOption,
  HighlightLibraryItem,
  HighlightLibrarySummary,
  HighlightViewMode,
} from '../types'
import HighlightCard from '../components/highlights/HighlightCard.vue'
import HighlightFilterToolbar from '../components/highlights/HighlightFilterToolbar.vue'
import Icon from '../components/ui/Icon.vue'

const route = useRoute()
const router = useRouter()

// Estado Reativo
const loading = ref(true)
const errorMessage = ref('')
const items = ref<HighlightLibraryItem[]>([])
const total = ref(0)
const page = ref(1)
const perPage = ref(15)
const totalPages = ref(1)
const availableBooks = ref<HighlightLibraryFilterOption[]>([])
const summary = ref<HighlightLibrarySummary | null>(null)

// Filtros
const searchQuery = ref('')
const selectedBookId = ref<number | null>(null)
const selectedKind = ref<string | null>(null)
const selectedColor = ref<string | null>(null)

// Modo de Visualização (Persistência em localStorage)
const STORAGE_KEY = 'caderno_highlights_view_mode'
const initialViewMode: HighlightViewMode =
  typeof window !== 'undefined' && window.localStorage
    ? (window.localStorage.getItem(STORAGE_KEY) as HighlightViewMode) || 'recent'
    : 'recent'
const viewMode = ref<HighlightViewMode>(initialViewMode)

watch(viewMode, (newVal) => {
  if (typeof window !== 'undefined' && window.localStorage) {
    window.localStorage.setItem(STORAGE_KEY, newVal)
  }
  updateUrlParams()
})

// Sincronização inicial a partir dos query params da URL
function initFromUrlParams() {
  const q = route.query.q as string | undefined
  if (q) searchQuery.value = q

  const book = route.query.book as string | undefined
  if (book && !Number.isNaN(Number(book))) selectedBookId.value = Number(book)

  const kind = route.query.kind as string | undefined
  if (kind) selectedKind.value = kind

  const color = route.query.color as string | undefined
  if (color) selectedColor.value = color

  const mode = route.query.view_mode as string | undefined
  if (mode === 'recent' || mode === 'by_book') viewMode.value = mode

  const p = route.query.page as string | undefined
  if (p && !Number.isNaN(Number(p))) page.value = Math.max(1, Number(p))
}

// Sincronização de volta para a URL
function updateUrlParams() {
  const query: Record<string, string> = {}
  if (searchQuery.value.trim()) query.q = searchQuery.value.trim()
  if (selectedBookId.value !== null) query.book = String(selectedBookId.value)
  if (selectedKind.value) query.kind = selectedKind.value
  if (selectedColor.value) query.color = selectedColor.value
  if (viewMode.value !== 'recent') query.view_mode = viewMode.value
  if (page.value > 1) query.page = String(page.value)

  void router.replace({ query })
}

let fetchAbortController: AbortController | null = null

async function fetchHighlights() {
  if (fetchAbortController) {
    fetchAbortController.abort()
  }
  fetchAbortController = new AbortController()

  loading.value = true
  errorMessage.value = ''

  try {
    const res = await getHighlightLibrary(
      {
        q: searchQuery.value.trim() || undefined,
        book_id: selectedBookId.value ?? undefined,
        kind: (selectedKind.value as HighlightKind) ?? undefined,
        color: (selectedColor.value as HighlightColor) ?? undefined,
        view_mode: viewMode.value,
        page: page.value,
        per_page: perPage.value,
      },
      fetchAbortController.signal
    )

    items.value = res.items
    total.value = res.total
    page.value = res.page
    perPage.value = res.per_page
    totalPages.value = res.pages
    availableBooks.value = res.available_books
    summary.value = res.summary
  } catch (err: unknown) {
    if (err instanceof Error && err.name === 'AbortError') return
    errorMessage.value = 'Não foi possível carregar a biblioteca de destaques. Tente novamente.'
  } finally {
    loading.value = false
  }
}

// Watchers de alteração de filtros
watch(
  [searchQuery, selectedBookId, selectedKind, selectedColor],
  () => {
    page.value = 1
    updateUrlParams()
    void fetchHighlights()
  }
)

function handleResetFilters() {
  searchQuery.value = ''
  selectedBookId.value = null
  selectedKind.value = null
  selectedColor.value = null
  page.value = 1
  updateUrlParams()
  void fetchHighlights()
}

function handlePageChange(newPage: number) {
  if (newPage < 1 || newPage > totalPages.value || newPage === page.value) return
  page.value = newPage
  updateUrlParams()
  void fetchHighlights()
  if (typeof window !== 'undefined') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// Gestão Rápida In-Card (T021, T022)
async function handleEditNote(id: number, studyId: number, newNote: string) {
  try {
    const updated = await updateStudyHighlight(studyId, id, { note: newNote })
    const target = items.value.find((it) => it.id === id)
    if (target) {
      target.note = updated.note
      target.updated_at = updated.updated_at
    }
  } catch {
    // Falha silenciosa ou log
  }
}

async function handleDeleteHighlight(id: number, studyId: number) {
  try {
    await deleteStudyHighlight(studyId, id)
    items.value = items.value.filter((it) => it.id !== id)
    total.value = Math.max(0, total.value - 1)
    if (items.value.length === 0 && page.value > 1) {
      page.value--
      void fetchHighlights()
    }
  } catch {
    // Tratamento de erro
  }
}

// Agrupamento para modo "Por Obra"
interface BookGroup {
  bookId: number
  bookTitle: string
  bookAuthor?: string | null
  items: HighlightLibraryItem[]
}

const groupedByBook = computed<BookGroup[]>(() => {
  const groups: Map<number, BookGroup> = new Map()

  for (const it of items.value) {
    let group = groups.get(it.book_id)
    if (!group) {
      group = {
        bookId: it.book_id,
        bookTitle: it.book_title,
        bookAuthor: it.book_author,
        items: [],
      }
      groups.set(it.book_id, group)
    }
    group.items.push(it)
  }

  return Array.from(groups.values())
})

const hasFiltersActive = computed(() => {
  return Boolean(
    searchQuery.value ||
    selectedBookId.value !== null ||
    selectedKind.value !== null ||
    selectedColor.value !== null
  )
})

onMounted(() => {
  initFromUrlParams()
  void fetchHighlights()
})
</script>

<template>
  <main class="highlights-library-view" aria-label="Biblioteca de Destaques e Anotações">
    <div class="library-container">
      <!-- Cabeçalho Principal -->
      <header class="library-header">
        <div class="header-titles">
          <h1 class="page-title">Destaques e Anotações</h1>
          <p class="page-subtitle">
            Explore, pesquise e organize todas as passagens marcadas e reflexões dos seus estudos.
          </p>
        </div>
      </header>

      <!-- Barra de Ferramentas e Filtros -->
      <HighlightFilterToolbar
        :search-query="searchQuery"
        :selected-book-id="selectedBookId"
        :selected-kind="selectedKind"
        :selected-color="selectedColor"
        :view-mode="viewMode"
        :available-books="availableBooks"
        :summary="summary"
        :total-count="total"
        @update:search-query="searchQuery = $event"
        @update:selected-book-id="selectedBookId = $event"
        @update:selected-kind="selectedKind = $event"
        @update:selected-color="selectedColor = $event"
        @update:view-mode="viewMode = $event"
        @reset-filters="handleResetFilters"
      />

      <!-- Feedback de Erro -->
      <div v-if="errorMessage" class="notice-error" role="alert">
        <Icon name="alert-triangle" :size="20" class="error-icon" />
        <div class="error-text">
          <p>{{ errorMessage }}</p>
          <button type="button" class="btn-retry" @click="fetchHighlights">Tentar novamente</button>
        </div>
      </div>

      <!-- Esqueleto de Carregamento (Loading Skeleton) -->
      <div v-else-if="loading" class="skeletons-list" aria-label="Carregando destaques...">
        <div v-for="n in 4" :key="n" class="skeleton-card">
          <div class="skeleton-header">
            <div class="skeleton-bar skeleton-title" />
            <div class="skeleton-bar skeleton-badge" />
          </div>
          <div class="skeleton-bar skeleton-quote" />
          <div class="skeleton-bar skeleton-quote-short" />
          <div class="skeleton-footer">
            <div class="skeleton-bar skeleton-date" />
            <div class="skeleton-bar skeleton-btn" />
          </div>
        </div>
      </div>

      <!-- Estado Vazio: Nenhum resultado encontrado -->
      <section
        v-else-if="items.length === 0"
        class="empty-state"
        aria-label="Nenhum destaque encontrado"
      >
        <div class="empty-icon-box" aria-hidden="true">
          <Icon name="search" :size="40" />
        </div>
        <h2 class="empty-title">
          {{ hasFiltersActive ? 'Nenhum destaque corresponde aos filtros' : 'Nenhum destaque registrado ainda' }}
        </h2>
        <p class="empty-description">
          <template v-if="hasFiltersActive">
            Tente remover os filtros ou buscar por outro termo textual para visualizar suas marcações.
          </template>
          <template v-else>
            Ao ler qualquer estudo no leitor, selecione trechos de texto para destacar passagens,
            fazer anotações pessoais, citações ou formular perguntas de reflexão.
          </template>
        </p>
        <div class="empty-actions">
          <button
            v-if="hasFiltersActive"
            type="button"
            class="btn-action-primary"
            @click="handleResetFilters"
          >
            <Icon name="rotate-ccw" :size="16" />
            <span>Limpar filtros</span>
          </button>
          <RouterLink
            v-else
            to="/livros"
            class="btn-action-primary"
          >
            <Icon name="book-open" :size="16" />
            <span>Explorar Meus Livros</span>
          </RouterLink>
        </div>
      </section>

      <!-- Conteúdo Principal: Modo "Recentes" -->
      <div
        v-else-if="viewMode === 'recent'"
        class="highlights-list mode-recent"
        aria-label="Lista de destaques recentes"
      >
        <HighlightCard
          v-for="item in items"
          :key="item.id"
          :item="item"
          @edit-note="handleEditNote"
          @delete="handleDeleteHighlight"
        />
      </div>

      <!-- Conteúdo Principal: Modo "Por Obra" -->
      <div
        v-else-if="viewMode === 'by_book'"
        class="highlights-groups mode-by-book"
        aria-label="Destaques agrupados por obra"
      >
        <section
          v-for="group in groupedByBook"
          :key="group.bookId"
          class="book-group-section"
        >
          <header class="group-header">
            <div class="group-title-row">
              <Icon name="book" :size="18" class="group-icon" />
              <h2 class="group-book-title">{{ group.bookTitle }}</h2>
              <span v-if="group.bookAuthor" class="group-book-author">
                — {{ group.bookAuthor }}
              </span>
            </div>
            <span class="group-badge">
              {{ group.items.length }} {{ group.items.length === 1 ? 'marcação' : 'marcações' }}
            </span>
          </header>

          <div class="group-cards-list">
            <HighlightCard
              v-for="item in group.items"
              :key="item.id"
              :item="item"
              @edit-note="handleEditNote"
              @delete="handleDeleteHighlight"
            />
          </div>
        </section>
      </div>

      <!-- Barra de Paginação (T018) -->
      <nav
        v-if="!loading && totalPages > 1"
        class="pagination-nav"
        aria-label="Navegação entre páginas de destaques"
      >
        <div class="pagination-info">
          Mostrando página <strong>{{ page }}</strong> de <strong>{{ totalPages }}</strong>
          ({{ total }} itens no total)
        </div>

        <div class="pagination-controls">
          <button
            type="button"
            class="pagination-btn btn-prev"
            :disabled="page <= 1"
            aria-label="Página anterior"
            @click="handlePageChange(page - 1)"
          >
            <Icon name="chevron-left" :size="18" />
            <span>Anterior</span>
          </button>

          <div class="pagination-pages">
            <button
              v-for="p in totalPages"
              :key="p"
              type="button"
              class="pagination-page-btn"
              :class="{ 'is-active': p === page }"
              :aria-current="p === page ? 'page' : undefined"
              :aria-label="`Ir para a página ${p}`"
              @click="handlePageChange(p)"
            >
              {{ p }}
            </button>
          </div>

          <button
            type="button"
            class="pagination-btn btn-next"
            :disabled="page >= totalPages"
            aria-label="Próxima página"
            @click="handlePageChange(page + 1)"
          >
            <span>Próxima</span>
            <Icon name="chevron-right" :size="18" />
          </button>
        </div>
      </nav>
    </div>
  </main>
</template>

<style scoped>
.highlights-library-view {
  width: 100%;
  min-height: calc(100vh - 60px);
  padding: 1.5rem 1rem 3rem;
  background-color: var(--color-bg-primary, #fafafa);
}

.library-container {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Cabeçalho */
.library-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text-primary, #0f172a);
  margin: 0 0 0.35rem;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 0.9375rem;
  color: var(--color-text-secondary, #64748b);
  margin: 0;
}

/* Listagem de Cards */
.highlights-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Modo Por Obra */
.highlights-groups {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.book-group-section {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--color-border, #e2e8f0);
}

.group-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.group-icon {
  color: var(--color-primary, #2563eb);
}

.group-book-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-text-primary, #0f172a);
  margin: 0;
}

.group-book-author {
  font-size: 0.875rem;
  color: var(--color-text-muted, #94a3b8);
}

.group-badge {
  font-size: 0.75rem;
  font-weight: 600;
  background-color: var(--color-surface-subtle, #f1f5f9);
  color: var(--color-text-secondary, #64748b);
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
}

.group-cards-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Esqueleto de Loading */
.skeletons-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skeleton-card {
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e4e4e7);
  border-radius: 8px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.skeleton-bar {
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: skeleton-pulse 1.5s infinite;
  border-radius: 4px;
}

@keyframes skeleton-pulse {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
}

.skeleton-title {
  width: 40%;
  height: 18px;
}

.skeleton-badge {
  width: 15%;
  height: 18px;
  border-radius: 9999px;
}

.skeleton-quote {
  width: 90%;
  height: 22px;
}

.skeleton-quote-short {
  width: 60%;
  height: 22px;
}

.skeleton-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
}

.skeleton-date {
  width: 20%;
  height: 14px;
}

.skeleton-btn {
  width: 25%;
  height: 32px;
  border-radius: 6px;
}

/* Estado Vazio */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3.5rem 1.5rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px dashed var(--color-border, #cbd5e1);
  border-radius: 8px;
}

.empty-icon-box {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background-color: var(--color-surface-subtle, #f1f5f9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted, #94a3b8);
  margin-bottom: 1.25rem;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary, #0f172a);
  margin: 0 0 0.5rem;
}

.empty-description {
  max-width: 480px;
  font-size: 0.9375rem;
  line-height: 1.55;
  color: var(--color-text-secondary, #64748b);
  margin: 0 0 1.5rem;
}

.empty-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-action-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background-color: var(--color-primary, #2563eb);
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 0.65rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.15s ease;
  min-height: 40px;
}

.btn-action-primary:hover {
  background-color: var(--color-primary-hover, #1d4ed8);
}

/* Feedback de Erro */
.notice-error {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 1rem 1.25rem;
  border-radius: 8px;
}

.error-icon {
  color: #dc2626;
  flex-shrink: 0;
}

.btn-retry {
  background: none;
  border: none;
  color: #dc2626;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  font-size: 0.875rem;
  font-weight: 600;
}

/* Paginação */
.pagination-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem 0;
  flex-wrap: wrap;
}

.pagination-info {
  font-size: 0.8125rem;
  color: var(--color-text-secondary, #64748b);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-pages {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.pagination-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 6px;
  padding: 0.4rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-primary, #0f172a);
  cursor: pointer;
  min-height: 36px;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn:not(:disabled):hover {
  background-color: var(--color-surface-hover, #f1f5f9);
}

.pagination-page-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border, #cbd5e1);
  background-color: var(--color-surface, #ffffff);
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-primary, #0f172a);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-page-btn.is-active {
  background-color: var(--color-primary, #2563eb);
  border-color: var(--color-primary, #2563eb);
  color: #ffffff;
  font-weight: 700;
}

.pagination-page-btn:not(.is-active):hover {
  background-color: var(--color-surface-hover, #f1f5f9);
}

/* Responsividade Móvel */
@media (max-width: 640px) {
  .highlights-library-view {
    padding: 1rem 0.75rem 2.5rem;
  }

  .pagination-nav {
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }

  .pagination-btn,
  .pagination-page-btn {
    min-height: 44px;
    min-width: 44px;
  }
}
</style>
