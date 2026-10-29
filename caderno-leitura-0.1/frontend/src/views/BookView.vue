<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import BookCover from '../components/BookCover.vue'
import BookEditModal from '../components/BookEditModal.vue'
import CategoryBadge from '../components/CategoryBadge.vue'
import ExportModal from '../components/ExportModal.vue'
import TrashConfirmModal from '../components/TrashConfirmModal.vue'
import Icon from '../components/ui/Icon.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import LoadingSkeleton from '../components/ui/LoadingSkeleton.vue'
import AppBreadcrumb from '../components/ui/AppBreadcrumb.vue'
import DropdownMenu from '../components/ui/DropdownMenu.vue'
import { api, errorMessage } from '../services/api'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import { positiveId, type Book, type Chapter, type StudySummary, type StudyViewMode, type BreadcrumbItem } from '../types'
import ViewSwitcher from '../components/views/ViewSwitcher.vue'
import StudyGridView from '../components/views/StudyGridView.vue'
import StudyListView from '../components/views/StudyListView.vue'
import { useViewPreference, loadStoredViewPreference } from '../composables/useViewPreference.ts'

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

// Criação inline e edição de capítulos
const isCreatingChapterInline = ref(false)
const newChapterInputRef = ref<HTMLInputElement | null>(null)
const editChapterInputRef = ref<HTMLInputElement | null>(null)
const chaptersScrollRef = ref<HTMLElement | null>(null)

// Modo Foco (recolhe faixas superior e inferior para máxima imersão)
const isFocusMode = ref(false)
const splitLayoutRef = computed(() => ({
  leftCollapsed: isFocusMode.value,
  rightCollapsed: isFocusMode.value,
  toggleCollapse: (_pane?: string) => { isFocusMode.value = !isFocusMode.value },
}))

function toggleFocusMode() {
  isFocusMode.value = !isFocusMode.value
}

const isInspectorExpandedMobile = ref(false)

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

const breadcrumbItems = computed<BreadcrumbItem[]>(() => [
  { label: 'Livros', to: '/livros' },
  { label: book.value?.title || 'Livro', current: true },
])

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

function startCreateChapterInline() {
  chapterName.value = ''
  chapterError.value = ''
  isCreatingChapterInline.value = true
  nextTick(() => {
    newChapterInputRef.value?.focus()
  })
}

function cancelCreateChapterInline() {
  isCreatingChapterInline.value = false
  chapterName.value = ''
  chapterError.value = ''
}

async function createChapterInline() {
  await createChapter()
  if (!chapterError.value) {
    isCreatingChapterInline.value = false
  }
}

function onMobileSelectChapter(event: Event) {
  const target = event.target as HTMLSelectElement
  const id = Number(target.value)
  if (id && book.value) {
    router.push({ name: 'book', params: { bookId: book.value.id }, query: { chapter: id } })
  }
}

function startEditChapter(ch: Chapter) {
  editingChapterId.value = ch.id
  editChapterName.value = ch.name
  editChapterError.value = ''
  nextTick(() => {
    editChapterInputRef.value?.focus()
  })
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
  setActiveStudy,
} = useViewPreference({
  bookId: bookId.value,
})

const viewRenderers: Record<StudyViewMode, any> = {
  grid: StudyGridView,
  list: StudyListView,
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

watch(() => selectedChapter.value?.id, () => {
  loadStudies()
  nextTick(() => {
    const activeEl = chaptersScrollRef.value?.querySelector('.chapter-pill.selected') as HTMLElement | null
    if (activeEl) {
      activeEl.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
    }
  })
}, { immediate: true })

onBeforeUnmount(() => { disposed = true; bookRequest?.abort(); studyRequest?.abort() })
</script>

<template>
  <div class="book-view">
    <AppBreadcrumb :items="breadcrumbItems" />

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
      <!-- Cabeçalho Principal do Livro -->
      <header class="page-header wrap book-header">
        <div class="book-header-main">
          <div class="book-header-cover">
            <BookCover :cover-image="book.cover_image" :title="book.title" :author="book.author" size="md" />
          </div>
          <div class="book-info">
            <p class="eyebrow">Livro</p>
            <h1 class="book-title">{{ book.title }}</h1>
            <p v-if="book.subtitle" class="book-subtitle">{{ book.subtitle }}</p>
            <p class="intro">
              {{ book.author || 'Autor não informado' }}
              <span v-if="book.year"> · {{ book.year }}</span>
            </p>

            <div class="book-meta-actions-row">
              <div v-if="book.categories && book.categories.length > 0" class="book-categories-strip">
                <CategoryBadge
                  v-for="cat in book.categories"
                  :key="cat.id"
                  :category="cat"
                  clickable
                  size="sm"
                  title="Filtrar por esta categoria na biblioteca"
                  @click="router.push({ path: '/books', query: { categoria: cat.id } })"
                />
              </div>

              <!-- Menu Agrupado de Ações no Mobile (<= 767px) -->
              <div class="book-mobile-actions-wrapper">
                <DropdownMenu align="right" aria-label="Ações do livro">
                  <template #trigger="{ isOpen, toggle, onKeydown }">
                    <button
                      type="button"
                      class="secondary button-sm book-mobile-actions-trigger"
                      :aria-expanded="isOpen"
                      aria-label="Ações do livro"
                      @click="toggle"
                      @keydown="onKeydown"
                    >
                      <Icon name="more-horizontal" :size="16" />
                      <span>Ações do livro</span>
                    </button>
                  </template>
                  <template #default="{ close }">
                    <div class="book-mobile-actions-menu" role="menu">
                      <button
                        type="button"
                        class="dropdown-item"
                        role="menuitem"
                        @click="toggleFocusMode(); close()"
                      >
                        <Icon :name="isFocusMode ? 'minimize-2' : 'maximize-2'" :size="16" />
                        <span>{{ isFocusMode ? 'Sair do foco' : 'Modo foco' }}</span>
                      </button>
                      <button
                        type="button"
                        class="dropdown-item"
                        role="menuitem"
                        @click="exportModalOpen = true; close()"
                      >
                        <Icon name="download" :size="16" />
                        <span>Exportar anotações</span>
                      </button>
                      <button
                        type="button"
                        class="dropdown-item"
                        role="menuitem"
                        @click="isEditingBook = true; close()"
                      >
                        <Icon name="pencil" :size="16" />
                        <span>Editar livro</span>
                      </button>
                      <button
                        type="button"
                        class="dropdown-item danger-item"
                        role="menuitem"
                        @click="confirmTrashBookOpen = true; close()"
                      >
                        <Icon name="trash" :size="16" />
                        <span>Mover para a lixeira</span>
                      </button>
                    </div>
                  </template>
                </DropdownMenu>
              </div>
            </div>
          </div>
        </div>

        <!-- Barra de Ações do Cabeçalho: Botões compactos de ícone com expansão suave no hover/foco -->
        <div class="header-actions desktop-actions">
          <!-- Botão Modo Foco -->
          <button
            class="secondary icon-action-btn focus-toggle-btn"
            :class="{ active: isFocusMode }"
            type="button"
            :title="splitLayoutRef?.leftCollapsed ? 'Desativar modo foco' : 'Modo foco (ocultar faixas)'"
            :aria-label="splitLayoutRef?.leftCollapsed ? 'Desativar modo foco' : 'Modo foco'"
            @click="toggleFocusMode"
          >
            <Icon :name="isFocusMode ? 'minimize-2' : 'maximize-2'" :size="16" />
            <span class="btn-pill-label">{{ isFocusMode ? 'Sair do foco' : 'Modo foco' }}</span>
          </button>

          <!-- Exportar Anotações -->
          <button
            class="secondary icon-action-btn"
            type="button"
            title="Exportar anotações"
            aria-label="Exportar anotações"
            @click="exportModalOpen = true"
          >
            <Icon name="download" :size="16" />
            <span class="btn-pill-label">Exportar anotações</span>
          </button>

          <!-- Editar Livro -->
          <button
            class="secondary icon-action-btn"
            type="button"
            title="Editar livro"
            aria-label="Editar livro"
            @click="isEditingBook = true"
          >
            <Icon name="pencil" :size="16" />
            <span class="btn-pill-label">Editar livro</span>
          </button>

          <!-- Mover para a Lixeira -->
          <button
            class="secondary icon-action-btn danger-action"
            type="button"
            title="Mover para a lixeira"
            aria-label="Mover para a lixeira"
            @click="confirmTrashBookOpen = true"
          >
            <Icon name="trash" :size="16" />
            <span class="btn-pill-label">Mover para a lixeira</span>
          </button>
        </div>
      </header>

      <!-- Arquitetura em 3 Faixas Horizontais Empilhadas -->
      <div class="book-layout book-split-layout wrap" :class="{ 'is-focus-mode': isFocusMode }">
        <!-- 1. FAIXA SUPERIOR: Barra Horizontal de Capítulos -->
        <section
          v-if="!isFocusMode"
          class="chapters-horizontal-bar panel"
          aria-labelledby="chapters-bar-heading"
        >
          <div class="chapters-bar-header">
            <div class="chapters-title-wrap">
              <Icon name="folder" :size="16" class="chapters-icon" />
              <h2 id="chapters-bar-heading" class="chapters-bar-title">Capítulos</h2>
              <span class="chapters-count-badge" aria-label="Total de capítulos">{{ chapters.length }}</span>
            </div>

            <!-- Seletor Dropdown para Telas Estreitas / Mobile -->
            <div v-if="chapters.length" class="chapters-mobile-select-wrap">
              <label for="mobile-chapter-select" class="sr-only">Selecione o capítulo</label>
              <select
                id="mobile-chapter-select"
                class="chapters-mobile-select"
                :value="selectedChapter?.id"
                @change="onMobileSelectChapter"
              >
                <option v-for="(ch, idx) in chapters" :key="ch.id" :value="ch.id">
                  {{ idx + 1 }}. {{ ch.name }}
                </option>
              </select>
            </div>

            <!-- Criação de Novo Capítulo (Inline e Compacta) -->
            <div class="chapters-create-wrap">
              <div v-if="isCreatingChapterInline" class="new-chapter-inline-box">
                <form @submit.prevent="createChapterInline">
                  <input
                    ref="newChapterInputRef"
                    v-model="chapterName"
                    required
                    placeholder="Nome do novo capítulo"
                    class="new-chapter-input"
                    :disabled="creatingChapter"
                    @keydown.esc="cancelCreateChapterInline"
                  />
                  <div class="inline-box-actions">
                    <button
                      type="submit"
                      class="primary button-sm inline-btn"
                      :disabled="creatingChapter || !chapterName.trim()"
                      title="Salvar capítulo"
                      aria-label="Confirmar novo capítulo"
                    >
                      <Icon name="check" :size="14" />
                      <span>Salvar</span>
                    </button>
                    <button
                      type="button"
                      class="secondary button-sm inline-btn"
                      :disabled="creatingChapter"
                      title="Cancelar"
                      aria-label="Cancelar novo capítulo"
                      @click="cancelCreateChapterInline"
                    >
                      <Icon name="x" :size="14" />
                    </button>
                  </div>
                </form>
              </div>
              <button
                v-else
                type="button"
                class="secondary button-sm add-chapter-pill-btn"
                title="Adicionar novo capítulo"
                aria-label="Novo capítulo"
                @click="startCreateChapterInline"
              >
                <Icon name="plus" :size="14" />
                <span>Novo capítulo</span>
              </button>
            </div>
          </div>

          <p v-if="chapterError" class="notice error chapter-bar-notice" role="alert">{{ chapterError }}</p>

          <!-- Faixa Rolável de Abas / Pílulas de Capítulos -->
          <nav
            v-if="chapters.length"
            ref="chaptersScrollRef"
            class="chapters-nav-strip"
            aria-label="Lista de capítulos do livro"
          >
            <ul class="chapters-pills-track">
              <li v-for="(chapter, idx) in chapters" :key="chapter.id" class="chapter-pill-item">
                <!-- Modo Edição de Nome do Capítulo -->
                <div v-if="editingChapterId === chapter.id" class="chapter-pill-edit-box">
                  <form @submit.prevent="saveChapter(chapter)">
                    <input
                      ref="editChapterInputRef"
                      v-model="editChapterName"
                      required
                      placeholder="Nome do capítulo"
                      class="chapter-edit-input"
                      :disabled="savingChapterName"
                      @keydown.esc="cancelEditChapter"
                    />
                    <button
                      type="submit"
                      class="primary button-xs pill-control-btn"
                      :disabled="savingChapterName || !editChapterName.trim()"
                      title="Salvar alterações"
                      aria-label="Salvar"
                    >
                      <Icon name="check" :size="13" />
                    </button>
                    <button
                      type="button"
                      class="secondary button-xs pill-control-btn"
                      :disabled="savingChapterName"
                      title="Cancelar"
                      aria-label="Cancelar"
                      @click="cancelEditChapter"
                    >
                      <Icon name="x" :size="13" />
                    </button>
                  </form>
                  <p v-if="editChapterError" class="notice error edit-chapter-error" role="alert">{{ editChapterError }}</p>
                </div>

                <!-- Pílula de Capítulo Normal -->
                <div
                  v-else
                  class="chapter-pill"
                  :class="{ selected: selectedChapter?.id === chapter.id }"
                >
                  <RouterLink
                    :to="{ name: 'book', params: { bookId: book.id }, query: { chapter: chapter.id } }"
                    class="chapter-pill-link"
                    :aria-current="selectedChapter?.id === chapter.id ? 'page' : undefined"
                  >
                    <span class="chapter-pill-num">{{ idx + 1 }}.</span>
                    <span class="chapter-pill-text" :title="chapter.name">{{ chapter.name }}</span>
                  </RouterLink>

                  <!-- Controles Contextuais Exclusivos do Capítulo Ativo -->
                  <div v-if="selectedChapter?.id === chapter.id" class="chapter-pill-active-tools">
                    <button
                      type="button"
                      class="pill-tool-btn"
                      :disabled="idx === 0 || movingChapter"
                      title="Mover capítulo para trás"
                      aria-label="Mover capítulo para trás"
                      @click.prevent="moveChapter(chapter.id, 'up')"
                    >
                      <Icon name="chevron-left" :size="13" />
                    </button>
                    <button
                      type="button"
                      class="pill-tool-btn"
                      :disabled="idx === chapters.length - 1 || movingChapter"
                      title="Mover capítulo para frente"
                      aria-label="Mover capítulo para frente"
                      @click.prevent="moveChapter(chapter.id, 'down')"
                    >
                      <Icon name="chevron-right" :size="13" />
                    </button>
                    <button
                      type="button"
                      class="pill-tool-btn"
                      title="Renomear capítulo"
                      aria-label="Renomear capítulo"
                      @click.prevent="startEditChapter(chapter)"
                    >
                      <Icon name="pencil" :size="12" />
                    </button>
                  </div>
                </div>
              </li>
            </ul>
          </nav>

          <p v-else class="muted chapters-empty-msg">Adicione o primeiro capítulo deste livro para organizar seus estudos.</p>
        </section>

        <!-- 2. BLOCO CENTRAL: Container Principal (Estudos do Capítulo) com 100% da Largura Útil -->
        <main class="studies-main-stage">
          <section
            v-if="selectedChapter"
            class="studies-area panel"
            aria-labelledby="studies-heading"
            :aria-busy="studiesLoading"
          >
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
            :description="chapters.length ? 'Escolha um capítulo na lista superior para consultar os estudos cadastrados.' : 'Cadastre um capítulo e depois importe o texto-base do fichamento que deseja estudar.'"
            heading-level="h2"
          />
        </main>

        <!-- 3. FAIXA INFERIOR: Barra Horizontal do Inspetor (Status Bar / Rodapé Analítico) -->
        <footer
          v-if="!isFocusMode"
          class="inspector-horizontal-bar panel"
          aria-label="Metadados e contexto do livro"
        >
          <!-- Gatilho Móvel do Inspetor -->
          <button
            type="button"
            class="inspector-mobile-toggle mobile-only"
            :aria-expanded="isInspectorExpandedMobile"
            aria-controls="inspector-content-panel"
            @click="isInspectorExpandedMobile = !isInspectorExpandedMobile"
          >
            <span class="toggle-text-wrap">
              <Icon name="sliders" :size="15" />
              <span>{{ isInspectorExpandedMobile ? 'Ocultar detalhes do livro' : 'Ver detalhes do livro' }}</span>
            </span>
            <Icon :name="isInspectorExpandedMobile ? 'chevron-up' : 'chevron-down'" :size="16" class="toggle-icon" />
          </button>

          <div
            id="inspector-content-panel"
            class="inspector-bar-content"
            :class="{ 'is-collapsed-mobile': !isInspectorExpandedMobile }"
          >
            <div class="inspector-metrics-grid">
              <div class="inspector-item">
                <span class="inspector-label">Livro</span>
                <span class="inspector-value font-medium" :title="book.title">{{ book.title }}</span>
              </div>

              <div v-if="book.author" class="inspector-divider" aria-hidden="true" />
              <div v-if="book.author" class="inspector-item">
                <span class="inspector-label">Autor</span>
                <span class="inspector-value" :title="book.author">{{ book.author }}</span>
              </div>

              <div v-if="book.year" class="inspector-divider" aria-hidden="true" />
              <div v-if="book.year" class="inspector-item">
                <span class="inspector-label">Ano</span>
                <span class="inspector-value">{{ book.year }}</span>
              </div>

              <div v-if="selectedChapter" class="inspector-divider" aria-hidden="true" />
              <div v-if="selectedChapter" class="inspector-item">
                <span class="inspector-label">Capítulo Selecionado</span>
                <span class="inspector-value font-medium" :title="selectedChapter.name">{{ selectedChapter.name }}</span>
              </div>

              <div class="inspector-divider" aria-hidden="true" />
              <div class="inspector-item">
                <span class="inspector-label">Total de Capítulos</span>
                <span class="inspector-value">{{ chapters.length }}</span>
              </div>

              <div v-if="selectedChapter" class="inspector-divider" aria-hidden="true" />
              <div v-if="selectedChapter" class="inspector-item">
                <span class="inspector-label">Estudos no Capítulo</span>
                <span class="inspector-value">{{ studies.length }}</span>
              </div>
            </div>

            <!-- Estudo em foco selecionado -->
            <div v-if="activeStudy" class="inspector-study-focus-card">
              <div class="inspector-divider" aria-hidden="true" />
              <div class="inspector-study-focus-info">
                <span class="inspector-label">Estudo em Foco</span>
                <span class="inspector-value font-medium" :title="activeStudy.title">{{ activeStudy.title }}</span>
                <span v-if="activeStudy.location" class="inspector-study-location">{{ activeStudy.location }}</span>
              </div>
              <RouterLink
                :to="{ name: 'study', params: { bookId: book.id, studyId: activeStudy.id } }"
                class="button secondary button-xs inspector-open-btn"
                title="Abrir leitura deste estudo"
              >
                Abrir leitura
              </RouterLink>
            </div>
          </div>
        </footer>
      </div>

      <!-- Modais Auxiliares -->
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

.book-header-main {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex: 1 1 auto;
  min-width: 0;
}

.book-header-cover {
  flex-shrink: 0;
}

.book-info {
  flex: 1 1 auto;
  min-width: 0;
}

/* ============================================================================
   Barra de Ações do Cabeçalho: Botões Compactos com Expansão no Hover/Foco
   ============================================================================ */
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.icon-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  min-width: 44px;
  padding: 0 12px;
  border-radius: var(--radius-control);
  overflow: hidden;
  white-space: nowrap;
  cursor: pointer;
  background-color: var(--color-surface);
  color: var(--color-text);
  border: var(--border-width) solid var(--color-border);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  flex-shrink: 0;
}

.icon-action-btn .btn-pill-label {
  display: inline-block;
  max-width: 0;
  opacity: 0;
  overflow: hidden;
  white-space: nowrap;
  font-size: 0.875rem;
  font-weight: 600;
  margin-left: 0;
  transition: max-width 0.25s cubic-bezier(0.16, 1, 0.3, 1),
              opacity 0.2s ease,
              margin-left 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.focus-toggle-btn.active {
  background-color: var(--color-selected-bg, var(--color-surface-soft));
  color: var(--color-selected-text);
  border-color: var(--color-accent);
}

@media (hover: hover) and (pointer: fine) {
  .icon-action-btn:hover:not(:disabled),
  .icon-action-btn:focus-visible:not(:disabled) {
    background-color: var(--color-surface-hover);
    border-color: var(--color-border-strong);
    color: var(--color-hover-text, var(--color-text));
    padding: 0 14px;
  }

  .icon-action-btn:hover:not(:disabled) .btn-pill-label,
  .icon-action-btn:focus-visible:not(:disabled) .btn-pill-label {
    max-width: 180px;
    opacity: 1;
    margin-left: 8px;
  }

  .icon-action-btn.danger-action:hover:not(:disabled),
  .icon-action-btn.danger-action:focus-visible:not(:disabled) {
    color: var(--color-danger, #b91c1c);
    border-color: var(--color-danger, #b91c1c);
    background-color: color-mix(in srgb, var(--color-danger, #b91c1c) 10%, var(--color-surface));
  }
}

/* ============================================================================
   Layout Horizontal em 3 Faixas Empilhadas
   ============================================================================ */
.book-layout,
.book-split-layout {
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 1);
  margin-top: calc(var(--space-unit) * 1.5);
  min-height: 60vh;
}

.studies-main-stage {
  flex: 1 1 auto;
  width: 100%;
  min-width: 0;
}

.studies-area {
  padding: calc(var(--space-unit) * 1.5);
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}

/* ============================================================================
   1. Faixa Superior: Barra Horizontal de Capítulos
   ============================================================================ */
.chapters-horizontal-bar {
  padding: calc(var(--space-unit) * 0.85) calc(var(--space-unit) * 1.25);
  box-sizing: border-box;
  background: var(--color-surface);
}

.chapters-bar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: calc(var(--space-unit) * 0.75);
}

.chapters-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chapters-icon {
  color: var(--color-muted);
}

.chapters-bar-title {
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: -0.015em;
  margin: 0;
  color: var(--color-text);
}

.chapters-count-badge {
  font-size: 0.75rem;
  font-weight: 700;
  background: var(--color-surface-soft);
  color: var(--color-muted);
  border: var(--border-width) solid var(--color-border);
  border-radius: 9999px;
  padding: 1px 8px;
}

.chapters-mobile-select-wrap {
  display: none;
}

.chapters-create-wrap {
  display: flex;
  align-items: center;
}

.add-chapter-pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8125rem;
  padding: 0.35rem 0.75rem;
  min-height: 34px;
}

.new-chapter-inline-box form {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.new-chapter-input {
  min-width: 180px;
  max-width: 260px;
  height: 34px;
  padding: 0 0.65rem;
  font-size: 0.875rem;
  background: var(--color-surface-soft);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-control);
}

.inline-box-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.inline-btn {
  height: 34px;
  padding: 0 0.6rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8125rem;
}

.chapter-bar-notice {
  margin: 0.25rem 0 0.5rem;
  padding: 0.4rem 0.75rem;
  font-size: 0.875rem;
}

/* Faixa de navegação rolável por pílulas */
.chapters-nav-strip {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  padding-bottom: 4px;
}

.chapters-pills-track {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  list-style: none;
  margin: 0;
  padding: 0;
  min-width: min-content;
}

.chapter-pill-item {
  flex-shrink: 0;
}

.chapter-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.85rem;
  background: var(--color-surface-soft);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-control);
  white-space: nowrap;
  font-size: 0.875rem;
  transition: all 0.15s ease;
}

.chapter-pill:hover {
  border-color: var(--color-border-strong);
  background: var(--color-surface-hover);
}

.chapter-pill.selected {
  background: var(--color-selected-bg, var(--color-surface));
  color: var(--color-selected-text, var(--color-accent));
  border-color: var(--color-accent);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chapter-pill-link {
  text-decoration: none;
  color: inherit;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 600;
}

.chapter-pill-num {
  color: var(--color-muted);
  font-size: 0.8125rem;
}

.chapter-pill.selected .chapter-pill-num {
  color: var(--color-selected-text);
}

.chapter-pill-active-tools {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  margin-left: 0.35rem;
  padding-left: 0.35rem;
  border-left: var(--border-width) solid var(--color-border-divider);
}

.pill-tool-btn {
  min-width: 24px;
  min-height: 24px;
  padding: 0;
  border: var(--border-width) solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-muted);
  border-radius: var(--radius-small);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.1s ease;
}

.pill-tool-btn:hover:not(:disabled) {
  background: var(--color-surface-hover);
  color: var(--color-text);
  border-color: var(--color-border-strong);
}

.chapter-pill-edit-box form {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: var(--color-surface-soft);
  padding: 0.25rem;
  border-radius: var(--radius-control);
  border: var(--border-width) solid var(--color-border);
}

.chapter-edit-input {
  height: 28px;
  padding: 0 0.5rem;
  font-size: 0.8125rem;
  min-width: 140px;
}

.pill-control-btn {
  min-height: 28px;
  padding: 0 0.4rem;
}

.edit-chapter-error {
  margin: 0.25rem 0 0;
  font-size: 0.75rem;
}

.chapters-empty-msg {
  margin: 0.5rem 0 0;
  font-size: 0.875rem;
}

/* ============================================================================
   2. Bloco Central: Estudos do Capítulo (Header & Palco)
   ============================================================================ */
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

.button-sm {
  min-height: 2.25rem;
  padding: calc(var(--space-unit) * 0.35) calc(var(--space-unit) * 0.75);
  font-size: 0.875rem;
}

.button-xs {
  min-height: 26px;
  padding: 2px 8px;
  font-size: 0.75rem;
  border-radius: var(--radius-small);
}

/* ============================================================================
   3. Faixa Inferior: Barra Horizontal do Inspetor (Status Bar / Rodapé)
   ============================================================================ */
.inspector-horizontal-bar {
  padding: calc(var(--space-unit) * 0.75) calc(var(--space-unit) * 1.25);
  box-sizing: border-box;
  background: var(--color-surface);
}

.inspector-bar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.inspector-metrics-grid {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.85rem 1.25rem;
}

.inspector-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.inspector-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-meta, #556984);
  font-weight: 600;
  line-height: 1;
}

.inspector-value {
  font-size: 0.875rem;
  color: var(--color-inverse-bg, #0f172a);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 240px;
}

.inspector-divider {
  width: 1px;
  height: 24px;
  background-color: var(--color-border-divider);
  flex-shrink: 0;
}

.inspector-study-focus-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-left: auto;
}

.inspector-study-focus-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.inspector-study-location {
  font-size: 0.75rem;
  color: var(--color-muted);
}

.inspector-open-btn {
  white-space: nowrap;
  flex-shrink: 0;
}

.book-mobile-actions-wrapper {
  display: none !important;
}

.inspector-mobile-toggle {
  display: none !important;
}

/* ============================================================================
   Responsividade: Tablet e Mobile
   ============================================================================ */
@media (max-width: 768px) {
  .book-layout,
  .book-split-layout {
    min-height: 0;
    margin-top: 0.75rem;
    gap: 0.75rem;
  }

  .studies-area {
    padding: 0.75rem;
    height: auto;
    min-height: 0;
  }

  .studies-header-bar {
    justify-content: flex-start;
    gap: 0.5rem;
    flex-direction: column;
    align-items: stretch;
    margin-bottom: 0.5rem;
  }

  .studies-header-bar > div:first-child {
    flex: initial;
    margin-bottom: 0.25rem;
  }

  .studies-header-bar h2 {
    margin: 0;
    font-size: 1.35rem;
    line-height: 1.25;
  }

  .studies-header-bar .eyebrow {
    margin: 0 0 0.15rem;
    font-size: 0.75rem;
  }

  .studies-header-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
    margin-top: 0.25rem;
  }

  .studies-header-controls .import-btn {
    width: 100%;
    text-align: center;
  }

  .list-caption {
    margin-top: 0.25rem;
    margin-bottom: 0.25rem;
  }

  .studies-view-stage {
    margin-top: 0.25rem;
  }
}

@media (max-width: 767px) {
  .book-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .book-header-main {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    gap: 0.875rem;
    width: 100%;
  }

  .book-header-cover {
    width: 48px;
    height: 72px;
    flex-shrink: 0;
  }

  .book-header-cover :deep(.book-cover),
  .book-header-cover :deep(img) {
    width: 48px !important;
    height: 72px !important;
    min-width: 48px !important;
    max-width: 48px !important;
    border-radius: var(--radius-sm, 4px);
    object-fit: cover;
  }

  .book-title {
    font-size: 1.15rem;
    line-height: 1.3;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .book-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    min-width: 0;
    flex: 1;
  }

  .book-info .eyebrow {
    font-size: 0.7rem;
    margin: 0;
  }

  .book-info .intro {
    font-size: 0.8rem;
    margin: 0;
    color: var(--color-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .book-meta-actions-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.35rem;
  }

  .book-categories-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    align-items: center;
  }

  .desktop-actions {
    display: none !important;
  }

  .book-mobile-actions-wrapper {
    display: inline-flex !important;
    margin-left: auto;
  }

  .book-mobile-actions-trigger {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    min-height: 44px;
    padding: 0.4rem 0.75rem;
    border-radius: var(--radius-control);
    font-size: 0.85rem;
    font-weight: 500;
  }

  .book-mobile-actions-menu {
    display: flex;
    flex-direction: column;
    min-width: 200px;
    padding: 0.35rem;
    gap: 0.25rem;
  }

  .book-mobile-actions-menu .dropdown-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
    min-height: 44px;
    padding: 0.5rem 0.75rem;
    text-align: left;
    font-size: 0.875rem;
    color: var(--color-text);
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    cursor: pointer;
  }

  .book-mobile-actions-menu .dropdown-item:hover,
  .book-mobile-actions-menu .dropdown-item:focus {
    background: var(--color-surface-hover);
    color: var(--color-hover-text);
  }

  .book-mobile-actions-menu .dropdown-item.danger-item {
    color: var(--color-danger, #b91c1c);
  }

  .book-mobile-actions-menu .dropdown-item.danger-item:hover,
  .book-mobile-actions-menu .dropdown-item.danger-item:focus {
    background: var(--color-danger-subtle, rgba(239, 68, 68, 0.1));
  }

  .chapters-horizontal-bar {
    padding: 0.75rem;
  }

  .chapters-bar-header {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .chapters-nav-strip {
    display: none !important;
  }

  .chapters-mobile-select-wrap {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
    margin-bottom: 0.25rem;
  }

  .chapters-mobile-select {
    flex: 1;
    width: 100%;
    min-height: 44px;
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
    background: var(--color-surface-soft);
    border: var(--border-width) solid var(--color-border);
    border-radius: var(--radius-control);
    color: var(--color-text);
  }

  .new-chapter-inline-box form {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }

  .new-chapter-input {
    max-width: 100%;
    width: 100%;
    min-height: 44px;
  }

  .inline-box-actions {
    justify-content: flex-end;
  }

  .inline-box-actions button {
    min-height: 44px;
  }

  .inspector-mobile-toggle {
    display: inline-flex !important;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    min-height: 44px;
    padding: 0.5rem 0.75rem;
    background: transparent;
    border: none;
    color: var(--color-text);
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
  }

  .toggle-text-wrap {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
  }

  .inspector-bar-content.is-collapsed-mobile {
    display: none !important;
  }

  .inspector-bar-content:not(.is-collapsed-mobile) {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
    padding-top: 0.75rem;
    border-top: var(--border-width) solid var(--color-border-divider);
  }

  .inspector-metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
    width: 100%;
  }

  .inspector-divider {
    display: none;
  }

  .inspector-study-focus-card {
    margin-left: 0;
    width: 100%;
    padding-top: 0.5rem;
    border-top: var(--border-width) solid var(--color-border-divider);
    justify-content: space-between;
  }

  .inspector-open-btn {
    min-height: 44px;
    display: inline-flex;
    align-items: center;
  }
}

@media (max-width: 640px) {
  .inspector-metrics-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .icon-action-btn,
  .icon-action-btn .btn-pill-label,
  .chapter-pill,
  .pill-tool-btn {
    transition: none !important;
  }
}
</style>
