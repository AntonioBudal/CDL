<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import Icon from '../ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    loading?: boolean
  }>(),
  {
    loading: false,
  },
)

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm', password?: string): void
}>()

const password = ref('')
const passwordInput = ref<HTMLInputElement | null>(null)

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      password.value = ''
      nextTick(() => {
        passwordInput.value?.focus()
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
  if (props.loading) return
  emit('confirm', password.value || undefined)
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
        aria-labelledby="deactivate-modal-title"
      >
        <header class="modal-header">
          <h2 id="deactivate-modal-title" class="modal-title text-warning">
            <Icon name="ban" :size="20" class="modal-title-icon" />
            Desativar Conta Temporariamente
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
          <div class="warning-box" role="note">
            <Icon name="alert-triangle" :size="18" class="warning-box-icon" />
            <p>
              Ao desativar sua conta, todas as suas sessões conectadas serão encerradas imediatamente.
              Seu perfil deixará de aparecer em pesquisas ou para amigos.
              <strong>Seus livros, anotações e estudos permanecerão intactos</strong>, e você poderá reativar
              o acesso a qualquer momento na tela de login.
            </p>
          </div>

          <form class="deactivate-form" @submit.prevent="handleConfirm">
            <div class="form-group">
              <label for="deactivate-password-input" class="form-label">
                Confirme sua senha atual (se cadastrada)
              </label>
              <input
                id="deactivate-password-input"
                ref="passwordInput"
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
                class="btn-warning"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner" aria-hidden="true" />
                {{ loading ? 'Desativando...' : 'Sim, desativar conta' }}
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

.text-warning {
  color: var(--color-warning, #d97706);
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

.warning-box {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  background-color: #fffbeb;
  border-left: 4px solid var(--color-warning, #d97706);
  border-radius: 4px;
  font-size: 0.875rem;
  color: #92400e;
  line-height: 1.45;
}

.warning-box p {
  margin: 0;
}

.warning-box-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.deactivate-form {
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
  border-color: var(--color-warning, #d97706);
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.15);
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

.btn-warning {
  min-height: 44px;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  background: var(--color-warning, #d97706);
  border: 1px solid var(--color-warning, #d97706);
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background-color 0.15s ease, opacity 0.15s ease;
}

.btn-warning:hover:not(:disabled) {
  background: #b45309;
}

.btn-cancel:disabled,
.btn-warning:disabled {
  opacity: 0.6;
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
