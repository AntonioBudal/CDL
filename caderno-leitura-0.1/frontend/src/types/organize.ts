// Organizar nas 4 seções (feature 089): contrato de /api/imports/organize.

export type OrganizeSection = 'summary' | 'explanation' | 'concepts' | 'references'

export const ORGANIZE_SECTIONS: readonly { key: OrganizeSection; label: string }[] = [
  { key: 'summary', label: 'Resumo' },
  { key: 'explanation', label: 'Explicação' },
  { key: 'concepts', label: 'Conceitos' },
  { key: 'references', label: 'Referências' },
] as const

export interface OrganizeLine {
  text: string
  bbox: number[] | null
  confidence: number | null
}

export interface OrganizeRequest {
  text: string
  lines?: OrganizeLine[]
}

export interface OrganizeSegment {
  index: number
  start: number
  end: number
  /** Texto do trecho, igual ao recebido; o cliente nunca recorta por posição. */
  text: string
  section: OrganizeSection
  confidence: number
  review: boolean
}

export interface OrganizeWarning {
  code: 'suggestion' | 'single_section'
  message: string
}

export interface OrganizeResult {
  sections: Record<OrganizeSection, string>
  segments: OrganizeSegment[]
  explicit_headings: boolean
  review_count: number
  engine: { name: string; version: string; sha256: string }
  elapsed_ms: number
  warnings: OrganizeWarning[]
}

export interface OrganizeStatus {
  available: boolean
  reason: 'not_installed' | 'integrity_failed' | null
  version: string | null
}

export type OrganizeErrorCode = 'too_large' | 'empty_text' | 'unavailable' | 'error'
