<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.ts'
import { errorMessage } from '../services/api.ts'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const usernameOrEmail = ref('')
const password = ref('')
const error = ref<string | null>(null)
const isSubmitting = ref(false)

onMounted(async () => {
  await auth.checkAuth()
  if (auth.ownerSetupRequired.value) {
    router.replace('/primeiro-acesso')
    return
  }
  if (auth.isAuthenticated.value) {
    const redirect = (route.query.redirect as string) || '/'
    router.replace(redirect)
  }
})

async function handleLogin() {
  error.value = null
  if (!usernameOrEmail.value.trim() || !password.value) {
    error.value = 'Informe seu nome de usuário (ou e-mail) e sua senha.'
    return
  }

  isSubmitting.value = true
  try {
    await auth.login(usernameOrEmail.value.trim(), password.value)
    const redirect = (route.query.redirect as string) || '/'
    router.replace(redirect)
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
        <h1 class="auth-title">Caderno de Leitura</h1>
        <p class="auth-subtitle">Identificação de acesso ao acervo de estudos</p>
      </header>

      <form class="auth-form" @submit.prevent="handleLogin">
        <div v-if="error" class="auth-error-alert" role="alert">
          {{ error }}
        </div>

        <div class="form-group">
          <label for="username_or_email" class="form-label">Usuário ou E-mail</label>
          <input
            id="username_or_email"
            v-model="usernameOrEmail"
            type="text"
            class="form-input"
            autocomplete="username"
            required
            autofocus
            placeholder="Seu nome de usuário ou e-mail"
            :disabled="isSubmitting"
          />
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Senha</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-input"
            autocomplete="current-password"
            required
            placeholder="Sua senha de acesso"
            :disabled="isSubmitting"
          />
        </div>

        <button
          type="submit"
          class="auth-submit-btn"
          :disabled="isSubmitting"
        >
          <span v-if="isSubmitting">Autenticando...</span>
          <span v-else>Entrar no Caderno</span>
        </button>
      </form>

      <footer v-if="auth.allowRegistration.value" class="auth-footer">
        <p class="auth-footer-text">
          Primeiro acesso neste computador?
          <RouterLink to="/registro" class="auth-link">Criar nova conta</RouterLink>
        </p>
      </footer>
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
  max-width: 420px;
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
  letter-spacing: -0.02em;
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
  line-height: 1.4;
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
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.form-input:focus {
  border-color: var(--color-accent, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
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
  transition: background-color 0.15s ease, opacity 0.15s ease;
}

.auth-submit-btn:hover:not(:disabled) {
  opacity: 0.92;
}

.auth-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-footer {
  margin-top: 1.5rem;
  text-align: center;
  border-top: 1px solid var(--color-border, #f3f4f6);
  padding-top: 1.25rem;
}

.auth-footer-text {
  font-size: 0.8125rem;
  color: var(--color-muted, #6b7280);
}

.auth-link {
  color: var(--color-accent, #2563eb);
  font-weight: 600;
  text-decoration: none;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>
