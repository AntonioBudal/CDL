import { computed, reactive } from 'vue'
import { ApiError, errorMessage } from '../services/api.ts'
import { ORGANIZE_SECTIONS, toSuggestion } from '../types/organize.ts'
import type {
  OrganizeErrorCode,
  OrganizeLine,
  OrganizerSuggestion,
  OrganizeRequest,
  OrganizeResult,
  OrganizeSection,
  OrganizeWarning,
} from '../types/organize.ts'

// Organizar nas 4 seções (feature 089): sugestão revisável; nada é reescrito, só trechos movidos.

interface OrganizeGateway {
  organize: (payload: OrganizeRequest, signal?: AbortSignal) => Promise<OrganizeResult>
}

export type OrganizedSections = Record<OrganizeSection, string>

export interface OrganizeReviewItem {
  index: number
  text: string
  section: OrganizeSection
  /** O trecho ainda aparece igual no editor da seção atual; senão, "já editado". */
  movable: boolean
}

interface Segment {
  index: number
  text: string
  review: boolean
}

const KEYS = ORGANIZE_SECTIONS.map(item => item.key)
const empty = (): OrganizedSections => ({ summary: '', explanation: '', concepts: '', references: '' })

function errorCode(error: unknown): OrganizeErrorCode {
  if (error instanceof ApiError && typeof error.data === 'object' && error.data !== null && 'code' in error.data) {
    return String((error.data as { code: unknown }).code) as OrganizeErrorCode
  }
  return 'error'
}

function removeOnce(content: string, piece: string): string {
  const at = content.indexOf(piece)
  if (at < 0) return content
  const end = at + piece.length
  if (content[end] === '\n') return content.slice(0, at) + content.slice(end + 1)
  if (at > 0 && content[at - 1] === '\n') return content.slice(0, at - 1) + content.slice(end)
  return content.slice(0, at) + content.slice(end)
}

export function useSectionOrganizer(gateway: OrganizeGateway) {
  const state = reactive({
    active: false,
    loading: false,
    snapshot: '',
    segments: [] as Segment[],
    assignment: [] as OrganizeSection[],
    sections: empty(),
    built: empty(),
    warnings: [] as OrganizeWarning[],
    explicitHeadings: false,
    error: null as { code: OrganizeErrorCode; message: string } | null,
  })
  let controller: AbortController | null = null
  // Para o registro silencioso do feedback (feature 091-B): a resposta da última organização e, se o leitor voltou
  // ao texto único, a sugestão marcada como revertida.
  let lastResult: OrganizeResult | null = null
  let lastLines: OrganizeLine[] | null = null
  let reverted: OrganizerSuggestion | null = null

  const edited = computed(() => state.active && KEYS.some(k => state.sections[k] !== state.built[k]))
  const hasText = computed(() => KEYS.some(k => state.sections[k].trim() !== ''))
  const reviewItems = computed<OrganizeReviewItem[]>(() => state.segments
    .map((segment, i) => ({ segment, section: state.assignment[i]! }))
    .filter(({ segment }) => segment.review)
    .map(({ segment, section }) => ({
      index: segment.index,
      text: segment.text,
      section,
      movable: state.sections[section].includes(segment.text),
    })))
  const reviewCounts = computed(() => {
    const counts = { summary: 0, explanation: 0, concepts: 0, references: 0 } as Record<OrganizeSection, number>
    for (const item of reviewItems.value) counts[item.section] += 1
    return counts
  })

  function build(section: OrganizeSection): string {
    return state.segments.filter((_, i) => state.assignment[i] === section).map(s => s.text).join('\n')
  }

  async function organize(text: string, lines?: OrganizeLine[] | null): Promise<boolean> {
    if (state.loading) return false
    if (!text.trim()) {
      state.error = { code: 'empty_text', message: 'Não há texto para organizar.' }
      return false
    }
    const current = new AbortController()
    controller = current
    state.loading = true
    state.error = null
    try {
      const payload: OrganizeRequest = lines && lines.length ? { text, lines } : { text }
      const result = await gateway.organize(payload, current.signal)
      if (current.signal.aborted) return false
      state.snapshot = text
      lastResult = result
      lastLines = lines && lines.length ? lines : null
      reverted = null
      state.segments = result.segments.map(s => ({ index: s.index, text: s.text, review: s.review }))
      state.assignment = result.segments.map(s => s.section)
      for (const k of KEYS) {
        state.built[k] = build(k)
        state.sections[k] = state.built[k]
      }
      state.warnings = result.warnings
      state.explicitHeadings = result.explicit_headings
      state.active = true
      return true
    } catch (error) {
      if (current.signal.aborted) return false
      state.error = { code: errorCode(error), message: errorMessage(error) }
      return false
    } finally {
      if (controller === current) {
        controller = null
        state.loading = false
      }
    }
  }

  function cancel() {
    controller?.abort()
    controller = null
    state.loading = false
  }

  /** Move um trecho para outra seção; devolve false se o trecho já foi editado no editor de origem. */
  function move(index: number, target: OrganizeSection): boolean {
    const i = state.segments.findIndex(s => s.index === index)
    if (i < 0) return false
    const source = state.assignment[i]!
    const piece = state.segments[i]!.text
    if (source === target || !state.sections[source].includes(piece)) return false
    const sourceIntact = state.sections[source] === state.built[source]
    const targetIntact = state.sections[target] === state.built[target]
    state.assignment[i] = target
    if (sourceIntact) {
      state.built[source] = build(source)
      state.sections[source] = state.built[source]
    } else {
      state.sections[source] = removeOnce(state.sections[source], piece)
    }
    if (targetIntact) {
      state.built[target] = build(target)
      state.sections[target] = state.built[target]
    } else {
      state.sections[target] = state.sections[target] ? `${state.sections[target]}\n${piece}` : piece
    }
    return true
  }

  /** A sugestão do organizador para o registro do feedback; `null` se o leitor nunca organizou. */
  function suggestion(): OrganizerSuggestion | null {
    if (state.active && lastResult) return toSuggestion(lastResult, state.snapshot, 'saved', lastLines)
    return reverted
  }

  /** Sai do modo organizado e devolve o texto exato de antes de organizar. */
  function revert(): string {
    const text = state.snapshot
    const kept = state.active && lastResult ? toSuggestion(lastResult, text, 'reverted', lastLines) : null
    reset()
    reverted = kept
    return text
  }

  function reset() {
    cancel()
    lastResult = null
    lastLines = null
    reverted = null
    Object.assign(state, {
      active: false, snapshot: '', segments: [], assignment: [], sections: empty(), built: empty(),
      warnings: [], explicitHeadings: false, error: null,
    })
  }

  return { state, edited, hasText, reviewItems, reviewCounts, organize, cancel, move, revert, reset, suggestion }
}
