import { api } from '../services/api.ts'
import type { ReviewBucket, ReviewItemRead, ReviewRating, ReviewStatsResponse } from '../types.ts'

export interface ReviewFilterParams {
  book_id?: number
  chapter_id?: number
  kind?: string
  limit?: number
  bucket?: ReviewBucket
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
}

export default reviewApi
