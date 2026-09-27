import { onBeforeUnmount, onMounted, ref, type Ref } from 'vue'
import type { StudySectionKey, TextSelectionContext } from '../types.ts'

export interface OffsetCalculationResult {
  start_offset: number
  end_offset: number
  selected_text: string
  prefix: string
  suffix: string
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

  function onMouseUp() {
    setTimeout(handleSelection, 20)
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
    document.addEventListener('touchend', onMouseUp)
    document.addEventListener('keyup', onKeyUp)
  })

  onBeforeUnmount(() => {
    if (typeof document === 'undefined') return
    document.removeEventListener('mouseup', onMouseUp)
    document.removeEventListener('touchend', onMouseUp)
    document.removeEventListener('keyup', onKeyUp)
  })

  return {
    selectionContext,
    isSelecting,
    clearSelection,
    handleSelection,
  }
}
