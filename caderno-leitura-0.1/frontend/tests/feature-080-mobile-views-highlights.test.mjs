import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const srcDir = path.resolve(__dirname, '../src')

describe('Feature 080: Visualizações Móveis e Responsividade de Destaques', () => {
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

  it('US2: StudyMapView implementa gestos táteis de pan/pinch e alternador móvel de lista semântica', () => {
    const mapPath = path.join(srcDir, 'components/views/StudyMapView.vue')
    const content = fs.readFileSync(mapPath, 'utf-8')

    assert.match(
      content,
      /touchstart|touchmove|handleTouch/,
      'StudyMapView deve conter handlers de eventos de toque para pan e pinch zoom'
    )
    assert.match(
      content,
      /mobile-map-view-mode|relations_list|lista-relacoes|relacoes-list/s,
      'StudyMapView deve oferecer alternador para lista semântica de relações no celular'
    )
  })

  it('US3: StudyCanvasView desbloqueia rolagem vertical no mobile com touch-action: pan-y', () => {
    const canvasPath = path.join(srcDir, 'components/views/StudyCanvasView.vue')
    const content = fs.readFileSync(canvasPath, 'utf-8')

    assert.match(
      content,
      /touch-action:\s*pan-y/,
      'StudyCanvasView deve desbloquear a rolagem vertical no mobile através de touch-action: pan-y'
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

  it('US2: StudyMapView restringe pinch zoom no intervalo [0.5, 2.5]', () => {
    const mapPath = path.join(srcDir, 'components/views/StudyMapView.vue')
    const content = fs.readFileSync(mapPath, 'utf-8')

    assert.match(
      content,
      /Math\.min\(2\.5,\s*Math\.max\(0\.5/,
      'StudyMapView deve limitar o pinch zoom ao intervalo canônico de 0.5 a 2.5'
    )
  })

  it('US3: CanvasToolbar compacta ferramentas secundárias em menu em telas menores', () => {
    const toolbarPath = path.join(srcDir, 'components/views/canvas/CanvasToolbar.vue')
    const content = fs.readFileSync(toolbarPath, 'utf-8')

    assert.match(
      content,
      /secondary-tools-group/,
      'CanvasToolbar deve agrupar ferramentas secundárias em secondary-tools-group'
    )
    assert.match(
      content,
      /more-tools-trigger/,
      'CanvasToolbar deve ter gatilho more-tools-trigger para telas menores'
    )
  })

  it('US4: StudyTreeNodeItem oculta drag handle em pointer: coarse e garante alvos táteis de 44px', () => {
    const treeNodePath = path.join(srcDir, 'components/views/StudyTreeNodeItem.vue')
    const content = fs.readFileSync(treeNodePath, 'utf-8')

    assert.match(
      content,
      /@media\s*\(pointer:\s*coarse\)[^}]*tree-drag-handle\s*\{[^}]*display:\s*none/s,
      'StudyTreeNodeItem deve ocultar a alça de arrasto sob pointer: coarse'
    )
    assert.match(
      content,
      /min-height:\s*44px/,
      'StudyTreeNodeItem deve garantir alvos táteis mínimos de 44px para botões de menu'
    )
  })

  it('US4: StudyTreeView comprime indentação de ramos aninhados no mobile', () => {
    const treePath = path.join(srcDir, 'components/views/StudyTreeView.vue')
    const content = fs.readFileSync(treePath, 'utf-8')

    assert.match(
      content,
      /@media\s*\(max-width:\s*768px\)[\s\S]*?\.tree-branch\s*\{[^}]*margin-left:/,
      'StudyTreeView deve comprimir indentação no mobile em @media (max-width: 768px)'
    )
  })

  it('Conformidade de estilo: Zero presença de emojis nos arquivos modificados da Feature 080', () => {
    const filesToCheck = [
      'components/highlights/HighlightFilterToolbar.vue',
      'components/highlights/HighlightCard.vue',
      'views/HighlightsLibraryView.vue',
      'components/views/StudyMapView.vue',
      'components/views/StudyCanvasView.vue',
      'components/views/StudyTreeNodeItem.vue',
      'components/views/StudyTreeView.vue',
      'components/views/canvas/CanvasToolbar.vue'
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
