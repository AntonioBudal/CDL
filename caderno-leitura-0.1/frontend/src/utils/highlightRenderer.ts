import type { StudyHighlight } from '../types.ts'

export interface HighlightClickEvent {
  highlight: StudyHighlight
  targetElement: HTMLElement
  boundingRect: DOMRect
}

export function findBestMatchOffset(
  fullText: string,
  targetText: string,
  approximateOffset: number = 0,
): number {
  if (!fullText || !targetText) return -1
  const target = targetText.trim()
  if (!target) return -1

  const indices: number[] = []
  let pos = fullText.indexOf(target)
  while (pos !== -1) {
    indices.push(pos)
    pos = fullText.indexOf(target, pos + 1)
  }

  if (indices.length === 0) {
    const lowerFull = fullText.toLowerCase()
    const lowerTarget = target.toLowerCase()
    pos = lowerFull.indexOf(lowerTarget)
    while (pos !== -1) {
      indices.push(pos)
      pos = lowerFull.indexOf(lowerTarget, pos + 1)
      if (indices.length > 50) break
    }
  }

  if (indices.length === 0) return -1

  let bestIndex = indices[0]!
  let minDiff = Math.abs(bestIndex - approximateOffset)
  for (let i = 1; i < indices.length; i++) {
    const diff = Math.abs(indices[i]! - approximateOffset)
    if (diff < minDiff) {
      minDiff = diff
      bestIndex = indices[i]!
    }
  }

  return bestIndex
}

export function getHighlightClassNames(hl: StudyHighlight): string {
  if (hl.kind === 'hidden') {
    return 'study-occlusion hl-hidden'
  }
  if (hl.kind === 'question') {
    return 'study-question-target hl-question'
  }
  if (hl.kind === 'note') {
    return `study-highlight study-note hl-${hl.color}`
  }
  if (hl.kind === 'quote') {
    return `study-highlight study-quote hl-${hl.color}`
  }
  return `study-highlight hl-${hl.color}`
}

export function removeHighlightsFromDom(root: HTMLElement): void {
  const marks = root.querySelectorAll<HTMLElement>('[data-highlight-id]')
  marks.forEach((mark) => {
    // Se tiver widgets injetados (como botão de revelar ou pergunta), remove-os
    const widgets = mark.querySelectorAll('.study-occlusion-btn, .study-question-badge, .study-note-badge')
    widgets.forEach((w) => w.remove())

    const parent = mark.parentNode
    if (!parent) return
    while (mark.firstChild) {
      parent.insertBefore(mark.firstChild, mark)
    }
    parent.removeChild(mark)
  })
  root.normalize()
}

export function applyHighlightsToDom(
  root: HTMLElement,
  highlights: StudyHighlight[],
  onHighlightClick?: (event: HighlightClickEvent) => void,
  onToggleActiveHighlight?: (id: number, isRevealed: boolean) => void,
): () => void {
  if (typeof document === 'undefined') return () => {}

  // 1. Remove destaques anteriores
  removeHighlightsFromDom(root)

  if (!highlights || highlights.length === 0) {
    return () => {}
  }

  const fullText = root.textContent || ''
  if (!fullText.trim()) return () => {}

  // 2. Ordena os destaques por offset descendente para evitar invalidar posições
  const sorted = [...highlights].sort((a, b) => b.start_offset - a.start_offset)

  for (const hl of sorted) {
    wrapSingleHighlight(root, hl, fullText)
  }

  // 3. Listener delegado de clique
  function handleClick(e: MouseEvent) {
    const target = e.target as HTMLElement
    const mark = target.closest<HTMLElement>('[data-highlight-id]')
    if (!mark || !root.contains(mark)) return

    // Se clicou no botão de revelar da oclusão, alterna estado
    if (target.classList.contains('study-occlusion-btn')) {
      e.stopPropagation()
      const hlId = Number(mark.getAttribute('data-highlight-id'))
      mark.classList.toggle('is-revealed')
      const isRev = mark.classList.contains('is-revealed')
      target.textContent = isRev ? 'Ocultar' : 'Revelar'
      mark.dispatchEvent(new CustomEvent('study-active-toggle', {
        bubbles: true,
        detail: { id: hlId, isRevealed: isRev },
      }))
      if (onToggleActiveHighlight && !Number.isNaN(hlId)) {
        onToggleActiveHighlight(hlId, isRev)
      }
      return
    }

    // Se clicou no botão de ver resposta da pergunta, alterna estado
    if (target.classList.contains('study-question-reveal-btn')) {
      e.stopPropagation()
      const hlId = Number(mark.getAttribute('data-highlight-id'))
      mark.classList.toggle('is-revealed')
      const isRev = mark.classList.contains('is-revealed')
      target.textContent = isRev ? 'Esconder resposta' : 'Ver resposta'
      mark.dispatchEvent(new CustomEvent('study-active-toggle', {
        bubbles: true,
        detail: { id: hlId, isRevealed: isRev },
      }))
      if (onToggleActiveHighlight && !Number.isNaN(hlId)) {
        onToggleActiveHighlight(hlId, isRev)
      }
      return
    }

    const hlId = Number(mark.getAttribute('data-highlight-id'))
    const found = highlights.find((h) => h.id === hlId)
    if (found && onHighlightClick) {
      e.stopPropagation()
      onHighlightClick({
        highlight: found,
        targetElement: mark,
        boundingRect: mark.getBoundingClientRect(),
      })
    }
  }

  root.addEventListener('click', handleClick)
  return () => {
    root.removeEventListener('click', handleClick)
  }
}

export function setHighlightsRevealedState(
  root: HTMLElement,
  revealed: boolean,
  onToggleCallback?: (id: number, isRevealed: boolean) => void,
): void {
  if (!root) return
  const marks = root.querySelectorAll<HTMLElement>('[data-highlight-id][data-kind="hidden"], [data-highlight-id][data-kind="question"]')
  marks.forEach((mark) => {
    const id = Number(mark.getAttribute('data-highlight-id'))
    const kind = mark.getAttribute('data-kind')
    if (revealed) {
      mark.classList.add('is-revealed')
    } else {
      mark.classList.remove('is-revealed')
    }
    if (kind === 'hidden') {
      const btn = mark.querySelector<HTMLButtonElement>('.study-occlusion-btn')
      if (btn) {
        btn.textContent = revealed ? 'Ocultar' : 'Revelar'
      }
    } else if (kind === 'question') {
      const btn = mark.querySelector<HTMLButtonElement>('.study-question-reveal-btn')
      if (btn) {
        btn.textContent = revealed ? 'Esconder resposta' : 'Ver resposta'
      }
    }
    if (onToggleCallback && !Number.isNaN(id)) {
      onToggleCallback(id, revealed)
    }
  })
}

export function collectInteractiveHighlights(
  root: HTMLElement,
): { id: number; kind: 'hidden' | 'question'; isRevealed: boolean }[] {
  if (!root) return []
  const marks = root.querySelectorAll<HTMLElement>('[data-highlight-id][data-kind="hidden"], [data-highlight-id][data-kind="question"]')
  const result: { id: number; kind: 'hidden' | 'question'; isRevealed: boolean }[] = []
  const seenIds = new Set<number>()

  marks.forEach((mark) => {
    const id = Number(mark.getAttribute('data-highlight-id'))
    const kind = mark.getAttribute('data-kind') as 'hidden' | 'question'
    if (!Number.isNaN(id) && !seenIds.has(id)) {
      seenIds.add(id)
      result.push({
        id,
        kind,
        isRevealed: mark.classList.contains('is-revealed'),
      })
    }
  })
  return result
}

export function scrollAndFocusHighlight(
  root: HTMLElement,
  highlightId: number,
): boolean {
  if (!root) return false
  const mark = root.querySelector<HTMLElement>(`[data-highlight-id="${highlightId}"]`)
  if (!mark) return false

  root.querySelectorAll('.study-highlight-focused').forEach((el) => {
    el.classList.remove('study-highlight-focused')
  })

  mark.classList.add('study-highlight-focused')
  if (typeof mark.scrollIntoView === 'function') {
    mark.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  const focusTarget = mark.querySelector<HTMLElement>('button') || mark
  if (focusTarget) {
    if (!focusTarget.hasAttribute('tabindex') && focusTarget !== mark.querySelector('button')) {
      focusTarget.setAttribute('tabindex', '-1')
    }
    if (typeof focusTarget.focus === 'function') {
      focusTarget.focus({ preventScroll: true })
    }
  }
  return true
}

function wrapSingleHighlight(root: HTMLElement, hl: StudyHighlight, fullText: string): void {
  const matchIndex = findBestMatchOffset(fullText, hl.selected_text, hl.start_offset)
  if (matchIndex === -1) return

  const targetStart = matchIndex
  const targetEnd = matchIndex + hl.selected_text.trim().length

  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null)
  let currentOffset = 0
  const nodesToWrap: { node: Text; startInNode: number; endInNode: number }[] = []

  let textNode = walker.nextNode() as Text | null
  while (textNode) {
    const len = textNode.nodeValue?.length || 0
    const nodeStart = currentOffset
    const nodeEnd = currentOffset + len

    if (nodeEnd > targetStart && nodeStart < targetEnd) {
      const startInNode = Math.max(0, targetStart - nodeStart)
      const endInNode = Math.min(len, targetEnd - nodeStart)
      nodesToWrap.push({ node: textNode, startInNode, endInNode })
    }

    currentOffset += len
    if (currentOffset >= targetEnd) break
    textNode = walker.nextNode() as Text | null
  }

  // Envolve os nós selecionados
  for (const { node, startInNode, endInNode } of nodesToWrap) {
    if (!node.parentNode) continue

    // Divide o nó de texto para isolar o trecho
    let middleNode = node
    if (endInNode < middleNode.length) {
      middleNode.splitText(endInNode)
    }
    if (startInNode > 0) {
      middleNode = middleNode.splitText(startInNode)
    }

    const wrapper = document.createElement(hl.kind === 'hidden' || hl.kind === 'question' ? 'span' : 'mark')
    wrapper.setAttribute('data-highlight-id', String(hl.id))
    wrapper.setAttribute('data-kind', hl.kind)
    wrapper.className = getHighlightClassNames(hl)

    const parent = middleNode.parentNode
    if (!parent) continue
    parent.insertBefore(wrapper, middleNode)
    wrapper.appendChild(middleNode)

    // Elementos visuais complementares
    if (hl.kind === 'hidden') {
      const revealBtn = document.createElement('button')
      revealBtn.type = 'button'
      revealBtn.className = 'study-occlusion-btn'
      revealBtn.textContent = 'Revelar'
      revealBtn.title = 'Clique para revelar ou ocultar o texto'
      wrapper.appendChild(revealBtn)
    } else if (hl.kind === 'question') {
      const qContainer = document.createElement('span')
      qContainer.className = 'study-question-badge'
      qContainer.innerHTML = `<span class="study-question-icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block;vertical-align:middle;margin-right:4px;"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></span><strong>Pergunta:</strong> ${escapeHtml(hl.note || 'O que este trecho expressa?')}`

      const revealBtn = document.createElement('button')
      revealBtn.type = 'button'
      revealBtn.className = 'study-question-reveal-btn'
      revealBtn.textContent = 'Ver resposta'
      qContainer.appendChild(revealBtn)

      wrapper.insertBefore(qContainer, wrapper.firstChild)
    } else if (hl.kind === 'note' && hl.note) {
      const noteBadge = document.createElement('span')
      noteBadge.className = 'study-note-badge'
      noteBadge.title = hl.note
      noteBadge.setAttribute('aria-label', `Nota: ${hl.note}`)
      noteBadge.innerHTML = `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block;vertical-align:middle;"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>`
      wrapper.appendChild(noteBadge)
    }
  }
}

export function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}
