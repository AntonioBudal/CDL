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
  /** `adapter`: estudos revisados, quando a sugestão veio do adaptador do usuário (feature 091-C). */
  engine: { name: string; version: string; sha256: string; adapter?: number | null }
  elapsed_ms: number
  warnings: OrganizeWarning[]
}

export interface OrganizeStatus {
  available: boolean
  reason: 'not_installed' | 'integrity_failed' | null
  version: string | null
}

export type OrganizeErrorCode = 'too_large' | 'empty_text' | 'unavailable' | 'error'

// Registro silencioso do feedback (feature 091-B): contrato de POST /api/studies/{id}/organizer-feedback.

export interface OrganizerSuggestionSegment {
  index: number
  start: number
  end: number
  section: OrganizeSection
  confidence: number
  review: boolean
}

/** O que o organizador sugeriu, como o navegador recebeu; `reverted` quando o leitor voltou ao texto único. */
export interface OrganizerSuggestion {
  engine: { version: string; sha256: string; adapter: number | null }
  outcome: 'saved' | 'reverted'
  text: string
  segments: OrganizerSuggestionSegment[]
  /** Linhas com posição enviadas ao organizador (091-C), para o adaptador realinhar a página. */
  lines?: OrganizeLine[]
}

export interface OrganizerFeedbackRequest {
  origin: 'digitize' | 'import'
  organizer: OrganizerSuggestion | null
}

/** Converte a resposta do organizador no que o registro guarda (sem o texto de cada trecho, que está em `text`). */
export function toSuggestion(
  result: OrganizeResult, text: string, outcome: OrganizerSuggestion['outcome'] = 'saved', lines?: OrganizeLine[] | null,
): OrganizerSuggestion {
  const suggestion: OrganizerSuggestion = {
    engine: { version: result.engine.version, sha256: result.engine.sha256, adapter: result.engine.adapter ?? null },
    outcome,
    text,
    segments: result.segments.map(({ index, start, end, section, confidence, review }) => ({ index, start, end, section, confidence, review })),
  }
  if (lines && lines.length) suggestion.lines = lines
  return suggestion
}
