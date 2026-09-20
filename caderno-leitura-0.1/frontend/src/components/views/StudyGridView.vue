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
  storageKey: `caderno_group_by_grid_${props.bookId}`,
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
  <div class="study-grid-view" role="region" aria-label="Visualização em Grade de Estudos">
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

    <div v-else class="study-grid-container">
      <div class="grid-controls-bar">
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
          <div class="study-cards-grid">
            <article
              v-for="study in group.studies"
              :key="study.id"
              class="study-card"
              :class="{ 'is-focused': activeStudyId === study.id }"
              @click="emit('select-study', study.id)"
            >
              <div class="card-header">
                <StudyStatusBadge
                  :status="study.reading_status || 'rascunho'"
                  :study-id="study.id"
                  :interactive="true"
                  @change="(newSt) => onStatusChange(study, newSt)"
                />
                <time :datetime="study.created_at" class="card-date">{{ formatDate(study.created_at) }}</time>
              </div>

              <div class="card-body">
                <h3 class="card-title">
                  <RouterLink
                    :to="{ name: 'study', params: { bookId, studyId: study.id } }"
                    class="card-title-link"
                    @click.stop="emit('select-study', study.id)"
                  >
                    {{ study.title }}
                  </RouterLink>
                </h3>
                <p class="card-location" v-if="study.location">
                  <Icon name="book-open" :size="13" class="location-icon" />
                  <span>{{ study.location }}</span>
                </p>
              </div>

              <div class="card-footer">
                <RouterLink
                  :to="{ name: 'study', params: { bookId, studyId: study.id } }"
                  class="card-action-link"
                >
                  Abrir leitura →
                </RouterLink>
                <button
                  type="button"
                  class="trash-action-btn"
                  title="Mover estudo para a lixeira"
                  aria-label="Mover estudo para a lixeira"
                  @click.stop="emit('trash-study', study)"
                >
                  <Icon name="trash" :size="14" />
                </button>
              </div>
            </article>
          </div>
        </GroupSection>
      </div>
    </div>
  </div>
</template>

<style scoped>
.study-grid-view {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.grid-controls-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1.25rem;
}

.study-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.study-card {
  background: var(--color-surface, #ffffff);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-card, 8px);
  padding: 1rem 1.15rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
  cursor: pointer;
}

.study-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-border-hover, #94a3b8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.study-card.is-focused {
  border-color: var(--color-accent, #1d4ed8);
  outline: 2px solid var(--color-accent);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.65rem;
}

.card-badge {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.15rem 0.45rem;
  border-radius: var(--radius-badge, 4px);
  background-color: color-mix(in srgb, var(--color-accent) 12%, var(--color-surface));
  color: var(--color-accent);
}

.card-date {
  font-size: 0.78rem;
  color: var(--color-muted, #64748b);
  font-variant-numeric: tabular-nums;
}

.card-body {
  flex: 1 1 auto;
  margin-bottom: 0.85rem;
}

.card-title {
  margin: 0 0 0.35rem 0;
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.35;
}

.card-title-link {
  color: var(--color-inverse-bg, #0f172a);
  text-decoration: none;
}

.card-title-link:hover {
  color: var(--color-accent);
}

.card-location {
  margin: 0;
  font-size: 0.82rem;
  color: var(--color-muted, #64748b);
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.location-icon {
  flex-shrink: 0;
  color: var(--color-meta, #556984);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--color-border-divider);
  padding-top: 0.65rem;
  margin-top: auto;
}

.card-action-link {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-accent);
  text-decoration: none;
}

.card-action-link:hover {
  text-decoration: underline;
}

.trash-action-btn {
  min-width: 32px;
  min-height: 32px;
  padding: 0;
  background: transparent;
  color: var(--color-muted);
  border: 1px solid transparent;
  border-radius: var(--radius-control);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.trash-action-btn:hover {
  color: var(--color-danger, #b91c1c);
  background: var(--color-surface-hover);
  border-color: var(--color-border);
}

@media (max-width: 640px) {
  .study-cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
