export interface SelectionRect {
  top: number
  bottom: number
  left: number
  right: number
  width: number
  height: number
}

export interface ToolbarPositionOptions {
  selectionRect: SelectionRect
  toolbarWidth: number
  toolbarHeight: number
  viewportWidth: number
  viewportHeight: number
  isMobile: boolean
}

export interface ComputedPosition {
  top?: string
  bottom?: string
  left: string
  isBottomDocked: boolean
}

export function computeToolbarPosition(opts: ToolbarPositionOptions): ComputedPosition {
  const { selectionRect, toolbarWidth, toolbarHeight, viewportWidth, viewportHeight, isMobile } = opts

  if (isMobile) {
    return {
      bottom: '0px',
      left: '0px',
      isBottomDocked: true,
    }
  }

  // Desktop: Centralizado horizontalmente em relação à seleção
  const horizontalCenter = selectionRect.left + (selectionRect.width / 2)
  const idealLeft = horizontalCenter - (toolbarWidth / 2)
  const clampedLeft = Math.max(12, Math.min(idealLeft, viewportWidth - toolbarWidth - 12))

  // Vertical: Acima da seleção por padrão
  let idealTop = selectionRect.top - toolbarHeight - 10
  if (idealTop < 10) {
    // Se estourar o topo da tela, posiciona abaixo da seleção
    idealTop = selectionRect.bottom + 10
  }

  // Clampa verticalmente
  const clampedTop = Math.max(10, Math.min(idealTop, viewportHeight - toolbarHeight - 10))

  return {
    top: `${Math.round(clampedTop)}px`,
    left: `${Math.round(clampedLeft)}px`,
    isBottomDocked: false,
  }
}
