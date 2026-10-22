import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')
const studyViewPath = path.resolve(srcDir, 'views/StudyView.vue')
const studyEditViewPath = path.resolve(srcDir, 'views/StudyEditView.vue')
const activeReadingBarPath = path.resolve(srcDir, 'components/ActiveReadingBar.vue')
const studyTabsPath = path.resolve(srcDir, 'components/StudyTabs.vue')

test('F084-US1: Menu contextual de ações secundárias e proteção de exclusão no leitor', () => {
  assert.ok(fs.existsSync(studyViewPath), 'StudyView.vue deve existir em views')
  const content = fs.readFileSync(studyViewPath, 'utf-8')

  // Importação e uso de DropdownMenu
  assert.ok(
    content.includes("import DropdownMenu from '../components/ui/DropdownMenu.vue'"),
    'StudyView deve importar DropdownMenu.vue'
  )
  assert.ok(content.includes('<DropdownMenu'), 'StudyView deve utilizar o componente DropdownMenu')

  // Ação primária isolada: Editar estudo
  assert.ok(
    content.includes('class="button primary edit-action') || content.includes("class=\"button primary edit-action"),
    'Botão de edição deve permanecer primário no cabeçalho'
  )

  // Ação de lixeira protegida dentro do menu suspenso
  assert.ok(
    content.includes('danger-action'),
    'Ação de exclusão deve possuir classe danger-action no menu suspenso'
  )
  assert.ok(
    content.includes('confirmTrashOpen = true'),
    'Ação de exclusão deve abrir o modal de confirmação'
  )

  // Verificação de que a lixeira reside protegida dentro do DropdownMenu
  const dropdownIdx = content.indexOf('<DropdownMenu')
  const trashIdx = content.indexOf('confirmTrashOpen = true')
  assert.ok(dropdownIdx !== -1 && trashIdx > dropdownIdx, 'Ação de lixeira deve residir dentro do DropdownMenu')

  // Itens do menu contextual
  assert.ok(content.includes('shareModalOpen = true'), 'Menu deve conter ação para compartilhar')
  assert.ok(content.includes('exportModalOpen = true'), 'Menu deve conter ação para exportar')
  assert.ok(content.includes('historyModalOpen = true'), 'Menu deve conter ação para histórico de versões')
  assert.ok(content.includes('dropdown-divider'), 'Menu deve conter separador antes da ação de lixeira')

  // Alvos táteis e acessibilidade
  assert.ok(content.includes('study-more-trigger'), 'Gatilho do menu deve possuir classe identificadora')
  assert.ok(content.includes('Mais opções do estudo'), 'Gatilho deve possuir rótulo descritivo acessível')
})

test('F084-US2: Indicador visual de persistência e rascunho em tempo real no editor', () => {
  assert.ok(fs.existsSync(studyEditViewPath), 'StudyEditView.vue deve existir em views')
  const content = fs.readFileSync(studyEditViewPath, 'utf-8')

  // Pílula de status no template
  assert.ok(content.includes('draft-status-pill'), 'Deve conter elemento .draft-status-pill')
  assert.ok(content.includes('role="status"'), 'Pílula de status deve declarar role="status"')
  assert.ok(content.includes('aria-live="polite"'), 'Pílula de status deve declarar aria-live="polite"')

  // Estados reativos computados
  assert.ok(content.includes('draftStatusLabel'), 'Deve computar draftStatusLabel')
  assert.ok(content.includes('Salvando…') || content.includes('Salvando...'), 'Deve conter estado textual Salvando')
  assert.ok(content.includes('Rascunho salvo neste navegador'), 'Deve conter estado textual de rascunho local')
  assert.ok(content.includes('Alterações salvas'), 'Deve conter estado textual de alterações salvas')

  // Classes de estilização dos estados
  assert.ok(content.includes('draftStatusClass'), 'Deve computar classes de variação da pílula')
})

test('F084-US3: Alvos de toque ergonômicos (>= 44x44px) na barra de leitura e abas', () => {
  assert.ok(fs.existsSync(activeReadingBarPath), 'ActiveReadingBar.vue deve existir')
  const barContent = fs.readFileSync(activeReadingBarPath, 'utf-8')

  // Botões da barra de leitura com no mínimo 44px
  assert.match(
    barContent,
    /\.reading-bar-btn[^{]*\{[^}]*min-height:\s*44px/s,
    'Botões da barra de leitura devem ter min-height de 44px no mobile'
  )
  assert.match(
    barContent,
    /\.close-btn[^{]*\{[^}]*min-height:\s*44px/s,
    'Botão close-btn deve possuir min-height de 44px no mobile ou ponteiro tátil'
  )

  // Abas de estudo com no mínimo 44px
  assert.ok(fs.existsSync(studyTabsPath), 'StudyTabs.vue deve existir')
  const styleCssPath = path.resolve(srcDir, 'style.css')
  const styleCss = fs.readFileSync(styleCssPath, 'utf-8')
  assert.match(
    styleCss,
    /\.study-tabs\s+\[role=['"]tab['"]\][^{]*\{[^}]*min-height:\s*(3rem|44px|48px)/s,
    'Abas de estudo em style.css devem garantir altura mínima de pelo menos 44px'
  )
})

test('F084-Polish: Ausência estrita de emojis e conformidade temática', () => {
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u

  for (const filePath of [studyViewPath, studyEditViewPath, activeReadingBarPath, studyTabsPath]) {
    const fileContent = fs.readFileSync(filePath, 'utf-8')
    assert.strictEqual(
      emojiRegex.test(fileContent),
      false,
      `O arquivo ${path.basename(filePath)} não deve conter emojis`
    )
  }
})
