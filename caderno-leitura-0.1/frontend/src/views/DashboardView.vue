<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import HeatmapCalendar from '../components/HeatmapCalendar.vue'
import ResumeStudiesWidget from '../components/dashboard/ResumeStudiesWidget.vue'
import OrphanStudiesWidget from '../components/dashboard/OrphanStudiesWidget.vue'
import RecentConnectionsWidget from '../components/dashboard/RecentConnectionsWidget.vue'
import QuickNavChips from '../components/dashboard/QuickNavChips.vue'
import Icon from '../components/ui/Icon.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import LoadingSkeleton from '../components/ui/LoadingSkeleton.vue'
import { api, errorMessage } from '../services/api'
import type { DashboardBlockVisibility, DashboardResponse, TimelineItem } from '../types'

const loading = ref(true)
const loadError = ref('')
const dashboardData = ref<DashboardResponse | null>(null)
const selectedDate = ref<string | null>(null)
const filteringTimeline = ref(false)

const activeNavSection = ref('resume')
const activeMobileTab = ref<'unlinked' | 'relations'>('unlinked')

const blocksVisibility = reactive<DashboardBlockVisibility>({
  resumeStudies: true,
  unlinkedStudies: true,
  recentRelations: true,
  timelineHeatmap: true,
})

const summary = computed(() => dashboardData.value?.summary || {
  total_books: 0,
  total_studies: 0,
  total_reading_days: 0,
  current_streak: 0,
  avg_studies_per_book: 0.0,
  total_relations: 0,
  total_categories: 0,
  unlinked_studies_count: 0,
})

const heatmapPoints = computed(() => dashboardData.value?.heatmap || [])
const timelineItems = computed(() => dashboardData.value?.timeline || [])
const recentStudies = computed(() => dashboardData.value?.recent_studies || [])
const unlinkedStudies = computed(() => dashboardData.value?.unlinked_studies || [])
const latestRelations = computed(() => dashboardData.value?.latest_relations || [])

function loadBlocksVisibility() {
  try {
    const raw = window.localStorage?.getItem('caderno_dashboard_blocks_visibility')
    if (raw) {
      const parsed = JSON.parse(raw)
      Object.assign(blocksVisibility, parsed)
    }
    const tab = window.localStorage?.getItem('caderno_dashboard_mobile_tab')
    if (tab === 'unlinked' || tab === 'relations') {
      activeMobileTab.value = tab
    }
  } catch {
    // ignore
  }
}

function setMobileTab(tab: 'unlinked' | 'relations') {
  activeMobileTab.value = tab
  try {
    window.localStorage?.setItem('caderno_dashboard_mobile_tab', tab)
  } catch {
    // ignore
  }
}

async function loadDashboard(dateFilter?: string | null) {
  if (dateFilter !== undefined) {
    filteringTimeline.value = true
  } else {
    loading.value = true
  }
  loadError.value = ''

  try {
    const tzOffset = -new Date().getTimezoneOffset()
    const data = await api.getDashboard({
      tz_offset: tzOffset,
      days: 365,
      date: dateFilter ?? selectedDate.value,
      limit: 30,
    })
    dashboardData.value = data
  } catch (err) {
    loadError.value = errorMessage(err)
  } finally {
    loading.value = false
    filteringTimeline.value = false
  }
}

async function handleSelectDate(date: string | null) {
  selectedDate.value = date
  await loadDashboard(date)
}

function clearDateFilter() {
  handleSelectDate(null)
}

function formatRelativeDate(isoStr: string): string {
  try {
    const d = new Date(isoStr)
    return d.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return isoStr
  }
}

function formatSelectedDate(dateStr: string): string {
  const [y, m, d] = dateStr.split('-').map(Number)
  return `${String(d).padStart(2, '0')}/${String(m).padStart(2, '0')}/${y}`
}

function actionBadgeLabel(item: TimelineItem): string {
  switch (item.action) {
    case 'book_created':
      return 'Novo livro'
    case 'study_created':
      return 'Novo estudo'
    case 'study_updated':
      return 'Estudo revisado'
    default:
      return 'Atividade'
  }
}

function actionBadgeClass(item: TimelineItem): string {
  switch (item.action) {
    case 'book_created':
      return 'badge-book'
    case 'study_created':
      return 'badge-study'
    case 'study_updated':
      return 'badge-updated'
    default:
      return ''
  }
}

onMounted(() => {
  loadBlocksVisibility()
  loadDashboard()
})
</script>

<template>
  <div class="dashboard-view wrap">
    <!-- Cabeçalho -->
    <header class="page-header dashboard-header">
      <div class="title-area">
        <p class="eyebrow">Cockpit de Estudos e Navegação</p>
        <h1>Dashboard 2.0</h1>
        <p class="intro">
          Retome seus estudos em 1 clique, acompanhe conexões conceituais recentes e monitore o pulso do seu acervo.
        </p>
      </div>
    </header>

    <!-- Estado de carregamento -->
    <div v-if="loading" class="dashboard-skeleton" role="status" aria-label="Carregando indicadores do caderno">
      <div class="metrics-grid" style="margin-bottom: 24px;">
        <LoadingSkeleton shape="rect" height="96px" />
        <LoadingSkeleton shape="rect" height="96px" />
        <LoadingSkeleton shape="rect" height="96px" />
        <LoadingSkeleton shape="rect" height="96px" />
      </div>
      <LoadingSkeleton shape="rect" height="180px" style="margin-bottom: 24px;" />
      <LoadingSkeleton shape="rect" height="240px" />
    </div>

    <!-- Estado de erro -->
    <div v-else-if="loadError" class="notice error" role="alert">
      <h2>Não foi possível carregar o dashboard.</h2>
      <p>{{ loadError }}</p>
      <button class="secondary" type="button" @click="loadDashboard()">
        Tentar novamente
      </button>
    </div>

    <!-- Conteúdo principal -->
    <template v-else-if="dashboardData">
      <!-- Estado vazio quando não há livros -->
      <EmptyState
        v-if="summary.total_books === 0"
        icon="book-open"
        title="Seu caderno ainda não possui livros ativos."
        description="Cadastre seu primeiro livro ou importe notas para começar a visualizar seu ritmo de leitura, sequência de dias ativos e rede de conexões."
      >
        <RouterLink to="/books" class="button primary">
          Ir para o Acervo de Livros
        </RouterLink>
      </EmptyState>

      <div v-else class="dashboard-content">
        <!-- Barra de Indicadores Métricos (Grade 2x2 no celular, 4 colunas em desktop) -->
        <section class="metrics-grid" aria-label="Indicadores principais">
          <div class="metric-card">
            <span class="metric-label">Livros Ativos</span>
            <span class="metric-value">{{ summary.total_books }}</span>
            <span class="metric-sub">no acervo</span>
          </div>

          <div class="metric-card">
            <span class="metric-label">Total de Estudos</span>
            <span class="metric-value">{{ summary.total_studies }}</span>
            <span class="metric-sub">anotações ativas</span>
          </div>

          <div class="metric-card">
            <span class="metric-label">Conexões Criadas</span>
            <span class="metric-value">{{ summary.total_relations }}</span>
            <span class="metric-sub">vínculos conceituais</span>
          </div>

          <div class="metric-card streak-card" :class="{ 'has-streak': summary.current_streak > 0 }">
            <span class="metric-label">Sequência Atual</span>
            <div class="streak-value-group">
              <span class="streak-icon" aria-hidden="true"><Icon name="flame" :size="20" /></span>
              <span class="metric-value">{{ summary.current_streak }}</span>
            </div>
            <span class="metric-sub">
              {{ summary.current_streak === 1 ? 'dia consecutivo' : 'dias consecutivos' }}
            </span>
          </div>
        </section>

        <!-- Chips de Navegação Rápida Aderentes (Mobile/Tablet) -->
        <QuickNavChips
          :active-section="activeNavSection"
          class="mobile-only-chips"
          @navigate="sec => activeNavSection = sec"
        />

        <!-- Cockpit de Retoma e Hub de Navegação (Desktop: 2 colunas | Mobile: Empilhado com Abas) -->
        <div class="cockpit-layout">
          <!-- Coluna Principal (Continuar Estudos) -->
          <div id="section-resume" class="cockpit-primary-col">
            <ResumeStudiesWidget
              v-show="blocksVisibility.resumeStudies"
              :studies="recentStudies"
            />
          </div>

          <!-- Coluna Secundária (Desktop >=1024px) -->
          <div class="cockpit-secondary-col desktop-only-col">
            <div id="section-connect" class="cockpit-subblock">
              <OrphanStudiesWidget
                v-show="blocksVisibility.unlinkedStudies"
                :unlinked-studies="unlinkedStudies"
                :total-count="summary.unlinked_studies_count"
              />
            </div>

            <div id="section-relations" class="cockpit-subblock">
              <RecentConnectionsWidget
                v-show="blocksVisibility.recentRelations"
                :recent-relations="latestRelations"
              />
            </div>
          </div>

          <!-- Abas Comutáveis para Widgets Secundários (Mobile <1024px) -->
          <div id="section-connect" class="mobile-secondary-tabs mobile-only-tabs">
            <div class="secondary-tabs-bar" role="tablist" aria-label="Widgets de conexão e grafo">
              <button
                type="button"
                role="tab"
                class="secondary-tab-btn"
                :class="{ active: activeMobileTab === 'unlinked' }"
                :aria-selected="activeMobileTab === 'unlinked'"
                aria-controls="panel-mobile-unlinked"
                @click="setMobileTab('unlinked')"
              >
                <Icon name="network" :size="16" aria-hidden="true" />
                <span>Para Conectar ({{ summary.unlinked_studies_count }})</span>
              </button>

              <button
                type="button"
                role="tab"
                class="secondary-tab-btn"
                :class="{ active: activeMobileTab === 'relations' }"
                :aria-selected="activeMobileTab === 'relations'"
                aria-controls="panel-mobile-relations"
                @click="setMobileTab('relations')"
              >
                <Icon name="link" :size="16" aria-hidden="true" />
                <span>Conexões ({{ latestRelations.length }})</span>
              </button>
            </div>

            <div
              v-show="activeMobileTab === 'unlinked'"
              id="panel-mobile-unlinked"
              role="tabpanel"
              class="secondary-tab-panel"
            >
              <OrphanStudiesWidget
                :unlinked-studies="unlinkedStudies"
                :total-count="summary.unlinked_studies_count"
              />
            </div>

            <div
              v-show="activeMobileTab === 'relations'"
              id="panel-mobile-relations"
              role="tabpanel"
              class="secondary-tab-panel"
            >
              <RecentConnectionsWidget
                :recent-relations="latestRelations"
              />
            </div>
          </div>
        </div>

        <!-- Seção de Histórico: Mapa de Calor e Linha do Tempo -->
        <div id="section-timeline" class="timeline-heatmap-block">
          <!-- Seção do Mapa de Calor -->
          <section class="heatmap-section" aria-label="Frequência em calendário">
            <HeatmapCalendar
              :points="heatmapPoints"
              :selected-date="selectedDate"
              @select-date="handleSelectDate"
            />
          </section>

          <!-- Seção da Linha do Tempo -->
          <section class="timeline-section" aria-label="Linha do tempo de atividades">
            <div class="timeline-header">
              <div class="timeline-title-area">
                <h2 class="timeline-heading">Atividades Recentes</h2>
                <p class="timeline-sub">
                  Histórico cronológico de criações e revisões no caderno.
                </p>
              </div>

              <!-- Chip de filtro ativo -->
              <div v-if="selectedDate" class="filter-chip" role="status">
                <span>Filtrando por: <strong>{{ formatSelectedDate(selectedDate) }}</strong></span>
                <button
                  type="button"
                  class="clear-filter-btn"
                  aria-label="Limpar filtro de data"
                  @click="clearDateFilter"
                >
                  <Icon name="x" :size="13" /> Limpar
                </button>
              </div>
            </div>

            <!-- Carregando filtro -->
            <p v-if="filteringTimeline" class="state-panel" role="status">
              Atualizando linha do tempo…
            </p>

            <!-- Lista de atividades -->
            <EmptyState
              v-else-if="timelineItems.length === 0"
              icon="calendar"
              :title="selectedDate ? `Nenhuma atividade em ${formatSelectedDate(selectedDate)}` : 'Nenhuma atividade recente registrada'"
              :description="selectedDate ? 'Não há registros de leitura ou atualizações nesta data específica.' : 'O histórico cronológico de criações e revisões no caderno aparecerá aqui conforme você estuda.'"
              heading-level="h3"
            >
              <button
                v-if="selectedDate"
                type="button"
                class="secondary"
                @click="clearDateFilter"
              >
                Exibir todas as atividades
              </button>
            </EmptyState>

            <div v-else class="timeline-list" role="feed" aria-label="Lista de atividades">
              <article
                v-for="item in timelineItems"
                :key="item.id"
                class="timeline-card"
              >
                <div class="timeline-card-header">
                  <span class="action-badge" :class="actionBadgeClass(item)">
                    {{ actionBadgeLabel(item) }}
                  </span>
                  <time :datetime="item.timestamp" class="timeline-time">
                    {{ formatRelativeDate(item.timestamp) }}
                  </time>
                </div>

                <div class="timeline-card-body">
                  <h3 class="timeline-item-title">{{ item.title }}</h3>
                  <p class="timeline-item-context">
                    Livro: <strong>{{ item.book_title }}</strong>
                    <span v-if="item.chapter_title"> · Capítulo: <em>{{ item.chapter_title }}</em></span>
                  </p>
                </div>

                <div class="timeline-card-footer">
                  <RouterLink
                    v-if="item.entity_type === 'study' && item.study_id"
                    :to="`/livros/${item.book_id}/estudos/${item.study_id}`"
                    class="timeline-link"
                  >
                    Ler estudo →
                  </RouterLink>
                  <RouterLink
                    v-else
                    :to="`/livros/${item.book_id}`"
                    class="timeline-link"
                  >
                    Abrir livro →
                  </RouterLink>
                </div>
              </article>
            </div>
          </section>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-bottom: 3rem;
  overflow-x: hidden;
  max-width: 100vw;
  box-sizing: border-box;
}

.dashboard-header {
  margin-bottom: 0.5rem;
}

.eyebrow {
  margin: 0 0 0.25rem 0;
  font-size: 0.82rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-accent);
}

.dashboard-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-ink, #0f172a);
}

.intro {
  margin: 0.4rem 0 0 0;
  font-size: 1rem;
  color: var(--color-muted, #475569);
  max-width: 65ch;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  width: 100%;
}

/* Grade de Métricas */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.metric-card {
  background: var(--color-surface);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-card, 6px);
  padding: 1.25rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.25rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  transition: transform 0.15s ease, border-color 0.15s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-border-hover, #94a3b8);
}

.metric-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-muted, #64748b);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.metric-value {
  font-size: 2.1rem;
  font-weight: 700;
  color: var(--color-ink, #0f172a);
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.metric-sub {
  font-size: 0.8rem;
  color: var(--color-subtle, #58677a);
}

.streak-card.has-streak {
  border-color: color-mix(in srgb, var(--color-accent) 40%, var(--color-border));
}

.streak-value-group {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.streak-icon {
  font-size: 1.5rem;
}

/* Cockpit Grid */
.cockpit-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr);
  gap: 1.5rem;
  align-items: start;
}

.cockpit-primary-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.cockpit-secondary-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.cockpit-subblock {
  display: flex;
  flex-direction: column;
}

.mobile-only-chips {
  display: none;
}

.mobile-only-tabs {
  display: none;
}

.secondary-tabs-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.secondary-tab-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  flex: 1;
  min-height: 44px;
  min-width: 44px;
  padding: 0.625rem 1rem;
  background: var(--color-surface);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 0.5rem);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.secondary-tab-btn.active {
  background: var(--color-accent);
  color: var(--color-on-accent, #ffffff);
  border-color: var(--color-accent);
  font-weight: 600;
}

.timeline-heatmap-block {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Seção da Linha do Tempo */
.timeline-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.timeline-heading {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-ink, #0f172a);
}

.timeline-sub {
  margin: 0.2rem 0 0 0;
  font-size: 0.88rem;
  color: var(--color-muted, #64748b);
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.4rem 0.85rem;
  background: var(--color-selected-bg, #eaf0ff);
  color: var(--color-selected-text, #163ba6);
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-badge, 4px);
  font-size: 0.85rem;
}

.clear-filter-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  font-weight: 600;
  color: inherit;
  min-height: 44px;
  min-width: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-small, 3px);
  touch-action: manipulation;
}

.clear-filter-btn:hover {
  background: rgba(0, 0, 0, 0.08);
}

.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.timeline-card {
  background: var(--color-surface);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-card, 6px);
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.timeline-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: var(--radius-badge, 4px);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.badge-book {
  background: var(--color-info-bg, #eff4fa);
  color: var(--color-accent, #1d4ed8);
  border: 1px solid var(--color-info-border, #c5d2e3);
}

.badge-study {
  background: color-mix(in srgb, var(--color-accent) 15%, var(--color-surface));
  color: var(--color-accent);
  border: 1px solid color-mix(in srgb, var(--color-accent) 30%, var(--color-surface));
}

.badge-updated {
  background: var(--color-surface-soft, #eaf0f8);
  color: var(--color-subtle, #58677a);
  border: 1px solid var(--color-border, #cbd5e1);
}

.timeline-time {
  font-size: 0.8rem;
  color: var(--color-muted, #64748b);
  font-variant-numeric: tabular-nums;
}

.timeline-item-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-ink, #0f172a);
}

.timeline-item-context {
  margin: 0.2rem 0 0 0;
  font-size: 0.85rem;
  color: var(--color-muted, #475569);
}

.timeline-card-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.25rem;
}

.timeline-link {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-accent);
  text-decoration: none;
  min-height: 44px;
  min-width: 44px;
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-control, 4px);
  touch-action: manipulation;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.timeline-link:hover {
  text-decoration: underline;
  background-color: var(--color-surface-hover);
}

/* Responsividade Mobile e Tablet (FR-014 e FR-015) */
@media (max-width: 1023px) {
  .cockpit-layout {
    display: flex;
    flex-direction: column;
  }

  .desktop-only-col {
    display: none !important;
  }

  .mobile-only-tabs {
    display: flex;
    flex-direction: column;
  }

  .mobile-only-chips {
    display: block;
  }
}

@media (max-width: 768px) {
  .dashboard-header h1 {
    font-size: clamp(1.5rem, 5vw, 2rem);
  }

  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .timeline-card-footer {
    justify-content: stretch;
  }

  .timeline-link {
    width: 100%;
    justify-content: center;
    background-color: var(--color-surface-hover);
  }
}
</style>
