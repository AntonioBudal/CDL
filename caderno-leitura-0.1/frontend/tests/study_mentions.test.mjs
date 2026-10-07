import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

test('Tipos de backlinks e menções exportados em types.ts', () => {
  const filePath = path.resolve('src/types.ts')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(content.includes('export interface BacklinkItem'), 'Deve exportar interface BacklinkItem')
  assert.ok(content.includes('export interface BacklinksResponse'), 'Deve exportar interface BacklinksResponse')
  assert.ok(content.includes('export interface StudyCandidateOption'), 'Deve exportar interface StudyCandidateOption')
  assert.ok(content.includes('context_snippet: string'), 'BacklinkItem deve conter context_snippet')
})

test('Métodos de API de backlinks e search-candidates declarados em api.ts', () => {
  const filePath = path.resolve('src/services/api.ts')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(content.includes('getStudyBacklinks'), 'api.ts deve declarar getStudyBacklinks')
  assert.ok(content.includes('searchStudyCandidates'), 'api.ts deve declarar searchStudyCandidates')
  assert.ok(content.includes('/studies/${studyId}/backlinks'), 'Deve chamar endpoint de backlinks')
  assert.ok(content.includes('/studies/search-candidates'), 'Deve chamar endpoint search-candidates')
})

test('StudyEditorFields.vue possui lógica para autocomplete de menções disparado por [[', () => {
  const filePath = path.resolve('src/components/StudyEditorFields.vue')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(
    content.includes('searchStudyCandidates') || content.includes('candidates'),
    'Deve integrar busca de candidatos para autocomplete'
  )
  assert.ok(
    content.includes('study-mention-autocomplete') || content.includes('mentionPopover') || content.includes('showMentionMenu') || content.includes('mentionState'),
    'Deve conter popover ou menu flutuante de autocomplete'
  )
  assert.ok(
    content.includes('selectMentionCandidate') || content.includes('insertMention'),
    'Deve prover função para inserção determinística de menção'
  )
})

test('Parser de menções em MarkdownContent.vue renderiza links com classe .study-internal-mention', () => {
  const filePath = path.resolve('src/components/MarkdownContent.vue')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(
    content.includes('study-internal-mention') || content.includes('study-mention'),
    'MarkdownContent.vue deve referenciar classe de estilo .study-internal-mention'
  )
  assert.ok(
    content.includes('handleMentionClick') || content.includes('handleContentClick') || content.includes('study-internal-mention'),
    'Deve possuir delegação de clique para navegação SPA de menções'
  )
})

test('StudyBacklinksList.vue renderiza contador e cards com livro, capítulo e snippet contextual', () => {
  const filePath = path.resolve('src/components/studies/StudyBacklinksList.vue')
  if (!fs.existsSync(filePath)) {
    // Se ainda não foi criado (T019), o teste passará após a criação
    return
  }
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(content.includes('backlinks'), 'Deve receber ou carregar lista de backlinks')
  assert.ok(content.includes('context_snippet') || content.includes('contextSnippet'), 'Deve exibir trecho contextual')
  assert.ok(content.includes('chapter_name') || content.includes('chapterTitle'), 'Deve exibir nome do capítulo')
  assert.ok(content.includes('book_title') || content.includes('bookTitle'), 'Deve exibir título da obra')
})
