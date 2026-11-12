import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

test('111: cartão "Receber destaques" nas Configurações', () => {
  const card = read('components/settings/ReceiverTokenCard.vue')
  assert.match(card, /`\$\{window\.location\.origin\}\/api\/receptor\/readwise\/v2`/)
  assert.match(card, /Seu token \(aparece só agora\)/)
  assert.match(card, /api\.issueReceiverToken\(\)/)
  assert.match(card, /api\.revokeReceiverToken\(\)/)
  assert.match(card, /A versão web do Readest não funciona/)
  assert.equal((card.match(/class="quiet receiver-button"/g) || []).length, 4)
  assert.match(read('views/SettingsView.vue'), /<ReceiverTokenCard \/>/)
  const api = read('services/api.ts')
  assert.match(api, /getReceiverToken: \(signal\?: AbortSignal\) => request<ReceiverTokenStatus>\('\/account\/receiver-token'/)
  assert.match(api, /revokeReceiverToken: \(\) => request<void>\('\/account\/receiver-token', \{ method: 'DELETE' \}\)/)
})

test('111: tela de importação aceita o JSON do KOReader', () => {
  const view = read('views/EreaderImportView.vue')
  assert.match(view, /<h1 id="ereader-heading">Importar de leitor digital<\/h1>/)
  assert.match(view, /accept="\.txt,\.sqlite,\.json,/)
  assert.match(view, /koreader: 'KOReader'/)
  assert.match(read('router/index.ts'), /meta: \{ title: 'Importar de leitor digital' \}/)
  assert.match(read('types.ts'), /export type EreaderSource = 'kindle' \| 'kobo' \| 'koreader' \| 'readest'/)
})
