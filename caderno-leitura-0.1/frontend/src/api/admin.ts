import { api } from '../services/api.ts'
import type {
  AdminReactivateResponse,
  AdminRevokeSessionsResponse,
  AdminRoleUpdateRequest,
  AdminRoleUpdateResponse,
  AdminStatsSummary,
  AdminSuspendRequest,
  AdminSuspendResponse,
  AdminUsersFilter,
  AdminUsersResponse,
} from '../types/admin.ts'

export const adminApi = {
  getUsers: (params?: AdminUsersFilter, signal?: AbortSignal): Promise<AdminUsersResponse> =>
    api.getAdminUsers(params, signal),

  getStats: (signal?: AbortSignal): Promise<AdminStatsSummary> =>
    api.getAdminStats(signal),

  suspendUser: (userId: string, payload?: AdminSuspendRequest): Promise<AdminSuspendResponse> =>
    api.suspendUser(userId, payload),

  reactivateUser: (userId: string): Promise<AdminReactivateResponse> =>
    api.reactivateUser(userId),

  updateUserRole: (userId: string, payload: AdminRoleUpdateRequest): Promise<AdminRoleUpdateResponse> =>
    api.updateUserRole(userId, payload),

  revokeAllSessions: (userId: string): Promise<AdminRevokeSessionsResponse> =>
    api.revokeAllSessions(userId),
}

export default adminApi
