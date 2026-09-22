<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.ts'
import { errorMessage } from '../services/api.ts'

const router = useRouter()
const auth = useAuthStore()

const password = ref('')
const confirmPassword = ref('')
const error = ref<string | null>(null)
const isSubmitting = ref(false)

async function handleSetup() {
  error.value = null
  if (password.value.length < 8) {
    error.value = 'A senha mestra deve ter no mínimo 8 caracteres.'
    return
  }
  if (password.value !== confirmPassword.value) {
    error.value = 'A confirmação de senha não confere.'
    return
  }

  isSubmitting.value = true
  try {
    await auth.setupOwner(password.value)
    router.replace('/')
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="auth-page-container">
    <div class="auth-card">
      <header class="auth-header">
        <h1 class="auth-title">Primeiro Acesso</h1>
        <p class="auth-subtitle">Defina a senha mestra para proteger o acervo do proprietário</p>
      </header>

      <form class="auth-form" @submit.prevent="handleSetup">
        <div v-if="error" class="auth-error-alert" role="alert">
          {{ error }}
        </div>

        <div class="form-group">
          <label for="setup_password" class="form-label">Nova Senha Mestra</label>
          <input
            id="setup_password"
            v-model="password"
            type="password"
            class="form-input"
            required
            minlength="8"
            placeholder="Mínimo de 8 caracteres"
            :disabled="isSubmitting"
          />
        </div>

        <div class="form-group">
          <label for="setup_confirm" class="form-label">Confirmar Senha Mestra</label>
          <input
            id="setup_confirm"
            v-model="confirmPassword"
            type="password"
            class="form-input"
            required
            minlength="8"
            placeholder="Digite a senha novamente"
            :disabled="isSubmitting"
          />
        </div>

        <button type="submit" class="auth-submit-btn" :disabled="isSubmitting">
          <span v-if="isSubmitting">Gravando...</span>
          <span v-else>Definir Senha e Iniciar</span>
        </button>
      </form>
    </div>
  </main>
</template>

<style scoped>
.auth-page-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 120px);
  padding: 1.5rem;
}

.auth-card {
  width: 100%;
  max-width: 440px;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-card, 12px);
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
  padding: 2.25rem 2rem;
}

.auth-header {
  text-align: center;
  margin-bottom: 1.75rem;
}

.auth-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text, #111827);
  margin-bottom: 0.35rem;
}

.auth-subtitle {
  font-size: 0.875rem;
  color: var(--color-muted, #6b7280);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.auth-error-alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-control, 6px);
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  font-size: 0.8125rem;
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
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-control, 6px);
  border: 1px solid var(--color-border, #d1d5db);
  background: var(--color-surface-soft, #f9fafb);
  color: var(--color-text, #111827);
  font-size: 0.9375rem;
  outline: none;
}

.form-input:focus {
  border-color: var(--color-accent, #3b82f6);
  background: var(--color-surface, #ffffff);
}

.auth-submit-btn {
  margin-top: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-control, 6px);
  background: var(--color-accent, #2563eb);
  color: #ffffff;
  font-size: 0.9375rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.auth-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
