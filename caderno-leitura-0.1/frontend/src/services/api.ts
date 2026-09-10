import type { Book, Chapter, ImportPreview, Study, StudyCreate, StudyPatch, StudySummary } from '../types.ts'

export interface HealthResponse {
  status: 'ok'
  service: string
  version: string
}

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Não foi possível concluir. Tente novamente.'
}

function detailMessage(data: unknown, status: number): string {
  if (typeof data === 'object' && data !== null && 'detail' in data) {
    if (typeof data.detail === 'string') return data.detail
    if (Array.isArray(data.detail) && status === 422) return 'Confira os campos obrigatórios e o conteúdo das seções.'
  }
  return status >= 500
    ? 'O caderno está indisponível. Verifique o servidor local e tente novamente.'
    : 'Não foi possível concluir a operação. Confira os dados e tente novamente.'
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(`/api${path}`, {
      ...options,
      headers: { Accept: 'application/json', ...(options.body ? { 'Content-Type': 'application/json' } : {}) },
      cache: 'no-store',
    })
  } catch (error) {
    if (options.signal?.aborted) throw error
    throw new ApiError('Não foi possível acessar o caderno. Verifique se o servidor local está aberto.', 0)
  }
  let data: unknown
  try { data = await response.json() } catch {
    throw new ApiError('O servidor não devolveu uma resposta válida. Verifique a conexão local.', response.ok ? 0 : response.status)
  }
  if (!response.ok) throw new ApiError(detailMessage(data, response.status), response.status)
  return data as T
}

export const api = {
  listBooks: (signal?: AbortSignal) => request<Book[]>('/books', { signal }),
  createBook: (title: string, author: string) => request<Book>('/books', {
    method: 'POST', body: JSON.stringify({ title: title.trim(), author: author.trim() || null }),
  }),
  listChapters: (bookId: number, signal?: AbortSignal) => request<Chapter[]>(`/books/${bookId}/chapters`, { signal }),
  createChapter: (bookId: number, name: string) => request<Chapter>(`/books/${bookId}/chapters`, {
    method: 'POST', body: JSON.stringify({ name: name.trim() }),
  }),
  listStudies: (chapterId: number, signal?: AbortSignal) => request<StudySummary[]>(`/chapters/${chapterId}/studies`, { signal }),
  getStudy: (id: number, signal?: AbortSignal) => request<Study>(`/studies/${id}`, { signal }),
  updateStudy: (id: number, payload: StudyPatch) => request<Study>(`/studies/${id}`, {
    method: 'PATCH', body: JSON.stringify(payload),
  }),
  preview: (source: string) => request<ImportPreview>('/imports/preview', {
    method: 'POST', body: JSON.stringify({ source_response: source }),
  }),
  createStudy: (payload: StudyCreate) => request<Study>('/studies', {
    method: 'POST', body: JSON.stringify(payload),
  }),
}

function isHealthResponse(value: unknown): value is HealthResponse {
  if (typeof value !== 'object' || value === null) return false

  return (
    'status' in value && value.status === 'ok' &&
    'service' in value && typeof value.service === 'string' &&
    'version' in value && typeof value.version === 'string'
  )
}

export async function fetchHealth(signal: AbortSignal): Promise<HealthResponse> {
  const response = await fetch('/api/health', {
    headers: { Accept: 'application/json' },
    cache: 'no-store',
    signal,
  })

  if (!response.ok) {
    throw new Error(`A API respondeu com o status HTTP ${response.status}.`)
  }

  const data: unknown = await response.json()
  if (!isHealthResponse(data)) {
    throw new Error('A resposta recebida não corresponde à API do Caderno de Leitura.')
  }

  return data
}
