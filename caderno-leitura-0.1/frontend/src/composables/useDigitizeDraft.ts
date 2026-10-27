import { computed, reactive } from 'vue'
import { ApiError, errorMessage } from '../services/api.ts'
import { positiveId } from '../types.ts'
import type { Study, StudyCreate } from '../types.ts'
import {
  DIGITIZE_ACCEPTED_TYPES,
  DIGITIZE_DEFAULT_SECTION,
  DIGITIZE_MAX_BYTES,
} from '../types/digitize.ts'
import type {
  DigitizeErrorCode,
  DigitizePreview,
  DigitizeSection,
  DigitizeStatus,
  DigitizeUnavailableReason,
} from '../types/digitize.ts'

export type DigitizePhase = 'checking' | 'unavailable' | 'idle' | 'reading' | 'review' | 'saving' | 'saved' | 'error'

interface DigitizeGateway {
  status: (signal?: AbortSignal) => Promise<DigitizeStatus>
  preview: (file: File, signal?: AbortSignal) => Promise<DigitizePreview>
  createStudy: (payload: StudyCreate) => Promise<Study>
}

interface DigitizeEnvironment {
  createObjectURL: (file: File) => string
  revokeObjectURL: (url: string) => void
  today: () => Date
}

export interface UncertainLine {
  index: number
  number: number
  text: string
  revised: boolean
}

const browserEnvironment = (): DigitizeEnvironment => ({
  createObjectURL: file => URL.createObjectURL(file),
  revokeObjectURL: url => URL.revokeObjectURL(url),
  today: () => new Date(),
})

export function defaultTitle(date: Date): string {
  const pad = (value: number) => String(value).padStart(2, '0')
  return `Página digitalizada em ${pad(date.getDate())}/${pad(date.getMonth() + 1)}/${date.getFullYear()}`
}

function errorCode(error: unknown): DigitizeErrorCode {
  if (error instanceof ApiError && typeof error.data === 'object' && error.data !== null && 'code' in error.data) {
    return String((error.data as { code: unknown }).code) as DigitizeErrorCode
  }
  return 'error'
}

export function useDigitizeDraft(gateway: DigitizeGateway, environment: DigitizeEnvironment = browserEnvironment()) {
  const state = reactive({
    phase: 'checking' as DigitizePhase,
    unavailableReason: null as DigitizeUnavailableReason | null,
    fileName: '',
    previewUrl: '',
    preview: null as DigitizePreview | null,
    text: '',
    section: DIGITIZE_DEFAULT_SECTION as DigitizeSection,
    bookId: '',
    chapterId: '',
    title: '',
    error: null as { code: DigitizeErrorCode; message: string } | null,
    saved: null as Study | null,
  })
  let reading: AbortController | null = null

  const busy = computed(() => state.phase === 'reading' || state.phase === 'saving')
  const dirty = computed(() => (state.phase === 'review' || state.phase === 'saving') && state.text.trim() !== '')
  const canSave = computed(() => state.phase === 'review' && positiveId(state.chapterId) !== null
    && state.title.trim() !== '' && state.text.trim() !== '')
  const uncertainLines = computed<UncertainLine[]>(() => (state.preview?.lines ?? [])
    .filter(line => line.low_confidence && line.text.trim() !== '')
    .map(line => ({ index: line.index, number: line.index + 1, text: line.text, revised: !state.text.includes(line.text) })))

  function releasePhoto() {
    if (state.previewUrl) environment.revokeObjectURL(state.previewUrl)
    state.previewUrl = ''
    state.fileName = ''
  }

  function fail(code: DigitizeErrorCode, message: string) {
    state.error = { code, message }
    state.phase = 'error'
  }

  async function checkStatus(signal?: AbortSignal): Promise<void> {
    state.phase = 'checking'
    try {
      const status = await gateway.status(signal)
      state.unavailableReason = status.available ? null : status.reason
      state.phase = status.available ? 'idle' : 'unavailable'
    } catch (error) {
      if (signal?.aborted) return
      fail(errorCode(error), errorMessage(error))
    }
  }

  async function choose(file: File): Promise<boolean> {
    if (busy.value || state.phase === 'unavailable') return false
    releasePhoto()
    state.preview = null
    state.error = null
    if (!DIGITIZE_ACCEPTED_TYPES.includes(file.type)) {
      fail('unsupported_format', 'Formato não suportado. Envie uma foto em JPEG, PNG ou WebP.')
      return false
    }
    if (file.size > DIGITIZE_MAX_BYTES) {
      fail('too_large', 'A imagem passa de 20 MB. Envie uma foto menor.')
      return false
    }
    const controller = new AbortController()
    reading = controller
    state.fileName = file.name
    state.previewUrl = environment.createObjectURL(file)
    state.phase = 'reading'
    try {
      const preview = await gateway.preview(file, controller.signal)
      if (controller.signal.aborted) return false
      state.preview = preview
      state.text = preview.text
      state.title = state.title.trim() || defaultTitle(environment.today())
      state.phase = 'review'
      return true
    } catch (error) {
      if (controller.signal.aborted) return false
      releasePhoto()
      const code = errorCode(error)
      if (code === 'unavailable') {
        state.unavailableReason = 'not_installed'
        state.phase = 'unavailable'
        return false
      }
      fail(code, errorMessage(error))
      return false
    } finally {
      if (reading === controller) reading = null
    }
  }

  function cancel() {
    if (state.phase !== 'reading') return
    reading?.abort()
    reading = null
    releasePhoto()
    state.phase = 'idle'
  }

  async function save(): Promise<Study | null> {
    // Uma foto gera no máximo um estudo (FR-009): só salva a partir da revisão, uma vez.
    if (state.phase !== 'review' || !state.preview) return null
    if (!canSave.value) {
      state.error = { code: 'save_failed', message: 'Escolha o livro, o capítulo e o título, e mantenha algum texto para salvar.' }
      return null
    }
    const payload: StudyCreate = {
      chapter_id: positiveId(state.chapterId)!,
      title: state.title.trim(),
      location: '',
      source_response: state.preview.text,
      summary: '', explanation: '', concepts: '', references: '',
      notes: '',
    }
    payload[state.section] = state.text
    state.phase = 'saving'
    state.error = null
    try {
      state.saved = await gateway.createStudy(payload)
      state.phase = 'saved'
      releasePhoto()
      return state.saved
    } catch (error) {
      state.error = {
        code: 'save_failed',
        message: error instanceof ApiError && error.status === 0
          ? 'Não foi possível confirmar o salvamento. O texto continua aqui. Confira os estudos do capítulo antes de reenviar.'
          : errorMessage(error),
      }
      state.phase = 'review'
      return null
    }
  }

  function reset() {
    if (busy.value) return
    releasePhoto()
    // Livro e capítulo ficam: a próxima página costuma ir para o mesmo destino.
    Object.assign(state, {
      phase: 'idle', preview: null, text: '', section: DIGITIZE_DEFAULT_SECTION, title: '', error: null, saved: null,
    })
  }

  function dispose() {
    reading?.abort()
    reading = null
    releasePhoto()
  }

  return { state, busy, dirty, canSave, uncertainLines, checkStatus, choose, cancel, save, reset, dispose }
}
