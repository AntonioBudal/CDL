import { api } from '../services/api.ts'
import type {
  DeactivateAccountRequest,
  ReactivateAccountRequest,
  DeleteAccountRequest,
  AuditLogListResponse,
  AuthSuccessResponse,
} from '../types.ts'

export const accountApi = {
  deactivateAccount: (
    data?: DeactivateAccountRequest,
  ): Promise<{ ok: boolean; message: string }> =>
    api.deactivateAccount(data),

  reactivateAccount: (
    data: ReactivateAccountRequest,
  ): Promise<AuthSuccessResponse> =>
    api.reactivateAccount(data),

  deleteAccount: (
    data: DeleteAccountRequest,
  ): Promise<{ ok: boolean; message: string }> =>
    api.deleteAccount(data),

  exportAccountData: (): Promise<{ filename: string; blob: Blob }> =>
    api.exportAccountData(),

  getAuditLogs: (
    params?: { event_type?: string; limit?: number; offset?: number },
    signal?: AbortSignal,
  ): Promise<AuditLogListResponse> =>
    api.getAuditLogs(params, signal),
}

export default accountApi
