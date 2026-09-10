<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { SECTION_LABELS, type AnalysisSections } from '../types'
import MarkdownContent from './MarkdownContent.vue'
defineProps<{ sections: AnalysisSections; idPrefix: string }>()
const active = ref(0)
const tabList = ref<HTMLElement | null>(null)
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
    <div v-for="(section, index) in SECTION_LABELS" :id="`${idPrefix}-panel-${section.key}`" :key="section.key"
      role="tabpanel" :aria-labelledby="`${idPrefix}-tab-${section.key}`" :hidden="active !== index" tabindex="0" class="study-panel">
      <MarkdownContent v-if="sections[section.key].trim()" :content="sections[section.key]" />
      <p v-else class="section-empty">Esta seção ainda está vazia. Use “Editar estudo” para preenchê-la.</p>
    </div>
  </section>
</template>
