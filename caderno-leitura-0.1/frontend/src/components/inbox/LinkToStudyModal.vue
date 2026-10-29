<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { api, errorMessage } from '../../services/api'
import { useInboxCount } from '../../composables/useInboxCount'
import Icon from '../ui/Icon.vue'
import type { InboxCapture, StudyCandidateOption } from '../../types'

const props = defineProps<{
  isOpen: boolean
  capture: InboxCapture | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'linked', updated: InboxCapture): void
}>()

const { refreshCount } = useInboxCount()

const searchQuery = ref('')
const candidates = ref<StudyCandidateOption[]>([])
const selectedStudyId = ref<number | null>(null)
const targetSection = ref<'references' | 'notes' | 'summary' | 'explanation' | 'concepts'>('references')
const loadingCandidates = ref(false)
const submitting = ref(false)
const error = ref<string | null>(null)
const searchInputRef = ref<HTMLInputElement | null>(null)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

const selectedStudy = computed(() =>
  candidates.value.find((c) => c.id === selectedStudyId.value) || null
)

async function fetchCandidates(q = '') {
  loadingCandidates.value = true
  error.value = null
  try {
    const list = await api.searchStudyCandidates(q, 15)
    candidates.value = list
    if (list.length > 0 && selectedStudyId.value === null) {
      selectedStudyId.value = list[0]?.id ?? null
    }
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    loadingCandidates.value = false
  }
}

function onSearchInput() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchCandidates(searchQuery.value.trim())
  }, 250)
}

watch(
  () => props.isOpen,
  async (open) => {
    if (open && props.capture) {
      searchQuery.value = ''
      selectedStudyId.value = null
      targetSection.value = 'references'
      error.value = null
      submitting.value = false
      await fetchCandidates('')
      await nextTick()
      searchInputRef.value?.focus()
    }
  }
)

function onKeyDown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    e.preventDefault()
    emit('close')
  }
}

async function handleLink() {
  if (!props.capture || !selectedStudyId.value || submitting.value) return
  submitting.value = true
  error.value = null
  try {
    const updated = await api.linkInboxCapture(props.capture.id, {
      target_study_id: selectedStudyId.value,
      target_section: targetSection.value,
    })
    await refreshCount()
    emit('linked', updated)
    emit('close')
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Transition name="fade">
    <div
      v-if="isOpen && capture"
      class="link-modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="link-modal-title"
      @keydown="onKeyDown"
      @click.self="emit('close')"
    >
      <div class="link-modal-card" role="document">
        <header class="link-modal-header">
          <div class="header-titles">
            <span class="eyebrow">Conectar Conhecimento</span>
            <h2 id="link-modal-title" class="title">Vincular a Estudo Existente</h2>
          </div>
          <button
            type="button"
            class="close-button"
            aria-label="Fechar janela de vinculação"
            @click="emit('close')"
          >
            <Icon name="x" size="sm" />
          </button>
        </header>

        <div class="link-modal-body">
          <!-- Prévia da captura a vincular -->
          <div class="capture-preview-box">
            <div class="preview-label">Conteúdo a anexar:</div>
            <p class="preview-text">"{{ capture.content }}"</p>
            <span v-if="capture.source_hint" class="preview-source">
              Fonte: {{ capture.source_hint }}
            </span>
          </div>

          <!-- Campo de busca de estudos -->
          <div class="search-section">
            <label for="study-search-input" class="field-label">
              Buscar Estudo de Destino
            </label>
            <div class="search-input-wrapper">
              <Icon name="search" size="xs" class="search-icon" />
              <input
                id="study-search-input"
                ref="searchInputRef"
                v-model="searchQuery"
                type="search"
                class="search-input"
                placeholder="Digite o título do estudo, livro ou capítulo..."
                @input="onSearchInput"
              />
            </div>
          </div>

          <!-- Seletor de seção de destino -->
          <div class="section-select-wrapper">
            <label for="target-section-select" class="field-label">
              Seção de destino no estudo
            </label>
            <select
              id="target-section-select"
              v-model="targetSection"
              class="target-select"
            >
              <option value="references">Referências (Recomendado)</option>
              <option value="notes">Anotações Pessoais</option>
              <option value="summary">Resumo</option>
              <option value="explanation">Explicação</option>
              <option value="concepts">Conceitos-Chave</option>
            </select>
            <span class="field-hint">
              O texto será anexado ao final desta seção formatado com citação e fonte.
            </span>
          </div>

          <!-- Lista de candidatos -->
          <div class="candidates-container">
            <div v-if="loadingCandidates" class="loading-state">
              <Icon name="clock" size="sm" class="spin" />
              <span>Buscando estudos...</span>
            </div>

            <div
              v-else-if="candidates.length === 0"
              class="empty-state"
            >
              <span>Nenhum estudo encontrado para "{{ searchQuery }}".</span>
            </div>

            <ul v-else class="candidates-list" role="radiogroup" aria-label="Lista de estudos">
              <li
                v-for="study in candidates"
                :key="study.id"
                class="candidate-item"
                :class="{ 'is-selected': selectedStudyId === study.id }"
                role="radio"
                :aria-checked="selectedStudyId === study.id"
                tabindex="0"
                @click="selectedStudyId = study.id"
                @keydown.space.prevent="selectedStudyId = study.id"
                @keydown.enter.prevent="selectedStudyId = study.id"
              >
                <div class="candidate-radio">
                  <span
                    class="radio-dot"
                    :class="{ 'is-active': selectedStudyId === study.id }"
                  ></span>
                </div>
                <div class="candidate-details">
                  <span class="candidate-title">{{ study.title }}</span>
                  <span class="candidate-meta">
                    {{ study.book_title }} · {{ study.chapter_name }}
                  </span>
                </div>
              </li>
            </ul>
          </div>

          <div v-if="error" class="error-banner">
            <Icon name="alert-triangle" size="xs" />
            <span>{{ error }}</span>
          </div>
        </div>

        <footer class="link-modal-footer">
          <div class="target-summary">
            <span v-if="selectedStudy" class="summary-text">
              Destino: <strong>{{ selectedStudy.title }}</strong>
            </span>
          </div>
          <div class="modal-actions">
            <button
              type="button"
              class="button button-ghost"
              :disabled="submitting"
              @click="emit('close')"
            >
              Cancelar
            </button>
            <button
              type="button"
              class="button button-primary"
              :disabled="submitting || !selectedStudyId"
              @click="handleLink"
            >
              <Icon name="link" size="xs" />
              <span>{{ submitting ? 'Vinculando...' : 'Vincular Captura' }}</span>
            </button>
          </div>
        </footer>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.link-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  padding: 16px;
}

.link-modal-card {
  width: 100%;
  max-width: 580px;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  max-height: 85vh;
}

.link-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border-subtle, #f3f4f6);
}

.eyebrow {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-link, #4f46e5);
}

.title {
  margin: 2px 0 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-text-main, #111827);
}

.close-button {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-text-muted, #9ca3af);
  padding: 6px;
  border-radius: 6px;
  min-height: 44px;
  min-width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.close-button:hover {
  background-color: var(--color-surface-hover, #f3f4f6);
  color: var(--color-text-main, #111827);
}

.link-modal-body {
  padding: 16px 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.capture-preview-box {
  background-color: var(--color-surface-input, #f9fafb);
  border-left: 3px solid var(--color-primary, #4f46e5);
  padding: 10px 14px;
  border-radius: 0 6px 6px 0;
}

.preview-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-muted, #6b7280);
  margin-bottom: 4px;
}

.preview-text {
  font-size: 0.85rem;
  font-style: italic;
  color: var(--color-text-main, #111827);
  margin: 0;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.preview-source {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-muted, #6b7280);
  margin-top: 4px;
}

.field-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-muted, #4b5563);
  margin-bottom: 6px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--color-text-muted, #9ca3af);
  pointer-events: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.search-input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  background-color: var(--color-surface, #ffffff);
  font-size: 0.875rem;
  color: var(--color-text-main, #111827);
  min-height: 44px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent, #2563eb);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.target-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  background-color: var(--color-surface, #ffffff);
  font-size: 0.875rem;
  color: var(--color-text-main, #111827);
  min-height: 44px;
}

.target-select:focus {
  outline: none;
  border-color: var(--color-primary, #4f46e5);
}

.field-hint {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-muted, #6b7280);
  margin-top: 4px;
}

.candidates-container {
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
  max-height: 180px;
  overflow-y: auto;
  background-color: var(--color-surface, #ffffff);
}

.loading-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  font-size: 0.85rem;
  color: var(--color-text-muted, #6b7280);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}

.candidates-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.candidate-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border-subtle, #f3f4f6);
  min-height: 44px;
  transition: background-color 0.15s ease;
}

.candidate-item:last-child {
  border-bottom: none;
}

.candidate-item:hover {
  background-color: var(--color-surface-hover, #f9fafb);
}

.candidate-item.is-selected {
  background-color: rgba(79, 70, 229, 0.08);
}

.candidate-radio {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-border, #d1d5db);
  border-radius: 50%;
  flex-shrink: 0;
}

.candidate-item.is-selected .candidate-radio {
  border-color: var(--color-primary, #4f46e5);
}

.radio-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: transparent;
  transition: background-color 0.15s ease;
}

.radio-dot.is-active {
  background-color: var(--color-primary, #4f46e5);
}

.candidate-details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.candidate-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-main, #111827);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.candidate-meta {
  font-size: 0.75rem;
  color: var(--color-text-muted, #6b7280);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  border-radius: 6px;
  font-size: 0.85rem;
}

.link-modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-top: 1px solid var(--color-border-subtle, #f3f4f6);
  background-color: var(--color-surface, #ffffff);
}

.summary-text {
  font-size: 0.8rem;
  color: var(--color-text-muted, #6b7280);
}

.modal-actions {
  display: flex;
  gap: 10px;
}

.button {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 44px;
  transition: all 0.15s ease;
  border: 1px solid transparent;
}

.button-ghost {
  background: transparent;
  color: var(--color-text-muted, #4b5563);
}

.button-ghost:hover {
  background-color: var(--color-surface-hover, #f3f4f6);
  color: var(--color-text-main, #111827);
}

.button-primary {
  background-color: var(--color-primary, #4f46e5);
  color: var(--color-on-accent);
}

.button-primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover, #4338ca);
  color: var(--color-accent-hover-text);
}

.button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
