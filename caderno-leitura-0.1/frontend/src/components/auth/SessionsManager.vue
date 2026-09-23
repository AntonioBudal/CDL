<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth.ts'
import { errorMessage } from '../../services/api.ts'
import Icon from '../ui/Icon.vue'
import GoogleSignInButton from './GoogleSignInButton.vue'
import type { SessionItem } from '../../types.ts'

const router = useRouter()
const auth = useAuthStore()
const currentUser = computed(() => auth.user.value)

const sessions = ref<SessionItem[]>([])
const isLoading = ref(false)
const actionMessage = ref<string | null>(null)
const actionError = ref<string | null>(null)
const revokingId = ref<string | null>(null)
const isLoggingOutAll = ref(false)

function formatDate(isoStr: string): string {
  try {
    const d = new Date(isoStr)
    return d.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return isoStr
  }
}

async function loadSessions() {
  isLoading.value = true
  actionError.value = null
  try {
    sessions.value = await auth.fetchSessions()
  } catch (err) {
    actionError.value = errorMessage(err)
  } finally {
    isLoading.value = false
  }
}

async function handleRevoke(session: SessionItem) {
  if (session.is_current) {
    if (!confirm('Esta é a sua sessão atual. Deseja realmente sair da aplicação?')) {
      return
    }
  } else {
    if (!confirm(`Deseja revogar o acesso do dispositivo "${session.device_name}"?`)) {
      return
    }
  }

  revokingId.value = session.id
  actionMessage.value = null
  actionError.value = null

  try {
    await auth.revokeSession(session.id)
    if (session.is_current) {
      await auth.logout()
      router.replace('/login')
      return
    }
    actionMessage.value = `Sessão do dispositivo "${session.device_name}" revogada com sucesso.`
    await loadSessions()
  } catch (err) {
    actionError.value = errorMessage(err)
  } finally {
    revokingId.value = null
  }
}

async function handleLogoutAll() {
  if (!confirm('Deseja encerrar todas as outras sessões ativas em outros navegadores e aparelhos?')) {
    return
  }

  isLoggingOutAll.value = true
  actionMessage.value = null
  actionError.value = null

  try {
    const count = await auth.logoutAll()
    actionMessage.value = count > 0
      ? `${count} outra(s) sessão(ões) revogada(s) com sucesso.`
      : 'Nenhuma outra sessão ativa encontrada.'
    await loadSessions()
  } catch (err) {
    actionError.value = errorMessage(err)
  } finally {
    isLoggingOutAll.value = false
  }
}

const isLinkingGoogle = ref(false)
const isUnlinkingGoogle = ref(false)

async function handleLinkGoogle(credential: string) {
  isLinkingGoogle.value = true
  actionError.value = null
  actionMessage.value = null
  try {
    await auth.linkGoogle(credential)
    actionMessage.value = 'Conta Google vinculada com sucesso a este perfil.'
  } catch (err) {
    actionError.value = errorMessage(err)
  } finally {
    isLinkingGoogle.value = false
  }
}

async function handleUnlinkGoogle() {
  if (!currentUser.value?.has_password) {
    actionError.value = 'Você precisa definir uma senha local antes de desvincular a conta Google, prevenindo bloqueio permanente.'
    return
  }

  if (!confirm('Deseja realmente desvincular sua conta Google deste perfil?')) {
    return
  }

  isUnlinkingGoogle.value = true
  actionError.value = null
  actionMessage.value = null
  try {
    await auth.unlinkGoogle()
    actionMessage.value = 'Conta Google desvinculada com sucesso.'
  } catch (err) {
    actionError.value = errorMessage(err)
  } finally {
    isUnlinkingGoogle.value = false
  }
}

onMounted(() => {
  void loadSessions()
})
</script>

<template>
  <div class="sessions-manager">
    <!-- Feedback de Ações -->
    <p v-if="actionMessage" class="notice session-notice" role="status">
      {{ actionMessage }}
    </p>
    <div v-if="actionError" class="auth-error-alert" role="alert">
      {{ actionError }}
    </div>

    <!-- Perfil da Conta -->
    <article class="system-card profile-card">
      <div class="profile-header">
        <div>
          <h3 class="profile-title">Conta Conectada</h3>
          <p class="muted">Detalhes do leitor autenticado na sessão atual.</p>
        </div>
        <span class="role-badge" :class="currentUser?.role">
          {{ currentUser?.role === 'admin' ? 'Proprietário' : 'Leitor' }}
        </span>
      </div>

      <div class="profile-grid">
        <div class="profile-field">
          <span class="field-label">Nome de Exibição</span>
          <span class="field-value">{{ currentUser?.display_name || '—' }}</span>
        </div>
        <div class="profile-field">
          <span class="field-label">Nome de Usuário</span>
          <span class="field-value">@{{ currentUser?.username || '—' }}</span>
        </div>
        <div class="profile-field">
          <span class="field-label">E-mail</span>
          <span class="field-value">{{ currentUser?.email || 'Não informado' }}</span>
        </div>
        <div class="profile-field">
          <span class="field-label">Status da Conta</span>
          <span class="field-value status-active">● Ativo</span>
        </div>
      </div>
    </article>

    <!-- Métodos de Acesso e Identidade Google -->
    <article v-if="auth.googleAuthEnabled.value" class="system-card identity-card">
      <div class="identity-header">
        <div>
          <h3 class="identity-title">Identidade e Acesso</h3>
          <p class="muted">Gerencie a vinculação da sua conta Google e métodos de autenticação.</p>
        </div>
      </div>

      <div class="identity-content">
        <div class="identity-row">
          <div class="identity-info">
            <div class="identity-provider">
              <Icon name="link" :size="18" class="identity-icon" />
              <strong>Google Identity</strong>
            </div>
            <p v-if="currentUser?.has_google" class="identity-status-linked">
              <Icon name="check" :size="14" /> Conta Google conectada a este perfil.
            </p>
            <p v-else class="identity-status-unlinked muted">
              Nenhuma conta Google vinculada a este perfil.
            </p>
          </div>

          <div class="identity-actions">
            <template v-if="currentUser?.has_google">
              <div v-if="!currentUser?.has_password" class="lockout-warning">
                <Icon name="alert-triangle" :size="14" />
                <span>Defina uma senha local antes de desvincular para evitar bloqueio.</span>
              </div>
              <button
                type="button"
                class="danger-button"
                :disabled="isUnlinkingGoogle || !currentUser?.has_password"
                @click="handleUnlinkGoogle"
              >
                {{ isUnlinkingGoogle ? 'Desvinculando...' : 'Desvincular Google' }}
              </button>
            </template>

            <template v-else>
              <div class="google-link-slot">
                <GoogleSignInButton
                  text="continue_with"
                  @success="handleLinkGoogle"
                  @error="(msg) => (actionError = msg)"
                />
              </div>
            </template>
          </div>
        </div>
      </div>
    </article>

    <!-- Dispositivos Conectados -->
    <article class="system-card">
      <div class="sessions-header">
        <div>
          <h3>Dispositivos Conectados</h3>
          <p class="muted">
            Todas as sessões ativas associadas à sua conta na rede local e privada.
          </p>
        </div>
        <div class="actions wrap">
          <button
            type="button"
            class="secondary"
            :disabled="isLoading"
            @click="loadSessions"
          >
            {{ isLoading ? 'Atualizando...' : 'Atualizar' }}
          </button>
          <button
            v-if="sessions.length > 1"
            type="button"
            class="danger-button"
            :disabled="isLoggingOutAll || isLoading"
            @click="handleLogoutAll"
          >
            {{ isLoggingOutAll ? 'Encerrando...' : 'Encerrar Outras Sessões' }}
          </button>
        </div>
      </div>

      <div v-if="isLoading && sessions.length === 0" class="loading-state muted">
        Carregando sessões ativas...
      </div>

      <div v-else-if="sessions.length === 0" class="empty-state muted">
        Nenhuma sessão ativa encontrada.
      </div>

      <ul v-else class="sessions-list" role="list">
        <li
          v-for="s in sessions"
          :key="s.id"
          class="session-item"
          :class="{ 'current-session': s.is_current }"
        >
          <div class="session-info">
            <div class="session-title-line">
              <Icon
                :name="s.device_name.toLowerCase().includes('phone') || s.device_name.toLowerCase().includes('android') ? 'smartphone' : 'monitor'"
                :size="16"
                class="device-icon"
              />
              <strong class="device-name">{{ s.device_name }}</strong>
              <span v-if="s.is_current" class="current-badge">
                Sessão Atual
              </span>
            </div>

            <div class="session-meta muted">
              <span>IP: <code>{{ s.ip_address }}</code></span>
              <span>·</span>
              <span>Última atividade: {{ formatDate(s.last_activity) }}</span>
            </div>
          </div>

          <div class="session-actions">
            <button
              type="button"
              class="revoke-btn"
              :class="{ 'revoke-current': s.is_current }"
              :disabled="revokingId === s.id"
              @click="handleRevoke(s)"
            >
              {{ revokingId === s.id ? 'Revogando...' : (s.is_current ? 'Sair' : 'Revogar Acesso') }}
            </button>
          </div>
        </li>
      </ul>
    </article>
  </div>
</template>

<style scoped>
.sessions-manager {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.session-notice {
  margin-bottom: 0.5rem;
}

.auth-error-alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-control, 6px);
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  font-size: 0.8125rem;
}

.profile-card {
  margin-bottom: 0.5rem;
}

.profile-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.profile-title {
  margin: 0 0 0.25rem;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.06));
  color: var(--color-muted);
}

.role-badge.admin {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.profile-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field-label {
  font-size: 0.75rem;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.field-value {
  font-size: 0.9375rem;
  color: var(--color-text);
  font-weight: 500;
}

.status-active {
  color: #16a34a;
}

.sessions-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.sessions-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.875rem 1rem;
  border-radius: var(--radius-control, 8px);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  transition: border-color 0.15s ease;
}

.session-item.current-session {
  border-color: var(--color-accent, #3b82f6);
  background: var(--color-surface-soft, rgba(59, 130, 246, 0.03));
}

.session-info {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.session-title-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.device-icon {
  font-size: 1.15rem;
}

.device-name {
  font-size: 0.9375rem;
  color: var(--color-text);
}

.current-badge {
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  background: #dbeafe;
  color: #1e40af;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.session-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
}

.session-meta code {
  font-size: 0.75rem;
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
}

.revoke-btn {
  padding: 0.4rem 0.8rem;
  border-radius: var(--radius-control, 6px);
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.revoke-btn:hover:not(:disabled) {
  border-color: #ef4444;
  color: #ef4444;
  background: #fef2f2;
}

.revoke-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.revoke-current {
  color: var(--color-muted);
}

.danger-button {
  padding: 0.45rem 0.85rem;
  border-radius: var(--radius-control, 6px);
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid #fca5a5;
  background: #fff5f5;
  color: #b91c1c;
  cursor: pointer;
  transition: all 0.15s ease;
}

.danger-button:hover:not(:disabled) {
  background: #fee2e2;
  border-color: #f87171;
}

.danger-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 2rem;
  font-size: 0.875rem;
}

.identity-header {
  margin-bottom: 1rem;
}

.identity-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.25rem;
}

.identity-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.identity-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem;
  border-radius: var(--radius-control, 6px);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
  border: 1px solid var(--color-border);
}

.identity-info {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.identity-provider {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text);
}

.identity-status-linked {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8125rem;
  color: #15803d;
  font-weight: 500;
  margin: 0;
}

.identity-status-unlinked {
  font-size: 0.8125rem;
  margin: 0;
}

.identity-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.lockout-warning {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: #b45309;
  background: #fffbeb;
  border: 1px solid #fde68a;
  padding: 0.35rem 0.6rem;
  border-radius: 4px;
  max-width: 320px;
}

.google-link-slot {
  min-width: 200px;
}
</style>
