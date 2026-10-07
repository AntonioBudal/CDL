import { computed, ref } from 'vue'
import { api } from '../services/api.ts'
import { useInboxCount } from './useInboxCount.ts'
import type { InboxCapture, InboxCaptureCreatePayload } from '../types.ts'

export interface QuickCaptureInitialOptions {
  bookId?: number | null
  initialContent?: string
  initialSource?: string
}

const isModalOpen = ref<boolean>(false)
const selectedBookId = ref<number | null>(null)
const initialText = ref<string>('')
const initialSourceHint = ref<string>('')
const isSubmitting = ref<boolean>(false)
const errorMessage = ref<string | null>(null)

export function useQuickCapture() {
  const { increment } = useInboxCount()

  const isOpen = computed(() => isModalOpen.value)
  const defaultBookId = computed(() => selectedBookId.value)
  const defaultContent = computed(() => initialText.value)
  const defaultSource = computed(() => initialSourceHint.value)
  const submitting = computed(() => isSubmitting.value)
  const error = computed(() => errorMessage.value)

  function open(options?: QuickCaptureInitialOptions): void {
    selectedBookId.value = options?.bookId ?? null
    initialText.value = options?.initialContent ?? ''
    initialSourceHint.value = options?.initialSource ?? ''
    errorMessage.value = null
    isModalOpen.value = true
  }

  function close(): void {
    isModalOpen.value = false
    selectedBookId.value = null
    initialText.value = ''
    initialSourceHint.value = ''
    errorMessage.value = null
  }

  async function submit(payload: InboxCaptureCreatePayload): Promise<InboxCapture | null> {
    if (!payload.content || !payload.content.trim()) {
      errorMessage.value = 'O texto da captura não pode estar vazio.'
      return null
    }

    isSubmitting.value = true
    errorMessage.value = null
    try {
      const created = await api.createInboxCapture({
        content: payload.content.trim(),
        source_hint: payload.source_hint?.trim() || null,
        book_id: payload.book_id ?? null,
      })
      increment()
      close()
      return created
    } catch (err: unknown) {
      errorMessage.value = err instanceof Error ? err.message : 'Falha ao salvar captura no Inbox.'
      return null
    } finally {
      isSubmitting.value = false
    }
  }

  return {
    isOpen,
    defaultBookId,
    defaultContent,
    defaultSource,
    submitting,
    error,
    open,
    close,
    submit,
  }
}
