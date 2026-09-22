import { computed, ref } from 'vue'
import { api } from '../services/api.ts'

import type { AuthConfigResponse, SessionItem, UserRead } from '../types.ts'

const currentUser = ref<UserRead | null>(null)
const currentSessionId = ref<string | null>(null)
const ownerSetupRequired = ref<boolean>(false)
const allowRegistration = ref<boolean>(true)
const isInitialized = ref<boolean>(false)
const isLoading = ref<boolean>(false)

export function useAuthStore() {
  const user = computed(() => currentUser.value)
  const isAuthenticated = computed(() => currentUser.value !== null)

  async function checkAuth(force: boolean = false): Promise<boolean> {
    if (isInitialized.value && !force) {
      return isAuthenticated.value
    }
    isLoading.value = true
    try {
      // 1. Carrega configuração pública do servidor
      try {
        const config: AuthConfigResponse = await api.getAuthConfig()
        ownerSetupRequired.value = config.owner_setup_required
        allowRegistration.value = config.allow_registration
      } catch {
        // Fallback defensivo caso o endpoint não responda
        ownerSetupRequired.value = false
        allowRegistration.value = true
      }

      // 2. Consulta usuário autenticado via cookie de sessão
      const user = await api.getMe()
      currentUser.value = user
      isInitialized.value = true
      return true
    } catch (err) {
      currentUser.value = null
      isInitialized.value = true
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function login(usernameOrEmail: string, password: string): Promise<UserRead> {
    isLoading.value = true
    try {
      const response = await api.login(usernameOrEmail, password)
      currentUser.value = response.user
      currentSessionId.value = response.session_id
      ownerSetupRequired.value = false
      isInitialized.value = true
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('caderno_auth_changed'))
      }
      return response.user
    } finally {
      isLoading.value = false
    }
  }

  async function setupOwner(password: string): Promise<UserRead> {
    isLoading.value = true
    try {
      const response = await api.setupOwner(password)
      currentUser.value = response.user
      currentSessionId.value = response.session_id
      ownerSetupRequired.value = false
      isInitialized.value = true
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('caderno_auth_changed'))
      }
      return response.user
    } finally {
      isLoading.value = false
    }
  }

  async function register(payload: {
    username: string
    display_name: string
    email?: string | null
    password: string
  }): Promise<UserRead> {
    isLoading.value = true
    try {
      const response = await api.register(payload)
      currentUser.value = response.user
      currentSessionId.value = response.session_id
      isInitialized.value = true
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('caderno_auth_changed'))
      }
      return response.user
    } finally {
      isLoading.value = false
    }
  }

  async function logout(): Promise<void> {
    try {
      await api.logout()
    } catch {
      // Ignora erro de rede no logout
    } finally {
      currentUser.value = null
      currentSessionId.value = null
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('caderno_auth_changed'))
      }
    }
  }

  async function fetchSessions(): Promise<SessionItem[]> {
    return await api.getSessions()
  }

  async function revokeSession(sessionId: string): Promise<void> {
    await api.revokeSession(sessionId)
  }

  async function logoutAll(): Promise<number> {
    const res = await api.logoutAll()
    return res.revoked_count
  }

  return {
    currentUser,
    user,
    currentSessionId,
    ownerSetupRequired,
    allowRegistration,
    isInitialized,
    isLoading,
    isAuthenticated,
    checkAuth,
    login,
    setupOwner,
    register,
    logout,
    fetchSessions,
    revokeSession,
    logoutAll,
  }
}

