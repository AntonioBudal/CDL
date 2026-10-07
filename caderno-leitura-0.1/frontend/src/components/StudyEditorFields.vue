<script setup lang="ts">
import { nextTick, ref } from 'vue'
import {
  SECTION_LABELS,
  EDITOR_SECTION_TABS,
  type AnalysisSections,
  type EditorSectionTabKey,
  type EditorViewMode,
  type StudyCandidateOption,
} from '../types'
import MarkdownToolbar from './MarkdownToolbar.vue'
import MarkdownContent from './MarkdownContent.vue'
import { searchStudyCandidates } from '../services/api'

defineProps<{ idPrefix: string; showMetadata?: boolean }>()
const title = defineModel<string>('title', { required: true })
const location = defineModel<string>('location', { required: true })
const notes = defineModel<string>('notes', { required: true })
const sections = defineModel<AnalysisSections>('sections', { required: true })

const activeTab = ref<EditorSectionTabKey>('summary')
const viewMode = ref<EditorViewMode>('focused')
const previewState = ref<Record<string, boolean>>({})

// Estado de autocomplete de menções contextuais [[...]]
interface MentionAutocompleteState {
  isOpen: boolean
  query: string
  triggerIndex: number
  sectionKey: keyof AnalysisSections | 'notes' | ''
  textareaEl: HTMLTextAreaElement | null
  candidates: StudyCandidateOption[]
  selectedIndex: number
  isLoading: boolean
}

const mentionState = ref<MentionAutocompleteState>({
  isOpen: false,
  query: '',
  triggerIndex: -1,
  sectionKey: '',
  textareaEl: null,
  candidates: [],
  selectedIndex: 0,
  isLoading: false,
})

let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

function togglePreview(key: string) {
  previewState.value[key] = !previewState.value[key]
}

function isPreviewing(key: string): boolean {
  return Boolean(previewState.value[key])
}

function hasContent(key: EditorSectionTabKey): boolean {
  if (key === 'notes') return Boolean(notes.value?.trim())
  return Boolean(sections.value[key]?.trim())
}

function closeMentionMenu() {
  mentionState.value.isOpen = false
  mentionState.value.candidates = []
  mentionState.value.selectedIndex = 0
  mentionState.value.textareaEl = null
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }
}

function checkMentionTrigger(key: keyof AnalysisSections | 'notes', textarea: HTMLTextAreaElement) {
  const cursor = textarea.selectionStart
  const textBefore = textarea.value.slice(0, cursor)
  const lastTrigger = textBefore.lastIndexOf('[[')

  if (lastTrigger === -1) {
    closeMentionMenu()
    return
  }

  const queryCandidate = textBefore.slice(lastTrigger + 2)
  if (queryCandidate.includes('\n') || queryCandidate.includes(']]')) {
    closeMentionMenu()
    return
  }

  mentionState.value.isOpen = true
  mentionState.value.query = queryCandidate.trim()
  mentionState.value.triggerIndex = lastTrigger
  mentionState.value.sectionKey = key
  mentionState.value.textareaEl = textarea

  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  mentionState.value.isLoading = true
  searchDebounceTimer = setTimeout(async () => {
    try {
      const results = await searchStudyCandidates(mentionState.value.query, 8)
      mentionState.value.candidates = results
      mentionState.value.selectedIndex = 0
    } catch {
      mentionState.value.candidates = []
    } finally {
      mentionState.value.isLoading = false
    }
  }, 120)
}

function handleTextareaInput(key: keyof AnalysisSections | 'notes', event: Event) {
  const target = event.target as HTMLTextAreaElement
  if (key === 'notes') {
    notes.value = target.value
  } else {
    sections.value = { ...sections.value, [key]: target.value }
  }
  checkMentionTrigger(key, target)
}

function handleTextareaKeyDown(_key: keyof AnalysisSections | 'notes', event: KeyboardEvent) {
  if (!mentionState.value.isOpen) return

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    if (mentionState.value.candidates.length > 0) {
      mentionState.value.selectedIndex =
        (mentionState.value.selectedIndex + 1) % mentionState.value.candidates.length
    }
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    if (mentionState.value.candidates.length > 0) {
      mentionState.value.selectedIndex =
        (mentionState.value.selectedIndex - 1 + mentionState.value.candidates.length) %
        mentionState.value.candidates.length
    }
  } else if (event.key === 'Enter' || event.key === 'Tab') {
    if (
      mentionState.value.candidates.length > 0 &&
      mentionState.value.selectedIndex >= 0 &&
      mentionState.value.selectedIndex < mentionState.value.candidates.length
    ) {
      event.preventDefault()
      selectMentionCandidate(mentionState.value.candidates[mentionState.value.selectedIndex])
    }
  } else if (event.key === 'Escape') {
    event.preventDefault()
    closeMentionMenu()
  }
}

function handleTextareaBlur() {
  setTimeout(() => {
    closeMentionMenu()
  }, 200)
}

function selectMentionCandidate(candidate: StudyCandidateOption) {
  const textarea = mentionState.value.textareaEl
  if (!textarea) return

  const key = mentionState.value.sectionKey
  const triggerIdx = mentionState.value.triggerIndex
  const cursor = textarea.selectionStart

  // Verifica se há estudos homônimos nos resultados para aplicar desambiguação por ID
  const hasDuplicateTitle = mentionState.value.candidates.some(
    (c) => c.id !== candidate.id && c.title.trim().toLowerCase() === candidate.title.trim().toLowerCase()
  )

  const mentionToken = hasDuplicateTitle
    ? `[[${candidate.title}|${candidate.id}]]`
    : `[[${candidate.title}]]`

  const currentVal = textarea.value
  const before = currentVal.slice(0, triggerIdx)
  const after = currentVal.slice(cursor)
  const nextVal = `${before}${mentionToken} ${after}`

  if (key === 'notes') {
    notes.value = nextVal
  } else if (key) {
    sections.value = { ...sections.value, [key]: nextVal }
  }

  const nextPos = before.length + mentionToken.length + 1
  closeMentionMenu()

  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(nextPos, nextPos)
  })
}
</script>

<template>
  <div v-if="showMetadata" class="form-grid">
    <div class="field">
      <label :for="`${idPrefix}-title`">Título do estudo</label>
      <input :id="`${idPrefix}-title`" v-model="title" required />
    </div>
    <div class="field">
      <label :for="`${idPrefix}-location`">Página ou localização <span class="optional">opcional</span></label>
      <input :id="`${idPrefix}-location`" v-model="location" placeholder="Ex.: p. 32–34 ou Loc. 1820" />
    </div>
  </div>

  <div class="editor-tabs-bar">
    <div class="tabs-scroll-container" role="tablist" aria-label="Navegação por seções de estudo">
      <button
        v-for="tab in EDITOR_SECTION_TABS"
        :key="tab.key"
        type="button"
        role="tab"
        :id="`${idPrefix}-tab-${tab.key}`"
        :aria-selected="activeTab === tab.key"
        :aria-controls="`${idPrefix}-panel-${tab.key}`"
        class="editor-tab-pill"
        :class="{ 'is-active': activeTab === tab.key, 'has-content': hasContent(tab.key) }"
        @click="activeTab = tab.key"
      >
        <span class="tab-label">{{ tab.label }}</span>
        <span
          v-if="hasContent(tab.key)"
          class="tab-indicator"
          title="Seção com conteúdo preenchido"
          aria-hidden="true"
        >•</span>
      </button>
    </div>

    <button
      type="button"
      class="view-mode-toggle-btn secondary"
      :aria-label="viewMode === 'focused' ? 'Alternar para ver todas as seções' : 'Alternar para modo focado'"
      @click="viewMode = viewMode === 'focused' ? 'all' : 'focused'"
    >
      {{ viewMode === 'focused' ? 'Ver todas as seções' : 'Modo focado' }}
    </button>
  </div>

  <p :id="`${idPrefix}-format-hint`" class="field-hint">
    Nas seções, use a barra de ferramentas ou digite Markdown para formatar títulos, listas, citações, links e digite <code>[[</code> para autocompletar menções a outros estudos.
  </p>

  <div class="analysis-grid" :class="{ 'is-focused-mode': viewMode === 'focused' }">
    <template v-for="section in SECTION_LABELS" :key="section.key">
      <div
        v-show="viewMode === 'all' || activeTab === section.key"
        :id="`${idPrefix}-panel-${section.key}`"
        class="field field-with-toolbar"
        role="tabpanel"
        :aria-labelledby="`${idPrefix}-tab-${section.key}`"
      >
        <div class="section-header">
          <label :for="`${idPrefix}-${section.key}`">{{ section.label }}</label>
          <button
            type="button"
            class="preview-toggle-btn"
            :title="isPreviewing(section.key) ? 'Voltar para edição' : 'Alternar prévia de Markdown'"
            :aria-label="`Alternar prévia de ${section.label}`"
            @click="togglePreview(section.key)"
          >
            {{ isPreviewing(section.key) ? 'Editar' : 'Prévia' }}
          </button>
        </div>

        <template v-if="isPreviewing(section.key)">
          <div :id="`${idPrefix}-${section.key}-preview`" class="preview-box panel">
            <MarkdownContent :content="sections[section.key] || '*Nenhum conteúdo preenchido nesta seção.*'" />
          </div>
        </template>
        <template v-else>
          <MarkdownToolbar :target-id="`${idPrefix}-${section.key}`" />
          <div class="textarea-wrapper">
            <textarea
              :id="`${idPrefix}-${section.key}`"
              :value="sections[section.key]"
              rows="9"
              class="textarea-with-toolbar"
              :aria-describedby="`${idPrefix}-format-hint`"
              :placeholder="`${section.label}: revise ou complete o conteúdo. Digite [[ para vincular estudos.`"
              @input="handleTextareaInput(section.key, $event)"
              @keydown="handleTextareaKeyDown(section.key, $event)"
              @blur="handleTextareaBlur"
            ></textarea>

            <!-- Popover de Autocomplete de Menções -->
            <div
              v-if="mentionState.isOpen && mentionState.sectionKey === section.key"
              class="study-mention-autocomplete-menu"
              role="listbox"
              aria-label="Sugestões de estudos para menção"
            >
              <div v-if="mentionState.isLoading" class="mention-autocomplete-status">
                Buscando estudos no acervo...
              </div>
              <div v-else-if="mentionState.candidates.length === 0" class="mention-autocomplete-empty">
                Nenhum estudo encontrado para "{{ mentionState.query }}"
              </div>
              <div v-else class="mention-candidates-list">
                <button
                  v-for="(candidate, idx) in mentionState.candidates"
                  :key="candidate.id"
                  type="button"
                  role="option"
                  :aria-selected="mentionState.selectedIndex === idx"
                  class="mention-candidate-item"
                  :class="{ 'is-selected': mentionState.selectedIndex === idx }"
                  @mouseenter="mentionState.selectedIndex = idx"
                  @mousedown.prevent="selectMentionCandidate(candidate)"
                  @click="selectMentionCandidate(candidate)"
                >
                  <div class="mention-candidate-title">{{ candidate.title }}</div>
                  <div class="mention-candidate-meta">
                    <span class="mention-candidate-book">{{ candidate.book_title }}</span>
                    <span v-if="candidate.chapter_name" class="mention-candidate-sep">·</span>
                    <span v-if="candidate.chapter_name" class="mention-candidate-chapter">{{ candidate.chapter_name }}</span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </template>
  </div>

  <div
    v-show="viewMode === 'all' || activeTab === 'notes'"
    :id="`${idPrefix}-panel-notes`"
    class="field notes-field field-with-toolbar"
    role="tabpanel"
    :aria-labelledby="`${idPrefix}-tab-notes`"
  >
    <div class="section-header">
      <label :for="`${idPrefix}-notes`">Minhas anotações e interpretações <span class="optional">opcional</span></label>
      <button
        type="button"
        class="preview-toggle-btn"
        :title="isPreviewing('notes') ? 'Voltar para edição' : 'Alternar prévia de Markdown'"
        aria-label="Alternar prévia de anotações"
        @click="togglePreview('notes')"
      >
        {{ isPreviewing('notes') ? 'Editar' : 'Prévia' }}
      </button>
    </div>

    <template v-if="isPreviewing('notes')">
      <div :id="`${idPrefix}-notes-preview`" class="preview-box panel">
        <MarkdownContent :content="notes || '*Nenhuma anotação preenchida.*'" />
      </div>
    </template>
    <template v-else>
      <MarkdownToolbar :target-id="`${idPrefix}-notes`" />
      <div class="textarea-wrapper">
        <textarea
          :id="`${idPrefix}-notes`"
          v-model="notes"
          rows="6"
          class="textarea-with-toolbar"
          placeholder="Suas reflexões sobre esta passagem… Digite [[ para vincular estudos."
          @input="handleTextareaInput('notes', $event)"
          @keydown="handleTextareaKeyDown('notes', $event)"
          @blur="handleTextareaBlur"
        ></textarea>

        <!-- Popover de Autocomplete em Notas -->
        <div
          v-if="mentionState.isOpen && mentionState.sectionKey === 'notes'"
          class="study-mention-autocomplete-menu"
          role="listbox"
          aria-label="Sugestões de estudos para menção em notas"
        >
          <div v-if="mentionState.isLoading" class="mention-autocomplete-status">
            Buscando estudos no acervo...
          </div>
          <div v-else-if="mentionState.candidates.length === 0" class="mention-autocomplete-empty">
            Nenhum estudo encontrado para "{{ mentionState.query }}"
          </div>
          <div v-else class="mention-candidates-list">
            <button
              v-for="(candidate, idx) in mentionState.candidates"
              :key="candidate.id"
              type="button"
              role="option"
              :aria-selected="mentionState.selectedIndex === idx"
              class="mention-candidate-item"
              :class="{ 'is-selected': mentionState.selectedIndex === idx }"
              @mouseenter="mentionState.selectedIndex = idx"
              @mousedown.prevent="selectMentionCandidate(candidate)"
              @click="selectMentionCandidate(candidate)"
            >
              <div class="mention-candidate-title">{{ candidate.title }}</div>
              <div class="mention-candidate-meta">
                <span class="mention-candidate-book">{{ candidate.book_title }}</span>
                <span v-if="candidate.chapter_name" class="mention-candidate-sep">·</span>
                <span v-if="candidate.chapter_name" class="mention-candidate-chapter">{{ candidate.chapter_name }}</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.editor-tabs-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 0.75rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border, #e4e4e7);
}

.tabs-scroll-container {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
}

.tabs-scroll-container::-webkit-scrollbar {
  display: none;
}

.editor-tab-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.35rem 0.75rem;
  min-height: 36px;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--color-border, #e4e4e7);
  background: var(--color-surface-subtle, var(--color-surface, #ffffff));
  color: var(--color-text, #18181b);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
  user-select: none;
}

.editor-tab-pill:hover {
  background: var(--color-surface-hover, rgba(0, 0, 0, 0.05));
  border-color: var(--color-border-strong, #d4d4d8);
}

.editor-tab-pill.is-active {
  background: var(--color-primary, #3b82f6);
  color: #ffffff;
  border-color: var(--color-primary, #3b82f6);
}

.tab-indicator {
  font-size: 1rem;
  line-height: 0.8;
  color: var(--color-primary, #3b82f6);
}

.editor-tab-pill.is-active .tab-indicator {
  color: #ffffff;
}

.view-mode-toggle-btn {
  font-size: 0.75rem;
  padding: 0.3rem 0.65rem;
  min-height: 32px;
  cursor: pointer;
  white-space: nowrap;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.35rem;
}

.preview-toggle-btn {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  min-height: 28px;
  border-radius: 4px;
  border: 1px solid var(--color-border, #e4e4e7);
  background: transparent;
  color: var(--color-text-muted, #71717a);
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.preview-toggle-btn:hover {
  background: var(--color-surface-hover, rgba(0, 0, 0, 0.05));
  color: var(--color-text, #18181b);
}

.preview-box {
  min-height: 180px;
  padding: 0.875rem 1rem;
  border: 1px solid var(--color-border, #e4e4e7);
  border-radius: var(--radius-control, 6px);
  background: var(--color-surface, #ffffff);
  overflow-y: auto;
}

.field-with-toolbar {
  display: flex;
  flex-direction: column;
}

.textarea-wrapper {
  position: relative;
  width: 100%;
}

.textarea-with-toolbar {
  border-top-left-radius: 0 !important;
  border-top-right-radius: 0 !important;
  margin-top: -1px;
  width: 100%;
}

/* Menu de Autocomplete de Menções [[ */
.study-mention-autocomplete-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-width: 480px;
  margin-top: 4px;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #d4d4d8);
  border-radius: var(--radius-control, 6px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  z-index: 60;
  max-height: 260px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.mention-autocomplete-status,
.mention-autocomplete-empty {
  padding: 0.75rem 1rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted, #71717a);
  text-align: center;
}

.mention-candidates-list {
  display: flex;
  flex-direction: column;
}

.mention-candidate-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  width: 100%;
  min-height: 48px;
  padding: 0.5rem 0.875rem;
  border: none;
  background: transparent;
  color: var(--color-text, #18181b);
  text-align: left;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border-subtle, rgba(0, 0, 0, 0.05));
  transition: background-color 0.12s ease;
}

.mention-candidate-item:last-child {
  border-bottom: none;
}

.mention-candidate-item:hover,
.mention-candidate-item.is-selected {
  background: var(--color-surface-hover, #f4f4f5);
}

.mention-candidate-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text, #18181b);
  line-height: 1.25;
}

.mention-candidate-meta {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: var(--color-text-muted, #71717a);
  margin-top: 0.15rem;
}

.mention-candidate-sep {
  opacity: 0.6;
}
</style>
