import { ref, computed } from 'vue'
import type { Category } from '../types'
import { api } from '../services/api.ts'

// Cache em memória compartilhado entre componentes
const categoriesCache = ref<Category[]>([])
const isLoading = ref(false)
const loadError = ref<string | null>(null)

export function normalizeCategoryText(text: string): string {
  return (text || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .trim()
}

export function useCategories() {
  async function loadCategories(force = false): Promise<Category[]> {
    if (!force && categoriesCache.value.length > 0) {
      return categoriesCache.value
    }

    isLoading.value = true
    loadError.value = null
    try {
      const data = await api.listCategories()
      categoriesCache.value = data
      return data
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Erro ao carregar categorias.'
      loadError.value = msg
      return []
    } finally {
      isLoading.value = false
    }
  }

  const categoryMap = computed(() => {
    const map = new Map<string, Category>()
    for (const cat of categoriesCache.value) {
      map.set(cat.id, cat)
    }
    return map
  })

  const childrenMap = computed(() => {
    const map = new Map<string, Category[]>()
    for (const cat of categoriesCache.value) {
      if (cat.parent_id) {
        const list = map.get(cat.parent_id) || []
        list.push(cat)
        map.set(cat.parent_id, list)
      }
    }
    return map
  })

  function searchCategories(query: string, limit = 20): Category[] {
    const term = normalizeCategoryText(query)
    if (!term) return categoriesCache.value.slice(0, limit)

    const tokens = term.split(' ').filter(Boolean)

    return categoriesCache.value
      .filter((cat) => {
        const normName = normalizeCategoryText(cat.name)
        const normPath = normalizeCategoryText(cat.path)
        return tokens.every((tok) => normName.includes(tok) || normPath.includes(tok))
      })
      .slice(0, limit)
  }

  function getDescendantIds(rootId: string): Set<string> {
    const result = new Set<string>()
    result.add(rootId)

    const queue = [rootId]
    while (queue.length > 0) {
      const curr = queue.shift()!
      const children = childrenMap.value.get(curr)
      if (children) {
        for (const child of children) {
          if (!result.has(child.id)) {
            result.add(child.id)
            queue.push(child.id)
          }
        }
      }
    }
    return result
  }

  function getCategoryById(id: string): Category | undefined {
    return categoryMap.value.get(id)
  }

  return {
    categories: categoriesCache,
    isLoading,
    loadError,
    loadCategories,
    searchCategories,
    getDescendantIds,
    getCategoryById,
    normalizeCategoryText,
  }
}
