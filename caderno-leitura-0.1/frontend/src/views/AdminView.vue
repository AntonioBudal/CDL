<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { adminApi } from '../api/admin.ts'
import { categoriesApi } from '../api/categories.ts'
import AdminConfirmModal from '../components/admin/AdminConfirmModal.vue'
import AdminUsersTable from '../components/admin/AdminUsersTable.vue'
import Icon from '../components/ui/Icon.vue'
import { useAuth } from '../composables/useAuth.ts'
import { getAdminSupportConfig, updateAdminSupportConfig } from '../services/api.ts'
import type { CategoryStats, SupportAdminConfig, SupportConfigUpdate } from '../types.ts'
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
const categoryStats = ref<CategoryStats | null>(null)
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
    const [adminStats, catStats] = await Promise.all([
      adminApi.getStats(),
      categoriesApi.getStats().catch(() => null),
    ])
    stats.value = adminStats
    categoryStats.value = catStats
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

// Abas administrativas
const activeTab = ref<'users' | 'support'>('users')

// Estado da aba de suporte
const supportConfig = ref<SupportAdminConfig>({
  pix_enabled: false,
  pix_key: null,
  pix_recipient_name: null,
  pix_qr_code_url: null,
  alternative_enabled: false,
  alternative_label: null,
  alternative_url: null,
  custom_message: null,
  has_any_method_active: false,
  source: 'default',
  updated_at: null,
  updated_by_user_id: null,
  updated_by_name: null,
})
const supportLoading = ref(false)
const supportSaving = ref(false)

async function fetchSupportConfig() {
  supportLoading.value = true
  try {
    const data = await getAdminSupportConfig()
    supportConfig.value = data
  } catch (err: unknown) {
    showFeedback(err instanceof Error ? err.message : 'Falha ao carregar configurações de apoio.', 'error')
  } finally {
    supportLoading.value = false
  }
}

async function handleSaveSupportConfig() {
  supportSaving.value = true
  try {
    const payload: SupportConfigUpdate = {
      pix_enabled: supportConfig.value.pix_enabled,
      pix_key: supportConfig.value.pix_key ? supportConfig.value.pix_key.trim() : null,
      pix_recipient_name: supportConfig.value.pix_recipient_name ? supportConfig.value.pix_recipient_name.trim() : null,
      pix_qr_code_url: supportConfig.value.pix_qr_code_url ? supportConfig.value.pix_qr_code_url.trim() : null,
      alternative_enabled: supportConfig.value.alternative_enabled,
      alternative_label: supportConfig.value.alternative_label ? supportConfig.value.alternative_label.trim() : null,
      alternative_url: supportConfig.value.alternative_url ? supportConfig.value.alternative_url.trim() : null,
      custom_message: supportConfig.value.custom_message ? supportConfig.value.custom_message.trim() : null,
    }
    const updated = await updateAdminSupportConfig(payload)
    supportConfig.value = updated
    showFeedback('Configurações de apoio salvas com sucesso no banco de dados.', 'success')
  } catch (err: unknown) {
    showFeedback(err instanceof Error ? err.message : 'Falha ao salvar configurações de apoio.', 'error')
  } finally {
    supportSaving.value = false
  }
}

function formatSourceLabel(source: string): string {
  switch (source) {
    case 'database':
      return 'Banco de Dados'
    case 'environment':
      return 'Variáveis de Ambiente (.env)'
    default:
      return 'Padrão do Sistema (Desativado)'
  }
}

function formatDateTime(val: string | null): string {
  if (!val) return '—'
  try {
    return new Date(val).toLocaleString('pt-BR')
  } catch {
    return val
  }
}

async function handleRefreshAll() {
  if (activeTab.value === 'users') {
    await Promise.all([fetchStats(), fetchUsers()])
  } else {
    await fetchSupportConfig()
  }
}

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
        :disabled="loading || statsLoading || supportLoading"
        @click="handleRefreshAll"
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

    <!-- Navegação por Abas -->
    <nav class="admin-tabs" role="tablist" aria-label="Seções da administração">
      <button
        type="button"
        role="tab"
        class="admin-tab-btn touch-button"
        :class="{ active: activeTab === 'users' }"
        :aria-selected="activeTab === 'users'"
        aria-controls="tab-panel-users"
        id="tab-users"
        @click="activeTab = 'users'"
      >
        <Icon name="users" :size="18" />
        <span>Contas e Acessos</span>
      </button>

      <button
        type="button"
        role="tab"
        class="admin-tab-btn touch-button"
        :class="{ active: activeTab === 'support' }"
        :aria-selected="activeTab === 'support'"
        aria-controls="tab-panel-support"
        id="tab-support"
        @click="() => { activeTab = 'support'; fetchSupportConfig(); }"
      >
        <Icon name="heart" :size="18" />
        <span>Apoio e Doações</span>
      </button>
    </nav>

    <!-- Aba 1: Gestão de Contas e Estatísticas -->
    <div
      v-show="activeTab === 'users'"
      id="tab-panel-users"
      role="tabpanel"
      aria-labelledby="tab-users"
      class="tab-panel-content"
    >
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

      <div class="stat-card">
        <div class="stat-icon-wrapper icon-taxonomy">
          <Icon name="folder" :size="20" />
        </div>
        <div class="stat-details">
          <span class="stat-label">Categorias Canônicas</span>
          <strong class="stat-value">{{ categoryStats?.canonical_categories ?? '—' }}</strong>
          <span v-if="categoryStats" class="text-xs text-muted">
            {{ categoryStats.total_book_associations }} {{ categoryStats.total_book_associations === 1 ? 'vínculo' : 'vínculos' }}
          </span>
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
    </div>

    <!-- Aba 2: Gestão de Apoio e Doações -->
    <div
      v-show="activeTab === 'support'"
      id="tab-panel-support"
      role="tabpanel"
      aria-labelledby="tab-support"
      class="tab-panel-content"
    >
      <div v-if="supportLoading" class="support-admin-loading">
        <Icon name="refresh-cw" :size="20" class="spin-icon" />
        <span>Carregando parâmetros de apoio...</span>
      </div>

      <div v-else class="support-admin-panel">
        <!-- Metadados de Origem -->
        <div class="support-meta-bar panel">
          <div class="meta-item">
            <span class="meta-label">Origem da Configuração:</span>
            <span class="meta-badge" :class="`badge-${supportConfig.source}`">
              {{ formatSourceLabel(supportConfig.source) }}
            </span>
          </div>

          <div v-if="supportConfig.updated_at" class="meta-item">
            <span class="meta-label">Última Atualização:</span>
            <span class="meta-val">{{ formatDateTime(supportConfig.updated_at) }}</span>
          </div>

          <div v-if="supportConfig.updated_by_name" class="meta-item">
            <span class="meta-label">Atualizado por:</span>
            <span class="meta-val">{{ supportConfig.updated_by_name }}</span>
          </div>

          <div class="meta-item meta-actions">
            <router-link
              to="/apoie"
              target="_blank"
              class="btn-preview-link touch-button"
              aria-label="Abrir página pública de apoio em nova aba"
            >
              <span>Ver Página Pública</span>
              <Icon name="external-link" :size="16" />
            </router-link>
          </div>
        </div>

        <!-- Formulário de Gestão -->
        <form @submit.prevent="handleSaveSupportConfig" class="support-admin-form">
          <!-- Bloco PIX -->
          <section class="admin-card panel" aria-labelledby="heading-pix-settings">
            <div class="card-header-toggle">
              <div class="header-text">
                <h2 id="heading-pix-settings" class="section-title">Transferência PIX</h2>
                <p class="section-subtitle text-muted">
                  Exibe chave PIX, nome do titular e imagem de QR Code na página de apoio.
                </p>
              </div>
              <label class="toggle-control" for="toggle-pix">
                <input
                  id="toggle-pix"
                  type="checkbox"
                  v-model="supportConfig.pix_enabled"
                  class="toggle-checkbox"
                />
                <span class="toggle-label" :class="{ 'label-active': supportConfig.pix_enabled }">
                  {{ supportConfig.pix_enabled ? 'Ativo' : 'Inativo' }}
                </span>
              </label>
            </div>

            <div class="form-grid" :class="{ 'form-disabled': !supportConfig.pix_enabled }">
              <div class="form-group">
                <label for="admin-pix-key" class="form-label">Chave PIX (E-mail, CPF/CNPJ, Telefone ou Aleatória):</label>
                <input
                  id="admin-pix-key"
                  type="text"
                  v-model="supportConfig.pix_key"
                  class="form-input"
                  placeholder="Ex: apoio@leitorum.app, CPF/CNPJ ou chave aleatória"
                  :disabled="!supportConfig.pix_enabled"
                />
              </div>

              <div class="form-group">
                <label for="admin-pix-recipient" class="form-label">Nome do Titular / Beneficiário:</label>
                <input
                  id="admin-pix-recipient"
                  type="text"
                  v-model="supportConfig.pix_recipient_name"
                  class="form-input"
                  placeholder="Ex: Mantenedor do Leitorum"
                  :disabled="!supportConfig.pix_enabled"
                />
              </div>

              <div class="form-group full-width">
                <label for="admin-pix-qr" class="form-label">URL ou Imagem em Base64 do QR Code:</label>
                <input
                  id="admin-pix-qr"
                  type="text"
                  v-model="supportConfig.pix_qr_code_url"
                  class="form-input"
                  placeholder="Ex: /api/static/pix-qr.png ou data:image/png;base64,..."
                  :disabled="!supportConfig.pix_enabled"
                />
              </div>
            </div>
          </section>

          <!-- Bloco Meio Alternativo (Google Pay / Link Externo) -->
          <section class="admin-card panel" aria-labelledby="heading-alt-settings">
            <div class="card-header-toggle">
              <div class="header-text">
                <h2 id="heading-alt-settings" class="section-title">Meio Alternativo (Google Pay / Link Externo)</h2>
                <p class="section-subtitle text-muted">
                  Disponibiliza um botão seguro de redirecionamento para carteira digital ou página externa.
                </p>
              </div>
              <label class="toggle-control" for="toggle-alt">
                <input
                  id="toggle-alt"
                  type="checkbox"
                  v-model="supportConfig.alternative_enabled"
                  class="toggle-checkbox"
                />
                <span class="toggle-label" :class="{ 'label-active': supportConfig.alternative_enabled }">
                  {{ supportConfig.alternative_enabled ? 'Ativo' : 'Inativo' }}
                </span>
              </label>
            </div>

            <div class="form-grid" :class="{ 'form-disabled': !supportConfig.alternative_enabled }">
              <div class="form-group">
                <label for="admin-alt-label" class="form-label">Rótulo do Botão:</label>
                <input
                  id="admin-alt-label"
                  type="text"
                  v-model="supportConfig.alternative_label"
                  class="form-input"
                  placeholder="Ex: Google Pay ou Apoio Coletivo"
                  :disabled="!supportConfig.alternative_enabled"
                />
              </div>

              <div class="form-group">
                <label for="admin-alt-url" class="form-label">Endereço Web / URL de Pagamento:</label>
                <input
                  id="admin-alt-url"
                  type="url"
                  v-model="supportConfig.alternative_url"
                  class="form-input"
                  placeholder="Ex: https://pay.google.com/exemplo ou https://apoie.me/..."
                  :disabled="!supportConfig.alternative_enabled"
                />
              </div>
            </div>
          </section>

          <!-- Mensagem Personalizada -->
          <section class="admin-card panel" aria-labelledby="heading-msg-settings">
            <h2 id="heading-msg-settings" class="section-title">Mensagem Institucional de Apoio</h2>
            <p class="section-subtitle text-muted">
              Texto complementar opcional exibido aos visitantes no topo da página de apoio.
            </p>

            <div class="form-group">
              <label for="admin-custom-message" class="sr-only">Mensagem de apoio</label>
              <textarea
                id="admin-custom-message"
                v-model="supportConfig.custom_message"
                rows="3"
                class="form-textarea"
                placeholder="Ex: Suas contribuições voluntárias ajudam a custear servidores, hospedagem e melhorias continuadas."
              ></textarea>
            </div>
          </section>

          <!-- Ação Salvar -->
          <div class="form-actions">
            <button
              type="submit"
              class="btn-save-support touch-button"
              :disabled="supportSaving"
            >
              <Icon name="check" :size="18" />
              <span>{{ supportSaving ? 'Salvando alterações...' : 'Salvar Configurações de Apoio' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

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

.icon-taxonomy {
  background-color: #eef2ff;
  color: #4f46e5;
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

/* Abas de Navegação */
.admin-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid var(--color-border, #e5e7eb);
  margin-bottom: 0.5rem;
}

.admin-tab-btn {
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  border-radius: 6px 6px 0 0;
  color: var(--color-text-muted, #4b5563);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.75rem 1.25rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.15s ease-in-out;
}

.admin-tab-btn:hover:not(.active) {
  color: var(--color-text, #111827);
  background-color: var(--color-surface-hover, #f3f4f6);
}

.admin-tab-btn.active {
  color: var(--color-primary, #2563eb);
  border-bottom-color: var(--color-primary, #2563eb);
}

.tab-panel-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Painel de Apoio e Doações */
.support-admin-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem;
  color: var(--color-text-muted, #6b7280);
  font-size: 0.95rem;
}

.support-admin-panel {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.support-meta-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1.25rem;
  padding: 1rem 1.25rem;
  background-color: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.meta-label {
  color: var(--color-text-muted, #6b7280);
  font-weight: 500;
}

.meta-val {
  font-weight: 600;
  color: var(--color-text, #111827);
}

.meta-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-database {
  background-color: #ecfdf5;
  color: #065f46;
}

.badge-environment {
  background-color: #eff6ff;
  color: #1d4ed8;
}

.badge-default {
  background-color: #f3f4f6;
  color: #4b5563;
}

.meta-actions {
  margin-left: auto;
}

.btn-preview-link {
  text-decoration: none;
  border: 1px solid var(--color-border, #d1d5db);
  background-color: var(--color-surface, #fff);
  color: var(--color-primary, #2563eb);
}

.btn-preview-link:hover {
  background-color: var(--color-surface-hover, #f3f4f6);
}

.support-admin-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.admin-card {
  background-color: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
  padding: 1.25rem;
}

.card-header-toggle {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.section-title {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text, #111827);
}

.section-subtitle {
  margin: 0;
  font-size: 0.85rem;
}

.toggle-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  min-height: 44px;
  user-select: none;
}

.toggle-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: var(--color-primary, #2563eb);
}

.toggle-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-muted, #6b7280);
}

.toggle-label.label-active {
  color: var(--color-primary, #2563eb);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  transition: opacity 0.2s ease-in-out;
}

.form-grid.form-disabled {
  opacity: 0.55;
  pointer-events: none;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-muted, #4b5563);
}

.form-input {
  min-height: 44px;
  padding: 0.65rem 0.85rem;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  font-size: 0.9rem;
  background-color: var(--color-surface, #fff);
  color: var(--color-text, #111827);
  box-sizing: border-box;
}

.form-input:focus {
  border-color: var(--color-primary, #2563eb);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
  outline: none;
}

.form-textarea {
  padding: 0.75rem;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  font-size: 0.9rem;
  background-color: var(--color-surface, #fff);
  color: var(--color-text, #111827);
  resize: vertical;
  min-height: 80px;
  box-sizing: border-box;
}

.form-textarea:focus {
  border-color: var(--color-primary, #2563eb);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
  outline: none;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding: 0.5rem 0;
}

.btn-save-support {
  background-color: var(--color-primary, #2563eb);
  color: #fff;
  border: none;
  font-weight: 600;
}

.btn-save-support:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.btn-save-support:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

