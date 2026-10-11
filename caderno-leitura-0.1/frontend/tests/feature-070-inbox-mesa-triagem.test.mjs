import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')

test('Setup: Tipos e enums de triagem declarados em types.ts', () => {
  const typesPath = path.resolve(srcDir, 'types.ts')
  assert.ok(fs.existsSync(typesPath), 'types.ts deve existir')
  const content = fs.readFileSync(typesPath, 'utf-8')

  assert.ok(content.includes('export type TriageFilterTab'), 'Deve exportar TriageFilterTab')
  assert.ok(content.includes("'inbox' | 'promoted' | 'linked' | 'archived' | 'all'"), 'TriageFilterTab deve conter os 5 filtros')
  assert.ok(content.includes('export interface TriageKeyboardState'), 'Deve exportar TriageKeyboardState')
})

test('US1: QuickThoughtDrop implementa campo superior permanente com expansão e Ctrl+Enter', () => {
  const compPath = path.resolve(srcDir, 'components/inbox/QuickThoughtDrop.vue')
  assert.ok(fs.existsSync(compPath), 'QuickThoughtDrop.vue deve existir')

  const content = fs.readFileSync(compPath, 'utf-8')

  // Estrutura e expansão
  assert.ok(content.includes('quick-thought-drop'), 'Deve conter container quick-thought-drop')
  assert.ok(content.includes('quick-drop-input'), 'Deve conter textarea com classe quick-drop-input')
  assert.ok(content.includes('is-expanded') || content.includes(':focus-within'), 'Deve suportar classe ou estado expandido')

  // Atalho e botões
  assert.ok(content.includes('Ctrl+Enter') || content.includes('Cmd+Enter'), 'Deve conter indicação de atalho Ctrl+Enter')
  assert.ok(content.includes('quick-drop-submit') || content.includes('button-submit'), 'Deve conter botão de envio')
  assert.ok(content.includes('quick-drop-source') || content.includes('source_hint'), 'Deve conter campo opcional de fonte')

  // Rejeição de vazio e emissão
  assert.ok(content.includes("emit('created'"), 'Deve emitir evento created')
  assert.ok(content.includes('api.createInboxCapture'), 'Deve chamar api.createInboxCapture')

  // Imunidade cromática e banimento de emojis
  assert.ok(!content.includes('#2563eb'), 'Não deve conter hex rígido #2563eb')
  assert.ok(!content.includes('#111827'), 'Não deve conter hex rígido #111827')
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'QuickThoughtDrop.vue não deve conter emojis')
})

test('US2: InboxView implementa Barra Segmentada de Triagem com contadores dinâmicos', () => {
  const viewPath = path.resolve(srcDir, 'views/InboxView.vue')
  assert.ok(fs.existsSync(viewPath), 'InboxView.vue deve existir')

  const content = fs.readFileSync(viewPath, 'utf-8')

  // QuickThoughtDrop integrado no topo
  assert.ok(content.includes('QuickThoughtDrop'), 'InboxView deve importar e integrar QuickThoughtDrop')

  // Barra segmentada e acessibilidade WAI-ARIA
  assert.ok(content.includes('triage-segmented-bar') || content.includes('status-tabs'), 'Deve conter container de triagem segmentada')
  assert.ok(content.includes('role="tablist"'), 'Barra segmentada deve possuir role="tablist"')
  assert.ok(content.includes('aria-selected'), 'Segmentos devem ter atributo acessível aria-selected')

  // Os 5 segmentos
  assert.ok(content.includes("'inbox'"), 'Deve suportar segmento inbox (Pendentes)')
  assert.ok(content.includes("'promoted'"), 'Deve suportar segmento promoted (Promovidos)')
  assert.ok(content.includes("'linked'"), 'Deve suportar segmento linked (Vinculados)')
  assert.ok(content.includes("'archived'"), 'Deve suportar segmento archived (Arquivados)')
  assert.ok(content.includes("'all'"), 'Deve suportar segmento all (Todos)')
})

test('US3: CaptureItemCard implementa ferramentas de triagem direta e transição de saída (.is-exiting)', () => {
  const cardPath = path.resolve(srcDir, 'components/inbox/CaptureItemCard.vue')
  assert.ok(fs.existsSync(cardPath), 'CaptureItemCard.vue deve existir')

  const content = fs.readFileSync(cardPath, 'utf-8')

  // Ferramentas de triagem no cartão
  assert.ok(content.includes("emit('archive'") || content.includes('handleArchive'), 'Deve suportar ação de arquivar')
  assert.ok(content.includes("emit('promote'") || content.includes('handlePromote'), 'Deve suportar ação de promover')
  assert.ok(content.includes("emit('link'") || content.includes('handleLink'), 'Deve suportar ação de vincular')
  assert.ok(content.includes('handleDelete'), 'Deve suportar ação de exclusão defensiva')

  // Transição cinética de saída
  assert.ok(content.includes('is-exiting'), 'Deve suportar classe CSS is-exiting')
  assert.ok(content.includes('translateX(30px)'), 'Deve conter deslocamento lateral na transição')
  assert.ok(content.includes('opacity: 0'), 'Deve conter desvanecimento de opacidade')

  // Imunidade cromática: remoção dos badges com hex rígido legados (#eff6ff, #2563eb, etc.)
  assert.ok(!content.includes('#eff6ff'), 'Não deve conter hex rígido #eff6ff')
  assert.ok(!content.includes('#2563eb'), 'Não deve conter hex rígido #2563eb')
  assert.ok(!content.includes('#ecfdf5'), 'Não deve conter hex rígido #ecfdf5')
  assert.ok(!content.includes('#059669'), 'Não deve conter hex rígido #059669')

  // Zero emojis
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'CaptureItemCard.vue não deve conter emojis')
})

test('US4: Navegação e Triagem por Teclado com atalhos J/K/E e Ctrl+Shift+C', () => {
  const viewPath = path.resolve(srcDir, 'views/InboxView.vue')
  const content = fs.readFileSync(viewPath, 'utf-8')

  // Atalhos J, K e E
  assert.ok(content.includes("'j'") || content.includes("'J'"), 'Deve escutar tecla J para navegar para baixo')
  assert.ok(content.includes("'k'") || content.includes("'K'"), 'Deve escutar tecla K para navegar para cima')
  assert.ok(content.includes("'e'") || content.includes("'E'"), 'Deve escutar tecla E para arquivar')

  // Guarda defensiva contra digitação em inputs/textareas
  assert.ok(
    content.includes('INPUT') ||
    content.includes('TEXTAREA') ||
    content.includes('isContentEditable') ||
    content.includes('tagName'),
    'Deve implementar guarda defensiva contra digitação em campos de texto'
  )

  // Atalho global Ctrl+Shift+C
  assert.ok(content.includes('Ctrl+Shift+C') || content.includes('key === "C"') || content.includes("key === 'C'"), 'Deve suportar atalho global Ctrl+Shift+C')

  // Cartão com anel de foco/seleção por teclado
  const cardPath = path.resolve(srcDir, 'components/inbox/CaptureItemCard.vue')
  const cardContent = fs.readFileSync(cardPath, 'utf-8')
  assert.ok(cardContent.includes('is-keyboard-selected'), 'CaptureItemCard deve suportar classe is-keyboard-selected')
})

test('US5: Estado vazio "Mesa Limpa" e tratamento editorial de erro em InboxView.vue', () => {
  const viewPath = path.resolve(srcDir, 'views/InboxView.vue')
  const content = fs.readFileSync(viewPath, 'utf-8')

  // Estado Mesa Limpa
  assert.ok(content.includes('Mesa Limpa') || content.includes('mesa limpa') || content.includes('mesa-limpa'), 'Deve renderizar estado Mesa Limpa')
  assert.ok(!content.includes('Sua Caixa de Entrada está vazia'), 'Deve substituir mensagem fria anterior por Mesa Limpa')

  // Tratamento editorial de erro
  assert.ok(content.includes('role="alert"'), 'Container de erro deve ter role="alert"')
  assert.ok(content.includes('Tentar novamente') || content.includes('Tentar Novamente'), 'Deve conter botão de tentar novamente')

  // Imunidade cromática e banimento de emojis em InboxView
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'InboxView.vue não deve conter emojis')
  assert.ok(!content.includes('#4f46e5'), 'Não deve conter hex rígido #4f46e5')
  assert.ok(!content.includes('#111827'), 'Não deve conter hex rígido #111827')
})
