<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api, errorMessage } from '../services/api.ts'
import { useInboxCount } from '../composables/useInboxCount.ts'
import QuickThoughtDrop from '../components/inbox/QuickThoughtDrop.vue'
import CaptureItemCard from '../components/inbox/CaptureItemCard.vue'
import LinkToStudyModal from '../components/inbox/LinkToStudyModal.vue'
import Icon from '../components/ui/Icon.vue'
import type { InboxCapture, TriageFilterTab } from '../types.ts'

const router = useRouter()
const { pendingCount, refreshCount, decrement, increment } = useInboxCount()

// Estados principais
const captures = ref<InboxCapture[]>([])
const loading = ref(true)
const fetchError = ref<string | null>(null)
const activeTab = ref<TriageFilterTab>('inbox')
const searchQuery = ref('')
const selectedIndex = ref<number>(-1)
const exitingCaptureIds = ref<Set<number>>(new Set())

// Referência ao campo Quick Thought Drop
const quickThoughtDropRef = ref<InstanceType<typeof QuickThoughtDrop> | null>(null)

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
  selectedIndex.value = -1
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

function handleTabChange(tab: TriageFilterTab) {
  if (activeTab.value === tab) return
  activeTab.value = tab
  selectedIndex.value = -1
  loadCaptures()
}

function onCaptureCreated(created: InboxCapture) {
  if (activeTab.value === 'inbox' || activeTab.value === 'all') {
    captures.value.unshift(created)
  }
  selectedIndex.value = 0
  refreshCount()
}

async function handleArchive(capture: InboxCapture) {
  exitingCaptureIds.value.add(capture.id)
  decrement()

  try {
    await api.updateInboxCapture(capture.id, { status: 'archived' })
  } catch (err) {
    // Reverte em caso de erro
    exitingCaptureIds.value.delete(capture.id)
    increment()
    fetchError.value = 'Não foi possível arquivar a nota. Tente novamente.'
    return
  }

  // Aguarda a animação cinética de 180ms
  setTimeout(() => {
    exitingCaptureIds.value.delete(capture.id)
    if (activeTab.value === 'inbox') {
      captures.value = captures.value.filter((c) => c.id !== capture.id)
      if (selectedIndex.value >= captures.value.length) {
        selectedIndex.value = Math.max(0, captures.value.length - 1)
      }
    } else {
      const idx = captures.value.findIndex((c) => c.id === capture.id)
      if (idx !== -1) {
        captures.value[idx] = { ...capture, status: 'archived' }
      }
    }
  }, 180)
}

async function handleUnarchive(capture: InboxCapture) {
  exitingCaptureIds.value.add(capture.id)
  increment()

  try {
    await api.updateInboxCapture(capture.id, { status: 'inbox' })
  } catch (err) {
    exitingCaptureIds.value.delete(capture.id)
    decrement()
    fetchError.value = 'Não foi possível mover a nota de volta para pendentes.'
    return
  }

  setTimeout(() => {
    exitingCaptureIds.value.delete(capture.id)
    if (activeTab.value === 'archived') {
      captures.value = captures.value.filter((c) => c.id !== capture.id)
    } else {
      const idx = captures.value.findIndex((c) => c.id === capture.id)
      if (idx !== -1) {
        captures.value[idx] = { ...capture, status: 'inbox' }
      }
    }
  }, 180)
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
  if (selectedIndex.value >= captures.value.length) {
    selectedIndex.value = Math.max(0, captures.value.length - 1)
  }
  refreshCount()
}

// Guarda defensiva e controle de teclado ergonômico
function isEditableTarget(target: EventTarget | null): boolean {
  if (!target || !(target instanceof HTMLElement)) return false
  const tag = target.tagName
  return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || target.isContentEditable
}

function handleGlobalKeydown(e: KeyboardEvent) {
  // Atalho global Ctrl+Shift+C para focar captura rápida
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'C' || e.key === 'c')) {
    e.preventDefault()
    quickThoughtDropRef.value?.focus()
    selectedIndex.value = -1
    return
  }

  // Guarda estrita: ignora atalhos de navegação durante digitação
  if (isEditableTarget(e.target)) {
    return
  }

  const total = filteredCaptures.value.length
  if (total === 0) return

  if (e.key === 'j' || e.key === 'J') {
    e.preventDefault()
    selectedIndex.value = selectedIndex.value < total - 1 ? selectedIndex.value + 1 : 0
    scrollToSelected()
  } else if (e.key === 'k' || e.key === 'K') {
    e.preventDefault()
    selectedIndex.value = selectedIndex.value > 0 ? selectedIndex.value - 1 : total - 1
    scrollToSelected()
  } else if (e.key === 'e' || e.key === 'E') {
    if (selectedIndex.value >= 0 && selectedIndex.value < total) {
      e.preventDefault()
      const target = filteredCaptures.value[selectedIndex.value]
      if (target.status === 'inbox') {
        handleArchive(target)
      }
    }
  }
}

async function scrollToSelected() {
  await nextTick()
  const selectedCard = document.querySelector('.capture-card.is-keyboard-selected')
  if (selectedCard) {
    selectedCard.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  }
}

watch(activeTab, () => {
  loadCaptures()
})

onMounted(async () => {
  window.addEventListener('keydown', handleGlobalKeydown)
  await Promise.all([loadCaptures(), refreshCount()])
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
})
</script>

<template>
  <div class="inbox-view">
    <!-- Cabeçalho Editorial -->
    <header class="page-header">
      <div class="header-content">
        <p class="eyebrow">Triagem e Captura</p>
        <h1 class="page-title">Mesa de Triagem</h1>
        <p class="page-subtitle">
          Descarrego imediato e organização de pensamentos provisórios antes de formalizá-los em estudos.
        </p>
      </div>

      <div class="header-actions">
        <kbd class="shortcut-pill" title="Atalho global para focar captura">Ctrl+Shift+C</kbd>
      </div>
    </header>

    <!-- Campo Permanente Superior: Quick Thought Drop -->
    <section class="quick-drop-section" aria-label="Área de Despejo de Pensamentos">
      <QuickThoughtDrop
        ref="quickThoughtDropRef"
        @created="onCaptureCreated"
      />
    </section>

    <!-- Barra Segmentada de Triagem e Busca -->
    <div class="inbox-toolbar">
      <nav
        class="triage-segmented-bar"
        role="tablist"
        aria-label="Filtro de capturas por segmento de triagem"
      >
        <button
          type="button"
          role="tab"
          class="segment-button"
          :class="{ 'is-active': activeTab === 'inbox' }"
          :aria-selected="activeTab === 'inbox'"
          @click="handleTabChange('inbox')"
        >
          <span>Pendentes</span>
          <span v-if="pendingCount > 0" class="tab-badge" aria-label="Quantidade pendente">
            {{ pendingCount }}
          </span>
        </button>

        <button
          type="button"
          role="tab"
          class="segment-button"
          :class="{ 'is-active': activeTab === 'promoted' }"
          :aria-selected="activeTab === 'promoted'"
          @click="handleTabChange('promoted')"
        >
          <span>Promovidos</span>
        </button>

        <button
          type="button"
          role="tab"
          class="segment-button"
          :class="{ 'is-active': activeTab === 'linked' }"
          :aria-selected="activeTab === 'linked'"
          @click="handleTabChange('linked')"
        >
          <span>Vinculados</span>
        </button>

        <button
          type="button"
          role="tab"
          class="segment-button"
          :class="{ 'is-active': activeTab === 'archived' }"
          :aria-selected="activeTab === 'archived'"
          @click="handleTabChange('archived')"
        >
          <span>Arquivados</span>
        </button>

        <button
          type="button"
          role="tab"
          class="segment-button"
          :class="{ 'is-active': activeTab === 'all' }"
          :aria-selected="activeTab === 'all'"
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
            placeholder="Pesquisar notas na mesa..."
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
      <!-- Estado de Erro Editorial -->
      <div v-if="fetchError" class="notice error-card" role="alert">
        <div class="error-content">
          <p class="error-message">{{ fetchError }}</p>
          <button type="button" class="button button-sm button-secondary retry-btn" @click="loadCaptures">
            Tentar novamente
          </button>
        </div>
      </div>

      <!-- Estado de Carregamento -->
      <div v-else-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Carregando notas da mesa de triagem...</p>
      </div>

      <!-- Estado Vazio Editorial: "Mesa Limpa" -->
      <div
        v-else-if="filteredCaptures.length === 0"
        class="inbox-empty-state"
        role="region"
        aria-label="Mesa Limpa"
      >
        <div class="empty-icon-wrap">
          <Icon name="inbox" size="lg" />
        </div>
        <h2 class="empty-title">
          <span v-if="searchQuery">Nenhuma nota encontrada</span>
          <span v-else-if="activeTab === 'inbox'">Mesa Limpa</span>
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
            Todos os seus pensamentos foram acolhidos e integrados ao seu acervo. Use o campo acima ou pressione <kbd>Ctrl+Shift+C</kbd> para registrar novos insights.
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
      </div>

      <!-- Grid / Lista de Capturas -->
      <div v-else class="captures-grid">
        <CaptureItemCard
          v-for="(item, idx) in filteredCaptures"
          :key="item.id"
          :capture="item"
          :is-selected="selectedIndex === idx"
          :is-exiting="exitingCaptureIds.has(item.id)"
          @archive="handleArchive"
          @unarchive="handleUnarchive"
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
  color: var(--color-link);
  margin-bottom: 4px;
}

.page-title {
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 6px;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 0.95rem;
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.45;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.shortcut-pill {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 4px 8px;
  display: inline-block;
}

.quick-drop-section {
  width: 100%;
}

/* Barra Segmentada de Triagem */
.inbox-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.triage-segmented-bar {
  display: flex;
  align-items: center;
  gap: 4px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 8px);
  padding: 4px;
  overflow-x: auto;
  max-width: 100%;
  scrollbar-width: none;
}

.triage-segmented-bar::-webkit-scrollbar {
  display: none;
}

.segment-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm, 6px);
  padding: 6px 14px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-muted);
  cursor: pointer;
  white-space: nowrap;
  transition: all 150ms ease;
  min-height: 38px;
}

.segment-button:hover {
  color: var(--color-text);
  background-color: var(--color-surface-hover);
}

.segment-button.is-active {
  color: var(--color-text);
  background-color: var(--color-surface-hover);
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.tab-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 9999px;
  background-color: var(--color-primary);
  color: #ffffff;
}

/* Busca Integrada */
.search-filter-box {
  flex: 1 1 240px;
  max-width: 320px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 10px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.inbox-search-input {
  width: 100%;
  padding: 8px 32px 8px 30px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 6px);
  background-color: var(--color-surface);
  color: var(--color-text);
  font-size: 0.875rem;
  outline: none;
  transition: border-color 150ms ease;
}

.inbox-search-input:focus {
  border-color: var(--color-accent);
}

.clear-search-btn {
  position: absolute;
  right: 8px;
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 2px;
  display: inline-flex;
}

/* Conteúdo Principal */
.inbox-content {
  min-height: 240px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 48px 16px;
  color: var(--color-text-muted);
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Notificação Editorial de Erro */
.error-card {
  padding: 16px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 8px);
}

.error-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.error-message {
  margin: 0;
  color: var(--color-text);
  font-size: 0.9rem;
}

.retry-btn {
  min-height: 36px;
}

/* Estado Vazio "Mesa Limpa" */
.inbox-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 48px 24px;
  background-color: var(--color-surface);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-lg, 12px);
  gap: 12px;
}

.empty-icon-wrap {
  width: 56px;
  height: 56px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: var(--color-surface-hover);
  color: var(--color-text-muted);
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.empty-description {
  font-size: 0.95rem;
  color: var(--color-text-muted);
  max-width: 480px;
  margin: 0;
  line-height: 1.5;
}

.captures-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Layout Móvel e Acessibilidade Tátil */
@media (max-width: 640px) {
  .inbox-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-filter-box {
    max-width: 100%;
  }

  .segment-button {
    min-height: 44px;
    padding: 8px 16px;
  }
}
</style>
