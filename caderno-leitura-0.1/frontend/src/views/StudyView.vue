<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api, errorMessage } from '../services/api'
import { useStudyResource } from '../composables/useStudyResource'
import StudyTabs from '../components/StudyTabs.vue'
import ReaderTools from '../components/ReaderTools.vue'
import ActiveReadingBar from '../components/ActiveReadingBar.vue'
import ExportModal from '../components/ExportModal.vue'
import TrashConfirmModal from '../components/TrashConfirmModal.vue'
import StudyRelationsList from '../components/relations/StudyRelationsList.vue'
import CreateRelationModal from '../components/relations/CreateRelationModal.vue'
import StudyStatusBadge from '../components/StudyStatusBadge.vue'
import ShareModal from '../components/sharing/ShareModal.vue'
import StudyHistoryModal from '../components/StudyHistoryModal.vue'
import FloatingActionsToolbar from '../components/FloatingActionsToolbar.vue'
import NoteQuestionPopover from '../components/NoteQuestionPopover.vue'
import HighlightActionPopover from '../components/HighlightActionPopover.vue'
import { useStudyHighlights } from '../composables/useStudyHighlights'
import { useActiveReadingSession } from '../composables/useActiveReadingSession'
import { formatQuoteText, useTextSelection } from '../composables/useTextSelection'
import { useFloatingToast } from '../composables/useFloatingToast'
import { useHighlightColorPreference } from '../composables/useHighlightColorPreference'
import type { HighlightClickEvent } from '../utils/highlightRenderer'
import type { HighlightColor, ResourceVisibility, Study, StudySectionKey, TextSelectionContext } from '../types.ts'


const route = useRoute()
const router = useRouter()
const resource = useStudyResource(api)
const { state } = resource

const exportModalOpen = ref(false)
const confirmTrashOpen = ref(false)
const createRelationModalOpen = ref(false)
const shareModalOpen = ref(false)
const historyModalOpen = ref(false)
const relationsListRef = ref<InstanceType<typeof StudyRelationsList> | null>(null)
const trashing = ref(false)
const trashError = ref('')

function handleStudyRestored(updatedStudy: Study) {
  if (state.context) {
    state.context.study = updatedStudy
  }
  showToast('Versão restaurada com sucesso!')
}


const canEdit = computed(() => state.context?.study.can_edit !== false)

// Destaques e Ações Contextuais (F0.6.2)
const studyId = computed(() => state.context?.study.id)
const {
  highlights,
  activeHighlight,
  popoverRect,
  addHighlight,
  editHighlight,
  removeHighlight,
  openHighlightPopover,
  closeHighlightPopover,
} = useStudyHighlights(studyId)

const studyTabsRef = ref<InstanceType<typeof StudyTabs> | null>(null)
const activeSection = ref<StudySectionKey>('summary')
const activePanelEl = computed(() => studyTabsRef.value?.activePanelEl || null)
const { selectionContext, clearSelection } = useTextSelection(activePanelEl, activeSection)

// Leitura Ativa (F0.6.3)
const activeReadingSession = useActiveReadingSession({
  activeSectionRef: activeSection,
  highlightsRef: highlights,
  containerRef: activePanelEl,
})

const totalInteractiveCount = computed(() => {
  return highlights.value.filter((h) => h.kind === 'hidden' || h.kind === 'question').length
})

function handleToggleActiveReading() {
  if (activeReadingSession.isActive.value) {
    activeReadingSession.endSession()
  } else {
    if (activeReadingSession.totalCount.value === 0 && totalInteractiveCount.value === 0) {
      showToast('Nenhum trecho oculto ou pergunta cadastrada neste estudo. Selecione um texto para criar oclusões ou perguntas.')
      return
    }
    activeReadingSession.startSession()
  }
}

function handleActiveToggle(event: Event) {
  const customEvent = event as CustomEvent<{ id: number; isRevealed: boolean }>
  if (customEvent.detail) {
    activeReadingSession.setNodeRevealed(customEvent.detail.id, customEvent.detail.isRevealed)
  }
}

function onActiveReadingKeydown(event: KeyboardEvent) {
  if (!activeReadingSession.isActive.value) return
  if (event.defaultPrevented || event.isComposing) return

  const target = event.target as HTMLElement | null
  if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)) {
    return
  }

  if (event.key === 'Escape') {
    event.preventDefault()
    activeReadingSession.endSession()
  } else if (event.key === 'j' || event.key === 'J' || event.key === 'ArrowDown') {
    event.preventDefault()
    activeReadingSession.next()
  } else if (event.key === 'k' || event.key === 'K' || event.key === 'ArrowUp') {
    event.preventDefault()
    activeReadingSession.previous()
  }
}

// Feedback visual (Toast genérico na base e Micro-Toast de ferramentas no topo)
const toastMessage = ref('')
let toastTimer: ReturnType<typeof setTimeout> | null = null

const highlightColorMap: Record<HighlightColor, string> = {
  yellow: '#fef08a',
  green: '#bbf7d0',
  blue: '#bae6fd',
  pink: '#fbcfe8',
  purple: '#e9d5ff',
}

const floatingToast = useFloatingToast()
const { activeColor: lastUsedColor } = useHighlightColorPreference()

const isNotePopoverOpen = ref(false)
const activePopoverKind = ref<'note' | 'question'>('note')
const popoverSelection = ref<TextSelectionContext | null>(null)

function handleOpenNote(payload: { selection: TextSelectionContext }) {
  popoverSelection.value = payload.selection
  activePopoverKind.value = 'note'
  isNotePopoverOpen.value = true
}

function handleOpenQuestion(payload: { selection: TextSelectionContext }) {
  popoverSelection.value = payload.selection
  activePopoverKind.value = 'question'
  isNotePopoverOpen.value = true
}

async function handlePopoverSave(payload: {
  text: string
  color: HighlightColor
  kind: 'note' | 'question'
  selection: TextSelectionContext
}) {
  const sel = payload.selection
  if (!sel || !state.context) return

  if (payload.kind === 'note') {
    const result = await addHighlight({
      section: sel.section,
      start_offset: sel.start_offset,
      end_offset: sel.end_offset,
      selected_text: sel.selected_text,
      prefix: sel.prefix,
      suffix: sel.suffix,
      color: payload.color,
      kind: 'note',
      note: payload.text,
    })
    if (result) {
      floatingToast.showToast({
        message: 'Anotação salva',
      })
    } else {
      showToast('Não foi possível salvar a anotação.')
    }
  } else {
    const result = await addHighlight({
      section: sel.section,
      start_offset: sel.start_offset,
      end_offset: sel.end_offset,
      selected_text: sel.selected_text,
      prefix: sel.prefix,
      suffix: sel.suffix,
      color: 'yellow',
      kind: 'question',
      note: payload.text,
    })
    if (result) {
      floatingToast.showToast({
        message: 'Pergunta cadastrada',
      })
    } else {
      showToast('Não foi possível criar a pergunta.')
    }
  }

  isNotePopoverOpen.value = false
  popoverSelection.value = null
  clearSelection()
}

function handlePopoverCancel() {
  isNotePopoverOpen.value = false
  popoverSelection.value = null
  clearSelection()
}

function showToast(message: string) {
  toastMessage.value = message
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
  }, 3000)
}

function handleToolSelected(payload: { tool: string; label: string; colorDot?: string }) {
  floatingToast.showToast({
    message: payload.label,
    colorDot: payload.colorDot,
  })
}

async function handleHighlight(payload: { color: HighlightColor; selection?: TextSelectionContext }) {
  const sel = payload.selection || selectionContext.value
  if (!sel || !state.context) return
  const result = await addHighlight({
    section: sel.section,
    start_offset: sel.start_offset,
    end_offset: sel.end_offset,
    selected_text: sel.selected_text,
    prefix: sel.prefix,
    suffix: sel.suffix,
    color: payload.color,
    kind: 'highlight',
  })
  if (result) {
    floatingToast.showToast({
      message: 'Destaque aplicado',
      colorDot: highlightColorMap[payload.color] || '#fef08a',
    })
  } else {
    showToast('Não foi possível salvar o destaque.')
  }
  clearSelection()
}

async function handleAnnotate(payload: { note: string; color: HighlightColor; selection?: TextSelectionContext }) {
  const sel = payload.selection || selectionContext.value
  if (!sel || !state.context) return
  const result = await addHighlight({
    section: sel.section,
    start_offset: sel.start_offset,
    end_offset: sel.end_offset,
    selected_text: sel.selected_text,
    prefix: sel.prefix,
    suffix: sel.suffix,
    color: payload.color,
    kind: 'note',
    note: payload.note,
  })
  if (result) {
    floatingToast.showToast({
      message: 'Anotação salva',
    })
  } else {
    showToast('Não foi possível salvar a anotação.')
  }
  clearSelection()
}

async function handleCopyQuote(payload?: { selection?: TextSelectionContext }) {
  const sel = payload?.selection || selectionContext.value
  if (!sel || !state.context) return
  const quote = formatQuoteText({
    selected_text: sel.selected_text,
    studyTitle: state.context.study.title,
    bookTitle: state.context.book.title,
    chapterName: state.context.chapter.name,
  })
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(quote)
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = quote
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }
    floatingToast.showToast({
      message: 'Citação copiada',
    })
  } catch {
    showToast('Não foi possível copiar automaticamente.')
  }
  clearSelection()
}

async function handleOcclude(payload?: { selection?: TextSelectionContext }) {
  const sel = payload?.selection || selectionContext.value
  if (!sel || !state.context) return
  const result = await addHighlight({
    section: sel.section,
    start_offset: sel.start_offset,
    end_offset: sel.end_offset,
    selected_text: sel.selected_text,
    prefix: sel.prefix,
    suffix: sel.suffix,
    color: 'yellow',
    kind: 'hidden',
  })
  if (result) {
    floatingToast.showToast({
      message: 'Trecho ocultado para revisão',
    })
  } else {
    showToast('Não foi possível ocultar o trecho.')
  }
  clearSelection()
}

async function handleAskQuestion(payload: { question: string; selection?: TextSelectionContext }) {
  const sel = payload.selection || selectionContext.value
  if (!sel || !state.context) return
  const result = await addHighlight({
    section: sel.section,
    start_offset: sel.start_offset,
    end_offset: sel.end_offset,
    selected_text: sel.selected_text,
    prefix: sel.prefix,
    suffix: sel.suffix,
    color: 'yellow',
    kind: 'question',
    note: payload.question,
  })
  if (result) {
    floatingToast.showToast({
      message: 'Pergunta cadastrada',
    })
  } else {
    showToast('Não foi possível criar a pergunta.')
  }
  clearSelection()
}

function handleHighlightClick(event: HighlightClickEvent) {
  openHighlightPopover(event.highlight, event.boundingRect)
}

async function handleChangeColor(color: HighlightColor) {
  if (!activeHighlight.value) return
  await editHighlight(activeHighlight.value.id, { color })
}

async function handleUpdateNote(note: string) {
  if (!activeHighlight.value) return
  await editHighlight(activeHighlight.value.id, { note })
}

async function handleDeleteHighlight() {
  if (!activeHighlight.value) return
  await removeHighlight(activeHighlight.value.id)
}

function handleRelationCreated() {
  createRelationModalOpen.value = false
  relationsListRef.value?.loadRelations()
}

function handleVisibilityChanged(payload: { visibility: ResourceVisibility; effectiveVisibility: ResourceVisibility }) {
  if (state.context) {
    state.context.study.visibility = payload.visibility
    state.context.study.effective_visibility = payload.effectiveVisibility
  }
}

async function handleTrash() {
  if (!state.context || trashing.value) return
  trashing.value = true
  trashError.value = ''
  try {
    await api.trashStudy(state.context.study.id)
    confirmTrashOpen.value = false
    await router.push({
      name: 'book',
      params: { bookId: state.context.book.id },
      query: { chapter: state.context.chapter.id }
    })
  } catch (error) {
    trashError.value = errorMessage(error)
  } finally {
    trashing.value = false
  }
}

async function load() { await resource.load(route.params.bookId, route.params.studyId) }
watch([() => route.params.bookId, () => route.params.studyId], load, { immediate: true })

watch(activeSection, async () => {
  clearSelection()
  await nextTick()
  if (activeReadingSession.isActive.value) {
    activeReadingSession.hideAll()
  }
})

onMounted(() => {
  window.addEventListener('keydown', onActiveReadingKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onActiveReadingKeydown)
  resource.cancel()
  if (toastTimer) clearTimeout(toastTimer)
})
</script>

<template>
  <div class="study-view">
    <p v-if="state.loading" class="state-panel" role="status">Carregando estudo…</p>
  <div v-else-if="state.error" class="notice error" role="alert">
    <h1>Não foi possível abrir o estudo.</h1><p>{{ state.error }}</p>
    <div class="actions wrap"><button type="button" class="secondary" @click="load">Tentar novamente</button><RouterLink to="/" class="text-link">Voltar aos livros</RouterLink></div>
  </div>
  <template v-else-if="state.context">
    <nav class="breadcrumb" aria-label="Caminho">
      <div class="breadcrumb-desktop">
        <RouterLink to="/">Meus livros</RouterLink><span aria-hidden="true">/</span>
        <RouterLink :to="{ name: 'book', params: { bookId: state.context.book.id } }">{{ state.context.book.title }}</RouterLink><span aria-hidden="true">/</span>
        <RouterLink :to="{ name: 'book', params: { bookId: state.context.book.id }, query: { chapter: state.context.chapter.id } }">{{ state.context.chapter.name }}</RouterLink>
      </div>
      <div class="breadcrumb-mobile">
        <RouterLink
          class="back-chapter-btn"
          :to="{ name: 'book', params: { bookId: state.context.book.id }, query: { chapter: state.context.chapter.id } }"
          :title="`Voltar a ${state.context.chapter.name}`"
        >
          <svg class="w-4 h-4 back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span class="back-chapter-text">Voltar a {{ state.context.chapter.name }}</span>
        </RouterLink>
      </div>
    </nav>
    <!-- Banner de Somente Leitura (Convidado) -->
    <div v-if="!canEdit" class="read-only-banner" role="status" aria-live="polite">
      <div class="read-only-icon" aria-hidden="true">
        <svg class="w-6 h-6 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
      </div>
      <div class="read-only-text">
        <p class="read-only-title">Estudo Compartilhado (Modo Somente Leitura)</p>
        <p class="read-only-desc">
          Este estudo foi compartilhado por
          <strong>{{ state.context.study.owner?.display_name || state.context.study.owner?.username || 'outro leitor' }}</strong>
          <span v-if="state.context.study.owner?.username" class="font-mono">(@{{ state.context.study.owner?.username }})</span>.
          Mutações e anotações pessoais são exclusivas do proprietário.
        </p>
      </div>
    </div>

    <header class="page-header reader-heading">
      <div class="reader-heading-main">
        <h1 class="reader-title">{{ state.context.study.title }}</h1>
        <div class="reader-meta-row">
          <StudyStatusBadge
            :status="state.context.study.reading_status || 'rascunho'"
            :study-id="state.context.study.id"
            :interactive="canEdit"
            @change="(newSt) => { if (state.context) state.context.study.reading_status = newSt }"
          />
          <span class="meta-dot-separator" aria-hidden="true">•</span>
          <span class="reader-location intro">{{ state.context.study.location || 'Localização não informada' }}</span>
        </div>
      </div>
      <div class="header-actions">
        <div class="header-actions-group">
          <!-- Compartilhar (se canEdit) -->
          <button
            v-if="canEdit"
            type="button"
            class="secondary share-action header-icon-btn"
            aria-label="Compartilhar estudo e gerenciar permissões"
            title="Compartilhar estudo"
            @click="shareModalOpen = true"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
          </button>

          <!-- Exportar estudo -->
          <button
            type="button"
            class="secondary export-action header-icon-btn"
            aria-label="Exportar estudo"
            title="Exportar estudo"
            @click="exportModalOpen = true"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>

          <!-- Histórico de versões -->
          <button
            type="button"
            class="secondary history-action header-icon-btn"
            aria-label="Abrir histórico de versões do estudo"
            title="Histórico de versões"
            @click="historyModalOpen = true"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>

          <!-- Editar estudo (se canEdit) -->
          <RouterLink
            v-if="canEdit"
            class="button primary edit-action header-icon-btn"
            :to="{ name: 'study-edit', params: { bookId: state.context.book.id, studyId: state.context.study.id } }"
            aria-label="Editar estudo"
            title="Editar estudo"
          >
            <svg class="w-4 h-4 edit-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </RouterLink>
        </div>

        <!-- Separação espacial entre ações comuns e a ação destrutiva de exclusão -->
        <div v-if="canEdit" class="header-actions-divider" aria-hidden="true"></div>

        <!-- Mover para a lixeira (se canEdit) -->
        <button
          v-if="canEdit"
          type="button"
          class="secondary danger-action header-icon-btn"
          aria-label="Mover para a lixeira"
          title="Mover para a lixeira"
          @click="confirmTrashOpen = true"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </header>

    <!-- Barra Contextual de Leitura Ativa (F0.6.3) -->
    <ActiveReadingBar
      :active="activeReadingSession.isActive.value"
      :revealed-count="activeReadingSession.revealedCount.value"
      :total-count="activeReadingSession.totalCount.value"
      :completion-percentage="activeReadingSession.completionPercentage.value"
      :current-index="activeReadingSession.focusedIndex.value"
      @reveal-all="activeReadingSession.revealAll"
      @hide-all="activeReadingSession.hideAll"
      @next="activeReadingSession.next"
      @previous="activeReadingSession.previous"
      @close="activeReadingSession.endSession"
    />

    <div
      class="reader-layout reader-static-surface"
      @study-active-toggle="handleActiveToggle"
    >
      <div class="reader-content-column">
        <StudyTabs
          ref="studyTabsRef"
          :key="state.context.study.id"
          :id-prefix="`study-${state.context.study.id}`"
          :sections="state.context.study"
          :highlights="highlights"
          @highlight-click="handleHighlightClick"
          @active-section-change="(key) => { activeSection = key; clearSelection(); }"
        />

        <ReaderTools
          :key="state.context.study.id"
          :active-reading-enabled="activeReadingSession.isActive.value"
          :interactive-count="totalInteractiveCount"
          @toggle-active-reading="handleToggleActiveReading"
        />
      </div>
      <aside class="panel reader-notes" aria-labelledby="notes-heading">
        <h2 id="notes-heading">Minhas anotações</h2>
        <p v-if="state.context.study.notes.trim()" class="notes-content">{{ state.context.study.notes }}</p>
        <p v-else class="muted">
          {{ canEdit ? 'Nenhuma anotação ainda. Registre suas interpretações em “Editar estudo”.' : 'Nenhuma anotação pública registrada.' }}
        </p>
      </aside>
    </div>
    <details class="original-response"><summary>Consultar Fichamento da Fonte</summary><pre>{{ state.context.study.source_response }}</pre></details>

    <StudyRelationsList
      ref="relationsListRef"
      :study-id="state.context.study.id"
      :book-id="state.context.book.id"
      :read-only="!canEdit"
      @open-create-modal="createRelationModalOpen = true"
    />

    <CreateRelationModal
      v-if="canEdit"
      :open="createRelationModalOpen"
      :source-study-id="state.context.study.id"
      :source-study-title="state.context.study.title"
      @close="createRelationModalOpen = false"
      @relation-created="handleRelationCreated"
    />

    <TrashConfirmModal
      v-if="canEdit"
      :open="confirmTrashOpen"
      title="Mover estudo para a lixeira?"
      :message="`Deseja enviar o estudo “${state.context.study.title}” para a lixeira? Ele poderá ser restaurado nos próximos 30 dias.`"
      confirm-label="Mover para a lixeira"
      :loading="trashing"
      @close="confirmTrashOpen = false"
      @confirm="handleTrash"
    />

    <ExportModal
      :open="exportModalOpen"
      :title="state.context.study.title"
      scope="study"
      :book-id="state.context.book.id"
      :study-id="state.context.study.id"
      @close="exportModalOpen = false"
    />

    <ShareModal
      v-if="canEdit"
      v-model="shareModalOpen"
      :study-id="state.context.study.id"
      :book-id="state.context.book.id"
      :initial-visibility="state.context.study.visibility"
      @visibility-changed="handleVisibilityChanged"
    />

    <StudyHistoryModal
      :open="historyModalOpen"
      :study-id="state.context.study.id"
      :can-edit="canEdit"
      @close="historyModalOpen = false"
      @restored="handleStudyRestored"
    />


    <!-- Barra Flutuante Contextual de Ações (F0.6.2 / F0.7.3) -->
    <FloatingActionsToolbar
      :visible="Boolean(selectionContext) && !isNotePopoverOpen"
      :selection="selectionContext"
      :study-title="state.context.study.title"
      :book-title="state.context.book.title"
      :chapter-name="state.context.chapter.name"
      :can-edit="canEdit"
      @highlight="handleHighlight"
      @annotate="handleAnnotate"
      @copy-quote="handleCopyQuote"
      @occlude="handleOcclude"
      @ask-question="handleAskQuestion"
      @open-note="handleOpenNote"
      @open-question="handleOpenQuestion"
      @tool-selected="handleToolSelected"
      @close="clearSelection"
    />

    <!-- Popover Desacoplado de Anotação e Pergunta (F 0.7.3) -->
    <NoteQuestionPopover
      :visible="isNotePopoverOpen"
      :kind="activePopoverKind"
      :selection="popoverSelection || selectionContext"
      :active-color="lastUsedColor"
      :anchor-rect="(popoverSelection || selectionContext)?.boundingRect"
      @save="handlePopoverSave"
      @cancel="handlePopoverCancel"
    />

    <!-- Popover de Gestão de Destaque Clicado (F0.6.2) -->
    <HighlightActionPopover
      :highlight="activeHighlight"
      :bounding-rect="popoverRect"
      :can-edit="canEdit"
      @change-color="handleChangeColor"
      @update-note="handleUpdateNote"
      @delete="handleDeleteHighlight"
      @close="closeHighlightPopover"
    />

    <!-- Micro-Toast Flutuante de Ferramentas no Topo do Leitor (F 0.7.2) -->
    <Transition name="floating-toast-fade">
      <div
        v-if="floatingToast.visible.value"
        class="study-micro-toast"
        role="status"
        aria-live="polite"
        aria-atomic="true"
      >
        <span
          v-if="floatingToast.colorDot.value"
          class="micro-toast-color-dot"
          :style="{ backgroundColor: floatingToast.colorDot.value }"
          aria-hidden="true"
        />
        <span class="micro-toast-text">{{ floatingToast.message.value }}</span>
      </div>
    </Transition>

    <!-- Toast de Notificação -->
    <Transition name="toast-fade">
      <div v-if="toastMessage" class="study-toast" role="status" aria-live="polite">
        <svg class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span>{{ toastMessage }}</span>
      </div>
    </Transition>
  </template>
  </div>
</template>

<style scoped>
.read-only-banner {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1.25rem;
  margin-bottom: 1.5rem;
  background: var(--color-surface-subtle, rgba(245, 158, 11, 0.08));
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: var(--radius-lg, 1rem);
}

.read-only-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.read-only-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary, #18181b);
  margin: 0;
}

.read-only-desc {
  font-size: 0.8125rem;
  color: var(--color-text-muted, #71717a);
  margin: 0.125rem 0 0 0;
}

.header-actions {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 0.5rem;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.header-actions-group {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 0.5rem;
}

.header-actions-divider {
  width: 1px;
  height: 24px;
  background: var(--color-border, #e4e4e7);
  margin: 0 0.25rem;
  flex-shrink: 0;
}

.header-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  min-height: 40px;
  width: 40px;
  height: 40px;
  padding: 0;
  border-radius: var(--radius-md, 0.5rem);
  flex-shrink: 0;
  cursor: pointer;
  transition: all 0.15s ease;
}

.header-icon-btn svg {
  width: 1.2em;
  height: 1.2em;
  flex-shrink: 0;
}

.edit-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.edit-icon {
  width: 1.2em;
  height: 1.2em;
  flex-shrink: 0;
}

.share-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  white-space: nowrap;
}

.share-action svg {
  width: 1.2em;
  height: 1.2em;
  flex-shrink: 0;
  min-width: 1.2em;
  min-height: 1.2em;
}

.danger-action:hover {
  color: #ef4444 !important;
  border-color: rgba(239, 68, 68, 0.4) !important;
  background: rgba(239, 68, 68, 0.08) !important;
}

.reader-content-column {
  display: flex;
  flex-direction: column;
  gap: var(--space-unit, 1rem);
  min-width: 0;
}

.desktop-only {
  display: inline-flex;
}

.mobile-only {
  display: none;
}

.breadcrumb-desktop {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.breadcrumb-mobile {
  display: none;
}

.back-chapter-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 44px;
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-md, 0.5rem);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary, #52525b);
  text-decoration: none;
  background: var(--color-surface-subtle, rgba(0, 0, 0, 0.04));
  border: 1px solid var(--color-border, #e4e4e7);
  max-width: 100%;
  transition: all 0.15s ease;
}

.back-chapter-btn:hover {
  background: var(--color-surface-hover, #f4f4f5);
  color: var(--color-text-primary, #18181b);
}

.back-icon {
  width: 1.125rem;
  height: 1.125rem;
  flex-shrink: 0;
}

.back-chapter-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.page-header.reader-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.reader-heading-main {
  flex: 1;
  min-width: 0;
}

.reader-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.25;
  color: var(--color-text-primary, #18181b);
  word-break: break-word;
}

.reader-meta-row {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}

.meta-dot-separator {
  color: var(--color-text-muted, #71717a);
  font-size: 0.75rem;
  line-height: 1;
  user-select: none;
}

.reader-location {
  font-size: 0.875rem;
  color: var(--color-text-muted, #71717a);
  margin: 0;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .desktop-only {
    display: none !important;
  }

  .mobile-only {
    display: flex !important;
  }

  .page-header.reader-heading {
    flex-direction: column;
    align-items: stretch;
    gap: 0.875rem;
    margin-bottom: 1.25rem;
  }

  .reader-heading-main {
    width: 100%;
  }

  .reader-title {
    font-size: 1.5rem;
    line-height: 1.25;
    margin: 0;
    width: 100%;
  }

  .reader-meta-row {
    margin-top: 0.375rem;
    gap: 0.5rem;
  }

  .header-actions {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: nowrap;
    gap: 0.5rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--color-border-subtle, rgba(0, 0, 0, 0.08));
    margin-top: 0;
  }

  .header-actions-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .header-actions-divider {
    display: none;
  }

  .header-actions .danger-action {
    margin-left: auto;
  }

  .header-icon-btn {
    min-width: 44px;
    min-height: 44px;
    width: 44px;
    height: 44px;
  }

  .edit-action {
    min-width: 44px;
    min-height: 44px;
    padding: 0;
    justify-content: center;
  }
}

@media (max-width: 640px) {
  .breadcrumb-desktop {
    display: none !important;
  }

  .breadcrumb-mobile {
    display: block !important;
    margin-bottom: 0.75rem;
  }
}

.study-toast {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: var(--color-surface, #18181b);
  color: var(--color-text-primary, #ffffff);
  border: 1px solid var(--color-border, #3f3f46);
  border-radius: 9999px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.2);
  font-size: 0.875rem;
  font-weight: 500;
  z-index: 10000;
  pointer-events: none;
}

.toast-icon {
  width: 1.125rem;
  height: 1.125rem;
  color: #10b981;
  flex-shrink: 0;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, 0.75rem);
}

/* Micro-Toast de Ferramentas no Topo do Leitor (F 0.7.2) */
.study-micro-toast {
  position: fixed;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--color-surface, #18181b);
  color: var(--color-text-primary, #ffffff);
  border: 1px solid var(--color-border, #3f3f46);
  border-radius: 9999px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25), 0 8px 10px -6px rgba(0, 0, 0, 0.15);
  font-size: 0.8125rem;
  font-weight: 500;
  z-index: 10001;
  pointer-events: none;
  white-space: nowrap;
}

.micro-toast-color-dot {
  width: 0.625rem;
  height: 0.625rem;
  border-radius: 9999px;
  display: inline-block;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.2);
}

.micro-toast-text {
  line-height: 1.25;
}

.floating-toast-fade-enter-active,
.floating-toast-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.floating-toast-fade-enter-from,
.floating-toast-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -0.5rem);
}

@media (prefers-reduced-motion: reduce) {
  .floating-toast-fade-enter-active,
  .floating-toast-fade-leave-active {
    transition: opacity 0.05s ease !important;
    transform: translateX(-50%) !important;
  }
}
</style>
