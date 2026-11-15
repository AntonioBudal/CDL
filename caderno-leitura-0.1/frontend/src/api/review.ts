import { api } from '../services/api.ts'
import type { ReviewBucket, ReviewItemRead, ReviewRating, ReviewStatsResponse } from '../types.ts'

export interface ReviewFilterParams {
  book_id?: number
  chapter_id?: number
  kind?: string
  limit?: number
  bucket?: ReviewBucket
  /** F0.11.08: só conceitos frágeis (com kind=concept) */
  fragile?: boolean
}

export const reviewApi = {
  getStats: (signal?: AbortSignal, filters?: Omit<ReviewFilterParams, 'limit' | 'bucket'>): Promise<ReviewStatsResponse> =>
    api.getReviewStats(signal, filters),

  getItems: (params?: ReviewFilterParams, signal?: AbortSignal): Promise<ReviewItemRead[]> =>
    api.getReviewItems(params, signal),

  recordRating: (
    highlightId: number,
    rating: ReviewRating,
    signal?: AbortSignal,
  ): Promise<{ id: number; last_reviewed_at: string; review_count: number; last_rating: ReviewRating }> =>
    api.recordReviewRating(highlightId, rating, signal),

  /** F0.11.08: cartão de conceito, pela chave do léxico */
  recordConceptRating: (key: string, rating: ReviewRating, signal?: AbortSignal) =>
    api.recordConceptRating(key, rating, signal),
  recordImageRating: (cardId: number, rating: ReviewRating, signal?: AbortSignal) =>
    api.recordImageRating(cardId, rating, signal),
}

export default reviewApi
