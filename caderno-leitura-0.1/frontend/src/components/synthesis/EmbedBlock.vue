<script setup lang="ts">
/** F0.11.11 (spec 113): um trecho transcluído, com o conteúdo atual da origem. */
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import MarkdownContent from '../MarkdownContent.vue'
import type { EmbedResolved } from '../../types'

const props = defineProps<{ item: EmbedResolved | null; pending?: boolean }>()

const origin = computed(() => {
  const item = props.item
  if (!item) return ''
  return [item.book_title, item.chapter_name, item.title, item.section_label].filter(Boolean).join(' · ')
})
const kindLabel = computed(() => {
  switch (props.item?.kind) {
    case 'highlight': return 'Destaque'
    case 'section': return 'Seção'
    default: return 'Estudo'
  }
})
</script>

<template>
  <figure class="embed-block" :class="{ 'is-unavailable': item && !item.available }">
    <template v-if="pending || !item">
      <p class="embed-muted">Carregando o trecho…</p>
    </template>
    <template v-else-if="!item.available">
      <p class="embed-muted">{{ item.markdown }}</p>
    </template>
    <template v-else>
      <figcaption class="embed-origin">
        <span class="embed-kind">{{ kindLabel }}</span>
        <span>{{ origin }}</span>
      </figcaption>
      <blockquote v-if="item.kind === 'highlight'" class="embed-quote">{{ item.markdown }}</blockquote>
      <MarkdownContent v-else :content="item.markdown || '*Seção vazia no estudo.*'" />
      <p v-if="item.note" class="embed-note"><strong>Nota:</strong> {{ item.note }}</p>
      <RouterLink
        v-if="item.study_id && item.book_id"
        :to="`/livros/${item.book_id}/estudos/${item.study_id}`"
        class="embed-link"
      >
        Abrir no estudo
      </RouterLink>
    </template>
  </figure>
</template>

<style scoped>
.embed-block {
  margin: 12px 0;
  padding: 12px 14px;
  border: 1px solid var(--color-border);
  border-left: 4px solid var(--color-border-strong);
  border-radius: 6px;
  background: var(--color-surface);
  color: var(--color-text);
  min-width: 0;
  overflow-wrap: anywhere;
}
.embed-block.is-unavailable {
  border-left-color: var(--color-warning-border);
}
.embed-origin {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 8px;
  align-items: center;
  font-size: 0.85rem;
  color: var(--color-muted);
  margin-bottom: 6px;
}
.embed-kind {
  font-weight: 600;
  padding: 0 8px;
  border-radius: 999px;
  background: var(--color-selected-bg);
  color: var(--color-selected-text);
}
.embed-quote {
  margin: 0;
  font-family: var(--font-serif, Georgia, serif);
  font-size: 1.05rem;
  line-height: 1.5;
}
.embed-note,
.embed-muted {
  color: var(--color-muted);
  margin: 6px 0 0;
}
.embed-link {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  color: var(--color-link);
}
</style>
