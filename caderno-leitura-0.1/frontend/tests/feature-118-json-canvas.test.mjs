import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const read = (rel) => fs.readFileSync(path.resolve(process.cwd(), 'src', rel), 'utf-8')

test('118: formato JSON Canvas no modal de exportar, só para o livro', () => {
  const modal = read('components/ExportModal.vue')
  assert.match(modal, /<label v-if="scope === 'book'" class="radio-card" :class="\{ selected: format === 'canvas' \}">/)
  assert.match(modal, /JSON Canvas \(Obsidian\)/)
  assert.match(modal, /await api\.exportBookCanvas\(props\.bookId\)/)
  assert.match(modal, /v-if="exportType === 'full' && format !== 'canvas'"/)
  assert.match(modal, /v-else-if="format !== 'canvas'"/)
  assert.match(read('services/api.ts'), /downloadExportFile\(`\/api\/books\/\$\{id\}\/canvas\/export`/)
})

test('118: nada de quadro na tela (decisão da 0.9 mantida)', () => {
  assert.ok(!fs.existsSync(path.resolve(process.cwd(), 'src', 'components', 'views', 'StudyCanvasView.vue')))
})
