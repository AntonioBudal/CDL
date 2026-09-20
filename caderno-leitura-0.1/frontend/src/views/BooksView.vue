<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import BookCover from '../components/BookCover.vue'
import CategoryBadge from '../components/CategoryBadge.vue'
import CategorySelector from '../components/CategorySelector.vue'
import LibraryToolbar from '../components/LibraryToolbar.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import LoadingSkeleton from '../components/ui/LoadingSkeleton.vue'
import { api, errorMessage } from '../services/api'
import { useLibraryFilter } from '../composables/useLibraryFilter'
import { useMagneticHover } from '../composables/useMagneticHover'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import type { Book } from '../types'

const { handlePointerMove, handlePointerLeave } = useMagneticHover()

const router = useRouter()
const books = ref<Book[]>([])
const loading = ref(true)
const loadError = ref('')
const title = ref('')
const titleInput = ref<HTMLInputElement | null>(null)
const author = ref('')
const newBookCategoryIds = ref<string[]>([])
const saving = ref(false)
const saveError = ref('')
let request: AbortController | null = null
let disposed = false
useUnsavedChanges(() => !!(title.value || author.value || newBookCategoryIds.value.length > 0), () => saving.value)

const {
  searchQuery,
  selectedCategory,
  viewMode,
  sortBy,
  filteredBooks,
  totalCount,
  filteredCount,
  hasActiveSearch,
  hasActiveCategory,
  hasActiveFilters,
  setViewMode,
  setSortBy,
  setSelectedCategory,
  clearSearch,
  clearCategory,
  clearAllFilters,
} = useLibraryFilter(books)

async function load() {
  request?.abort()
  const controller = new AbortController()
  request = controller
  loading.value = true
  loadError.value = ''
  try {
    const result = await api.listBooks(controller.signal)
    if (!controller.signal.aborted) books.value = result
  } catch (error) {
    if (!controller.signal.aborted) loadError.value = errorMessage(error)
  } finally {
    if (!controller.signal.aborted) loading.value = false
  }
}

async function createBook() {
  if (saving.value || !title.value.trim()) return
  saving.value = true
  saveError.value = ''
  let created: Book | null = null
  try {
    created = await api.createBook(title.value, author.value, newBookCategoryIds.value)
    title.value = ''; author.value = ''; newBookCategoryIds.value = []
  } catch (error) {
    if (!disposed) saveError.value = errorMessage(error)
  } finally { saving.value = false }
  if (created && !disposed) await router.push({ name: 'book', params: { bookId: created.id } })
}

onMounted(load)
onBeforeUnmount(() => { disposed = true; request?.abort() })
</script>

<template>
  <div class="books-view">
    <header class="page-header">
    <p class="eyebrow">Seu acervo</p>
    <h1>Meus livros</h1>
  </header>
  <div class="library-layout">
    <section aria-label="Livros cadastrados" :aria-busy="loading">
      <div v-if="loading" class="books-loading-skeleton" role="status" aria-label="Carregando livros">
        <div class="book-grid">
          <div v-for="i in 4" :key="i" class="book-card-skeleton" style="display: flex; flex-direction: column; gap: 12px; align-items: center; padding: 24px 16px; border: 1px solid var(--color-border); border-radius: var(--radius-md);">
            <LoadingSkeleton shape="rect" width="120px" height="180px" />
            <LoadingSkeleton shape="text" width="75%" height="20px" />
            <LoadingSkeleton shape="text" width="50%" height="14px" />
          </div>
        </div>
      </div>
      <div v-else-if="loadError" class="notice error" role="alert">
        <p>{{ loadError }}</p>
        <button class="secondary" type="button" @click="load">Tentar novamente</button>
      </div>
      <EmptyState
        v-else-if="books.length === 0"
        icon="book-open"
        title="Seu primeiro livro começa aqui"
        description="Cadastre o livro abaixo e, em seguida, adicione um capítulo para organizar seus estudos."
        heading-level="h2"
      >
        <a href="#book-title" class="button primary" @click.prevent="titleInput?.focus()">Cadastrar meu primeiro livro</a>
      </EmptyState>
      <template v-else>
        <LibraryToolbar
          :search-query="searchQuery"
          :selected-category="selectedCategory"
          :view-mode="viewMode"
          :sort-by="sortBy"
          :total-count="totalCount"
          :filtered-count="filteredCount"
          :has-active-search="hasActiveSearch"
          :has-active-category="hasActiveCategory"
          :has-active-filters="hasActiveFilters"
          @update:search-query="searchQuery = $event"
          @update:selected-category="setSelectedCategory"
          @update:view-mode="setViewMode"
          @update:sort-by="setSortBy"
          @clear-search="clearSearch"
          @clear-category="clearCategory"
          @clear-all-filters="clearAllFilters"
        />

        <EmptyState
          v-if="filteredBooks.length === 0"
          icon="search"
          title="Nenhum livro encontrado"
          :description="searchQuery && selectedCategory
            ? `Nenhum resultado corresponde à busca “${searchQuery}” na categoria selecionada.`
            : searchQuery
              ? `Nenhum resultado corresponde à busca “${searchQuery}”.`
              : 'Nenhum livro encontrado na categoria selecionada.'"
          heading-level="h2"
        >
          <button type="button" class="secondary" @click="clearAllFilters">Limpar filtros</button>
        </EmptyState>

        <!-- Modo Grade de Capas -->
        <ul v-else-if="viewMode === 'grid'" class="book-grid">
          <li v-for="(book, index) in filteredBooks" :key="book.id" :style="{ '--card-index': index }">
            <RouterLink
              class="book-card has-cover"
              :to="{ name: 'book', params: { bookId: book.id } }"
              @pointermove="handlePointerMove"
              @pointerleave="handlePointerLeave"
            >
              <div class="book-card-cover-wrapper">
                <BookCover :cover-image="book.cover_image" :title="book.title" :author="book.author" size="md" />
              </div>
              <span class="book-number" aria-hidden="true">{{ String(index + 1).padStart(2, '0') }}</span>
              <h2>{{ book.title }}</h2>
              <p>{{ book.author || 'Autor não informado' }}</p>
              <div v-if="book.categories && book.categories.length > 0" class="flex flex-wrap gap-1 mt-1.5 justify-center">
                <CategoryBadge
                  v-for="cat in book.categories.slice(0, 2)"
                  :key="cat.id"
                  :category="cat"
                  clickable
                  size="sm"
                  title="Filtrar por esta categoria"
                  @click="setSelectedCategory(cat.id)"
                />
                <span v-if="book.categories.length > 2" class="text-xs text-muted self-center">
                  +{{ book.categories.length - 2 }}
                </span>
              </div>
              <span class="card-action">Ver capítulos</span>
            </RouterLink>
          </li>
        </ul>

        <!-- Modo Lista Compacta -->
        <ul v-else class="book-list-compact" role="list">
          <li
            v-for="(book, index) in filteredBooks"
            :key="book.id"
            class="book-list-item"
            :style="{ '--card-index': index }"
            @pointermove="handlePointerMove"
            @pointerleave="handlePointerLeave"
          >
            <RouterLink class="book-list-link" :to="{ name: 'book', params: { bookId: book.id } }">
              <div class="book-list-cover">
                <BookCover :cover-image="book.cover_image" :title="book.title" :author="book.author" size="sm" />
              </div>
              <div class="book-list-info">
                <div class="book-list-header">
                  <h2 class="book-list-title">{{ book.title }}</h2>
                  <span v-if="book.year" class="book-list-year" aria-label="Ano de publicação">({{ book.year }})</span>
                </div>
                <p v-if="book.subtitle" class="book-list-subtitle">{{ book.subtitle }}</p>
                <p class="book-list-author">{{ book.author || 'Autor não informado' }}</p>
                <div v-if="book.categories && book.categories.length > 0" class="flex flex-wrap gap-1 mt-1">
                  <CategoryBadge
                    v-for="cat in book.categories"
                    :key="cat.id"
                    :category="cat"
                    clickable
                    size="sm"
                    title="Filtrar por esta categoria"
                    @click="setSelectedCategory(cat.id)"
                  />
                </div>
              </div>
              <span class="book-list-action" aria-hidden="true">Ver capítulos →</span>
            </RouterLink>
          </li>
        </ul>
      </template>
    </section>
    <aside class="panel form-panel" aria-labelledby="new-book-heading">
      <h2 id="new-book-heading">Novo livro</h2>
      <form @submit.prevent="createBook">
        <fieldset :disabled="saving">
          <div class="field">
            <label for="book-title">Título do livro</label>
            <input id="book-title" ref="titleInput" v-model="title" required placeholder="Como aparece na capa" />
          </div>
          <div class="field">
            <label for="book-author">Autor <span class="optional">opcional</span></label>
            <input id="book-author" v-model="author" autocomplete="off" />
          </div>
          <div class="field">
            <label>Categorias <span class="optional">opcional</span></label>
            <CategorySelector v-model="newBookCategoryIds" :disabled="saving" />
          </div>
          <p v-if="saveError" class="notice error" role="alert">{{ saveError }}</p>
          <button class="primary full-width" :disabled="saving || !title.trim()">{{ saving ? 'Cadastrando…' : 'Cadastrar livro' }}</button>
        </fieldset>
      </form>
    </aside>
  </div>
  </div>
</template>

<style scoped>
.book-card-cover-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.search-empty-state {
  text-align: center;
  padding: 2.5rem 1.5rem;
  background-color: var(--bg-surface, var(--card, #fff));
  border-radius: var(--radius, 8px);
  border: 1px dashed var(--border, #ccc);
  margin-top: 1rem;
}

.search-empty-state h2 {
  font-size: 1.15rem;
  margin-bottom: 0.5rem;
}

.search-empty-state p {
  color: var(--muted, #666);
  margin-bottom: 1rem;
}

/* Modo Lista Compacta */
.book-list-compact {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  list-style: none;
  padding: 0;
  margin: 0;
}

.book-list-item {
  border-radius: var(--radius, 8px);
  background-color: var(--bg-surface, var(--card, #fff));
  border: 1px solid var(--border, #e5e5e5);
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.book-list-item:hover {
  transform: translateY(-1px);
  border-color: var(--accent, #3b82f6);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.book-list-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1.25rem;
  text-decoration: none;
  color: inherit;
}

.book-list-cover {
  flex-shrink: 0;
  width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.book-list-info {
  flex: 1 1 auto;
  min-width: 0;
}

.book-list-header {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.book-list-title {
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0;
  color: var(--text, #222);
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-list-year {
  font-size: 0.85rem;
  color: var(--muted, #777);
  font-weight: 400;
}

.book-list-subtitle {
  font-size: 0.85rem;
  color: var(--muted, #666);
  margin: 0.15rem 0 0 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-list-author {
  font-size: 0.88rem;
  color: var(--muted, #666);
  margin: 0.2rem 0 0 0;
}

.book-list-action {
  flex-shrink: 0;
  font-size: 0.88rem;
  color: var(--accent, #3b82f6);
  font-weight: 500;
  margin-left: auto;
  padding-left: 0.5rem;
}

@media (max-width: 640px) {
  .book-list-link {
    padding: 0.65rem 0.85rem;
    gap: 0.75rem;
  }

  .book-list-action {
    display: none;
  }
}
</style>
