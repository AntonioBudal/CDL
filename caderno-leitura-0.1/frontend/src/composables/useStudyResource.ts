import { reactive } from 'vue'
import { errorMessage } from '../services/api.ts'
import { positiveId, type Book, type Chapter, type Study, type StudyContext } from '../types.ts'

interface StudyGateway {
  getStudy: (id: number, signal?: AbortSignal) => Promise<Study>
  listBooks: (signal?: AbortSignal) => Promise<Book[]>
  listChapters: (id: number, signal?: AbortSignal) => Promise<Chapter[]>
}

export function useStudyResource(gateway: StudyGateway) {
  const state = reactive({ loading: true, error: '', context: null as StudyContext | null })
  let request: AbortController | null = null

  function cancel() { request?.abort() }

  async function load(bookParam: unknown, studyParam: unknown): Promise<StudyContext | null> {
    cancel()
    const controller = new AbortController()
    request = controller
    state.loading = true
    state.error = ''
    state.context = null
    const bookId = positiveId(bookParam)
    const studyId = positiveId(studyParam)
    if (bookId === null || studyId === null) {
      state.error = 'Estudo não encontrado. Confira o endereço ou volte aos livros.'
      state.loading = false
      return null
    }
    try {
      const [study, books, chapters] = await Promise.all([
        gateway.getStudy(studyId, controller.signal),
        gateway.listBooks(controller.signal),
        gateway.listChapters(bookId, controller.signal),
      ])
      if (controller.signal.aborted) return null
      const book = books.find(item => item.id === bookId)
      const chapter = chapters.find(item => item.id === study.chapter_id && item.book_id === bookId)
      if (!book || !chapter || study.id !== studyId) {
        state.error = 'Este estudo não foi encontrado neste livro. Volte aos livros para abri-lo.'
        return null
      }
      state.context = { book, chapter, study }
      return state.context
    } catch (error) {
      if (!controller.signal.aborted) state.error = errorMessage(error)
      return null
    } finally {
      if (!controller.signal.aborted) state.loading = false
    }
  }

  return { state, load, cancel }
}
