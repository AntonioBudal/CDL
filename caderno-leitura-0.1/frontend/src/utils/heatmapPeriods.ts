// F0.12.10 (spec 123): períodos do calendário do Painel. A API aceita de 30 a 730 dias; "ano passado" pede 730 (que
// cobrem o ano anterior inteiro) e filtra as datas na tela, sem mudar o servidor.
import type { HeatmapPoint } from '../types'

export type HeatmapPeriodId = '1m' | '3m' | '6m' | '12m' | 'last-year'

export interface HeatmapPeriod {
  id: HeatmapPeriodId
  days: number
  label: string
}

export const HEATMAP_PERIODS: HeatmapPeriod[] = [
  { id: '1m', days: 30, label: '1 mês' },
  { id: '3m', days: 91, label: '3 meses' },
  { id: '6m', days: 182, label: '6 meses' },
  { id: '12m', days: 365, label: '12 meses' },
  { id: 'last-year', days: 730, label: 'Ano passado' },
]

export const DEFAULT_PERIOD: HeatmapPeriodId = '12m'
export const PERIOD_STORAGE_KEY = 'leitorum_heatmap_period'

export function isPeriodId(value: unknown): value is HeatmapPeriodId {
  return HEATMAP_PERIODS.some((p) => p.id === value)
}

export function periodDays(id: string): number {
  return HEATMAP_PERIODS.find((p) => p.id === id)?.days ?? 365
}

/** Rótulo do período para o subtítulo: "Ano passado (2025)" mostra o ano. */
export function periodLabel(id: string, today: Date = new Date()): string {
  if (id === 'last-year') return `Ano passado (${today.getFullYear() - 1})`
  return HEATMAP_PERIODS.find((p) => p.id === id)?.label ?? '12 meses'
}

/** Só o ano anterior inteiro em "ano passado"; os outros períodos já vêm cortados pela API. */
export function pointsForPeriod(points: HeatmapPoint[], id: string, today: Date = new Date()): HeatmapPoint[] {
  if (id !== 'last-year') return points
  const year = String(today.getFullYear() - 1)
  return points.filter((p) => p.date.startsWith(`${year}-`))
}
