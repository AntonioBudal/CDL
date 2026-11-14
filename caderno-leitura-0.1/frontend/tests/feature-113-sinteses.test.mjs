import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { embedToken, insertOnOwnLine, parseEmbed, splitBody } from '../src/utils/synthesisEmbeds.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

// Mesmos casos do backend (tests/test_synthesis.py::test_parser).
const BODY = `# Minha síntese

Texto meu sobre os dois livros.

![[Estudo A|5]]
![[Estudo A|5#resumo]]
  ![[destaque:9]]
Isto tem ![[Estudo A|5]] no meio.
![[Sem id]]
![[Estudo A|5#capitulo]]

\`\`\`
![[Estudo A|5]]
\`\`\`
![[Estudo A|5]]
`

test('113: analisador igual ao do servidor', () => {
  const kinds = splitBody(BODY).map((s) => [s.type, s.type === 'embed' ? s.embed.key : null])
  assert.deepEqual(kinds, [
    ['text', null],
    ['embed', 'study:5'],
    ['embed', 'study:5#resumo'],
    ['embed', 'highlight:9'],
    ['invalid', null],
    ['invalid', null],
    ['invalid', null],
    ['text', null],
    ['embed', 'study:5'],
    ['text', null],
  ])
  assert.equal(parseEmbed('Título com | barra|12#Conceitos')?.key, 'study:12#conceitos')
  assert.equal(parseEmbed('destaque:0'), null)
  assert.equal(parseEmbed('Título|0'), null)
})

test('113: marca pronta e inserção numa linha própria', () => {
  assert.equal(embedToken('study', 3, 'Estudo [x] | y'), '![[Estudo x y|3]]')
  assert.equal(embedToken('section', 3, 'Estudo', 'conceitos'), '![[Estudo|3#conceitos]]')
  assert.equal(embedToken('highlight', 7), '![[destaque:7]]')
  assert.deepEqual(insertOnOwnLine('abc def', 3, 'X'), { body: 'abc\nX\n def', cursor: 5 })
  assert.deepEqual(insertOnOwnLine('', 0, 'X'), { body: 'X', cursor: 1 })
  assert.deepEqual(insertOnOwnLine('a\n', 2, 'X'), { body: 'a\nX', cursor: 3 })
})

test('113: telas, rotas, menus e API', () => {
  const router = read('router/index.ts')
  assert.match(router, /path: '\/sinteses', name: 'syntheses'/)
  assert.match(router, /path: '\/sinteses\/:id\(\\\\d\+\)', name: 'synthesis'/)
  assert.match(read('components/layout/NavigationTabs.vue'), /routes: \['syntheses', 'synthesis'\]/)
  assert.match(read('components/navigation/MobileMoreMenu.vue'), /to="\/sinteses"/)
  assert.match(read('components/layout/UserDropdown.vue'), /Cadernos de síntese/)
  const view = read('views/SynthesisView.vue')
  assert.match(view, /<EmbedBlock v-else-if="segment\.type === 'embed'"/)
  assert.match(view, /Marca de trecho não reconhecida/)
  assert.match(view, /useUnsavedChanges\(/)
  assert.match(view, /e\.status === 409/)
  assert.match(read('components/synthesis/InsertEmbedDialog.vue'), /Estudo inteiro/)
  assert.match(read('views/SynthesesView.vue'), /Excluídos/)
  const api = read('services/api.ts')
  assert.match(api, /`\/syntheses\/\$\{id\}\/resolved`/)
  assert.match(api, /downloadExportFile\(`\/api\/syntheses\/\$\{id\}\/export`/)
})
