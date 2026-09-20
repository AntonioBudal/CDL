<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import BookCover from '../components/BookCover.vue'
import BookEditModal from '../components/BookEditModal.vue'
import CategoryBadge from '../components/CategoryBadge.vue'
import ExportModal from '../components/ExportModal.vue'
import TrashConfirmModal from '../components/TrashConfirmModal.vue'
import SplitLayout from '../components/layout/SplitLayout.vue'
import Icon from '../components/ui/Icon.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import LoadingSkeleton from '../components/ui/LoadingSkeleton.vue'
import { api, errorMessage } from '../services/api'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import { positiveId, type Book, type Chapter, type StudySummary, type StudyViewMode } from '../types'
import ViewSwitcher from '../components/views/ViewSwitcher.vue'
import StudyGridView from '../components/views/StudyGridView.vue'
import StudyListView from '../components/views/StudyListView.vue'
import StudyTreeView from '../components/views/StudyTreeView.vue'
import StudyMapView from '../components/views/StudyMapView.vue'
import StudyCanvasView from '../components/views/StudyCanvasView.vue'
import { useViewPreference, loadStoredViewPreference } from '../composables/useViewPreference.ts'

const splitLayoutRef = ref<InstanceType<typeof SplitLayout> | null>(null)

const route = useRoute()
const router = useRouter()
const book = ref<Book | null>(null)
const exportModalOpen = ref(false)
const chapters = ref<Chapter[]>([])
const studies = ref<StudySummary[]>([])
const loading = ref(true)
const loadError = ref('')
const studiesLoading = ref(false)
const studiesError = ref('')
const chapterName = ref('')
const chapterError = ref('')
const creatingChapter = ref(false)
const isEditingBook = ref(false)
const editingChapterId = ref<number | null>(null)
const editChapterName = ref('')
const editChapterError = ref('')
const savingChapterName = ref(false)
const movingChapter = ref(false)
const bookId = computed(() => positiveId(route.params.bookId))

const confirmTrashBookOpen = ref(false)
const trashingBook = ref(false)
const trashBookError = ref('')

const confirmTrashStudyOpen = ref(false)
const studyToTrash = ref<StudySummary | null>(null)
const trashingStudy = ref(false)
const trashStudyError = ref('')

const selectedChapter = computed(() => route.query.chapter == null
  ? chapters.value[0] ?? null
  : chapters.value.find(chapter => chapter.id === positiveId(route.query.chapter)) ?? null)
let bookRequest: AbortController | null = null
let studyRequest: AbortController | null = null
let disposed = false

useUnsavedChanges(
  () => !!chapterName.value || (editingChapterId.value !== null && editChapterName.value !== (chapters.value.find(c => c.id === editingChapterId.value)?.name ?? '')),
  () => creatingChapter.value || savingChapterName.value || movingChapter.value,
)

async function loadBook() {
  bookRequest?.abort()
  const controller = new AbortController()
  bookRequest = controller
  loading.value = true
  loadError.value = ''
  book.value = null
  chapters.value = []
  chapterName.value = ''
  chapterError.value = ''
  const id = bookId.value
  if (id === null) { loadError.value = 'Livro não encontrado.'; loading.value = false; return }
  try {
    const [allBooks, result] = await Promise.all([api.listBooks(controller.signal), api.listChapters(id, controller.signal)])
    if (controller.signal.aborted) return
    book.value = allBooks.find(item => item.id === id) ?? null
    if (book.value === null) { loadError.value = 'Livro não encontrado.'; return }
    chapters.value = result
  } catch (error) {
    if (!controller.signal.aborted) loadError.value = errorMessage(error)
  } finally {
    if (!controller.signal.aborted) loading.value = false
  }
}

async function loadStudies() {
  studyRequest?.abort()
  const controller = new AbortController()
  studyRequest = controller
  studies.value = []
  studiesError.value = ''
  const chapter = selectedChapter.value
  studiesLoading.value = chapter !== null
  if (!chapter) return
  try {
    const result = await api.listStudies(chapter.id, controller.signal)
    if (!controller.signal.aborted) studies.value = result
  } catch (error) {
    if (!controller.signal.aborted) studiesError.value = errorMessage(error)
  } finally {
    if (!controller.signal.aborted) studiesLoading.value = false
  }
}

async function createChapter() {
  const id = bookId.value
  if (creatingChapter.value || id === null || !chapterName.value.trim()) return
  creatingChapter.value = true
  chapterError.value = ''
  try {
    const chapter = await api.createChapter(id, chapterName.value)
    if (disposed || bookId.value !== id) return
    chapters.value.push(chapter)
    chapterName.value = ''
    await router.replace({ name: 'book', params: { bookId: id }, query: { chapter: chapter.id } })
  } catch (error) {
    if (!disposed && bookId.value === id) chapterError.value = errorMessage(error)
  } finally { creatingChapter.value = false }
}

function startEditChapter(ch: Chapter) {
  editingChapterId.value = ch.id
  editChapterName.value = ch.name
  editChapterError.value = ''
}

function cancelEditChapter() {
  editingChapterId.value = null
  editChapterName.value = ''
  editChapterError.value = ''
}

async function saveChapter(ch: Chapter) {
  const id = bookId.value
  const trimmed = editChapterName.value.trim()
  if (!trimmed || id === null || savingChapterName.value) return
  savingChapterName.value = true
  editChapterError.value = ''
  try {
    const updated = await api.updateChapter(id, ch.id, {
      name: trimmed,
      expected_updated_at: ch.updated_at ?? null,
    })
    const index = chapters.value.findIndex(c => c.id === ch.id)
    if (index !== -1) {
      chapters.value[index] = updated
    }
    editingChapterId.value = null
  } catch (error) {
    editChapterError.value = errorMessage(error)
  } finally {
    savingChapterName.value = false
  }
}

async function moveChapter(chapterId: number, direction: 'up' | 'down') {
  const id = bookId.value
  if (id === null || movingChapter.value) return
  movingChapter.value = true
  chapterError.value = ''
  try {
    const reordered = await api.moveChapter(id, chapterId, direction)
    chapters.value = reordered
  } catch (error) {
    chapterError.value = errorMessage(error)
  } finally {
    movingChapter.value = false
  }
}

function onBookSaved(updatedBook: Book) {
  book.value = updatedBook
}

async function handleTrashBook() {
  if (!book.value || trashingBook.value) return
  trashingBook.value = true
  trashBookError.value = ''
  try {
    await api.trashBook(book.value.id)
    confirmTrashBookOpen.value = false
    await router.push({ name: 'home' })
  } catch (error) {
    trashBookError.value = errorMessage(error)
  } finally {
    trashingBook.value = false
  }
}

function confirmTrashStudy(study: StudySummary) {
  studyToTrash.value = study
  trashStudyError.value = ''
  confirmTrashStudyOpen.value = true
}

async function handleTrashStudy() {
  if (!studyToTrash.value || trashingStudy.value) return
  trashingStudy.value = true
  trashStudyError.value = ''
  try {
    await api.trashStudy(studyToTrash.value.id)
    confirmTrashStudyOpen.value = false
    studyToTrash.value = null
    await loadStudies()
  } catch (error) {
    trashStudyError.value = errorMessage(error)
  } finally {
    trashingStudy.value = false
  }
}

const {
  currentMode: activeViewMode,
  activeStudyId,
  availableModes: viewOptions,
  setMode: setViewMode,
  setActiveStudy
} = useViewPreference({
  bookId: bookId.value
})

const viewRenderers: Record<StudyViewMode, any> = {
  grid: StudyGridView,
  list: StudyListView,
  tree: StudyTreeView,
  map: StudyMapView,
  canvas: StudyCanvasView
}

const activeRendererComponent = computed(() => viewRenderers[activeViewMode.value] ?? StudyGridView)

const activeStudy = computed(() => {
  if (!activeStudyId.value) return null
  return studies.value.find(s => s.id === activeStudyId.value) ?? null
})

watch(bookId, (newId) => {
  if (newId) {
    const stored = loadStoredViewPreference(newId)
    if (stored) {
      activeViewMode.value = stored
    }
  }
  loadBook()
}, { immediate: true })
watch(() => selectedChapter.value?.id, loadStudies, { immediate: true })
onBeforeUnmount(() => { disposed = true; bookRequest?.abort(); studyRequest?.abort() })
</script>

<template>
  <div class="book-view">
    <nav class="breadcrumb" aria-label="Caminho"><RouterLink to="/">Meus livros</RouterLink><span aria-hidden="true">/</span><span>Livro</span></nav>
  <div v-if="loading" class="book-loading-skeleton" role="status" aria-label="Carregando livro">
    <div style="display: flex; gap: 24px; margin-bottom: 32px; align-items: flex-start;">
      <LoadingSkeleton shape="rect" width="160px" height="240px" />
      <div style="flex: 1; display: flex; flex-direction: column; gap: 12px;">
        <LoadingSkeleton shape="text" width="25%" height="16px" />
        <LoadingSkeleton shape="text" width="60%" height="36px" />
        <LoadingSkeleton shape="text" width="40%" height="20px" />
      </div>
    </div>
  </div>
  <div v-else-if="loadError" class="notice error" role="alert">
    <h1>Não foi possível abrir o livro.</h1>
    <p>{{ loadError }}</p>
    <button class="secondary" type="button" @click="loadBook">Tentar novamente</button>
  </div>
  <template v-else-if="book">
    <header class="page-header wrap book-header">
      <div class="book-header-main">
        <div class="book-header-cover">
          <BookCover :cover-image="book.cover_image" :title="book.title" :author="book.author" size="md" />
        </div>
        <div class="book-info">
          <p class="eyebrow">Livro</p>
          <h1>{{ book.title }}</h1>
          <p v-if="book.subtitle" class="book-subtitle">{{ book.subtitle }}</p>
          <p class="intro">
            {{ book.author || 'Autor não informado' }}
            <span v-if="book.year"> · {{ book.year }}</span>
          </p>
          <div v-if="book.categories && book.categories.length > 0" class="flex flex-wrap gap-1.5 mt-2.5">
            <CategoryBadge
              v-for="cat in book.categories"
              :key="cat.id"
              :category="cat"
              size="sm"
            />
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button
          class="secondary icon-toggle-btn"
          type="button"
          :title="splitLayoutRef?.leftCollapsed ? 'Expandir capítulos' : 'Recolher capítulos'"
          :aria-label="splitLayoutRef?.leftCollapsed ? 'Expandir capítulos' : 'Recolher capítulos'"
          @click="splitLayoutRef?.toggleCollapse('left')"
        >
          <Icon name="list" :size="16" />
        </button>
        <button
          class="secondary icon-toggle-btn"
          type="button"
          :title="splitLayoutRef?.rightCollapsed ? 'Exibir contexto' : 'Recolher contexto'"
          :aria-label="splitLayoutRef?.rightCollapsed ? 'Exibir contexto' : 'Recolher contexto'"
          @click="splitLayoutRef?.toggleCollapse('right')"
        >
          <Icon name="sliders" :size="16" />
        </button>
        <button class="secondary" type="button" @click="exportModalOpen = true">Exportar anotações</button>
        <button class="secondary" type="button" @click="isEditingBook = true">Editar livro</button>
        <button class="secondary danger-action" type="button" @click="confirmTrashBookOpen = true">Mover para a lixeira</button>
      </div>
    </header>

    <SplitLayout
      ref="splitLayoutRef"
      :book-id="book.id"
      :has-right-pane="true"
      class="book-split-layout wrap"
    >
      <!-- Painel Esquerdo: Navegador de Capítulos -->
      <template #left>
        <aside class="panel chapter-sidebar h-full" aria-labelledby="chapters-heading">
          <div class="section-heading">
            <h2 id="chapters-heading">Capítulos</h2>
            <span class="count">{{ chapters.length }}</span>
          </div>
          <nav v-if="chapters.length" aria-label="Capítulos do livro">
            <ul class="chapter-list">
              <li v-for="(chapter, idx) in chapters" :key="chapter.id" class="chapter-item">
                <div v-if="editingChapterId === chapter.id" class="chapter-edit-box">
                  <form @submit.prevent="saveChapter(chapter)">
                    <div class="field">
                      <input
                        v-model="editChapterName"
                        required
                        placeholder="Nome do capítulo"
                        :disabled="savingChapterName"
                        @keydown.esc="cancelEditChapter"
                      />
                    </div>
                    <p v-if="editChapterError" class="notice error" role="alert">{{ editChapterError }}</p>
                    <div class="actions">
                      <button type="submit" class="primary button-sm" :disabled="savingChapterName || !editChapterName.trim()">
                        {{ savingChapterName ? 'Salvando…' : 'Salvar' }}
                      </button>
                      <button type="button" class="secondary button-sm" :disabled="savingChapterName" @click="cancelEditChapter">
                        Cancelar
                      </button>
                    </div>
                  </form>
                </div>
                <div v-else class="chapter-row">
                  <RouterLink :to="{ name: 'book', params: { bookId: book.id }, query: { chapter: chapter.id } }"
                    :class="{ selected: selectedChapter?.id === chapter.id }" :aria-current="selectedChapter?.id === chapter.id ? 'page' : undefined">
                    {{ chapter.name }}
                  </RouterLink>
                  <div class="chapter-actions">
                    <button
                      type="button"
                      class="action-btn"
                      :disabled="idx === 0 || movingChapter"
                      title="Mover para cima"
                      aria-label="Mover para cima"
                      @click.prevent="moveChapter(chapter.id, 'up')"
                    >▲</button>
                    <button
                      type="button"
                      class="action-btn"
                      :disabled="idx === chapters.length - 1 || movingChapter"
                      title="Mover para baixo"
                      aria-label="Mover para baixo"
                      @click.prevent="moveChapter(chapter.id, 'down')"
                    >▼</button>
                    <button
                      type="button"
                      class="action-btn"
                      title="Renomear capítulo"
                      aria-label="Renomear capítulo"
                      @click.prevent="startEditChapter(chapter)"
                    ><Icon name="pencil" :size="13" /></button>
                  </div>
                </div>
              </li>
            </ul>
          </nav>
          <p v-else class="muted">Adicione o primeiro capítulo deste livro.</p>
          <form class="chapter-form" @submit.prevent="createChapter">
            <fieldset :disabled="creatingChapter">
              <div class="field">
                <label for="chapter-name">Novo capítulo</label>
                <input id="chapter-name" v-model="chapterName" required placeholder="Nome ou número do capítulo" />
              </div>
              <p v-if="chapterError" class="notice error" role="alert">{{ chapterError }}</p>
              <button class="secondary full-width" :disabled="creatingChapter || !chapterName.trim()">{{ creatingChapter ? 'Cadastrando…' : 'Adicionar capítulo' }}</button>
            </fieldset>
          </form>
        </aside>
      </template>

      <!-- Palco Central: Estudos do Capítulo Selecionado -->
      <template #default>
        <section v-if="selectedChapter" class="studies-area panel-subtle" aria-labelledby="studies-heading" :aria-busy="studiesLoading">
          <header class="section-heading wrap studies-header-bar">
            <div>
              <p class="eyebrow">Estudos do capítulo</p>
              <h2 id="studies-heading">{{ selectedChapter.name }}</h2>
            </div>
            <div class="studies-header-controls">
              <ViewSwitcher
                v-model="activeViewMode"
                :options="viewOptions"
                :compact="true"
                @update:model-value="setViewMode"
              />
              <RouterLink class="button primary import-btn" :to="{ name: 'import', query: { book: book.id, chapter: selectedChapter.id } }">
                Importar estudo
              </RouterLink>
            </div>
          </header>
          <div v-if="studiesLoading" class="studies-loading-skeleton" role="status" aria-label="Carregando estudos">
            <LoadingSkeleton shape="rect" height="64px" style="margin-bottom: 12px;" />
            <LoadingSkeleton shape="rect" height="64px" style="margin-bottom: 12px;" />
          </div>
          <div v-else-if="studiesError" class="notice error" role="alert">
            <p>{{ studiesError }}</p>
            <button class="secondary" @click="loadStudies">Tentar novamente</button>
          </div>
          <template v-else>
            <p class="list-caption">{{ studies.length }} {{ studies.length === 1 ? 'estudo salvo' : 'estudos salvos' }}</p>
            <div class="studies-view-stage">
              <Transition name="view-fade" mode="out-in">
                <component
                  :is="activeRendererComponent"
                  :studies="studies"
                  :book-id="book.id"
                  :chapter-id="selectedChapter.id"
                  :chapters="chapters"
                  :active-study-id="activeStudyId"
                  :loading="studiesLoading"
                  @select-study="setActiveStudy"
                  @trash-study="confirmTrashStudy"
                />
              </Transition>
            </div>
          </template>
        </section>
        <EmptyState
          v-else
          :icon="chapters.length ? 'folder' : 'book-open'"
          :title="chapters.length ? 'Selecione um capítulo' : 'Organize seu primeiro estudo'"
          :description="chapters.length ? 'Escolha um capítulo na lista lateral para consultar os estudos cadastrados.' : 'Cadastre um capítulo e depois importe o texto-base do fichamento que deseja estudar.'"
          heading-level="h2"
        />
      </template>

      <!-- Painel Direito: Inspetor de Contexto -->
      <template #right>
        <aside class="panel context-sidebar h-full" aria-labelledby="context-heading">
          <div class="section-heading">
            <h2 id="context-heading">Inspetor</h2>
          </div>
          <div class="context-details">
            <div class="context-group">
              <span class="context-label">Livro</span>
              <p class="context-value">{{ book.title }}</p>
            </div>
            <div class="context-group" v-if="book.author">
              <span class="context-label">Autor</span>
              <p class="context-value">{{ book.author }}</p>
            </div>
            <div class="context-group" v-if="book.year">
              <span class="context-label">Ano</span>
              <p class="context-value">{{ book.year }}</p>
            </div>
            <div class="context-group" v-if="selectedChapter">
              <span class="context-label">Capítulo Selecionado</span>
              <p class="context-value font-medium">{{ selectedChapter.name }}</p>
            </div>
            <div class="context-divider" />
            <div class="context-group">
              <span class="context-label">Total de Capítulos</span>
              <p class="context-value">{{ chapters.length }}</p>
            </div>
            <div class="context-group" v-if="selectedChapter">
              <span class="context-label">Estudos no Capítulo</span>
              <p class="context-value">{{ studies.length }}</p>
            </div>
            <template v-if="activeStudy">
              <div class="context-divider" />
              <div class="context-group">
                <span class="context-label">Estudo em Foco</span>
                <p class="context-value font-medium">{{ activeStudy.title }}</p>
                <p class="text-xs text-muted mt-1" v-if="activeStudy.location">{{ activeStudy.location }}</p>
                <RouterLink
                  :to="{ name: 'study', params: { bookId: book.id, studyId: activeStudy.id } }"
                  class="button secondary button-sm mt-2 full-width"
                >
                  Abrir leitura
                </RouterLink>
              </div>
            </template>
          </div>
        </aside>
      </template>
    </SplitLayout>

    <BookEditModal
      v-if="book"
      :book="book"
      :open="isEditingBook"
      @close="isEditingBook = false"
      @saved="onBookSaved"
    />

    <TrashConfirmModal
      v-if="book"
      :open="confirmTrashBookOpen"
      title="Mover livro para a lixeira?"
      :message="`Deseja enviar o livro “${book.title}” para a lixeira? Todos os seus capítulos e estudos associados também serão movidos.`"
      confirm-label="Mover para a lixeira"
      :loading="trashingBook"
      @close="confirmTrashBookOpen = false"
      @confirm="handleTrashBook"
    />

    <TrashConfirmModal
      v-if="studyToTrash"
      :open="confirmTrashStudyOpen"
      title="Mover estudo para a lixeira?"
      :message="`Deseja enviar o estudo “${studyToTrash.title}” para a lixeira? Ele poderá ser restaurado nos próximos 30 dias.`"
      confirm-label="Mover para a lixeira"
      :loading="trashingStudy"
      @close="confirmTrashStudyOpen = false"
      @confirm="handleTrashStudy"
    />
    <ExportModal
      v-if="book"
      :open="exportModalOpen"
      :title="book.title"
      scope="book"
      :book-id="book.id"
      @close="exportModalOpen = false"
    />
  </template>
  </div>
</template>

<style scoped>
.book-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: calc(var(--space-unit) * 1.5);
}

.book-subtitle {
  font-size: 1.125rem;
  color: var(--color-muted);
  font-style: italic;
  margin: calc(var(--space-unit) * 0.25) 0 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: calc(var(--space-unit) * 0.75);
}

.chapter-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: calc(var(--space-unit) * 0.5);
  border-radius: var(--radius-small);
}

.chapter-row > a {
  flex: 1 1 auto;
  min-width: 0;
}

.chapter-actions {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

.action-btn {
  min-height: 1.875rem;
  min-width: 1.875rem;
  padding: 0;
  font-size: 0.75rem;
  background: var(--color-surface);
  color: var(--color-muted);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-control);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover:not(:disabled) {
  color: var(--color-text);
  background: var(--color-surface-hover);
  border-color: var(--color-border-strong);
}

.chapter-edit-box {
  padding: calc(var(--space-unit) * 0.75);
  background: var(--color-surface-soft);
  border-radius: var(--radius-small);
  border: var(--border-width) solid var(--color-border);
}

.chapter-edit-box .field {
  margin-bottom: calc(var(--space-unit) * 0.5);
}

.button-sm {
  min-height: 2.25rem;
  padding: calc(var(--space-unit) * 0.35) calc(var(--space-unit) * 0.75);
  font-size: 0.875rem;
}

.danger-action {
  color: var(--color-danger, #b91c1c);
}

.danger-action:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-danger, #b91c1c);
}

.study-item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: calc(var(--space-unit) * 1);
}

.study-info {
  flex: 1 1 auto;
  min-width: 0;
}

.study-actions {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
}

.book-header-main {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex: 1 1 auto;
}

.book-header-cover {
  flex-shrink: 0;
}

@media (max-width: 640px) {
  .book-header-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}

/* Painéis Redimensionáveis e Inspetor de Contexto (F06) */
.icon-toggle-btn {
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border-radius: var(--radius-control);
}

.book-split-layout {
  margin-top: calc(var(--space-unit) * 1.5);
  min-height: 60vh;
}

.chapter-sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.studies-area {
  padding: calc(var(--space-unit) * 1.5);
  height: 100%;
  box-sizing: border-box;
}

.context-sidebar {
  height: 100%;
  padding: calc(var(--space-unit) * 1.25);
  box-sizing: border-box;
  background: var(--color-surface);
}

.context-details {
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 0.85);
  margin-top: calc(var(--space-unit) * 1);
}

.context-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.context-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-meta, #556984);
}

.context-value {
  font-size: 0.925rem;
  color: var(--color-inverse-bg, #0f172a);
  margin: 0;
}

.context-divider {
  height: 1px;
  background-color: var(--color-border-divider);
  margin: calc(var(--space-unit) * 0.5) 0;
}

/* Sistema de Visualizações (F01) */
.studies-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.studies-header-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.studies-view-stage {
  width: 100%;
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .studies-header-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .studies-header-controls {
    flex-direction: column;
    align-items: stretch;
  }
  .studies-header-controls .import-btn {
    width: 100%;
    text-align: center;
  }
}
</style>
