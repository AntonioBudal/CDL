<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import type { CandidateStudyItem, StudyRelationItem, StudyRelationType } from '../../types'
import { RELATION_TYPE_LABELS } from '../../composables/useStudyRelations'
import { createStudyRelation, searchCandidateStudies, errorMessage } from '../../services/api'
import Icon from '../ui/Icon.vue'

interface Props {
  open: boolean
  sourceStudyId: number
  sourceStudyTitle?: string
}

const props = withDefaults(defineProps<Props>(), {
  sourceStudyTitle: '',
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'relation-created', item: StudyRelationItem): void
}>()

const RELATION_TYPES: StudyRelationType[] = [
  'relacionado_com',
  'complementa',
  'contradiz',
  'depende_de',
  'mesmo_tema',
  'desdobramento_de',
]

const searchQuery = ref('')
const candidates = ref<CandidateStudyItem[]>([])
const selectedStudy = ref<CandidateStudyItem | null>(null)
const selectedType = ref<StudyRelationType>('relacionado_com')
const description = ref('')
const searching = ref(false)
const submitting = ref(false)
const errorNotice = ref<string | null>(null)

const searchInputRef = ref<HTMLInputElement | null>(null)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

async function executeSearch() {
  if (!props.sourceStudyId) return
  searching.value = true
  errorNotice.value = null
  try {
    const results = await searchCandidateStudies(props.sourceStudyId, searchQuery.value.trim())
    candidates.value = results
  } catch (err) {
    errorNotice.value = errorMessage(err)
  } finally {
    searching.value = false
  }
}

function handleSearchInput() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    executeSearch()
  }, 250)
}

function selectCandidate(study: CandidateStudyItem) {
  selectedStudy.value = study
}

function handleKeyDown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    close()
  }
}

function close() {
  if (submitting.value) return
  emit('close')
}

async function handleCreate() {
  if (!selectedStudy.value || submitting.value) return
  submitting.value = true
  errorNotice.value = null
  try {
    const created = await createStudyRelation(props.sourceStudyId, {
      target_study_id: selectedStudy.value.id,
      relation_type: selectedType.value,
      description: description.value.trim(),
    })
    emit('relation-created', created)
    close()
  } catch (err) {
    errorNotice.value = errorMessage(err)
  } finally {
    submitting.value = false
  }
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      searchQuery.value = ''
      selectedStudy.value = null
      selectedType.value = 'relacionado_com'
      description.value = ''
      errorNotice.value = null
      executeSearch()
      nextTick(() => {
        searchInputRef.value?.focus()
      })
    }
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="modal-backdrop"
      @click.self="close"
      @keydown="handleKeyDown"
    >
      <div
        class="modal-dialog panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <header class="modal-header">
          <div class="header-title-wrap">
            <Icon name="network" :size="20" class="header-icon" />
            <h2 id="modal-title" class="header-title">Conectar Estudo</h2>
          </div>
          <button
            type="button"
            class="modal-close-btn"
            aria-label="Fechar janela"
            :disabled="submitting"
            @click="close"
          >
            <Icon name="x" :size="18" />
          </button>
        </header>

        <div class="modal-body">
          <div v-if="errorNotice" class="error-banner" role="alert">
            <Icon name="alert-triangle" :size="16" />
            <span>{{ errorNotice }}</span>
          </div>

          <!-- Etapa 1: Busca e Seleção do Estudo Alvo -->
          <div class="step-section">
            <label for="study-search-input" class="step-label">
              1. Selecione o estudo a ser conectado:
            </label>
            <div class="search-input-wrapper">
              <Icon name="search" :size="16" class="search-icon" />
              <input
                id="study-search-input"
                ref="searchInputRef"
                v-model="searchQuery"
                type="search"
                class="search-input"
                placeholder="Digite o título do estudo, capítulo ou livro…"
                autocomplete="off"
                @input="handleSearchInput"
              />
              <span v-if="searching" class="search-spinner" aria-hidden="true" />
            </div>

            <!-- Lista de Resultados da Busca -->
            <div
              class="candidates-list-box"
              role="listbox"
              aria-label="Estudos disponíveis no acervo"
            >
              <div v-if="searching && candidates.length === 0" class="empty-hint">
                Buscando estudos no acervo…
              </div>
              <div v-else-if="candidates.length === 0" class="empty-hint">
                Nenhum estudo encontrado para os termos digitados.
              </div>
              <button
                v-for="cand in candidates"
                :key="cand.id"
                type="button"
                role="option"
                :aria-selected="selectedStudy?.id === cand.id"
                class="candidate-row"
                :class="{ 'selected-candidate': selectedStudy?.id === cand.id }"
                @click="selectCandidate(cand)"
              >
                <div class="candidate-info">
                  <span class="candidate-title">{{ cand.title }}</span>
                  <span class="candidate-meta">
                    {{ cand.book_title }} • {{ cand.chapter_title }}
                  </span>
                </div>
                <div class="candidate-check" aria-hidden="true">
                  <Icon
                    v-if="selectedStudy?.id === cand.id"
                    name="check-circle"
                    :size="18"
                    class="checked-icon"
                  />
                </div>
              </button>
            </div>
          </div>

          <!-- Etapa 2: Tipo de Relação Semântica -->
          <div class="step-section">
            <label for="relation-type-select" class="step-label">
              2. Natureza da relação conceitual:
            </label>
            <div class="types-grid" role="radiogroup" aria-label="Tipo de relação semântica">
              <button
                v-for="typeKey in RELATION_TYPES"
                :key="typeKey"
                type="button"
                role="radio"
                :aria-checked="selectedType === typeKey"
                class="type-option-btn"
                :class="[
                  selectedType === typeKey ? 'type-btn-active' : 'type-btn-idle',
                  RELATION_TYPE_LABELS[typeKey]?.badgeClass || 'badge-neutral',
                ]"
                @click="selectedType = typeKey"
              >
                <span class="type-btn-text">
                  {{ RELATION_TYPE_LABELS[typeKey]?.outbound || typeKey }}
                </span>
              </button>
            </div>
          </div>

          <!-- Etapa 3: Anotação / Justificativa Opcional -->
          <div class="step-section">
            <label for="relation-desc-input" class="step-label">
              3. Justificativa ou notas conceituais (opcional):
            </label>
            <input
              id="relation-desc-input"
              v-model="description"
              type="text"
              class="desc-input"
              placeholder="Ex.: Este argumento refuta a objeção levantada no estudo anterior…"
              maxlength="255"
              @keydown.enter.prevent="handleCreate"
            />
          </div>
        </div>

        <footer class="modal-actions">
          <button
            type="button"
            class="modal-btn modal-btn-secondary"
            :disabled="submitting"
            @click="close"
          >
            Cancelar
          </button>
          <button
            type="button"
            class="modal-btn modal-btn-primary"
            :disabled="!selectedStudy || submitting"
            @click="handleCreate"
          >
            <span v-if="submitting" class="spinner" aria-hidden="true" />
            <span>{{ submitting ? 'Conectando…' : 'Criar Vínculo' }}</span>
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
  z-index: 1000;
  padding: 1rem;
}

.modal-dialog {
  width: 100%;
  max-width: 580px;
  max-height: 90vh;
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text, #111827);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.header-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-icon {
  color: var(--color-accent, #2563eb);
}

.header-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text, #111827);
}

.modal-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--color-text-muted, #6b7280);
  cursor: pointer;
  transition: all 0.15s ease;
}

.modal-close-btn:hover:not(:disabled) {
  background-color: var(--color-neutral-subtle, #f3f4f6);
  color: var(--color-text, #111827);
}

.modal-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  overflow-y: auto;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
  border-radius: 6px;
  font-size: 0.875rem;
}

.step-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.step-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text, #1f2937);
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.875rem;
  color: var(--color-text-muted, #9ca3af);
  pointer-events: none;
}

.search-input {
  width: 100%;
  min-height: 44px;
  padding: 0.625rem 2.25rem 0.625rem 2.5rem;
  font-size: 0.9375rem;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  background-color: #ffffff;
  color: var(--color-text, #111827);
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent, #2563eb);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.search-spinner {
  position: absolute;
  right: 0.875rem;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.15);
  border-top-color: var(--color-accent, #2563eb);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.candidates-list-box {
  max-height: 180px;
  overflow-y: auto;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 6px;
  background-color: var(--color-card-bg, #fafafa);
  display: flex;
  flex-direction: column;
}

.empty-hint {
  padding: 1.25rem;
  text-align: center;
  font-size: 0.875rem;
  color: var(--color-text-muted, #6b7280);
}

.candidate-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 48px;
  padding: 0.625rem 0.875rem;
  border: none;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background: transparent;
  cursor: pointer;
  text-align: left;
  transition: background-color 0.12s ease;
}

.candidate-row:last-child {
  border-bottom: none;
}

.candidate-row:hover {
  background-color: var(--color-neutral-subtle, #f3f4f6);
}

.selected-candidate {
  background-color: #eff6ff !important;
  border-left: 3px solid var(--color-accent, #2563eb);
}

.candidate-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  overflow: hidden;
}

.candidate-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text, #111827);
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.candidate-meta {
  font-size: 0.75rem;
  color: var(--color-text-muted, #6b7280);
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.candidate-check {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
}

.checked-icon {
  color: var(--color-accent, #2563eb);
}

.types-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.type-option-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  font-size: 0.8125rem;
  font-weight: 500;
  transition: all 0.15s ease;
  text-align: center;
}

.type-btn-active {
  border-color: currentColor !important;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.25);
  font-weight: 600;
}

.type-btn-idle {
  opacity: 0.75;
}

.type-btn-idle:hover {
  opacity: 1;
}

.desc-input {
  width: 100%;
  min-height: 44px;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  background-color: #ffffff;
  color: var(--color-text, #111827);
  box-sizing: border-box;
}

.desc-input:focus {
  outline: none;
  border-color: var(--color-accent, #2563eb);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.modal-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background-color: var(--color-card-bg, #fafafa);
  border-top: 1px solid var(--color-border, #e5e7eb);
}

.modal-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  min-height: 44px;
  min-width: 96px;
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s ease;
}

.modal-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-btn-secondary {
  background-color: #ffffff;
  border-color: var(--color-border, #d1d5db);
  color: var(--color-text, #374151);
}

.modal-btn-secondary:hover:not(:disabled) {
  background-color: var(--color-neutral-subtle, #f3f4f6);
}

.modal-btn-primary {
  background-color: var(--color-accent, #2563eb);
  color: #ffffff;
}

.modal-btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 640px) {
  .types-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
