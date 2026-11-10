import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

test('105: API envia o arquivo nas duas chamadas e as escolhas em JSON', () => {
  const api = read('services/api.ts')
  assert.match(api, /request<EreaderPreviewResponse>\('\/inbox\/ereader\/preview', \{ method: 'POST', body: formData \}\)/)
  assert.match(api, /formData\.append\('choices', JSON\.stringify\(choices\)\)/)
  assert.match(api, /request<EreaderImportResponse>\('\/inbox\/ereader\/import'/)
  const types = read('types.ts')
  for (const name of ['EreaderPreviewResponse', 'EreaderChoice', 'EreaderImportResponse', 'EreaderBookPreview']) {
    assert.match(types, new RegExp(`export interface ${name} \\{`))
  }
})

test('105: rota e botão na Mesa de Triagem', () => {
  assert.match(read('router/index.ts'), /path: '\/inbox\/importar-leitor', name: 'ereader-import'/)
  const inbox = read('views/InboxView.vue')
  assert.match(inbox, /<RouterLink to="\/inbox\/importar-leitor" class="button quiet ereader-import-link">Importar do Kindle ou Kobo<\/RouterLink>/)
})

test('105: tela em três passos com prévia, destino por livro e resultado', () => {
  const view = read('views/EreaderImportView.vue')
  assert.match(view, /type Step = 'pick' \| 'review' \| 'done'/)
  assert.ok(view.includes('documents/My Clippings.txt'))
  assert.ok(view.includes('.kobo/KoboReader.sqlite'))
  assert.ok(view.includes('Nada é gravado nesta etapa'))
  assert.match(view, /book\.suggested_action === 'existing' && book\.suggested_book_id \? String\(book\.suggested_book_id\) : 'create'/)
  assert.ok(view.includes('<option value="skip">Não importar este livro</option>'))
  assert.match(view, /return \{ key: book\.key, action: 'existing', book_id: Number\(value\) \}/)
  assert.match(view, /aria-live="polite"/)
  assert.match(view, /query: \{ livro: String\(book\.book_id\) \}/)
  assert.match(view, /class="quiet ereader-secondary"/)
})
