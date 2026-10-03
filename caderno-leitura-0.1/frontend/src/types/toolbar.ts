export type HighlightColor = 'yellow' | 'green' | 'blue' | 'pink' | 'purple'

export const HIGHLIGHT_COLORS: readonly HighlightColor[] = [
  'yellow',
  'green',
  'blue',
  'pink',
  'purple',
] as const

export const HIGHLIGHT_COLOR_HEX: Record<HighlightColor, string> = {
  yellow: '#fef08a',
  green: '#bbf7d0',
  blue: '#bae6fd',
  pink: '#fbcfe8',
  purple: '#e9d5ff',
}

export const HIGHLIGHT_COLOR_BORDER: Record<HighlightColor, string> = {
  yellow: '#facc15',
  green: '#4ade80',
  blue: '#38bdf8',
  pink: '#f472b6',
  purple: '#c084fc',
}

export const HIGHLIGHT_COLOR_LABELS: Record<HighlightColor, string> = {
  yellow: 'Amarelo',
  green: 'Verde',
  blue: 'Azul',
  pink: 'Rosa',
  purple: 'Lilás',
}

export interface HighlightColorOption {
  id: HighlightColor
  label: string
  bg: string
  border: string
}

export const HIGHLIGHT_COLOR_OPTIONS: readonly HighlightColorOption[] = [
  { id: 'yellow', label: 'Amarelo', bg: '#fef08a', border: '#facc15' },
  { id: 'green', label: 'Verde', bg: '#bbf7d0', border: '#4ade80' },
  { id: 'blue', label: 'Azul', bg: '#bae6fd', border: '#38bdf8' },
  { id: 'pink', label: 'Rosa', bg: '#fbcfe8', border: '#f472b6' },
  { id: 'purple', label: 'Lilás', bg: '#e9d5ff', border: '#c084fc' },
] as const

export type ToolbarMode =
  | 'idle'
  | 'color_palette'
  | 'note_popover'
  | 'question_popover'

export type PopoverKind = 'note' | 'question'

export interface PopoverPosition {
  top?: number
  bottom?: number
  left: number
  placement: 'top' | 'bottom'
  isMobile: boolean
  visualViewportOffsetBottom?: number
}
