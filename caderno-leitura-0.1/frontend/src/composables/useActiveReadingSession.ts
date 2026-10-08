import { ref, computed, onUnmounted, type Ref } from 'vue'
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

// --- Composable para Sessões Estruturadas de Estudo (F 0.7.14) ---

import {
  startStudySession as apiStartSession,
  getStudySession as apiGetSession,
  answerStudySessionItem as apiAnswerItem,
  completeStudySession as apiCompleteSession,
  interruptStudySession as apiInterruptSession,
} from '../services/api.ts'
import type {
  ReviewItemRead,
  SessionRating,
  StudySessionDetail,
  StudySessionStartPayload,
  StudySessionSummary,
} from '../types.ts'

export function useStructuredStudySession() {
  const session = ref<StudySessionDetail | null>(null)
  const loading = ref(false)
  const submitting = ref(false)
  const error = ref<string | null>(null)
  const currentIndex = ref(0)
  const isRevealed = ref(false)
  const showConfirmExit = ref(false)
  const elapsedSeconds = ref(0)
  const cardElapsedSeconds = ref(0)
  const summary = ref<StudySessionSummary | null>(null)
  const showSummaryModal = ref(false)

  let timerHandle: ReturnType<typeof setInterval> | null = null

  function startTimer() {
    stopTimer()
    timerHandle = setInterval(() => {
      elapsedSeconds.value++
      cardElapsedSeconds.value++
    }, 1000)
  }

  function stopTimer() {
    if (timerHandle) {
      clearInterval(timerHandle)
      timerHandle = null
    }
  }

  const formattedTimer = computed(() => {
    const mins = Math.floor(elapsedSeconds.value / 60)
    const secs = elapsedSeconds.value % 60
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  })

  const currentCard = computed<ReviewItemRead | null>(() => {
    if (!session.value || !session.value.pending_cards) return null
    if (currentIndex.value >= session.value.pending_cards.length) return null
    return session.value.pending_cards[currentIndex.value]
  })

  const progress = computed(() => {
    const total = session.value?.total_items || 0
    const current = Math.min(currentIndex.value + 1, total)
    const percent = total > 0 ? Math.round((currentIndex.value / total) * 100) : 0
    return { current, total, percent }
  })

  async function loadSession(sessionId: number) {
    loading.value = true
    error.value = null
    try {
      const data = await apiGetSession(sessionId)
      session.value = data
      currentIndex.value = data.completed_items
      isRevealed.value = false
      if (data.status === 'completed') {
        showSummaryModal.value = true
      } else {
        startTimer()
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Falha ao carregar a sessão de estudo.'
    } finally {
      loading.value = false
    }
  }

  async function startNewSession(payload: StudySessionStartPayload) {
    loading.value = true
    error.value = null
    try {
      const data = await apiStartSession(payload)
      session.value = data
      currentIndex.value = 0
      isRevealed.value = false
      elapsedSeconds.value = 0
      cardElapsedSeconds.value = 0
      startTimer()
      return data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Falha ao iniciar nova sessão de estudo.'
      throw err
    } finally {
      loading.value = false
    }
  }

  function revealAnswer() {
    isRevealed.value = true
  }

  async function answerCard(rating: SessionRating) {
    if (!session.value || !currentCard.value || submitting.value) return
    const card = currentCard.value
    const timeSpent = cardElapsedSeconds.value

    submitting.value = true
    error.value = null

    try {
      await apiAnswerItem(session.value.id, {
        highlight_id: card.id,
        rating,
        time_spent_seconds: timeSpent,
      })

      // Incrementa índice e zera tempo do cartão
      currentIndex.value++
      cardElapsedSeconds.value = 0
      isRevealed.value = false

      // Se concluiu todos os itens
      if (currentIndex.value >= (session.value.pending_cards?.length || 0)) {
        stopTimer()
        await finalizeSession()
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Falha ao registrar resposta do cartão.'
    } finally {
      submitting.value = false
    }
  }

  async function finalizeSession() {
    if (!session.value) return
    try {
      const res = await apiCompleteSession(session.value.id, {
        duration_seconds: elapsedSeconds.value,
      })
      summary.value = res
      showSummaryModal.value = true
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Falha ao finalizar sessão.'
    }
  }

  async function interruptAndExit(onDone?: () => void) {
    stopTimer()
    if (session.value && session.value.status === 'in_progress') {
      try {
        await apiInterruptSession(session.value.id)
      } catch {
        // silencioso
      }
    }
    showConfirmExit.value = false
    if (onDone) onDone()
  }

  function requestExit() {
    if (session.value && session.value.status === 'in_progress') {
      showConfirmExit.value = true
    }
  }

  function cancelExit() {
    showConfirmExit.value = false
  }

  function handleKeydown(e: KeyboardEvent, onExitApproved?: () => void) {
    if (showConfirmExit.value) {
      if (e.key === 'Escape') {
        cancelExit()
      } else if (e.key === 'Enter') {
        void interruptAndExit(onExitApproved)
      }
      return
    }

    if (showSummaryModal.value) {
      return
    }

    if (e.key === 'Escape') {
      e.preventDefault()
      requestExit()
      return
    }

    if (e.key === ' ' || e.code === 'Space') {
      if (!isRevealed.value) {
        e.preventDefault()
        revealAnswer()
      }
      return
    }

    if (isRevealed.value && !submitting.value) {
      if (e.key === '1' || e.key === 'f' || e.key === 'F') {
        e.preventDefault()
        void answerCard('easy')
      } else if (e.key === '2' || e.key === 'm' || e.key === 'M') {
        e.preventDefault()
        void answerCard('medium')
      } else if (e.key === '3' || e.key === 'd' || e.key === 'D') {
        e.preventDefault()
        void answerCard('hard')
      }
    }
  }

  onUnmounted(() => {
    stopTimer()
  })

  return {
    session,
    loading,
    submitting,
    error,
    currentIndex,
    isRevealed,
    showConfirmExit,
    elapsedSeconds,
    formattedTimer,
    summary,
    showSummaryModal,
    currentCard,
    progress,
    loadSession,
    startNewSession,
    revealAnswer,
    answerCard,
    finalizeSession,
    requestExit,
    cancelExit,
    interruptAndExit,
    handleKeydown,
  }
}

