import { api } from '../services/api.ts'
import type {
  AuthConfigResponse,
  AuthSuccessResponse,
  ExternalIdentityRead,
  SessionItem,
  UserRead,
} from '../types.ts'

export const authApi = {
  getMe: (signal?: AbortSignal): Promise<UserRead> => api.getMe(signal),
  getAuthConfig: (signal?: AbortSignal): Promise<AuthConfigResponse> => api.getAuthConfig(signal),
  setupOwner: (password: string): Promise<AuthSuccessResponse> => api.setupOwner(password),
  register: (payload: {
    username: string
    display_name: string
    email?: string | null
    password: string
  }): Promise<AuthSuccessResponse> => api.register(payload),
  login: (usernameOrEmail: string, password: string): Promise<AuthSuccessResponse> =>
    api.login(usernameOrEmail, password),
  logout: (): Promise<{ ok: boolean }> => api.logout(),
  getSessions: (signal?: AbortSignal): Promise<SessionItem[]> => api.getSessions(signal),
  revokeSession: (sessionId: string): Promise<void> => api.revokeSession(sessionId),
  logoutAll: (): Promise<{ revoked_count: number }> => api.logoutAll(),
  loginWithGoogle: (credential: string): Promise<AuthSuccessResponse> =>
    api.loginWithGoogle(credential),
  linkGoogle: (credential: string): Promise<ExternalIdentityRead> => api.linkGoogle(credential),
  unlinkGoogle: (): Promise<{ ok: boolean }> => api.unlinkGoogle(),
}

export default authApi
