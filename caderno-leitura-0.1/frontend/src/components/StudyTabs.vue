<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { SECTION_LABELS, type AnalysisSections, type StudySectionKey, type StudyHighlight } from '../types'
import MarkdownContent from './MarkdownContent.vue'
import type { HighlightClickEvent } from '../utils/highlightRenderer'

const props = withDefaults(
  defineProps<{
    sections: AnalysisSections
    idPrefix: string
    highlights?: StudyHighlight[]
  }>(),
  {
    highlights: () => [],
  }
)

const emit = defineEmits<{
  (e: 'highlight-click', event: HighlightClickEvent): void
  (e: 'active-section-change', sectionKey: StudySectionKey): void
}>()

const active = ref(0)
const tabList = ref<HTMLElement | null>(null)
const activePanelEl = ref<HTMLElement | null>(null)

const activeSectionKey = computed<StudySectionKey>(() => SECTION_LABELS[active.value].key)

watch(activeSectionKey, (key) => {
  emit('active-section-change', key)
}, { immediate: true })

async function onKeydown(event: KeyboardEvent, index: number) {
  const last = SECTION_LABELS.length - 1
  const next = event.key === 'ArrowRight' ? (index + 1) % SECTION_LABELS.length
    : event.key === 'ArrowLeft' ? (index + last) % SECTION_LABELS.length
    : event.key === 'Home' ? 0 : event.key === 'End' ? last : null
  if (next === null) return
  event.preventDefault()
  active.value = next
  await nextTick()
  tabList.value?.querySelectorAll<HTMLButtonElement>('[role="tab"]')[next]?.focus()
}

defineExpose({
  activeSectionKey,
  activePanelEl,
})
</script>

<template>
  <section class="reader-analysis" aria-label="Análise do estudo">
    <div ref="tabList" class="study-tabs" role="tablist" aria-label="Seções da análise" aria-orientation="horizontal">
      <button v-for="(section, index) in SECTION_LABELS" :id="`${idPrefix}-tab-${section.key}`" :key="section.key"
        type="button" role="tab" :aria-selected="active === index" :tabindex="active === index ? 0 : -1"
        :aria-controls="`${idPrefix}-panel-${section.key}`" @click="active = index" @keydown="onKeydown($event, index)">
        {{ section.label }}
      </button>
    </div>
    <div
      v-for="(section, index) in SECTION_LABELS"
      :id="`${idPrefix}-panel-${section.key}`"
      :key="section.key"
      :ref="(el) => { if (active === index) activePanelEl = el as HTMLElement }"
      role="tabpanel"
      :aria-labelledby="`${idPrefix}-tab-${section.key}`"
      :hidden="active !== index"
      tabindex="0"
      class="study-panel"
    >
      <MarkdownContent
        v-if="sections[section.key].trim()"
        :content="sections[section.key]"
        :highlights="highlights.filter((h) => h.section === section.key)"
        @highlight-click="(event) => emit('highlight-click', event)"
      />
      <p v-else class="section-empty">Esta seção ainda está vazia. Use “Editar estudo” para preenchê-la.</p>
    </div>
  </section>
</template>
