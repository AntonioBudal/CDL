<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import type { HeatmapPoint } from '../types'

const props = defineProps<{
  points: HeatmapPoint[]
  selectedDate: string | null
}>()

const emit = defineEmits<{
  (e: 'select-date', date: string | null): void
}>()

const mobileExpanded = ref(false)
const scrollAreaRef = ref<HTMLElement | null>(null)

function scrollToRecent(): void {
  nextTick(() => {
    if (typeof window !== 'undefined' && window.innerWidth < 768 && scrollAreaRef.value) {
      const el = scrollAreaRef.value
      el.scrollTo({
        left: el.scrollWidth - el.clientWidth,
        behavior: 'smooth'
      })
    }
  })
}

onMounted(() => {
  scrollToRecent()
})

watch(() => props.points, () => {
  scrollToRecent()
})

const MONTH_NAMES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
const DAY_LABELS = [
  { label: '', index: 0 },
  { label: 'Seg', index: 1 },
  { label: '', index: 2 },
  { label: 'Qua', index: 3 },
  { label: '', index: 4 },
  { label: 'Sex', index: 5 },
  { label: '', index: 6 },
]

function getDayOfWeek(dateStr: string): number {
  const [y, m, d] = dateStr.split('-').map(Number)
  return new Date(y, m - 1, d).getDay()
}

interface CalendarWeek {
  days: (HeatmapPoint | null)[]
  monthLabel?: string
}

// Recorte adaptativo: no mobile compacto exibe cerca de 17 semanas (~120 dias)
const activePoints = computed(() => {
  if (!props.points || props.points.length === 0) return []
  if (!mobileExpanded.value) {
    // Por padrão no mobile mostramos os últimos 120 dias (~4 meses)
    // No desktop via CSS o container mostra todas as colunas
    return props.points
  }
  return props.points
})

const weeks = computed<CalendarWeek[]>(() => {
  const pts = activePoints.value
  if (pts.length === 0) return []

  const result: CalendarWeek[] = []
  let currentWeek: (HeatmapPoint | null)[] = []
  let currentMonth = -1

  // Preenche dias antes do início do primeiro dia da série
  const firstDayOfWeek = getDayOfWeek(pts[0].date)
  for (let i = 0; i < firstDayOfWeek; i++) {
    currentWeek.push(null)
  }

  for (const pt of pts) {
    currentWeek.push(pt)
    if (currentWeek.length === 7) {
      // Verifica se houve troca de mês nesta semana
      let monthLabel: string | undefined
      for (const d of currentWeek) {
        if (d) {
          const [, m, dayNum] = d.date.split('-').map(Number)
          const monthIdx = m - 1
          if (monthIdx !== currentMonth && dayNum <= 7) {
            currentMonth = monthIdx
            monthLabel = MONTH_NAMES[monthIdx]
            break
          }
        }
      }
      result.push({ days: currentWeek, monthLabel })
      currentWeek = []
    }
  }

  // Completa a última semana com nulos se necessário
  if (currentWeek.length > 0) {
    let monthLabel: string | undefined
    for (const d of currentWeek) {
      if (d) {
        const [, m, dayNum] = d.date.split('-').map(Number)
        const monthIdx = m - 1
        if (monthIdx !== currentMonth && dayNum <= 7) {
          currentMonth = monthIdx
          monthLabel = MONTH_NAMES[monthIdx]
          break
        }
      }
    }
    while (currentWeek.length < 7) {
      currentWeek.push(null)
    }
    result.push({ days: currentWeek, monthLabel })
  }

  return result
})

function formatTooltip(point: HeatmapPoint): string {
  const [y, m, d] = point.date.split('-').map(Number)
  const formatted = `${String(d).padStart(2, '0')}/${String(m).padStart(2, '0')}/${y}`
  if (point.count === 0) return `${formatted}: Nenhuma atividade`
  const label = point.count === 1 ? 'atividade' : 'atividades'
  return `${formatted}: ${point.count} ${label}`
}

function handleCellClick(point: HeatmapPoint) {
  if (props.selectedDate === point.date) {
    emit('select-date', null)
  } else {
    emit('select-date', point.date)
  }
}
</script>

<template>
  <div class="heatmap-card" :class="{ 'mobile-expanded': mobileExpanded }">
    <div class="heatmap-header">
      <div class="heatmap-title-group">
        <h3 class="heatmap-heading">Frequência em Calendário</h3>
        <p class="heatmap-sub">Últimos 12 meses de atividades diárias</p>
      </div>
      <button
        type="button"
        class="secondary mobile-toggle-btn"
        @click="mobileExpanded = !mobileExpanded"
      >
        {{ mobileExpanded ? 'Ver período compacto' : 'Ver ano completo' }}
      </button>
    </div>

    <div ref="scrollAreaRef" class="heatmap-scroll-area">
      <div class="heatmap-grid-wrapper">
        <!-- Rótulos dos dias da semana -->
        <div class="day-labels" aria-hidden="true">
          <span
            v-for="(day, idx) in DAY_LABELS"
            :key="idx"
            class="day-label"
          >
            {{ day.label }}
          </span>
        </div>

        <!-- Grade de semanas -->
        <div class="weeks-container" role="grid" aria-label="Mapa de calor de atividades de leitura">
          <div
            v-for="(week, wIdx) in weeks"
            :key="wIdx"
            class="week-column"
            role="row"
          >
            <!-- Rótulo do mês no topo da semana -->
            <span class="month-label" aria-hidden="true">
              {{ week.monthLabel || '' }}
            </span>

            <div class="days-column">
              <template v-for="(day, dIdx) in week.days" :key="dIdx">
                <button
                  v-if="day"
                  type="button"
                  class="heatmap-cell"
                  :class="[
                    `level-${day.level}`,
                    { selected: selectedDate === day.date }
                  ]"
                  :title="formatTooltip(day)"
                  :aria-label="formatTooltip(day)"
                  :aria-pressed="selectedDate === day.date"
                  role="gridcell"
                  @click="handleCellClick(day)"
                />
                <span
                  v-else
                  class="heatmap-cell empty-cell"
                  aria-hidden="true"
                />
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Legenda de intensidade -->
    <div class="heatmap-legend" aria-label="Legenda de intensidade">
      <span class="legend-text">Menos</span>
      <span class="legend-cell level-0" title="Sem atividade" />
      <span class="legend-cell level-1" title="1 atividade" />
      <span class="legend-cell level-2" title="2 a 3 atividades" />
      <span class="legend-cell level-3" title="4 ou mais atividades" />
      <span class="legend-text">Mais</span>
    </div>
  </div>
</template>

<style scoped>
.heatmap-card {
  background: var(--color-surface);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-panel, 8px);
  padding: 1.25rem 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.heatmap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.heatmap-heading {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-ink, #0f172a);
}

.heatmap-sub {
  margin: 0.2rem 0 0 0;
  font-size: 0.85rem;
  color: var(--color-muted, #64748b);
}

.mobile-toggle-btn {
  display: none;
  font-size: 0.8rem;
  padding: 0.35rem 0.75rem;
}

@media (max-width: 768px) {
  .mobile-toggle-btn {
    display: inline-flex;
  }
}

.heatmap-scroll-area {
  overflow-x: auto;
  padding-bottom: 0.5rem;
  -webkit-overflow-scrolling: touch;
}

.heatmap-grid-wrapper {
  display: inline-flex;
  gap: 0.4rem;
  min-width: max-content;
}

.day-labels {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-top: 1.3rem; /* Espaço alinhado ao rótulo do mês */
  user-select: none;
}

.day-label {
  height: 14px;
  line-height: 14px;
  font-size: 0.68rem;
  color: var(--color-muted, #64748b);
  width: 24px;
  text-align: right;
  padding-right: 4px;
}

.weeks-container {
  display: flex;
  gap: 3px;
}

.week-column {
  display: flex;
  flex-direction: column;
  width: 14px;
}

.month-label {
  height: 1.1rem;
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--color-muted, #64748b);
  overflow: visible;
  white-space: nowrap;
}

.days-column {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.heatmap-cell {
  width: 14px;
  height: 14px;
  padding: 0;
  margin: 0;
  border-radius: var(--radius-small, 3px);
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: transform 0.12s ease, outline-color 0.12s ease;
  box-sizing: border-box;
}

.heatmap-cell:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
  z-index: 3;
}

.heatmap-cell:hover {
  transform: scale(1.25);
  z-index: 2;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.heatmap-cell.selected {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
  z-index: 3;
}

.empty-cell {
  background: transparent;
  border-color: transparent;
  cursor: default;
  pointer-events: none;
}

/* Tokens semânticos de contraste para células do heatmap */
:root {
  --heatmap-cell-empty-bg: var(--color-surface-soft, #f1f5f9);
  --heatmap-cell-empty-border: var(--color-border-divider, #e2e8f0);
  --heatmap-cell-empty-opacity: 0.6;
}

:root:is([data-theme='breu'], [data-theme='vinil'], [data-theme='vespera'], [data-theme='fiorde'], [data-theme='dark']) {
  --heatmap-cell-empty-bg: rgba(255, 255, 255, 0.04);
  --heatmap-cell-empty-border: rgba(255, 255, 255, 0.08);
  --heatmap-cell-empty-opacity: 0.45;
}

:root:is([data-theme='pergaminho'], [data-theme='sequoia'], [data-theme='sepia']) {
  --heatmap-cell-empty-bg: rgba(60, 40, 20, 0.06);
  --heatmap-cell-empty-border: rgba(60, 40, 20, 0.14);
  --heatmap-cell-empty-opacity: 0.5;
}

:root:is([data-theme='solario'], [data-theme='voltagem'], [data-theme='solarized']) {
  --heatmap-cell-empty-bg: rgba(0, 43, 54, 0.08);
  --heatmap-cell-empty-border: rgba(0, 43, 54, 0.16);
  --heatmap-cell-empty-opacity: 0.55;
}

:root[data-theme='e-ink'] {
  --heatmap-cell-empty-bg: #ffffff;
  --heatmap-cell-empty-border: #9ca3af;
  --heatmap-cell-empty-opacity: 0.5;
}

/* Níveis de intensidade com contraste e opacidade calibrados */
.level-0 {
  background: var(--heatmap-cell-empty-bg, var(--color-surface-soft, #f1f5f9));
  border-color: var(--heatmap-cell-empty-border, var(--color-border-divider, #e2e8f0));
  opacity: var(--heatmap-cell-empty-opacity, 0.6);
}

.level-1,
.level-2,
.level-3 {
  opacity: 1;
}

.level-1 {
  background: color-mix(in srgb, var(--color-accent, #1d4ed8) 35%, var(--color-surface, #ffffff));
  border-color: color-mix(in srgb, var(--color-accent, #1d4ed8) 50%, transparent);
}

.level-2 {
  background: color-mix(in srgb, var(--color-accent, #1d4ed8) 70%, var(--color-surface, #ffffff));
  border-color: color-mix(in srgb, var(--color-accent, #1d4ed8) 80%, transparent);
}

.level-3 {
  background: var(--color-accent, #1d4ed8);
  border-color: var(--color-accent, #1d4ed8);
  box-shadow: 0 0 2px color-mix(in srgb, var(--color-accent, #1d4ed8) 50%, transparent);
}

/* Modo monocromático estrito para tema E-Ink */
:root[data-theme="e-ink"] .level-0 {
  background: #ffffff;
  border-color: #9ca3af;
  border-style: dashed;
  opacity: 0.5;
}
:root[data-theme="e-ink"] .level-1 {
  background: #d1d5db;
  border-color: #000000;
  border-style: solid;
  opacity: 1;
}
:root[data-theme="e-ink"] .level-2 {
  background: #6b7280;
  border-color: #000000;
  border-style: solid;
  opacity: 1;
}
:root[data-theme="e-ink"] .level-3 {
  background: #000000;
  border-color: #000000;
  border-style: solid;
  opacity: 1;
}

.heatmap-legend {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  margin-top: 1rem;
  font-size: 0.75rem;
  color: var(--color-muted, #64748b);
}

.legend-text {
  margin: 0 4px;
}

.legend-cell {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: var(--radius-small, 2px);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

@media (max-width: 768px) {
  .heatmap-cell {
    width: 17px;
    height: 17px;
  }
  .week-column {
    width: 17px;
  }
  .day-label {
    height: 17px;
    line-height: 17px;
  }
}
</style>
