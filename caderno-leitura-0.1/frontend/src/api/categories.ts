import { api } from '../services/api.ts'
import type { Category, CategoryStats, CategorySuggestion } from '../types.ts'

export interface CategoryFilterParams {
  q?: string
  canonical_only?: boolean
}

export const categoriesApi = {
  list: (params?: CategoryFilterParams, signal?: AbortSignal): Promise<Category[]> =>
    api.listCategories(params, signal),

  suggest: (q: string, signal?: AbortSignal): Promise<CategorySuggestion> =>
    api.suggestCategories(q, signal),

  getStats: (signal?: AbortSignal): Promise<CategoryStats> =>
    api.getCategoryStats(signal),

  create: (name: string): Promise<Category> =>
    api.createCategory({ name }),

  delete: (id: string): Promise<void> =>
    api.deleteCategory(id),
}

export default categoriesApi
