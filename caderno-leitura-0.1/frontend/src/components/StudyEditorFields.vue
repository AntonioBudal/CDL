<script setup lang="ts">
import { ref } from 'vue'
import {
  SECTION_LABELS,
  EDITOR_SECTION_TABS,
  type AnalysisSections,
  type EditorSectionTabKey,
  type EditorViewMode,
} from '../types'
import MarkdownToolbar from './MarkdownToolbar.vue'
import MarkdownContent from './MarkdownContent.vue'

defineProps<{ idPrefix: string; showMetadata?: boolean }>()
const title = defineModel<string>('title', { required: true })
const location = defineModel<string>('location', { required: true })
const notes = defineModel<string>('notes', { required: true })
const sections = defineModel<AnalysisSections>('sections', { required: true })

const activeTab = ref<EditorSectionTabKey>('summary')
const viewMode = ref<EditorViewMode>('focused')
const previewState = ref<Record<string, boolean>>({})

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

function updateSection(key: keyof AnalysisSections, event: Event) {
  sections.value = { ...sections.value, [key]: (event.target as HTMLTextAreaElement).value }
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
    Nas seções, use a barra de ferramentas ou digite Markdown para formatar títulos, listas, negrito, itálico, citações e links.
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
          <textarea
            :id="`${idPrefix}-${section.key}`"
            :value="sections[section.key]"
            rows="9"
            class="textarea-with-toolbar"
            :aria-describedby="`${idPrefix}-format-hint`"
            :placeholder="`${section.label}: revise ou complete o conteúdo.`"
            @input="updateSection(section.key, $event)"
          ></textarea>
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
      <textarea
        :id="`${idPrefix}-notes`"
        v-model="notes"
        rows="6"
        class="textarea-with-toolbar"
        placeholder="Suas reflexões sobre esta passagem…"
      ></textarea>
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

.textarea-with-toolbar {
  border-top-left-radius: 0 !important;
  border-top-right-radius: 0 !important;
  margin-top: -1px;
}
</style>
