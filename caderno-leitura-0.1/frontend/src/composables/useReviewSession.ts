import { computed, reactive } from 'vue'
import { reviewApi, type ReviewFilterParams } from '../api/review.ts'
import type { ReviewItemRead, ReviewRating } from '../types.ts'

export interface ReviewSessionState {
  items: ReviewItemRead[]
  currentIndex: number
  isRevealed: boolean
  isCompleted: boolean
  ratings: Record<number, ReviewRating>
  loading: boolean
  submitting: boolean
  error: string | null
}

export function useReviewSession() {
  const state = reactive<ReviewSessionState>({
    items: [],
    currentIndex: 0,
    isRevealed: false,
    isCompleted: false,
    ratings: {},
    loading: false,
    submitting: false,
    error: null,
  })

  const currentItem = computed<ReviewItemRead | null>(() => {
    if (state.items.length === 0 || state.currentIndex >= state.items.length) {
      return null
    }
    return state.items[state.currentIndex]
  })

  const progress = computed(() => {
    const total = state.items.length
    if (total === 0) {
      return { current: 0, total: 0, percent: 0 }
    }
    const current = Math.min(state.currentIndex + 1, total)
    const percent = Math.round((current / total) * 100)
    return { current, total, percent }
  })

  const summary = computed(() => {
    let easy = 0
    let medium = 0
    let hard = 0
    for (const r of Object.values(state.ratings)) {
      if (r === 'easy') easy++
      else if (r === 'medium') medium++
      else if (r === 'hard') hard++
    }
    const total = easy + medium + hard
    return { easy, medium, hard, total }
  })

  async function loadItems(filters?: ReviewFilterParams) {
    state.loading = true
    state.error = null
    try {
      const items = await reviewApi.getItems({
        limit: 10,
        ...filters,
      })
      state.items = items
      state.currentIndex = 0
      state.isRevealed = false
      state.isCompleted = false
      state.ratings = {}
    } catch (err: unknown) {
      state.error = err instanceof Error ? err.message : 'Falha ao carregar itens de estudo.'
      state.items = []
    } finally {
      state.loading = false
    }
  }

  function revealAnswer() {
    state.isRevealed = true
  }

  async function submitRating(rating: ReviewRating) {
    const item = currentItem.value
    if (!item) return

    state.submitting = true
    state.error = null
    try {
      await reviewApi.recordRating(item.id, rating)
      state.ratings[item.id] = rating

      if (state.currentIndex + 1 >= state.items.length) {
        state.isCompleted = true
      } else {
        state.currentIndex++
        state.isRevealed = false
      }
    } catch (err: unknown) {
      state.error = err instanceof Error ? err.message : 'Falha ao gravar avaliação.'
    } finally {
      state.submitting = false
    }
  }

  async function restartOrContinue(filters?: ReviewFilterParams) {
    await loadItems(filters)
  }

  function reset() {
    state.items = []
    state.currentIndex = 0
    state.isRevealed = false
    state.isCompleted = false
    state.ratings = {}
    state.loading = false
    state.submitting = false
    state.error = null
  }

  return {
    state,
    currentItem,
    progress,
    summary,
    loadItems,
    revealAnswer,
    submitRating,
    restartOrContinue,
    reset,
  }
}
