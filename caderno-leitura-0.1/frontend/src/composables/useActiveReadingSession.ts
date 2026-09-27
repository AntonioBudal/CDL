import { ref, computed, type Ref } from 'vue'
import type {
  ActiveStudyNode,
  StudyHighlight,
  StudySectionKey,
} from '../types.ts'
import {
  setHighlightsRevealedState,
  scrollAndFocusHighlight,
  collectInteractiveHighlights,
} from '../utils/highlightRenderer.ts'

export interface UseActiveReadingSessionOptions {
  activeSectionRef?: Ref<StudySectionKey>
  highlightsRef?: Ref<StudyHighlight[]>
  containerRef?: Ref<HTMLElement | null>
}

export function useActiveReadingSession(options: UseActiveReadingSessionOptions = {}) {
  const {
    activeSectionRef = ref<StudySectionKey>('summary'),
    highlightsRef = ref<StudyHighlight[]>([]),
    containerRef = ref<HTMLElement | null>(null),
  } = options

  const isActive = ref(false)
  const focusedIndex = ref(-1)
  const revealedMap = ref<Record<number, boolean>>({})

  const interactiveHighlights = computed(() => {
    return highlightsRef.value.filter((h) => {
      const matchSection = h.section === activeSectionRef.value
      const isInteractive = h.kind === 'hidden' || h.kind === 'question'
      return matchSection && isInteractive
    })
  })

  const totalCount = computed(() => interactiveHighlights.value.length)

  const revealedCount = computed(() => {
    return interactiveHighlights.value.filter((h) => !!revealedMap.value[h.id]).length
  })

  const completionPercentage = computed(() => {
    if (totalCount.value === 0) return 0
    return Math.round((revealedCount.value / totalCount.value) * 100)
  })

  const nodes = computed<ActiveStudyNode[]>(() => {
    return interactiveHighlights.value.map((h) => ({
      highlight_id: h.id,
      kind: h.kind as 'hidden' | 'question',
      section: h.section,
      is_revealed: !!revealedMap.value[h.id],
      prompt_text: h.note || '',
      answer_text: h.selected_text || '',
    }))
  })

  function startSession(initialRevealed = false) {
    isActive.value = true
    focusedIndex.value = -1

    // Inicializa todos os trechos interativos da seção ativa
    const newMap = { ...revealedMap.value }
    for (const h of interactiveHighlights.value) {
      newMap[h.id] = initialRevealed
    }
    revealedMap.value = newMap

    if (containerRef.value) {
      setHighlightsRevealedState(containerRef.value, initialRevealed)
    }
  }

  function endSession() {
    isActive.value = false
    focusedIndex.value = -1

    // Ao encerrar, restaura a visualização normal de leitura (tudo legível)
    const newMap = { ...revealedMap.value }
    for (const h of interactiveHighlights.value) {
      newMap[h.id] = true
    }
    revealedMap.value = newMap

    if (containerRef.value) {
      setHighlightsRevealedState(containerRef.value, true)
    }
  }

  function revealAll() {
    const newMap = { ...revealedMap.value }
    for (const h of interactiveHighlights.value) {
      newMap[h.id] = true
    }
    revealedMap.value = newMap

    if (containerRef.value) {
      setHighlightsRevealedState(containerRef.value, true)
    }
  }

  function hideAll() {
    const newMap = { ...revealedMap.value }
    for (const h of interactiveHighlights.value) {
      newMap[h.id] = false
    }
    revealedMap.value = newMap

    if (containerRef.value) {
      setHighlightsRevealedState(containerRef.value, false)
    }
  }

  function toggleNode(highlightId: number) {
    const current = !!revealedMap.value[highlightId]
    const nextState = !current
    revealedMap.value = {
      ...revealedMap.value,
      [highlightId]: nextState,
    }

    if (containerRef.value) {
      const mark = containerRef.value.querySelector<HTMLElement>(`[data-highlight-id="${highlightId}"]`)
      if (mark) {
        if (nextState) {
          mark.classList.add('is-revealed')
        } else {
          mark.classList.remove('is-revealed')
        }
        const occlusionBtn = mark.querySelector<HTMLButtonElement>('.study-occlusion-btn')
        if (occlusionBtn) {
          occlusionBtn.textContent = nextState ? 'Ocultar' : 'Revelar'
        }
        const questionBtn = mark.querySelector<HTMLButtonElement>('.study-question-reveal-btn')
        if (questionBtn) {
          questionBtn.textContent = nextState ? 'Esconder resposta' : 'Ver resposta'
        }
      }
    }
  }

  function setNodeRevealed(highlightId: number, isRevealed: boolean) {
    revealedMap.value = {
      ...revealedMap.value,
      [highlightId]: isRevealed,
    }
  }

  function next(): boolean {
    if (interactiveHighlights.value.length === 0) return false
    const nextIdx = (focusedIndex.value + 1) % interactiveHighlights.value.length
    focusedIndex.value = nextIdx

    const target = interactiveHighlights.value[nextIdx]
    if (target && containerRef.value) {
      return scrollAndFocusHighlight(containerRef.value, target.id)
    }
    return true
  }

  function previous(): boolean {
    if (interactiveHighlights.value.length === 0) return false
    let prevIdx = focusedIndex.value - 1
    if (prevIdx < 0) {
      prevIdx = interactiveHighlights.value.length - 1
    }
    focusedIndex.value = prevIdx

    const target = interactiveHighlights.value[prevIdx]
    if (target && containerRef.value) {
      return scrollAndFocusHighlight(containerRef.value, target.id)
    }
    return true
  }

  function syncFromDom(root?: HTMLElement | null) {
    const targetRoot = root || containerRef.value
    if (!targetRoot) return
    const domHighlights = collectInteractiveHighlights(targetRoot)
    const newMap = { ...revealedMap.value }
    for (const dh of domHighlights) {
      newMap[dh.id] = dh.isRevealed
    }
    revealedMap.value = newMap
  }

  return {
    isActive,
    activeSection: activeSectionRef,
    focusedIndex,
    revealedMap,
    interactiveHighlights,
    totalCount,
    revealedCount,
    completionPercentage,
    nodes,
    startSession,
    endSession,
    revealAll,
    hideAll,
    toggleNode,
    setNodeRevealed,
    next,
    previous,
    syncFromDom,
  }
}
