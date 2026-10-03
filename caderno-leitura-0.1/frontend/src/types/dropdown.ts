import type { RouteLocationRaw } from 'vue-router'

export type DropdownItemVariant = 'default' | 'danger'
export type DropdownMenuAlign = 'left' | 'right'

export interface DropdownMenuItem {
  id: string
  label: string
  variant?: DropdownItemVariant
  to?: RouteLocationRaw
  action?: () => void | Promise<void>
  disabled?: boolean
  visible?: boolean
  dividerBefore?: boolean
}

export interface DropdownMenuProps {
  align?: DropdownMenuAlign
  ariaLabel?: string
  disabled?: boolean
}
