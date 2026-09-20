<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { UnlinkedStudyItem } from '../../types.ts'
import StudyStatusBadge from '../StudyStatusBadge.vue'
import Icon from '../ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    unlinkedStudies?: UnlinkedStudyItem[]
    totalCount?: number
  }>(),
  {
    unlinkedStudies: () => [],
    totalCount: 0,
  }
)
</script>

<template>
  <section class="orphan-studies-widget card" aria-labelledby="orphan-studies-heading">
    <div class="widget-header">
      <div class="header-title-group">
        <Icon name="network" :size="20" class="header-icon" aria-hidden="true" />
        <h2 id="orphan-studies-heading" class="widget-title">Estudos para Conectar</h2>
        <span
          class="badge-count"
          :class="{ 'badge-alert': (totalCount || unlinkedStudies.length) > 0 }"
          :aria-label="`${totalCount || unlinkedStudies.length} estudos sem relações`"
        >
          {{ totalCount || unlinkedStudies.length }}
        </span>
      </div>
      <p class="header-sub">Estudos que ainda não possuem vínculos conceituais no acervo.</p>
    </div>

    <div v-if="unlinkedStudies.length === 0" class="empty-state">
      <Icon name="check-circle" :size="32" class="empty-icon-success" aria-hidden="true" />
      <p class="empty-text">Excelente! Todos os estudos ativos possuem conexões no acervo.</p>
    </div>

    <div v-else class="studies-list" role="list">
      <article
        v-for="study in unlinkedStudies"
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
              :to="{ path: `/livros/${study.book_id}/estudos/${study.study_id}` }"
              class="study-title-link"
            >
              {{ study.title }}
            </RouterLink>
          </h3>

          <div class="study-meta-bottom">
            <StudyStatusBadge :status="study.reading_status" :interactive="false" />
          </div>
        </div>

        <div class="study-card-actions">
          <RouterLink
            :to="{ path: `/livros/${study.book_id}/estudos/${study.study_id}`, query: { openRelation: 'true' } }"
            class="btn-connect-action"
            :aria-label="`Criar relação para o estudo: ${study.title}`"
          >
            <Icon name="link" :size="16" aria-hidden="true" />
            <span>Conectar</span>
          </RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.orphan-studies-widget {
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
  flex-direction: column;
  gap: 0.25rem;
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

.header-sub {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
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

.badge-count.badge-alert {
  background: rgba(234, 179, 8, 0.15);
  color: #ca8a04;
  border-color: rgba(234, 179, 8, 0.3);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  text-align: center;
  gap: 0.5rem;
  color: var(--color-text-muted);
}

.empty-icon-success {
  color: #16a34a;
}

.empty-text {
  margin: 0;
  font-size: 0.875rem;
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
  padding: 0.875rem 1rem;
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
  gap: 0.25rem;
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
  font-size: 0.9375rem;
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
  gap: 0.5rem;
  font-size: 0.75rem;
}

.study-card-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.btn-connect-action {
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
  font-size: 0.8125rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-connect-action:hover {
  background: var(--color-accent);
  color: var(--color-on-accent, #ffffff);
  border-color: var(--color-accent);
}

@media (max-width: 640px) {
  .study-card {
    flex-direction: column;
    align-items: stretch;
  }

  .study-card-actions {
    margin-top: 0.25rem;
  }

  .btn-connect-action {
    width: 100%;
  }
}
</style>
