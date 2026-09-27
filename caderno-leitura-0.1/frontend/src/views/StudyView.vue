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
import FloatingActionsToolbar from '../components/FloatingActionsToolbar.vue'
import HighlightActionPopover from '../components/HighlightActionPopover.vue'
import { useStudyHighlights } from '../composables/useStudyHighlights'
import { useActiveReadingSession } from '../composables/useActiveReadingSession'
import { formatQuoteText, useTextSelection } from '../composables/useTextSelection'
import type { HighlightClickEvent } from '../utils/highlightRenderer'
import type { HighlightColor, ResourceVisibility, StudySectionKey, TextSelectionContext } from '../types.ts'

const route = useRoute()
const router = useRouter()
const resource = useStudyResource(api)
const { state } = resource

const exportModalOpen = ref(false)
const confirmTrashOpen = ref(false)
const createRelationModalOpen = ref(false)
const shareModalOpen = ref(false)
const relationsListRef = ref<InstanceType<typeof StudyRelationsList> | null>(null)
const trashing = ref(false)
const trashError = ref('')

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

// Feedback visual (Toast)
const toastMessage = ref('')
let toastTimer: ReturnType<typeof setTimeout> | null = null

function showToast(message: string) {
  toastMessage.value = message
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
  }, 3000)
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
    showToast('Trecho destacado com sucesso!')
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
    showToast('Anotação vinculada com sucesso!')
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
    showToast('Citação copiada para a área de transferência!')
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
    showToast('Trecho ocultado para estudo ativo!')
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
    showToast('Pergunta criada com sucesso!')
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
      <RouterLink to="/">Meus livros</RouterLink><span aria-hidden="true">/</span>
      <RouterLink :to="{ name: 'book', params: { bookId: state.context.book.id } }">{{ state.context.book.title }}</RouterLink><span aria-hidden="true">/</span>
      <RouterLink :to="{ name: 'book', params: { bookId: state.context.book.id }, query: { chapter: state.context.chapter.id } }">{{ state.context.chapter.name }}</RouterLink>
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
      <div>
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
          <p class="eyebrow" style="margin: 0;">Estudo</p>
          <StudyStatusBadge
            :status="state.context.study.reading_status || 'rascunho'"
            :study-id="state.context.study.id"
            :interactive="canEdit"
            @change="(newSt) => { if (state.context) state.context.study.reading_status = newSt }"
          />
        </div>
        <h1>{{ state.context.study.title }}</h1>
        <p class="intro">{{ state.context.study.location || 'Localização não informada' }}</p>
      </div>
      <div class="header-actions">
        <button
          v-if="canEdit"
          type="button"
          class="secondary share-action"
          aria-label="Compartilhar estudo e gerenciar permissões"
          @click="shareModalOpen = true"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          Compartilhar
        </button>
        <button type="button" class="secondary" @click="exportModalOpen = true">Exportar estudo</button>
        <RouterLink
          v-if="canEdit"
          class="button secondary"
          :to="{ name: 'study-edit', params: { bookId: state.context.book.id, studyId: state.context.study.id } }"
        >
          Editar estudo
        </RouterLink>
        <button
          v-if="canEdit"
          type="button"
          class="secondary danger-action"
          @click="confirmTrashOpen = true"
        >
          Mover para a lixeira
        </button>
      </div>
    </header>
    <ReaderTools
      :key="state.context.study.id"
      :active-reading-enabled="activeReadingSession.isActive.value"
      :interactive-count="totalInteractiveCount"
      @toggle-active-reading="handleToggleActiveReading"
    />

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
      <StudyTabs
        ref="studyTabsRef"
        :key="state.context.study.id"
        :id-prefix="`study-${state.context.study.id}`"
        :sections="state.context.study"
        :highlights="highlights"
        @highlight-click="handleHighlightClick"
        @active-section-change="(key) => { activeSection = key; clearSelection(); }"
      />
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

    <!-- Barra Flutuante Contextual de Ações (F0.6.2) -->
    <FloatingActionsToolbar
      :visible="Boolean(selectionContext)"
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
      @close="clearSelection"
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
  gap: calc(var(--space-unit) * 0.75);
}

.share-action {
  display: inline-flex;
  align-items: center;
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

.danger-action {
  color: var(--color-danger, #b91c1c);
}

.danger-action:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-danger, #b91c1c);
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
</style>
