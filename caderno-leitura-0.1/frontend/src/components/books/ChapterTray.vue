<script setup lang="ts">
import { uiLocale } from '../../i18n/format.ts'
/**
 * F0.11.02 (spec 104): bandeja do capítulo — capturas pendentes (status "inbox") do capítulo escolhido, com
 * "Virar estudo" (Importar com a captura), "Arquivar" e "Abrir na caixa de entrada".
 */
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { api, errorMessage } from '../../services/api'
import { useQuickCapture } from '../../composables/useQuickCapture'
import type { InboxCapture } from '../../types'

const props = defineProps<{
  bookId: number
  chapterId: number
  /** Muda quando algo fora da bandeja criou ou mudou capturas (ex.: captura rápida). */
  refreshKey?: number
}>()

const emit = defineEmits<{ (e: 'changed'): void }>()

const quickCapture = useQuickCapture()
const items = ref<InboxCapture[]>([])
const loading = ref(false)
const loadError = ref('')
const actionError = ref('')
const archivingId = ref<number | null>(null)
const expanded = ref<Set<number>>(new Set())
const open = ref(true)
const liveMessage = ref('')
let request: AbortController | null = null

async function load() {
  request?.abort()
  const controller = new AbortController()
  request = controller
  loading.value = true
  loadError.value = ''
  try {
    const list = await api.getInboxCaptures({ status: 'inbox', chapter_id: props.chapterId, limit: 100 }, controller.signal)
    if (controller.signal.aborted) return
    items.value = list
    open.value = list.length > 0
  } catch (error) {
    if (!controller.signal.aborted) loadError.value = errorMessage(error)
  } finally {
    if (!controller.signal.aborted) loading.value = false
  }
}

watch(() => [props.chapterId, props.refreshKey], () => void load(), { immediate: true })
onBeforeUnmount(() => request?.abort())

const countLabel = computed(() => (items.value.length === 1 ? '1 captura' : `${items.value.length} capturas`))

function promoteLink(capture: InboxCapture) {
  return {
    path: '/importar',
    query: { promote_inbox_id: String(capture.id), book: String(props.bookId), chapter: String(props.chapterId) },
  }
}

async function archive(capture: InboxCapture) {
  if (archivingId.value) return
  archivingId.value = capture.id
  actionError.value = ''
  try {
    await api.updateInboxCapture(capture.id, { status: 'archived' })
    items.value = items.value.filter((item) => item.id !== capture.id)
    liveMessage.value = 'Captura arquivada.'
    emit('changed')
  } catch (error) {
    actionError.value = errorMessage(error)
  } finally {
    archivingId.value = null
  }
}

function toggleExpand(id: number) {
  const next = new Set(expanded.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  expanded.value = next
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(uiLocale(), { day: '2-digit', month: 'short', year: 'numeric' })
  } catch {
    return ''
  }
}

function captureHere() {
  quickCapture.open({ bookId: props.bookId, chapterId: props.chapterId })
}
</script>

<template>
  <section class="chapter-tray" aria-labelledby="chapter-tray-heading">
    <div class="chapter-tray-head">
      <button
        type="button"
        class="quiet chapter-tray-toggle"
        :aria-expanded="open"
        aria-controls="chapter-tray-body"
        @click="open = !open"
      >
        <span id="chapter-tray-heading" class="chapter-tray-title">Bandeja do capítulo</span>
        <span class="chapter-tray-count">{{ loading ? '…' : countLabel }}</span>
      </button>
      <button type="button" class="quiet chapter-tray-capture" @click="captureHere">Capturar neste capítulo</button>
    </div>

    <div v-show="open" id="chapter-tray-body" class="chapter-tray-body">
      <p v-if="loadError" class="chapter-tray-error" role="alert">
        {{ loadError }}
        <button type="button" class="quiet chapter-tray-retry" @click="load">Tentar novamente</button>
      </p>
      <p v-else-if="!loading && items.length === 0" class="chapter-tray-muted">
        Nada na bandeja. Ideias capturadas neste capítulo aparecem aqui até virarem estudo.
      </p>
      <ul v-else class="chapter-tray-list">
        <li v-for="capture in items" :key="capture.id" class="chapter-tray-item">
          <p class="chapter-tray-text" :class="{ 'is-clamped': !expanded.has(capture.id) }">{{ capture.content }}</p>
          <button
            v-if="capture.content.length > 180"
            type="button"
            class="quiet chapter-tray-more"
            :aria-expanded="expanded.has(capture.id)"
            @click="toggleExpand(capture.id)"
          >
            {{ expanded.has(capture.id) ? 'Ver menos' : 'Ver tudo' }}
          </button>
          <p class="chapter-tray-meta">
            <span v-if="capture.source_hint">{{ capture.source_hint }} · </span>{{ formatDate(capture.created_at) }}
          </p>
          <div class="chapter-tray-actions">
            <RouterLink :to="promoteLink(capture)" class="button primary chapter-tray-action">Virar estudo</RouterLink>
            <button
              type="button"
              class="quiet chapter-tray-action"
              :disabled="archivingId === capture.id"
              @click="archive(capture)"
            >
              {{ archivingId === capture.id ? 'Arquivando…' : 'Arquivar' }}
            </button>
            <RouterLink :to="{ path: '/inbox', query: { livro: String(bookId) } }" class="chapter-tray-link">
              Abrir na caixa de entrada
            </RouterLink>
          </div>
        </li>
      </ul>
      <p v-if="actionError" class="chapter-tray-error" role="alert">{{ actionError }}</p>
    </div>
    <span class="visually-hidden" role="status" aria-live="polite">{{ liveMessage }}</span>
  </section>
</template>

<style scoped>
.chapter-tray {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 0 0 1rem;
  padding: 0.75rem 1rem;
  border: 1px dashed var(--color-border-strong, var(--color-border));
  border-radius: 10px;
  background: var(--color-surface);
  min-width: 0;
}

.chapter-tray-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.chapter-tray-toggle {
  display: inline-flex;
  align-items: baseline;
  gap: 0.5rem;
  min-height: 44px;
  padding: 0 0.25rem;
}

.chapter-tray-title {
  font-weight: 700;
  color: var(--color-text);
}

.chapter-tray-count {
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.chapter-tray-capture,
.chapter-tray-retry {
  --quiet-border: var(--color-border-strong, var(--color-border));
  min-height: 44px;
  font-size: 0.875rem;
}

.chapter-tray-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.chapter-tray-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chapter-tray-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  min-width: 0;
}

.chapter-tray-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.chapter-tray-text {
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  line-height: 1.5;
  color: var(--color-text);
}

.chapter-tray-text.is-clamped {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  /* Uma regra global troca o display de <p>; a altura máxima garante as 3 linhas mesmo assim. */
  max-height: calc(1.5em * 3);
}

.chapter-tray-more {
  align-self: flex-start;
  min-height: 44px;
  --quiet-fg: var(--color-link, var(--color-text));
}

.chapter-tray-meta,
.chapter-tray-muted {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.chapter-tray-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
}

.chapter-tray-action {
  min-height: 44px;
  font-size: 0.875rem;
}

.chapter-tray-action.quiet {
  --quiet-border: var(--color-border-strong, var(--color-border));
}

.chapter-tray-link {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  font-size: 0.875rem;
  color: var(--color-link);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.chapter-tray-error {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-danger-text, var(--color-error-text, var(--color-text)));
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
