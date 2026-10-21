import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const bookViewPath = path.resolve(__dirname, '../src/views/BookView.vue')

describe('Refatoração da Visualização Interna do Livro (/livros) - Layout Horizontal e Barra Compacta', () => {
  const content = fs.readFileSync(bookViewPath, 'utf-8')

  it('US1: Arquitetura em 3 faixas horizontais empilhadas eliminando layout de 3 colunas verticais', () => {
    // Verifica a presença das 3 faixas estruturais
    assert.ok(content.includes('chapters-horizontal-bar'), 'Deve conter a faixa superior de capítulos (.chapters-horizontal-bar)')
    assert.ok(content.includes('studies-main-stage'), 'Deve conter o bloco central de estudos com 100% da largura (.studies-main-stage)')
    assert.ok(content.includes('inspector-horizontal-bar'), 'Deve conter a faixa inferior do inspetor (.inspector-horizontal-bar)')

    // Verifica que o layout usa flex-direction column para empilhar as faixas
    assert.match(
      content,
      /\.book-layout,\s*\.book-split-layout\s*\{[^}]*display:\s*flex;[^}]*flex-direction:\s*column;/s,
      'Layout principal deve empilhar faixas verticalmente via flex-direction: column'
    )
  })

  it('US1: Faixa Superior de Capítulos possui navegação por pílulas roláveis e controles contextuais', () => {
    // Barra de navegação e pílulas
    assert.ok(content.includes('chapters-nav-strip'), 'Deve conter faixa rolável de navegação (.chapters-nav-strip)')
    assert.ok(content.includes('chapters-pills-track'), 'Deve conter trilha de pílulas (.chapters-pills-track)')
    assert.ok(content.includes('chapter-pill'), 'Deve conter elementos de pílula de capítulo (.chapter-pill)')
    assert.ok(content.includes('scrollIntoView'), 'Deve auto-rolar suavemente para o capítulo ativo')

    // Controles contextuais no capítulo selecionado
    assert.ok(content.includes('chapter-pill-active-tools'), 'Deve conter barra de ferramentas no capítulo ativo')
    assert.ok(content.includes('moveChapter'), 'Deve conter suporte a reordenação de capítulos')
    assert.ok(content.includes('startEditChapter'), 'Deve permitir renomeação rápida do capítulo')

    // Criação inline rápida
    assert.ok(content.includes('startCreateChapterInline'), 'Deve conter gatilho para criação inline')
    assert.ok(content.includes('new-chapter-inline-box'), 'Deve conter caixa de criação inline')
    assert.ok(content.includes('@keydown.esc="cancelCreateChapterInline"'), 'Deve fechar criação inline ao pressionar Escape')

    // Dropdown mobile
    assert.ok(content.includes('chapters-mobile-select'), 'Deve conter seletor dropdown para dispositivos móveis')
  })

  it('US2: Bloco Central de Estudos ocupa 100% da largura útil sem barra de rolagem forçada', () => {
    assert.match(
      content,
      /\.studies-main-stage\s*\{[^}]*width:\s*100%;/s,
      'Bloco central de estudos deve ter width: 100%'
    )
    assert.ok(content.includes('<ViewSwitcher'), 'Deve manter controle de alternância de visualização grid/list')
    assert.ok(content.includes('activeRendererComponent'), 'Deve renderizar dinamicamente StudyGridView ou StudyListView')
  })

  it('US3: Faixa Inferior do Inspetor atua como status bar analítica horizontal', () => {
    assert.ok(content.includes('inspector-bar-content'), 'Deve conter container do inspetor (.inspector-bar-content)')
    assert.ok(content.includes('inspector-metrics-grid'), 'Deve conter grade de métricas (.inspector-metrics-grid)')
    assert.ok(content.includes('inspector-item'), 'Deve conter itens de métricas (.inspector-item)')
    assert.ok(content.includes('Capítulo Selecionado'), 'Deve exibir indicador de capítulo selecionado')
    assert.ok(content.includes('Total de Capítulos'), 'Deve exibir total de capítulos')
    assert.ok(content.includes('Estudos no Capítulo'), 'Deve exibir estudos no capítulo')

    // Card de estudo em foco
    assert.ok(content.includes('inspector-study-focus-card'), 'Deve conter card contextual de estudo em foco')
    assert.ok(content.includes('Abrir leitura'), 'Deve conter link direto para leitura do estudo em foco')
  })

  it('US4: Barra de Ações do Cabeçalho com botões compactos e efeito expanding pill no hover/foco', () => {
    assert.ok(content.includes('icon-action-btn'), 'Botões devem utilizar a classe .icon-action-btn')
    assert.ok(content.includes('btn-pill-label'), 'Rótulos expansíveis devem usar a classe .btn-pill-label')
    assert.ok(content.includes('focus-toggle-btn'), 'Deve incluir botão discreto de Modo Foco')
    assert.ok(content.includes('danger-action'), 'Botão de mover para lixeira deve possuir variação de perigo')

    // CSS de expansão suave
    assert.match(
      content,
      /\.icon-action-btn\s*\{[^}]*min-height:\s*44px;[^}]*min-width:\s*44px;/s,
      'Botões de ação devem ter alvos mínimos de 44x44px'
    )
    assert.match(
      content,
      /\.icon-action-btn\s+\.btn-pill-label\s*\{[^}]*max-width:\s*0;[^}]*opacity:\s*0;/s,
      'Rótulo deve iniciar recolhido com max-width: 0 e opacity: 0'
    )
    assert.match(
      content,
      /\.icon-action-btn:hover:not\(:disabled\)\s+\.btn-pill-label[^}]*max-width:\s*180px;[^}]*opacity:\s*1;/s,
      'Rótulo deve expandir no hover com max-width e opacity 1'
    )
  })

  it('US5: Responsividade mobile e acessibilidade (alvos táteis >= 44px e prefers-reduced-motion)', () => {
    // Alvos táteis e layout em max-width 640px
    assert.match(content, /@media\s*\(max-width:\s*640px\)/, 'Deve conter regras específicas para mobile <= 640px')
    assert.match(
      content,
      /\.chapters-mobile-select\s*\{[^}]*min-height:\s*44px;/s,
      'Seletor mobile de capítulos deve ter altura mínima de 44px'
    )
    assert.match(
      content,
      /\.inspector-metrics-grid\s*\{[^}]*grid-template-columns:\s*1fr\s+1fr;/s,
      'Inspetor mobile deve reorganizar indicadores em grade de 2 colunas'
    )

    // Redução de movimento
    assert.match(content, /@media\s*\(prefers-reduced-motion:\s*reduce\)/, 'Deve suportar prefers-reduced-motion')
  })

  it('US6: Conformidade Constitucional estrita: ZERO EMOJIS no código-fonte', () => {
    const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
    assert.doesNotMatch(content, emojiRegex, 'BookView.vue não deve conter nenhum caractere de emoji')
  })
})
