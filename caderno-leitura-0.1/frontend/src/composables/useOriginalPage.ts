// "Folha original" no estudo (feature 090-C): fotos de conferência, navegação, zoom, manter e apagar.
import { computed, reactive } from 'vue'
import { errorMessage } from '../services/api.ts'
import type { MediaItem } from '../types/media.ts'

export interface OriginalPageGateway {
  list: (studyId: number, signal?: AbortSignal) => Promise<{ items: MediaItem[] }>
  setKeep: (id: string, keepForever: boolean) => Promise<MediaItem>
  remove: (id: string) => Promise<{ freed_bytes: number }>
}

export const ZOOM_MIN = 0.5
export const ZOOM_MAX = 4
export const ZOOM_STEP = 0.25

export function useOriginalPage(gateway: OriginalPageGateway) {
  const state = reactive({
    items: [] as MediaItem[],
    index: 0,
    loading: false,
    loaded: false,
    error: '',
    zoom: 1,
    fit: true,
    working: false,
  })
  let request: AbortController | null = null

  const current = computed<MediaItem | null>(() => state.items[state.index] ?? null)
  const count = computed(() => state.items.length)
  const zoomPercent = computed(() => Math.round(state.zoom * 100))

  async function load(studyId: number): Promise<void> {
    request?.abort()
    const controller = new AbortController()
    request = controller
    state.loading = true
    state.error = ''
    try {
      const result = await gateway.list(studyId, controller.signal)
      if (controller.signal.aborted) return
      state.items = result.items
      state.index = Math.min(state.index, Math.max(0, result.items.length - 1))
      state.loaded = true
    } catch (error) {
      if (controller.signal.aborted) return
      state.error = errorMessage(error)
    } finally {
      if (request === controller) {
        request = null
        state.loading = false
      }
    }
  }

  function resetView() {
    state.zoom = 1
    state.fit = true
  }

  function go(step: 1 | -1) {
    if (state.items.length < 2) return
    state.index = (state.index + step + state.items.length) % state.items.length
    resetView()
  }

  function zoomBy(step: number) {
    const next = Math.round((state.zoom + step) / ZOOM_STEP) * ZOOM_STEP
    state.zoom = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, next))
    state.fit = false
  }

  const zoomIn = () => zoomBy(ZOOM_STEP)
  const zoomOut = () => zoomBy(-ZOOM_STEP)

  /** Teclas do visualizador: +, − e 0 (ajustar), setas para trocar de foto. */
  function handleKey(key: string): boolean {
    if (key === '+' || key === '=') zoomIn()
    else if (key === '-' || key === '−') zoomOut()
    else if (key === '0') resetView()
    else if (key === 'ArrowRight') go(1)
    else if (key === 'ArrowLeft') go(-1)
    else return false
    return true
  }

  async function toggleKeep(): Promise<void> {
    const item = current.value
    if (!item || state.working) return
    state.working = true
    state.error = ''
    try {
      state.items[state.index] = await gateway.setKeep(item.id, !item.keep_forever)
    } catch (error) {
      state.error = errorMessage(error)
    } finally {
      state.working = false
    }
  }

  async function removeCurrent(): Promise<boolean> {
    const item = current.value
    if (!item || state.working) return false
    state.working = true
    state.error = ''
    try {
      await gateway.remove(item.id)
      state.items.splice(state.index, 1)
      state.index = Math.min(state.index, Math.max(0, state.items.length - 1))
      resetView()
      return true
    } catch (error) {
      state.error = errorMessage(error)
      return false
    } finally {
      state.working = false
    }
  }

  function dispose() {
    request?.abort()
    request = null
  }

  return { state, current, count, zoomPercent, load, go, zoomIn, zoomOut, resetView, handleKey, toggleKeep, removeCurrent, dispose }
}
