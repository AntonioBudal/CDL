// Digitalizar Caderno (feature 086): contrato de /api/digitize e constantes da tela.

export type DigitizeUnavailableReason = 'not_installed' | 'integrity_failed'

export interface DigitizeStatus {
  available: boolean
  reason: DigitizeUnavailableReason | null
}

export interface DigitizeLine {
  index: number
  text: string
  confidence: number
  low_confidence: boolean
  /** Caixa [x0, y0, x1, y1] da linha na imagem (feature 089); usada pela organização nas 4 seções. */
  bbox?: number[] | null
}

export interface DigitizeWarning {
  code: 'draft' | 'no_text' | 'many_uncertain'
  message: string
}

export interface DigitizeEngine {
  name: string
  version: string
  reader: string
  license_status: string
}

export interface DigitizePreview {
  text: string
  lines: DigitizeLine[]
  low_confidence_count: number
  warnings: DigitizeWarning[]
  engine: DigitizeEngine
  elapsed_ms: number
}

export type DigitizeErrorCode =
  | 'too_large'
  | 'unsupported_format'
  | 'invalid_image'
  | 'unavailable'
  | 'busy'
  | 'low_memory'
  | 'timeout'
  | 'engine_failed'
  | 'save_failed'
  | 'error'

export type DigitizeSection = 'summary' | 'explanation' | 'concepts' | 'references'

export const DIGITIZE_SECTIONS: readonly { key: DigitizeSection; label: string }[] = [
  { key: 'summary', label: 'Resumo' },
  { key: 'explanation', label: 'Explicação' },
  { key: 'concepts', label: 'Conceitos' },
  { key: 'references', label: 'Referências' },
] as const

export const DIGITIZE_DEFAULT_SECTION: DigitizeSection = 'summary'

export const DIGITIZE_ACCEPT = 'image/jpeg,image/png,image/webp'
export const DIGITIZE_ACCEPTED_TYPES: readonly string[] = ['image/jpeg', 'image/png', 'image/webp']
export const DIGITIZE_MAX_BYTES = 20 * 1024 * 1024

export interface ExitShortcut {
  title: string
  description: string
  routePath: string
  actionLabel: string
}

export const DIGITIZE_EXIT_SHORTCUTS: readonly ExitShortcut[] = [
  {
    title: 'Importar fichamento digitado',
    description: 'Cole trechos copiados do seu leitor de e-books ou digite anotações no Ateliê de Fichamento.',
    routePath: '/importar',
    actionLabel: 'Abrir Ateliê de Fichamento',
  },
  {
    title: 'Anotar na Caixa de Entrada',
    description: 'Despeje ideias rápidas, citações soltas ou pensamentos sem necessidade de classificação prévia.',
    routePath: '/inbox',
    actionLabel: 'Ir para Caixa de Entrada',
  },
] as const
