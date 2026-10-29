<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import {
  SECTION_LABELS,
  EDITOR_SECTION_TABS,
  type AnalysisSections,
  type EditorSectionTabKey,
  type EditorViewMode,
  type StudyCandidateOption,
  type StudyTemplateId,
} from '../types'
import { getStudyTemplate } from '../constants/studyTemplates'
import TemplateSelectorModal from './studies/TemplateSelectorModal.vue'
import MarkdownToolbar from './MarkdownToolbar.vue'
import MarkdownContent from './MarkdownContent.vue'
import { searchStudyCandidates } from '../services/api'

defineProps<{ idPrefix: string; showMetadata?: boolean }>()
const title = defineModel<string>('title', { required: true })
const location = defineModel<string>('location', { required: true })
const notes = defineModel<string>('notes', { required: true })
const sections = defineModel<AnalysisSections>('sections', { required: true })
const templateId = defineModel<StudyTemplateId>('templateId', { default: 'classico' })

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

// Gerenciamento e Aplicação de Templates Estruturados (F0.7.15)
const isTemplateModalOpen = ref(false)
const isConfirmSwitchModalOpen = ref(false)
const pendingTemplateId = ref<StudyTemplateId | null>(null)

const activeTemplateDef = computed(() => {
  return getStudyTemplate(templateId.value)
})

const pendingTemplateDef = computed(() => {
  return pendingTemplateId.value ? getStudyTemplate(pendingTemplateId.value) : null
})

function hasAnyAnalysisContent(): boolean {
  return Boolean(
    sections.value.summary?.trim() ||
    sections.value.explanation?.trim() ||
    sections.value.concepts?.trim() ||
    sections.value.references?.trim()
  )
}

function handleOpenTemplateModal() {
  isTemplateModalOpen.value = true
}

function handleCloseTemplateModal() {
  isTemplateModalOpen.value = false
}

function handleSelectTemplate(newTemplateId: StudyTemplateId) {
  isTemplateModalOpen.value = false
  if (newTemplateId === templateId.value) return

  if (hasAnyAnalysisContent()) {
    pendingTemplateId.value = newTemplateId
    isConfirmSwitchModalOpen.value = true
  } else {
    applyTemplateDirectly(newTemplateId)
  }
}

function applyTemplateDirectly(targetId: StudyTemplateId) {
  templateId.value = targetId
  const tpl = getStudyTemplate(targetId)
  sections.value = {
    summary: tpl.sections.summary.skeleton,
    explanation: tpl.sections.explanation.skeleton,
    concepts: tpl.sections.concepts.skeleton,
    references: tpl.sections.references.skeleton,
  }
}

function handleConfirmReplace() {
  if (pendingTemplateId.value) {
    applyTemplateDirectly(pendingTemplateId.value)
  }
  isConfirmSwitchModalOpen.value = false
  pendingTemplateId.value = null
}

function appendToSection(existing: string, skeleton: string): string {
  const trimmed = (existing || '').trim()
  if (!trimmed) return skeleton
  return `${trimmed}\n\n---\n\n${skeleton}`
}

function handleConfirmAppend() {
  if (pendingTemplateId.value) {
    const targetId = pendingTemplateId.value
    templateId.value = targetId
    const tpl = getStudyTemplate(targetId)
    sections.value = {
      summary: appendToSection(sections.value.summary, tpl.sections.summary.skeleton),
      explanation: appendToSection(sections.value.explanation, tpl.sections.explanation.skeleton),
      concepts: appendToSection(sections.value.concepts, tpl.sections.concepts.skeleton),
      references: appendToSection(sections.value.references, tpl.sections.references.skeleton),
    }
  }
  isConfirmSwitchModalOpen.value = false
  pendingTemplateId.value = null
}

function handleCancelSwitch() {
  isConfirmSwitchModalOpen.value = false
  pendingTemplateId.value = null
}

function onWindowKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && isConfirmSwitchModalOpen.value) {
    e.preventDefault()
    handleCancelSwitch()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onWindowKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onWindowKeydown)
})
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

  <!-- Barra de Modelo Estruturado de Estudo (F0.7.15) -->
  <div class="template-selector-banner">
    <div class="template-current-meta">
      <span class="template-category-pill">Modelo</span>
      <span class="template-active-name">{{ activeTemplateDef.name }}</span>
      <span class="template-active-desc">{{ activeTemplateDef.shortDescription }}</span>
    </div>
    <button
      type="button"
      class="template-change-btn secondary"
      aria-haspopup="dialog"
      aria-label="Alterar modelo analítico de estudo"
      @click="handleOpenTemplateModal"
    >
      Trocar Modelo
    </button>
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

  <!-- Modal de Seleção de Template -->
  <TemplateSelectorModal
    v-if="isTemplateModalOpen"
    :current-template-id="templateId"
    @select="handleSelectTemplate"
    @close="handleCloseTemplateModal"
  />

  <!-- Modal de Salvaguarda na Troca de Template (Q1: A) -->
  <div
    v-if="isConfirmSwitchModalOpen && pendingTemplateDef"
    class="template-confirm-overlay"
    role="dialog"
    aria-modal="true"
    aria-labelledby="confirm-switch-title"
    @click.self="handleCancelSwitch"
  >
    <div class="template-confirm-container">
      <header class="confirm-header">
        <span class="confirm-pill">Atenção</span>
        <h3 id="confirm-switch-title" class="confirm-title">
          Alteração de Modelo Analítico
        </h3>
        <p class="confirm-subtitle">
          Você já possui anotações registradas nas seções deste estudo. Como deseja aplicar a estrutura de <strong>{{ pendingTemplateDef.name }}</strong>?
        </p>
      </header>

      <div class="confirm-options">
        <button
          type="button"
          class="confirm-choice-card append-choice"
          @click="handleConfirmAppend"
        >
          <div class="choice-tag-wrap">
            <span class="choice-tag recommended">Recomendado</span>
          </div>
          <strong class="choice-title">Anexar ao Final</strong>
          <p class="choice-desc">
            Preserva 100% das suas anotações atuais intactas e adiciona o roteiro do novo modelo ao final de cada seção com um separador divisório.
          </p>
        </button>

        <button
          type="button"
          class="confirm-choice-card replace-choice"
          @click="handleConfirmReplace"
        >
          <div class="choice-tag-wrap">
            <span class="choice-tag warning">Sobrescrita</span>
          </div>
          <strong class="choice-title">Substituir Conteúdo</strong>
          <p class="choice-desc">
            Substitui todo o conteúdo das quatro seções analíticas pelos esqueletos em branco do novo modelo.
          </p>
        </button>
      </div>

      <footer class="confirm-footer">
        <button
          type="button"
          class="btn-cancel-switch secondary"
          @click="handleCancelSwitch"
        >
          Cancelar
        </button>
      </footer>
    </div>
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
  color: var(--color-link, #3b82f6);
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

/* Banner de Modelo Estruturado (F0.7.15) */
.template-selector-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 1rem;
  margin-top: 0.75rem;
  margin-bottom: 0.75rem;
  background-color: var(--color-surface, #f8fafc);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  flex-wrap: wrap;
}

.template-current-meta {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-wrap: wrap;
  flex: 1;
  min-width: 240px;
}

.template-category-pill {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  background-color: var(--color-accent-subtle, #eff6ff);
  color: var(--color-link, #2563eb);
}

.template-active-name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
}

.template-active-desc {
  font-size: 0.8125rem;
  color: var(--color-text-muted, #64748b);
}

.template-change-btn {
  min-height: 44px;
  min-width: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
}

/* Modal de Salvaguarda na Troca de Template */
.template-confirm-overlay {
  position: fixed;
  inset: 0;
  z-index: 120;
  background-color: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.template-confirm-container {
  width: 100%;
  max-width: 580px;
  background-color: var(--color-bg, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.confirm-header {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.confirm-pill {
  display: inline-block;
  align-self: flex-start;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-warning-text, #b45309);
  background-color: var(--color-warning-subtle, #fef3c7);
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
}

.confirm-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text, #0f172a);
  margin: 0;
}

.confirm-subtitle {
  font-size: 0.875rem;
  line-height: 1.45;
  color: var(--color-text-muted, #4b5563);
  margin: 0;
}

.confirm-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.confirm-choice-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  padding: 1rem;
  min-height: 44px;
  border-radius: 8px;
  border: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-surface, #f9fafb);
  cursor: pointer;
  transition: all 0.15s ease;
}

.confirm-choice-card:hover,
.confirm-choice-card:focus-visible {
  border-color: var(--color-accent, #2563eb);
  background-color: var(--color-surface-hover, #f3f4f6);
  outline: 2px solid var(--color-accent, #2563eb);
  outline-offset: 1px;
}

.choice-tag-wrap {
  margin-bottom: 0.375rem;
}

.choice-tag {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
}

.choice-tag.recommended {
  background-color: var(--color-accent-subtle, #eff6ff);
  color: var(--color-link, #2563eb);
}

.choice-tag.warning {
  background-color: var(--color-danger-subtle, #fee2e2);
  color: var(--color-danger-text, #b91c1c);
}

.choice-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text, #111827);
  margin-bottom: 0.25rem;
}

.choice-desc {
  font-size: 0.8125rem;
  line-height: 1.4;
  color: var(--color-text-muted, #6b7280);
  margin: 0;
}

.confirm-footer {
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--color-border-subtle, #f3f4f6);
  padding-top: 1rem;
}

.btn-cancel-switch {
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  border-radius: 6px;
  cursor: pointer;
}
</style>
