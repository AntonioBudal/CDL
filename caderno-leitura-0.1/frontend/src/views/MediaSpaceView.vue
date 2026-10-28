<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api } from '../services/api'
import { useMediaSpace, OLDER_THAN_DAYS } from '../composables/useMediaSpace'
import EmptyState from '../components/ui/EmptyState.vue'
import LoadingSkeleton from '../components/ui/LoadingSkeleton.vue'
import Icon from '../components/ui/Icon.vue'
import TrashConfirmModal from '../components/TrashConfirmModal.vue'
import StorageMeter from '../components/media/StorageMeter.vue'
import MediaCard from '../components/media/MediaCard.vue'
import type { MediaItem, MediaKind, MediaSort } from '../types/media'
import { VAULT_STATE_TEXT, formatBytes, usageText } from '../utils/mediaFormat'

// Quem não é administrador vê só o estado do servidor, sem números (C-Q4).
const SERVER_LEVEL_TEXT = {
  normal: 'O servidor tem espaço para novas imagens.',
  high: 'O servidor está quase cheio.',
  full: 'O servidor está sem espaço para novas imagens.',
} as const

const router = useRouter()
const space = useMediaSpace({
  usage: api.getMediaUsage,
  list: api.listMedia,
  setKeep: api.setMediaKeep,
  remove: api.deleteMedia,
  bulk: api.bulkDeleteMedia,
})
const { state } = space
const viewing = ref<MediaItem | null>(null)
const closeButton = ref<HTMLButtonElement | null>(null)
watch(viewing, async (item) => {
  if (item) {
    await nextTick()
    closeButton.value?.focus()
  }
})

const vaultState = computed(() => state.usage?.vault?.state ?? 'ready')
const vaultLocked = computed(() => vaultState.value !== 'ready')
const userText = computed(() => state.usage
  ? `Seu espaço: ${usageText(state.usage.user.used_bytes, state.usage.user.quota_bytes, state.usage.user.count)}`
  : '')
const server = computed(() => state.usage?.server ?? null)
const serverText = computed(() => {
  const value = server.value
  if (!value) return ''
  if (value.used_bytes === undefined || value.quota_bytes === undefined) {
    return SERVER_LEVEL_TEXT[value.level]
  }
  const free = value.disk_free_bytes != null ? ` · ${formatBytes(value.disk_free_bytes)} livres no HD` : ''
  return `Capacidade geral do servidor: ${formatBytes(value.used_bytes)} de ${formatBytes(value.quota_bytes)}${free}`
})
const completedLabel = computed(() => {
  const preview = state.previews.completed
  return preview && preview.matched > 0
    ? `Apagar fotos de estudos concluídos (${preview.matched}, ${formatBytes(preview.freed_bytes)})`
    : 'Nenhuma foto de estudo concluído'
})
const olderLabel = computed(() => {
  const preview = state.previews.older
  return preview && preview.matched > 0
    ? `Apagar fotos com mais de ${OLDER_THAN_DAYS} dias (${preview.matched}, ${formatBytes(preview.freed_bytes)})`
    : `Nenhuma foto com mais de ${OLDER_THAN_DAYS} dias`
})
const confirmLabel = computed(() => state.pending
  ? `Apagar ${state.pending.matched === 1 ? 'imagem' : `${state.pending.matched} imagens`}`
  : 'Apagar')

function onKind(event: Event) {
  void space.setFilters({ kind: (event.target as HTMLSelectElement).value as MediaKind | '' })
}

function onBook(event: Event) {
  const value = Number((event.target as HTMLSelectElement).value)
  void space.setFilters({ bookId: Number.isInteger(value) && value > 0 ? value : null })
}

function onSort(event: Event) {
  void space.setFilters({ sort: (event.target as HTMLSelectElement).value as MediaSort })
}

function openStudy(item: MediaItem) {
  if (item.study && item.book) {
    void router.push({ name: 'study', params: { bookId: item.book.id, studyId: item.study.id } })
  }
}

onMounted(() => { void space.load() })
onBeforeUnmount(() => space.dispose())
</script>

<template>
  <main class="media-space" role="main" aria-labelledby="media-space-title">
    <header class="page-header">
      <h1 id="media-space-title">Minhas Imagens e Espaço</h1>
      <p class="lead">
        Fotos de páginas guardadas para conferência, capas e foto de perfil. Todas ficam cifradas no servidor.
      </p>
    </header>

    <section class="panel usage-panel" aria-label="Uso do espaço">
      <LoadingSkeleton v-if="state.loading && !state.usage" :lines="3" />
      <template v-else-if="state.usage">
        <StorageMeter
          label="Seu espaço"
          :text="userText"
          :level="state.usage.user.level"
          :percent="state.usage.user.percent"
        />
        <StorageMeter
          v-if="server"
          label="Servidor"
          :text="serverText"
          :level="server.level"
          :percent="server.percent ?? null"
        />
      </template>
    </section>

    <p v-if="vaultLocked" class="notice error" role="alert">{{ VAULT_STATE_TEXT[vaultState] }}</p>
    <p v-if="state.error" class="notice error" role="alert">{{ state.error }}</p>
    <p v-if="state.notice" class="notice" role="status">{{ state.notice }}</p>

    <template v-if="!vaultLocked">
      <section class="panel" aria-labelledby="free-heading">
        <h2 id="free-heading">Liberar espaço</h2>
        <p class="muted">Fotos marcadas para manter permanentemente ficam de fora. Os estudos não são alterados.</p>
        <div class="bulk-actions">
          <button
            type="button"
            class="secondary"
            :disabled="!state.previews.completed?.matched"
            @click="space.askBulk('completed')"
          >
            <Icon name="trash" :size="16" aria-hidden="true" /> {{ completedLabel }}
          </button>
          <button
            type="button"
            class="secondary"
            :disabled="!state.previews.older?.matched"
            @click="space.askBulk('older')"
          >
            <Icon name="clock" :size="16" aria-hidden="true" /> {{ olderLabel }}
          </button>
        </div>
      </section>

      <section class="panel" aria-labelledby="images-heading">
        <div class="list-heading">
          <h2 id="images-heading">Imagens</h2>
          <div class="filters">
            <label>
              <span>Tipo</span>
              <select :value="state.kind" @change="onKind">
                <option value="">Todas</option>
                <option value="notebook_page">Páginas digitalizadas</option>
                <option value="cover">Capas</option>
                <option value="avatar">Foto de perfil</option>
              </select>
            </label>
            <label>
              <span>Livro</span>
              <select :value="state.bookId ?? ''" @change="onBook">
                <option value="">Todos</option>
                <option v-for="book in space.books.value" :key="book.id" :value="book.id">{{ book.title }}</option>
              </select>
            </label>
            <label>
              <span>Ordenar</span>
              <select :value="state.sort" @change="onSort">
                <option value="created_desc">Mais recentes</option>
                <option value="size_desc">Maiores</option>
                <option value="expires_asc">Expiram antes</option>
              </select>
            </label>
          </div>
        </div>

        <div v-if="state.loading" class="card-grid" aria-busy="true">
          <LoadingSkeleton v-for="n in 4" :key="n" height="160px" />
        </div>
        <EmptyState
          v-else-if="state.items.length === 0"
          icon="image"
          title="Nenhuma imagem guardada"
          description="Ao digitalizar uma página, marque &quot;Guardar a foto com o estudo&quot; para conferir depois."
          heading-level="h3"
        >
          <RouterLink class="button primary" to="/digitalizar">Digitalizar uma página</RouterLink>
        </EmptyState>
        <div v-else class="card-grid">
          <MediaCard
            v-for="item in state.items"
            :key="item.id"
            :item="item"
            :selected="state.selected.includes(item.id)"
            :busy="state.busyIds.includes(item.id) || state.working"
            @toggle-select="space.toggleSelected(item.id)"
            @view="viewing = item"
            @toggle-keep="space.toggleKeep(item)"
            @open-study="openStudy(item)"
            @delete="space.askSingle(item)"
          />
        </div>
        <button
          v-if="state.nextOffset !== null && !state.loading"
          type="button"
          class="secondary load-more"
          :disabled="state.loadingMore"
          @click="space.loadMore"
        >
          {{ state.loadingMore ? 'Carregando…' : 'Mostrar mais' }}
        </button>
      </section>
    </template>

    <div v-if="state.selected.length > 0" class="selection-bar" role="region" aria-label="Imagens selecionadas">
      <span>{{ state.selected.length }} {{ state.selected.length === 1 ? 'selecionada' : 'selecionadas' }}</span>
      <button type="button" class="secondary" @click="space.clearSelection">Limpar seleção</button>
      <button type="button" class="primary" :disabled="state.working" @click="space.askSelected">
        Apagar selecionadas ({{ state.selected.length }})
      </button>
    </div>

    <div v-if="viewing" class="image-dialog" role="dialog" aria-modal="true" aria-labelledby="image-dialog-title" @keydown.esc="viewing = null">
      <div class="image-dialog-box">
        <header>
          <h2 id="image-dialog-title">{{ viewing.study?.title ?? viewing.book?.title ?? 'Imagem' }}</h2>
          <button ref="closeButton" type="button" class="secondary icon-only" aria-label="Fechar" @click="viewing = null">
            <Icon name="x" :size="18" aria-hidden="true" />
          </button>
        </header>
        <img :src="`/api/media/${viewing.id}/content`" :alt="viewing.study ? `Página digitalizada do estudo ${viewing.study.title}` : 'Imagem guardada'">
      </div>
    </div>

    <TrashConfirmModal
      :open="state.pending !== null"
      :title="state.pending?.title ?? ''"
      :message="state.pending?.message ?? ''"
      :confirm-label="confirmLabel"
      danger
      :loading="state.working"
      @close="space.cancelPending"
      @confirm="space.confirmPending"
    />
  </main>
</template>

<style scoped>
.media-space {
  display: grid;
  gap: 1.25rem;
  max-width: 1100px;
  margin: 0 auto;
  padding-bottom: 6rem;
}

.lead,
.muted {
  color: var(--color-text-secondary);
}

.usage-panel {
  display: grid;
  gap: 1.25rem;
}

.bulk-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.bulk-actions button {
  min-height: 44px;
  white-space: normal;
  text-align: left;
}

.list-heading {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.list-heading h2 {
  margin: 0;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.filters label {
  display: grid;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.filters select {
  min-height: 44px;
  min-width: 10rem;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(340px, 100%), 1fr));
  gap: 1rem;
}

.load-more {
  margin-top: 1rem;
  min-height: 44px;
}

.selection-bar {
  position: sticky;
  bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-panel, 10px);
  background: var(--color-surface);
}

.selection-bar span {
  font-weight: 600;
  margin-right: auto;
}

.selection-bar button {
  min-height: 44px;
}

.image-dialog {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: color-mix(in srgb, var(--color-inverse-bg) 60%, transparent);
}

.image-dialog-box {
  display: grid;
  gap: 0.75rem;
  max-width: min(960px, 100%);
  max-height: 100%;
  padding: 1rem;
  overflow: auto;
  border-radius: var(--radius-panel, 10px);
  background: var(--color-surface);
}

.image-dialog-box header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.image-dialog-box h2 {
  margin: 0;
  font-size: 1.125rem;
  overflow-wrap: anywhere;
}

.image-dialog-box img {
  max-width: 100%;
  height: auto;
}

.icon-only {
  min-width: 44px;
  min-height: 44px;
  padding: 0;
}

.media-space button:focus-visible,
.media-space select:focus-visible,
.media-space a:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

@media (max-width: 640px) {
  .card-grid {
    grid-template-columns: 1fr;
  }

  .selection-bar {
    position: fixed;
    left: 0.75rem;
    right: 0.75rem;
    bottom: calc(var(--mobile-nav-offset, 0px) + 0.75rem);
    z-index: 20;
  }

  .filters,
  .filters label,
  .filters select {
    width: 100%;
  }
}
</style>
