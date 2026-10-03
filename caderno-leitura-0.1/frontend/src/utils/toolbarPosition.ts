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

export interface PopoverPositionOptions {
  selectionRect: SelectionRect
  popoverWidth: number
  popoverHeight: number
  viewportWidth: number
  viewportHeight: number
  isMobile: boolean
  visualViewportOffsetBottom?: number
}

export interface ComputedPopoverPosition {
  top?: number
  bottom?: number
  left: number
  placement: 'top' | 'bottom'
  isMobile: boolean
  visualViewportOffsetBottom?: number
}

export function computePopoverPosition(opts: PopoverPositionOptions): ComputedPopoverPosition {
  const {
    selectionRect,
    popoverWidth,
    popoverHeight,
    viewportWidth,
    viewportHeight,
    isMobile,
    visualViewportOffsetBottom,
  } = opts

  if (isMobile) {
    const bottomOffset = visualViewportOffsetBottom && visualViewportOffsetBottom > 0
      ? visualViewportOffsetBottom
      : 0
    return {
      bottom: bottomOffset,
      left: 0,
      placement: 'bottom',
      isMobile: true,
      visualViewportOffsetBottom: bottomOffset,
    }
  }

  // Desktop: centralizado em relação à seleção
  const horizontalCenter = selectionRect.left + (selectionRect.width / 2)
  const idealLeft = horizontalCenter - (popoverWidth / 2)
  const clampedLeft = Math.max(12, Math.min(idealLeft, viewportWidth - popoverWidth - 12))

  // Vertical: Acima da seleção por padrão com respiro de 8px
  let idealTop = selectionRect.top - popoverHeight - 8
  let placement: 'top' | 'bottom' = 'top'

  if (idealTop < 10) {
    // Se não houver espaço suficiente acima, posiciona abaixo da seleção
    idealTop = selectionRect.bottom + 8
    placement = 'bottom'
  }

  // Clampa verticalmente para não extrapolar o viewport
  const clampedTop = Math.max(10, Math.min(idealTop, viewportHeight - popoverHeight - 10))

  return {
    top: Math.round(clampedTop),
    left: Math.round(clampedLeft),
    placement,
    isMobile: false,
  }
}
