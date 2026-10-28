<script setup lang="ts">
import { computed, ref } from 'vue'
import Icon from '../ui/Icon.vue'
import { MEDIA_KIND_LABELS, type MediaItem } from '../../types/media'
import { formatBytes, shortDate, validityText } from '../../utils/mediaFormat'

const props = defineProps<{
  item: MediaItem
  selected: boolean
  busy?: boolean
}>()

const emit = defineEmits<{
  (event: 'toggle-select'): void
  (event: 'view'): void
  (event: 'toggle-keep'): void
  (event: 'open-study'): void
  (event: 'delete'): void
}>()

const broken = ref(false)
const unavailable = computed(() => props.item.status === 'missing' || broken.value)
const isPage = computed(() => props.item.kind === 'notebook_page')
const studyText = computed(() => {
  if (!isPage.value) return ''
  if (!props.item.study) return 'Estudo apagado'
  return props.item.study.in_trash ? `${props.item.study.title} (estudo na lixeira)` : props.item.study.title
})
const title = computed(() => {
  if (props.item.kind === 'avatar') return MEDIA_KIND_LABELS.avatar
  return props.item.book?.title ?? MEDIA_KIND_LABELS[props.item.kind]
})
const alt = computed(() => isPage.value
  ? `Página digitalizada do estudo ${props.item.study?.title ?? 'apagado'}`
  : props.item.kind === 'cover' ? `Capa do livro ${props.item.book?.title ?? ''}`.trim() : 'Sua foto de perfil')
const checkboxId = computed(() => `media-select-${props.item.id}`)
</script>

<template>
  <article class="media-card" :class="{ selected }" :aria-labelledby="`${checkboxId}-title`">
    <div class="media-thumb">
      <div v-if="unavailable" class="thumb-unavailable">
        <Icon name="alert-triangle" :size="22" aria-hidden="true" />
        <span>Arquivo indisponível</span>
      </div>
      <img
        v-else
        :src="`/api/media/${item.id}/thumbnail`"
        :alt="alt"
        loading="lazy"
        decoding="async"
        @error="broken = true"
      >
    </div>
    <div class="media-body">
      <div class="media-top">
        <input
          v-if="isPage"
          :id="checkboxId"
          type="checkbox"
          class="media-check"
          :checked="selected"
          :aria-label="`Selecionar ${alt}`"
          @change="emit('toggle-select')"
        >
        <div>
          <h3 :id="`${checkboxId}-title`" class="media-title">{{ title }}</h3>
          <p class="media-kind">{{ MEDIA_KIND_LABELS[item.kind] }}<template v-if="studyText"> · {{ studyText }}</template></p>
        </div>
      </div>
      <p class="media-meta">
        {{ shortDate(item.created_at) }} · <span :class="{ 'keeps': item.keep_forever }">{{ validityText(item) }}</span>
        · {{ formatBytes(item.byte_size) }}
      </p>
      <div class="media-actions">
        <button v-if="!unavailable" type="button" class="secondary small" @click="emit('view')">
          <Icon name="eye" :size="16" aria-hidden="true" /> Ver
        </button>
        <button
          v-if="isPage && !unavailable"
          type="button"
          class="secondary small"
          :aria-pressed="item.keep_forever"
          :disabled="busy"
          @click="emit('toggle-keep')"
        >
          <Icon :name="item.keep_forever ? 'lock' : 'unlock'" :size="16" aria-hidden="true" />
          Manter permanentemente
        </button>
        <button v-if="isPage && item.study && !item.study.in_trash" type="button" class="secondary small" @click="emit('open-study')">
          <Icon name="book-open" :size="16" aria-hidden="true" /> Abrir o estudo
        </button>
        <button type="button" class="secondary small danger-text" :disabled="busy" @click="emit('delete')">
          <Icon name="trash" :size="16" aria-hidden="true" /> Apagar
        </button>
      </div>
    </div>
  </article>
</template>

<style scoped>
.media-card {
  display: grid;
  grid-template-columns: 112px 1fr;
  gap: 1rem;
  padding: 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card, 8px);
  background: var(--color-surface);
}

.media-card.selected {
  border-color: var(--color-accent);
  box-shadow: inset 0 0 0 1px var(--color-accent);
}

.media-thumb {
  width: 112px;
  height: 140px;
  border-radius: 6px;
  overflow: hidden;
  background: var(--color-surface-inset);
  display: flex;
  align-items: center;
  justify-content: center;
}

.media-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-unavailable {
  display: grid;
  justify-items: center;
  gap: 0.35rem;
  padding: 0.5rem;
  text-align: center;
  font-size: 0.8125rem;
  color: var(--color-warning-text);
}

.media-body {
  display: grid;
  gap: 0.5rem;
  align-content: start;
  min-width: 0;
}

.media-top {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.media-check {
  width: 22px;
  height: 22px;
  margin: 0.15rem 0 0;
  flex-shrink: 0;
  accent-color: var(--color-accent);
}

.media-title {
  margin: 0;
  font-size: 1rem;
  overflow-wrap: anywhere;
}

.media-kind,
.media-meta {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  overflow-wrap: anywhere;
}

.keeps {
  font-weight: 600;
  color: var(--color-text);
}

.media-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.media-actions button {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.media-actions .danger-text {
  color: var(--color-error-text);
  border-color: var(--color-error-border);
}

.media-actions button[aria-pressed='true'] {
  border-color: var(--color-accent);
  color: var(--color-accent-hover-text, var(--color-accent));
}

.media-actions button:focus-visible,
.media-check:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

@media (max-width: 480px) {
  .media-card {
    grid-template-columns: 1fr;
  }

  .media-thumb {
    width: 100%;
    height: 180px;
  }

  .media-actions button {
    flex: 1 1 calc(50% - 0.25rem);
    justify-content: center;
  }
}
</style>
