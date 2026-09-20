<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { api, errorMessage } from '../services/api'
import Icon from './ui/Icon.vue'
import type { ExportConfig, ExportFormat } from '../types'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    scope: 'book' | 'study'
    bookId: number
    studyId?: number | null
  }>(),
  {
    studyId: null,
  },
)

const emit = defineEmits<{
  (e: 'close'): void
}>()

const format = ref<ExportFormat>('markdown')
const includeNotes = ref(true)
const includeSections = ref(true)
const includeSource = ref(false)
const includeMetadata = ref(true)

const downloading = ref(false)
const downloadError = ref('')

const firstFocusable = ref<HTMLInputElement | null>(null)

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      downloadError.value = ''
      downloading.value = false
      nextTick(() => {
        firstFocusable.value?.focus()
      })
    }
  },
  { immediate: true },
)

function onKeyDown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    close()
  }
}

function close() {
  if (downloading.value) return
  emit('close')
}

async function handleDownload() {
  if (downloading.value) return
  downloading.value = true
  downloadError.value = ''

  const config: ExportConfig = {
    format: format.value,
    includeNotes: includeNotes.value,
    includeSections: includeSections.value,
    includeSource: includeSource.value,
    includeMetadata: includeMetadata.value,
  }

  try {
    if (props.scope === 'book') {
      await api.exportBook(props.bookId, config)
    } else if (props.scope === 'study' && props.studyId !== null) {
      await api.exportStudy(props.studyId, config)
    }
    emit('close')
  } catch (error) {
    downloadError.value = errorMessage(error)
  } finally {
    downloading.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="modal-backdrop"
      @click.self="close"
      @keydown="onKeyDown"
    >
      <div
        class="modal-dialog panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="export-modal-title"
      >
        <header class="modal-header">
          <div class="header-info">
            <span class="eyebrow">{{ scope === 'book' ? 'Exportar Livro' : 'Exportar Estudo' }}</span>
            <h2 id="export-modal-title">{{ title }}</h2>
          </div>
          <button
            type="button"
            class="modal-close"
            aria-label="Fechar diálogo de exportação"
            :disabled="downloading"
            @click="close"
          >
            <Icon name="x" :size="16" />
          </button>
        </header>

        <div class="modal-body">
          <div v-if="downloadError" class="notice error" role="alert">
            <p>{{ downloadError }}</p>
          </div>

          <fieldset class="export-fieldset">
            <legend class="fieldset-legend">Formato de Exportação</legend>
            <div class="format-options">
              <label class="radio-card" :class="{ selected: format === 'markdown' }">
                <input
                  ref="firstFocusable"
                  v-model="format"
                  type="radio"
                  name="export-format"
                  value="markdown"
                />
                <div class="format-details">
                  <strong class="format-name">Markdown (.md)</strong>
                  <span class="format-desc">Compatível com Obsidian, Notion e leitores modernos. Inclui Frontmatter YAML.</span>
                </div>
              </label>

              <label class="radio-card" :class="{ selected: format === 'text' }">
                <input
                  v-model="format"
                  type="radio"
                  name="export-format"
                  value="text"
                />
                <div class="format-details">
                  <strong class="format-name">Texto Puro (.txt)</strong>
                  <span class="format-desc">Texto simples legível com divisores ASCII, ideal para impressão ou anotação rápida.</span>
                </div>
              </label>
            </div>
          </fieldset>

          <fieldset class="export-fieldset">
            <legend class="fieldset-legend">Conteúdo a Incluir</legend>
            <div class="content-options">
              <label class="checkbox-row disabled-checkbox">
                <input
                  v-model="includeNotes"
                  type="checkbox"
                  disabled
                />
                <div class="checkbox-label">
                  <strong>Minhas Anotações</strong>
                  <span class="checkbox-desc">Suas reflexões pessoais manuscritas (sempre inclusas).</span>
                </div>
              </label>

              <label class="checkbox-row">
                <input
                  v-model="includeSections"
                  type="checkbox"
                />
                <div class="checkbox-label">
                  <strong>Seções de Estudo</strong>
                  <span class="checkbox-desc">Resumo, Explicação, Conceitos Principais e Referências.</span>
                </div>
              </label>

              <label class="checkbox-row">
                <input
                  v-model="includeMetadata"
                  type="checkbox"
                />
                <div class="checkbox-label">
                  <strong>Metadados e Cabeçalho</strong>
                  <span class="checkbox-desc">Autor, ano, categorias e data da exportação.</span>
                </div>
              </label>

              <label class="checkbox-row">
                <input
                  v-model="includeSource"
                  type="checkbox"
                />
                <div class="checkbox-label">
                  <strong>Fichamento da Fonte</strong>
                  <span class="checkbox-desc">Texto-base de apoio preservado na íntegra para consulta.</span>
                </div>
              </label>
            </div>
          </fieldset>
        </div>

        <footer class="modal-actions actions">
          <button
            type="button"
            class="secondary"
            :disabled="downloading"
            @click="close"
          >
            Cancelar
          </button>
          <button
            type="button"
            class="primary"
            :disabled="downloading"
            @click="handleDownload"
          >
            <span v-if="downloading" class="spinner" aria-hidden="true" />
            {{ downloading ? 'Gerando arquivo...' : 'Baixar arquivo' }}
          </button>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 1rem;
}

.modal-dialog {
  width: 100%;
  max-width: 520px;
  background: var(--color-bg, #fff);
  color: var(--color-text, #111);
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--color-border, #ddd);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border, #eee);
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.eyebrow {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-primary, #2b6cb0);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  line-height: 1.3;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  color: var(--color-text-muted, #666);
  border-radius: 4px;
}

.modal-close:hover:not(:disabled) {
  background: var(--color-bg-alt, #eee);
  color: var(--color-text, #111);
}

.modal-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-height: calc(85vh - 120px);
  overflow-y: auto;
}

.export-fieldset {
  border: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.fieldset-legend {
  font-size: 0.88rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
  color: var(--color-text, #222);
}

.format-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.radio-card {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  border: 1px solid var(--color-border, #ccc);
  background: var(--color-bg, #fff);
  cursor: pointer;
  transition: border-color 0.15s, background-color 0.15s;
}

.radio-card:hover {
  border-color: var(--color-primary, #2b6cb0);
  background: var(--color-bg-alt, #f8fafc);
}

.radio-card.selected {
  border-color: var(--color-primary, #2b6cb0);
  background: var(--color-bg-alt, #eff6ff);
}

.radio-card input[type="radio"] {
  margin-top: 0.2rem;
  cursor: pointer;
}

.format-details {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.format-name {
  font-size: 0.92rem;
  color: var(--color-text, #111);
}

.format-desc {
  font-size: 0.8rem;
  color: var(--color-text-muted, #666);
  line-height: 1.35;
}

.content-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.checkbox-row {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  background: var(--color-bg, #fff);
  cursor: pointer;
  transition: background-color 0.15s;
}

.checkbox-row:hover:not(.disabled-checkbox) {
  background: var(--color-bg-alt, #f8fafc);
}

.disabled-checkbox {
  opacity: 0.75;
  cursor: not-allowed;
  background: var(--color-bg-alt, #f8fafc);
}

.checkbox-row input[type="checkbox"] {
  margin-top: 0.2rem;
  cursor: pointer;
}

.disabled-checkbox input[type="checkbox"] {
  cursor: not-allowed;
}

.checkbox-label {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.checkbox-label strong {
  font-size: 0.88rem;
  color: var(--color-text, #111);
}

.checkbox-desc {
  font-size: 0.78rem;
  color: var(--color-text-muted, #666);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background-color: var(--color-bg-alt, #fafafa);
  border-top: 1px solid var(--color-border, #eee);
}

button {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

button.secondary {
  background: var(--color-bg, #fff);
  border-color: var(--color-border, #ccc);
  color: var(--color-text, #333);
}

button.secondary:hover:not(:disabled) {
  background: var(--color-bg-alt, #f0f0f0);
}

button.primary {
  background: var(--color-primary, #2b6cb0);
  color: #fff;
}

button.primary:hover:not(:disabled) {
  background: var(--color-primary-hover, #2c5282);
}

.spinner {
  width: 0.9rem;
  height: 0.9rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
