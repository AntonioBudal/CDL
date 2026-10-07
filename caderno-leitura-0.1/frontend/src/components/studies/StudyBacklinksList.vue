<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import type { BacklinkItem } from '../../types'
import { getStudyBacklinks } from '../../services/api'
import Icon from '../ui/Icon.vue'

interface Props {
  studyId: number
}

const props = defineProps<Props>()

const backlinks = ref<BacklinkItem[]>([])
const total = ref(0)
const loading = ref(false)
const error = ref('')

const SECTION_TRANSLATIONS: Record<string, string> = {
  summary: 'Resumo',
  explanation: 'Explicação',
  concepts: 'Conceitos',
  references: 'Referências',
  notes: 'Notas',
}

function getSectionLabel(sectionKey: string): string {
  return SECTION_TRANSLATIONS[sectionKey] || sectionKey
}

async function fetchBacklinks(id: number) {
  if (!id) return
  loading.value = true
  error.value = ''
  try {
    const res = await getStudyBacklinks(id)
    backlinks.value = res.items
    total.value = res.total
  } catch (err) {
    error.value = 'Não foi possível carregar as menções recebidas.'
    backlinks.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

watch(
  () => props.studyId,
  (newId) => {
    if (newId) {
      fetchBacklinks(newId)
    }
  },
  { immediate: true }
)

defineExpose({
  reload: () => fetchBacklinks(props.studyId),
})
</script>

<template>
  <section class="study-backlinks-section panel" aria-labelledby="backlinks-heading">
    <div class="backlinks-header">
      <div class="backlinks-title-wrapper">
        <Icon name="network" :size="18" class="backlinks-icon" aria-hidden="true" />
        <h2 id="backlinks-heading" class="backlinks-title">
          Menções Contextuais (Backlinks)
        </h2>
        <span class="backlinks-counter" :title="`${total} referências no acervo`">
          {{ total }}
        </span>
      </div>
      <p class="backlinks-subtitle">
        Estudos do acervo que citam este documento via <code>[[...]]</code>
      </p>
    </div>

    <!-- Carregando -->
    <div v-if="loading" class="backlinks-loading" aria-live="polite">
      Carregando referências contextuais...
    </div>

    <!-- Erro -->
    <div v-else-if="error" class="backlinks-error" role="alert">
      {{ error }}
    </div>

    <!-- Nenhum backlink -->
    <div v-else-if="total === 0" class="backlinks-empty">
      <p class="empty-message">
        Nenhum outro estudo menciona este documento no momento. Digite <code>[[{{ studyId }}]]</code> em outro estudo para conectar.
      </p>
    </div>

    <!-- Lista de backlinks -->
    <div v-else class="backlinks-grid" role="list">
      <article
        v-for="item in backlinks"
        :key="item.id"
        class="backlink-card"
        role="listitem"
      >
        <div class="backlink-card-top">
          <RouterLink
            :to="`/livros/${item.book_id}/estudos/${item.source_study_id}`"
            class="backlink-study-link"
          >
            <span class="study-name">{{ item.source_study_title }}</span>
          </RouterLink>
          <span class="backlink-section-badge">
            {{ getSectionLabel(item.section) }}
          </span>
        </div>

        <div class="backlink-hierarchy-meta">
          <span class="meta-book-title">{{ item.book_title }}</span>
          <span v-if="item.chapter_name" class="meta-separator">·</span>
          <span v-if="item.chapter_name" class="meta-chapter-name">{{ item.chapter_name }}</span>
        </div>

        <blockquote class="backlink-context-snippet" :title="`Citado na seção ${getSectionLabel(item.section)}`">
          {{ item.context_snippet }}
        </blockquote>
      </article>
    </div>
  </section>
</template>

<style scoped>
.study-backlinks-section {
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius-surface, 8px);
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e4e4e7);
}

.backlinks-header {
  margin-bottom: 1rem;
}

.backlinks-title-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.backlinks-icon {
  color: var(--color-primary, #3b82f6);
  flex-shrink: 0;
}

.backlinks-title {
  font-size: 1.0625rem;
  font-weight: 600;
  color: var(--color-text, #18181b);
  margin: 0;
}

.backlinks-counter {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 0.4rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 9999px;
  background: var(--color-surface-hover, #f4f4f5);
  color: var(--color-text-muted, #71717a);
  border: 1px solid var(--color-border, #d4d4d8);
}

.backlinks-subtitle {
  font-size: 0.8125rem;
  color: var(--color-text-muted, #71717a);
  margin: 0.25rem 0 0 0;
}

.backlinks-subtitle code {
  font-size: 0.8em;
  padding: 0.1em 0.3em;
  border-radius: 3px;
  background: var(--color-surface-hover, #f4f4f5);
}

.backlinks-loading,
.backlinks-error,
.backlinks-empty {
  padding: 1rem;
  font-size: 0.875rem;
  color: var(--color-text-muted, #71717a);
  background: var(--color-surface-subtle, rgba(0, 0, 0, 0.02));
  border-radius: 6px;
  text-align: center;
}

.backlinks-error {
  color: var(--color-danger, #ef4444);
}

.empty-message {
  margin: 0;
}

.backlinks-grid {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.backlink-card {
  padding: 0.875rem 1rem;
  border-radius: 6px;
  background: var(--color-surface-subtle, #fafafa);
  border: 1px solid var(--color-border-subtle, #e4e4e7);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.backlink-card:hover {
  border-color: var(--color-border-strong, #d4d4d8);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.backlink-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.backlink-study-link {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-primary, #3b82f6);
  text-decoration: none;
  transition: color 0.15s ease;
}

.backlink-study-link:hover {
  color: var(--color-primary-hover, #2563eb);
  text-decoration: underline;
}

.backlink-section-badge {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  background: var(--color-surface-hover, #f4f4f5);
  color: var(--color-text-muted, #71717a);
  border: 1px solid var(--color-border, #e4e4e7);
  white-space: nowrap;
}

.backlink-hierarchy-meta {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: var(--color-text-muted, #71717a);
  margin-top: 0.15rem;
  margin-bottom: 0.5rem;
}

.meta-separator {
  opacity: 0.5;
}

.backlink-context-snippet {
  margin: 0;
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: var(--color-text, #27272a);
  background: var(--color-surface, #ffffff);
  border-left: 3px solid var(--color-primary, #3b82f6);
  border-radius: 0 4px 4px 0;
  font-style: italic;
}
</style>
