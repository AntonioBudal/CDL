/**
 * useMagneticHover
 * Composable leve para gerenciamento de atração magnética sutil ao cursor.
 * Calcula deslocamento normalizado no intervalo [-1.0, 1.0] e define variáveis CSS locais.
 */

export function useMagneticHover() {
  function handlePointerMove(event: PointerEvent) {
    if (event.pointerType === 'touch') return

    const target = event.currentTarget as HTMLElement | null
    if (!target) return

    const rect = target.getBoundingClientRect()
    if (!rect.width || !rect.height) return

    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2

    // Coordenadas relativas normalizadas entre -1 e 1
    const relX = Math.max(-1, Math.min(1, (event.clientX - centerX) / (rect.width / 2)))
    const relY = Math.max(-1, Math.min(1, (event.clientY - centerY) / (rect.height / 2)))

    target.style.setProperty('--sc-magnetic-x', relX.toFixed(3))
    target.style.setProperty('--sc-magnetic-y', relY.toFixed(3))
    target.setAttribute('data-magnetic', 'active')
  }

  function handlePointerLeave(event: PointerEvent) {
    const target = event.currentTarget as HTMLElement | null
    if (!target) return

    target.style.setProperty('--sc-magnetic-x', '0')
    target.style.setProperty('--sc-magnetic-y', '0')
    target.removeAttribute('data-magnetic')
  }

  return {
    handlePointerMove,
    handlePointerLeave,
  }
}
