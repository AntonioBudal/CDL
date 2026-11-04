<script setup lang="ts">
import { ref, watch } from 'vue'
import Drawer from '../ui/Drawer.vue'
import MarkdownContent from '../MarkdownContent.vue'
import { api } from '../../services/api'
import type { Study } from '../../types.ts'

// Gaveta de contexto da revisão (F0.10.04): as quatro partes do estudo de origem do cartão, abertas só depois de
// revelar a resposta, para não estragar a recuperação ativa.
const props = defineProps<{
  open: boolean
  studyId: number
  studyTitle: string
}>()

const emit = defineEmits<{ (e: 'close'): void }>()

const SECTIONS: { key: 'summary' | 'explanation' | 'concepts' | 'references'; label: string }[] = [
  { key: 'summary', label: 'Resumo' },
  { key: 'explanation', label: 'Explicação' },
  { key: 'concepts', label: 'Conceitos' },
  { key: 'references', label: 'Referências' },
]

const study = ref<Study | null>(null)
const loading = ref(false)
const unavailable = ref(false)
let loadedId: number | null = null

watch(
  () => [props.open, props.studyId] as const,
  async ([isOpen, id]) => {
    if (!isOpen || id === loadedId) return
    loading.value = true
    unavailable.value = false
    try {
      study.value = await api.getStudy(id)
      loadedId = id
    } catch {
      study.value = null
      unavailable.value = true
    } finally {
      loading.value = false
    }
  },
  { immediate: true },
)
</script>

<template>
  <Drawer :open="open" :title="study?.title || studyTitle" description="O estudo de onde veio este cartão." width="560px" @close="emit('close')">
    <p v-if="loading" class="muted" role="status">Carregando o estudo…</p>
    <p v-else-if="unavailable" class="notice error" role="alert">Este estudo não está mais disponível.</p>
    <div v-else-if="study" class="context-sections">
      <section v-for="section in SECTIONS" :key="section.key" class="context-section" :aria-labelledby="`ctx-${section.key}`">
        <h3 :id="`ctx-${section.key}`" class="context-section-title">{{ section.label }}</h3>
        <MarkdownContent v-if="study[section.key]?.trim()" :content="study[section.key]" />
        <p v-else class="muted">Sem anotações nesta parte.</p>
      </section>
    </div>
  </Drawer>
</template>

<style scoped>
.context-sections {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.context-section-title {
  margin: 0 0 0.4rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--color-link);
}

.context-section :deep(p) {
  margin: 0 0 0.5rem;
  line-height: 1.6;
}
</style>
