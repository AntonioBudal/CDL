export type UserRole = 'user' | 'admin'
export type UserStatus = 'ativo' | 'suspenso'
export type LoginProvider = 'local' | 'google' | 'ambos'

export interface AdminUserItem {
  id: string
  username: string
  display_name: string
  email: string | null
  role: UserRole
  status: UserStatus
  provider: LoginProvider
  created_at: string
  last_access: string
  studies_count: number
  books_count: number
  active_sessions_count: number
}

export interface AdminUsersResponse {
  items: AdminUserItem[]
  total: number
}

export interface AdminStatsSummary {
  total_users: number
  active_users: number
  suspended_users: number
  admin_users: number
  total_studies: number
}

export interface AdminSuspendRequest {
  reason?: string
}

export interface AdminSuspendResponse {
  id: string
  status: 'suspenso'
  sessions_revoked: number
  message: string
}

export interface AdminReactivateResponse {
  id: string
  status: 'ativo'
  message: string
}

export interface AdminRoleUpdateRequest {
  role: UserRole
}

export interface AdminRoleUpdateResponse {
  id: string
  role: UserRole
  message: string
}

export interface AdminRevokeSessionsResponse {
  id: string
  sessions_revoked: number
  message: string
}

export interface AdminUsersFilter {
  q?: string
  status?: 'all' | 'ativo' | 'suspenso'
  role?: 'all' | 'user' | 'admin'
  limit?: number
  offset?: number
}
