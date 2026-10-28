<script setup lang="ts">
import { computed, ref } from 'vue'
import Icon from '../ui/Icon.vue'
import TrashConfirmModal from '../TrashConfirmModal.vue'
import type { useOriginalPage } from '../../composables/useOriginalPage'
import { validityText } from '../../utils/mediaFormat'

// Foto de conferência ao lado do texto do estudo (feature 090-C). A imagem vem decifrada e sem cache.
const props = defineProps<{
  viewer: ReturnType<typeof useOriginalPage>
  studyTitle: string
}>()

const emit = defineEmits<{ (event: 'close'): void }>()

const state = props.viewer.state
const current = props.viewer.current
const confirmOpen = ref(false)
const stage = ref<HTMLElement | null>(null)
let drag: { x: number; y: number; left: number; top: number } | null = null

const validity = computed(() => {
  if (!current.value) return ''
  const text = validityText(current.value)
  return text.startsWith('expira') ? `Apagada automaticamente: ${text}` : text
})

function onKey(event: KeyboardEvent) {
  if (event.target instanceof HTMLInputElement) return
  if (event.key === 'Escape') {
    emit('close')
    return
  }
  if (props.viewer.handleKey(event.key)) event.preventDefault()
}

function startDrag(event: PointerEvent) {
  if (state.fit || !stage.value) return
  drag = { x: event.clientX, y: event.clientY, left: stage.value.scrollLeft, top: stage.value.scrollTop }
  stage.value.setPointerCapture(event.pointerId)
}

function moveDrag(event: PointerEvent) {
  if (!drag || !stage.value) return
  stage.value.scrollLeft = drag.left - (event.clientX - drag.x)
  stage.value.scrollTop = drag.top - (event.clientY - drag.y)
}

function endDrag() {
  drag = null
}

async function confirmRemove() {
  if (await props.viewer.removeCurrent()) confirmOpen.value = false
}
</script>

<template>
  <section class="original-page" aria-labelledby="original-page-title" @keydown="onKey">
    <header class="viewer-header">
      <h2 id="original-page-title">Folha original</h2>
      <button type="button" class="secondary icon-only" aria-label="Fechar a folha original" @click="emit('close')">
        <Icon name="x" :size="18" aria-hidden="true" />
      </button>
    </header>

    <p v-if="state.loading" class="muted" role="status">Carregando a foto…</p>
    <p v-else-if="state.error" class="notice error" role="alert">{{ state.error }}</p>
    <p v-else-if="!current" class="muted">Nenhuma foto guardada com este estudo.</p>

    <template v-if="current">
      <div class="viewer-toolbar" role="toolbar" aria-label="Zoom da folha original">
        <button type="button" class="secondary icon-only" aria-label="Diminuir o zoom" @click="viewer.zoomOut">
          <Icon name="minus" :size="18" aria-hidden="true" />
        </button>
        <span class="zoom-value" aria-live="polite">{{ state.fit ? 'Ajustada à largura' : `${viewer.zoomPercent.value}%` }}</span>
        <button type="button" class="secondary icon-only" aria-label="Aumentar o zoom" @click="viewer.zoomIn">
          <Icon name="plus" :size="18" aria-hidden="true" />
        </button>
        <button type="button" class="secondary" @click="viewer.resetView">Ajustar à largura</button>
        <template v-if="viewer.count.value > 1">
          <button type="button" class="secondary icon-only" aria-label="Foto anterior" @click="viewer.go(-1)">
            <Icon name="chevron-left" :size="18" aria-hidden="true" />
          </button>
          <span>{{ state.index + 1 }} de {{ viewer.count.value }}</span>
          <button type="button" class="secondary icon-only" aria-label="Próxima foto" @click="viewer.go(1)">
            <Icon name="chevron-right" :size="18" aria-hidden="true" />
          </button>
        </template>
      </div>

      <div
        ref="stage"
        class="viewer-stage"
        :class="{ zoomed: !state.fit }"
        tabindex="0"
        aria-label="Foto da página; use + e − para o zoom e 0 para ajustar"
        @pointerdown="startDrag"
        @pointermove="moveDrag"
        @pointerup="endDrag"
        @pointercancel="endDrag"
      >
        <p v-if="current.status === 'missing'" class="notice error">O arquivo desta foto não foi encontrado no cofre.</p>
        <img
          v-else
          :key="current.id"
          :src="`/api/media/${current.id}/content`"
          :alt="`Folha original do estudo ${studyTitle}`"
          :style="state.fit ? undefined : { width: `${state.zoom * 100}%` }"
          draggable="false"
        >
      </div>

      <footer class="viewer-footer">
        <p class="validity">{{ validity }}</p>
        <div class="footer-actions">
          <button
            type="button"
            class="secondary"
            :aria-pressed="current.keep_forever"
            :disabled="state.working"
            @click="viewer.toggleKeep"
          >
            <Icon :name="current.keep_forever ? 'lock' : 'unlock'" :size="16" aria-hidden="true" />
            Manter permanentemente
          </button>
          <button type="button" class="secondary danger-text" :disabled="state.working" @click="confirmOpen = true">
            <Icon name="trash" :size="16" aria-hidden="true" /> Apagar foto
          </button>
        </div>
      </footer>
    </template>

    <TrashConfirmModal
      :open="confirmOpen"
      title="Apagar esta foto?"
      message="A foto da página será apagada. O estudo e seus textos não serão alterados."
      confirm-label="Apagar foto"
      danger
      :loading="state.working"
      @close="confirmOpen = false"
      @confirm="confirmRemove"
    />
  </section>
</template>

<style scoped>
.original-page {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  height: 100%;
  min-height: 0;
}

.viewer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.viewer-header h2 {
  margin: 0;
  font-size: 1.125rem;
}

.viewer-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.icon-only {
  min-width: 44px;
  min-height: 44px;
  padding: 0;
}

.zoom-value {
  min-width: 9ch;
  text-align: center;
  color: var(--color-text-secondary);
}

.viewer-stage {
  flex: 1;
  min-height: 320px;
  overflow: auto;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface-inset);
  touch-action: pan-x pan-y;
}

.viewer-stage.zoomed {
  cursor: grab;
}

.viewer-stage img {
  display: block;
  width: 100%;
  height: auto;
  max-width: none;
  user-select: none;
}

.viewer-footer {
  display: grid;
  gap: 0.5rem;
}

.validity {
  margin: 0;
  color: var(--color-text-secondary);
}

.footer-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.footer-actions button {
  min-height: 44px;
}

.footer-actions button[aria-pressed='true'] {
  border-color: var(--color-accent);
}

.danger-text {
  color: var(--color-error-text);
  border-color: var(--color-error-border);
}

.viewer-stage:focus-visible,
.original-page button:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.muted {
  color: var(--color-text-secondary);
}
</style>
