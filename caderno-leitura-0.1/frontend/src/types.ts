export interface Book { id: number; title: string; author: string | null }
export interface Chapter { id: number; book_id: number; name: string; position: number }
export interface StudySummary {
  id: number
  chapter_id: number
  title: string
  location: string
  created_at: string
  updated_at: string
}
export interface AnalysisSections { summary: string; explanation: string; concepts: string; references: string }
export interface Study extends StudySummary, AnalysisSections { source_response: string; notes: string }
export type StudyPatch = Partial<AnalysisSections & Pick<Study, 'title' | 'location' | 'notes'>>
export interface StudyContext { book: Book; chapter: Chapter; study: Study }
export interface StudyCreate extends AnalysisSections {
  chapter_id: number
  title: string | null
  location: string
  source_response: string
  notes: string
}
export interface ImportWarning { code: string; message: string; section: string | null; line: number | null }
export interface ImportPreview extends AnalysisSections { source_response: string; unassigned_text: string; warnings: ImportWarning[] }
export const SECTION_LABELS = [
  { key: 'summary', label: 'Resumo' },
  { key: 'explanation', label: 'Explicação' },
  { key: 'concepts', label: 'Conceitos' },
  { key: 'references', label: 'Referências' },
] as const

export function positiveId(value: unknown): number | null {
  if (typeof value !== 'string' || !/^\d+$/.test(value)) return null
  const id = Number(value)
  return Number.isSafeInteger(id) && id > 0 ? id : null
}
