<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import Icon from './ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    message: string
    confirmLabel?: string
    cancelLabel?: string
    danger?: boolean
    loading?: boolean
  }>(),
  {
    confirmLabel: 'Confirmar',
    cancelLabel: 'Cancelar',
    danger: false,
    loading: false,
  },
)

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm'): void
}>()

const confirmButton = ref<HTMLButtonElement | null>(null)
const cancelButton = ref<HTMLButtonElement | null>(null)

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      nextTick(() => {
        // Para ações perigosas, foca o cancelar por padrão; senão no confirmar
        if (props.danger) {
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

function confirm() {
  if (props.loading) return
  emit('confirm')
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
        :aria-labelledby="'confirm-title'"
      >
        <header class="modal-header">
          <h2 id="confirm-title" :class="{ 'text-danger': danger }">{{ title }}</h2>
          <button
            type="button"
            class="modal-close"
            aria-label="Fechar diálogo"
            :disabled="loading"
            @click="close"
          >
            <Icon name="x" :size="16" />
          </button>
        </header>

        <div class="modal-body">
          <p class="confirm-message">{{ message }}</p>
          <div v-if="danger" class="danger-warning" role="note">
            <p><Icon name="alert-triangle" :size="16" class="inline-icon" /> <strong>Atenção:</strong> Esta ação é permanente e irreversível.</p>
          </div>
        </div>

        <footer class="modal-actions actions">
          <button
            ref="cancelButton"
            type="button"
            class="secondary"
            :disabled="loading"
            @click="close"
          >
            {{ cancelLabel }}
          </button>
          <button
            ref="confirmButton"
            type="button"
            :class="danger ? 'danger-button' : 'primary'"
            :disabled="loading"
            @click="confirm"
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
  z-index: 999;
  padding: 1rem;
}

.modal-dialog {
  width: 100%;
  max-width: 480px;
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
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border, #eee);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
}

.text-danger {
  color: #c53030;
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
  gap: 0.75rem;
}

.confirm-message {
  margin: 0;
  line-height: 1.5;
  font-size: 0.95rem;
}

.danger-warning {
  background-color: #fff5f5;
  border-left: 4px solid #e53e3e;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  font-size: 0.88rem;
  color: #9b2c2c;
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

button.danger-button {
  background: #c53030;
  color: #fff;
}

button.danger-button:hover:not(:disabled) {
  background: #9b2c2c;
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
