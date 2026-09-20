<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { RecentRelationItem, StudyRelationType } from '../../types.ts'
import { RELATION_TYPE_LABELS } from '../../composables/useStudyRelations.ts'
import Icon from '../ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    recentRelations?: RecentRelationItem[]
  }>(),
  {
    recentRelations: () => [],
  }
)

function getRelationMeta(type: string) {
  const normType = type as StudyRelationType
  return RELATION_TYPE_LABELS[normType] || {
    outbound: type.replace(/_/g, ' '),
    inbound: type.replace(/_/g, ' '),
    badgeClass: 'badge-neutral',
  }
}

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
  <section class="recent-connections-widget card" aria-labelledby="recent-connections-heading">
    <div class="widget-header">
      <div class="header-title-group">
        <Icon name="network" :size="20" class="header-icon" aria-hidden="true" />
        <h2 id="recent-connections-heading" class="widget-title">Conexões Recentes</h2>
        <span
          v-if="recentRelations.length > 0"
          class="badge-count"
          :aria-label="`${recentRelations.length} conexões registradas`"
        >
          {{ recentRelations.length }}
        </span>
      </div>
      <p class="header-sub">Pontes conceituais estabelecidas recentemente entre estudos.</p>
    </div>

    <div v-if="recentRelations.length === 0" class="empty-state">
      <Icon name="link" :size="32" class="empty-icon" aria-hidden="true" />
      <p class="empty-text">Nenhuma conexão conceitual registrada recentemente.</p>
      <p class="empty-sub">Vincule ideias entre autores para visualizar o diálogo aqui.</p>
    </div>

    <div v-else class="connections-list" role="list">
      <article
        v-for="rel in recentRelations"
        :key="rel.relation_id"
        class="connection-card"
        role="listitem"
      >
        <div class="connection-header">
          <span class="relation-badge" :class="getRelationMeta(rel.relation_type).badgeClass">
            <Icon name="link" :size="12" aria-hidden="true" />
            <span>{{ getRelationMeta(rel.relation_type).outbound }}</span>
          </span>
          <span class="relation-time" :title="rel.created_at">
            {{ formatRelativeTime(rel.created_at) }}
          </span>
        </div>

        <div class="connection-body">
          <div class="study-node source-node">
            <span class="node-book-title" :title="rel.source_book_title">{{ rel.source_book_title }}</span>
            <RouterLink
              :to="{ path: `/livros/${rel.source_book_id}/estudos/${rel.source_study_id}` }"
              class="node-study-link"
              :title="rel.source_study_title"
            >
              {{ rel.source_study_title }}
            </RouterLink>
          </div>

          <div class="node-arrow" aria-hidden="true">
            <Icon name="arrow-right" :size="16" />
          </div>

          <div class="study-node target-node">
            <span class="node-book-title" :title="rel.target_book_title">{{ rel.target_book_title }}</span>
            <RouterLink
              :to="{ path: `/livros/${rel.target_book_id}/estudos/${rel.target_study_id}` }"
              class="node-study-link"
              :title="rel.target_study_title"
            >
              {{ rel.target_study_title }}
            </RouterLink>
          </div>
        </div>

        <p v-if="rel.description" class="connection-description">
          "{{ rel.description }}"
        </p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.recent-connections-widget {
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

.empty-icon {
  opacity: 0.5;
}

.empty-text {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 500;
}

.empty-sub {
  margin: 0;
  font-size: 0.75rem;
}

.connections-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.connection-card {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  padding: 0.875rem 1rem;
  background: var(--color-surface-alt, var(--color-surface));
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 0.5rem);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.connection-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-sm);
}

.connection-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.relation-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  padding: 0.1875rem 0.5rem;
  border-radius: var(--radius-sm, 0.25rem);
  border: 1px solid var(--color-border);
}

.relation-badge.badge-neutral {
  background: var(--color-surface-hover);
  color: var(--color-text-muted);
}

.relation-badge.badge-complement {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  border-color: rgba(34, 197, 94, 0.3);
}

.relation-badge.badge-contradict {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border-color: rgba(239, 68, 68, 0.3);
}

.relation-badge.badge-dependency {
  background: rgba(168, 85, 247, 0.1);
  color: #9333ea;
  border-color: rgba(168, 85, 247, 0.3);
}

.relation-badge.badge-theme {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  border-color: rgba(59, 130, 246, 0.3);
}

.relation-badge.badge-derivation {
  background: rgba(249, 115, 22, 0.1);
  color: #ea580c;
  border-color: rgba(249, 115, 22, 0.3);
}

.relation-time {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.connection-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.study-node {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.node-book-title {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-study-link {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
  min-height: 24px;
}

.node-study-link:hover {
  color: var(--color-accent);
  text-decoration: underline;
}

.node-arrow {
  color: var(--color-text-muted);
  opacity: 0.6;
  flex-shrink: 0;
}

.connection-description {
  margin: 0;
  font-size: 0.8125rem;
  font-style: italic;
  color: var(--color-text-muted);
  border-left: 2px solid var(--color-border);
  padding-left: 0.5rem;
}

@media (max-width: 640px) {
  .connection-body {
    flex-direction: column;
    align-items: flex-start;
  }

  .node-arrow {
    transform: rotate(90deg);
    align-self: center;
    margin: 0.25rem 0;
  }
}
</style>
