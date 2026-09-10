<script setup lang="ts">
import { SECTION_LABELS, type AnalysisSections } from '../types'
defineProps<{ idPrefix: string; showMetadata?: boolean }>()
const title = defineModel<string>('title', { required: true })
const location = defineModel<string>('location', { required: true })
const notes = defineModel<string>('notes', { required: true })
const sections = defineModel<AnalysisSections>('sections', { required: true })
function updateSection(key: keyof AnalysisSections, event: Event) {
  sections.value = { ...sections.value, [key]: (event.target as HTMLTextAreaElement).value }
}
</script>

<template>
  <div v-if="showMetadata" class="form-grid">
    <div class="field"><label :for="`${idPrefix}-title`">Título do estudo</label><input :id="`${idPrefix}-title`" v-model="title" required /></div>
    <div class="field"><label :for="`${idPrefix}-location`">Página ou localização <span class="optional">opcional</span></label><input :id="`${idPrefix}-location`" v-model="location" placeholder="Ex.: p. 32–34 ou Loc. 1820" /></div>
  </div>
  <p :id="`${idPrefix}-format-hint`" class="field-hint">Nas seções, use Markdown para parágrafos, listas, **negrito**, *itálico* e [links](https://exemplo.com).</p>
  <div class="analysis-grid">
    <div v-for="section in SECTION_LABELS" :key="section.key" class="field">
      <label :for="`${idPrefix}-${section.key}`">{{ section.label }}</label>
      <textarea :id="`${idPrefix}-${section.key}`" :value="sections[section.key]" rows="9"
        :aria-describedby="`${idPrefix}-format-hint`" :placeholder="`${section.label}: revise ou complete o conteúdo.`"
        @input="updateSection(section.key, $event)"></textarea>
    </div>
  </div>
  <div class="field notes-field">
    <label :for="`${idPrefix}-notes`">Minhas anotações e interpretações <span class="optional">opcional</span></label>
    <textarea :id="`${idPrefix}-notes`" v-model="notes" rows="5" placeholder="Suas reflexões sobre esta passagem…"></textarea>
  </div>
</template>
