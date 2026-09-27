<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { sharingApi } from '../../api/sharing.ts'
import type { SharedStudySummary } from '../../types.ts'
import Icon from '../ui/Icon.vue'
import LoadingSkeleton from '../ui/LoadingSkeleton.vue'

const loading = ref(true)
const loadError = ref<string | null>(null)
const items = ref<SharedStudySummary[]>([])
const total = ref(0)

const searchQuery = ref('')
const authorFilter = ref('')
let debounceTimer: ReturnType<typeof setTimeout> | null = null

async function fetchSharedStudies() {
  loading.value = true
  loadError.value = null
  try {
    const res = await sharingApi.getSharedStudies({
      q: searchQuery.value.trim() || undefined,
      author: authorFilter.value.trim().replace(/^@/, '') || undefined,
      limit: 50,
    })
    items.value = res.items
    total.value = res.total
  } catch (err: unknown) {
    loadError.value = err instanceof Error ? err.message : 'Falha ao carregar estudos compartilhados.'
  } finally {
    loading.value = false
  }
}

function onSearchInput() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchSharedStudies()
  }, 300)
}

function clearFilters() {
  searchQuery.value = ''
  authorFilter.value = ''
  fetchSharedStudies()
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso)
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    }).format(d)
  } catch {
    return iso
  }
}

function getVisibilityLabel(vis: string): { label: string } {
  switch (vis) {
    case 'public':
      return { label: 'Público' }
    case 'friends':
      return { label: 'Amigos' }
    case 'custom':
      return { label: 'Nominal' }
    default:
      return { label: 'Compartilhado' }
  }
}

onMounted(fetchSharedStudies)
</script>

<template>
  <div class="shared-studies-container">
    <!-- Barra de Filtros e Busca -->
    <div class="shared-filters-bar">
      <div class="filters-inputs-row">
        <!-- Input de busca textual -->
        <div class="search-input-box">
          <Icon name="search" :size="16" class="search-input-icon" />
          <input
            v-model="searchQuery"
            type="search"
            placeholder="Buscar por título ou tema..."
            class="shared-search-input"
            aria-label="Buscar estudos compartilhados por texto"
            @input="onSearchInput"
          />
        </div>

        <!-- Input de busca por autor -->
        <div class="author-input-box">
          <span class="author-prefix" aria-hidden="true">@</span>
          <input
            v-model="authorFilter"
            type="search"
            placeholder="autor (username)"
            class="shared-author-input"
            aria-label="Filtrar estudos compartilhados por autor"
            @input="onSearchInput"
          />
        </div>
      </div>

      <div v-if="searchQuery || authorFilter" class="filters-actions">
        <button
          type="button"
          class="clear-filters-btn"
          @click="clearFilters"
        >
          Limpar filtros
        </button>
      </div>
    </div>

    <!-- Indicador de Carregamento (Skeletons) -->
    <div v-if="loading" class="shared-grid" role="status" aria-label="Carregando estudos compartilhados">
      <div
        v-for="i in 4"
        :key="i"
        class="shared-study-card skeleton-card"
      >
        <div class="card-header">
          <div class="card-author">
            <LoadingSkeleton shape="circle" width="32px" height="32px" />
            <div class="author-skeleton-lines">
              <LoadingSkeleton shape="text" width="100px" height="14px" />
              <LoadingSkeleton shape="text" width="60px" height="11px" />
            </div>
          </div>
          <LoadingSkeleton shape="rect" width="60px" height="20px" />
        </div>
        <div class="card-body">
          <LoadingSkeleton shape="text" width="80%" height="20px" />
          <LoadingSkeleton shape="text" width="50%" height="14px" />
        </div>
      </div>
    </div>

    <!-- Mensagem de Erro -->
    <div
      v-else-if="loadError"
      class="shared-error-alert"
      role="alert"
    >
      <div class="error-content">
        <Icon name="alert-triangle" :size="18" class="error-icon" />
        <span class="error-text">{{ loadError }}</span>
      </div>
      <button
        type="button"
        class="retry-btn"
        @click="fetchSharedStudies"
      >
        Tentar novamente
      </button>
    </div>

    <!-- Lista Vazia -->
    <div
      v-else-if="items.length === 0"
      class="shared-empty-state"
    >
      <div class="empty-icon-wrap" aria-hidden="true">
        <Icon name="users" :size="48" class="empty-state-svg" />
      </div>
      <h3 class="empty-title">
        {{ searchQuery || authorFilter ? 'Nenhum estudo corresponde à busca' : 'Nenhum estudo compartilhado com você' }}
      </h3>
      <p class="empty-description">
        {{
          searchQuery || authorFilter
            ? 'Tente ajustar os termos de busca ou limpar os filtros para encontrar outros estudos.'
            : 'Quando seus amigos no Leitorum ou outros leitores compartilharem estudos e livros, eles aparecerão aqui para você ler e consultar.'
        }}
      </p>
      <div v-if="searchQuery || authorFilter" class="empty-action">
        <button
          type="button"
          class="reset-filters-btn"
          @click="clearFilters"
        >
          Ver todos os compartilhados
        </button>
      </div>
    </div>

    <!-- Grid de Estudos Compartilhados -->
    <div v-else class="shared-grid">
      <article
        v-for="item in items"
        :key="item.id"
        class="shared-study-card"
      >
        <div class="card-content">
          <!-- Cabeçalho do Card: Autor + Badge de Visibilidade -->
          <div class="card-header">
            <div class="card-author">
              <div class="avatar-circle">
                <img
                  v-if="item.owner_avatar_url"
                  :src="item.owner_avatar_url"
                  :alt="item.owner_display_name"
                  class="avatar-image"
                />
                <span v-else>{{ item.owner_display_name.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="author-info">
                <p class="author-name">
                  {{ item.owner_display_name }}
                </p>
                <p class="author-handle">
                  @{{ item.owner_username }}
                </p>
              </div>
            </div>

            <span
              class="visibility-badge"
              :title="`Visibilidade: ${item.visibility}`"
            >
              <span>{{ getVisibilityLabel(item.visibility).label }}</span>
            </span>
          </div>

          <!-- Título do Estudo -->
          <div class="card-body">
            <h3 class="study-title">
              <RouterLink :to="{ name: 'study', params: { bookId: item.book_id, studyId: item.id } }">
                {{ item.title }}
              </RouterLink>
            </h3>
            <p class="book-subtitle">
              <span class="book-name">{{ item.book_title }}</span>
              <span v-if="item.chapter_name"> · {{ item.chapter_name }}</span>
            </p>
          </div>
        </div>

        <!-- Rodapé do Card -->
        <div class="card-footer">
          <span class="update-date">Atualizado em {{ formatDate(item.updated_at) }}</span>
          <RouterLink
            :to="{ name: 'study', params: { bookId: item.book_id, studyId: item.id } }"
            class="open-study-link"
            aria-label="Abrir estudo em modo somente leitura"
          >
            Abrir leitura →
          </RouterLink>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.shared-studies-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 1.5);
}

.shared-filters-bar {
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 0.75);
}

@media (min-width: 640px) {
  .shared-filters-bar {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.filters-inputs-row {
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 0.65);
  flex: 1;
}

@media (min-width: 640px) {
  .filters-inputs-row {
    flex-direction: row;
    align-items: center;
  }
}

.search-input-box {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.search-input-icon {
  position: absolute;
  left: 0.875rem;
  color: var(--color-muted);
  pointer-events: none;
  width: 16px;
  height: 16px;
}

.shared-search-input {
  width: 100%;
  padding: calc(var(--space-unit) * 0.65) calc(var(--space-unit) * 0.85);
  padding-left: 2.35rem;
  font-size: 0.875rem;
  border-radius: var(--radius-control);
  background: var(--color-surface);
  border: var(--border-width) solid var(--color-border);
  color: var(--color-text);
  min-height: 44px;
  outline: none;
  box-shadow: var(--shadow-control);
}

.shared-search-input:focus {
  border-color: var(--color-accent);
}

.author-input-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

@media (min-width: 640px) {
  .author-input-box {
    width: 14rem;
  }
}

.author-prefix {
  position: absolute;
  left: 0.875rem;
  color: var(--color-muted);
  font-family: monospace;
  font-size: 0.875rem;
  pointer-events: none;
}

.shared-author-input {
  width: 100%;
  padding: calc(var(--space-unit) * 0.65) calc(var(--space-unit) * 0.85);
  padding-left: 2.1rem;
  font-size: 0.875rem;
  border-radius: var(--radius-control);
  background: var(--color-surface);
  border: var(--border-width) solid var(--color-border);
  color: var(--color-text);
  min-height: 44px;
  outline: none;
  box-shadow: var(--shadow-control);
}

.shared-author-input:focus {
  border-color: var(--color-accent);
}

.filters-actions {
  display: flex;
  align-items: center;
}

.clear-filters-btn {
  min-height: 44px;
  padding: 0 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: var(--radius-control);
  background: var(--color-surface-soft);
  color: var(--color-muted);
  border: var(--border-width) solid var(--color-border);
  cursor: pointer;
  transition: all 0.15s ease;
}

.clear-filters-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

/* Grid de cards */
.shared-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: calc(var(--space-unit) * 1);
}

@media (min-width: 768px) {
  .shared-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.shared-study-card {
  padding: calc(var(--space-unit) * 1.25);
  border-radius: var(--radius-card);
  border: var(--border-width) solid var(--color-border);
  background: var(--color-surface);
  box-shadow: var(--shadow-panel);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.shared-study-card:hover {
  border-color: var(--color-border-hover);
  background: var(--color-card-hover);
}

.skeleton-card {
  gap: calc(var(--space-unit) * 1);
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 0.75);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: calc(var(--space-unit) * 0.75);
}

.card-author {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  min-width: 0;
}

.author-skeleton-lines {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.avatar-circle {
  width: 2rem;
  height: 2rem;
  border-radius: 9999px;
  background: var(--color-surface-soft);
  color: var(--color-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8125rem;
  font-weight: 700;
  overflow: hidden;
  flex-shrink: 0;
  border: var(--border-width) solid var(--color-border);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.author-info {
  min-width: 0;
}

.author-name {
  font-size: 0.8125rem;
  font-weight: 650;
  color: var(--color-text);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.author-handle {
  font-size: 0.75rem;
  color: var(--color-muted);
  font-family: monospace;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.visibility-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  background: var(--color-surface-inset);
  color: var(--color-muted);
  border: var(--border-width) solid var(--color-border);
  flex-shrink: 0;
}

.card-body {
  margin-top: 0.25rem;
}

.study-title {
  font-size: 1.0625rem;
  font-weight: 650;
  line-height: 1.4;
  margin: 0;
  color: var(--color-text);
}

.study-title a {
  text-decoration: none;
  color: inherit;
  transition: color 0.15s ease;
}

.study-title a:hover {
  color: var(--color-accent);
}

.book-subtitle {
  font-size: 0.8125rem;
  color: var(--color-muted);
  margin: 0.35rem 0 0;
}

.book-name {
  font-weight: 600;
  color: var(--color-text);
}

.card-footer {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: var(--border-width) solid var(--color-border-list);
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--color-muted);
}

.open-study-link {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 650;
  color: var(--color-accent);
  text-decoration: none;
  border-radius: var(--radius-control);
  transition: background 0.15s ease, color 0.15s ease;
}

.open-study-link:hover {
  background: var(--color-surface-hover);
}

/* Erro */
.shared-error-alert {
  padding: calc(var(--space-unit) * 1);
  border-radius: var(--radius-control);
  background: var(--color-error-bg);
  color: var(--color-error-text);
  border: var(--border-width) solid var(--color-error-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: calc(var(--space-unit) * 0.75);
}

.error-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.error-icon {
  flex-shrink: 0;
  color: var(--color-error-marker);
  width: 18px;
  height: 18px;
}

.error-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.retry-btn {
  min-height: 44px;
  padding: 0.35rem 0.85rem;
  font-size: 0.8125rem;
  font-weight: 650;
  border-radius: var(--radius-control);
  background: var(--color-surface);
  color: var(--color-error-text);
  border: var(--border-width) solid var(--color-error-border);
  cursor: pointer;
}

/* Empty State */
.shared-empty-state {
  padding: calc(var(--space-unit) * 3) calc(var(--space-unit) * 1.5);
  text-align: center;
  border-radius: var(--radius-panel);
  border: var(--border-width) dashed var(--color-border);
  background: var(--color-surface);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: calc(var(--space-unit) * 0.75);
}

.empty-icon-wrap {
  display: flex;
  justify-content: center;
}

.empty-state-svg {
  max-width: 120px;
  max-height: 120px;
  width: 48px;
  height: 48px;
  color: var(--color-muted);
  margin: 0 auto;
}

.empty-title {
  font-size: 1.0625rem;
  font-weight: 650;
  color: var(--color-text);
  margin: 0;
}

.empty-description {
  font-size: 0.875rem;
  color: var(--color-muted);
  max-width: 32rem;
  line-height: 1.5;
  margin: 0;
}

.empty-action {
  margin-top: 0.5rem;
}

.reset-filters-btn {
  min-height: 44px;
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 650;
  border-radius: var(--radius-button);
  background: var(--color-accent);
  color: var(--color-on-accent);
  border: none;
  cursor: pointer;
  transition: background 0.15s ease;
}

.reset-filters-btn:hover {
  background: var(--color-accent-hover);
}
</style>
