import type { RouteLocationRaw } from 'vue-router'
import type { IconName } from '../types'

/**
 * Item individual de trilha de navegação (Breadcrumb).
 */
export interface BreadcrumbItem {
  /** Rótulo legível exibido no item */
  label: string
  /** Destino da rota. Se omitido ou current = true, renderizado como texto/página atual */
  to?: RouteLocationRaw
  /** Indica se é a página ativa/atual */
  current?: boolean
}

/**
 * Item primário da barra de navegação desktop.
 */
export interface PrimaryNavItem {
  to: string
  label: string
  routes: string[]
  icon: IconName
  badgeCount?: () => number
}

/**
 * Item secundário exibido no dropdown "Mais".
 */
export interface SecondaryNavItem {
  to: string
  label: string
  routes: string[]
  icon: IconName
  requiresAdmin?: boolean
  badgeCount?: () => number
}
