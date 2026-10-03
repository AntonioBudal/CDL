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
    <!-- Estado de carregamento com Skeleton Screens fiéis à geometria do cartão -->
    <div v-if="loading" class="study-grid-container" aria-busy="true" aria-label="Carregando estudos">
      <div class="study-cards-grid">
        <div v-for="n in 6" :key="n" class="study-card skeleton-card" aria-hidden="true">
          <div class="card-header skeleton-header">
            <div class="skeleton-pill skeleton-animation"></div>
            <div class="skeleton-date skeleton-animation"></div>
          </div>
          <div class="card-body">
            <div class="skeleton-line skeleton-title skeleton-animation"></div>
            <div class="skeleton-line skeleton-title-short skeleton-animation"></div>
            <div class="skeleton-line skeleton-location skeleton-animation"></div>
            <div class="skeleton-line skeleton-preview skeleton-animation"></div>
            <div class="skeleton-line skeleton-preview-short skeleton-animation"></div>
          </div>
          <div class="card-footer skeleton-footer">
            <div class="skeleton-line skeleton-btn skeleton-animation"></div>
            <div class="skeleton-circle skeleton-animation"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Estado vazio quando não houver estudos e não estiver carregando -->
    <EmptyState
      v-else-if="studies.length === 0"
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

    <!-- Grade com dados carregados -->
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
              :class="[
                'status-' + (study.reading_status || 'rascunho'),
                { 'is-focused': activeStudyId === study.id }
              ]"
              tabindex="0"
              role="article"
              :aria-label="study.title"
              @click="emit('select-study', study.id)"
              @keydown.enter="emit('select-study', study.id)"
            >
              <div class="card-header">
                <StudyStatusBadge
                  :status="study.reading_status || 'rascunho'"
                  :study-id="study.id"
                  :interactive="true"
                  @click.stop
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
                <p v-if="study.summary_preview" class="card-summary-preview">
                  {{ study.summary_preview }}
                </p>
              </div>

              <div class="card-footer">
                <div class="card-footer-left">
                  <RouterLink
                    :to="{ name: 'study', params: { bookId, studyId: study.id } }"
                    class="card-action-link"
                    @click.stop="emit('select-study', study.id)"
                  >
                    Abrir leitura →
                  </RouterLink>
                  <div
                    v-if="(study.highlights_count && study.highlights_count > 0) || (study.relations_count && study.relations_count > 0)"
                    class="card-metrics"
                  >
                    <span
                      v-if="study.highlights_count && study.highlights_count > 0"
                      class="metric-badge"
                      title="Destaques e anotações no estudo"
                    >
                      <Icon name="pencil" :size="12" />
                      <span>{{ study.highlights_count }}</span>
                    </span>
                    <span
                      v-if="study.relations_count && study.relations_count > 0"
                      class="metric-badge"
                      title="Conexões semânticas vinculadas"
                    >
                      <Icon name="link" :size="12" />
                      <span>{{ study.relations_count }}</span>
                    </span>
                  </div>
                </div>
                <button
                  type="button"
                  class="trash-action-btn"
                  title="Mover estudo para a lixeira"
                  aria-label="Mover estudo para a lixeira"
                  @click.stop="emit('trash-study', study)"
                >
                  <Icon name="trash" :size="15" />
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

/* Responsividade de colunas: 3 colunas (desktop amplo), 2 colunas (tablet/médio), 1 coluna (mobile) */
.study-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
}

@media (max-width: 1024px) {
  .study-cards-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .study-cards-grid {
    grid-template-columns: 1fr;
    gap: 0.85rem;
  }
}

/* Cartão do Estudo */
.study-card {
  position: relative;
  background: var(--color-surface, #ffffff);
  border: var(--border-width, 1px) solid var(--color-border);
  border-left: 4px solid var(--color-border);
  border-radius: var(--radius-card, 8px);
  padding: 1.1rem 1.15rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 190px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
  cursor: pointer;
  outline: none;
}

/* Friso Cromático por Status */
.study-card.status-rascunho {
  border-left: 4px solid var(--color-status-rascunho, #a1a1aa);
}

.study-card.status-em_andamento,
.study-card.status-em_estudo {
  border-left: 4px solid var(--color-status-andamento, #f59e0b);
}

.study-card.status-revisado {
  border-left: 4px solid var(--color-status-revisado, #3b82f6);
}

.study-card.status-concluido {
  border-left: 4px solid var(--color-status-concluido, #10b981);
}

.study-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-border-hover, #94a3b8);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  background-color: var(--color-surface-hover);
}

.study-card:focus-visible {
  outline: 2px solid var(--color-accent, #1d4ed8);
  outline-offset: 2px;
}

.study-card.is-focused {
  border-color: var(--color-accent, #1d4ed8);
  box-shadow: 0 0 0 2px var(--color-accent);
}

.study-card:hover .card-title-link {
  color: var(--color-accent);
}

.study-card:hover .card-date {
  color: var(--color-text);
  opacity: 0.9;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.65rem;
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
  margin: 0 0 0.4rem 0;
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-title-link {
  color: var(--color-text);
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

/* Prévia Tipográfica Analítica */
.card-summary-preview {
  margin: 0.65rem 0 0 0;
  font-size: 0.84rem;
  line-height: 1.45;
  color: var(--color-muted, #64748b);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  font-style: italic;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--color-border-divider, rgba(0, 0, 0, 0.06));
  padding-top: 0.65rem;
  margin-top: auto;
  gap: 0.5rem;
}

.card-footer-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.card-action-link {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-accent, #1d4ed8);
  text-decoration: none;
}

.card-action-link:hover {
  text-decoration: underline;
}

.card-metrics {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.metric-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.15rem 0.4rem;
  border-radius: var(--radius-badge, 4px);
  background-color: var(--color-surface-hover, rgba(0, 0, 0, 0.04));
  color: var(--color-muted, #64748b);
  border: 1px solid var(--color-border-divider, rgba(0, 0, 0, 0.06));
}

/* Botão da Lixeira com Alvo Tátil Mínimo de 44x44px */
.trash-action-btn {
  min-width: 44px;
  min-height: 44px;
  padding: 0;
  background: transparent;
  color: var(--color-muted, #64748b);
  border: 1px solid transparent;
  border-radius: var(--radius-control, 6px);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
  flex-shrink: 0;
}

.trash-action-btn:hover {
  color: var(--color-danger, #b91c1c);
  background: var(--color-surface-hover);
  border-color: var(--color-border);
}

/* Skeleton Screens fiéis à geometria do cartão */
.skeleton-card {
  cursor: default;
  pointer-events: none;
  border-left: 4px solid var(--color-border);
}

.skeleton-animation {
  background: linear-gradient(
    90deg,
    var(--color-surface-hover, #f1f5f9) 25%,
    var(--color-border, #e2e8f0) 50%,
    var(--color-surface-hover, #f1f5f9) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-pulse 1.6s infinite ease-in-out;
  border-radius: 4px;
}

@keyframes skeleton-pulse {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.skeleton-pill {
  width: 76px;
  height: 20px;
}

.skeleton-date {
  width: 60px;
  height: 14px;
}

.skeleton-line {
  height: 12px;
  margin-bottom: 0.5rem;
}

.skeleton-title {
  height: 18px;
  width: 85%;
  margin-bottom: 0.4rem;
}

.skeleton-title-short {
  height: 18px;
  width: 50%;
  margin-bottom: 0.6rem;
}

.skeleton-location {
  width: 40%;
  height: 12px;
  margin-bottom: 0.8rem;
}

.skeleton-preview {
  width: 100%;
  height: 12px;
  margin-bottom: 0.35rem;
}

.skeleton-preview-short {
  width: 70%;
  height: 12px;
}

.skeleton-footer {
  border-top: 1px solid var(--color-border-divider, rgba(0, 0, 0, 0.06));
  padding-top: 0.65rem;
}

.skeleton-btn {
  width: 90px;
  height: 16px;
  margin-bottom: 0;
}

.skeleton-circle {
  width: 32px;
  height: 32px;
  border-radius: 6px;
}
</style>
