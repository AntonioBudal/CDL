import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import {
  abntCallWithLocator,
  buildReferenceScopes,
  formatLocator,
  parseLocator,
  referenceLines,
} from '../src/utils/referenceScopes.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

const book = { title: 'Livro de Teste', author: 'Ana Fictícia', subtitle: '', year: 2001 }

// ---------- Localizador ----------

test('099: localizações de página', () => {
  for (const [input, value] of [
    ['p. 32–34', '32–34'],
    ['pp. 32-34', '32–34'],
    ['p.32', '32'],
    ['pág. 7', '7'],
    ['Página 12', '12'],
    ['32 - 34', '32–34'],
    ['15', '15'],
  ]) {
    assert.deepEqual(parseLocator(input), { kind: 'page', value }, input)
  }
})

test('099: localizações de posição (e-book)', () => {
  assert.deepEqual(parseLocator('Loc. 1820'), { kind: 'loc', value: '1820' })
  assert.deepEqual(parseLocator('posição 1820'), { kind: 'loc', value: '1820' })
  assert.deepEqual(parseLocator('pos. 10-12'), { kind: 'loc', value: '10–12' })
})

test('099: localização livre e vazia', () => {
  assert.deepEqual(parseLocator('cap. 3, início'), { kind: 'raw', value: 'cap. 3, início' })
  assert.deepEqual(parseLocator('   '), { kind: 'none', value: '' })
  assert.deepEqual(parseLocator(null), { kind: 'none', value: '' })
  assert.equal(formatLocator({ kind: 'page', value: '32–34' }), 'p. 32–34')
  assert.equal(formatLocator({ kind: 'loc', value: '1820' }), 'loc. 1820')
})

// ---------- Escopos ----------

test('099: obra completa e incompleta', () => {
  assert.deepEqual(buildReferenceScopes({ book }).work.missing, [])
  assert.equal(buildReferenceScopes({ book }).work.complete, true)
  assert.deepEqual(buildReferenceScopes({ book: { ...book, year: null } }).work.missing, ['year'])
  assert.deepEqual(buildReferenceScopes({ book: { ...book, author: ' ', year: null } }).work.missing, ['author', 'year'])
  assert.deepEqual(buildReferenceScopes({}).work.missing, ['author', 'year'])
})

test('099: trecho e obras citadas', () => {
  const scopes = buildReferenceScopes({
    book,
    chapter: { name: 'Capítulo 1' },
    location: 'p. 3',
    referencesText: '### Referências\n- Obra Fictícia A\n\n2. Obra Fictícia B\n* Obra Fictícia C',
  })
  assert.equal(scopes.passage.chapter, 'Capítulo 1')
  assert.deepEqual(scopes.passage.locator, { kind: 'page', value: '3' })
  assert.deepEqual(scopes.cited.lines, ['Obra Fictícia A', 'Obra Fictícia B', 'Obra Fictícia C'])
  assert.equal(scopes.cited.count, 3)
  assert.deepEqual(referenceLines(''), [])
})

test('099: chamada ABNT com página, posição, sem localização e sem ano', () => {
  assert.equal(abntCallWithLocator(buildReferenceScopes({ book, location: 'p. 32-34' })), '(Fictícia, 2001, p. 32–34)')
  assert.equal(abntCallWithLocator(buildReferenceScopes({ book, location: 'Loc. 1820' })), '(Fictícia, 2001, loc. 1820)')
  assert.equal(abntCallWithLocator(buildReferenceScopes({ book, location: 'cap. 3' })), '(Fictícia, 2001)')
  assert.equal(abntCallWithLocator(buildReferenceScopes({ book: { ...book, year: null } })), '(Fictícia, [s. d.])')
  assert.equal(abntCallWithLocator(buildReferenceScopes({ book: { title: 'Livro de Teste' } })), '(Livro..., [s. d.])')
})

// ---------- Tela ----------

test('099: faixa da obra mostra dados, aviso e botão só com permissão', () => {
  const strip = read('components/import/ImportWorkMetaStrip.vue')
  assert.match(strip, /buildReferenceScopes\(/)
  assert.match(strip, /abntCallWithLocator\(/)
  assert.ok(strip.includes("'sem autor'") && strip.includes("'sem ano'"))
  assert.match(strip, /props\.book\.can_edit !== false/)
  assert.match(strip, /v-if="canEdit && !editing"/)
  assert.ok(strip.includes('Completar dados do livro'))
  assert.ok(strip.includes('Como este estudo será citado'))
  for (const label of ['Obra:', 'Trecho:', 'Obras citadas:']) assert.ok(strip.includes(label), label)
})

test('099: completar usa o PATCH com expected_version e mostra erro sem perder o digitado', () => {
  const strip = read('components/import/ImportWorkMetaStrip.vue')
  assert.match(strip, /api\.updateBook\(book\.id, payload\)/)
  assert.match(strip, /payload\.expected_version = book\.version/)
  assert.match(strip, /formError\.value = errorMessage\(error\)/)
  assert.match(strip, /emit\('book-updated', updated\)/)
  assert.match(strip, /year < 1000 \|\| year > 2100/)
  // controles secundários neutros
  assert.match(strip, /class="quiet work-meta-complete-btn"/)
  assert.match(strip, /class="quiet" :disabled="saving" @click="closeForm"/)
})

test('099: ImportView integra a faixa, troca o livro atualizado e unifica o rótulo da localização', () => {
  const view = read('views/ImportView.vue')
  assert.match(view, /<ImportWorkMetaStrip[\s\S]*?:references-text="state\.sections\.references"[\s\S]*?@book-updated="onBookUpdated"/)
  assert.match(view, /function onBookUpdated\(updated: Book\)/)
  assert.ok(view.includes('Página ou localização <span class="optional">opcional</span>'))
  assert.ok(!view.includes('>Localização <span'))
})
