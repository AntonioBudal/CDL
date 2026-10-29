<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { STUDY_TEMPLATES, getStudyTemplate } from '../../constants/studyTemplates.ts'
import type { StudyTemplateId, StudyTemplateDefinition } from '../../types.ts'

const props = defineProps<{
  currentTemplateId: StudyTemplateId
}>()

const emit = defineEmits<{
  (e: 'select', templateId: StudyTemplateId): void
  (e: 'close'): void
}>()

const selectedId = ref<StudyTemplateId>(props.currentTemplateId)
const activePreviewTemplate = computed<StudyTemplateDefinition>(() => {
  return getStudyTemplate(selectedId.value)
})

function handleSelect(id: StudyTemplateId) {
  selectedId.value = id
}

function handleConfirm() {
  emit('select', selectedId.value)
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    e.preventDefault()
    emit('close')
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <div
    class="template-modal-overlay"
    role="dialog"
    aria-modal="true"
    aria-labelledby="template-modal-title"
    @click.self="emit('close')"
  >
    <div class="template-modal-container">
      <!-- Cabeçalho do Diálogo -->
      <header class="modal-header">
        <div>
          <span class="modal-badge">Roteiros Cognitivos</span>
          <h2 id="template-modal-title" class="modal-title">
            Modelos Estruturados de Análise
          </h2>
          <p class="modal-description">
            Selecione um modelo analítico para guiar sua investigação intelectual sem alterar a estrutura de 4 seções do Leitorum.
          </p>
        </div>
        <button
          type="button"
          class="btn-close-modal"
          aria-label="Fechar diálogo de templates"
          title="Fechar (Esc)"
          @click="emit('close')"
        >
          &times;
        </button>
      </header>

      <!-- Corpo com 2 colunas: Lista de Modelos e Prévia Detalhada -->
      <div class="modal-body-layout">
        <!-- Coluna da Esquerda: Lista de Opções -->
        <div class="templates-list-pane" role="radiogroup" aria-label="Selecione um template de estudo">
          <div
            v-for="tpl in STUDY_TEMPLATES"
            :key="tpl.id"
            class="template-card"
            :class="{ active: selectedId === tpl.id, current: currentTemplateId === tpl.id }"
            role="radio"
            :aria-checked="selectedId === tpl.id"
            tabindex="0"
            @click="handleSelect(tpl.id)"
            @keydown.enter.prevent="handleSelect(tpl.id)"
            @keydown.space.prevent="handleSelect(tpl.id)"
          >
            <div class="card-meta">
              <span class="card-badge">{{ tpl.badgeLabel }}</span>
              <span v-if="currentTemplateId === tpl.id" class="card-current-tag">Atual</span>
            </div>
            <h3 class="card-name">{{ tpl.name }}</h3>
            <p class="card-desc">{{ tpl.shortDescription }}</p>
          </div>
        </div>

        <!-- Coluna da Direita: Painel de Prévia do Roteiro -->
        <div class="template-preview-pane">
          <div class="preview-header">
            <h4 class="preview-title">
              Estrutura de: {{ activePreviewTemplate.name }}
            </h4>
            <p class="preview-purpose">
              {{ activePreviewTemplate.detailedPurpose }}
            </p>
          </div>

          <div class="preview-sections-grid">
            <div class="preview-section-item">
              <div class="section-tag-header">
                <span class="section-pill summary-pill">Resumo</span>
                <span class="section-target-label">{{ activePreviewTemplate.sections.summary.label }}</span>
              </div>
              <p class="section-hint">{{ activePreviewTemplate.sections.summary.hint }}</p>
              <pre class="section-code">{{ activePreviewTemplate.sections.summary.skeleton }}</pre>
            </div>

            <div class="preview-section-item">
              <div class="section-tag-header">
                <span class="section-pill explanation-pill">Explicação</span>
                <span class="section-target-label">{{ activePreviewTemplate.sections.explanation.label }}</span>
              </div>
              <p class="section-hint">{{ activePreviewTemplate.sections.explanation.hint }}</p>
              <pre class="section-code">{{ activePreviewTemplate.sections.explanation.skeleton }}</pre>
            </div>

            <div class="preview-section-item">
              <div class="section-tag-header">
                <span class="section-pill concepts-pill">Conceitos</span>
                <span class="section-target-label">{{ activePreviewTemplate.sections.concepts.label }}</span>
              </div>
              <p class="section-hint">{{ activePreviewTemplate.sections.concepts.hint }}</p>
              <pre class="section-code">{{ activePreviewTemplate.sections.concepts.skeleton }}</pre>
            </div>

            <div class="preview-section-item">
              <div class="section-tag-header">
                <span class="section-pill references-pill">Referências</span>
                <span class="section-target-label">{{ activePreviewTemplate.sections.references.label }}</span>
              </div>
              <p class="section-hint">{{ activePreviewTemplate.sections.references.hint }}</p>
              <pre class="section-code">{{ activePreviewTemplate.sections.references.skeleton }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Rodapé de Ações -->
      <footer class="modal-footer">
        <button
          type="button"
          class="btn-secondary"
          @click="emit('close')"
        >
          Cancelar
        </button>
        <button
          type="button"
          class="btn-primary"
          @click="handleConfirm"
        >
          Aplicar este Template
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.template-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background-color: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.template-modal-container {
  width: 100%;
  max-width: 920px;
  max-height: 90vh;
  background-color: var(--color-bg, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: 1.5rem 1.75rem 1.25rem;
  border-bottom: 1px solid var(--color-border-subtle, #e5e7eb);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.modal-badge {
  display: inline-block;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-link, #2563eb);
  background-color: var(--color-accent-subtle, #eff6ff);
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  margin-bottom: 0.375rem;
}

.modal-title {
  font-family: var(--font-serif, "EB Garamond", serif);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text, #111827);
  margin: 0 0 0.25rem 0;
}

.modal-description {
  font-size: 0.875rem;
  color: var(--color-text-muted, #6b7280);
  margin: 0;
  line-height: 1.4;
}

.btn-close-modal {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background-color: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 1.5rem;
  color: var(--color-text-muted, #6b7280);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-close-modal:hover {
  background-color: var(--color-bg-subtle, #f3f4f6);
  color: var(--color-text, #111827);
}

.modal-body-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 320px 1fr;
  overflow: hidden;
  min-height: 0;
}

.templates-list-pane {
  padding: 1.25rem;
  overflow-y: auto;
  border-right: 1px solid var(--color-border-subtle, #e5e7eb);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background-color: var(--color-bg-subtle, #f9fafb);
}

.template-card {
  padding: 1rem;
  background-color: var(--color-bg, #ffffff);
  border: 1px solid var(--color-border-subtle, #e5e7eb);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  outline: none;
}

.template-card:hover {
  border-color: var(--color-border-accent, #93c5fd);
  background-color: #fbfdff;
}

.template-card:focus-visible {
  border-color: var(--color-accent, #2563eb);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

.template-card.active {
  border-color: var(--color-accent, #2563eb);
  background-color: var(--color-accent-subtle, #eff6ff);
  box-shadow: 0 1px 3px rgba(37, 99, 235, 0.1);
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.375rem;
}

.card-badge {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-link, #2563eb);
}

.card-current-tag {
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-success, #16a34a);
  background-color: #f0fdf4;
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
}

.card-name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text, #111827);
  margin: 0 0 0.25rem 0;
}

.card-desc {
  font-size: 0.8125rem;
  color: var(--color-text-muted, #6b7280);
  margin: 0;
  line-height: 1.35;
}

.template-preview-pane {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.preview-header {
  border-bottom: 1px solid var(--color-border-subtle, #f3f4f6);
  padding-bottom: 0.875rem;
}

.preview-title {
  font-size: 1.0625rem;
  font-weight: 600;
  color: var(--color-text, #111827);
  margin: 0 0 0.375rem 0;
}

.preview-purpose {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #4b5563);
  margin: 0;
  line-height: 1.45;
}

.preview-sections-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preview-section-item {
  background-color: var(--color-bg-subtle, #f9fafb);
  border: 1px solid var(--color-border-subtle, #e5e7eb);
  border-radius: 8px;
  padding: 0.875rem 1rem;
}

.section-tag-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.375rem;
}

.section-pill {
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
}

.summary-pill {
  background-color: #dbeafe;
  color: #1e40af;
}

.explanation-pill {
  background-color: #e0e7ff;
  color: #3730a3;
}

.concepts-pill {
  background-color: #fef3c7;
  color: #92400e;
}

.references-pill {
  background-color: #f3e8ff;
  color: #6b21a8;
}

.section-target-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text, #111827);
}

.section-hint {
  font-size: 0.75rem;
  color: var(--color-text-muted, #6b7280);
  margin: 0 0 0.5rem 0;
}

.section-code {
  font-family: var(--font-mono, monospace);
  font-size: 0.75rem;
  background-color: var(--color-bg, #ffffff);
  border: 1px solid var(--color-border-subtle, #e5e7eb);
  border-radius: 4px;
  padding: 0.5rem 0.75rem;
  margin: 0;
  color: var(--color-text-secondary, #374151);
  white-space: pre-wrap;
  line-height: 1.4;
}

.modal-footer {
  padding: 1rem 1.75rem;
  border-top: 1px solid var(--color-border-subtle, #e5e7eb);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  background-color: var(--color-bg, #ffffff);
}

.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-primary {
  background-color: var(--color-accent, #2563eb);
  color: #ffffff;
  border: 1px solid transparent;
}

.btn-primary:hover {
  background-color: var(--color-accent-hover, #1d4ed8);
}

.btn-secondary {
  background-color: transparent;
  color: var(--color-text, #374151);
  border: 1px solid var(--color-border, #d1d5db);
}

.btn-secondary:hover {
  background-color: var(--color-bg-subtle, #f3f4f6);
}

@media (max-width: 768px) {
  .template-modal-container {
    max-height: 95vh;
  }
  .modal-body-layout {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }
  .templates-list-pane {
    border-right: none;
    border-bottom: 1px solid var(--color-border-subtle, #e5e7eb);
    max-height: 220px;
  }
  .modal-footer {
    flex-direction: column-reverse;
  }
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
