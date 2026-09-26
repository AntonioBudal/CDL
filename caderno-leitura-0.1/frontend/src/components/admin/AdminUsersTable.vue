<script setup lang="ts">
import type { AdminUserItem } from '../../types/admin.ts'
import Icon from '../ui/Icon.vue'

defineProps<{
  users: AdminUserItem[]
  loading?: boolean
  currentUserId?: string
}>()

const emit = defineEmits<{
  (e: 'suspend', user: AdminUserItem): void
  (e: 'reactivate', user: AdminUserItem): void
  (e: 'revoke-sessions', user: AdminUserItem): void
  (e: 'change-role', user: AdminUserItem): void
}>()

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  } catch {
    return dateStr
  }
}
</script>

<template>
  <div class="admin-table-container">
    <div v-if="loading && users.length === 0" class="loading-state">
      <span class="spinner" aria-hidden="true" />
      <p>Carregando contas cadastradas...</p>
    </div>

    <div v-else-if="users.length === 0" class="empty-state">
      <Icon name="search" :size="32" class="empty-icon text-muted" />
      <p class="empty-text">Nenhuma conta encontrada com os filtros informados.</p>
    </div>

    <div v-else class="table-wrapper">
      <table class="admin-table" aria-label="Tabela de usuários cadastrados">
        <thead>
          <tr>
            <th scope="col">Usuário</th>
            <th scope="col">Papel</th>
            <th scope="col">Status</th>
            <th scope="col">Provedor</th>
            <th scope="col" class="text-center">Estudos</th>
            <th scope="col" class="text-center">Sessões</th>
            <th scope="col">Último Acesso</th>
            <th scope="col" class="text-right">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="u in users"
            :key="u.id"
            :class="{ 'row-suspended': u.status === 'suspenso', 'row-current': u.id === currentUserId }"
          >
            <td class="cell-user">
              <div class="user-identity">
                <span class="user-name">
                  {{ u.display_name }}
                  <span v-if="u.id === currentUserId" class="badge-self">Você</span>
                </span>
                <span class="user-username text-muted">@{{ u.username }}</span>
                <span v-if="u.email" class="user-email text-muted">{{ u.email }}</span>
              </div>
            </td>

            <td>
              <span
                class="badge"
                :class="u.role === 'admin' ? 'badge-admin' : 'badge-user'"
              >
                {{ u.role === 'admin' ? 'Administrador' : 'Leitor' }}
              </span>
            </td>

            <td>
              <span
                class="badge"
                :class="u.status === 'ativo' ? 'badge-active' : 'badge-suspended'"
              >
                {{ u.status === 'ativo' ? 'Ativo' : 'Suspenso' }}
              </span>
            </td>

            <td>
              <span class="provider-label">
                {{ u.provider === 'google' ? 'Google' : u.provider === 'ambos' ? 'Local + Google' : 'Local' }}
              </span>
            </td>

            <td class="text-center">
              <span class="metric-value">{{ u.studies_count }}</span>
            </td>

            <td class="text-center">
              <span
                class="sessions-count"
                :class="{ 'has-sessions': u.active_sessions_count > 0 }"
              >
                {{ u.active_sessions_count }}
              </span>
            </td>

            <td>
              <span class="date-label text-muted">{{ formatDate(u.last_access) }}</span>
            </td>

            <td class="cell-actions text-right">
              <div class="action-buttons">
                <!-- Alterar Papel -->
                <button
                  type="button"
                  class="btn-action btn-role"
                  :aria-label="`Alterar papel de @${u.username}`"
                  :title="u.role === 'admin' ? 'Rebaixar para Leitor' : 'Promover a Administrador'"
                  @click="emit('change-role', u)"
                >
                  <Icon :name="u.role === 'admin' ? 'arrow-down' : 'arrow-up'" :size="15" />
                  <span class="action-label">{{ u.role === 'admin' ? 'Rebaixar' : 'Promover' }}</span>
                </button>

                <!-- Desconectar Sessões -->
                <button
                  v-if="u.active_sessions_count > 0"
                  type="button"
                  class="btn-action btn-disconnect"
                  :aria-label="`Desconectar sessões de @${u.username}`"
                  title="Encerrar todas as sessões ativas deste usuário"
                  @click="emit('revoke-sessions', u)"
                >
                  <Icon name="log-out" :size="15" />
                  <span class="action-label">Desconectar</span>
                </button>

                <!-- Suspender ou Reativar -->
                <button
                  v-if="u.status === 'ativo'"
                  type="button"
                  class="btn-action btn-suspend"
                  :disabled="u.id === currentUserId"
                  :aria-label="`Suspender conta de @${u.username}`"
                  :title="u.id === currentUserId ? 'Não é possível suspender sua própria conta' : 'Suspender conta'"
                  @click="emit('suspend', u)"
                >
                  <Icon name="ban" :size="15" />
                  <span class="action-label">Suspender</span>
                </button>

                <button
                  v-else
                  type="button"
                  class="btn-action btn-reactivate"
                  :aria-label="`Reativar conta de @${u.username}`"
                  title="Reativar conta de usuário"
                  @click="emit('reactivate', u)"
                >
                  <Icon name="check" :size="15" />
                  <span class="action-label">Reativar</span>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.admin-table-container {
  width: 100%;
  background: var(--color-surface, #fff);
  border-radius: 8px;
  border: 1px solid var(--color-border, #e5e7eb);
  overflow: hidden;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.9rem;
}

.admin-table th {
  padding: 0.85rem 1rem;
  background-color: var(--color-surface-subtle, #f9fafb);
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  font-weight: 600;
  color: var(--color-text-muted, #4b5563);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.admin-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--color-border-subtle, #f3f4f6);
  vertical-align: middle;
}

.admin-table tbody tr:hover {
  background-color: var(--color-surface-hover, #f8fafc);
}

.row-suspended {
  background-color: rgba(239, 68, 68, 0.04);
}

.row-current {
  background-color: rgba(37, 99, 235, 0.03);
}

.user-identity {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.user-name {
  font-weight: 600;
  color: var(--color-text, #111827);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-username {
  font-size: 0.8rem;
}

.user-email {
  font-size: 0.75rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.badge-admin {
  background-color: #ede9fe;
  color: #6d28d9;
}

.badge-user {
  background-color: #e0f2fe;
  color: #0369a1;
}

.badge-active {
  background-color: #dcfce7;
  color: #15803d;
}

.badge-suspended {
  background-color: #fee2e2;
  color: #b91c1c;
}

.badge-self {
  font-size: 0.7rem;
  font-weight: 600;
  background-color: var(--color-primary-subtle, #dbeafe);
  color: var(--color-primary, #1d4ed8);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.provider-label,
.date-label {
  font-size: 0.85rem;
}

.sessions-count {
  display: inline-block;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.85rem;
  background: var(--color-surface-subtle, #f3f4f6);
  color: var(--color-text-muted, #6b7280);
}

.sessions-count.has-sessions {
  background: #dbeafe;
  color: #1e40af;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.btn-action {
  min-height: 44px;
  min-width: 44px;
  padding: 0.4rem 0.65rem;
  border-radius: 6px;
  border: 1px solid var(--color-border, #d1d5db);
  background: var(--color-surface, #fff);
  color: var(--color-text, #374151);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  transition: all 0.15s;
}

.btn-action:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-role:hover:not(:disabled) {
  border-color: #8b5cf6;
  color: #7c3aed;
  background-color: #f5f3ff;
}

.btn-disconnect:hover:not(:disabled) {
  border-color: #f59e0b;
  color: #d97706;
  background-color: #fffbeb;
}

.btn-suspend:hover:not(:disabled) {
  border-color: #ef4444;
  color: #dc2626;
  background-color: #fef2f2;
}

.btn-reactivate:hover:not(:disabled) {
  border-color: #10b981;
  color: #059669;
  background-color: #ecfdf5;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  gap: 0.75rem;
  text-align: center;
}

.empty-text {
  color: var(--color-text-muted, #6b7280);
  font-size: 0.95rem;
  margin: 0;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--color-border, #e5e7eb);
  border-top-color: var(--color-primary, #2563eb);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.text-muted {
  color: var(--color-text-muted, #6b7280);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 900px) {
  .action-label {
    display: none;
  }
}
</style>
