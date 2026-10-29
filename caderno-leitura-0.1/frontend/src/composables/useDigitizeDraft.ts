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
import type { OrganizerFeedbackRequest, OrganizeRequest, OrganizeResult } from '../types/organize.ts'
import type { StudyPhotoResult } from '../types/media.ts'
import { useSectionOrganizer } from './useSectionOrganizer.ts'

export type DigitizePhase = 'checking' | 'unavailable' | 'idle' | 'reading' | 'review' | 'saving' | 'saved' | 'error'

interface DigitizeGateway {
  status: (signal?: AbortSignal) => Promise<DigitizeStatus>
  preview: (file: File, signal?: AbortSignal) => Promise<DigitizePreview>
  createStudy: (payload: StudyCreate) => Promise<Study>
  /** Organização nas 4 seções (feature 089); opcional para quem só digitaliza. */
  organize?: (payload: OrganizeRequest, signal?: AbortSignal) => Promise<OrganizeResult>
  /** Guarda a foto com o estudo salvo, para conferência (feature 090-C); só com a caixa marcada. */
  storePhoto?: (studyId: number, file: File) => Promise<StudyPhotoResult>
  /** Registro silencioso do feedback do organizador e da leitura (feature 091-B). */
  sendFeedback?: (studyId: number, payload: OrganizerFeedbackRequest) => Promise<void>
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
    // Foto de conferência (feature 090-C): desmarcada por padrão; sem ela, a foto some como na 086.
    keepPhoto: false,
    photoExpiresAt: null as string | null,
    photoWarning: '',
  })
  let reading: AbortController | null = null
  // A foto fica só na memória do navegador durante a revisão, para ser reenviada se o leitor pedir.
  let photo: File | null = null
  const organizer = useSectionOrganizer({
    organize: (payload, signal) => gateway.organize
      ? gateway.organize(payload, signal)
      : Promise.reject(new Error('A organização automática não está disponível.')),
  })

  const busy = computed(() => state.phase === 'reading' || state.phase === 'saving')
  const hasContent = computed(() => organizer.state.active ? organizer.hasText.value : state.text.trim() !== '')
  const dirty = computed(() => (state.phase === 'review' || state.phase === 'saving') && hasContent.value)
  const canSave = computed(() => state.phase === 'review' && positiveId(state.chapterId) !== null
    && state.title.trim() !== '' && hasContent.value)
  const uncertainLines = computed<UncertainLine[]>(() => (state.preview?.lines ?? [])
    .filter(line => line.low_confidence && line.text.trim() !== '')
    .map(line => ({ index: line.index, number: line.index + 1, text: line.text, revised: !state.text.includes(line.text) })))

  function releasePhoto() {
    if (state.previewUrl) environment.revokeObjectURL(state.previewUrl)
    state.previewUrl = ''
    state.fileName = ''
    photo = null
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
    photo = file
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
    if (organizer.state.active) Object.assign(payload, organizer.state.sections)
    else payload[state.section] = state.text
    state.phase = 'saving'
    state.error = null
    state.photoExpiresAt = null
    state.photoWarning = ''
    try {
      state.saved = await gateway.createStudy(payload)
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
    // O estudo já está salvo: uma falha ao guardar a foto só vira aviso, nunca desfaz o estudo.
    if (state.keepPhoto && photo && gateway.storePhoto) {
      try {
        const stored = await gateway.storePhoto(state.saved.id, photo)
        state.photoExpiresAt = stored.item.expires_at
      } catch (error) {
        state.photoWarning = errorMessage(error)
      }
    }
    // Registro do feedback (091-B): em silêncio e sem esperar; uma falha nunca chega ao leitor (FR-007).
    const send = gateway.sendFeedback
    if (send) {
      const studyId = state.saved.id
      const payload: OrganizerFeedbackRequest = { origin: 'digitize', organizer: organizer.suggestion() }
      Promise.resolve().then(() => send(studyId, payload)).catch(() => {})
    }
    state.phase = 'saved'
    releasePhoto()
    return state.saved
  }

  /** Organiza o texto revisado nas 4 seções, com a posição das linhas lidas quando houver. */
  async function organize(): Promise<boolean> {
    if (state.phase !== 'review') return false
    const lines = (state.preview?.lines ?? [])
      .filter(line => Array.isArray(line.bbox))
      .map(line => ({ text: line.text, bbox: line.bbox ?? null, confidence: line.confidence }))
    return organizer.organize(state.text, lines)
  }

  /** Volta ao texto único exatamente como estava antes de organizar. */
  function unorganize() {
    if (!organizer.state.active) return
    state.text = organizer.revert()
  }

  function reset() {
    if (busy.value) return
    organizer.reset()
    releasePhoto()
    // Livro e capítulo ficam: a próxima página costuma ir para o mesmo destino.
    Object.assign(state, {
      phase: 'idle', preview: null, text: '', section: DIGITIZE_DEFAULT_SECTION, title: '', error: null, saved: null,
      keepPhoto: false, photoExpiresAt: null, photoWarning: '',
    })
  }

  function dispose() {
    organizer.cancel()
    reading?.abort()
    reading = null
    releasePhoto()
  }

  return {
    state, busy, dirty, canSave, uncertainLines, organizer, checkStatus, choose, cancel, save, reset, dispose,
    organize, unorganize,
  }
}
