<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import TrashConfirmModal from '../components/TrashConfirmModal.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import LoadingSkeleton from '../components/ui/LoadingSkeleton.vue'
import Icon from '../components/ui/Icon.vue'
import { api, errorMessage } from '../services/api'
import type {
  TrashBookItem,
  TrashStudyItem,
  TrashSummary,
  TrashItemType,
  SelectedItemKeyString,
} from '../types'
import {
  toTrashKey,
  parseTrashKey,
  calculateRetention,
} from '../types/trash'

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

// Estado de seleção em lote
const selectedKeys = ref<Set<SelectedItemKeyString>>(new Set())

// Estado do modal de exclusão definitiva de livro individual
const bookToDelete = ref<TrashBookItem | null>(null)
const deletingBook = ref(false)

// Estado do modal de exclusão definitiva de estudo individual
const studyToDelete = ref<TrashStudyItem | null>(null)
const deletingStudy = ref(false)

// Estado do modal de exclusão em lote
const confirmBatchDeleteOpen = ref(false)
const batchDeleting = ref(false)

// Estado do modal de esvaziamento total
const confirmEmptyOpen = ref(false)
const emptyingTrash = ref(false)

// Conjunto de chaves de itens com animação de restauração ativa (saída suave de 180ms)
const restoringKeys = ref<Set<SelectedItemKeyString>>(new Set())
const batchRestoring = ref(false)

const filteredBooks = computed(() => {
  if (activeFilter.value === 'studies') return []
  return trashData.value.books
})

const filteredStudies = computed(() => {
  if (activeFilter.value === 'books') return []
  return trashData.value.studies
})

const totalCount = computed(() => trashData.value.books.length + trashData.value.studies.length)
const selectedCount = computed(() => selectedKeys.value.size)

// Lista de chaves dos itens atualmente visíveis na aba ativa
const visibleKeys = computed<SelectedItemKeyString[]>(() => {
  const keys: SelectedItemKeyString[] = []
  if (activeFilter.value !== 'studies') {
    for (const b of trashData.value.books) {
      keys.push(toTrashKey('book', b.id))
    }
  }
  if (activeFilter.value !== 'books') {
    for (const s of trashData.value.studies) {
      keys.push(toTrashKey('study', s.id))
    }
  }
  return keys
})

const isAllSelected = computed(() => {
  if (visibleKeys.value.length === 0) return false
  return visibleKeys.value.every((k) => selectedKeys.value.has(k))
})

const batchDeleteSummary = computed(() => {
  let books = 0
  let studies = 0
  for (const key of selectedKeys.value) {
    const { type } = parseTrashKey(key)
    if (type === 'book') books++
    else if (type === 'study') studies++
  }
  return { books, studies, total: selectedKeys.value.size }
})

function isSelected(type: TrashItemType, id: number): boolean {
  return selectedKeys.value.has(toTrashKey(type, id))
}

function isRestoring(type: TrashItemType, id: number): boolean {
  return restoringKeys.value.has(toTrashKey(type, id))
}

function toggleSelect(type: TrashItemType, id: number) {
  const key = toTrashKey(type, id)
  const next = new Set(selectedKeys.value)
  if (next.has(key)) {
    next.delete(key)
  } else {
    next.add(key)
  }
  selectedKeys.value = next
}

function toggleSelectAll() {
  const next = new Set(selectedKeys.value)
  if (isAllSelected.value) {
    for (const k of visibleKeys.value) {
      next.delete(k)
    }
  } else {
    for (const k of visibleKeys.value) {
      next.add(k)
    }
  }
  selectedKeys.value = next
}

function clearSelection() {
  selectedKeys.value = new Set()
}

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
  const key = toTrashKey('book', bookItem.id)
  if (restoringKeys.value.has(key)) return

  const nextRestoring = new Set(restoringKeys.value)
  nextRestoring.add(key)
  restoringKeys.value = nextRestoring

  try {
    await api.restoreBook(bookItem.id)
    // Aguarda término da transição de saída de 180ms
    await new Promise((resolve) => setTimeout(resolve, 180))
    setNotice(`Livro “${bookItem.title}” restaurado com sucesso para o acervo ativo!`)
    const nextSelected = new Set(selectedKeys.value)
    nextSelected.delete(key)
    selectedKeys.value = nextSelected
    await loadTrash()
  } catch (err) {
    setNotice(errorMessage(err), 'error')
  } finally {
    const after = new Set(restoringKeys.value)
    after.delete(key)
    restoringKeys.value = after
  }
}

async function handleRestoreStudy(studyItem: TrashStudyItem) {
  const key = toTrashKey('study', studyItem.id)
  if (restoringKeys.value.has(key)) return

  const nextRestoring = new Set(restoringKeys.value)
  nextRestoring.add(key)
  restoringKeys.value = nextRestoring

  try {
    const res = await api.restoreStudy(studyItem.id)
    // Aguarda término da transição de saída de 180ms
    await new Promise((resolve) => setTimeout(resolve, 180))
    if (res.book_restored) {
      setNotice(`Estudo “${studyItem.title}” restaurado! O livro ancestral também foi reativado no acervo ativo.`)
    } else {
      setNotice(`Estudo “${studyItem.title}” restaurado com sucesso!`)
    }
    const nextSelected = new Set(selectedKeys.value)
    nextSelected.delete(key)
    selectedKeys.value = nextSelected
    await loadTrash()
  } catch (err) {
    setNotice(errorMessage(err), 'error')
  } finally {
    const after = new Set(restoringKeys.value)
    after.delete(key)
    restoringKeys.value = after
  }
}

async function handleBatchRestore() {
  if (batchRestoring.value || selectedKeys.value.size === 0) return
  batchRestoring.value = true

  // Marca todos os itens selecionados para animação de saída
  const itemsToRestore = Array.from(selectedKeys.value)
  const nextRestoring = new Set(restoringKeys.value)
  for (const k of itemsToRestore) {
    nextRestoring.add(k)
  }
  restoringKeys.value = nextRestoring

  let restoredCount = 0
  let hadBookAncestralRestored = false
  const errors: string[] = []

  const promises = itemsToRestore.map(async (key) => {
    const { type, id } = parseTrashKey(key)
    try {
      if (type === 'book') {
        await api.restoreBook(id)
        restoredCount++
      } else {
        const res = await api.restoreStudy(id)
        restoredCount++
        if (res.book_restored) hadBookAncestralRestored = true
      }
    } catch (err) {
      errors.push(errorMessage(err))
    }
  })

  await Promise.allSettled(promises)
  await new Promise((resolve) => setTimeout(resolve, 180))

  clearSelection()
  restoringKeys.value = new Set()
  batchRestoring.value = false

  await loadTrash()

  if (errors.length > 0 && restoredCount === 0) {
    setNotice(`Falha ao restaurar itens: ${errors[0]}`, 'error')
  } else if (errors.length > 0) {
    setNotice(`${restoredCount} itens restaurados, mas alguns falharam.`, 'error')
  } else if (hadBookAncestralRestored) {
    setNotice(`${restoredCount} ${restoredCount === 1 ? 'item restaurado' : 'itens restaurados'}! Livros ancestrais também foram reativados.`)
  } else {
    setNotice(`${restoredCount} ${restoredCount === 1 ? 'item restaurado' : 'itens restaurados'} com sucesso para o acervo ativo!`)
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
    const key = toTrashKey('book', bookToDelete.value.id)
    const nextSelected = new Set(selectedKeys.value)
    nextSelected.delete(key)
    selectedKeys.value = nextSelected
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
    const key = toTrashKey('study', studyToDelete.value.id)
    const nextSelected = new Set(selectedKeys.value)
    nextSelected.delete(key)
    selectedKeys.value = nextSelected
    studyToDelete.value = null
    await loadTrash()
  } catch (err) {
    setNotice(errorMessage(err), 'error')
  } finally {
    deletingStudy.value = false
  }
}

async function handleBatchDelete() {
  if (batchDeleting.value || selectedKeys.value.size === 0) return
  batchDeleting.value = true

  const itemsToDelete = Array.from(selectedKeys.value)
  let deletedCount = 0
  const errors: string[] = []

  const promises = itemsToDelete.map(async (key) => {
    const { type, id } = parseTrashKey(key)
    try {
      if (type === 'book') {
        await api.permanentDeleteBook(id)
      } else {
        await api.permanentDeleteStudy(id)
      }
      deletedCount++
    } catch (err) {
      errors.push(errorMessage(err))
    }
  })

  await Promise.allSettled(promises)

  clearSelection()
  batchDeleting.value = false
  confirmBatchDeleteOpen.value = false

  await loadTrash()

  if (errors.length > 0 && deletedCount === 0) {
    setNotice(`Falha ao excluir itens: ${errors[0]}`, 'error')
  } else {
    setNotice(`${deletedCount} ${deletedCount === 1 ? 'item excluído' : 'itens excluídos'} definitivamente.`)
  }
}

async function handleEmptyTrash() {
  if (emptyingTrash.value) return
  emptyingTrash.value = true
  try {
    const res = await api.emptyTrash()
    setNotice(`Lixeira esvaziada com sucesso! (${res.purged_books} livros e ${res.purged_studies} estudos expurgados)`)
    confirmEmptyOpen.value = false
    clearSelection()
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
          <Icon name="trash" :size="16" />
          <span>Esvaziar lixeira</span>
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
            <li
              v-for="book in filteredBooks"
              :key="book.id"
              class="trash-card panel"
              :class="{
                'is-selected': isSelected('book', book.id),
                'is-restoring': isRestoring('book', book.id),
              }"
            >
              <div class="card-left-group">
                <label class="item-checkbox-wrapper" :for="`cb-book-${book.id}`">
                  <input
                    :id="`cb-book-${book.id}`"
                    type="checkbox"
                    class="trash-item-checkbox"
                    :checked="isSelected('book', book.id)"
                    :aria-label="`Selecionar livro ${book.title}`"
                    @change="toggleSelect('book', book.id)"
                  />
                </label>
                <div class="trash-card-info">
                  <div class="badge-row">
                    <span class="type-badge book-badge">Livro</span>
                    <div
                      class="retention-pill"
                      :class="{ 'urgency-urgent': calculateRetention(book.days_until_purge).isUrgent }"
                    >
                      <Icon name="clock" :size="12" class="retention-icon" />
                      <span class="purge-text">{{ calculateRetention(book.days_until_purge).urgencyLabel }}</span>
                      <div
                        class="retention-progress-bar"
                        :style="{ width: `${calculateRetention(book.days_until_purge).elapsedPercentage}%` }"
                      />
                    </div>
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
              </div>

              <div class="trash-card-actions">
                <button
                  type="button"
                  class="primary button-sm"
                  :disabled="isRestoring('book', book.id)"
                  @click="handleRestoreBook(book)"
                >
                  <Icon name="rotate-ccw" :size="14" />
                  <span>{{ isRestoring('book', book.id) ? 'Restaurando…' : 'Restaurar' }}</span>
                </button>
                <button
                  type="button"
                  class="secondary danger-btn button-sm"
                  :disabled="isRestoring('book', book.id)"
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
            <li
              v-for="study in filteredStudies"
              :key="study.id"
              class="trash-card panel"
              :class="{
                'is-selected': isSelected('study', study.id),
                'is-restoring': isRestoring('study', study.id),
              }"
            >
              <div class="card-left-group">
                <label class="item-checkbox-wrapper" :for="`cb-study-${study.id}`">
                  <input
                    :id="`cb-study-${study.id}`"
                    type="checkbox"
                    class="trash-item-checkbox"
                    :checked="isSelected('study', study.id)"
                    :aria-label="`Selecionar estudo ${study.title}`"
                    @change="toggleSelect('study', study.id)"
                  />
                </label>
                <div class="trash-card-info">
                  <div class="badge-row">
                    <span class="type-badge study-badge">Estudo</span>
                    <div
                      class="retention-pill"
                      :class="{ 'urgency-urgent': calculateRetention(study.days_until_purge).isUrgent }"
                    >
                      <Icon name="clock" :size="12" class="retention-icon" />
                      <span class="purge-text">{{ calculateRetention(study.days_until_purge).urgencyLabel }}</span>
                      <div
                        class="retention-progress-bar"
                        :style="{ width: `${calculateRetention(study.days_until_purge).elapsedPercentage}%` }"
                      />
                    </div>
                  </div>
                  <h3 class="trash-card-title">{{ study.title }}</h3>
                  <p class="trash-card-meta study-origin">
                    Origem: <strong>{{ study.book_title }}</strong> &gt; {{ study.chapter_name }}
                  </p>
                  <p class="deleted-date">
                    Descartado em {{ formatDate(study.deleted_at) }}
                  </p>
                </div>
              </div>

              <div class="trash-card-actions">
                <button
                  type="button"
                  class="primary button-sm"
                  :disabled="isRestoring('study', study.id)"
                  @click="handleRestoreStudy(study)"
                >
                  <Icon name="rotate-ccw" :size="14" />
                  <span>{{ isRestoring('study', study.id) ? 'Restaurando…' : 'Restaurar' }}</span>
                </button>
                <button
                  type="button"
                  class="secondary danger-btn button-sm"
                  :disabled="isRestoring('study', study.id)"
                  @click="confirmPermanentDeleteStudy(study)"
                >
                  Excluir definitivamente
                </button>
              </div>
            </li>
          </ul>
        </section>
      </div>

      <!-- Barra Flutuante de Ações em Lote -->
      <aside
        v-if="selectedCount > 0"
        class="trash-batch-bar"
        role="region"
        aria-label="Ações em lote da lixeira"
      >
        <div class="batch-bar-content">
          <div class="batch-bar-info">
            <span class="batch-count">
              <strong>{{ selectedCount }}</strong>
              {{ selectedCount === 1 ? 'item selecionado' : 'itens selecionados' }}
            </span>
          </div>
          <div class="batch-bar-actions">
            <button
              type="button"
              class="batch-btn secondary"
              @click="toggleSelectAll"
            >
              {{ isAllSelected ? 'Desmarcar todos' : 'Selecionar todos' }}
            </button>
            <button
              type="button"
              class="batch-btn primary"
              :disabled="batchRestoring || batchDeleting"
              @click="handleBatchRestore"
            >
              <Icon name="rotate-ccw" :size="14" />
              <span>{{ batchRestoring ? 'Restaurando...' : 'Restaurar selecionados' }}</span>
            </button>
            <button
              type="button"
              class="batch-btn danger"
              :disabled="batchRestoring || batchDeleting"
              @click="confirmBatchDeleteOpen = true"
            >
              <Icon name="trash" :size="14" />
              <span>Excluir definitivamente</span>
            </button>
            <button
              type="button"
              class="batch-close-btn"
              aria-label="Limpar seleção"
              @click="clearSelection"
            >
              <Icon name="x" :size="16" />
            </button>
          </div>
        </div>
      </aside>
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

    <!-- Modal Exclusão Definitiva em Lote -->
    <TrashConfirmModal
      :open="confirmBatchDeleteOpen"
      title="Excluir itens selecionados definitivamente?"
      :message="`Tem certeza de que deseja excluir permanentemente ${batchDeleteSummary.books} livro(s) e ${batchDeleteSummary.studies} estudo(s) selecionado(s)? Esta ação é permanente e irreversível.`"
      confirm-label="Excluir selecionados agora"
      :danger="true"
      :loading="batchDeleting"
      @close="confirmBatchDeleteOpen = false"
      @confirm="handleBatchDelete"
    />

    <!-- Modal Esvaziar Lixeira -->
    <TrashConfirmModal
      :open="confirmEmptyOpen"
      title="Esvaziar toda a lixeira?"
      :message="`Tem certeza de que deseja esvaziar a lixeira agora? Serão destruídos permanentemente ${trashData.books.length} livro(s) e ${trashData.studies.length} estudo(s) atualmente na custódia. Esta ação é irreversível.`"
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
  padding-bottom: calc(var(--space-unit) * 6);
  position: relative;
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
  transition: transform 180ms ease-out, opacity 180ms ease-out, border-color 0.15s ease, background-color 0.15s ease;
}

.trash-card.is-selected {
  border-color: var(--color-primary, #2563eb);
  background: var(--color-surface-soft, rgba(37, 99, 235, 0.04));
}

.trash-card.is-restoring {
  transform: translateY(-20px);
  opacity: 0;
  pointer-events: none;
}

.card-left-group {
  display: flex;
  align-items: center;
  gap: calc(var(--space-unit) * 1);
  flex: 1 1 auto;
  min-width: 0;
}

.item-checkbox-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  cursor: pointer;
  flex-shrink: 0;
}

.trash-item-checkbox {
  width: 1.15rem;
  height: 1.15rem;
  cursor: pointer;
  accent-color: var(--color-primary, #2563eb);
}

.trash-card-info {
  flex: 1 1 auto;
  min-width: 0;
}

.badge-row {
  display: flex;
  align-items: center;
  gap: calc(var(--space-unit) * 0.75);
  margin-bottom: calc(var(--space-unit) * 0.35);
  flex-wrap: wrap;
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
  background: var(--color-surface-soft, #e0e7ff);
  color: var(--color-primary, #3730a3);
  border: 1px solid var(--color-border);
}

.study-badge {
  background: var(--color-surface-soft, #fef3c7);
  color: var(--color-text, #92400e);
  border: 1px solid var(--color-border);
}

.retention-pill {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  overflow: hidden;
}

.retention-pill.urgency-urgent {
  border-color: var(--color-danger, #e53e3e);
  color: var(--color-danger, #e53e3e);
  font-weight: 600;
  background: var(--color-danger-subtle, rgba(229, 62, 62, 0.08));
}

.retention-progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  background: var(--color-border);
  transition: width 0.3s ease;
}

.urgency-urgent .retention-progress-bar {
  background: var(--color-danger, #e53e3e);
}

.retention-icon {
  flex-shrink: 0;
}

.trash-card-title {
  font-size: 1.125rem;
  margin: 0 0 calc(var(--space-unit) * 0.25);
  color: var(--color-text);
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
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.danger-btn {
  color: var(--color-danger, #b91c1c);
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.danger-btn:hover:not(:disabled) {
  background: var(--color-surface-hover);
  border-color: var(--color-danger, #b91c1c);
}

/* Barra Flutuante de Ações em Lote */
.trash-batch-bar {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  max-width: 90vw;
  width: auto;
  border-radius: 9999px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  padding: 0.5rem 1rem;
  animation: slideUp 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideUp {
  from {
    transform: translate(-50%, 40px);
    opacity: 0;
  }
  to {
    transform: translate(-50%, 0);
    opacity: 1;
  }
}

.batch-bar-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.batch-bar-info {
  display: flex;
  align-items: center;
  white-space: nowrap;
}

.batch-count {
  font-size: 0.875rem;
  color: var(--color-text);
}

.batch-bar-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.batch-btn {
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border: 1px solid var(--color-border);
  min-height: 38px;
}

.batch-btn.secondary {
  background: var(--color-surface);
  color: var(--color-text);
}

.batch-btn.secondary:hover:not(:disabled) {
  background: var(--color-surface-hover);
}

.batch-btn.primary {
  background: var(--color-primary, #2563eb);
  color: #fff;
  border-color: transparent;
}

.batch-btn.primary:hover:not(:disabled) {
  opacity: 0.92;
}

.batch-btn.danger {
  background: var(--color-danger, #dc2626);
  color: #fff;
  border-color: transparent;
}

.batch-btn.danger:hover:not(:disabled) {
  opacity: 0.92;
}

.batch-close-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.35rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  border-radius: 50%;
  min-width: 38px;
  min-height: 38px;
}

.batch-close-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

@media (max-width: 640px) {
  .trash-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-left-group {
    width: 100%;
  }

  .trash-card-actions {
    width: 100%;
    justify-content: flex-end;
    margin-top: calc(var(--space-unit) * 0.5);
    padding-left: 44px;
  }

  .trash-batch-bar {
    border-radius: var(--radius-small);
    width: 95vw;
    bottom: 1rem;
    padding: 0.75rem;
  }

  .batch-bar-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .batch-bar-actions {
    width: 100%;
    flex-wrap: wrap;
    justify-content: space-between;
  }
}
</style>
