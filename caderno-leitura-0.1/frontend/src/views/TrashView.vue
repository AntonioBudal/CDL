<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import TrashConfirmModal from '../components/TrashConfirmModal.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import LoadingSkeleton from '../components/ui/LoadingSkeleton.vue'
import { api, errorMessage } from '../services/api'
import type { TrashBookItem, TrashStudyItem, TrashSummary } from '../types'

type FilterType = 'all' | 'books' | 'studies'

const loading = ref(true)
const loadError = ref('')
const trashData = ref<TrashSummary>({
  books: [],
  studies: [],
  total_items: 0,
})

const activeFilter = ref<FilterType>('all')
const actionNotice = ref('')
const actionNoticeType = ref<'success' | 'error'>('success')

// Estado do modal de exclusão definitiva de livro
const bookToDelete = ref<TrashBookItem | null>(null)
const deletingBook = ref(false)

// Estado do modal de exclusão definitiva de estudo
const studyToDelete = ref<TrashStudyItem | null>(null)
const deletingStudy = ref(false)

// Estado do modal de esvaziamento total
const confirmEmptyOpen = ref(false)
const emptyingTrash = ref(false)

// Estado de restauração em andamento
const restoringItemId = ref<number | null>(null)

const filteredBooks = computed(() => {
  if (activeFilter.value === 'studies') return []
  return trashData.value.books
})

const filteredStudies = computed(() => {
  if (activeFilter.value === 'books') return []
  return trashData.value.studies
})

const totalCount = computed(() => trashData.value.books.length + trashData.value.studies.length)

async function loadTrash() {
  loading.value = true
  loadError.value = ''
  try {
    const data = await api.getTrash()
    trashData.value = data
  } catch (err) {
    loadError.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}

function setNotice(message: string, type: 'success' | 'error' = 'success') {
  actionNotice.value = message
  actionNoticeType.value = type
  setTimeout(() => {
    if (actionNotice.value === message) {
      actionNotice.value = ''
    }
  }, 6000)
}

async function handleRestoreBook(bookItem: TrashBookItem) {
  if (restoringItemId.value !== null) return
  restoringItemId.value = bookItem.id
  try {
    await api.restoreBook(bookItem.id)
    setNotice(`Livro “${bookItem.title}” restaurado com sucesso para o acervo ativo!`)
    await loadTrash()
  } catch (err) {
    setNotice(errorMessage(err), 'error')
  } finally {
    restoringItemId.value = null
  }
}

async function handleRestoreStudy(studyItem: TrashStudyItem) {
  if (restoringItemId.value !== null) return
  restoringItemId.value = studyItem.id
  try {
    const res = await api.restoreStudy(studyItem.id)
    if (res.book_restored) {
      setNotice(`Estudo “${studyItem.title}” restaurado! O livro ancestral também foi reativado no acervo ativo.`)
    } else {
      setNotice(`Estudo “${studyItem.title}” restaurado com sucesso!`)
    }
    await loadTrash()
  } catch (err) {
    setNotice(errorMessage(err), 'error')
  } finally {
    restoringItemId.value = null
  }
}

function confirmPermanentDeleteBook(bookItem: TrashBookItem) {
  bookToDelete.value = bookItem
}

async function handlePermanentDeleteBook() {
  if (!bookToDelete.value || deletingBook.value) return
  deletingBook.value = true
  try {
    await api.permanentDeleteBook(bookToDelete.value.id)
    setNotice(`Livro “${bookToDelete.value.title}” excluído definitivamente.`)
    bookToDelete.value = null
    await loadTrash()
  } catch (err) {
    setNotice(errorMessage(err), 'error')
  } finally {
    deletingBook.value = false
  }
}

function confirmPermanentDeleteStudy(studyItem: TrashStudyItem) {
  studyToDelete.value = studyItem
}

async function handlePermanentDeleteStudy() {
  if (!studyToDelete.value || deletingStudy.value) return
  deletingStudy.value = true
  try {
    await api.permanentDeleteStudy(studyToDelete.value.id)
    setNotice(`Estudo “${studyToDelete.value.title}” excluído definitivamente.`)
    studyToDelete.value = null
    await loadTrash()
  } catch (err) {
    setNotice(errorMessage(err), 'error')
  } finally {
    deletingStudy.value = false
  }
}

async function handleEmptyTrash() {
  if (emptyingTrash.value) return
  emptyingTrash.value = true
  try {
    const res = await api.emptyTrash()
    setNotice(`Lixeira esvaziada com sucesso! (${res.purged_books} livros e ${res.purged_studies} estudos expurgados)`)
    confirmEmptyOpen.value = false
    await loadTrash()
  } catch (err) {
    setNotice(errorMessage(err), 'error')
  } finally {
    emptyingTrash.value = false
  }
}

function formatDate(dateStr: string) {
  try {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return dateStr
  }
}

onMounted(loadTrash)
</script>

<template>
  <div class="trash-container wrap">
    <header class="page-header trash-header">
      <div class="title-area">
        <p class="eyebrow">Gerenciamento de Acervo</p>
        <h1>Lixeira</h1>
        <p class="intro">
          Itens descartados são mantidos por até 30 dias antes do expurgo automático permanente.
        </p>
      </div>
      <div v-if="totalCount > 0" class="header-actions">
        <button
          type="button"
          class="secondary danger-btn"
          :disabled="loading"
          @click="confirmEmptyOpen = true"
        >
          Esvaziar lixeira
        </button>
      </div>
    </header>

    <div
      v-if="actionNotice"
      class="notice"
      :class="actionNoticeType === 'error' ? 'error' : 'success'"
      role="status"
    >
      <p>{{ actionNotice }}</p>
    </div>

    <div v-if="loading" class="trash-loading-skeleton" role="status" aria-label="Carregando itens da lixeira">
      <LoadingSkeleton shape="rect" height="40px" style="margin-bottom: 20px;" />
      <LoadingSkeleton shape="rect" height="80px" style="margin-bottom: 12px;" />
      <LoadingSkeleton shape="rect" height="80px" style="margin-bottom: 12px;" />
    </div>

    <div v-else-if="loadError" class="notice error" role="alert">
      <h2>Não foi possível carregar a lixeira.</h2>
      <p>{{ loadError }}</p>
      <button class="secondary" type="button" @click="loadTrash">Tentar novamente</button>
    </div>

    <template v-else>
      <EmptyState
        v-if="totalCount === 0"
        icon="trash"
        title="A lixeira está vazia."
        description="Nenhum livro ou estudo foi descartado. Livros e anotações descartados aparecerão aqui com opção de restauração."
      >
        <RouterLink to="/" class="button primary">Voltar aos meus livros</RouterLink>
      </EmptyState>

      <div v-else class="trash-content">
        <div class="filters-bar" role="tablist" aria-label="Filtros da lixeira">
          <button
            type="button"
            class="filter-tab"
            :class="{ active: activeFilter === 'all' }"
            role="tab"
            :aria-selected="activeFilter === 'all'"
            @click="activeFilter = 'all'"
          >
            Todos ({{ totalCount }})
          </button>
          <button
            type="button"
            class="filter-tab"
            :class="{ active: activeFilter === 'books' }"
            role="tab"
            :aria-selected="activeFilter === 'books'"
            @click="activeFilter = 'books'"
          >
            Livros ({{ trashData.books.length }})
          </button>
          <button
            type="button"
            class="filter-tab"
            :class="{ active: activeFilter === 'studies' }"
            role="tab"
            :aria-selected="activeFilter === 'studies'"
            @click="activeFilter = 'studies'"
          >
            Estudos individuais ({{ trashData.studies.length }})
          </button>
        </div>

        <!-- Seção de Livros -->
        <section
          v-if="filteredBooks.length > 0"
          class="trash-section"
          aria-labelledby="trash-books-heading"
        >
          <h2 id="trash-books-heading" class="section-title">
            Livros na Lixeira ({{ filteredBooks.length }})
          </h2>
          <ul class="trash-list">
            <li v-for="book in filteredBooks" :key="book.id" class="trash-card panel">
              <div class="trash-card-info">
                <div class="badge-row">
                  <span class="type-badge book-badge">Livro</span>
                  <span
                    class="purge-badge"
                    :class="{ 'purge-urgent': book.days_until_purge <= 5 }"
                  >
                    Expurgo em {{ book.days_until_purge }} {{ book.days_until_purge === 1 ? 'dia' : 'dias' }}
                  </span>
                </div>
                <h3 class="trash-card-title">{{ book.title }}</h3>
                <p class="trash-card-meta">
                  {{ book.author || 'Autor não informado' }} ·
                  {{ book.chapters_count }} {{ book.chapters_count === 1 ? 'capítulo' : 'capítulos' }} ·
                  {{ book.studies_count }} {{ book.studies_count === 1 ? 'estudo' : 'estudos' }}
                </p>
                <p class="deleted-date">
                  Descartado em {{ formatDate(book.deleted_at) }}
                </p>
              </div>

              <div class="trash-card-actions">
                <button
                  type="button"
                  class="primary button-sm"
                  :disabled="restoringItemId === book.id"
                  @click="handleRestoreBook(book)"
                >
                  {{ restoringItemId === book.id ? 'Restaurando…' : 'Restaurar' }}
                </button>
                <button
                  type="button"
                  class="secondary danger-btn button-sm"
                  :disabled="restoringItemId === book.id"
                  @click="confirmPermanentDeleteBook(book)"
                >
                  Excluir definitivamente
                </button>
              </div>
            </li>
          </ul>
        </section>

        <!-- Seção de Estudos -->
        <section
          v-if="filteredStudies.length > 0"
          class="trash-section"
          aria-labelledby="trash-studies-heading"
        >
          <h2 id="trash-studies-heading" class="section-title">
            Estudos Individuais na Lixeira ({{ filteredStudies.length }})
          </h2>
          <ul class="trash-list">
            <li v-for="study in filteredStudies" :key="study.id" class="trash-card panel">
              <div class="trash-card-info">
                <div class="badge-row">
                  <span class="type-badge study-badge">Estudo</span>
                  <span
                    class="purge-badge"
                    :class="{ 'purge-urgent': study.days_until_purge <= 5 }"
                  >
                    Expurgo em {{ study.days_until_purge }} {{ study.days_until_purge === 1 ? 'dia' : 'dias' }}
                  </span>
                </div>
                <h3 class="trash-card-title">{{ study.title }}</h3>
                <p class="trash-card-meta">
                  Origem: <strong>{{ study.book_title }}</strong> &gt; {{ study.chapter_name }}
                </p>
                <p class="deleted-date">
                  Descartado em {{ formatDate(study.deleted_at) }}
                </p>
              </div>

              <div class="trash-card-actions">
                <button
                  type="button"
                  class="primary button-sm"
                  :disabled="restoringItemId === study.id"
                  @click="handleRestoreStudy(study)"
                >
                  {{ restoringItemId === study.id ? 'Restaurando…' : 'Restaurar' }}
                </button>
                <button
                  type="button"
                  class="secondary danger-btn button-sm"
                  :disabled="restoringItemId === study.id"
                  @click="confirmPermanentDeleteStudy(study)"
                >
                  Excluir definitivamente
                </button>
              </div>
            </li>
          </ul>
        </section>
      </div>
    </template>

    <!-- Modal Exclusão Definitiva de Livro -->
    <TrashConfirmModal
      v-if="bookToDelete"
      :open="!!bookToDelete"
      title="Excluir livro definitivamente?"
      :message="`Tem certeza de que deseja excluir permanentemente o livro “${bookToDelete.title}”? Todos os seus capítulos e estudos subordinados serão apagados de forma irreversível.`"
      confirm-label="Excluir definitivamente"
      :danger="true"
      :loading="deletingBook"
      @close="bookToDelete = null"
      @confirm="handlePermanentDeleteBook"
    />

    <!-- Modal Exclusão Definitiva de Estudo -->
    <TrashConfirmModal
      v-if="studyToDelete"
      :open="!!studyToDelete"
      title="Excluir estudo definitivamente?"
      :message="`Tem certeza de que deseja excluir permanentemente o estudo “${studyToDelete.title}”? Esta ação é permanente e irreversível.`"
      confirm-label="Excluir definitivamente"
      :danger="true"
      :loading="deletingStudy"
      @close="studyToDelete = null"
      @confirm="handlePermanentDeleteStudy"
    />

    <!-- Modal Esvaziar Lixeira -->
    <TrashConfirmModal
      :open="confirmEmptyOpen"
      title="Esvaziar toda a lixeira?"
      message="Tem certeza de que deseja esvaziar a lixeira agora? Todos os livros e estudos atualmente na lixeira serão permanentemente destruídos do banco de dados. Esta ação é irreversível."
      confirm-label="Esvaziar lixeira agora"
      :danger="true"
      :loading="emptyingTrash"
      @close="confirmEmptyOpen = false"
      @confirm="handleEmptyTrash"
    />
  </div>
</template>

<style scoped>
.trash-container {
  padding-bottom: calc(var(--space-unit) * 3);
}

.trash-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: calc(var(--space-unit) * 1.5);
  margin-bottom: calc(var(--space-unit) * 1.5);
}

.title-area {
  flex: 1 1 auto;
}

.header-actions {
  flex-shrink: 0;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: calc(var(--space-unit) * 0.75);
}

.filters-bar {
  display: flex;
  gap: calc(var(--space-unit) * 0.5);
  margin-bottom: calc(var(--space-unit) * 1.5);
  border-bottom: var(--border-width) solid var(--color-border);
  padding-bottom: calc(var(--space-unit) * 0.5);
}

.filter-tab {
  background: transparent;
  border: none;
  padding: calc(var(--space-unit) * 0.5) calc(var(--space-unit) * 1);
  border-radius: var(--radius-control);
  cursor: pointer;
  font-weight: 500;
  color: var(--color-muted);
  transition: all 0.15s ease;
}

.filter-tab:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.filter-tab.active {
  color: var(--color-primary, #0f172a);
  background: var(--color-surface-soft);
  font-weight: 600;
}

.trash-section {
  margin-bottom: calc(var(--space-unit) * 2);
}

.section-title {
  font-size: 1.125rem;
  margin-bottom: calc(var(--space-unit) * 0.75);
  color: var(--color-text);
}

.trash-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 0.75);
}

.trash-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: calc(var(--space-unit) * 1.5);
  padding: calc(var(--space-unit) * 1.25);
  border-radius: var(--radius-small);
  border: var(--border-width) solid var(--color-border);
  background: var(--color-surface);
}

.trash-card-info {
  flex: 1 1 auto;
  min-width: 0;
}

.badge-row {
  display: flex;
  align-items: center;
  gap: calc(var(--space-unit) * 0.5);
  margin-bottom: calc(var(--space-unit) * 0.35);
}

.type-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-control);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.book-badge {
  background: #e0e7ff;
  color: #3730a3;
}

.study-badge {
  background: #fef3c7;
  color: #92400e;
}

.purge-badge {
  font-size: 0.75rem;
  color: var(--color-muted);
}

.purge-urgent {
  color: #dc2626;
  font-weight: 600;
}

.trash-card-title {
  font-size: 1.125rem;
  margin: 0 0 calc(var(--space-unit) * 0.25);
}

.trash-card-meta {
  font-size: 0.875rem;
  color: var(--color-muted);
  margin: 0 0 calc(var(--space-unit) * 0.25);
}

.deleted-date {
  font-size: 0.75rem;
  color: var(--color-muted);
  margin: 0;
}

.trash-card-actions {
  display: flex;
  align-items: center;
  gap: calc(var(--space-unit) * 0.5);
  flex-shrink: 0;
}

.button-sm {
  min-height: 2.25rem;
  padding: calc(var(--space-unit) * 0.35) calc(var(--space-unit) * 0.75);
  font-size: 0.875rem;
}

.danger-btn {
  color: var(--color-danger, #b91c1c);
}

.danger-btn:hover:not(:disabled) {
  background: var(--color-surface-hover);
  border-color: var(--color-danger, #b91c1c);
}

@media (max-width: 640px) {
  .trash-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .trash-card-actions {
    width: 100%;
    justify-content: flex-end;
    margin-top: calc(var(--space-unit) * 0.5);
  }
}
</style>
