<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api, errorMessage } from '../services/api'
import { useInboxCount } from '../composables/useInboxCount'
import { useQuickCapture } from '../composables/useQuickCapture'
import CaptureItemCard from '../components/inbox/CaptureItemCard.vue'
import LinkToStudyModal from '../components/inbox/LinkToStudyModal.vue'
import Icon from '../components/ui/Icon.vue'
import type { InboxCapture, InboxStatus } from '../types'

const router = useRouter()
const { pendingCount, refreshCount } = useInboxCount()
const quickCapture = useQuickCapture()

// Estados principais
const captures = ref<InboxCapture[]>([])
const loading = ref(true)
const fetchError = ref<string | null>(null)
const activeTab = ref<InboxStatus | 'all'>('inbox')
const searchQuery = ref('')

// Controle do modal de vinculação
const linkModalOpen = ref(false)
const captureToLink = ref<InboxCapture | null>(null)

let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

const filteredCaptures = computed(() => {
  return captures.value
})

async function loadCaptures() {
  loading.value = true
  fetchError.value = null
  try {
    const list = await api.getInboxCaptures({
      status: activeTab.value,
      q: searchQuery.value.trim() || undefined,
      limit: 100,
    })
    captures.value = list
  } catch (err) {
    fetchError.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}

function onSearchInput() {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    loadCaptures()
  }, 250)
}

function clearSearch() {
  searchQuery.value = ''
  loadCaptures()
}

function handleTabChange(tab: InboxStatus | 'all') {
  if (activeTab.value === tab) return
  activeTab.value = tab
  loadCaptures()
}

function handlePromote(capture: InboxCapture) {
  const query: Record<string, string> = {
    promote_inbox_id: String(capture.id),
  }
  if (capture.book_id) {
    query.book = String(capture.book_id)
  }
  router.push({
    path: '/importar',
    query,
  })
}

function handleOpenLink(capture: InboxCapture) {
  captureToLink.value = capture
  linkModalOpen.value = true
}

function handleCaptureLinked(updated: InboxCapture) {
  const index = captures.value.findIndex((c) => c.id === updated.id)
  if (index !== -1) {
    if (activeTab.value === 'inbox') {
      // Remove da aba de pendentes
      captures.value.splice(index, 1)
    } else {
      captures.value[index] = updated
    }
  }
  refreshCount()
}

function handleCaptureUpdated(updated: InboxCapture) {
  const index = captures.value.findIndex((c) => c.id === updated.id)
  if (index !== -1) {
    captures.value[index] = updated
  }
  refreshCount()
}

function handleCaptureDeleted(deletedId: number) {
  captures.value = captures.value.filter((c) => c.id !== deletedId)
  refreshCount()
}

function openNewCapture() {
  quickCapture.open()
}

watch(activeTab, () => {
  loadCaptures()
})

onMounted(async () => {
  await Promise.all([loadCaptures(), refreshCount()])
})
</script>

<template>
  <div class="inbox-view">
    <!-- Cabeçalho da Visão -->
    <header class="page-header">
      <div class="header-content">
        <p class="eyebrow">Triagem e Captura</p>
        <h1 class="page-title">Caixa de Entrada de Capturas</h1>
        <p class="page-subtitle">
          Despeje pensamentos, citações e ideias provisórias antes de formalizá-los em estudos completos.
        </p>
      </div>

      <div class="header-actions">
        <button
          type="button"
          class="button primary button-create-capture"
          title="Nova Captura Rápida (Ctrl+Shift+C)"
          @click="openNewCapture"
        >
          <Icon name="plus" size="sm" />
          <span>Nova Captura</span>
          <kbd class="shortcut-pill">Ctrl+Shift+C</kbd>
        </button>
      </div>
    </header>

    <!-- Barra de Ferramentas: Abas e Busca -->
    <div class="inbox-toolbar">
      <nav class="status-tabs" aria-label="Filtro de capturas por status">
        <button
          type="button"
          class="tab-button"
          :class="{ 'is-active': activeTab === 'inbox' }"
          @click="handleTabChange('inbox')"
        >
          <span>Pendentes</span>
          <span v-if="pendingCount > 0" class="tab-badge">
            {{ pendingCount }}
          </span>
        </button>

        <button
          type="button"
          class="tab-button"
          :class="{ 'is-active': activeTab === 'promoted' }"
          @click="handleTabChange('promoted')"
        >
          <span>Promovidos</span>
        </button>

        <button
          type="button"
          class="tab-button"
          :class="{ 'is-active': activeTab === 'linked' }"
          @click="handleTabChange('linked')"
        >
          <span>Vinculados</span>
        </button>

        <button
          type="button"
          class="tab-button"
          :class="{ 'is-active': activeTab === 'archived' }"
          @click="handleTabChange('archived')"
        >
          <span>Arquivados</span>
        </button>

        <button
          type="button"
          class="tab-button"
          :class="{ 'is-active': activeTab === 'all' }"
          @click="handleTabChange('all')"
        >
          <span>Todos</span>
        </button>
      </nav>

      <div class="search-filter-box">
        <div class="search-input-wrapper">
          <Icon name="search" size="xs" class="search-icon" />
          <input
            v-model="searchQuery"
            type="search"
            class="inbox-search-input"
            placeholder="Pesquisar no Inbox..."
            aria-label="Pesquisar capturas"
            @input="onSearchInput"
          />
          <button
            v-if="searchQuery"
            type="button"
            class="clear-search-btn"
            aria-label="Limpar pesquisa"
            @click="clearSearch"
          >
            <Icon name="x" size="xs" />
          </button>
        </div>
      </div>
    </div>

    <!-- Conteúdo Principal -->
    <main class="inbox-content">
      <!-- Estado de Erro -->
      <div v-if="fetchError" class="notice error" role="alert">
        <p>{{ fetchError }}</p>
        <button type="button" class="secondary" @click="loadCaptures">
          Tentar novamente
        </button>
      </div>

      <!-- Estado de Carregamento -->
      <div v-else-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Carregando anotações do Inbox...</p>
      </div>

      <!-- Estado Vazio -->
      <div
        v-else-if="filteredCaptures.length === 0"
        class="inbox-empty-state"
        role="region"
        aria-label="Caixa de entrada vazia"
      >
        <div class="empty-icon-wrap">
          <Icon name="inbox" size="lg" />
        </div>
        <h2 class="empty-title">
          <span v-if="searchQuery">Nenhuma captura encontrada</span>
          <span v-else-if="activeTab === 'inbox'">Sua Caixa de Entrada está vazia</span>
          <span v-else-if="activeTab === 'promoted'">Nenhuma captura promovida</span>
          <span v-else-if="activeTab === 'linked'">Nenhuma captura vinculada</span>
          <span v-else-if="activeTab === 'archived'">Nenhuma captura arquivada</span>
          <span v-else>Nenhuma captura registrada</span>
        </h2>
        <p class="empty-description">
          <span v-if="searchQuery">
            Não encontramos resultados para "{{ searchQuery }}". Tente buscar por outros termos.
          </span>
          <span v-else-if="activeTab === 'inbox'">
            Excelente momento para registrar um insight! Pressione <kbd>Ctrl+Shift+C</kbd> ou clique no botão abaixo para adicionar notas rápidas sem sair do seu fluxo.
          </span>
          <span v-else-if="activeTab === 'promoted'">
            Capturas que você transformar em estudos formais aparecerão organizadas aqui com links diretos.
          </span>
          <span v-else-if="activeTab === 'linked'">
            Capturas anexadas a estudos existentes do seu acervo serão preservadas nesta aba.
          </span>
          <span v-else>
            Seu histórico de anotações temporárias aparecerá aqui.
          </span>
        </p>

        <button
          v-if="!searchQuery && activeTab === 'inbox'"
          type="button"
          class="button primary empty-cta-btn"
          @click="openNewCapture"
        >
          <Icon name="plus" size="sm" />
          <span>Registrar Primeira Captura</span>
        </button>
      </div>

      <!-- Grid / Lista de Capturas -->
      <div v-else class="captures-grid">
        <CaptureItemCard
          v-for="item in filteredCaptures"
          :key="item.id"
          :capture="item"
          @promote="handlePromote"
          @link="handleOpenLink"
          @updated="handleCaptureUpdated"
          @deleted="handleCaptureDeleted"
        />
      </div>
    </main>

    <!-- Modal de Vinculação a Estudo Existente -->
    <LinkToStudyModal
      :is-open="linkModalOpen"
      :capture="captureToLink"
      @close="linkModalOpen = false"
      @linked="handleCaptureLinked"
    />
  </div>
</template>

<style scoped>
.inbox-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1080px;
  margin: 0 auto;
  padding: 8px 16px 40px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.header-content {
  flex: 1 1 300px;
}

.eyebrow {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-primary, #4f46e5);
  margin-bottom: 4px;
}

.page-title {
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--color-text-main, #111827);
  margin: 0 0 6px;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 0.95rem;
  color: var(--color-text-muted, #6b7280);
  margin: 0;
  max-width: 600px;
  line-height: 1.5;
}

.button-create-capture {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  min-height: 44px;
  font-weight: 600;
  font-size: 0.9rem;
  border-radius: var(--radius-control, 8px);
  background-color: var(--color-accent, #2563eb);
  color: #ffffff;
  border: 1px solid transparent;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(37, 99, 235, 0.2);
  transition: all 0.15s ease;
  white-space: nowrap;
}

.button-create-capture:hover {
  background-color: var(--color-accent-hover, #1d4ed8);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(37, 99, 235, 0.25);
  transform: translateY(-1px);
}

.button-create-capture:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

.button-create-capture:focus-visible {
  outline: 2px solid var(--color-accent, #2563eb);
  outline-offset: 2px;
}

.shortcut-pill {
  display: inline-block;
  font-size: 0.7rem;
  font-family: var(--font-mono, monospace);
  background-color: rgba(255, 255, 255, 0.22);
  color: #ffffff;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.35);
  letter-spacing: 0.02em;
}

@media (max-width: 640px) {
  .shortcut-pill {
    display: none;
  }
}

.inbox-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding: 12px 16px;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 10px;
}

.status-tabs {
  display: flex;
  align-items: center;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.tab-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-muted, #4b5563);
  cursor: pointer;
  min-height: 44px;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.tab-button:hover {
  background-color: var(--color-surface-hover, #f3f4f6);
  color: var(--color-text-main, #111827);
}

.tab-button.is-active {
  background-color: var(--color-primary-light, #eef2ff);
  color: var(--color-primary, #4f46e5);
  font-weight: 600;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 6px;
  font-size: 0.72rem;
  font-weight: 700;
  border-radius: 9999px;
  background-color: var(--color-primary, #4f46e5);
  color: #ffffff;
}

.search-filter-box {
  flex: 1 1 240px;
  max-width: 320px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--color-text-muted, #9ca3af);
  pointer-events: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.inbox-search-input {
  width: 100%;
  padding: 8px 36px 8px 36px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  background-color: var(--color-surface, #ffffff);
  font-size: 0.875rem;
  color: var(--color-text-main, #111827);
  min-height: 44px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.inbox-search-input:focus {
  outline: none;
  border-color: var(--color-accent, #2563eb);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.clear-search-btn {
  position: absolute;
  right: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-text-muted, #9ca3af);
  padding: 4px;
  min-width: 36px;
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: color 0.15s ease, background-color 0.15s ease;
}

.clear-search-btn:hover {
  color: var(--color-text-main, #111827);
  background-color: var(--color-surface-hover, #f3f4f6);
}

.inbox-content {
  min-height: 300px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 20px;
  color: var(--color-text-muted, #6b7280);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(79, 70, 229, 0.2);
  border-top-color: var(--color-primary, #4f46e5);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}

.inbox-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 60px 24px;
  background-color: var(--color-surface, #ffffff);
  border: 1px dashed var(--color-border, #d1d5db);
  border-radius: 12px;
}

.empty-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: var(--color-primary-light, #eef2ff);
  color: var(--color-primary, #4f46e5);
  margin-bottom: 16px;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-main, #111827);
  margin: 0 0 8px;
}

.empty-description {
  font-size: 0.9rem;
  color: var(--color-text-muted, #6b7280);
  max-width: 480px;
  line-height: 1.5;
  margin: 0 0 20px;
}

.empty-description kbd {
  display: inline-block;
  padding: 2px 6px;
  font-size: 0.75rem;
  background-color: var(--color-surface-hover, #f3f4f6);
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 4px;
}

.empty-cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
}

.captures-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  .header-actions {
    display: flex;
  }
  .button-create-capture {
    width: 100%;
    justify-content: center;
  }
  .inbox-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .search-filter-box {
    max-width: 100%;
  }
}
</style>
