import { onBeforeUnmount, onMounted, ref, type Ref } from 'vue'
import type { StudySectionKey, TextSelectionContext } from '../types.ts'

export interface OffsetCalculationResult {
  start_offset: number
  end_offset: number
  selected_text: string
  prefix: string
  suffix: string
}

export interface WordBoundariesResult {
  start: number
  end: number
  word: string
}

export interface DoubleTapCheckParams {
  lastTapTimestamp: number
  lastTapX: number
  lastTapY: number
  currentTapTimestamp: number
  currentTapX: number
  currentTapY: number
  isScrolling: boolean
  maxIntervalMs?: number
  maxDistancePx?: number
}

/**
 * Localiza limites de palavra em torno de uma posição (offset) em um texto.
 * Considera pontuação, quebras de linha e caracteres alfanuméricos com acentuação.
 */
export function findWordBoundaries(text: string, offset: number): WordBoundariesResult | null {
  if (!text || offset < 0 || offset > text.length) return null

  const isWordChar = (char: string) => /[a-zA-Z0-9À-ÿ_]/.test(char)

  let start = offset
  let end = offset

  // Se o ponto estiver em um espaço ou pontuação, verifica se o caractere imediatamente anterior pertence à palavra
  if ((start >= text.length || !isWordChar(text[start])) && start > 0 && isWordChar(text[start - 1])) {
    start = start - 1
    end = start
  }

  if (start >= text.length || !isWordChar(text[start])) {
    return null
  }

  while (start > 0 && isWordChar(text[start - 1])) {
    start--
  }
  while (end < text.length && isWordChar(text[end])) {
    end++
  }

  if (start < end) {
    return {
      start,
      end,
      word: text.slice(start, end),
    }
  }

  return null
}

/**
 * Expande uma Range de seleção pontual para os limites da palavra correspondente.
 */
export function expandRangeToWord(range: Range): Range | null {
  const container = range.startContainer
  if (container.nodeType !== Node.TEXT_NODE) return null
  const text = container.textContent || ''
  const offset = range.startOffset

  const boundaries = findWordBoundaries(text, offset)
  if (!boundaries) return null

  try {
    const newRange = document.createRange()
    newRange.setStart(container, boundaries.start)
    newRange.setEnd(container, boundaries.end)
    return newRange
  } catch {
    return null
  }
}

/**
 * Avalia se dois toques sucessivos configuram um duplo toque legítimo.
 */
export function isDoubleTap(params: DoubleTapCheckParams): boolean {
  if (params.isScrolling) return false
  const timeDiff = params.currentTapTimestamp - params.lastTapTimestamp
  if (timeDiff <= 0 || timeDiff > (params.maxIntervalMs ?? 320)) return false
  const dist = Math.hypot(params.currentTapX - params.lastTapX, params.currentTapY - params.lastTapY)
  return dist <= (params.maxDistancePx ?? 15)
}

/**
 * Obtém Range pontual a partir de coordenadas da tela.
 */
export function getRangeFromPoint(x: number, y: number): Range | null {
  if (typeof document === 'undefined') return null
  if (document.caretRangeFromPoint) {
    return document.caretRangeFromPoint(x, y)
  }
  if ('caretPositionFromPoint' in document) {
    const doc = document as unknown as { caretPositionFromPoint: (x: number, y: number) => { offsetNode: Node; offset: number } | null }
    const pos = doc.caretPositionFromPoint(x, y)
    if (pos && pos.offsetNode) {
      const range = document.createRange()
      range.setStart(pos.offsetNode, pos.offset)
      range.setEnd(pos.offsetNode, pos.offset)
      return range
    }
  }
  return null
}

export function calculateOffsetsFromText(
  fullText: string,
  selectedText: string,
  approximateIndex: number = 0,
): OffsetCalculationResult | null {
  if (!fullText || !selectedText) return null

  const target = selectedText.trim()
  if (!target) return null

  // Encontra todas as ocorrências de target no texto
  const indices: number[] = []
  let pos = fullText.indexOf(target)
  while (pos !== -1) {
    indices.push(pos)
    pos = fullText.indexOf(target, pos + 1)
  }

  if (indices.length === 0) {
    // Tenta busca case-insensitive caso haja pequenas variações de maiúsculas
    const lowerFull = fullText.toLowerCase()
    const lowerTarget = target.toLowerCase()
    pos = lowerFull.indexOf(lowerTarget)
    while (pos !== -1) {
      indices.push(pos)
      pos = lowerFull.indexOf(lowerTarget, pos + 1)
      if (indices.length > 50) break
    }
  }

  if (indices.length === 0) return null

  // Escolhe a ocorrência mais próxima de approximateIndex
  let bestIndex = indices[0]!
  let minDiff = Math.abs(bestIndex - approximateIndex)
  for (let i = 1; i < indices.length; i++) {
    const diff = Math.abs(indices[i]! - approximateIndex)
    if (diff < minDiff) {
      minDiff = diff
      bestIndex = indices[i]!
    }
  }

  const start_offset = bestIndex
  const end_offset = bestIndex + target.length
  const prefixStart = Math.max(0, start_offset - 30)
  const suffixEnd = Math.min(fullText.length, end_offset + 30)

  return {
    start_offset,
    end_offset,
    selected_text: target,
    prefix: fullText.slice(prefixStart, start_offset),
    suffix: fullText.slice(end_offset, suffixEnd),
  }
}

export function formatQuoteText(params: {
  selected_text: string
  studyTitle: string
  bookTitle?: string
  chapterName?: string
}): string {
  const { selected_text, studyTitle, bookTitle, chapterName } = params
  const cleanSnippet = selected_text.trim()

  const attributionParts: string[] = []
  if (studyTitle) attributionParts.push(`*${studyTitle}*`)
  if (chapterName) attributionParts.push(chapterName)
  if (bookTitle) attributionParts.push(`(${bookTitle})`)

  const attribution = attributionParts.join(', ')

  return `> "${cleanSnippet}"\n>\n> — ${attribution}\n`
}

export function useTextSelection(
  containerRef: Ref<HTMLElement | null>,
  currentSection: Ref<StudySectionKey>,
) {
  const selectionContext = ref<TextSelectionContext | null>(null)
  const isSelecting = ref(false)

  // Rastreamento de toques móveis
  let lastTapTimestamp = 0
  let lastTapX = 0
  let lastTapY = 0
  let touchStartX = 0
  let touchStartY = 0
  let isScrolling = false

  function clearSelection() {
    selectionContext.value = null
    const sel = typeof window !== 'undefined' ? window.getSelection() : null
    if (sel && sel.rangeCount > 0) {
      sel.removeAllRanges()
    }
  }

  function handleSelection() {
    if (typeof window === 'undefined') return
    const selection = window.getSelection()
    if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
      selectionContext.value = null
      return
    }

    const text = selection.toString().trim()
    if (text.length < 2) {
      selectionContext.value = null
      return
    }

    const container = containerRef.value
    if (!container) return

    const range = selection.getRangeAt(0)
    // Verifica se a seleção está contida no container do estudo
    if (!container.contains(range.commonAncestorContainer)) {
      selectionContext.value = null
      return
    }

    // Calcula o offset de início criando uma range do início do container até a range selecionada
    const preRange = document.createRange()
    preRange.selectNodeContents(container)
    preRange.setEnd(range.startContainer, range.startOffset)
    const approxStart = preRange.toString().length

    const fullContainerText = container.textContent || ''
    const offsets = calculateOffsetsFromText(fullContainerText, text, approxStart)
    if (!offsets) {
      selectionContext.value = null
      return
    }

    const boundingRect = range.getBoundingClientRect()

    selectionContext.value = {
      section: currentSection.value,
      selected_text: offsets.selected_text,
      prefix: offsets.prefix,
      suffix: offsets.suffix,
      start_offset: offsets.start_offset,
      end_offset: offsets.end_offset,
      boundingRect,
    }
  }

  function onMouseUp(event: MouseEvent) {
    const target = event.target as HTMLElement | null
    if (target && target.closest('.floating-actions-toolbar')) {
      return
    }
    setTimeout(handleSelection, 20)
  }

  function onDblClick(event: MouseEvent) {
    const target = event.target as HTMLElement | null
    if (target && target.closest('.floating-actions-toolbar')) {
      return
    }
    setTimeout(handleSelection, 20)
  }

  function onTouchStart(e: TouchEvent) {
    if (!e.touches || e.touches.length === 0) return
    const touch = e.touches[0]
    touchStartX = touch.clientX
    touchStartY = touch.clientY
    isScrolling = false
  }

  function onTouchMove(e: TouchEvent) {
    if (!e.touches || e.touches.length === 0) return
    const touch = e.touches[0]
    const dx = touch.clientX - touchStartX
    const dy = touch.clientY - touchStartY
    if (Math.hypot(dx, dy) > 15) {
      isScrolling = true
    }
  }

  function onTouchEnd(e: TouchEvent) {
    const target = e.target as HTMLElement | null
    if (target && target.closest('.floating-actions-toolbar')) {
      return
    }

    // Se houve rolagem acima do limiar, preserva seleção atual sem cancelar ou forçar seleção incorreta
    if (isScrolling) {
      return
    }

    if (!e.changedTouches || e.changedTouches.length === 0) {
      setTimeout(handleSelection, 20)
      return
    }

    const touch = e.changedTouches[0]
    const currentTapX = touch.clientX
    const currentTapY = touch.clientY
    const currentTapTimestamp = Date.now()

    const doubleTapDetected = isDoubleTap({
      lastTapTimestamp,
      lastTapX,
      lastTapY,
      currentTapTimestamp,
      currentTapX,
      currentTapY,
      isScrolling,
      maxIntervalMs: 320,
      maxDistancePx: 15,
    })

    if (doubleTapDetected) {
      if (e.cancelable) {
        e.preventDefault()
      }
      lastTapTimestamp = 0
      // Tenta expandir palavra sob o ponto se a seleção nativa estiver colapsada
      if (typeof window !== 'undefined') {
        const sel = window.getSelection()
        if (!sel || sel.rangeCount === 0 || sel.isCollapsed) {
          const pointRange = getRangeFromPoint(currentTapX, currentTapY)
          if (pointRange) {
            const wordRange = expandRangeToWord(pointRange)
            if (wordRange && sel) {
              sel.removeAllRanges()
              sel.addRange(wordRange)
            }
          }
        }
      }
      setTimeout(handleSelection, 20)
    } else {
      lastTapTimestamp = currentTapTimestamp
      lastTapX = currentTapX
      lastTapY = currentTapY
      setTimeout(handleSelection, 20)
    }
  }

  function onKeyUp(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      clearSelection()
      return
    }
    if (event.key === 'Shift' || event.key.startsWith('Arrow')) {
      handleSelection()
    }
  }

  onMounted(() => {
    if (typeof document === 'undefined') return
    document.addEventListener('mouseup', onMouseUp)
    document.addEventListener('dblclick', onDblClick)
    document.addEventListener('touchstart', onTouchStart, { passive: true })
    document.addEventListener('touchmove', onTouchMove, { passive: true })
    document.addEventListener('touchend', onTouchEnd)
    document.addEventListener('keyup', onKeyUp)
  })

  onBeforeUnmount(() => {
    if (typeof document === 'undefined') return
    document.removeEventListener('mouseup', onMouseUp)
    document.removeEventListener('dblclick', onDblClick)
    document.removeEventListener('touchstart', onTouchStart)
    document.removeEventListener('touchmove', onTouchMove)
    document.removeEventListener('touchend', onTouchEnd)
    document.removeEventListener('keyup', onKeyUp)
  })

  return {
    selectionContext,
    isSelecting,
    clearSelection,
    handleSelection,
  }
}
