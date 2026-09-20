import { ref, computed, watch, isRef, type Ref, type ComputedRef } from 'vue'
import type { StudyGroupByCriteria, StudyGroup, ReadingStatus } from '../types.ts'

export interface StudyGroupingItem {
  id: number
  chapter_id?: number
  title?: string
  location?: string
  reading_status?: ReadingStatus | string
  created_at?: string
  updated_at?: string
  category?: string
  [key: string]: any
}

export interface UseStudyGroupingOptions<T extends StudyGroupingItem = StudyGroupingItem> {
  studies: Ref<T[]> | ComputedRef<T[]> | T[]
  initialCriteria?: StudyGroupByCriteria
  storageKey?: string
  chapters?: Ref<{ id: number; name: string }[]> | ComputedRef<{ id: number; name: string }[]> | { id: number; name: string }[]
  categories?: Ref<{ id: string; name: string }[]> | ComputedRef<{ id: string; name: string }[]> | { id: string; name: string }[]
  studyCategoryMap?: Ref<Record<number, string>> | ComputedRef<Record<number, string>> | Record<number, string>
}

export const READING_STATUS_LABELS: Record<string, { label: string; badgeClass: string }> = {
  rascunho: { label: 'Rascunho', badgeClass: 'badge-rascunho' },
  em_estudo: { label: 'Em Estudo', badgeClass: 'badge-em-estudo' },
  revisado: { label: 'Revisado', badgeClass: 'badge-revisado' },
  concluido: { label: 'Concluído', badgeClass: 'badge-concluido' },
}

export function getDateBucket(isoDate?: string): { id: string; title: string; order: number } {
  if (!isoDate) {
    return { id: 'antigos', title: 'Mais Antigos', order: 4 }
  }

  const d = new Date(isoDate)
  if (isNaN(d.getTime())) {
    return { id: 'antigos', title: 'Mais Antigos', order: 4 }
  }

  const now = new Date()
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const oneWeekAgo = startOfToday - 7 * 24 * 60 * 60 * 1000
  const oneMonthAgo = startOfToday - 30 * 24 * 60 * 60 * 1000
  const time = d.getTime()

  if (time >= startOfToday) {
    return { id: 'hoje', title: 'Hoje', order: 1 }
  } else if (time >= oneWeekAgo) {
    return { id: 'esta_semana', title: 'Esta Semana', order: 2 }
  } else if (time >= oneMonthAgo) {
    return { id: 'este_mes', title: 'Este Mês', order: 3 }
  } else {
    return { id: 'antigos', title: 'Mais Antigos', order: 4 }
  }
}

export function useStudyGrouping<T extends StudyGroupingItem = StudyGroupingItem>(
  options: UseStudyGroupingOptions<T>,
) {
  const getRawStudies = (): T[] => {
    return isRef(options.studies) ? options.studies.value : options.studies
  }

  const getChapters = (): { id: number; name: string }[] => {
    if (!options.chapters) return []
    return isRef(options.chapters) ? options.chapters.value : options.chapters
  }

  const getCategoryMap = (): Record<number, string> => {
    if (!options.studyCategoryMap) return {}
    return isRef(options.studyCategoryMap) ? options.studyCategoryMap.value : options.studyCategoryMap
  }

  const storageKey = options.storageKey ?? 'caderno_study_group_by'

  // Carregar critério persistido
  const loadSavedCriteria = (): StudyGroupByCriteria => {
    if (typeof localStorage !== 'undefined') {
      const saved = localStorage.getItem(storageKey)
      if (saved && ['chapter', 'status', 'category', 'date', 'manual'].includes(saved)) {
        return saved as StudyGroupByCriteria
      }
    }
    return options.initialCriteria ?? 'chapter'
  }

  const currentCriteria = ref<StudyGroupByCriteria>(loadSavedCriteria())
  const collapsedGroups = ref<Record<string, boolean>>({})

  // Salvar alterações de critério no localStorage
  watch(currentCriteria, (newVal) => {
    if (typeof localStorage !== 'undefined') {
      try {
        localStorage.setItem(storageKey, newVal)
      } catch {
        // quota exceeded or private mode
      }
    }
  })

  function toggleGroup(groupId: string) {
    collapsedGroups.value[groupId] = !collapsedGroups.value[groupId]
  }

  function setGroupCollapsed(groupId: string, collapsed: boolean) {
    collapsedGroups.value[groupId] = collapsed
  }

  function setCriteria(newCriteria: StudyGroupByCriteria) {
    currentCriteria.value = newCriteria
  }

  const groups = computed<StudyGroup<T>[]>(() => {
    const rawStudies = getRawStudies()
    if (!rawStudies || rawStudies.length === 0) {
      return []
    }

    const criteria = currentCriteria.value

    if (criteria === 'status') {
      // 4 raias canônicas: rascunho, em_estudo, revisado, concluido
      const statusBuckets: Record<string, T[]> = {
        rascunho: [],
        em_estudo: [],
        revisado: [],
        concluido: [],
      }

      for (const study of rawStudies) {
        const rawStatus = (study.reading_status || 'rascunho').toLowerCase()
        if (statusBuckets[rawStatus]) {
          statusBuckets[rawStatus].push(study)
        } else {
          statusBuckets['rascunho'].push(study)
        }
      }

      const statusOrder = ['rascunho', 'em_estudo', 'revisado', 'concluido']
      const result: StudyGroup<T>[] = []

      for (const st of statusOrder) {
        const items = statusBuckets[st]
        if (items.length > 0) {
          const meta = READING_STATUS_LABELS[st]
          result.push({
            id: `status-${st}`,
            title: meta.label,
            badgeLabel: meta.label,
            badgeClass: meta.badgeClass,
            count: items.length,
            isCollapsed: !!collapsedGroups.value[`status-${st}`],
            studies: items,
          })
        }
      }
      return result
    }

    if (criteria === 'category') {
      const catMap = getCategoryMap()
      const categoryBuckets: Record<string, T[]> = {}
      const withoutCategory: T[] = []

      for (const study of rawStudies) {
        const categoryName = study.category || catMap[study.id]
        if (categoryName && categoryName.trim()) {
          const norm = categoryName.trim()
          if (!categoryBuckets[norm]) {
            categoryBuckets[norm] = []
          }
          categoryBuckets[norm].push(study)
        } else {
          withoutCategory.push(study)
        }
      }

      const result: StudyGroup<T>[] = []
      const sortedKeys = Object.keys(categoryBuckets).sort((a, b) => a.localeCompare(b, 'pt-BR'))

      for (const catName of sortedKeys) {
        const items = categoryBuckets[catName]
        const groupId = `cat-${catName.toLowerCase().replace(/\s+/g, '-')}`
        result.push({
          id: groupId,
          title: catName,
          count: items.length,
          isCollapsed: !!collapsedGroups.value[groupId],
          studies: items,
        })
      }

      if (withoutCategory.length > 0) {
        result.push({
          id: 'cat-sem-categoria',
          title: 'Sem Categoria',
          count: withoutCategory.length,
          isCollapsed: !!collapsedGroups.value['cat-sem-categoria'],
          studies: withoutCategory,
        })
      }

      return result
    }

    if (criteria === 'date') {
      const dateBuckets: Record<string, { title: string; order: number; items: T[] }> = {
        hoje: { title: 'Hoje', order: 1, items: [] },
        esta_semana: { title: 'Esta Semana', order: 2, items: [] },
        este_mes: { title: 'Este Mês', order: 3, items: [] },
        antigos: { title: 'Mais Antigos', order: 4, items: [] },
      }

      for (const study of rawStudies) {
        const bucket = getDateBucket(study.created_at)
        dateBuckets[bucket.id].items.push(study)
      }

      const result: StudyGroup<T>[] = []
      const sortedBuckets = Object.entries(dateBuckets)
        .filter(([_, b]) => b.items.length > 0)
        .sort((a, b) => a[1].order - b[1].order)

      for (const [key, bucket] of sortedBuckets) {
        const groupId = `date-${key}`
        result.push({
          id: groupId,
          title: bucket.title,
          count: bucket.items.length,
          isCollapsed: !!collapsedGroups.value[groupId],
          studies: bucket.items,
        })
      }

      return result
    }

    // Default / 'chapter'
    const chapters = getChapters()
    const chapterMap = new Map<number, string>()
    for (const ch of chapters) {
      chapterMap.set(ch.id, ch.name)
    }

    const chapterBuckets = new Map<number | string, { title: string; items: T[] }>()

    for (const study of rawStudies) {
      const chId = study.chapter_id ?? 0
      if (!chapterBuckets.has(chId)) {
        const title = chapterMap.get(chId) || (chId > 0 ? `Capítulo ${chId}` : 'Geral')
        chapterBuckets.set(chId, { title, items: [] })
      }
      chapterBuckets.get(chId)!.items.push(study)
    }

    const result: StudyGroup<T>[] = []
    for (const [chId, data] of chapterBuckets.entries()) {
      const groupId = `chapter-${chId}`
      result.push({
        id: groupId,
        title: data.title,
        count: data.items.length,
        isCollapsed: !!collapsedGroups.value[groupId],
        studies: data.items,
      })
    }

    return result
  })

  const totalStudies = computed(() => {
    return getRawStudies().length
  })

  return {
    currentCriteria,
    collapsedGroups,
    groups,
    totalStudies,
    setCriteria,
    toggleGroup,
    setGroupCollapsed,
  }
}
