// Decisão de navegação do router.beforeEach, sem Vue nem window, para poder ser testada.

export const SETUP_PATH = '/primeiro-acesso'
const AUTH_PATHS = ['/login', '/registro', SETUP_PATH]

export interface GuardInput {
  path: string
  fullPath: string
  isPublicMeta: boolean
  requiresAdmin: boolean
  isAuthenticated: boolean
  isAdmin: boolean
  ownerSetupRequired: boolean
  /** Valor de `caderno_home_view` no localStorage, ou null. */
  homePreference: string | null
}

export type GuardResult = null | string | { path: string; query?: Record<string, string> }

/** Para onde redirecionar a navegação; `null` deixa seguir. */
export function resolveNavigation(input: GuardInput): GuardResult {
  // Enquanto o proprietário não cadastrou a senha mestra inicial, só o primeiro acesso é permitido. A regra vem
  // antes da de usuário autenticado: sem login obrigatório, o proprietário já chega autenticado e, sem isto, as
  // duas regras se redirecionavam uma para a outra sem fim.
  if (input.ownerSetupRequired) {
    return input.path === SETUP_PATH ? null : SETUP_PATH
  }

  const isPublicRoute = input.isPublicMeta || AUTH_PATHS.includes(input.path)

  // Não autenticado em rota protegida
  if (!input.isAuthenticated && !isPublicRoute) {
    return { path: '/login', query: input.fullPath !== '/' ? { redirect: input.fullPath } : undefined }
  }

  // Autenticado na raiz (Landing Page) ou nas telas de login, registro e primeiro acesso
  if (input.isAuthenticated && (input.path === '/' || AUTH_PATHS.includes(input.path))) {
    return input.homePreference === 'dashboard' ? '/dashboard' : '/livros'
  }

  // Rota que exige administrador (RBAC)
  if ((input.requiresAdmin || input.path === '/admin') && !input.isAdmin) {
    return { path: '/livros', query: { aviso: 'acesso-restrito' } }
  }

  return null
}
