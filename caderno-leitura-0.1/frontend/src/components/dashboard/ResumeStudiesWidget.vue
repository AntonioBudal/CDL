<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import type { RecentStudyActivityItem } from '../../types.ts'
import StudyStatusBadge from '../StudyStatusBadge.vue'
import Icon from '../ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    studies?: RecentStudyActivityItem[]
    collapsible?: boolean
  }>(),
  {
    studies: () => [],
    collapsible: false,
  }
)

const expanded = ref(false)

const displayedStudies = computed(() => {
  if (expanded.value) {
    return props.studies.slice(0, 10)
  }
  return props.studies.slice(0, 5)
})

const canExpand = computed(() => props.studies.length > 5)

function formatRelativeTime(isoStr: string): string {
  if (!isoStr) return ''
  try {
    const d = new Date(isoStr)
    const now = new Date()
    const diffMs = now.getTime() - d.getTime()
    const diffMin = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMin / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMin < 1) return 'Agora mesmo'
    if (diffMin < 60) return `Há ${diffMin} min`
    if (diffHours < 24) return `Há ${diffHours} h`
    if (diffDays === 1) return 'Ontem'
    if (diffDays < 7) return `Há ${diffDays} dias`

    return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
  } catch {
    return isoStr
  }
}
</script>

<template>
  <section class="resume-studies-widget card" aria-labelledby="resume-studies-heading">
    <div class="widget-header">
      <div class="header-title-group">
        <Icon name="book-open" :size="20" class="header-icon" aria-hidden="true" />
        <h2 id="resume-studies-heading" class="widget-title">Continuar Estudos</h2>
        <span v-if="studies.length > 0" class="badge-count" :aria-label="`${studies.length} estudos recentes`">
          {{ studies.length }}
        </span>
      </div>
    </div>

    <div v-if="studies.length === 0" class="empty-state">
      <Icon name="book" :size="32" class="empty-icon" aria-hidden="true" />
      <p class="empty-text">Nenhum estudo recente encontrado.</p>
      <RouterLink to="/books" class="btn-empty-action">
        Explorar Acervo de Livros
      </RouterLink>
    </div>

    <div v-else class="studies-list" role="list">
      <article
        v-for="study in displayedStudies"
        :key="study.study_id"
        class="study-card"
        role="listitem"
      >
        <div class="study-card-content">
          <div class="study-meta-top">
            <span class="book-name" :title="study.book_title">
              {{ study.book_title }}
            </span>
            <span v-if="study.chapter_title" class="meta-sep" aria-hidden="true">•</span>
            <span v-if="study.chapter_title" class="chapter-name" :title="study.chapter_title">
              {{ study.chapter_title }}
            </span>
          </div>

          <h3 class="study-title">
            <RouterLink
              :to="{ path: `/books/${study.book_id}`, query: { study: String(study.study_id) } }"
              class="study-title-link"
            >
              {{ study.title }}
            </RouterLink>
          </h3>

          <div class="study-meta-bottom">
            <StudyStatusBadge :status="study.reading_status" :interactive="false" />
            <span class="updated-time" :title="study.updated_at">
              {{ formatRelativeTime(study.updated_at) }}
            </span>
          </div>
        </div>

        <div class="study-card-actions">
          <RouterLink
            :to="{ path: `/books/${study.book_id}`, query: { study: String(study.study_id) } }"
            class="btn-resume-action"
            :aria-label="`Continuar estudo: ${study.title}`"
          >
            <span>Continuar</span>
            <Icon name="arrow-right" :size="16" aria-hidden="true" />
          </RouterLink>
        </div>
      </article>

      <div v-if="canExpand" class="expand-actions">
        <button
          type="button"
          class="btn-toggle-expand"
          :aria-expanded="expanded"
          @click="expanded = !expanded"
        >
          <span>{{ expanded ? 'Mostrar menos' : `Ver mais (${studies.length})` }}</span>
          <Icon :name="expanded ? 'chevron-down' : 'chevron-right'" :size="16" aria-hidden="true" />
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.resume-studies-widget {
  padding: 1.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 0.75rem);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.widget-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-icon {
  color: var(--color-accent);
}

.widget-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-text);
}

.badge-count {
  background: var(--color-surface-hover);
  color: var(--color-text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  border: 1px solid var(--color-border);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.5rem 1rem;
  text-align: center;
  gap: 0.75rem;
  color: var(--color-text-muted);
}

.empty-icon {
  opacity: 0.5;
}

.empty-text {
  margin: 0;
  font-size: 0.875rem;
}

.btn-empty-action {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: 0.5rem 1rem;
  background: var(--color-accent);
  color: var(--color-on-accent, #ffffff);
  border-radius: var(--radius-md, 0.5rem);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: opacity 0.15s ease;
}

.btn-empty-action:hover {
  opacity: 0.9;
}

.studies-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.study-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: var(--color-surface-alt, var(--color-surface));
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 0.5rem);
  gap: 1rem;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.study-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-sm);
}

.study-card-content {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  flex: 1;
  min-width: 0;
}

.study-meta-top {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-name {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta-sep {
  opacity: 0.5;
}

.chapter-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.study-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.35;
}

.study-title-link {
  color: var(--color-text);
  text-decoration: none;
  display: inline-block;
}

.study-title-link:hover {
  color: var(--color-accent);
  text-decoration: underline;
}

.study-meta-bottom {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.75rem;
}

.updated-time {
  color: var(--color-text-muted);
}

.study-card-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.btn-resume-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem 0.875rem;
  background: var(--color-surface);
  color: var(--color-accent);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 0.5rem);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-resume-action:hover {
  background: var(--color-accent);
  color: var(--color-on-accent, #ffffff);
  border-color: var(--color-accent);
}

.expand-actions {
  display: flex;
  justify-content: center;
  padding-top: 0.25rem;
}

.btn-toggle-expand {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  min-height: 44px;
  padding: 0.5rem 1rem;
  background: transparent;
  color: var(--color-text-muted);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md, 0.5rem);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-toggle-expand:hover {
  color: var(--color-accent);
  border-color: var(--color-accent);
  background: var(--color-surface-hover);
}

@media (max-width: 640px) {
  .study-card {
    flex-direction: column;
    align-items: stretch;
  }

  .study-card-actions {
    margin-top: 0.25rem;
  }

  .btn-resume-action {
    width: 100%;
  }
}
</style>
