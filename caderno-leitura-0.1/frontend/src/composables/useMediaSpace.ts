// "Minhas Imagens e Espaço" (feature 090-C): uso, lista, filtros, seleção e apagamento com prévia.
import { computed, reactive } from 'vue'
import { errorMessage } from '../services/api.ts'
import type {
  BulkDeleteRequest, BulkDeleteResult, MediaItem, MediaKind, MediaList, MediaListParams, MediaSort, MediaUsage,
} from '../types/media.ts'
import { formatBytes } from '../utils/mediaFormat.ts'

export interface MediaSpaceGateway {
  usage: (signal?: AbortSignal) => Promise<MediaUsage>
  list: (params: MediaListParams, signal?: AbortSignal) => Promise<MediaList>
  setKeep: (id: string, keepForever: boolean) => Promise<MediaItem>
  remove: (id: string) => Promise<{ freed_bytes: number }>
  bulk: (payload: BulkDeleteRequest) => Promise<BulkDeleteResult>
}

export type BulkKind = 'completed' | 'older'
export const OLDER_THAN_DAYS = 30
const PAGE_SIZE = 48

export interface PendingDeletion {
  scope: BulkKind | 'selected' | 'single'
  ids: string[]
  matched: number
  freedBytes: number
  title: string
  message: string
}

function plural(count: number, one: string, many: string): string {
  return `${count} ${count === 1 ? one : many}`
}

export function useMediaSpace(gateway: MediaSpaceGateway) {
  const state = reactive({
    usage: null as MediaUsage | null,
    items: [] as MediaItem[],
    nextOffset: null as number | null,
    loading: true,
    loadingMore: false,
    error: '',
    notice: '',
    kind: '' as MediaKind | '',
    bookId: null as number | null,
    sort: 'created_desc' as MediaSort,
    selected: [] as string[],
    previews: { completed: null as BulkDeleteResult | null, older: null as BulkDeleteResult | null },
    pending: null as PendingDeletion | null,
    working: false,
    busyIds: [] as string[],
  })
  let request: AbortController | null = null

  const selectedItems = computed(() => state.items.filter(item => state.selected.includes(item.id)))
  const books = computed(() => {
    const seen = new Map<number, string>()
    for (const item of state.items) if (item.book) seen.set(item.book.id, item.book.title)
    return [...seen].map(([id, title]) => ({ id, title })).sort((a, b) => a.title.localeCompare(b.title))
  })

  function params(offset = 0): MediaListParams {
    return { kind: state.kind, book_id: state.bookId, sort: state.sort, limit: PAGE_SIZE, offset }
  }

  async function refreshUsage() {
    try {
      state.usage = await gateway.usage()
    } catch {
      // O uso é complementar: a lista continua utilizável sem ele.
    }
  }

  async function refreshPreviews() {
    const [completed, older] = await Promise.allSettled([
      gateway.bulk({ filter: 'completed_studies', dry_run: true }),
      gateway.bulk({ filter: 'older_than_days', days: OLDER_THAN_DAYS, dry_run: true }),
    ])
    state.previews.completed = completed.status === 'fulfilled' ? completed.value : null
    state.previews.older = older.status === 'fulfilled' ? older.value : null
  }

  async function load(): Promise<void> {
    request?.abort()
    const controller = new AbortController()
    request = controller
    state.loading = true
    state.error = ''
    try {
      const [usage, list] = await Promise.all([gateway.usage(controller.signal), gateway.list(params(), controller.signal)])
      if (controller.signal.aborted) return
      state.usage = usage
      state.items = list.items
      state.nextOffset = list.next_offset
      state.selected = state.selected.filter(id => list.items.some(item => item.id === id))
      await refreshPreviews()
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

  async function loadMore(): Promise<void> {
    if (state.nextOffset === null || state.loadingMore) return
    state.loadingMore = true
    try {
      const list = await gateway.list(params(state.nextOffset))
      const known = new Set(state.items.map(item => item.id))
      state.items.push(...list.items.filter(item => !known.has(item.id)))
      state.nextOffset = list.next_offset
    } catch (error) {
      state.error = errorMessage(error)
    } finally {
      state.loadingMore = false
    }
  }

  function setFilters(changes: { kind?: MediaKind | ''; bookId?: number | null; sort?: MediaSort }) {
    if (changes.kind !== undefined) state.kind = changes.kind
    if (changes.bookId !== undefined) state.bookId = changes.bookId
    if (changes.sort !== undefined) state.sort = changes.sort
    state.selected = []
    return load()
  }

  function toggleSelected(id: string) {
    state.selected = state.selected.includes(id) ? state.selected.filter(value => value !== id) : [...state.selected, id]
  }

  function clearSelection() {
    state.selected = []
  }

  async function toggleKeep(item: MediaItem): Promise<void> {
    if (item.kind !== 'notebook_page' || state.busyIds.includes(item.id)) return
    state.busyIds.push(item.id)
    state.notice = ''
    try {
      const updated = await gateway.setKeep(item.id, !item.keep_forever)
      const index = state.items.findIndex(entry => entry.id === item.id)
      if (index >= 0) state.items[index] = updated
      state.notice = updated.keep_forever ? 'Foto mantida permanentemente.' : 'A foto voltou a expirar em 30 dias.'
      await refreshPreviews()
    } catch (error) {
      state.error = errorMessage(error)
    } finally {
      state.busyIds = state.busyIds.filter(id => id !== item.id)
    }
  }

  function askBulk(kind: BulkKind) {
    const preview = kind === 'completed' ? state.previews.completed : state.previews.older
    if (!preview || preview.matched === 0) return
    const what = kind === 'completed' ? 'de estudos concluídos' : `com mais de ${OLDER_THAN_DAYS} dias`
    state.pending = {
      scope: kind,
      ids: [],
      matched: preview.matched,
      freedBytes: preview.freed_bytes,
      title: `Apagar fotos ${what}?`,
      message: `Apagar ${plural(preview.matched, 'foto', 'fotos')} (${formatBytes(preview.freed_bytes)})? `
        + 'Os estudos e seus textos não serão alterados.',
    }
  }

  function askSelected() {
    const items = selectedItems.value
    if (items.length === 0) return
    const bytes = items.reduce((sum, item) => sum + item.byte_size, 0)
    state.pending = {
      scope: 'selected',
      ids: items.map(item => item.id),
      matched: items.length,
      freedBytes: bytes,
      title: 'Apagar as imagens selecionadas?',
      message: `Apagar ${plural(items.length, 'imagem', 'imagens')} (${formatBytes(bytes)})? `
        + 'Os estudos e seus textos não serão alterados.',
    }
  }

  function askSingle(item: MediaItem) {
    const consequence = item.kind === 'cover'
      ? 'O livro fica sem capa.'
      : item.kind === 'avatar' ? 'Seu perfil fica sem foto.' : 'O estudo e seus textos não serão alterados.'
    state.pending = {
      scope: 'single',
      ids: [item.id],
      matched: 1,
      freedBytes: item.byte_size,
      title: 'Apagar esta imagem?',
      message: `Apagar a imagem (${formatBytes(item.byte_size)})? ${consequence}`,
    }
  }

  function cancelPending() {
    if (!state.working) state.pending = null
  }

  async function confirmPending(): Promise<boolean> {
    const pending = state.pending
    if (!pending || state.working) return false
    state.working = true
    state.error = ''
    try {
      let deleted = 0
      let freed = 0
      if (pending.scope === 'single' && state.items.find(item => item.id === pending.ids[0])?.kind !== 'notebook_page') {
        // Capas e avatares saem pela rota individual, que também limpa a referência no livro ou no perfil.
        freed = (await gateway.remove(pending.ids[0])).freed_bytes
        deleted = 1
      } else {
        const payload: BulkDeleteRequest = pending.scope === 'completed'
          ? { filter: 'completed_studies', dry_run: false }
          : pending.scope === 'older'
            ? { filter: 'older_than_days', days: OLDER_THAN_DAYS, dry_run: false }
            : { ids: pending.ids, dry_run: false }
        const result = await gateway.bulk(payload)
        deleted = result.deleted
        freed = result.freed_bytes
      }
      state.pending = null
      state.selected = []
      state.notice = `${plural(deleted, 'imagem apagada', 'imagens apagadas')} (${formatBytes(freed)} liberados).`
      await load()
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

  return {
    state, books, selectedItems, load, loadMore, refreshUsage, setFilters, toggleSelected, clearSelection, toggleKeep,
    askBulk, askSelected, askSingle, cancelPending, confirmPending, dispose,
  }
}
