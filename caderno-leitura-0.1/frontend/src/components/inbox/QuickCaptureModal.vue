<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { useQuickCapture } from '../../composables/useQuickCapture'
import { api } from '../../services/api'
import Icon from '../ui/Icon.vue'
import type { Book } from '../../types'

const {
  isOpen,
  defaultBookId,
  defaultContent,
  defaultSource,
  submitting,
  error,
  close,
  submit,
} = useQuickCapture()

const content = ref('')
const sourceHint = ref('')
const selectedBookId = ref<number | null>(null)
const books = ref<Book[]>([])
const loadingBooks = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const successFeedback = ref(false)

async function loadBooks() {
  if (books.value.length > 0) return
  loadingBooks.value = true
  try {
    const list = await api.listBooks()
    books.value = list.filter((b) => !b.deleted_at)
  } catch {
    // Silencioso se offline ou erro
  } finally {
    loadingBooks.value = false
  }
}

watch(isOpen, async (opened) => {
  if (opened) {
    content.value = defaultContent.value || ''
    sourceHint.value = defaultSource.value || ''
    selectedBookId.value = defaultBookId.value || null
    successFeedback.value = false
    loadBooks()
    await nextTick()
    textareaRef.value?.focus()
  }
})

function onKeyDown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    e.preventDefault()
    close()
  } else if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault()
    handleSave()
  }
}

async function handleSave() {
  if (!content.value.trim() || submitting.value) return

  const result = await submit({
    content: content.value.trim(),
    source_hint: sourceHint.value.trim() || null,
    book_id: selectedBookId.value || null,
  })

  if (result) {
    successFeedback.value = true
    setTimeout(() => {
      successFeedback.value = false
    }, 1500)
  }
}
</script>

<template>
  <Transition name="fade">
    <div
      v-if="isOpen"
      class="quick-capture-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="quick-capture-title"
      @keydown="onKeyDown"
      @click.self="close"
    >
      <div class="quick-capture-card" role="document">
        <header class="quick-capture-header">
          <div class="header-titles">
            <span class="eyebrow">Captura Rápida</span>
            <h2 id="quick-capture-title" class="title">Novo Pensamento no Inbox</h2>
          </div>
          <button
            type="button"
            class="close-button"
            aria-label="Fechar captura rápida"
            @click="close"
          >
            <Icon name="x" size="sm" />
          </button>
        </header>

        <form class="quick-capture-form" @submit.prevent="handleSave">
          <div class="field-group">
            <label for="capture-content" class="field-label visually-hidden">
              Texto da Captura
            </label>
            <textarea
              id="capture-content"
              ref="textareaRef"
              v-model="content"
              class="capture-textarea"
              placeholder="O que você está pensando ou lendo agora? Despeje aqui sua ideia ou citação..."
              rows="4"
              required
              :disabled="submitting"
            ></textarea>
          </div>

          <div class="capture-metadata-row">
            <div class="field-group flex-1">
              <label for="capture-source" class="field-label">
                Fonte ou Referência (Opcional)
              </label>
              <input
                id="capture-source"
                v-model="sourceHint"
                type="text"
                class="capture-input"
                placeholder="Ex.: Capítulo 3, pág. 45 ou autor"
                maxlength="500"
                :disabled="submitting"
              />
            </div>

            <div class="field-group flex-1">
              <label for="capture-book" class="field-label">
                Vincular a um Livro (Opcional)
              </label>
              <select
                id="capture-book"
                v-model="selectedBookId"
                class="capture-select"
                :disabled="submitting || loadingBooks"
              >
                <option :value="null">Nenhum (ideia avulsa)</option>
                <option v-for="b in books" :key="b.id" :value="b.id">
                  {{ b.title }}
                </option>
              </select>
            </div>
          </div>

          <div v-if="error" class="error-banner" role="alert">
            <Icon name="alert-triangle" size="sm" />
            <span>{{ error }}</span>
          </div>

          <footer class="quick-capture-footer">
            <span class="keyboard-tip">
              Dica: pressione <kbd>Ctrl</kbd>+<kbd>Enter</kbd> para salvar ou <kbd>Esc</kbd> para fechar
            </span>
            <div class="actions-group">
              <button
                type="button"
                class="button button-ghost"
                :disabled="submitting"
                @click="close"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="button button-primary"
                :disabled="submitting || !content.trim()"
              >
                <Icon v-if="submitting" name="refresh-cw" size="sm" class="animate-spin" />
                <span>{{ submitting ? 'Salvando...' : 'Salvar no Inbox' }}</span>
              </button>
            </div>
          </footer>
        </form>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.quick-capture-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 16px;
}

.quick-capture-card {
  width: 100%;
  max-width: 580px;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-lg, 12px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.quick-capture-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 18px 20px 12px;
  border-bottom: 1px solid var(--color-border-subtle, #f3f4f6);
}

.header-titles .eyebrow {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-link, #4f46e5);
  margin-bottom: 2px;
}

.header-titles .title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-text-main, #111827);
}

.close-button {
  background: transparent;
  border: none;
  color: var(--color-text-muted, #6b7280);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.close-button:hover {
  background-color: var(--color-surface-hover, #f3f4f6);
  color: var(--color-text-main, #111827);
}

.quick-capture-form {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 0.825rem;
  font-weight: 500;
  color: var(--color-text-muted, #4b5563);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.capture-textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 8px;
  background-color: var(--color-surface, #ffffff);
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.6;
  color: var(--color-text, #111827);
  resize: vertical;
  min-height: 120px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.capture-textarea::placeholder {
  color: var(--color-placeholder, #9ca3af);
  font-style: italic;
}

.capture-textarea:focus {
  outline: none;
  border-color: var(--color-accent, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
  background-color: var(--color-surface, #ffffff);
}

.capture-metadata-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.flex-1 {
  flex: 1 1 200px;
}

.capture-input,
.capture-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  background-color: var(--color-surface, #ffffff);
  font-size: 0.875rem;
  color: var(--color-text, #111827);
  min-height: 44px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.capture-input:focus,
.capture-select:focus {
  outline: none;
  border-color: var(--color-accent, #2563eb);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
  background-color: var(--color-surface, #ffffff);
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

.quick-capture-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 4px;
  padding-top: 14px;
  border-top: 1px solid var(--color-border-subtle, #f3f4f6);
}

.keyboard-tip {
  font-size: 0.75rem;
  color: var(--color-text-muted, #9ca3af);
}

.keyboard-tip kbd {
  display: inline-block;
  padding: 2px 4px;
  font-size: 0.7rem;
  font-family: inherit;
  background-color: var(--color-surface-hover, #f3f4f6);
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 4px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.1);
}

.actions-group {
  display: flex;
  align-items: center;
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
  color: var(--color-muted, #4b5563);
}

.button-ghost:hover:not(:disabled) {
  background-color: var(--color-surface-hover, #f3f4f6);
  color: var(--color-text, #111827);
}

.button-primary {
  background-color: var(--color-accent, #2563eb);
  color: #ffffff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(37, 99, 235, 0.2);
}

.button-primary:hover:not(:disabled) {
  background-color: var(--color-accent-hover, #1d4ed8);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(37, 99, 235, 0.25);
  transform: translateY(-1px);
}

.button:focus-visible {
  outline: 2px solid var(--color-accent, #2563eb);
  outline-offset: 2px;
}

.button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 640px) {
  .quick-capture-backdrop {
    padding: 8px;
    align-items: flex-end;
  }
  .quick-capture-card {
    max-height: calc(100dvh - 16px);
    max-height: calc(100vh - 16px);
    overflow-y: auto;
    border-radius: 12px 12px 0 0;
  }
  .quick-capture-footer {
    flex-direction: column;
    align-items: stretch;
  }
  .actions-group {
    justify-content: flex-end;
  }
  .keyboard-tip {
    text-align: center;
  }
}
</style>
