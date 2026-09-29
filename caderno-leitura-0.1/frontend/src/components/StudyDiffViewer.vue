<script setup lang="ts">
import type { SectionDiff, StudyDiffResult } from '../types.ts'

const props = defineProps<{
  diff: StudyDiffResult
}>()

interface SectionMeta {
  key: keyof StudyDiffResult['sections']
  label: string
}

const SECTION_DEFS: SectionMeta[] = [
  { key: 'title', label: 'Título' },
  { key: 'summary', label: 'Resumo' },
  { key: 'explanation', label: 'Argumentos' },
  { key: 'concepts', label: 'Conceitos' },
  { key: 'references', label: 'Citações e Referências' },
  { key: 'notes', label: 'Anotações' },
]

function getStatusBadge(status: SectionDiff['status']) {
  switch (status) {
    case 'modified':
      return { text: 'Modificada', class: 'badge-modified' }
    case 'added':
      return { text: 'Adicionada', class: 'badge-added' }
    case 'removed':
      return { text: 'Removida', class: 'badge-removed' }
    case 'unchanged':
    default:
      return { text: 'Inalterada', class: 'badge-unchanged' }
  }
}
</script>

<template>
  <div class="diff-viewer" role="region" aria-label="Visualização de diferenças entre versões">
    <div class="diff-legend" aria-hidden="true">
      <span class="legend-item"><ins class="diff-sample insert"></ins> Trecho adicionado</span>
      <span class="legend-item"><del class="diff-sample delete"></del> Trecho removido</span>
      <span class="legend-item"><span class="diff-sample unchanged"></span> Inalterado</span>
    </div>

    <div class="diff-sections">
      <section
        v-for="sec in SECTION_DEFS"
        :key="sec.key"
        class="diff-section-card"
        :class="`status-${diff.sections[sec.key]?.status || 'unchanged'}`"
      >
        <header class="section-diff-header">
          <h3 class="section-diff-title">{{ sec.label }}</h3>
          <span
            class="section-status-badge"
            :class="getStatusBadge(diff.sections[sec.key]?.status || 'unchanged').class"
          >
            {{ getStatusBadge(diff.sections[sec.key]?.status || 'unchanged').text }}
          </span>
        </header>

        <div v-if="diff.sections[sec.key]?.status === 'unchanged'" class="section-diff-empty">
          <p class="muted-text">Esta seção permaneceu idêntica entre as versões comparadas.</p>
        </div>

        <div v-else class="section-diff-content">
          <template v-for="(chunk, idx) in diff.sections[sec.key]?.chunks || []" :key="idx">
            <ins v-if="chunk.type === 'insert'" class="diff-chunk insert" :title="'Texto adicionado'">{{ chunk.text }}</ins>
            <del v-else-if="chunk.type === 'delete'" class="diff-chunk delete" :title="'Texto removido'">{{ chunk.text }}</del>
            <span v-else class="diff-chunk equal">{{ chunk.text }}</span>
          </template>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.diff-viewer {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.diff-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  padding: 0.625rem 1rem;
  background-color: var(--color-surface-subtle, rgba(0, 0, 0, 0.03));
  border: 1px solid var(--color-border-subtle, rgba(0, 0, 0, 0.08));
  border-radius: 6px;
  font-size: 0.8125rem;
  color: var(--color-text-muted, #666);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.diff-sample {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
}

.diff-sample.insert {
  background-color: #d1fae5;
  border: 1px solid #10b981;
}

.diff-sample.delete {
  background-color: #fee2e2;
  border: 1px solid #ef4444;
}

.diff-sample.unchanged {
  background-color: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #ccc);
}

.diff-sections {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.diff-section-card {
  border: 1px solid var(--color-border, rgba(0, 0, 0, 0.1));
  border-radius: 8px;
  background: var(--color-surface, #fff);
  overflow: hidden;
}

.section-diff-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.625rem 1rem;
  background-color: var(--color-surface-subtle, rgba(0, 0, 0, 0.02));
  border-bottom: 1px solid var(--color-border-subtle, rgba(0, 0, 0, 0.06));
}

.section-diff-title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text, inherit);
}

.section-status-badge {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.badge-modified {
  background-color: #fef3c7;
  color: #92400e;
}

.badge-added {
  background-color: #d1fae5;
  color: #065f46;
}

.badge-removed {
  background-color: #fee2e2;
  color: #991b1b;
}

.badge-unchanged {
  background-color: var(--color-surface-subtle, rgba(0, 0, 0, 0.05));
  color: var(--color-text-muted, #777);
}

.section-diff-empty {
  padding: 1rem;
  font-size: 0.875rem;
  color: var(--color-text-muted, #666);
  font-style: italic;
}

.section-diff-content {
  padding: 1rem;
  font-size: 0.9375rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
}

.diff-chunk {
  text-decoration: none;
}

.diff-chunk.insert {
  background-color: #d1fae5;
  color: #065f46;
  border-bottom: 2px solid #10b981;
  padding: 1px 2px;
  border-radius: 2px;
}

.diff-chunk.delete {
  background-color: #fee2e2;
  color: #991b1b;
  text-decoration: line-through;
  border-bottom: 2px solid #ef4444;
  padding: 1px 2px;
  border-radius: 2px;
}

.diff-chunk.equal {
  color: var(--color-text, inherit);
}
</style>
