import { ref, computed, onMounted, onUnmounted, getCurrentInstance, type Ref, type ComputedRef } from 'vue'
import type { PaneId, LayoutMode, SplitLayoutDimensions } from '../types'

export const GLOBAL_STORAGE_KEY = 'caderno_pane_sizes_global'
export const BOOK_STORAGE_KEY_PREFIX = 'caderno_pane_sizes_book_'

export interface UseSplitPanesOptions {
  bookId?: string | number | null
  initialLeftWidth?: number
  initialRightWidth?: number
  minWidth?: number
  maxWidth?: number
  minMainWidth?: number
  snapThreshold?: number
  gutterWidth?: number
  onResizeEnd?: (dimensions: SplitLayoutDimensions) => void
}

export interface UseSplitPanesReturn {
  leftWidth: Ref<number>
  rightWidth: Ref<number>
  leftCollapsed: Ref<boolean>
  rightCollapsed: Ref<boolean>
  isDragging: Ref<boolean>
  activePane: Ref<PaneId | null>
  layoutMode: ComputedRef<LayoutMode>
  containerWidth: Ref<number | null>

  // Ações
  startDrag: (pane: PaneId, event: PointerEvent) => void
  toggleCollapse: (pane: PaneId) => void
  resetToDefault: (pane: PaneId) => void
  stepResize: (pane: PaneId, deltaPixels: number) => void
  getDimensions: () => SplitLayoutDimensions
  saveDimensions: () => void
}

/**
 * Lê dimensões salvas no localStorage com estratégia híbrida:
 * 1. Chave específica do livro (se fornecido)
 * 2. Chave global do leitor
 * 3. Null caso nenhuma esteja gravada
 */
export function loadStoredDimensions(bookId?: string | number | null): SplitLayoutDimensions | null {
  if (typeof window === 'undefined' || !window.localStorage) {
    return null
  }

  try {
    if (bookId != null && String(bookId).trim() !== '') {
      const rawBook = localStorage.getItem(`${BOOK_STORAGE_KEY_PREFIX}${bookId}`)
      if (rawBook) {
        const parsed = JSON.parse(rawBook)
        if (typeof parsed.leftWidth === 'number' && typeof parsed.rightWidth === 'number') {
          return parsed as SplitLayoutDimensions
        }
      }
    }

    const rawGlobal = localStorage.getItem(GLOBAL_STORAGE_KEY)
    if (rawGlobal) {
      const parsed = JSON.parse(rawGlobal)
      if (typeof parsed.leftWidth === 'number' && typeof parsed.rightWidth === 'number') {
        return parsed as SplitLayoutDimensions
      }
    }
  } catch (err) {
    console.warn('[useSplitPanes] Falha ao ler localStorage:', err)
  }

  return null
}

/**
 * Persiste dimensões no localStorage
 */
export function saveStoredDimensions(
  dimensions: SplitLayoutDimensions,
  bookId?: string | number | null
): void {
  if (typeof window === 'undefined' || !window.localStorage) {
    return
  }

  try {
    const payload = JSON.stringify(dimensions)
    if (bookId != null && String(bookId).trim() !== '') {
      localStorage.setItem(`${BOOK_STORAGE_KEY_PREFIX}${bookId}`, payload)
    }
    // Mantém a chave global atualizada para consistência em novos livros
    localStorage.setItem(GLOBAL_STORAGE_KEY, payload)
  } catch (err) {
    console.warn('[useSplitPanes] Falha ao salvar no localStorage:', err)
  }
}

export function useSplitPanes(options: UseSplitPanesOptions = {}): UseSplitPanesReturn {
  const minWidth = options.minWidth ?? 240
  const maxWidth = options.maxWidth ?? 600
  const defaultWidth = options.initialLeftWidth ?? 300
  const defaultRightWidth = options.initialRightWidth ?? 300
  const minMainWidth = options.minMainWidth ?? 360
  const snapThreshold = options.snapThreshold ?? 60
  const gutterWidth = options.gutterWidth ?? 8

  // Carrega configuração pré-existente
  const stored = loadStoredDimensions(options.bookId)

  const leftWidth = ref<number>(
    stored ? Math.max(minWidth, Math.min(maxWidth, stored.leftWidth)) : defaultWidth
  )
  const rightWidth = ref<number>(
    stored ? Math.max(minWidth, Math.min(maxWidth, stored.rightWidth)) : defaultRightWidth
  )
  // Conforme decisão ratificada Q1: painel direito inicia recolhido por padrão se não houver preferência salva
  const leftCollapsed = ref<boolean>(stored ? Boolean(stored.leftCollapsed) : false)
  const rightCollapsed = ref<boolean>(stored ? Boolean(stored.rightCollapsed) : true)

  const isDragging = ref<boolean>(false)
  const activePane = ref<PaneId | null>(null)
  const containerWidth = ref<number | null>(null)

  // Detecção de viewport e modo de layout
  const windowWidth = ref<number>(typeof window !== 'undefined' ? window.innerWidth : 1200)

  const layoutMode = computed<LayoutMode>(() => {
    if (windowWidth.value < 768) return 'mobile'
    if (windowWidth.value < 1024) return 'drawer'
    return 'split'
  })

  function updateWindowWidth() {
    if (typeof window !== 'undefined') {
      windowWidth.value = window.innerWidth
    }
  }

  // Registra listener de resize de janela de forma segura
  if (getCurrentInstance()) {
    onMounted(() => {
      if (typeof window !== 'undefined') {
        windowWidth.value = window.innerWidth
        window.addEventListener('resize', updateWindowWidth, { passive: true })
      }
    })

    onUnmounted(() => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('resize', updateWindowWidth)
      }
    })
  }

  function getDimensions(): SplitLayoutDimensions {
    return {
      leftWidth: leftWidth.value,
      rightWidth: rightWidth.value,
      leftCollapsed: leftCollapsed.value,
      rightCollapsed: rightCollapsed.value,
      updatedAt: new Date().toISOString()
    }
  }

  function saveDimensions(): void {
    saveStoredDimensions(getDimensions(), options.bookId)
  }

  function toggleCollapse(pane: PaneId): void {
    if (pane === 'left') {
      leftCollapsed.value = !leftCollapsed.value
      // Se estava colapsado e a largura estava abaixo do mínimo, restaura o padrão
      if (!leftCollapsed.value && leftWidth.value < minWidth) {
        leftWidth.value = defaultWidth
      }
    } else {
      rightCollapsed.value = !rightCollapsed.value
      if (!rightCollapsed.value && rightWidth.value < minWidth) {
        rightWidth.value = defaultRightWidth
      }
    }
    saveDimensions()
    options.onResizeEnd?.(getDimensions())
  }

  function resetToDefault(pane: PaneId): void {
    if (pane === 'left') {
      leftWidth.value = defaultWidth
      leftCollapsed.value = false
    } else {
      rightWidth.value = defaultRightWidth
      rightCollapsed.value = false
    }
    saveDimensions()
    options.onResizeEnd?.(getDimensions())
  }

  function stepResize(pane: PaneId, deltaPixels: number): void {
    if (pane === 'left') {
      if (leftCollapsed.value) {
        if (deltaPixels > 0) {
          leftCollapsed.value = false
          leftWidth.value = minWidth
          saveDimensions()
          options.onResizeEnd?.(getDimensions())
        }
        return
      }

      const next = leftWidth.value + deltaPixels
      if (next < snapThreshold) {
        leftCollapsed.value = true
      } else {
        leftWidth.value = Math.max(minWidth, Math.min(maxWidth, next))
      }
    } else {
      if (rightCollapsed.value) {
        if (deltaPixels > 0) {
          rightCollapsed.value = false
          rightWidth.value = minWidth
          saveDimensions()
          options.onResizeEnd?.(getDimensions())
        }
        return
      }

      const next = rightWidth.value + deltaPixels
      if (next < snapThreshold) {
        rightCollapsed.value = true
      } else {
        rightWidth.value = Math.max(minWidth, Math.min(maxWidth, next))
      }
    }
    saveDimensions()
    options.onResizeEnd?.(getDimensions())
  }

  // --- Lógica de Arrasto com PointerEvents ---
  let startX = 0
  let startWidth = 0
  let currentTarget: HTMLElement | null = null
  let capturedPointerId: number | null = null

  function handlePointerMove(e: PointerEvent): void {
    if (!isDragging.value || !activePane.value) return

    const delta = activePane.value === 'left' ? e.clientX - startX : startX - e.clientX
    const proposed = startWidth + delta

    // Snap to collapse
    if (proposed < snapThreshold) {
      if (activePane.value === 'left') {
        leftCollapsed.value = true
      } else {
        rightCollapsed.value = true
      }
      return
    }

    // Se passou do threshold, garante que o painel está visível
    if (activePane.value === 'left' && leftCollapsed.value) {
      leftCollapsed.value = false
    } else if (activePane.value === 'right' && rightCollapsed.value) {
      rightCollapsed.value = false
    }

    // Cálculo da largura máxima disponível preservando o palco principal
    const totalAvailable = containerWidth.value || (typeof window !== 'undefined' ? window.innerWidth : 1200)
    const otherWidth =
      activePane.value === 'left'
        ? rightCollapsed.value ? 0 : rightWidth.value
        : leftCollapsed.value ? 0 : leftWidth.value
    const totalGutters = 2 * gutterWidth
    const maxAllowedByMain = Math.max(minWidth, totalAvailable - otherWidth - minMainWidth - totalGutters)

    const effectiveMax = Math.min(maxWidth, maxAllowedByMain)
    const clamped = Math.max(minWidth, Math.min(effectiveMax, proposed))

    if (activePane.value === 'left') {
      leftWidth.value = clamped
    } else {
      rightWidth.value = clamped
    }
  }

  function handlePointerUp(_e: PointerEvent): void {
    if (!isDragging.value) return

    if (currentTarget && capturedPointerId !== null) {
      try {
        currentTarget.releasePointerCapture(capturedPointerId)
      } catch {
        // Ignora erro se ponteiro já foi liberado
      }
    }

    if (typeof window !== 'undefined') {
      window.removeEventListener('pointermove', handlePointerMove)
      window.removeEventListener('pointerup', handlePointerUp)
      window.removeEventListener('pointercancel', handlePointerUp)
      if (typeof document !== 'undefined') {
        document.body.classList.remove('split-resizing')
      }
    }

    isDragging.value = false
    activePane.value = null
    currentTarget = null
    capturedPointerId = null

    saveDimensions()
    options.onResizeEnd?.(getDimensions())
  }

  function startDrag(pane: PaneId, event: PointerEvent): void {
    if (event.button !== 0 && event.pointerType === 'mouse') {
      return // Apenas botão principal do mouse
    }

    event.preventDefault()
    isDragging.value = true
    activePane.value = pane
    startX = event.clientX
    startWidth = pane === 'left' ? leftWidth.value : rightWidth.value

    currentTarget = event.currentTarget as HTMLElement | null
    capturedPointerId = event.pointerId

    if (currentTarget && typeof currentTarget.setPointerCapture === 'function') {
      try {
        currentTarget.setPointerCapture(event.pointerId)
      } catch {
        // Fallback gracioso para listeners na window
      }
    }

    if (typeof window !== 'undefined') {
      window.addEventListener('pointermove', handlePointerMove)
      window.addEventListener('pointerup', handlePointerUp)
      window.addEventListener('pointercancel', handlePointerUp)
      if (typeof document !== 'undefined') {
        document.body.classList.add('split-resizing')
      }
    }
  }

  return {
    leftWidth,
    rightWidth,
    leftCollapsed,
    rightCollapsed,
    isDragging,
    activePane,
    layoutMode,
    containerWidth,

    startDrag,
    toggleCollapse,
    resetToDefault,
    stepResize,
    getDimensions,
    saveDimensions
  }
}
