<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { adminApi } from '../api/admin.ts'
import AdminConfirmModal from '../components/admin/AdminConfirmModal.vue'
import AdminUsersTable from '../components/admin/AdminUsersTable.vue'
import Icon from '../components/ui/Icon.vue'
import { useAuth } from '../composables/useAuth.ts'
import type {
  AdminStatsSummary,
  AdminUserItem,
  AdminUsersFilter,
  UserRole,
} from '../types/admin.ts'

const auth = useAuth()
const currentUserId = computed(() => auth.currentUser.value?.id)

// Estado de dados
const users = ref<AdminUserItem[]>([])
const totalUsers = ref(0)
const stats = ref<AdminStatsSummary | null>(null)
const loading = ref(false)
const statsLoading = ref(false)
const actionLoading = ref(false)

// Feedback e mensagens
const feedbackMessage = ref<string | null>(null)
const feedbackType = ref<'success' | 'error'>('success')
let feedbackTimer: ReturnType<typeof setTimeout> | null = null

function showFeedback(msg: string, type: 'success' | 'error' = 'success') {
  feedbackMessage.value = msg
  feedbackType.value = type
  if (feedbackTimer) clearTimeout(feedbackTimer)
  feedbackTimer = setTimeout(() => {
    feedbackMessage.value = null
  }, 5000)
}

// Filtros
const searchQuery = ref('')
const statusFilter = ref<'all' | 'ativo' | 'suspenso'>('all')
const roleFilter = ref<'all' | 'user' | 'admin'>('all')
const limit = ref(25)
const offset = ref(0)
let searchDebounce: ReturnType<typeof setTimeout> | null = null

// Modais de confirmação
type ModalAction = 'suspend' | 'reactivate' | 'revoke-sessions' | 'change-role' | null
const activeModalAction = ref<ModalAction>(null)
const selectedUser = ref<AdminUserItem | null>(null)

const modalTitle = computed(() => {
  if (!selectedUser.value) return ''
  switch (activeModalAction.value) {
    case 'suspend':
      return 'Suspender Conta de Usuário'
    case 'reactivate':
      return 'Reativar Conta de Usuário'
    case 'revoke-sessions':
      return 'Desconectar Todas as Sessões'
    case 'change-role':
      return selectedUser.value.role === 'admin'
        ? 'Rebaixar para Leitor'
        : 'Promover a Administrador'
    default:
      return ''
  }
})

const modalMessage = computed(() => {
  if (!selectedUser.value) return ''
  const name = selectedUser.value.display_name
  const username = selectedUser.value.username
  switch (activeModalAction.value) {
    case 'suspend':
      return `Tem certeza que deseja suspender a conta de ${name} (@${username})?`
    case 'reactivate':
      return `Deseja reativar a conta de ${name} (@${username})? O usuário poderá voltar a acessar a plataforma.`
    case 'revoke-sessions':
      return `Deseja encerrar forçadamente todas as sessões ativas de ${name} (@${username})?`
    case 'change-role':
      return selectedUser.value.role === 'admin'
        ? `Tem certeza que deseja rebaixar ${name} (@${username}) para a função de Leitor?`
        : `Deseja conceder privilégios de Administrador para ${name} (@${username})? Administradores têm acesso total ao gerenciamento do sistema.`
    default:
      return ''
  }
})

const modalSubmessage = computed(() => {
  if (activeModalAction.value === 'suspend') {
    return 'Todas as sessões ativas deste usuário serão revogadas no banco de dados, desconectando imediatamente seus navegadores e celulares.'
  }
  if (activeModalAction.value === 'revoke-sessions') {
    return 'O usuário será desconectado de todos os computadores e aparelhos móveis imediatamente.'
  }
  return undefined
})

const modalVariant = computed((): 'danger' | 'warning' | 'primary' => {
  if (activeModalAction.value === 'suspend') return 'danger'
  if (activeModalAction.value === 'revoke-sessions') return 'warning'
  if (activeModalAction.value === 'change-role') return 'warning'
  return 'primary'
})

const modalConfirmLabel = computed(() => {
  switch (activeModalAction.value) {
    case 'suspend':
      return 'Suspender Conta'
    case 'reactivate':
      return 'Reativar'
    case 'revoke-sessions':
      return 'Desconectar'
    case 'change-role':
      return selectedUser.value?.role === 'admin' ? 'Rebaixar' : 'Promover'
    default:
      return 'Confirmar'
  }
})

async function fetchStats() {
  statsLoading.value = true
  try {
    stats.value = await adminApi.getStats()
  } catch (err: any) {
    showFeedback(err?.message || 'Falha ao carregar indicadores administrativos.', 'error')
  } finally {
    statsLoading.value = false
  }
}

async function fetchUsers() {
  loading.value = true
  try {
    const params: AdminUsersFilter = {
      q: searchQuery.value.trim() || undefined,
      status: statusFilter.value !== 'all' ? statusFilter.value : undefined,
      role: roleFilter.value !== 'all' ? roleFilter.value : undefined,
      limit: limit.value,
      offset: offset.value,
    }
    const response = await adminApi.getUsers(params)
    users.value = response.items
    totalUsers.value = response.total
  } catch (err: any) {
    showFeedback(err?.message || 'Falha ao buscar usuários.', 'error')
  } finally {
    loading.value = false
  }
}

function onSearchInput() {
  if (searchDebounce) clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => {
    offset.value = 0
    fetchUsers()
  }, 350)
}

function clearFilters() {
  searchQuery.value = ''
  statusFilter.value = 'all'
  roleFilter.value = 'all'
  offset.value = 0
  fetchUsers()
}

// Ações do Modal
function openActionModal(action: ModalAction, user: AdminUserItem) {
  selectedUser.value = user
  activeModalAction.value = action
}

function closeModal() {
  activeModalAction.value = null
  selectedUser.value = null
}

async function handleModalConfirm(inputValue?: string) {
  if (!selectedUser.value || !activeModalAction.value) return
  actionLoading.value = true
  const targetUser = selectedUser.value

  try {
    if (activeModalAction.value === 'suspend') {
      const res = await adminApi.suspendUser(targetUser.id, { reason: inputValue?.trim() || undefined })
      showFeedback(res.message, 'success')
    } else if (activeModalAction.value === 'reactivate') {
      const res = await adminApi.reactivateUser(targetUser.id)
      showFeedback(res.message, 'success')
    } else if (activeModalAction.value === 'revoke-sessions') {
      const res = await adminApi.revokeAllSessions(targetUser.id)
      showFeedback(res.message, 'success')
    } else if (activeModalAction.value === 'change-role') {
      const newRole: UserRole = targetUser.role === 'admin' ? 'user' : 'admin'
      const res = await adminApi.updateUserRole(targetUser.id, { role: newRole })
      showFeedback(res.message, 'success')
    }

    closeModal()
    await Promise.all([fetchUsers(), fetchStats()])
  } catch (err: any) {
    const errorDetail = err?.data?.detail || err?.message || 'Erro ao processar ação administrativa.'
    showFeedback(errorDetail, 'error')
  } finally {
    actionLoading.value = false
  }
}

// Paginação
const currentPage = computed(() => Math.floor(offset.value / limit.value) + 1)
const totalPages = computed(() => Math.max(1, Math.ceil(totalUsers.value / limit.value)))

function prevPage() {
  if (offset.value > 0) {
    offset.value = Math.max(0, offset.value - limit.value)
    fetchUsers()
  }
}

function nextPage() {
  if (offset.value + limit.value < totalUsers.value) {
    offset.value += limit.value
    fetchUsers()
  }
}

watch([statusFilter, roleFilter], () => {
  offset.value = 0
  fetchUsers()
})

onMounted(() => {
  fetchStats()
  fetchUsers()
})
</script>

<template>
  <main class="admin-view-container" aria-label="Painel de Administração">
    <!-- Cabeçalho -->
    <header class="admin-header">
      <div class="header-titles">
        <h1 class="page-title">
          <Icon name="shield" :size="26" class="title-icon" />
          Administração do Sistema
        </h1>
        <p class="page-subtitle text-muted">
          Gerenciamento de contas, papéis de acesso (RBAC), governança de sessões e estatísticas da plataforma.
        </p>
      </div>

      <button
        type="button"
        class="btn-refresh touch-button"
        aria-label="Atualizar dados"
        :disabled="loading || statsLoading"
        @click="() => { fetchStats(); fetchUsers(); }"
      >
        <Icon name="refresh-cw" :size="16" />
        <span>Atualizar</span>
      </button>
    </header>

    <!-- Feedback Banner -->
    <div
      v-if="feedbackMessage"
      class="feedback-banner"
      :class="feedbackType === 'success' ? 'banner-success' : 'banner-error'"
      role="alert"
    >
      <Icon :name="feedbackType === 'success' ? 'check-circle' : 'alert-triangle'" :size="18" />
      <span>{{ feedbackMessage }}</span>
      <button
        type="button"
        class="banner-close"
        aria-label="Fechar notificação"
        @click="feedbackMessage = null"
      >
        <Icon name="x" :size="14" />
      </button>
    </div>

    <!-- Cards de Indicadores Globais -->
    <section class="stats-section" aria-label="Indicadores da plataforma">
      <div class="stat-card">
        <div class="stat-icon-wrapper icon-users">
          <Icon name="users" :size="20" />
        </div>
        <div class="stat-details">
          <span class="stat-label">Total de Contas</span>
          <strong class="stat-value">{{ stats?.total_users ?? '—' }}</strong>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrapper icon-active">
          <Icon name="user-check" :size="20" />
        </div>
        <div class="stat-details">
          <span class="stat-label">Contas Ativas</span>
          <strong class="stat-value">{{ stats?.active_users ?? '—' }}</strong>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrapper icon-suspended">
          <Icon name="user-x" :size="20" />
        </div>
        <div class="stat-details">
          <span class="stat-label">Contas Suspensas</span>
          <strong class="stat-value">{{ stats?.suspended_users ?? '—' }}</strong>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrapper icon-admin">
          <Icon name="shield" :size="20" />
        </div>
        <div class="stat-details">
          <span class="stat-label">Administradores</span>
          <strong class="stat-value">{{ stats?.admin_users ?? '—' }}</strong>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrapper icon-studies">
          <Icon name="book-open" :size="20" />
        </div>
        <div class="stat-details">
          <span class="stat-label">Total de Estudos</span>
          <strong class="stat-value">{{ stats?.total_studies ?? '—' }}</strong>
        </div>
      </div>
    </section>

    <!-- Barra de Filtros e Busca -->
    <section class="filters-section panel" aria-label="Filtros de usuários">
      <div class="search-box">
        <Icon name="search" :size="18" class="search-icon text-muted" />
        <input
          v-model="searchQuery"
          type="search"
          class="search-input"
          placeholder="Buscar por @username, nome de exibição ou e-mail..."
          aria-label="Buscar contas de usuários"
          @input="onSearchInput"
        />
      </div>

      <div class="filter-controls">
        <div class="filter-group">
          <label for="status-filter" class="filter-label">Status:</label>
          <select
            id="status-filter"
            v-model="statusFilter"
            class="filter-select"
            aria-label="Filtrar por status"
          >
            <option value="all">Todos</option>
            <option value="ativo">Ativos</option>
            <option value="suspenso">Suspensos</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="role-filter" class="filter-label">Papel:</label>
          <select
            id="role-filter"
            v-model="roleFilter"
            class="filter-select"
            aria-label="Filtrar por papel"
          >
            <option value="all">Todos</option>
            <option value="user">Leitores</option>
            <option value="admin">Administradores</option>
          </select>
        </div>

        <button
          v-if="searchQuery || statusFilter !== 'all' || roleFilter !== 'all'"
          type="button"
          class="btn-clear touch-button"
          aria-label="Limpar filtros"
          @click="clearFilters"
        >
          <Icon name="x" :size="14" />
          <span>Limpar</span>
        </button>
      </div>
    </section>

    <!-- Tabela de Contas -->
    <section class="table-section" aria-label="Lista de contas de usuários">
      <AdminUsersTable
        :users="users"
        :loading="loading"
        :current-user-id="currentUserId"
        @suspend="(u) => openActionModal('suspend', u)"
        @reactivate="(u) => openActionModal('reactivate', u)"
        @revoke-sessions="(u) => openActionModal('revoke-sessions', u)"
        @change-role="(u) => openActionModal('change-role', u)"
      />

      <!-- Barra de Paginação -->
      <footer v-if="totalUsers > 0" class="pagination-footer">
        <span class="pagination-info text-muted">
          Exibindo {{ offset + 1 }} a {{ Math.min(offset + limit, totalUsers) }} de {{ totalUsers }} contas
        </span>

        <div class="pagination-buttons">
          <button
            type="button"
            class="touch-button btn-page"
            :disabled="offset === 0 || loading"
            aria-label="Página anterior"
            @click="prevPage"
          >
            <Icon name="chevron-left" :size="16" />
            <span>Anterior</span>
          </button>

          <span class="page-indicator">
            Página {{ currentPage }} de {{ totalPages }}
          </span>

          <button
            type="button"
            class="touch-button btn-page"
            :disabled="offset + limit >= totalUsers || loading"
            aria-label="Próxima página"
            @click="nextPage"
          >
            <span>Próxima</span>
            <Icon name="chevron-right" :size="16" />
          </button>
        </div>
      </footer>
    </section>

    <!-- Modal Universal de Confirmação -->
    <AdminConfirmModal
      :open="activeModalAction !== null"
      :title="modalTitle"
      :message="modalMessage"
      :submessage="modalSubmessage"
      :variant="modalVariant"
      :confirm-label="modalConfirmLabel"
      :loading="actionLoading"
      :require-input="activeModalAction === 'suspend'"
      input-label="Motivo da suspensão (opcional):"
      input-placeholder="Ex: Violação das diretrizes de uso da plataforma"
      @close="closeModal"
      @confirm="handleModalConfirm"
    />
  </main>
</template>

<style scoped>
.admin-view-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
}

.header-titles {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.page-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text, #111827);
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.title-icon {
  color: var(--color-primary, #2563eb);
}

.page-subtitle {
  margin: 0;
  font-size: 0.9rem;
}

.feedback-banner {
  padding: 0.85rem 1.25rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.banner-success {
  background-color: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.banner-error {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.banner-close {
  background: transparent;
  border: none;
  cursor: pointer;
  margin-left: auto;
  padding: 0.35rem;
  color: inherit;
  min-width: 32px;
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  background-color: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
  padding: 1.15rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-users {
  background-color: #eff6ff;
  color: #2563eb;
}

.icon-active {
  background-color: #ecfdf5;
  color: #059669;
}

.icon-suspended {
  background-color: #fef2f2;
  color: #dc2626;
}

.icon-admin {
  background-color: #f5f3ff;
  color: #7c3aed;
}

.icon-studies {
  background-color: #fffbeb;
  color: #d97706;
}

.stat-details {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--color-text-muted, #6b7280);
  font-weight: 500;
}

.stat-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-text, #111827);
}

.filters-section {
  background-color: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 260px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
}

.search-input {
  width: 100%;
  padding: 0.65rem 0.85rem 0.65rem 2.4rem;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  font-size: 0.9rem;
  min-height: 44px;
  outline: none;
  box-sizing: border-box;
}

.search-input:focus {
  border-color: var(--color-primary, #2563eb);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-muted, #4b5563);
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  font-size: 0.85rem;
  min-height: 44px;
  background-color: var(--color-surface, #fff);
  outline: none;
  cursor: pointer;
}

.touch-button {
  min-height: 44px;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  transition: all 0.15s;
}

.btn-refresh,
.btn-clear {
  border: 1px solid var(--color-border, #d1d5db);
  background-color: var(--color-surface, #fff);
  color: var(--color-text, #374151);
}

.btn-refresh:hover:not(:disabled),
.btn-clear:hover:not(:disabled) {
  background-color: var(--color-surface-hover, #f3f4f6);
}

.pagination-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 0.5rem 0.5rem 0.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-page {
  border: 1px solid var(--color-border, #d1d5db);
  background-color: var(--color-surface, #fff);
  color: var(--color-text, #374151);
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-indicator {
  font-size: 0.85rem;
  font-weight: 500;
}

.text-muted {
  color: var(--color-text-muted, #6b7280);
}
</style>
