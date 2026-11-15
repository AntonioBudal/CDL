import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { conceptKey, replaceStudyMentions } from '../src/services/markdown.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

test('108: chave do conceito igual à do servidor', () => {
  assert.equal(conceptKey('Mímese'), 'mimese')
  assert.equal(conceptKey('Razão Prática!'), 'razao-pratica')
  assert.equal(conceptKey('  '), '')
})

test('108: [[conceito:…]] vira link de conceito sem afetar menções a estudos', () => {
  const html = replaceStudyMentions('<p>Ver [[conceito: Mímese ]] e [[Outro Estudo|12]] e [[Estudo Livre]].</p>')
  assert.match(html, /<a href="\/conceitos\/mimese" class="study-concept-mention" data-concept-key="mimese" aria-label="conceito: Mímese">Mímese<\/a>/)
  assert.match(html, /<a href="\/estudos\/12" class="study-internal-mention" data-study-id="12" data-study-title="Outro Estudo">Outro Estudo<\/a>/)
  assert.match(html, /class="study-internal-mention" data-study-title="Estudo Livre"/)
  assert.ok(!html.includes('[[conceito'))
  const code = replaceStudyMentions('<code>[[conceito:Mímese]]</code>')
  assert.equal(code, '<code>[[conceito:Mímese]]</code>', 'dentro de código fica como está')
})

test('108: leitura navega para o conceito; editor sugere conceitos', () => {
  const content = read('components/MarkdownContent.vue')
  assert.match(content, /closest\('\.study-concept-mention'\)/)
  assert.match(content, /router\?\.push\(`\/conceitos\/\$\{concept\.dataset\.conceptKey\}`\)/)
  const editor = read('components/StudyEditorFields.vue')
  assert.match(editor, /const CONCEPT_PREFIX = \/\^conceito\\s\*:\\s\*\/i/)
  assert.match(editor, /api\.getConceptCandidates\(conceptQuery, onlyConcepts \? 10 : 4\)/)
  assert.match(editor, /mentionToken = `\[\[conceito:\$\{candidate\.term\}\]\]`/)
  assert.equal((editor.match(/<span class="mention-candidate-kind">Conceito<\/span>/g) || []).length, 2)
})

test('108: páginas, rotas, menus e API', () => {
  const router = read('router/index.ts')
  assert.match(router, /path: '\/conceitos', name: 'lexicon'/)
  assert.match(router, /path: '\/conceitos\/:key', name: 'concept'/)
  assert.match(read('components/layout/NavigationTabs.vue'), /to: '\/conceitos',\n\s+label: t\('nav\.concepts'\)/) // F0.12.09: texto por chave (pt-BR em src/i18n/messages)
  assert.ok(read('components/navigation/MobileMoreMenu.vue').includes("<span class=\"drawer-item-label\">{{ t('nav.concepts') }}</span>")) // F0.12.09: texto por chave
  assert.ok(read('components/layout/UserDropdown.vue').includes("<span>{{ t('nav.concepts') }}</span>")) // F0.12.09: texto por chave
  const api = read('services/api.ts')
  assert.match(api, /listConcepts: \(params/)
  assert.match(api, /getConcept: \(key: string/)
  const lexicon = read('views/LexiconView.vue')
  assert.match(lexicon, /aria-live="polite"/)
  assert.match(lexicon, /class="quiet lexicon-page"/)
  const concept = read('views/ConceptView.vue')
  assert.ok(concept.includes('Ainda sem definição nos seus estudos.'))
  assert.ok(concept.includes('Mencionado em'))
})
