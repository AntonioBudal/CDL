import type {
  Book, BookPatch, Category, Chapter, ChapterPatch, CoverResponse, DashboardParams, DashboardResponse, ExportConfig, ImportPreview, RestoreResult, Study, StudyCreate, StudyPatch, StudySummary,
  TrashSummary, TrashEmptyResponse, BookCanvasResponse, CanvasBatchUpdatePayload, CanvasBatchUpdateItem, StudyCanvasNode,
  StudyRelationsResponse, StudyRelationItem, CreateStudyRelationPayload, UpdateStudyRelationPayload, CandidateStudyItem, BookCanvasRelationItem,
  StudyStatusUpdatePayload, StudyStatusResponse, CanvasFrameItem, CreateCanvasFramePayload, UpdateCanvasFramePayload,
  SearchResponse, SearchHistoryResponse, UserRead,
} from '../types.ts'

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

let currentApiUserId: string | null = null

export function setApiUserId(id: string | null): void {
  currentApiUserId = id
}

export function getApiUserId(): string | null {
  return currentApiUserId
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData
  const headers: Record<string, string> = {
    Accept: 'application/json',
  }
  if (options.body && !isFormData) {
    headers['Content-Type'] = 'application/json'
  }
  if (currentApiUserId) {
    headers['X-User-Id'] = currentApiUserId
  }

  try {
    response = await fetch(`/api${path}`, {
      ...options,
      headers: { ...headers, ...(options.headers as Record<string, string> | undefined) },
      cache: 'no-store',
    })
  } catch (error) {
    if (options.signal?.aborted) throw error
    throw new ApiError('Não foi possível acessar o caderno. Verifique se o servidor local está aberto.', 0)
  }
  let data: unknown
  if (response.status === 204 || response.status === 205) {
    return null as T
  }
  try { data = await response.json() } catch {
    throw new ApiError('O servidor não devolveu uma resposta válida. Verifique a conexão local.', response.ok ? 0 : response.status)
  }
  if (!response.ok) throw new ApiError(detailMessage(data, response.status), response.status)
  return data as T
}

export const api = {
  listBooks: (signal?: AbortSignal) => request<Book[]>('/books', { signal }),
  createBook: (title: string, author?: string | null, category_ids?: string[]) => request<Book>('/books', {
    method: 'POST',
    body: JSON.stringify({
      title: title.trim(),
      author: author ? author.trim() : null,
      category_ids: category_ids || [],
    }),
  }),
  listCategories: (q?: string, signal?: AbortSignal) => {
    const url = q && q.trim() ? `/categories?q=${encodeURIComponent(q.trim())}` : '/categories'
    return request<Category[]>(url, { signal })
  },
  updateBook: (id: number, payload: BookPatch) => request<Book>(`/books/${id}`, {
    method: 'PATCH', body: JSON.stringify(payload),
  }),
  uploadBookCover: (id: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request<CoverResponse>(`/books/${id}/cover`, {
      method: 'POST',
      body: formData,
    })
  },
  importBookCoverFromUrl: (id: number, url: string) => request<CoverResponse>(`/books/${id}/cover/url`, {
    method: 'POST',
    body: JSON.stringify({ url }),
  }),
  removeBookCover: (id: number) => request<CoverResponse>(`/books/${id}/cover`, {
    method: 'DELETE',
  }),
  listChapters: (bookId: number, signal?: AbortSignal) => request<Chapter[]>(`/books/${bookId}/chapters`, { signal }),
  createChapter: (bookId: number, name: string) => request<Chapter>(`/books/${bookId}/chapters`, {
    method: 'POST', body: JSON.stringify({ name: name.trim() }),
  }),
  updateChapter: (bookId: number, chapterId: number, payload: ChapterPatch) => request<Chapter>(`/books/${bookId}/chapters/${chapterId}`, {
    method: 'PATCH', body: JSON.stringify(payload),
  }),
  moveChapter: (bookId: number, chapterId: number, direction: 'up' | 'down') => request<Chapter[]>(`/books/${bookId}/chapters/${chapterId}/move`, {
    method: 'POST', body: JSON.stringify({ direction }),
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

  // Métodos de Lixeira (Soft Delete e Purga)
  trashBook: (id: number) => request<Book>(`/books/${id}/trash`, { method: 'POST' }),
  trashStudy: (id: number) => request<Study>(`/studies/${id}/trash`, { method: 'POST' }),
  restoreBook: (id: number) => request<Book>(`/books/${id}/restore`, { method: 'POST' }),
  restoreStudy: (id: number) => request<Study & { book_restored?: boolean }>(`/studies/${id}/restore`, { method: 'POST' }),
  permanentDeleteBook: (id: number) => request<void>(`/books/${id}/permanent`, { method: 'DELETE' }),
  permanentDeleteStudy: (id: number) => request<void>(`/studies/${id}/permanent`, { method: 'DELETE' }),
  getTrash: (signal?: AbortSignal) => request<TrashSummary>('/trash', { signal }),
  emptyTrash: () => request<TrashEmptyResponse>('/trash/empty', { method: 'POST' }),
  purgeExpired: () => request<{ purged_books: number; purged_studies: number }>('/trash/purge-expired', { method: 'POST' }),
  getDashboard: (params?: DashboardParams, signal?: AbortSignal) => {
    const searchParams = new URLSearchParams()
    if (params?.tz_offset !== undefined) searchParams.set('tz_offset', String(params.tz_offset))
    if (params?.days !== undefined) searchParams.set('days', String(params.days))
    if (params?.date) searchParams.set('date', params.date)
    if (params?.limit !== undefined) searchParams.set('limit', String(params.limit))
    const qs = searchParams.toString()
    return request<DashboardResponse>(`/dashboard${qs ? `?${qs}` : ''}`, { signal })
  },
  exportBook: (id: number, config: ExportConfig) => {
    const qs = buildExportQuery(config)
    const ext = config.format === 'markdown' ? 'md' : 'txt'
    return downloadExportFile(`/api/books/${id}/export?${qs}`, `livro-${id}.${ext}`)
  },
  exportStudy: (id: number, config: ExportConfig) => {
    const qs = buildExportQuery(config)
    const ext = config.format === 'markdown' ? 'md' : 'txt'
    return downloadExportFile(`/api/studies/${id}/export?${qs}`, `estudo-${id}.${ext}`)
  },

  // Relações entre Estudos (F04)
  getStudyRelations: (studyId: number, signal?: AbortSignal) =>
    request<StudyRelationsResponse>(`/studies/${studyId}/relations`, { signal }),
  createStudyRelation: (studyId: number, payload: CreateStudyRelationPayload) =>
    request<StudyRelationItem>(`/studies/${studyId}/relations`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateStudyRelation: (relationId: number, payload: UpdateStudyRelationPayload) =>
    request<StudyRelationItem>(`/relations/${relationId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  deleteStudyRelation: (relationId: number) =>
    request<{ success: boolean; message: string }>(`/relations/${relationId}`, {
      method: 'DELETE',
    }),
  searchCandidateStudies: (excludeStudyId: number, query = '', limit = 20, signal?: AbortSignal) => {
    const params = new URLSearchParams()
    params.set('exclude_study_id', String(excludeStudyId))
    if (query.trim()) params.set('query', query.trim())
    params.set('limit', String(limit))
    return request<CandidateStudyItem[]>(`/studies/search-candidates?${params.toString()}`, { signal })
  },
  getBookRelations: (bookId: number, signal?: AbortSignal) =>
    request<BookCanvasRelationItem[]>(`/books/${bookId}/relations`, { signal }),
  // Agrupamento Visual e Status de Leitura (F05)
  updateStudyStatus: (studyId: number, payload: StudyStatusUpdatePayload) =>
    request<StudyStatusResponse>(`/studies/${studyId}/status`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  getCanvasFrames: (bookId: number, signal?: AbortSignal) =>
    request<CanvasFrameItem[]>(`/books/${bookId}/canvas/frames`, { signal }),
  createCanvasFrame: (bookId: number, payload: CreateCanvasFramePayload) =>
    request<CanvasFrameItem>(`/books/${bookId}/canvas/frames`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateCanvasFrame: (frameId: number, payload: UpdateCanvasFramePayload) =>
    request<CanvasFrameItem>(`/canvas/frames/${frameId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  deleteCanvasFrame: (frameId: number) =>
    request<{ success: boolean; message: string }>(`/canvas/frames/${frameId}`, {
      method: 'DELETE',
    }),

  // Categorias (F01 CRUD)
  createCategory: (payload: { id?: string; name: string; parent_id?: string | null }) =>
    request<Category>('/categories', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteCategory: (id: string) =>
    request<void>(`/categories/${id}`, {
      method: 'DELETE',
    }),

  // Usuário e Autenticação (F01)
  getMe: (signal?: AbortSignal) => request<UserRead>('/auth/me', { signal }),
}

export function buildExportQuery(config: ExportConfig): string {
  const params = new URLSearchParams()
  params.set('format', config.format)
  params.set('include_notes', String(config.includeNotes))
  params.set('include_sections', String(config.includeSections))
  params.set('include_source', String(config.includeSource))
  params.set('include_metadata', String(config.includeMetadata))
  return params.toString()
}

export function getExportBookUrl(id: number, config: ExportConfig): string {
  const qs = buildExportQuery(config)
  return `/api/books/${id}/export?${qs}`
}

export function getExportStudyUrl(id: number, config: ExportConfig): string {
  const qs = buildExportQuery(config)
  return `/api/studies/${id}/export?${qs}`
}

export async function downloadExportFile(url: string, defaultFilename: string): Promise<{ filename: string; blob: Blob }> {
  const headers: Record<string, string> = {}
  if (currentApiUserId) {
    headers['X-User-Id'] = currentApiUserId
  }
  const response = await fetch(url, {
    headers,
    cache: 'no-store',
  })
  if (!response.ok) {
    let msg = 'Não foi possível exportar o arquivo.'
    try {
      const errData = await response.json()
      if (errData && typeof errData === 'object' && 'detail' in errData && typeof errData.detail === 'string') {
        msg = errData.detail
      }
    } catch {
      // ignore
    }
    throw new ApiError(msg, response.status)
  }

  const blob = await response.blob()
  let filename = defaultFilename
  const disposition = response.headers.get('Content-Disposition')
  if (disposition) {
    const match = /filename\*?=['"]?(?:UTF-\d['"]*)?([^;\r\n"']*)['"]?/i.exec(disposition)
    if (match && match[1]) {
      filename = decodeURIComponent(match[1])
    }
  }

  if (typeof window !== 'undefined' && typeof document !== 'undefined' && window.URL?.createObjectURL) {
    const blobUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(blobUrl)
  }

  return { filename, blob }
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

export async function downloadBackupBundle(signal?: AbortSignal): Promise<{ filename: string, blob: Blob }> {
  const response = await fetch('/api/backup/bundle', {
    headers: { Accept: 'application/zip' },
    cache: 'no-store',
    signal,
  })

  if (!response.ok) {
    const data: unknown = await response.json().catch(() => null)
    const detail =
      typeof data === 'object' && data !== null && 'detail' in data && typeof data.detail === 'string'
        ? data.detail
        : `Falha ao gerar pacote de backup (HTTP ${response.status}).`
    throw new Error(detail)
  }

  const disposition = response.headers.get('Content-Disposition') ?? ''
  const filename = disposition.match(/filename="([^"]+)"/)?.[1] ?? `caderno-backup-${new Date().toISOString().replace(/[:.]/g, '-')}.zip`
  const blob = await response.blob()

  if (typeof window !== 'undefined' && typeof document !== 'undefined') {
    const blobUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(blobUrl)
  }

  return { filename, blob }
}

export async function restoreBackupPackage(file: File, signal?: AbortSignal): Promise<RestoreResult> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch('/api/backup/restore', {
    method: 'POST',
    body: formData,
    signal,
  })

  if (!response.ok) {
    const data: unknown = await response.json().catch(() => null)
    const detail =
      typeof data === 'object' && data !== null && 'detail' in data && typeof data.detail === 'string'
        ? data.detail
        : `Falha ao restaurar acervo (HTTP ${response.status}).`
    throw new Error(detail)
  }

  return response.json()
}

// --- Canvas de Estudos (F03) ---

export async function getCanvasNodes(bookId: number): Promise<BookCanvasResponse> {
  return request<BookCanvasResponse>(`/books/${bookId}/canvas`)
}

export async function saveCanvasBatch(
  bookId: number,
  payload: CanvasBatchUpdatePayload,
): Promise<BookCanvasResponse> {
  return request<BookCanvasResponse>(`/books/${bookId}/canvas`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function patchCanvasNode(
  studyId: number,
  data: Partial<CanvasBatchUpdateItem>,
): Promise<StudyCanvasNode> {
  return request<StudyCanvasNode>(`/studies/${studyId}/canvas`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

// --- Relações entre Estudos (F04) ---

export async function getStudyRelations(studyId: number, signal?: AbortSignal): Promise<StudyRelationsResponse> {
  return request<StudyRelationsResponse>(`/studies/${studyId}/relations`, { signal })
}

export async function createStudyRelation(
  studyId: number,
  payload: CreateStudyRelationPayload,
): Promise<StudyRelationItem> {
  return request<StudyRelationItem>(`/studies/${studyId}/relations`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateStudyRelation(
  relationId: number,
  payload: UpdateStudyRelationPayload,
): Promise<StudyRelationItem> {
  return request<StudyRelationItem>(`/relations/${relationId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function deleteStudyRelation(relationId: number): Promise<{ success: boolean; message: string }> {
  return request<{ success: boolean; message: string }>(`/relations/${relationId}`, {
    method: 'DELETE',
  })
}

export async function searchCandidateStudies(
  excludeStudyId: number,
  query = '',
  limit = 20,
  signal?: AbortSignal,
): Promise<CandidateStudyItem[]> {
  const params = new URLSearchParams()
  params.set('exclude_study_id', String(excludeStudyId))
  if (query.trim()) params.set('query', query.trim())
  params.set('limit', String(limit))
  return request<CandidateStudyItem[]>(`/studies/search-candidates?${params.toString()}`, { signal })
}

export async function getBookRelations(bookId: number, signal?: AbortSignal): Promise<BookCanvasRelationItem[]> {
  return request<BookCanvasRelationItem[]>(`/books/${bookId}/relations`, { signal })
}

export async function updateStudyStatus(
  studyId: number,
  payload: StudyStatusUpdatePayload,
): Promise<StudyStatusResponse> {
  return request<StudyStatusResponse>(`/studies/${studyId}/status`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function getCanvasFrames(
  bookId: number,
  signal?: AbortSignal,
): Promise<CanvasFrameItem[]> {
  return request<CanvasFrameItem[]>(`/books/${bookId}/canvas/frames`, { signal })
}

export async function createCanvasFrame(
  bookId: number,
  payload: CreateCanvasFramePayload,
): Promise<CanvasFrameItem> {
  return request<CanvasFrameItem>(`/books/${bookId}/canvas/frames`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateCanvasFrame(
  frameId: number,
  payload: UpdateCanvasFramePayload,
): Promise<CanvasFrameItem> {
  return request<CanvasFrameItem>(`/canvas/frames/${frameId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function deleteCanvasFrame(
  frameId: number,
): Promise<{ success: boolean; message: string }> {
  return request<{ success: boolean; message: string }>(`/canvas/frames/${frameId}`, {
    method: 'DELETE',
  })
}

export interface SearchParams {
  q: string
  mode?: 'and' | 'or'
  book_id?: number
  category_id?: string | number
  limit?: number
}

export async function searchStudies(
  params: SearchParams,
  signal?: AbortSignal,
): Promise<SearchResponse> {
  const query = new URLSearchParams()
  query.set('q', params.q)
  if (params.mode) query.set('mode', params.mode)
  if (params.book_id != null) query.set('book_id', String(params.book_id))
  if (params.category_id != null) query.set('category_id', String(params.category_id))
  if (params.limit != null) query.set('limit', String(params.limit))
  return request<SearchResponse>(`/search?${query.toString()}`, { signal })
}

export async function getSearchHistory(
  signal?: AbortSignal,
): Promise<SearchHistoryResponse> {
  return request<SearchHistoryResponse>('/search/history', { signal })
}

export async function deleteSearchHistoryItem(
  id: number,
): Promise<{ success: boolean; message: string }> {
  return request<{ success: boolean; message: string }>(`/search/history/${id}`, {
    method: 'DELETE',
  })
}

export async function clearSearchHistory(): Promise<{ success: boolean; message: string }> {
  return request<{ success: boolean; message: string }>('/search/history', {
    method: 'DELETE',
  })
}



