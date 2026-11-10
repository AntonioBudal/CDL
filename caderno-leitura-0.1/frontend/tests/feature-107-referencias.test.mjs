import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import {
  abntInTextCall,
  apaInTextCall,
  bibliography,
  bibtexKey,
  escapeBibtex,
  formatReference,
  missingReferenceFields,
  toABNT,
  toAPA,
  toBibTeX,
  toCSLItem,
  uniqueKeys,
} from '../src/utils/referenceFormats.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

const full = {
  title: 'Livro de Teste',
  subtitle: 'um subtítulo',
  author: 'Ana Maria Fictícia',
  year: 2001,
  publisher: 'Editora Fictícia',
  publication_place: 'São Paulo',
  isbn: '9788535908466',
}
const bare = { title: 'Livro Sem Dados' }

// ---------- ABNT ----------
test('107: ABNT completa e parcial', () => {
  assert.equal(toABNT(full).text, 'FICTÍCIA, Ana Maria. Livro de Teste: um subtítulo. São Paulo: Editora Fictícia, 2001.')
  assert.equal(toABNT(bare).text, 'LIVRO Sem Dados. [s. d.].')
  assert.equal(abntInTextCall(full, { location: 'p. 32-34' }), '(Fictícia, 2001, p. 32–34)')
  assert.equal(abntInTextCall(full, { location: 'Loc. 1820' }), '(Fictícia, 2001, loc. 1820)')
  assert.equal(abntInTextCall(full), '(Fictícia, 2001)')
})

// ---------- APA ----------
test('107: APA com iniciais, partículas, hífen, vários autores e sem data', () => {
  assert.equal(toAPA(full).text, 'Fictícia, A. M. (2001). Livro de Teste: um subtítulo. Editora Fictícia.')
  assert.equal(toAPA(full).html, 'Fictícia, A. M. (2001). <i>Livro de Teste: um subtítulo</i>. Editora Fictícia.')
  assert.equal(toAPA({ title: 'T', author: 'Machado de Assis' }).text, 'Assis, M. (s.d.). T.')
  assert.equal(toAPA({ title: 'T', author: 'Jean-Paul Teste' }).text, 'Teste, J.-P. (s.d.). T.')
  assert.equal(toAPA({ title: 'T', author: 'Ana Fictícia; Bia Teste', year: 1999 }).text, 'Fictícia, A., & Teste, B. (1999). T.')
  assert.equal(toAPA({ title: 'T', author: 'A Um; B Dois; C Três', year: 1999 }).text, 'Um, A., Dois, B., & Três, C. (1999). T.')
  assert.equal(toAPA(bare).text, 'Livro Sem Dados. (s.d.).')
  const many = Array.from({ length: 22 }, (_, i) => `Nome Autor${i + 1}`).join('; ')
  assert.match(toAPA({ title: 'T', author: many }).text, /Autor19, N\., \. \. \. Autor22, N\./)
})

test('107: chamada APA', () => {
  assert.equal(apaInTextCall(full, { location: 'p. 32' }), '(Fictícia, 2001, p. 32)')
  assert.equal(apaInTextCall(full, { location: '32-34' }), '(Fictícia, 2001, pp. 32–34)')
  assert.equal(apaInTextCall({ ...full, author: 'Ana Fictícia e Bia Teste' }), '(Fictícia & Teste, 2001)')
  assert.equal(apaInTextCall({ ...full, author: 'A Um; B Dois; C Três' }), '(Um et al., 2001)')
  assert.equal(apaInTextCall(bare), '(Livro Sem Dados, s.d.)')
})

// ---------- BibTeX ----------
test('107: BibTeX com chave estável, escapes e trecho', () => {
  assert.equal(bibtexKey(full), 'ficticia2001livro')
  assert.equal(bibtexKey(bare), 'anonsdlivro')
  assert.equal(escapeBibtex('A & B {x} 50% $ # _ ~ ^ \\'), 'A \\& B \\{x\\} 50\\% \\$ \\# \\_ \\textasciitilde{} \\textasciicircum{} \\textbackslash{}')
  const bib = toBibTeX(full, { chapter: 'Capítulo 1', location: 'p. 32-34' })
  assert.ok(bib.startsWith('@book{ficticia2001livro,\n'))
  for (const line of [
    'author = {Fictícia, Ana Maria}', 'title = {Livro de Teste: um subtítulo}', 'year = {2001}',
    'publisher = {Editora Fictícia}', 'address = {São Paulo}', 'isbn = {9788535908466}',
    'chapter = {Capítulo 1}', 'pages = {32--34}',
  ]) assert.ok(bib.includes(line), line)
  assert.ok(!toBibTeX(bare).includes('author'))
  assert.ok(toBibTeX({ title: 'T', author: 'Platão' }).includes('author = {{Platão}}'), 'nome único protegido por chaves')
})

// ---------- CSL-JSON ----------
test('107: CSL-JSON válido com trecho', () => {
  const item = toCSLItem(full, { chapter: 'Capítulo 1', location: 'p. 32-34' })
  assert.deepEqual(item, {
    id: 'ficticia2001livro', type: 'book', title: 'Livro de Teste: um subtítulo',
    author: [{ family: 'Fictícia', given: 'Ana Maria' }], issued: { 'date-parts': [[2001]] },
    publisher: 'Editora Fictícia', 'publisher-place': 'São Paulo', ISBN: '9788535908466',
    page: '32-34', note: 'cap. Capítulo 1',
  })
  assert.deepEqual(toCSLItem({ title: 'T "aspas"\nquebra', author: 'Platão' }).author, [{ literal: 'Platão' }])
  const json = formatReference({ title: 'T "aspas"' }, 'csl').text
  assert.equal(JSON.parse(json)[0].title, 'T "aspas"')
  assert.equal(toCSLItem(full, { location: 'Loc. 1820' }).note, 'pos. 1820')
})

// ---------- Bibliografia ----------
test('107: bibliografia ordenada e com chaves únicas', () => {
  const books = [
    { title: 'Zeta', author: 'Bia Teste', year: 2000 },
    { title: 'Alfa Livro', author: 'Ana Fictícia', year: 2001 },
    { title: 'Alfa Livro', author: 'Ana Fictícia', year: 2001 },
  ]
  const abnt = bibliography(books, 'abnt').trim().split('\n\n')
  assert.deepEqual(abnt.map((t) => t.split('.')[0]), ['FICTÍCIA, Ana', 'FICTÍCIA, Ana', 'TESTE, Bia'])
  assert.deepEqual(uniqueKeys(books), ['teste2000zeta', 'ficticia2001alfaa', 'ficticia2001alfab'].map((k, i) => (i === 0 ? 'teste2000zeta' : k)))
  const bib = bibliography(books, 'bibtex')
  assert.equal((bib.match(/@book\{/g) || []).length, 3)
  assert.ok(bib.includes('@book{ficticia2001alfaa,') && bib.includes('@book{ficticia2001alfab,'))
  assert.equal(JSON.parse(bibliography(books, 'csl')).length, 3)
  assert.deepEqual(missingReferenceFields(bare), ['autor', 'ano', 'editora', 'local'])
  assert.deepEqual(missingReferenceFields(full), [])
})

// ---------- Telas ----------
test('107: painel com abas, copiar, baixar, chamada do trecho e obras citadas', () => {
  const panel = read('components/references/ReferencePanel.vue')
  assert.match(panel, /role="tablist" aria-label="Formato da referência"/)
  assert.match(panel, /role="tab"/)
  assert.match(panel, /:aria-selected="item\.value === format"/)
  assert.match(panel, /copyRich\(output\.value\.text, html\)/)
  assert.match(panel, /new Blob\(\[content\]/)
  assert.ok(panel.includes('Chamada no texto (este trecho)'))
  assert.ok(panel.includes('Obras citadas neste estudo'))
  assert.ok(panel.includes('Como você escreveu, sem estruturar'))
  assert.match(panel, /aria-live="polite"/)
  assert.match(panel, /class="quiet reference-link"/)
})

test('107: livro, estudo e biblioteca usam o painel e a bibliografia', () => {
  const book = read('views/BookView.vue')
  assert.match(book, /<ReferencePanel\n\s+v-if="book"\n\s+:open="referenceOpen"/)
  assert.ok(book.includes('<span>Referência</span>'))
  const study = read('views/StudyView.vue')
  assert.match(study, /:passage="\{ chapter: state\.context\.chapter\.name, location: state\.context\.study\.location \}"/)
  assert.match(study, /:cited-text="state\.context\.study\.references"/)
  const books = read('views/BooksView.vue')
  assert.match(books, /bibliography\(list, info\.value\)/)
  assert.match(books, /const list = filteredBooks\.value/)
  assert.match(books, /class="quiet bibliography-button"/)
})
