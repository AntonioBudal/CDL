import type {
  Book, BookPatch, Category, CategorySuggestion, CategoryStats, Chapter, ChapterPatch, CoverResponse, DashboardParams, DashboardResponse, ExportConfig, ImportPreview, RestoreResult, Study, StudyCreate, StudyPatch, StudySummary,
  TrashSummary, TrashEmptyResponse, BookCanvasResponse, CanvasBatchUpdatePayload, CanvasBatchUpdateItem, StudyCanvasNode,
  StudyRelationsResponse, StudyRelationItem, CreateStudyRelationPayload, UpdateStudyRelationPayload, CandidateStudyItem, BookCanvasRelationItem,
  StudyStatusUpdatePayload, StudyStatusResponse, CanvasFrameItem, CreateCanvasFramePayload, UpdateCanvasFramePayload,
  StudyHighlight, StudyHighlightCreatePayload, StudyHighlightUpdatePayload,
  StudyVersionSummary, StudyVersionDetail, StudyDiffResult,
  SupportPublicInfo, SupportAdminConfig, SupportConfigUpdate,
  SearchResponse, SearchHistoryResponse, UserRead,
  AuthConfigResponse, AuthSuccessResponse, SessionItem, ExternalIdentityRead,
  AuditLogListResponse, DeactivateAccountRequest, ReactivateAccountRequest, DeleteAccountRequest,
} from '../types.ts'


import type {
  ConflictData,
  SyncChangesResponse,
  UserPreferenceRead,
  UserPreferenceUpdate,
  UserProfilePrivate,
  UserProfilePublic,
  UserProfileUpdate,
  UserSearchItem,
  FriendItem,
  FriendRequestsResponse,
  FriendBlockedItem,
  FriendsSummary,
  FriendshipStatusResponse,
  FriendshipActionResponse,
  ResourcePermissionsRead,
  ResourcePermissionItem,
  ResourceVisibility,
  BookVisibility,
  SharedStudiesResponse,
  SharedBooksResponse,
} from '../types.ts'

import type {
  AdminUsersFilter,
  AdminUsersResponse,
  AdminStatsSummary,
  AdminSuspendRequest,
  AdminSuspendResponse,
  AdminReactivateResponse,
  AdminRoleUpdateRequest,
  AdminRoleUpdateResponse,
  AdminRevokeSessionsResponse,
} from '../types/admin.ts'

import type {
  NotificationItem,
  NotificationListResponse,
  UnreadCountResponse,
  BroadcastNotificationRequest,
  BroadcastNotificationResponse,
  NotificationPurgeResponse,
} from '../types/notifications.ts'

export interface NotificationReadAllResponse {
  marked_count: number
  message: string
}

export interface HealthResponse {
  status: 'ok'
  service: string
  version: string
}

export class ApiError extends Error {
  status: number
  data?: unknown
  constructor(message: string, status: number, data?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

export class ConcurrencyConflictApiError extends ApiError {
  conflictData: ConflictData
  constructor(message: string, conflictData: ConflictData) {
    super(message, 409, conflictData)
    this.name = 'ConcurrencyConflictApiError'
    this.conflictData = conflictData
  }
}

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Não foi possível concluir. Tente novamente.'
}

export function detailMessage(data: unknown, status: number): string {
  if (typeof data === 'object' && data !== null) {
    if ('message' in data && typeof (data as { message: unknown }).message === 'string') {
      return (data as { message: string }).message
    }
    if ('detail' in data) {
      const detail = (data as { detail: unknown }).detail
      if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && status === 422) {
      const fieldLabels: Record<string, string> = {
        username: 'Nome de usuário',
        display_name: 'Nome de exibição',
        email: 'E-mail',
        password: 'Senha',
        username_or_email: 'Usuário ou e-mail',
        title: 'Título',
        content: 'Conteúdo',
      }
      const messages = detail
        .map((err) => {
          if (typeof err === 'string') return err
          if (err && typeof err === 'object') {
            const e = err as { loc?: unknown[]; msg?: string }
            if (typeof e.msg === 'string') {
              const cleanMsg = e.msg.replace(/^Value error,\s*/i, '')
              const lastLoc = Array.isArray(e.loc) ? String(e.loc[e.loc.length - 1]) : ''
              const label = fieldLabels[lastLoc] || (lastLoc && lastLoc !== 'body' ? lastLoc : '')
              if (label && !cleanMsg.toLowerCase().includes(label.toLowerCase())) {
                return `${label}: ${cleanMsg}`
              }
              return cleanMsg
            }
          }
          return null
        })
        .filter((msg): msg is string => Boolean(msg))

      if (messages.length > 0) {
        return messages.join('. ')
      }
      return 'Confira os campos obrigatórios e os dados informados.'
    }
  }
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
      credentials: 'same-origin',
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
  if (!response.ok) {
    if (
      response.status === 409 &&
      typeof data === 'object' &&
      data !== null &&
      'server_version' in data
    ) {
      throw new ConcurrencyConflictApiError(detailMessage(data, 409), data as ConflictData)
    }
    throw new ApiError(detailMessage(data, response.status), response.status, data)
  }
  return data as T
}

export const api = {
  listBooks: (signal?: AbortSignal) => request<Book[]>('/books', { signal }),
  getBook: (id: number, signal?: AbortSignal) => request<Book>(`/books/${id}`, { signal }),
  createBook: (title: string, author?: string | null, category_ids?: string[]) => request<Book>('/books', {
    method: 'POST',
    body: JSON.stringify({
      title: title.trim(),
      author: author ? author.trim() : null,
      category_ids: category_ids || [],
    }),
  }),
  listCategories: (params?: string | { q?: string; canonical_only?: boolean }, signal?: AbortSignal) => {
    let q: string | undefined
    let canonicalOnly: boolean | undefined
    if (typeof params === 'string') {
      q = params
    } else if (params) {
      q = params.q
      canonicalOnly = params.canonical_only
    }
    const queryParts: string[] = []
    if (q && q.trim()) queryParts.push(`q=${encodeURIComponent(q.trim())}`)
    if (canonicalOnly !== undefined) queryParts.push(`canonical_only=${canonicalOnly}`)
    const qs = queryParts.length ? `?${queryParts.join('&')}` : ''
    return request<Category[]>(`/categories${qs}`, { signal })
  },
  suggestCategories: (q: string, signal?: AbortSignal) =>
    request<CategorySuggestion>(`/categories/suggest?q=${encodeURIComponent(q.trim())}`, { signal }),
  getCategoryStats: (signal?: AbortSignal) =>
    request<CategoryStats>('/categories/stats', { signal }),
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

  // Métodos de Destaques e Ações Contextuais
  listStudyHighlights: (studyId: number, section?: string, signal?: AbortSignal) => {
    const url = section ? `/studies/${studyId}/highlights?section=${encodeURIComponent(section)}` : `/studies/${studyId}/highlights`
    return request<StudyHighlight[]>(url, { signal })
  },
  createStudyHighlight: (studyId: number, payload: StudyHighlightCreatePayload) => request<StudyHighlight>(`/studies/${studyId}/highlights`, {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  updateStudyHighlight: (studyId: number, highlightId: number, payload: StudyHighlightUpdatePayload) => request<StudyHighlight>(`/studies/${studyId}/highlights/${highlightId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  }),
  deleteStudyHighlight: (studyId: number, highlightId: number) => request<void>(`/studies/${studyId}/highlights/${highlightId}`, {
    method: 'DELETE',
  }),

  // Métodos de Histórico e Versões de Estudos (F0.6.5)
  listStudyVersions: (studyId: number, signal?: AbortSignal) =>
    request<StudyVersionSummary[]>(`/studies/${studyId}/versions`, { signal }),
  getStudyVersionDetail: (studyId: number, versionId: number, signal?: AbortSignal) =>
    request<StudyVersionDetail>(`/studies/${studyId}/versions/${versionId}`, { signal }),
  getStudyVersionDiff: (studyId: number, versionId: number, targetVersionId?: number, signal?: AbortSignal) => {
    const url = targetVersionId
      ? `/studies/${studyId}/versions/${versionId}/diff?target_version_id=${targetVersionId}`
      : `/studies/${studyId}/versions/${versionId}/diff`
    return request<StudyDiffResult>(url, { signal })
  },
  restoreStudyVersion: (studyId: number, versionId: number) =>
    request<Study>(`/studies/${studyId}/versions/${versionId}/restore`, {
      method: 'POST',
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

  // Sincronização Multidispositivo e Preferências (F04)
  fetchSyncChanges: (since?: string | null, signal?: AbortSignal) => {
    const qs = since ? `?since=${encodeURIComponent(since)}` : ''
    return request<SyncChangesResponse>(`/sync/changes${qs}`, { signal })
  },
  getUserPreferences: (signal?: AbortSignal) =>
    request<UserPreferenceRead>('/preferences', { signal }),
  updateUserPreferences: (payload: UserPreferenceUpdate) =>
    request<UserPreferenceRead>('/preferences', {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  // Perfil e Privacidade (F05)
  getMyProfile: (signal?: AbortSignal) =>
    request<UserProfilePrivate>('/profile/me', { signal }),
  updateMyProfile: (payload: UserProfileUpdate) =>
    request<UserProfilePrivate>('/profile/me', {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  uploadAvatar: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request<{ avatar_url: string }>('/profile/avatar', {
      method: 'POST',
      body: formData,
    })
  },
  deleteAvatar: () =>
    request<{ avatar_url: string | null }>('/profile/avatar', {
      method: 'DELETE',
    }),
  getUserPublicProfile: (username: string, signal?: AbortSignal) =>
    request<UserProfilePublic>(`/users/${encodeURIComponent(username)}`, { signal }),
  searchUsers: (query?: string, signal?: AbortSignal) => {
    const qs = query ? `?q=${encodeURIComponent(query)}` : ''
    return request<UserSearchItem[]>(`/users${qs}`, { signal })
  },

  // Sistema de Amizades (F06)
  sendFriendRequest: (username: string) =>
    request<FriendshipActionResponse>(`/friends/request/${encodeURIComponent(username)}`, {
      method: 'POST',
    }),
  acceptFriendRequest: (requestId: number) =>
    request<FriendshipActionResponse>(`/friends/accept/${requestId}`, {
      method: 'POST',
    }),
  rejectFriendRequest: (requestId: number) =>
    request<FriendshipActionResponse>(`/friends/reject/${requestId}`, {
      method: 'POST',
    }),
  cancelFriendRequest: (requestId: number) =>
    request<FriendshipActionResponse>(`/friends/cancel/${requestId}`, {
      method: 'DELETE',
    }),
  removeFriend: (username: string) =>
    request<FriendshipActionResponse>(`/friends/${encodeURIComponent(username)}`, {
      method: 'DELETE',
    }),
  blockUser: (username: string) =>
    request<FriendshipActionResponse>(`/friends/block/${encodeURIComponent(username)}`, {
      method: 'POST',
    }),
  unblockUser: (username: string) =>
    request<FriendshipActionResponse>(`/friends/unblock/${encodeURIComponent(username)}`, {
      method: 'POST',
    }),
  getFriends: (signal?: AbortSignal) =>
    request<FriendItem[]>('/friends', { signal }),
  getFriendRequests: (signal?: AbortSignal) =>
    request<FriendRequestsResponse>('/friends/requests', { signal }),
  getBlockedUsers: (signal?: AbortSignal) =>
    request<FriendBlockedItem[]>('/friends/blocked', { signal }),
  getFriendsSummary: (signal?: AbortSignal) =>
    request<FriendsSummary>('/friends/summary', { signal }),
  getRelationStatus: (username: string, signal?: AbortSignal) =>
    request<FriendshipStatusResponse>(`/friends/status/${encodeURIComponent(username)}`, { signal }),

  // Compartilhamento e Permissões (F07)
  getStudyPermissions: (studyId: number, signal?: AbortSignal) =>
    request<ResourcePermissionsRead>(`/studies/${studyId}/permissions`, { signal }),
  updateStudyVisibility: (studyId: number, visibility: ResourceVisibility) =>
    request<ResourcePermissionsRead>(`/studies/${studyId}/visibility`, {
      method: 'PUT',
      body: JSON.stringify({ visibility }),
    }),
  updateBookVisibility: (bookId: number, visibility: BookVisibility) =>
    request<Book>(`/books/${bookId}/visibility`, {
      method: 'PUT',
      body: JSON.stringify({ visibility }),
    }),
  grantStudyPermission: (studyId: number, username: string) =>
    request<ResourcePermissionItem>(`/studies/${studyId}/permissions`, {
      method: 'POST',
      body: JSON.stringify({ username }),
    }),
  revokeStudyPermission: (studyId: number, userId: string) =>
    request<{ ok: boolean }>(`/studies/${studyId}/permissions/${userId}`, {
      method: 'DELETE',
    }),
  getSharedStudies: (
    params?: { q?: string; author?: string; limit?: number; offset?: number },
    signal?: AbortSignal,
  ) => {
    const searchParams = new URLSearchParams()
    if (params?.q?.trim()) searchParams.set('q', params.q.trim())
    if (params?.author?.trim()) searchParams.set('author', params.author.trim())
    if (params?.limit != null) searchParams.set('limit', String(params.limit))
    if (params?.offset != null) searchParams.set('offset', String(params.offset))
    const queryStr = searchParams.toString()
    return request<SharedStudiesResponse>(`/shared/studies${queryStr ? `?${queryStr}` : ''}`, { signal })
  },
  getSharedBooks: (
    params?: { q?: string; limit?: number; offset?: number },
    signal?: AbortSignal,
  ) => {
    const searchParams = new URLSearchParams()
    if (params?.q?.trim()) searchParams.set('q', params.q.trim())
    if (params?.limit != null) searchParams.set('limit', String(params.limit))
    if (params?.offset != null) searchParams.set('offset', String(params.offset))
    const queryStr = searchParams.toString()
    return request<SharedBooksResponse>(`/shared/books${queryStr ? `?${queryStr}` : ''}`, { signal })
  },

  // Administração e RBAC (F08)
  getAdminUsers: (
    params?: AdminUsersFilter,
    signal?: AbortSignal,
  ) => {
    const searchParams = new URLSearchParams()
    if (params?.q?.trim()) searchParams.set('q', params.q.trim())
    if (params?.status && params.status !== 'all') searchParams.set('status', params.status)
    if (params?.role && params.role !== 'all') searchParams.set('role', params.role)
    if (params?.limit != null) searchParams.set('limit', String(params.limit))
    if (params?.offset != null) searchParams.set('offset', String(params.offset))
    const queryStr = searchParams.toString()
    return request<AdminUsersResponse>(`/admin/users${queryStr ? `?${queryStr}` : ''}`, { signal })
  },
  getAdminStats: (signal?: AbortSignal) =>
    request<AdminStatsSummary>('/admin/stats', { signal }),
  suspendUser: (userId: string, payload?: AdminSuspendRequest) =>
    request<AdminSuspendResponse>(`/admin/users/${userId}/suspend`, {
      method: 'POST',
      body: payload ? JSON.stringify(payload) : undefined,
    }),
  reactivateUser: (userId: string) =>
    request<AdminReactivateResponse>(`/admin/users/${userId}/reactivate`, {
      method: 'POST',
    }),
  updateUserRole: (userId: string, payload: AdminRoleUpdateRequest) =>
    request<AdminRoleUpdateResponse>(`/admin/users/${userId}/role`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  revokeAllSessions: (userId: string) =>
    request<AdminRevokeSessionsResponse>(`/admin/users/${userId}/sessions/revoke-all`, {
      method: 'POST',
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

  // Usuário e Autenticação (F01 & F02)
  getMe: (signal?: AbortSignal) => request<UserRead>('/auth/me', { signal }),
  getAuthConfig: (signal?: AbortSignal) => request<AuthConfigResponse>('/auth/config', { signal }),
  setupOwner: (password: string) =>
    request<AuthSuccessResponse>('/auth/setup-owner', {
      method: 'POST',
      body: JSON.stringify({ password }),
    }),
  register: (payload: { username: string; display_name: string; email?: string | null; password: string }) =>
    request<AuthSuccessResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  login: (usernameOrEmail: string, password: string) =>
    request<AuthSuccessResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username_or_email: usernameOrEmail, password }),
    }),
  logout: () =>
    request<{ ok: boolean }>('/auth/logout', {
      method: 'POST',
    }),
  getSessions: (signal?: AbortSignal) => request<SessionItem[]>('/auth/sessions', { signal }),
  revokeSession: (sessionId: string) =>
    request<void>(`/auth/sessions/${sessionId}`, {
      method: 'DELETE',
    }),
  logoutAll: () =>
    request<{ revoked_count: number }>('/auth/logout-all', {
      method: 'POST',
    }),
  loginWithGoogle: (credential: string) =>
    request<AuthSuccessResponse>('/auth/google', {
      method: 'POST',
      body: JSON.stringify({ credential }),
    }),
  linkGoogle: (credential: string) =>
    request<ExternalIdentityRead>('/auth/google/link', {
      method: 'POST',
      body: JSON.stringify({ credential }),
    }),
  unlinkGoogle: () =>
    request<{ ok: boolean }>('/auth/google/unlink', {
      method: 'DELETE',
    }),

  // Ciclo de Vida da Conta e Segurança (F10)
  deactivateAccount: (data?: DeactivateAccountRequest) =>
    request<{ ok: boolean; message: string }>('/account/deactivate', {
      method: 'POST',
      body: JSON.stringify(data || {}),
    }),
  reactivateAccount: (data: ReactivateAccountRequest) =>
    request<AuthSuccessResponse>('/account/reactivate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  deleteAccount: (data: DeleteAccountRequest) =>
    request<{ ok: boolean; message: string }>('/account', {
      method: 'DELETE',
      body: JSON.stringify(data),
    }),
  exportAccountData: () =>
    downloadExportFile('/api/account/export', 'caderno-dados-acervo.zip'),
  getAuditLogs: (
    params?: { event_type?: string; limit?: number; offset?: number },
    signal?: AbortSignal,
  ) => {
    const searchParams = new URLSearchParams()
    if (params?.event_type != null) searchParams.set('event_type', params.event_type)
    if (params?.limit != null) searchParams.set('limit', String(params.limit))
    if (params?.offset != null) searchParams.set('offset', String(params.offset))
    const queryStr = searchParams.toString()
    return request<AuditLogListResponse>(`/admin/audit-logs${queryStr ? `?${queryStr}` : ''}`, { signal })
  },

  // Notificações e Atividade Social (F09)
  getNotifications: (
    params?: { unread_only?: boolean; limit?: number; offset?: number },
    signal?: AbortSignal,
  ) => {
    const searchParams = new URLSearchParams()
    if (params?.unread_only != null) searchParams.set('unread_only', String(params.unread_only))
    if (params?.limit != null) searchParams.set('limit', String(params.limit))
    if (params?.offset != null) searchParams.set('offset', String(params.offset))
    const queryStr = searchParams.toString()
    return request<NotificationListResponse>(`/notifications${queryStr ? `?${queryStr}` : ''}`, { signal })
  },
  getUnreadCount: (signal?: AbortSignal) =>
    request<UnreadCountResponse>('/notifications/unread-count', { signal }),
  markNotificationAsRead: (notificationId: string) =>
    request<NotificationItem>(`/notifications/${notificationId}/read`, {
      method: 'PATCH',
    }),
  markAllNotificationsAsRead: () =>
    request<NotificationReadAllResponse>('/notifications/read-all', {
      method: 'POST',
    }),
  broadcastNotification: (payload: BroadcastNotificationRequest) =>
    request<BroadcastNotificationResponse>('/admin/notifications/broadcast', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  purgeNotifications: (retentionDays?: number) => {
    const queryStr = retentionDays != null ? `?retention_days=${retentionDays}` : ''
    return request<NotificationPurgeResponse>(`/admin/notifications/purge${queryStr}`, {
      method: 'POST',
    })
  },

  // Apoie o Leitorum (F0.6.6)
  getSupportInfo: (signal?: AbortSignal) =>
    request<SupportPublicInfo>('/support', { signal }),
  getAdminSupportConfig: (signal?: AbortSignal) =>
    request<SupportAdminConfig>('/admin/support', { signal }),
  updateAdminSupportConfig: (payload: SupportConfigUpdate) =>
    request<SupportAdminConfig>('/admin/support', {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
}


export function buildExportQuery(config: ExportConfig): string {
  const params = new URLSearchParams()
  params.set('format', config.format)
  params.set('export_type', config.exportType || 'full')
  params.set('include_highlights', String(config.includeHighlights ?? true))
  params.set('exercise_mode', String(config.exerciseMode ?? false))
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

// --- Funções de Amizade (F06) ---
export async function sendFriendRequest(username: string): Promise<FriendshipActionResponse> {
  return api.sendFriendRequest(username)
}
export async function acceptFriendRequest(requestId: number): Promise<FriendshipActionResponse> {
  return api.acceptFriendRequest(requestId)
}
export async function rejectFriendRequest(requestId: number): Promise<FriendshipActionResponse> {
  return api.rejectFriendRequest(requestId)
}
export async function cancelFriendRequest(requestId: number): Promise<FriendshipActionResponse> {
  return api.cancelFriendRequest(requestId)
}
export async function removeFriend(username: string): Promise<FriendshipActionResponse> {
  return api.removeFriend(username)
}
export async function blockUser(username: string): Promise<FriendshipActionResponse> {
  return api.blockUser(username)
}
export async function unblockUser(username: string): Promise<FriendshipActionResponse> {
  return api.unblockUser(username)
}
export async function getFriends(signal?: AbortSignal): Promise<FriendItem[]> {
  return api.getFriends(signal)
}
export async function getFriendRequests(signal?: AbortSignal): Promise<FriendRequestsResponse> {
  return api.getFriendRequests(signal)
}
export async function getBlockedUsers(signal?: AbortSignal): Promise<FriendBlockedItem[]> {
  return api.getBlockedUsers(signal)
}
export async function getFriendsSummary(signal?: AbortSignal): Promise<FriendsSummary> {
  return api.getFriendsSummary(signal)
}
export async function getRelationStatus(username: string, signal?: AbortSignal): Promise<FriendshipStatusResponse> {
  return api.getRelationStatus(username, signal)
}

export async function getSupportInfo(signal?: AbortSignal): Promise<SupportPublicInfo> {
  return api.getSupportInfo(signal)
}

export async function getAdminSupportConfig(signal?: AbortSignal): Promise<SupportAdminConfig> {
  return api.getAdminSupportConfig(signal)
}

export async function updateAdminSupportConfig(payload: SupportConfigUpdate): Promise<SupportAdminConfig> {
  return api.updateAdminSupportConfig(payload)
}

