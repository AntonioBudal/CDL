<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import Icon from '../ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    expectedUsername: string
    loading?: boolean
  }>(),
  {
    loading: false,
  },
)

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm', payload: { confirmation_text: string; password?: string }): void
}>()

const confirmationText = ref('')
const password = ref('')
const confirmInput = ref<HTMLInputElement | null>(null)

const isConfirmationValid = computed(() => {
  return confirmationText.value.trim() === props.expectedUsername.trim()
})

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      confirmationText.value = ''
      password.value = ''
      nextTick(() => {
        confirmInput.value?.focus()
      })
    }
  },
  { immediate: true },
)

function onKeyDown(event: KeyboardEvent) {
  if (event.key === 'Escape' && !props.loading) {
    close()
  }
}

function close() {
  if (props.loading) return
  emit('close')
}

function handleConfirm() {
  if (!isConfirmationValid.value || props.loading) return
  emit('confirm', {
    confirmation_text: confirmationText.value.trim(),
    password: password.value || undefined,
  })
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
        aria-labelledby="delete-account-title"
      >
        <header class="modal-header">
          <h2 id="delete-account-title" class="modal-title text-danger">
            <Icon name="trash" :size="20" class="modal-title-icon" />
            Excluir Conta Permanentemente
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
          <div class="danger-box" role="alert">
            <Icon name="alert-triangle" :size="20" class="danger-box-icon" />
            <div>
              <strong>Atenção: Esta ação é definitiva e irreversível!</strong>
              <p>
                Todos os seus livros, capítulos, estudos, anotações, histórico de leitura,
                perfil e conexões com amigos serão completamente apagados do banco de dados (LGPD).
                Não será possível recuperar seus dados.
              </p>
            </div>
          </div>

          <form class="delete-form" @submit.prevent="handleConfirm">
            <div class="form-group">
              <label for="confirm-username-input" class="form-label">
                Digite exatamente seu identificador <code>{{ expectedUsername }}</code> para autorizar:
              </label>
              <input
                id="confirm-username-input"
                ref="confirmInput"
                v-model="confirmationText"
                type="text"
                class="form-input"
                :disabled="loading"
                :placeholder="expectedUsername"
                required
                autocomplete="off"
              />
            </div>

            <div class="form-group">
              <label for="delete-password-input" class="form-label">
                Confirme sua senha de acesso (se cadastrada)
              </label>
              <input
                id="delete-password-input"
                v-model="password"
                type="password"
                class="form-input"
                :disabled="loading"
                placeholder="Digite sua senha de acesso"
              />
            </div>

            <footer class="modal-actions">
              <button
                type="button"
                class="btn-cancel"
                :disabled="loading"
                @click="close"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="btn-danger"
                :disabled="!isConfirmationValid || loading"
              >
                <span v-if="loading" class="spinner" aria-hidden="true" />
                {{ loading ? 'Excluindo...' : 'Excluir definitivamente' }}
              </button>
            </footer>
          </form>
        </div>
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
  background-color: var(--color-surface, #ffffff);
  border-radius: var(--radius-card, 12px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--color-border, #e5e7eb);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.modal-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.text-danger {
  color: var(--color-danger, #dc2626);
}

.modal-title-icon {
  flex-shrink: 0;
}

.modal-close {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-muted, #6b7280);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  min-width: 44px;
  min-height: 44px;
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

.danger-box {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  background-color: #fef2f2;
  border-left: 4px solid var(--color-danger, #dc2626);
  border-radius: 4px;
  font-size: 0.875rem;
  color: #991b1b;
  line-height: 1.45;
}

.danger-box p {
  margin: 0.35rem 0 0 0;
  color: #7f1d1d;
}

.danger-box-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.delete-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text, #374151);
}

.form-label code {
  background: var(--color-surface-soft, #f3f4f6);
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
  color: var(--color-danger, #dc2626);
}

.form-input {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  font-size: 0.9375rem;
  outline: none;
  min-height: 44px;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: var(--color-danger, #dc2626);
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.15);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
}

.btn-cancel {
  min-height: 44px;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  background: transparent;
  border: 1px solid var(--color-border, #d1d5db);
  color: var(--color-text, #374151);
  transition: background-color 0.15s ease;
}

.btn-cancel:hover:not(:disabled) {
  background-color: var(--color-surface-hover, #f3f4f6);
}

.btn-danger {
  min-height: 44px;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  background: var(--color-danger, #dc2626);
  border: 1px solid var(--color-danger, #dc2626);
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background-color 0.15s ease, opacity 0.15s ease;
}

.btn-danger:hover:not(:disabled) {
  background: #b91c1c;
}

.btn-cancel:disabled,
.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
