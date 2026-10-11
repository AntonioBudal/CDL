/**
 * Tipos e modelos auxiliares da Lixeira — Arquivo de Salvaguarda e Segurança
 * Feature 08 (073-lixeira-arquivo-salvaguarda)
 */

export type TrashItemType = 'book' | 'study'

export interface SelectedTrashItemKey {
  type: TrashItemType
  id: number
}

export type SelectedItemKeyString = `${TrashItemType}-${number}`

export interface RetentionMetrics {
  daysRemaining: number
  totalRetentionDays: number
  elapsedPercentage: number
  isUrgent: boolean
  urgencyLabel: string
}

export interface BatchActionProgress {
  isActive: boolean
  totalCount: number
  completedCount: number
  currentAction: 'restoring' | 'deleting' | null
  errors: string[]
}

/**
 * Converte um par (tipo, id) em uma string de chave de seleção estável.
 */
export function toTrashKey(type: TrashItemType, id: number): SelectedItemKeyString {
  return `${type}-${id}`
}

/**
 * Analisa uma string de chave de seleção no par original (tipo, id).
 */
export function parseTrashKey(key: SelectedItemKeyString): SelectedTrashItemKey {
  const [type, idStr] = key.split('-') as [TrashItemType, string]
  return {
    type,
    id: Number(idStr),
  }
}

/**
 * Calcula as métricas de retenção temporal baseando-se no prazo de custódia de 30 dias.
 */
export function calculateRetention(daysRemaining: number, totalDays = 30): RetentionMetrics {
  const safeDays = Math.max(0, Math.min(totalDays, Math.round(daysRemaining)))
  const elapsed = totalDays - safeDays
  const elapsedPercentage = Math.max(0, Math.min(100, Math.round((elapsed / totalDays) * 100)))
  const isUrgent = safeDays <= 5
  const urgencyLabel = safeDays === 1 ? 'Expurgo em 1 dia' : `Expurgo em ${safeDays} dias`

  return {
    daysRemaining: safeDays,
    totalRetentionDays: totalDays,
    elapsedPercentage,
    isUrgent,
    urgencyLabel,
  }
}
