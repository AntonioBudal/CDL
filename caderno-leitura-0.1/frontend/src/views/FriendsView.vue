<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useFriends } from '../composables/useFriends.ts'
import { profileApi } from '../api/profile.ts'
import type { SocialActiveTab, UserSearchItem } from '../types.ts'
import BookplateCard from '../components/BookplateCard.vue'
import FriendActionButtons from '../components/FriendActionButtons.vue'
import Icon from '../components/ui/Icon.vue'
import { getInitials, useProfile } from '../composables/useProfile.ts'
import { useAuthStore } from '../stores/auth.ts'

const activeTab = ref<SocialActiveTab>('friends')
const friendsService = useFriends()
const authStore = useAuthStore()
const profileService = useProfile()

const userHandle = computed(() => {
  return profileService.profile.value?.username || authStore.user.value?.username || ''
})

const userDisplayName = computed(() => {
  return profileService.profile.value?.display_name || authStore.user.value?.display_name || userHandle.value
})

const userAvatarUrl = computed(() => {
  return profileService.profile.value?.avatar_url || null
})

const userBio = computed(() => {
  return profileService.profile.value?.bio || null
})

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

const suggestedThemes = [
  'Literatura Clássica',
  'Filosofia & Ensaio',
  'História & Humanidades',
  'Ficção & Narrativa',
  'Poesia & Crítica',
]

function applyThemeSuggestion(theme: string) {
  searchQuery.value = theme
}

async function switchTab(tab: SocialActiveTab) {
  activeTab.value = tab
  if (tab === 'friends') {
    await friendsService.fetchFriends()
  } else if (tab === 'requests') {
    await friendsService.fetchRequests()
  } else if (tab === 'blocked') {
    await friendsService.fetchBlocked()
  } else if (tab === 'discover' && searchResults.value.length === 0 && searchQuery.value) {
    await executeSearch(searchQuery.value)
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
  if (!profileService.profile.value) {
    void profileService.fetchProfile()
  }
  await Promise.all([
    friendsService.fetchSummary(),
    friendsService.fetchFriends(),
  ])
})
</script>

<template>
  <main class="friends-view wrap">
    <!-- Cabeçalho Principal do Salão Literário -->
    <header class="friends-header">
      <div class="header-titles">
        <h1 class="page-title">
          <Icon name="users" :size="28" />
          <span>Salão Literário & Círculos de Estudo</span>
        </h1>
        <p class="header-subtitle muted">
          Conecte-se com outros leitores, acompanhe estudos mútuos e gerencie sua correspondência intelectual no Leitorum.
        </p>
      </div>

      <!-- Sumário Rápido de Estatísticas -->
      <div class="summary-chips" aria-label="Resumo social">
        <div class="chip">
          <span class="chip-number">{{ summary.friends_count }}</span>
          <span class="chip-label">{{ summary.friends_count === 1 ? 'conexão' : 'conexões' }}</span>
        </div>
        <div v-if="summary.pending_received_count > 0" class="chip highlight">
          <span class="chip-number">{{ summary.pending_received_count }}</span>
          <span class="chip-label">pendente{{ summary.pending_received_count > 1 ? 's' : '' }}</span>
        </div>
      </div>
    </header>

    <!-- Cartão de Identidade do Leitor (Ex-Líbris Digital Permanente no Topo) -->
    <BookplateCard
      v-if="userHandle"
      :username="userHandle"
      :display-name="userDisplayName"
      :avatar-url="userAvatarUrl"
      :bio="userBio"
      :friends-count="summary.friends_count"
      :pending-count="summary.pending_received_count"
    />

    <!-- Alerta de Erro -->
    <div v-if="error" class="error-banner panel" role="alert">
      <Icon name="alert-triangle" :size="20" />
      <span>{{ error }}</span>
    </div>

    <!-- Navegação de Abas WAI-ARIA -->
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
        <span class="tab-label">Círculo de Leitura</span>
        <span class="sr-only">Meus Amigos</span>
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
      <Icon name="clock" :size="24" class="spinning-icon" />
      <span>Carregando informações do salão…</span>
    </div>

    <!-- Conteúdo da Aba 1: Círculo de Leitura (Meus Amigos) -->
    <section
      v-else-if="activeTab === 'friends'"
      id="panel-friends"
      role="tabpanel"
      aria-labelledby="tab-friends"
      class="tab-content"
    >
      <!-- Estado Vazio Acolhedor: Círculo em Formação -->
      <div v-if="friends.length === 0" class="empty-state panel friends-empty-state">
        <div class="empty-icon-wrapper">
          <Icon name="users" :size="36" class="empty-icon" />
        </div>
        <h2 class="empty-title">Círculo de Leitura em Formação</h2>
        <p class="empty-desc muted">
          Seu salão literário ainda não possui conexões ativas. Compartilhe seu Ex-Líbris digital acima com colegas ou explore outros leitores para trocar anotações e estudos mútuos.
        </p>

        <div class="empty-actions">
          <button
            type="button"
            class="button primary action-btn"
            @click="switchTab('discover')"
          >
            <Icon name="search" :size="16" />
            <span>Descobrir Leitores</span>
          </button>
        </div>
      </div>

      <!-- Grid de Cartões de Conexão Literária -->
      <div v-else class="friends-grid">
        <article
          v-for="item in friends"
          :key="item.friendship_id"
          class="person-card panel"
        >
          <div class="person-card-top">
            <RouterLink
              :to="`/u/${item.user.username}`"
              class="person-avatar-link"
              :aria-label="`Ver estante de ${item.user.display_name}`"
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
            </RouterLink>

            <div class="person-info">
              <RouterLink
                :to="`/u/${item.user.username}`"
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
          Nenhuma solicitação de correspondência literária recebida no momento.
        </div>

        <div v-else class="requests-grid">
          <article
            v-for="req in requests.received"
            :key="req.request_id"
            class="person-card panel"
          >
            <div class="person-card-top">
              <RouterLink
                :to="`/u/${req.user.username}`"
                class="person-avatar-link"
                :aria-label="`Ver estante de ${req.user.display_name}`"
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
              </RouterLink>

              <div class="person-info">
                <RouterLink
                  :to="`/u/${req.user.username}`"
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
            <div class="person-card-top">
              <RouterLink
                :to="`/u/${req.user.username}`"
                class="person-avatar-link"
                :aria-label="`Ver estante de ${req.user.display_name}`"
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
              </RouterLink>

              <div class="person-info">
                <RouterLink
                  :to="`/u/${req.user.username}`"
                  class="person-name-link"
                >
                  <h3 class="person-name">{{ req.user.display_name }}</h3>
                  <span class="person-handle muted">@{{ req.user.username }}</span>
                </RouterLink>
                <span class="meta-since muted">
                  Enviada em {{ formatDate(req.created_at) }}
                </span>
              </div>
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

      <!-- Guia Acolhedor de Exploração e Sugestões Temáticas (quando busca vazia) -->
      <div v-if="!searchQuery" class="discover-guide panel">
        <div class="guide-header">
          <div class="guide-icon-wrapper">
            <Icon name="globe" :size="24" class="guide-icon" />
          </div>
          <div>
            <h3 class="guide-title">Descubra Leitores e Parceiros de Estudo</h3>
            <p class="guide-desc muted">
              Explore outros cadernos literários e conecte-se com pesquisadores que leem e investigam temas afins.
            </p>
          </div>
        </div>

        <div class="suggestions-wrapper">
          <span class="suggestions-label muted">Sugestões de temas e interesses:</span>
          <div class="suggestions-chips">
            <button
              v-for="theme in suggestedThemes"
              :key="theme"
              type="button"
              class="suggestion-chip"
              @click="applyThemeSuggestion(theme)"
            >
              <Icon name="book" :size="12" />
              <span>{{ theme }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Estado: Busca vazia sem resultados -->
      <div v-else-if="searchResults.length === 0 && !isSearching" class="empty-state panel">
        <Icon name="search" :size="40" class="muted" />
        <h3 class="empty-title">Nenhum leitor encontrado</h3>
        <p class="empty-desc muted">
          Nenhum leitor descobrível corresponde à sua pesquisa "{{ searchQuery }}". Tente buscar por outro termo ou nome de usuário.
        </p>
      </div>

      <!-- Resultados Encontrados -->
      <div v-else class="friends-grid">
        <article
          v-for="u in searchResults"
          :key="u.username"
          class="person-card panel"
        >
          <div class="person-card-top">
            <RouterLink
              :to="`/u/${u.username}`"
              class="person-avatar-link"
              :aria-label="`Ver estante de ${u.display_name}`"
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
            </RouterLink>

            <div class="person-info">
              <RouterLink
                :to="`/u/${u.username}`"
                class="person-name-link"
              >
                <h3 class="person-name">{{ u.display_name }}</h3>
                <span class="person-handle muted">@{{ u.username }}</span>
              </RouterLink>
              <p v-if="u.bio" class="person-bio muted">{{ u.bio }}</p>
            </div>
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
        <h2 class="empty-title">Nenhum usuário bloqueado</h2>
        <p class="empty-desc muted">
          Você não bloqueou nenhum usuário. Leitores bloqueados não podem visualizar seus estudos, perfis ou enviar solicitações de correspondência.
        </p>
      </div>

      <div v-else class="friends-grid">
        <article
          v-for="item in blockedUsers"
          :key="item.friendship_id"
          class="person-card panel"
        >
          <div class="person-card-top">
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
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.75rem;
  margin: 0 0 0.5rem;
  color: var(--color-text);
}

.header-subtitle {
  margin: 0;
  max-width: 36rem;
  font-size: 0.95rem;
  color: var(--color-text-muted);
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
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  font-size: 0.875rem;
  color: var(--color-text);
}

.chip-number {
  font-weight: 700;
  font-size: 1.1rem;
}

.chip.highlight {
  background-color: var(--color-surface-soft);
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
  background-color: var(--color-surface-soft);
  border: 1px solid var(--color-accent);
  color: var(--color-accent);
  border-radius: var(--radius-sm, 6px);
}

.tabs-nav {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--color-border);
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
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  background-color: var(--color-tab-hover);
  color: var(--color-tab-hover-text);
}

.tab-btn:hover .tab-badge:not(.alert) {
  color: var(--color-tab-hover-text);
}

.tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  font-weight: 600;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.1rem 0.5rem;
  border-radius: 9999px;
  background-color: var(--color-surface-soft);
  color: var(--color-text);
}

.tab-badge.alert {
  background-color: var(--color-accent);
  color: var(--color-surface);
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem;
  color: var(--color-text-muted);
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
  color: var(--color-text);
}

.count-badge {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.1rem 0.45rem;
  border-radius: 9999px;
  background-color: var(--color-surface-soft);
  color: var(--color-text);
}

.empty-substate {
  padding: 1.5rem;
  text-align: center;
  background-color: var(--color-surface);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-surface, 10px);
  color: var(--color-text-muted);
}

.person-card {
  display: flex;
  flex-direction: column;
  padding: 1.25rem;
  border-radius: var(--radius-surface, 10px);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  gap: 1rem;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}

.person-card:hover {
  background-color: var(--color-surface-hover, var(--color-surface-soft));
  border-color: var(--color-border-hover, var(--color-primary));
}

.person-card-top {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
}

.person-avatar-link {
  text-decoration: none;
  display: block;
}

.person-avatar {
  width: 52px;
  height: 52px;
  flex-shrink: 0;
}

.avatar-img {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--color-border);
}

.avatar-initials {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background-color: var(--color-surface-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.person-info {
  flex: 1;
  min-width: 0;
}

.person-name-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.person-name-link:hover .person-name {
  color: var(--color-primary);
}

.person-name {
  margin: 0;
  font-size: 1.05rem;
  color: var(--color-text);
}

.person-handle {
  font-size: 0.85rem;
  display: block;
  margin-bottom: 0.35rem;
  color: var(--color-text-muted);
}

.person-bio {
  font-size: 0.85rem;
  margin: 0.25rem 0 0.5rem;
  line-height: 1.35;
  color: var(--color-text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta-since {
  font-size: 0.75rem;
  display: block;
  color: var(--color-text-muted);
}

.person-actions {
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border-subtle, var(--color-border));
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-surface, 10px);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 1rem;
  outline: none;
  color: var(--color-text);
}

.discover-guide {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: var(--radius-surface, 10px);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
}

.guide-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.guide-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background-color: var(--color-surface-soft);
  color: var(--color-primary);
  flex-shrink: 0;
}

.guide-title {
  margin: 0 0 0.25rem;
  font-size: 1.15rem;
  color: var(--color-text);
}

.guide-desc {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
  color: var(--color-text-muted);
}

.suggestions-wrapper {
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.suggestions-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-weight: 600;
  display: block;
  margin-bottom: 0.5rem;
}

.suggestions-chips {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.suggestion-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  background-color: var(--color-surface-soft);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  font-size: 0.825rem;
  cursor: pointer;
  min-height: 36px;
  transition: all 0.15s ease;
}

.suggestion-chip:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.empty-state {
  text-align: center;
  padding: 3.5rem 1.5rem;
  border-radius: var(--radius-surface, 12px);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
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

.friends-empty-state {
  max-width: 540px;
  margin: 1.5rem auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1rem;
}

.empty-icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--color-surface-soft);
  color: var(--color-primary);
  margin-bottom: 0.25rem;
}

.empty-title {
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0;
  color: var(--color-text);
}

.empty-desc {
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0;
  max-width: 440px;
  color: var(--color-text-muted);
}

.empty-actions {
  margin-top: 0.5rem;
}

.action-btn {
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem 1.15rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: var(--radius-sm, 6px);
  cursor: pointer;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
