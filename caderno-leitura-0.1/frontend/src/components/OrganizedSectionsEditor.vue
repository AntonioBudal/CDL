<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { ORGANIZE_SECTIONS, type OrganizeSection } from '../types/organize'
import type { OrganizedSections } from '../composables/useSectionOrganizer'

// Os 4 editores da organização (feature 089): empilhados no desktop, abas abaixo de 768 px.

const props = defineProps<{ idPrefix: string; reviewCounts: Record<OrganizeSection, number>; disabled?: boolean }>()
const sections = defineModel<OrganizedSections>('sections', { required: true })

const compact = ref(false)
const active = ref<OrganizeSection>('summary')
const tabs = ref<HTMLButtonElement[]>([])
let query: MediaQueryList | null = null

function syncCompact() {
  compact.value = query?.matches ?? false
}

function update(key: OrganizeSection, value: string) {
  sections.value = { ...sections.value, [key]: value }
}

async function focusTab(index: number) {
  const count = ORGANIZE_SECTIONS.length
  const next = (index + count) % count
  active.value = ORGANIZE_SECTIONS[next]!.key
  await nextTick()
  tabs.value[next]?.focus()
}

function onTabKey(event: KeyboardEvent, index: number) {
  if (event.key === 'ArrowRight') { event.preventDefault(); void focusTab(index + 1) }
  else if (event.key === 'ArrowLeft') { event.preventDefault(); void focusTab(index - 1) }
  else if (event.key === 'Home') { event.preventDefault(); void focusTab(0) }
  else if (event.key === 'End') { event.preventDefault(); void focusTab(ORGANIZE_SECTIONS.length - 1) }
}

/** Mostra a seção pedida (no celular, troca de aba) e devolve o editor dela. */
async function reveal(key: OrganizeSection): Promise<HTMLTextAreaElement | null> {
  active.value = key
  await nextTick()
  return document.getElementById(`${props.idPrefix}-${key}`) as HTMLTextAreaElement | null
}

defineExpose({ reveal })

onMounted(() => {
  if (typeof window === 'undefined' || !window.matchMedia) return
  query = window.matchMedia('(max-width: 767px)')
  syncCompact()
  query.addEventListener('change', syncCompact)
})
onBeforeUnmount(() => query?.removeEventListener('change', syncCompact))
</script>

<template>
  <div class="organized-editor">
    <div v-if="compact" class="organized-tabs" role="tablist" aria-label="Seções do estudo">
      <button
        v-for="(item, index) in ORGANIZE_SECTIONS"
        :id="`${idPrefix}-tab-${item.key}`"
        :key="item.key"
        ref="tabs"
        type="button"
        role="tab"
        class="organized-tab"
        :aria-selected="active === item.key"
        :aria-controls="`${idPrefix}-panel-${item.key}`"
        :tabindex="active === item.key ? 0 : -1"
        @click="active = item.key"
        @keydown="onTabKey($event, index)"
      >
        <span>{{ item.label }}</span>
        <span v-if="reviewCounts[item.key]" class="tab-count">
          {{ reviewCounts[item.key] }}<span class="sr-only"> para conferir</span>
        </span>
      </button>
    </div>

    <div
      v-for="item in ORGANIZE_SECTIONS"
      v-show="!compact || active === item.key"
      :id="`${idPrefix}-panel-${item.key}`"
      :key="item.key"
      class="organized-panel"
      :role="compact ? 'tabpanel' : undefined"
      :aria-labelledby="compact ? `${idPrefix}-tab-${item.key}` : undefined"
    >
      <label class="organized-label" :for="`${idPrefix}-${item.key}`">
        {{ item.label }}
        <span v-if="reviewCounts[item.key]" class="label-count">{{ reviewCounts[item.key] }} para conferir</span>
      </label>
      <textarea
        :id="`${idPrefix}-${item.key}`"
        :value="sections[item.key]"
        :disabled="disabled"
        :rows="sections[item.key] ? 6 : 3"
        spellcheck="true"
        @input="update(item.key, ($event.target as HTMLTextAreaElement).value)"
      />
    </div>
  </div>
</template>

<style scoped>
.organized-editor {
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 1);
}

.organized-tabs {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: calc(var(--space-unit) * 0.4);
}

.organized-tab {
  min-height: 44px;
  justify-content: center;
  background: var(--color-surface);
  color: var(--color-text);
  border: var(--border-width) solid var(--color-border-strong);
  white-space: normal;
}

.organized-tab[aria-selected='true'] {
  background: var(--color-selected-bg);
  color: var(--color-selected-text);
  border-color: var(--color-accent);
}

.organized-tab:hover:not([aria-selected='true']) {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.organized-tab:focus-visible,
.organized-panel textarea:focus-visible {
  outline: var(--focus-width, 2px) solid var(--color-accent);
  outline-offset: var(--focus-offset, 2px);
}

.tab-count,
.label-count {
  display: inline-flex;
  align-items: center;
  border-radius: var(--radius-button);
  background: var(--color-warning-bg);
  color: var(--color-warning-text);
  border: var(--border-width) solid var(--color-warning-border);
  font-size: 0.8125rem;
  font-weight: 650;
  padding: 0 calc(var(--space-unit) * 0.4);
}

.organized-label {
  display: flex;
  align-items: center;
  gap: calc(var(--space-unit) * 0.5);
  font-weight: 650;
  margin-bottom: calc(var(--space-unit) * 0.4);
}

.organized-panel textarea {
  min-height: 6rem;
  resize: vertical;
  line-height: 1.6;
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
  border: 0;
}

@media (prefers-reduced-motion: reduce) {
  .organized-editor * {
    transition: none !important;
  }
}
</style>
