<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { StudySummary, ReadingStatus } from '../../types'
import Icon from '../ui/Icon.vue'
import EmptyState from '../ui/EmptyState.vue'
import GroupBySelector from './GroupBySelector.vue'
import GroupSection from './GroupSection.vue'
import StudyStatusBadge from '../StudyStatusBadge.vue'
import { useStudyGrouping } from '../../composables/useStudyGrouping'

interface Props {
  studies: StudySummary[]
  bookId: number
  chapterId?: number | null
  chapters?: { id: number; name: string }[]
  activeStudyId?: number | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  chapterId: null,
  chapters: () => [],
  activeStudyId: null,
  loading: false,
})

const emit = defineEmits<{
  (e: 'select-study', studyId: number): void
  (e: 'trash-study', study: StudySummary): void
}>()

const { currentCriteria, groups, toggleGroup } = useStudyGrouping({
  studies: computed(() => props.studies),
  storageKey: `caderno_group_by_list_${props.bookId}`,
  chapters: computed(() => props.chapters),
})

function onStatusChange(study: StudySummary, newStatus: ReadingStatus) {
  study.reading_status = newStatus
}

function formatDate(isoStr: string): string {
  try {
    return new Date(isoStr).toLocaleDateString('pt-BR')
  } catch {
    return isoStr
  }
}
</script>

<template>
  <div class="study-list-view" role="region" aria-label="Visualização em Lista de Estudos">
    <EmptyState
      v-if="studies.length === 0 && !loading"
      icon="book-open"
      title="Nenhum estudo neste capítulo"
      description="Importe o texto-base de um fichamento para registrar reflexões e análises sobre este trecho da leitura."
      heading-level="h3"
    >
      <RouterLink
        v-if="chapterId"
        class="button primary"
        :to="{ name: 'import', query: { book: bookId, chapter: chapterId } }"
      >
        Importar estudo
      </RouterLink>
    </EmptyState>

    <div v-else class="study-list-container">
      <div class="list-controls-bar">
        <GroupBySelector v-model="currentCriteria" />
      </div>

      <div class="groups-wrapper">
        <GroupSection
          v-for="group in groups"
          :key="group.id"
          :id="group.id"
          :title="group.title"
          :count="group.count"
          :is-collapsed="group.isCollapsed"
          :badge-label="group.badgeLabel"
          :badge-class="group.badgeClass"
          @toggle="toggleGroup"
        >
          <div class="study-tabular-list">
            <div class="list-header-row">
              <span class="col-title">Título do Estudo</span>
              <span class="col-status">Status</span>
              <span class="col-location">Localização</span>
              <span class="col-date">Data</span>
              <span class="col-actions">Ações</span>
            </div>

            <div
              v-for="study in group.studies"
              :key="study.id"
              class="study-row-item"
              :class="{ 'is-focused': activeStudyId === study.id }"
              @click="emit('select-study', study.id)"
            >
              <div class="col-title cell">
                <RouterLink
                  :to="{ name: 'study', params: { bookId, studyId: study.id } }"
                  class="row-title-link"
                  @click.stop="emit('select-study', study.id)"
                >
                  {{ study.title }}
                </RouterLink>
              </div>

              <div class="col-status cell">
                <StudyStatusBadge
                  :status="study.reading_status || 'rascunho'"
                  :study-id="study.id"
                  :interactive="true"
                  @change="(newSt) => onStatusChange(study, newSt)"
                />
              </div>

              <div class="col-location cell">
                <span v-if="study.location" class="location-tag">
                  <Icon name="book-open" :size="12" class="mr-1 inline" />
                  {{ study.location }}
                </span>
                <span v-else class="text-muted">—</span>
              </div>

              <div class="col-date cell">
                <time :datetime="study.created_at" class="row-date">
                  {{ formatDate(study.created_at) }}
                </time>
              </div>

              <div class="col-actions cell">
                <button
                  type="button"
                  class="row-trash-btn"
                  title="Mover estudo para a lixeira"
                  aria-label="Mover estudo para a lixeira"
                  @click.stop="emit('trash-study', study)"
                >
                  <Icon name="trash" :size="14" />
                </button>
              </div>
            </div>
          </div>
        </GroupSection>
      </div>
    </div>
  </div>
</template>

<style scoped>
.study-list-view {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.list-controls-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1.25rem;
}

.study-tabular-list {
  display: flex;
  flex-direction: column;
  background: var(--color-surface, #ffffff);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-card, 8px);
  overflow: hidden;
}

.list-header-row {
  display: flex;
  align-items: center;
  padding: 0.65rem 1rem;
  background-color: var(--color-surface-soft, #f8fafc);
  border-bottom: 1px solid var(--color-border-divider);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-meta, #556984);
}

.study-row-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border-divider);
  transition: background-color 0.15s ease;
  cursor: pointer;
}

.study-row-item:last-child {
  border-bottom: none;
}

.study-row-item:hover {
  background-color: var(--color-surface-hover, #f1f5f9);
}

.study-row-item.is-focused {
  background-color: var(--color-selected-bg, #eaf0ff);
  border-left: 3px solid var(--color-accent, #1d4ed8);
}

.col-title {
  flex: 2 1 0%;
  min-width: 0;
}

.col-status {
  flex: 0.9 1 0%;
  min-width: 110px;
}

.col-location {
  flex: 1.2 1 0%;
  min-width: 0;
}

.col-date {
  flex: 0.8 1 0%;
  min-width: 80px;
}

.col-actions {
  flex: 0 0 44px;
  display: flex;
  justify-content: flex-end;
}

.row-title-link {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-inverse-bg, #0f172a);
  text-decoration: none;
}

.row-title-link:hover {
  color: var(--color-accent);
  text-decoration: underline;
}

.location-tag {
  font-size: 0.82rem;
  color: var(--color-muted, #64748b);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-date {
  font-size: 0.8rem;
  color: var(--color-muted, #64748b);
  font-variant-numeric: tabular-nums;
}

.row-trash-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-muted);
  border-radius: var(--radius-control);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.row-trash-btn:hover {
  color: var(--color-danger, #b91c1c);
  background: var(--color-surface-hover);
  border-color: var(--color-border);
}

@media (max-width: 640px) {
  .list-header-row {
    display: none;
  }

  .study-row-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.35rem;
    padding: 0.85rem 1rem;
  }

  .col-actions {
    align-self: flex-end;
    margin-top: -1.5rem;
  }
}
</style>
