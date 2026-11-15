import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

test('116: tela Importar biblioteca, rota e entrada em Livros', () => {
  const view = read('views/LibraryImportView.vue')
  assert.match(view, /<h1 id="library-import-heading">Importar biblioteca<\/h1>/)
  assert.match(view, /api\.previewLibraryImport\(file\.value\)/)
  assert.match(view, /api\.importLibrary\(file\.value, choices, withReviews\.value\)/)
  assert.match(view, /As notas em estrelas não são importadas/)
  assert.match(view, /Goodreads[\s\S]*StoryGraph[\s\S]*BookWyrm/)
  assert.match(read('router/index.ts'), /path: '\/livros\/importar', name: 'library-import'/)
  assert.match(read('views/BooksView.vue'), /<RouterLink to="\/livros\/importar" class="books-import-link">Importar de outro serviço<\/RouterLink>/)
})

test('116: leitor digital aceita Readwise (CSV) e Omnivore (ZIP)', () => {
  const view = read('views/EreaderImportView.vue')
  assert.match(view, /accept="[^"]*\.csv[^"]*\.zip/)
  assert.match(view, /readwise: 'Readwise', omnivore: 'Omnivore'/)
  assert.match(read('types.ts'), /'readwise' \| 'omnivore'/)
})
