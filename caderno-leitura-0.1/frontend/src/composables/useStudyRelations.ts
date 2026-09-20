import { ref, computed } from 'vue'
import type {
  StudyRelationItem,
  StudyRelationType,
  CreateStudyRelationPayload,
  UpdateStudyRelationPayload,
} from '../types.ts'
import {
  getStudyRelations as apiGetRelations,
  createStudyRelation as apiCreateRelation,
  updateStudyRelation as apiUpdateRelation,
  deleteStudyRelation as apiDeleteRelation,
  errorMessage,
} from '../services/api.ts'

export const RELATION_TYPE_LABELS: Record<StudyRelationType, { outbound: string; inbound: string; badgeClass: string }> = {
  relacionado_com: {
    outbound: 'Relacionado com',
    inbound: 'Relacionado com',
    badgeClass: 'badge-neutral',
  },
  complementa: {
    outbound: 'Complementa',
    inbound: 'Complementado por',
    badgeClass: 'badge-complement',
  },
  contradiz: {
    outbound: 'Contradiz',
    inbound: 'Contradito por',
    badgeClass: 'badge-contradict',
  },
  depende_de: {
    outbound: 'Depende de',
    inbound: 'Pré-requisito de',
    badgeClass: 'badge-dependency',
  },
  mesmo_tema: {
    outbound: 'Mesmo tema',
    inbound: 'Mesmo tema',
    badgeClass: 'badge-theme',
  },
  desdobramento_de: {
    outbound: 'Desdobramento de',
    inbound: 'Desdobra-se em',
    badgeClass: 'badge-derivation',
  },
}

export function useStudyRelations() {
  const outboundRelations = ref<StudyRelationItem[]>([])
  const inboundRelations = ref<StudyRelationItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const activeStudyId = ref<number | null>(null)

  const totalRelationsCount = computed(
    () => outboundRelations.value.length + inboundRelations.value.length
  )

  async function loadRelations(studyId: number) {
    activeStudyId.value = studyId
    loading.value = true
    error.value = null
    try {
      const response = await apiGetRelations(studyId)
      outboundRelations.value = response.outbound
      inboundRelations.value = response.inbound
    } catch (err) {
      error.value = errorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function addRelation(studyId: number, payload: CreateStudyRelationPayload): Promise<StudyRelationItem> {
    loading.value = true
    error.value = null
    try {
      const item = await apiCreateRelation(studyId, payload)
      outboundRelations.value.unshift(item)
      return item
    } catch (err) {
      const msg = errorMessage(err)
      error.value = msg
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateRelation(relationId: number, payload: UpdateStudyRelationPayload): Promise<StudyRelationItem> {
    loading.value = true
    error.value = null
    try {
      const updated = await apiUpdateRelation(relationId, payload)
      const idx = outboundRelations.value.findIndex(r => r.id === relationId)
      if (idx !== -1) {
        outboundRelations.value[idx] = updated
      }
      return updated
    } catch (err) {
      const msg = errorMessage(err)
      error.value = msg
      throw err
    } finally {
      loading.value = false
    }
  }

  async function removeRelation(relationId: number): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await apiDeleteRelation(relationId)
      outboundRelations.value = outboundRelations.value.filter(r => r.id !== relationId)
      inboundRelations.value = inboundRelations.value.filter(r => r.id !== relationId)
    } catch (err) {
      const msg = errorMessage(err)
      error.value = msg
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    outboundRelations,
    inboundRelations,
    totalRelationsCount,
    loading,
    error,
    activeStudyId,
    loadRelations,
    addRelation,
    updateRelation,
    removeRelation,
  }
}
