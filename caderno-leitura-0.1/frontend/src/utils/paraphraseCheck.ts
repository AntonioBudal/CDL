/**
 * F0.11.07 (spec 109): validador de paráfrase.
 *
 * Compara cada frase do leitor (Resumo, Explicação, Conceitos) com o texto da fonte usando Jaccard de trigramas de
 * palavras e a maior sequência de palavras idênticas. A fonte é texto do livro guardado pelo leitor (capturas e
 * citações literais de outros estudos); trechos entre aspas, em `>` ou marcados como citação literal ficam de fora. Medida só lexical, de propósito: não entende sinônimos.
 * Tudo roda no navegador; nada é enviado a lugar nenhum.
 */
import { abntAuthorCall } from './citationFormatter.ts'

export const COPY_THRESHOLD = 0.5
export const CLOSE_THRESHOLD = 0.25
export const COPY_RUN = 12
export const MIN_WORDS = 6
/** Janelas de 1 a 3 frases da fonte: o leitor costuma fundir frases. */
const MAX_WINDOW = 3
const MAX_CANDIDATES = 24
const MAX_EXCERPT = 600

export type ParaphraseSectionKey = 'summary' | 'explanation' | 'concepts'
export type ParaphraseLevel = 'copy' | 'close'

export const PARAPHRASE_SECTIONS: { key: ParaphraseSectionKey; label: string }[] = [
  { key: 'summary', label: 'Resumo' },
  { key: 'explanation', label: 'Explicação' },
  { key: 'concepts', label: 'Conceitos' },
]

export interface ParaphraseSourceInput {
  label: string
  text: string
}

export interface TextPart {
  text: string
  shared: boolean
}

export interface ParaphraseFlag {
  section: ParaphraseSectionKey
  /** Frase como está no editor (com Markdown), para "Marcar como citação". */
  sentence: string
  level: ParaphraseLevel
  /** Jaccard de trigramas, de 0 a 1. */
  score: number
  /** Maior sequência de palavras idênticas à fonte. */
  run: number
  sourceLabel: string
  sentenceParts: TextPart[]
  sourceParts: TextPart[]
}

/** Trecho marcado como citação literal neste estudo: a frase que o contém não é verificada. */
export interface DeclaredQuote {
  section: string
  text: string
}

export interface ParaphraseResult {
  flagged: ParaphraseFlag[]
  /** Frases verificadas (com pelo menos MIN_WORDS palavras fora de aspas). */
  total: number
  copies: number
}

interface SourceSentence {
  source: number
  label: string
  text: string
  words: string[]
  grams: Set<string>
}

export interface SourceIndex {
  sentences: SourceSentence[]
  postings: Map<string, number[]>
}

// ---------------------------------------------------------------- normalização

export function normalizeWords(text: string): string[] {
  return text
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim()
    .split(' ')
    .filter(Boolean)
}

/** Tira a marcação Markdown que não é texto (menções, links, ênfase, títulos, marcadores). */
export function stripMarkdown(text: string): string {
  return text
    .replace(/\[\[conceito:\s*([^\]|]*?)\s*\]\]/gi, '$1')
    .replace(/\[\[([^\]|]+)(?:\|[^\]]*)?\]\]/g, '$1')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/^\s{0,3}#{1,6}\s+/gm, '')
    .replace(/^\s*(?:[-*+]|\d+[.)])\s+/gm, '')
    .replace(/[*_`~]+/g, '')
}

const QUOTED = /"[^"\n]*"|“[^”\n]*”|«[^»\n]*»/g

/** Retira os trechos entre aspas: são citação direta assumida. */
export function withoutDeclaredQuotes(text: string): string {
  return text.replace(QUOTED, ' ')
}

/**
 * Frases de uma seção como trechos do texto original (para poder substituí-las depois). Linhas de bloco de
 * citação (`> …`) e de código ficam de fora.
 */
export function splitSentences(text: string): string[] {
  const out: string[] = []
  let inFence = false
  for (const line of (text || '').split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) { inFence = !inFence; continue }
    if (inFence || /^\s*>/.test(line) || !line.trim()) continue
    // Corta depois de . ! ? … seguidos de espaço, sem cortar dentro de aspas.
    let start = 0
    let quote: string | null = null
    for (let i = 0; i < line.length; i += 1) {
      const ch = line[i]!
      if (quote) {
        if ((quote === '"' && ch === '"') || (quote === '“' && ch === '”') || (quote === '«' && ch === '»')) quote = null
        continue
      }
      if (ch === '"' || ch === '“' || ch === '«') { quote = ch; continue }
      if (/[.!?…]/.test(ch) && (i + 1 >= line.length || /\s/.test(line[i + 1]!))) {
        const piece = line.slice(start, i + 1).trim()
        if (piece) out.push(piece)
        start = i + 1
      }
    }
    const rest = line.slice(start).trim()
    if (rest) out.push(rest)
  }
  return out
}

export function trigrams(words: string[]): Set<string> {
  const grams = new Set<string>()
  for (let i = 0; i + 2 < words.length; i += 1) grams.add(`${words[i]} ${words[i + 1]} ${words[i + 2]}`)
  return grams
}

export function jaccard(a: Set<string>, b: Set<string>): number {
  if (a.size === 0 || b.size === 0) return 0
  let shared = 0
  const [small, large] = a.size <= b.size ? [a, b] : [b, a]
  for (const g of small) if (large.has(g)) shared += 1
  return shared / (a.size + b.size - shared)
}

/** Maior sequência de palavras consecutivas idênticas nas duas listas. */
export function longestCommonRun(a: string[], b: string[]): number {
  let best = 0
  let prev = new Array<number>(b.length + 1).fill(0)
  for (let i = 1; i <= a.length; i += 1) {
    const cur = new Array<number>(b.length + 1).fill(0)
    for (let j = 1; j <= b.length; j += 1) {
      if (a[i - 1] === b[j - 1]) {
        cur[j] = prev[j - 1]! + 1
        if (cur[j]! > best) best = cur[j]!
      }
    }
    prev = cur
  }
  return best
}

// ---------------------------------------------------------------- índice da fonte

export function buildSourceIndex(sources: ParaphraseSourceInput[]): SourceIndex {
  const sentences: SourceSentence[] = []
  const postings = new Map<string, number[]>()
  sources.forEach((source, sourceNo) => {
    const plain = stripMarkdown(source.text || '').replace(/^\s*>\s?/gm, '')
    for (const text of splitSentences(plain)) {
      const words = normalizeWords(text)
      if (words.length === 0) continue
      const grams = trigrams(words)
      const id = sentences.length
      sentences.push({ source: sourceNo, label: source.label, text, words, grams })
      for (const g of grams) {
        const list = postings.get(g)
        if (list) list.push(id)
        else postings.set(g, [id])
      }
    }
  })
  return { sentences, postings }
}

// ---------------------------------------------------------------- verificação

function wordFlags(words: string[], sharedGrams: Set<string>): boolean[] {
  const flags = new Array<boolean>(words.length).fill(false)
  for (let i = 0; i + 2 < words.length; i += 1) {
    if (sharedGrams.has(`${words[i]} ${words[i + 1]} ${words[i + 2]}`)) flags[i] = flags[i + 1] = flags[i + 2] = true
  }
  return flags
}

/** Divide o texto em partes, marcando as palavras que fazem parte de trigramas em comum. */
export function markShared(text: string, sharedGrams: Set<string>, limit = Infinity): TextPart[] {
  const words = normalizeWords(text)
  const flags = wordFlags(words, sharedGrams)
  const tokens: TextPart[] = []
  let wordNo = 0
  let length = 0
  let cut = false
  for (const token of text.split(/(\s+)/)) {
    if (!token) continue
    if (length >= limit) { cut = true; break }
    length += token.length
    const space = /^\s+$/.test(token)
    const n = space ? 0 : normalizeWords(token).length
    tokens.push({ text: token, shared: n > 0 && flags.slice(wordNo, wordNo + n).some(Boolean) })
    wordNo += n
  }
  // Espaço entre duas palavras marcadas também fica marcado, para o trecho sair inteiro.
  tokens.forEach((t, i) => {
    if (/^\s+$/.test(t.text)) t.shared = Boolean(tokens[i - 1]?.shared && tokens[i + 1]?.shared)
  })
  if (cut) tokens.push({ text: '…', shared: false })
  const parts: TextPart[] = []
  for (const t of tokens) {
    const last = parts[parts.length - 1]
    if (last && last.shared === t.shared) last.text += t.text
    else parts.push({ ...t })
  }
  return parts
}

interface Window { first: number; last: number }

function windowWords(index: SourceIndex, w: Window): string[] {
  const out: string[] = []
  for (let i = w.first; i <= w.last; i += 1) out.push(...index.sentences[i]!.words)
  return out
}

function windowText(index: SourceIndex, w: Window): string {
  return index.sentences.slice(w.first, w.last + 1).map((s) => s.text).join(' ')
}

function bestMatch(grams: Set<string>, words: string[], index: SourceIndex) {
  const counts = new Map<number, number>()
  for (const g of grams) {
    for (const id of index.postings.get(g) ?? []) counts.set(id, (counts.get(id) ?? 0) + 1)
  }
  if (counts.size === 0) return null
  const candidates = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, MAX_CANDIDATES).map(([id]) => id)
  const seen = new Set<string>()
  let best: { window: Window; score: number; shared: number } | null = null
  for (const id of candidates) {
    const source = index.sentences[id]!.source
    for (let size = 1; size <= MAX_WINDOW; size += 1) {
      for (let first = id - size + 1; first <= id; first += 1) {
        const last = first + size - 1
        if (first < 0 || last >= index.sentences.length) continue
        if (index.sentences[first]!.source !== source || index.sentences[last]!.source !== source) continue
        const key = `${first}:${last}`
        if (seen.has(key)) continue
        seen.add(key)
        let shared = 0
        let size2 = 0
        for (let i = first; i <= last; i += 1) size2 += index.sentences[i]!.grams.size
        for (const g of grams) {
          for (let i = first; i <= last; i += 1) {
            if (index.sentences[i]!.grams.has(g)) { shared += 1; break }
          }
        }
        const score = shared / (grams.size + size2 - shared)
        if (!best || score > best.score || (score === best.score && shared > best.shared)) {
          best = { window: { first, last }, score, shared }
        }
      }
    }
  }
  // A maior sequência comum é calculada nos melhores candidatos (pega cópia dentro de frase longa).
  let run = 0
  let runWindow: Window | null = null
  for (const id of candidates.slice(0, 5)) {
    const w = { first: Math.max(0, id - 1), last: Math.min(index.sentences.length - 1, id + 1) }
    const r = longestCommonRun(words, windowWords(index, w))
    if (r > run) { run = r; runWindow = { first: id, last: id } }
  }
  return best ? { ...best, run, runWindow } : null
}

function containsDeclared(words: string[], declared: string[]): boolean {
  if (declared.length === 0) return false
  const joined = ` ${words.join(' ')} `
  return declared.some((d) => joined.includes(` ${d} `) || ` ${d} `.includes(joined))
}

export function checkParaphrase(
  sections: Partial<Record<ParaphraseSectionKey, string>>,
  index: SourceIndex,
  declaredQuotes: DeclaredQuote[] = [],
): ParaphraseResult {
  const flagged: ParaphraseFlag[] = []
  let total = 0
  for (const { key } of PARAPHRASE_SECTIONS) {
    const declared = declaredQuotes
      .filter((q) => q.section === key)
      .map((q) => normalizeWords(stripMarkdown(q.text)))
      .filter((w) => w.length >= 3)
      .map((w) => w.join(' '))
    for (const sentence of splitSentences(sections[key] || '')) {
      const plain = withoutDeclaredQuotes(stripMarkdown(sentence))
      const words = normalizeWords(plain)
      if (words.length < MIN_WORDS) continue
      if (containsDeclared(normalizeWords(stripMarkdown(sentence)), declared)) continue
      total += 1
      const grams = trigrams(words)
      const match = index.sentences.length ? bestMatch(grams, words, index) : null
      if (!match) continue
      const level: ParaphraseLevel | null =
        match.score >= COPY_THRESHOLD || match.run >= COPY_RUN ? 'copy'
          : match.score >= CLOSE_THRESHOLD ? 'close' : null
      if (!level) continue
      const window = match.score >= CLOSE_THRESHOLD || !match.runWindow ? match.window : match.runWindow
      const sourceGrams = new Set<string>()
      for (let i = window.first; i <= window.last; i += 1) for (const g of index.sentences[i]!.grams) sourceGrams.add(g)
      const shared = new Set([...grams].filter((g) => sourceGrams.has(g)))
      flagged.push({
        section: key,
        sentence,
        level,
        score: match.score,
        run: match.run,
        sourceLabel: index.sentences[window.first]!.label,
        sentenceParts: markShared(stripMarkdown(sentence), shared),
        sourceParts: markShared(windowText(index, window), shared, MAX_EXCERPT),
      })
    }
  }
  return { flagged, total, copies: flagged.filter((f) => f.level === 'copy').length }
}

// ---------------------------------------------------------------- marcar como citação

export function abntQuoteCall(author: string | null | undefined, year: number | null | undefined, title?: string | null): string {
  const who = author?.trim()
    ? abntAuthorCall(author, title).toLocaleUpperCase('pt-BR').replace(/ ET AL\.$/, ' et al.')
    : abntAuthorCall(author, title)
  return `(${who}, ${year ? String(year) : '[s. d.]'}, p. )`
}

/**
 * Põe a frase entre aspas e acrescenta a chamada ABNT antes da pontuação final. Substitui só a primeira ocorrência
 * exata; devolve `null` se a frase não estiver mais no texto.
 */
export function markAsQuote(sectionText: string, sentence: string, call: string): string | null {
  const at = sectionText.indexOf(sentence)
  if (at < 0) return null
  const marker = sentence.match(/^\s*(?:[-*+]|\d+[.)])\s+/)?.[0] ?? ''
  const body = sentence.slice(marker.length)
  const match = body.match(/^(.*?)([.!?…]*)$/s)
  const core = (match?.[1] ?? body).trim().replace(/"/g, "'")
  const end = match?.[2] || '.'
  const quoted = `${marker}“${core}” ${call}${end}`
  return sectionText.slice(0, at) + quoted + sectionText.slice(at + sentence.length)
}
