import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const srcDir = path.resolve(__dirname, '../src')

describe('Feature 080: Responsividade de Destaques e Foco em Visualizações Estáveis', () => {
  it('US1: HighlightFilterToolbar permite flex-wrap e expande busca para largura total no mobile', () => {
    const toolbarPath = path.join(srcDir, 'components/highlights/HighlightFilterToolbar.vue')
    const content = fs.readFileSync(toolbarPath, 'utf-8')

    assert.match(
      content,
      /toolbar-primary-row\s*\{[^}]*flex-wrap:\s*wrap/s,
      'toolbar-primary-row deve permitir flex-wrap para acomodar campo de busca e alternador de modo'
    )
    assert.match(
      content,
      /\.search-input-wrapper\s*\{[^}]*width:\s*100%/s,
      'No mobile, o search-input-wrapper deve expandir para largura total'
    )
  })

  it('US1: HighlightsLibraryView aplica contenção de overflow e espaçamento inferior com --mobile-nav-offset', () => {
    const libraryPath = path.join(srcDir, 'views/HighlightsLibraryView.vue')
    const content = fs.readFileSync(libraryPath, 'utf-8')

    assert.match(
      content,
      /--mobile-nav-offset/,
      'HighlightsLibraryView deve aplicar padding inferior com --mobile-nav-offset'
    )
    assert.match(
      content,
      /overflow-x:\s*hidden/,
      'HighlightsLibraryView deve conter transbordamento horizontal com overflow-x: hidden'
    )
    assert.match(
      content,
      /\.pagination-nav\s*\{[^}]*flex-wrap:\s*wrap/s,
      'A navegacao de paginacao deve suportar flex-wrap para telas estreitas'
    )
  })

  it('Foundational: style.css declara container query para palco de estudos', () => {
    const stylePath = path.join(srcDir, 'style.css')
    const content = fs.readFileSync(stylePath, 'utf-8')

    assert.match(
      content,
      /container-type:\s*inline-size/,
      'style.css deve declarar container-type: inline-size para o palco de estudos'
    )
    assert.match(
      content,
      /container-name:\s*study-stage/,
      'style.css deve declarar container-name: study-stage para o palco de estudos'
    )
  })

  it('US1: HighlightCard aplica contenção de largura e alvos táteis mínimos', () => {
    const cardPath = path.join(srcDir, 'components/highlights/HighlightCard.vue')
    const content = fs.readFileSync(cardPath, 'utf-8')

    assert.match(
      content,
      /\.highlight-card\s*\{[^}]*max-width:\s*100%/s,
      'HighlightCard deve declarar max-width: 100% para evitar transbordamento'
    )
    assert.match(
      content,
      /\.highlight-card\s*\{[^}]*box-sizing:\s*border-box/s,
      'HighlightCard deve declarar box-sizing: border-box'
    )
  })

  it('Visualizações estáveis: BookView opera com foco exclusivo em Grade e Lista', () => {
    const bookViewPath = path.join(srcDir, 'views/BookView.vue')
    const content = fs.readFileSync(bookViewPath, 'utf-8')

    assert.ok(content.includes('StudyGridView'), 'BookView deve incluir StudyGridView')
    assert.ok(content.includes('StudyListView'), 'BookView deve incluir StudyListView')
    assert.ok(!content.includes('StudyMapView'), 'BookView não deve incluir StudyMapView')
    assert.ok(!content.includes('StudyCanvasView'), 'BookView não deve incluir StudyCanvasView')
    assert.ok(!content.includes('StudyTreeView'), 'BookView não deve incluir StudyTreeView')
  })

  it('Conformidade de estilo: Zero presença de emojis nos arquivos modificados da Feature 080', () => {
    const filesToCheck = [
      'components/highlights/HighlightFilterToolbar.vue',
      'components/highlights/HighlightCard.vue',
      'views/HighlightsLibraryView.vue',
      'views/BookView.vue'
    ]

    const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u

    for (const file of filesToCheck) {
      const fullPath = path.join(srcDir, file)
      if (fs.existsSync(fullPath)) {
        const content = fs.readFileSync(fullPath, 'utf-8')
        assert.doesNotMatch(
          content,
          emojiRegex,
          `Arquivo ${file} nao deve conter nenhum caractere emoji`
        )
      }
    }
  })
})
