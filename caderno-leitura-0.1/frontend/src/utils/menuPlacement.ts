// F0.12.10 (spec 123): onde abrir um menu suspenso para ele caber na tela. Função pura (testada sem navegador).
// Horizontal: alinha ao gatilho (direita ou esquerda) e encosta dentro da tela com margem. Vertical: abre embaixo;
// se não couber (descontando a barra de baixo do celular), abre em cima; se não couber em nenhum, rola por dentro.

export interface MenuRect {
  left: number
  right: number
  top: number
  bottom: number
}

export interface MenuPlacementInput {
  trigger: MenuRect
  menu: { width: number; height: number }
  viewport: { width: number; height: number }
  align: 'left' | 'right'
  /** Altura ocupada embaixo por barras fixas (ex.: navegação do celular). */
  bottomInset?: number
  margin?: number
  gap?: number
}

export interface MenuPlacement {
  left: number
  top: number
  maxHeight: number
  openUp: boolean
}

export function placeMenu({
  trigger,
  menu,
  viewport,
  align,
  bottomInset = 0,
  margin = 8,
  gap = 6,
}: MenuPlacementInput): MenuPlacement {
  const width = Math.min(menu.width, viewport.width - margin * 2)
  const idealLeft = align === 'right' ? trigger.right - width : trigger.left
  const left = Math.max(margin, Math.min(idealLeft, viewport.width - width - margin))

  const usableBottom = viewport.height - bottomInset - margin
  const spaceBelow = usableBottom - (trigger.bottom + gap)
  const spaceAbove = trigger.top - gap - margin

  if (menu.height <= spaceBelow) {
    return { left, top: trigger.bottom + gap, maxHeight: menu.height, openUp: false }
  }
  if (menu.height <= spaceAbove) {
    return { left, top: trigger.top - gap - menu.height, maxHeight: menu.height, openUp: true }
  }
  // Não cabe inteiro: usa o lado com mais espaço e rola por dentro.
  if (spaceBelow >= spaceAbove) {
    return { left, top: trigger.bottom + gap, maxHeight: Math.max(120, spaceBelow), openUp: false }
  }
  const maxHeight = Math.max(120, spaceAbove)
  return { left, top: trigger.top - gap - maxHeight, maxHeight, openUp: true }
}
