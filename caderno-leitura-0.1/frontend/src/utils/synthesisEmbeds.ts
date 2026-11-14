/**
 * F0.11.11 (spec 113): marcas de transclusão dos cadernos de síntese (mesmo analisador do servidor).
 *
 * Cada marca fica sozinha na linha, fora de bloco de código:
 * `![[Título|id]]` (estudo inteiro), `![[Título|id#resumo]]` (seção) e `![[destaque:123]]` (destaque).
 */

export const SECTION_SLUGS = {
  resumo: { key: 'summary', label: 'Resumo' },
  explicacao: { key: 'explanation', label: 'Explicação' },
  conceitos: { key: 'concepts', label: 'Conceitos' },
  referencias: { key: 'references', label: 'Referências' },
} as const

export type SectionSlug = keyof typeof SECTION_SLUGS

export interface EmbedRef {
  key: string
  kind: 'study' | 'section' | 'highlight'
  id: number
  section?: SectionSlug
  title?: string
}

export type BodySegment =
  | { type: 'text'; text: string }
  | { type: 'embed'; text: string; embed: EmbedRef }
  | { type: 'invalid'; text: string }

const EMBED_LINE = /^\s*!\[\[(.+?)\]\]\s*$/
const HIGHLIGHT_TARGET = /^\s*destaque\s*:\s*(\d+)\s*$/i
const STUDY_TARGET = /^(.+)\|\s*(\d+)\s*(?:#\s*([a-z]+))?\s*$/i
const FENCE = /^\s*(```|~~~)/

export function parseEmbed(inner: string): EmbedRef | null {
  const highlight = HIGHLIGHT_TARGET.exec(inner)
  if (highlight) {
    const id = Number(highlight[1])
    return id > 0 ? { key: `highlight:${id}`, kind: 'highlight', id } : null
  }
  const study = STUDY_TARGET.exec(inner)
  if (!study) return null
  const id = Number(study[2])
  if (!(id > 0)) return null
  const title = study[1]!.trim()
  const section = study[3]?.toLowerCase()
  if (section !== undefined) {
    if (!(section in SECTION_SLUGS)) return null
    return { key: `study:${id}#${section}`, kind: 'section', id, section: section as SectionSlug, title }
  }
  return { key: `study:${id}`, kind: 'study', id, title }
}

export function splitBody(body: string): BodySegment[] {
  const segments: BodySegment[] = []
  const buffer: string[] = []
  let inFence = false
  const flush = () => {
    if (buffer.length) {
      segments.push({ type: 'text', text: buffer.join('\n') })
      buffer.length = 0
    }
  }
  for (const line of (body || '').split('\n')) {
    if (FENCE.test(line)) {
      inFence = !inFence
      buffer.push(line)
      continue
    }
    if (inFence || !line.includes('![[')) {
      buffer.push(line)
      continue
    }
    const match = EMBED_LINE.exec(line)
    const embed = match ? parseEmbed(match[1]!) : null
    flush()
    segments.push(embed ? { type: 'embed', text: line, embed } : { type: 'invalid', text: line })
  }
  flush()
  return segments
}

/** Marca pronta para inserir (o título é só para quem lê o texto cru; `|` e `]` viram espaço). */
export function embedToken(kind: 'study' | 'section' | 'highlight', id: number, title = '', section?: SectionSlug): string {
  if (kind === 'highlight') return `![[destaque:${id}]]`
  const clean = (title || 'Estudo').replace(/[|\]\[\n]+/g, ' ').replace(/\s+/g, ' ').trim() || 'Estudo'
  return section ? `![[${clean}|${id}#${section}]]` : `![[${clean}|${id}]]`
}

/** Insere a marca numa linha própria na posição do cursor. */
export function insertOnOwnLine(body: string, position: number, token: string): { body: string; cursor: number } {
  const at = Math.max(0, Math.min(position, body.length))
  const before = body.slice(0, at)
  const after = body.slice(at)
  const lead = before === '' || before.endsWith('\n') ? '' : '\n'
  const trail = after === '' || after.startsWith('\n') ? '' : '\n'
  const inserted = `${lead}${token}${trail}`
  return { body: before + inserted + after, cursor: before.length + lead.length + token.length }
}
