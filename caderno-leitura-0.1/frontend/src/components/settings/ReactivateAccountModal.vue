<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import Icon from '../ui/Icon.vue'
import { accountApi } from '../../api/account.ts'
import { errorMessage } from '../../services/api.ts'
import type { AuthSuccessResponse } from '../../types.ts'

const props = withDefaults(
  defineProps<{
    open: boolean
    usernameOrEmail?: string
    initialPassword?: string
  }>(),
  {
    usernameOrEmail: '',
    initialPassword: '',
  },
)

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'reactivated', authData: AuthSuccessResponse): void
}>()

const username = ref('')
const password = ref('')
const isSubmitting = ref(false)
const error = ref<string | null>(null)
const passwordInput = ref<HTMLInputElement | null>(null)

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      username.value = props.usernameOrEmail || ''
      password.value = props.initialPassword || ''
      error.value = null
      nextTick(() => {
        if (!password.value) {
          passwordInput.value?.focus()
        }
      })
    }
  },
  { immediate: true },
)

function onKeyDown(event: KeyboardEvent) {
  if (event.key === 'Escape' && !isSubmitting.value) {
    close()
  }
}

function close() {
  if (isSubmitting.value) return
  emit('close')
}

async function handleReactivate() {
  if (!username.value.trim()) {
    error.value = 'Informe seu usuário ou e-mail cadastrado.'
    return
  }

  error.value = null
  isSubmitting.value = true

  try {
    const res = await accountApi.reactivateAccount({
      username_or_email: username.value.trim(),
      password: password.value || undefined,
    })
    emit('reactivated', res)
  } catch (err: unknown) {
    error.value = errorMessage(err)
  } finally {
    isSubmitting.value = false
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
        aria-labelledby="reactivate-modal-title"
      >
        <header class="modal-header">
          <h2 id="reactivate-modal-title" class="modal-title">
            <Icon name="refresh-cw" :size="20" class="modal-title-icon" />
            Reativação de Conta
          </h2>
          <button
            type="button"
            class="modal-close"
            aria-label="Fechar diálogo"
            :disabled="isSubmitting"
            @click="close"
          >
            <Icon name="x" :size="18" />
          </button>
        </header>

        <div class="modal-body">
          <div class="info-box" role="note">
            <Icon name="alert-triangle" :size="18" class="info-box-icon" />
            <p>
              Sua conta está desativada no momento. Ao confirmar a reativação,
              seu acervo, anotações e acesso serão restabelecidos imediatamente.
            </p>
          </div>

          <div v-if="error" class="error-alert" role="alert">
            {{ error }}
          </div>

          <form class="reactivate-form" @submit.prevent="handleReactivate">
            <div class="form-group">
              <label for="reactivate-username" class="form-label">Usuário ou E-mail</label>
              <input
                id="reactivate-username"
                v-model="username"
                type="text"
                class="form-input"
                required
                :disabled="isSubmitting"
                placeholder="Seu usuário ou e-mail"
              />
            </div>

            <div class="form-group">
              <label for="reactivate-password" class="form-label">Confirme sua Senha</label>
              <input
                id="reactivate-password"
                ref="passwordInput"
                v-model="password"
                type="password"
                class="form-input"
                :disabled="isSubmitting"
                placeholder="Sua senha de acesso (se cadastrada)"
              />
            </div>

            <footer class="modal-actions">
              <button
                type="button"
                class="btn-cancel"
                :disabled="isSubmitting"
                @click="close"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="btn-confirm"
                :disabled="isSubmitting"
              >
                <span v-if="isSubmitting" class="spinner" aria-hidden="true" />
                {{ isSubmitting ? 'Reativando...' : 'Reativar Minha Conta' }}
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
  max-width: 460px;
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
  color: var(--color-text, #111827);
}

.modal-title-icon {
  color: var(--color-accent, #2563eb);
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

.info-box {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  background-color: #eff6ff;
  border-left: 4px solid var(--color-accent, #2563eb);
  border-radius: 4px;
  font-size: 0.875rem;
  color: #1e40af;
  line-height: 1.4;
}

.info-box p {
  margin: 0;
}

.info-box-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.error-alert {
  padding: 0.75rem 1rem;
  border-radius: 6px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  font-size: 0.85rem;
  line-height: 1.4;
}

.reactivate-form {
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
  border-color: var(--color-accent, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
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

.btn-confirm {
  min-height: 44px;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  background: var(--color-accent, #2563eb);
  border: 1px solid var(--color-accent, #2563eb);
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background-color 0.15s ease, opacity 0.15s ease;
}

.btn-confirm:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-cancel:disabled,
.btn-confirm:disabled {
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
