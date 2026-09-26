<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useFriends } from '../composables/useFriends.ts'
import { profileApi } from '../api/profile.ts'
import type { UserSearchItem } from '../types.ts'
import FriendActionButtons from '../components/FriendActionButtons.vue'
import Icon from '../components/ui/Icon.vue'
import { getInitials } from '../composables/useProfile.ts'

type ActiveTab = 'friends' | 'requests' | 'blocked' | 'discover'

const activeTab = ref<ActiveTab>('friends')
const friendsService = useFriends()

// Estado da busca de descobríveis
const searchQuery = ref('')
const searchResults = ref<UserSearchItem[]>([])
const isSearching = ref(false)
let searchTimeout: ReturnType<typeof setTimeout> | null = null

const friends = friendsService.friends
const requests = friendsService.requests
const blockedUsers = friendsService.blockedUsers
const summary = friendsService.summary
const loading = friendsService.loading
const error = friendsService.error

async function switchTab(tab: ActiveTab) {
  activeTab.value = tab
  if (tab === 'friends') {
    await friendsService.fetchFriends()
  } else if (tab === 'requests') {
    await friendsService.fetchRequests()
  } else if (tab === 'blocked') {
    await friendsService.fetchBlocked()
  } else if (tab === 'discover' && searchResults.value.length === 0) {
    await executeSearch('')
  }
}

async function executeSearch(query: string) {
  isSearching.value = true
  try {
    const results = await profileApi.searchUsers(query)
    searchResults.value = results
  } catch {
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

watch(searchQuery, (newVal) => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    void executeSearch(newVal)
  }, 300)
})

function formatDate(dateString?: string | null): string {
  if (!dateString) return ''
  try {
    const d = new Date(dateString)
    return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
  } catch {
    return ''
  }
}

onMounted(async () => {
  await Promise.all([
    friendsService.fetchSummary(),
    friendsService.fetchFriends(),
  ])
})
</script>

<template>
  <main class="friends-view wrap">
    <!-- Cabeçalho Principal -->
    <header class="friends-header">
      <div class="header-titles">
        <h1 class="page-title">
          <Icon name="users" :size="28" />
          <span>Amizades e Leitores</span>
        </h1>
        <p class="header-subtitle muted">
          Conecte-se com outros leitores, acompanhe estudos mútuos e gerencie sua rede social no Leitorum.
        </p>
      </div>

      <!-- Sumário Rápido de Estatísticas -->
      <div class="summary-chips" aria-label="Resumo social">
        <div class="chip">
          <span class="chip-number">{{ summary.friends_count }}</span>
          <span class="chip-label">{{ summary.friends_count === 1 ? 'amigo' : 'amigos' }}</span>
        </div>
        <div v-if="summary.pending_received_count > 0" class="chip highlight">
          <span class="chip-number">{{ summary.pending_received_count }}</span>
          <span class="chip-label">pendente{{ summary.pending_received_count > 1 ? 's' : '' }}</span>
        </div>
      </div>
    </header>

    <!-- Alerta de Erro -->
    <div v-if="error" class="error-banner panel" role="alert">
      <Icon name="alert-triangle" :size="20" />
      <span>{{ error }}</span>
    </div>

    <!-- Navegação de Abas -->
    <nav class="tabs-nav" role="tablist" aria-label="Abas da comunidade de amigos">
      <button
        id="tab-friends"
        type="button"
        role="tab"
        class="tab-btn"
        :class="{ active: activeTab === 'friends' }"
        :aria-selected="activeTab === 'friends'"
        aria-controls="panel-friends"
        @click="switchTab('friends')"
      >
        <Icon name="users" :size="18" />
        <span>Meus Amigos</span>
        <span class="tab-badge">{{ summary.friends_count }}</span>
      </button>

      <button
        id="tab-requests"
        type="button"
        role="tab"
        class="tab-btn"
        :class="{ active: activeTab === 'requests' }"
        :aria-selected="activeTab === 'requests'"
        aria-controls="panel-requests"
        @click="switchTab('requests')"
      >
        <Icon name="mail" :size="18" />
        <span>Solicitações</span>
        <span
          v-if="summary.pending_received_count > 0"
          class="tab-badge alert"
          aria-label="Novas solicitações recebidas"
        >
          {{ summary.pending_received_count }}
        </span>
      </button>

      <button
        id="tab-discover"
        type="button"
        role="tab"
        class="tab-btn"
        :class="{ active: activeTab === 'discover' }"
        :aria-selected="activeTab === 'discover'"
        aria-controls="panel-discover"
        @click="switchTab('discover')"
      >
        <Icon name="search" :size="18" />
        <span>Descobrir Leitores</span>
      </button>

      <button
        id="tab-blocked"
        type="button"
        role="tab"
        class="tab-btn"
        :class="{ active: activeTab === 'blocked' }"
        :aria-selected="activeTab === 'blocked'"
        aria-controls="panel-blocked"
        @click="switchTab('blocked')"
      >
        <Icon name="ban" :size="18" />
        <span>Bloqueados</span>
      </button>
    </nav>

    <!-- Indicador de Carregamento -->
    <div v-if="loading" class="loading-state" role="status" aria-live="polite">
      <Icon name="search" :size="24" class="spinning-icon" />
      <span>Carregando informações…</span>
    </div>

    <!-- Conteúdo da Aba 1: Meus Amigos -->
    <section
      v-else-if="activeTab === 'friends'"
      id="panel-friends"
      role="tabpanel"
      aria-labelledby="tab-friends"
      class="tab-content"
    >
      <div v-if="friends.length === 0" class="empty-state panel">
        <Icon name="users" :size="48" class="empty-icon muted" />
        <h2>Nenhum amigo conectado ainda</h2>
        <p class="muted">
          Você ainda não possui amigos no seu caderno. Descubra outros leitores ou compartilhe seu handle @{{ summary }} para começar.
        </p>
        <button
          type="button"
          class="button primary action-btn"
          @click="switchTab('discover')"
        >
          <Icon name="search" :size="16" />
          <span>Buscar leitores</span>
        </button>
      </div>

      <div v-else class="friends-grid">
        <article
          v-for="item in friends"
          :key="item.friendship_id"
          class="person-card panel"
        >
          <div class="person-avatar">
            <img
              v-if="item.user.avatar_url"
              :src="item.user.avatar_url"
              :alt="item.user.display_name"
              class="avatar-img"
            />
            <div v-else class="avatar-initials" aria-hidden="true">
              {{ getInitials(item.user.display_name || item.user.username) }}
            </div>
          </div>

          <div class="person-info">
            <RouterLink
              :to="`/@${item.user.username}`"
              class="person-name-link"
            >
              <h3 class="person-name">{{ item.user.display_name }}</h3>
              <span class="person-handle muted">@{{ item.user.username }}</span>
            </RouterLink>
            <p v-if="item.user.bio" class="person-bio muted">{{ item.user.bio }}</p>
            <span v-if="item.since" class="meta-since muted">
              Amigos desde {{ formatDate(item.since) }}
            </span>
          </div>

          <div class="person-actions">
            <FriendActionButtons
              :username="item.user.username"
              initial-status="friends"
              :initial-request-id="item.friendship_id"
              compact
            />
          </div>
        </article>
      </div>
    </section>

    <!-- Conteúdo da Aba 2: Solicitações -->
    <section
      v-else-if="activeTab === 'requests'"
      id="panel-requests"
      role="tabpanel"
      aria-labelledby="tab-requests"
      class="tab-content"
    >
      <!-- Solicitações Recebidas -->
      <div class="requests-section">
        <h2 class="section-title">
          <span>Solicitações Recebidas</span>
          <span class="count-badge">{{ requests.received.length }}</span>
        </h2>

        <div v-if="requests.received.length === 0" class="empty-substate muted">
          Nenhuma solicitação de amizade recebida no momento.
        </div>

        <div v-else class="requests-grid">
          <article
            v-for="req in requests.received"
            :key="req.request_id"
            class="person-card panel"
          >
            <div class="person-avatar">
              <img
                v-if="req.user.avatar_url"
                :src="req.user.avatar_url"
                :alt="req.user.display_name"
                class="avatar-img"
              />
              <div v-else class="avatar-initials" aria-hidden="true">
                {{ getInitials(req.user.display_name || req.user.username) }}
              </div>
            </div>

            <div class="person-info">
              <RouterLink
                :to="`/@${req.user.username}`"
                class="person-name-link"
              >
                <h3 class="person-name">{{ req.user.display_name }}</h3>
                <span class="person-handle muted">@{{ req.user.username }}</span>
              </RouterLink>
              <p v-if="req.user.bio" class="person-bio muted">{{ req.user.bio }}</p>
              <span class="meta-since muted">
                Recebida em {{ formatDate(req.created_at) }}
              </span>
            </div>

            <div class="person-actions">
              <FriendActionButtons
                :username="req.user.username"
                initial-status="pending_received"
                :initial-request-id="req.request_id"
              />
            </div>
          </article>
        </div>
      </div>

      <!-- Solicitações Enviadas -->
      <div class="requests-section">
        <h2 class="section-title">
          <span>Solicitações Enviadas</span>
          <span class="count-badge">{{ requests.sent.length }}</span>
        </h2>

        <div v-if="requests.sent.length === 0" class="empty-substate muted">
          Você não enviou nenhuma solicitação pendente.
        </div>

        <div v-else class="requests-grid">
          <article
            v-for="req in requests.sent"
            :key="req.request_id"
            class="person-card panel"
          >
            <div class="person-avatar">
              <img
                v-if="req.user.avatar_url"
                :src="req.user.avatar_url"
                :alt="req.user.display_name"
                class="avatar-img"
              />
              <div v-else class="avatar-initials" aria-hidden="true">
                {{ getInitials(req.user.display_name || req.user.username) }}
              </div>
            </div>

            <div class="person-info">
              <RouterLink
                :to="`/@${req.user.username}`"
                class="person-name-link"
              >
                <h3 class="person-name">{{ req.user.display_name }}</h3>
                <span class="person-handle muted">@{{ req.user.username }}</span>
              </RouterLink>
              <span class="meta-since muted">
                Enviada em {{ formatDate(req.created_at) }}
              </span>
            </div>

            <div class="person-actions">
              <FriendActionButtons
                :username="req.user.username"
                initial-status="pending_sent"
                :initial-request-id="req.request_id"
              />
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- Conteúdo da Aba 3: Descobrir Leitores -->
    <section
      v-else-if="activeTab === 'discover'"
      id="panel-discover"
      role="tabpanel"
      aria-labelledby="tab-discover"
      class="tab-content"
    >
      <div class="search-bar panel">
        <Icon name="search" :size="18" class="search-icon muted" />
        <input
          v-model="searchQuery"
          type="search"
          class="search-input"
          placeholder="Buscar leitor por nome ou @username…"
          aria-label="Buscar leitores descobríveis"
        />
        <div v-if="isSearching" class="search-spinner">
          <Icon name="clock" :size="16" class="spinning-icon" />
        </div>
      </div>

      <div v-if="searchResults.length === 0 && !isSearching" class="empty-state panel">
        <Icon name="search" :size="40" class="muted" />
        <h3>Nenhum leitor encontrado</h3>
        <p class="muted">
          {{ searchQuery ? 'Nenhum leitor descobrível corresponde à sua pesquisa.' : 'Busque por amigos ou conhecidos para conectar.' }}
        </p>
      </div>

      <div v-else class="friends-grid">
        <article
          v-for="u in searchResults"
          :key="u.username"
          class="person-card panel"
        >
          <div class="person-avatar">
            <img
              v-if="u.avatar_url"
              :src="u.avatar_url"
              :alt="u.display_name"
              class="avatar-img"
            />
            <div v-else class="avatar-initials" aria-hidden="true">
              {{ getInitials(u.display_name || u.username) }}
            </div>
          </div>

          <div class="person-info">
            <RouterLink
              :to="`/@${u.username}`"
              class="person-name-link"
            >
              <h3 class="person-name">{{ u.display_name }}</h3>
              <span class="person-handle muted">@{{ u.username }}</span>
            </RouterLink>
            <p v-if="u.bio" class="person-bio muted">{{ u.bio }}</p>
          </div>

          <div class="person-actions">
            <FriendActionButtons
              :username="u.username"
              compact
            />
          </div>
        </article>
      </div>
    </section>

    <!-- Conteúdo da Aba 4: Bloqueados -->
    <section
      v-else-if="activeTab === 'blocked'"
      id="panel-blocked"
      role="tabpanel"
      aria-labelledby="tab-blocked"
      class="tab-content"
    >
      <div v-if="blockedUsers.length === 0" class="empty-state panel">
        <Icon name="ban" :size="48" class="empty-icon muted" />
        <h2>Nenhum usuário bloqueado</h2>
        <p class="muted">
          Você não bloqueou nenhum usuário. Leitores bloqueados não podem visualizar seus estudos, perfis ou enviar solicitações.
        </p>
      </div>

      <div v-else class="friends-grid">
        <article
          v-for="item in blockedUsers"
          :key="item.friendship_id"
          class="person-card panel"
        >
          <div class="person-avatar">
            <img
              v-if="item.user.avatar_url"
              :src="item.user.avatar_url"
              :alt="item.user.display_name"
              class="avatar-img"
            />
            <div v-else class="avatar-initials" aria-hidden="true">
              {{ getInitials(item.user.display_name || item.user.username) }}
            </div>
          </div>

          <div class="person-info">
            <h3 class="person-name">{{ item.user.display_name }}</h3>
            <span class="person-handle muted">@{{ item.user.username }}</span>
            <span class="meta-since muted">
              Bloqueado em {{ formatDate(item.blocked_at) }}
            </span>
          </div>

          <div class="person-actions">
            <FriendActionButtons
              :username="item.user.username"
              initial-status="blocked_by_me"
              :initial-request-id="item.friendship_id"
              compact
            />
          </div>
        </article>
      </div>
    </section>
  </main>
</template>

<style scoped>
.friends-view {
  max-width: 60rem;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
}

.friends-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.75rem;
  margin: 0 0 0.5rem;
}

.header-subtitle {
  margin: 0;
  max-width: 36rem;
  font-size: 0.95rem;
}

.summary-chips {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.chip {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
  padding: 0.4rem 0.85rem;
  border-radius: 9999px;
  background-color: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e5e5e5);
  font-size: 0.875rem;
}

.chip-number {
  font-weight: 700;
  font-size: 1.1rem;
}

.chip.highlight {
  background-color: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border-color: rgba(239, 68, 68, 0.3);
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
  background-color: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #dc2626;
  border-radius: var(--radius-sm, 6px);
}

.tabs-nav {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--color-border, #e5e5e5);
  margin-bottom: 1.5rem;
  overflow-x: auto;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  min-height: 44px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--color-text-muted, #666);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--color-text, #111);
}

.tab-btn.active {
  color: var(--color-primary, #2563eb);
  border-bottom-color: var(--color-primary, #2563eb);
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.1rem 0.5rem;
  border-radius: 9999px;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.06));
}

.tab-badge.alert {
  background-color: #dc2626;
  color: #fff;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem;
  color: var(--color-text-muted, #666);
}

.friends-grid,
.requests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.requests-section {
  margin-bottom: 2.5rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.15rem;
  margin-bottom: 1rem;
}

.count-badge {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.1rem 0.45rem;
  border-radius: 9999px;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.06));
}

.empty-substate {
  padding: 1.5rem;
  text-align: center;
  background-color: var(--color-surface, #fff);
  border: 1px dashed var(--color-border, #e5e5e5);
  border-radius: var(--radius-surface, 10px);
}

.person-card {
  display: flex;
  flex-direction: column;
  padding: 1.25rem;
  border-radius: var(--radius-surface, 10px);
  background-color: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e5e5e5);
  gap: 1rem;
}

.person-avatar {
  width: 52px;
  height: 52px;
}

.avatar-img {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-initials {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background-color: var(--color-surface-soft, #f0f0f0);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--color-text-muted, #555);
}

.person-info {
  flex: 1;
}

.person-name-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.person-name-link:hover .person-name {
  color: var(--color-primary, #2563eb);
}

.person-name {
  margin: 0;
  font-size: 1.05rem;
}

.person-handle {
  font-size: 0.85rem;
  display: block;
  margin-bottom: 0.35rem;
}

.person-bio {
  font-size: 0.85rem;
  margin: 0.25rem 0 0.5rem;
  line-height: 1.3;
}

.meta-since {
  font-size: 0.75rem;
  display: block;
}

.person-actions {
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border, #f0f0f0);
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
  background-color: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e5e5e5);
  border-radius: var(--radius-surface, 10px);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 1rem;
  outline: none;
}

.empty-state {
  text-align: center;
  padding: 3.5rem 1.5rem;
  border-radius: var(--radius-surface, 12px);
  background-color: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e5e5e5);
}

.empty-icon {
  margin-bottom: 1rem;
}

.spinning-icon {
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
