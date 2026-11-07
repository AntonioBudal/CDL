/**
 * Desafio F12 (F0.10.08, spec 101): utilidades puras para mostrar ao visitante, no próprio navegador,
 * quais endereços a página contatou e qual política de segurança (CSP) o servidor enviou.
 */

export interface AuditEntry {
  name: string
}

export interface OriginGroup {
  origin: string
  sameOrigin: boolean
  count: number
}

function originOf(url: string): string | null {
  if (!url || /^(data|blob|about|javascript):/i.test(url)) return null
  try {
    return new URL(url).origin
  } catch {
    return null
  }
}

/**
 * Agrupa entradas de `performance.getEntriesByType('navigation' | 'resource')` por origem.
 * Ignora `data:`, `blob:` e `about:`. A origem da página vem primeiro; as demais, por ordem alfabética.
 */
export function groupEntriesByOrigin(entries: AuditEntry[], pageOrigin: string): OriginGroup[] {
  const counts = new Map<string, number>()
  for (const entry of entries) {
    const origin = originOf(entry.name)
    if (!origin) continue
    counts.set(origin, (counts.get(origin) || 0) + 1)
  }
  return [...counts.entries()]
    .map(([origin, count]) => ({ origin, count, sameOrigin: origin === pageOrigin }))
    .sort((a, b) => Number(b.sameOrigin) - Number(a.sameOrigin) || a.origin.localeCompare(b.origin))
}

export function externalOrigins(groups: OriginGroup[]): OriginGroup[] {
  return groups.filter((group) => !group.sameOrigin)
}

export interface CspSummary {
  present: boolean
  directives: Record<string, string>
}

const SHOWN_DIRECTIVES = ['default-src', 'connect-src', 'script-src', 'img-src', 'frame-ancestors'] as const

/** Lê o cabeçalho Content-Security-Policy e devolve as diretivas mostradas na página. */
export function summarizeCsp(header: string | null | undefined): CspSummary {
  const text = (header || '').trim()
  if (!text) return { present: false, directives: {} }
  const directives: Record<string, string> = {}
  for (const part of text.split(';')) {
    const [name = '', ...values] = part.trim().split(/\s+/)
    const key = name.toLowerCase()
    if ((SHOWN_DIRECTIVES as readonly string[]).includes(key)) directives[key] = values.join(' ')
  }
  return { present: true, directives }
}
