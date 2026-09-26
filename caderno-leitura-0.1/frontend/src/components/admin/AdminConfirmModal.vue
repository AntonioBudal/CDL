<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import Icon from '../ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    message: string
    submessage?: string
    confirmLabel?: string
    cancelLabel?: string
    variant?: 'danger' | 'warning' | 'primary'
    loading?: boolean
    requireInput?: boolean
    inputLabel?: string
    inputPlaceholder?: string
  }>(),
  {
    confirmLabel: 'Confirmar',
    cancelLabel: 'Cancelar',
    variant: 'primary',
    loading: false,
    requireInput: false,
    inputLabel: 'Motivo',
    inputPlaceholder: 'Informe o motivo (opcional)',
  },
)

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm', inputValue?: string): void
}>()

const confirmButton = ref<HTMLButtonElement | null>(null)
const cancelButton = ref<HTMLButtonElement | null>(null)
const inputField = ref<HTMLInputElement | null>(null)
const textValue = ref('')

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      textValue.value = ''
      nextTick(() => {
        if (props.requireInput) {
          inputField.value?.focus()
        } else if (props.variant === 'danger') {
          cancelButton.value?.focus()
        } else {
          confirmButton.value?.focus()
        }
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
  if (props.loading) return
  emit('close')
}

function handleConfirm() {
  if (props.loading) return
  emit('confirm', textValue.value)
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
        aria-labelledby="admin-confirm-title"
      >
        <header class="modal-header">
          <h2
            id="admin-confirm-title"
            :class="{
              'text-danger': variant === 'danger',
              'text-warning': variant === 'warning',
            }"
          >
            {{ title }}
          </h2>
          <button
            type="button"
            class="modal-close"
            aria-label="Fechar diálogo"
            :disabled="loading"
            @click="close"
          >
            <Icon name="x" :size="18" />
          </button>
        </header>

        <div class="modal-body">
          <p class="confirm-message">{{ message }}</p>
          <p v-if="submessage" class="confirm-submessage text-muted">{{ submessage }}</p>

          <div v-if="requireInput" class="input-container">
            <label for="admin-modal-input" class="input-label">{{ inputLabel }}</label>
            <input
              id="admin-modal-input"
              ref="inputField"
              v-model="textValue"
              type="text"
              class="admin-input"
              :placeholder="inputPlaceholder"
              :disabled="loading"
              @keydown.enter="handleConfirm"
            />
          </div>

          <div v-if="variant === 'danger'" class="danger-warning" role="note">
            <p>
              <Icon name="alert-triangle" :size="16" class="inline-icon" />
              <strong>Atenção:</strong> Esta ação desconectará imediatamente todas as sessões ativas do usuário.
            </p>
          </div>
        </div>

        <footer class="modal-actions actions">
          <button
            ref="cancelButton"
            type="button"
            class="secondary touch-button"
            :disabled="loading"
            @click="close"
          >
            {{ cancelLabel }}
          </button>
          <button
            ref="confirmButton"
            type="button"
            :class="[
              'touch-button',
              variant === 'danger' ? 'danger-button' : variant === 'warning' ? 'warning-button' : 'primary'
            ]"
            :disabled="loading"
            @click="handleConfirm"
          >
            <span v-if="loading" class="spinner" aria-hidden="true" />
            {{ loading ? 'Processando...' : confirmLabel }}
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
  max-width: 480px;
  background-color: var(--color-surface, #fff);
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
}

.modal-close {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-text-muted, #6b7280);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  min-width: 44px;
  min-h: 44px;
  border-radius: 4px;
}

.modal-close:hover:not(:disabled) {
  background-color: var(--color-surface-hover, #f3f4f6);
  color: var(--color-text, #111827);
}

.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.confirm-message {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--color-text, #1f2937);
}

.confirm-submessage {
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.4;
}

.text-muted {
  color: var(--color-text-muted, #6b7280);
}

.text-danger {
  color: var(--color-danger, #dc2626);
}

.text-warning {
  color: var(--color-warning, #d97706);
}

.danger-warning {
  padding: 0.75rem 1rem;
  background-color: var(--color-danger-subtle, #fef2f2);
  border-left: 4px solid var(--color-danger, #dc2626);
  border-radius: 4px;
  font-size: 0.85rem;
  color: var(--color-danger-text, #991b1b);
}

.danger-warning p {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.inline-icon {
  flex-shrink: 0;
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.input-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text, #374151);
}

.admin-input {
  width: 100%;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  font-size: 0.9rem;
  outline: none;
  min-height: 44px;
  box-sizing: border-box;
}

.admin-input:focus {
  border-color: var(--color-primary, #2563eb);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background-color: var(--color-surface-subtle, #f9fafb);
  border-top: 1px solid var(--color-border, #e5e7eb);
}

.touch-button {
  min-height: 44px;
  min-width: 88px;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background-color 0.15s, border-color 0.15s;
}

.touch-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.danger-button {
  background-color: var(--color-danger, #dc2626);
  color: white;
  border: 1px solid var(--color-danger, #dc2626);
}

.danger-button:hover:not(:disabled) {
  background-color: var(--color-danger-hover, #b91c1c);
}

.warning-button {
  background-color: var(--color-warning, #d97706);
  color: white;
  border: 1px solid var(--color-warning, #d97706);
}

.warning-button:hover:not(:disabled) {
  background-color: var(--color-warning-hover, #b45309);
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
