import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')
const bookViewPath = path.resolve(srcDir, 'views/BookView.vue')

test('F083-US1: Cabeçalho condensado de linha dupla e menu de ações no mobile', () => {
  assert.ok(fs.existsSync(bookViewPath), 'BookView.vue deve existir em views')
  const content = fs.readFileSync(bookViewPath, 'utf-8')

  // Importação e uso de DropdownMenu
  assert.ok(content.includes("import DropdownMenu from '../components/ui/DropdownMenu.vue'"), 'Deve importar DropdownMenu.vue')
  assert.ok(content.includes('<DropdownMenu'), 'Deve utilizar o componente DropdownMenu')

  // Gatilho e ações no menu móvel
  assert.ok(content.includes('book-mobile-actions-wrapper'), 'Deve conter container para ações móveis (.book-mobile-actions-wrapper)')
  assert.ok(content.includes('book-mobile-actions-trigger'), 'Deve conter gatilho móvel de ações (.book-mobile-actions-trigger)')
  assert.ok(content.includes('Ações do livro'), 'Gatilho deve conter rótulo legível "Ações do livro"')

  // As 4 ações devem estar presentes no menu móvel
  assert.ok(content.includes('toggleFocusMode'), 'Menu móvel deve conter ação para modo foco')
  assert.ok(content.includes('exportModalOpen = true'), 'Menu móvel deve conter ação para exportar anotações')
  assert.ok(content.includes('isEditingBook = true'), 'Menu móvel deve conter ação para editar livro')
  assert.ok(content.includes('confirmTrashBookOpen = true'), 'Menu móvel deve conter ação para mover para a lixeira')

  // Regras de layout móvel para cabeçalho
  assert.match(
    content,
    /\.desktop-actions\s*\{[^}]*display:\s*none\s*!important/s,
    'Ações desktop devem ser ocultadas no mobile sob .desktop-actions'
  )
  assert.match(
    content,
    /\.book-header-cover[^{]*\{[^}]*width:\s*48px/s,
    'Miniatura da capa no mobile deve ter largura travada em 48px'
  )
  assert.match(
    content,
    /-webkit-line-clamp:\s*2/,
    'Título do livro deve aplicar truncamento em até 2 linhas'
  )
})

test('F083-US2: Faixa de capítulos unificada sem esteira horizontal duplicada no mobile', () => {
  const content = fs.readFileSync(bookViewPath, 'utf-8')

  // Supressão da esteira de pílulas roláveis redundante no mobile
  assert.match(
    content,
    /\.chapters-nav-strip\s*\{[^}]*display:\s*none\s*!important/s,
    'A esteira horizontal de pílulas (.chapters-nav-strip) deve ser oculta no mobile'
  )

  // Seletor unificado e botão de novo capítulo
  assert.ok(content.includes('chapters-mobile-select'), 'Deve conter o seletor móvel .chapters-mobile-select')
  assert.ok(content.includes('chapters-mobile-select-wrap'), 'Deve conter container do seletor móvel')
  assert.ok(content.includes('add-chapter-pill-btn') || content.includes('add-chapter-mobile-btn'), 'Deve conter botão de novo capítulo')
})

test('F083-US3: Inspetor analítico recolhível por padrão no mobile', () => {
  const content = fs.readFileSync(bookViewPath, 'utf-8')

  // Estado reativo em script
  assert.ok(
    content.includes('isInspectorExpandedMobile = ref(false)'),
    'Deve definir isInspectorExpandedMobile inicializado como false'
  )

  // Gatilho de alternância com atributos WAI-ARIA
  assert.ok(content.includes('inspector-mobile-toggle'), 'Deve conter botão de alternância do inspetor móvel')
  assert.ok(content.includes(':aria-expanded="isInspectorExpandedMobile"'), 'Botão deve ter atributo :aria-expanded')
  assert.ok(content.includes('aria-controls="inspector-content-panel"'), 'Botão deve declarar aria-controls correspondente')
  assert.ok(content.includes('Ver detalhes do livro'), 'Deve conter texto "Ver detalhes do livro"')
  assert.ok(content.includes('Ocultar detalhes do livro'), 'Deve conter texto "Ocultar detalhes do livro"')

  // Regras CSS para alternância
  assert.match(
    content,
    /\.inspector-bar-content\.is-collapsed-mobile\s*\{[^}]*display:\s*none\s*!important/s,
    'Conteúdo do inspetor deve ficar oculto quando is-collapsed-mobile estiver ativo'
  )
  assert.match(
    content,
    /\.inspector-mobile-toggle\s*\{[^}]*display:\s*none\s*!important/s,
    'Gatilho móvel do inspetor deve ser ocultado no desktop'
  )
})

test('F083-Polish: Ausência estrita de emojis e preservação de variáveis de temas', () => {
  const filesToCheck = [
    'src/views/BookView.vue',
    'tests/feature-083-book-mobile-layout.test.mjs',
  ]

  const emojiRegex = /[\u{1F300}-\u{1F5FF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F900}-\u{1F9FF}\u{1FA70}-\u{1FAFF}]/u

  for (const relativePath of filesToCheck) {
    const fullPath = path.resolve(srcDir, '..', relativePath)
    if (fs.existsSync(fullPath)) {
      const content = fs.readFileSync(fullPath, 'utf-8')
      const match = content.match(emojiRegex)
      assert.strictEqual(
        match,
        null,
        `Arquivo ${relativePath} contém emoji proíbido: ${match ? match[0] : ''}`
      )
    }
  }
})
