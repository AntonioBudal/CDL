import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

test('FloatingActionsToolbar.vue oculta legendas e adota ícones de 44x44px no mobile (US2)', () => {
  const filePath = path.resolve('src/components/FloatingActionsToolbar.vue')
  const content = fs.readFileSync(filePath, 'utf-8')

  // Envolve legendas em tags identificáveis
  assert.ok(content.includes('<span class="btn-text">Destacar</span>'), 'Destacar deve possuir classe btn-text')
  assert.ok(content.includes('<span class="btn-text">Anotar</span>'), 'Anotar deve possuir classe btn-text')
  assert.ok(content.includes('<span class="btn-text">Citação</span>'), 'Citação deve possuir classe btn-text')
  assert.ok(content.includes('<span class="btn-text">Ocultar</span>'), 'Ocultar deve possuir classe btn-text')
  assert.ok(content.includes('<span class="btn-text">Pergunta</span>'), 'Pergunta deve possuir classe btn-text')

  // Regra CSS que oculta o texto no mobile
  assert.ok(content.includes('.is-mobile .toolbar-btn .btn-text'), 'Deve conter seletor para ocultar texto no mobile')
  assert.ok(content.includes('display: none;'), 'Deve ocultar com display: none')

  // Dimensões táteis mínimas de 44x44px
  assert.ok(content.includes('min-height: 44px;'), 'Deve garantir min-height de 44px')
  assert.ok(content.includes('min-width: 44px;'), 'Deve garantir min-width de 44px')

  // Ícones SVG no mobile
  assert.ok(content.includes('.is-mobile .icon-svg'), 'Deve estilizar icon-svg no mobile')

  // Emissão do evento tool-selected
  assert.ok(content.includes("emit('tool-selected'"), 'Toolbar deve emitir tool-selected para feedback')
})

test('FloatingActionsToolbar.vue amplia a paleta de cores no mobile para alvos confortáveis (FR-010)', () => {
  const filePath = path.resolve('src/components/FloatingActionsToolbar.vue')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(content.includes('.is-mobile .color-choice-btn'), 'Deve estilizar botões de escolha de cor no mobile')
  assert.ok(content.includes('width: 36px;'), 'Círculo de cor deve ter 36px no mobile')
  assert.ok(content.includes('height: 36px;'), 'Círculo de cor deve ter 36px no mobile')
})

test('FloatingActionsToolbar.vue adapta prompts móveis de anotação e pergunta (US4 / FR-004)', () => {
  const filePath = path.resolve('src/components/FloatingActionsToolbar.vue')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(content.includes('.is-mobile .prompt-container'), 'Deve conter container móvel de prompt')
  assert.ok(content.includes('.is-mobile .prompt-textarea'), 'Deve conter estilização mobile para textarea')
  assert.ok(content.includes('.is-mobile .prompt-input'), 'Deve conter estilização mobile para input')
  assert.ok(content.includes('.is-mobile .prompt-actions'), 'Deve conter ações móveis de prompt')
})

test('StudyView.vue integra o micro-toast flutuante com acessibilidade e posicionamento no topo (US3)', () => {
  const filePath = path.resolve('src/views/StudyView.vue')
  const content = fs.readFileSync(filePath, 'utf-8')

  // Import e inicialização do composable
  assert.ok(content.includes("import { useFloatingToast } from '../composables/useFloatingToast'"), 'Deve importar useFloatingToast')
  assert.ok(content.includes('const floatingToast = useFloatingToast()'), 'Deve inicializar floatingToast')

  // Template com semântica WAI-ARIA
  assert.ok(content.includes('class="study-micro-toast"'), 'Deve conter div com classe study-micro-toast')
  assert.ok(content.includes('role="status"'), 'Deve possuir role="status" para leitores de tela')
  assert.ok(content.includes('aria-live="polite"'), 'Deve possuir aria-live="polite"')
  assert.ok(content.includes('micro-toast-color-dot'), 'Deve renderizar indicador de cor quando aplicável')

  // Conexão do evento @tool-selected na toolbar
  assert.ok(content.includes('@tool-selected="handleToolSelected"'), 'Toolbar deve conectar @tool-selected')

  // Posicionamento no topo e pointer-events: none
  assert.ok(content.includes('top: 1rem;'), 'Micro-toast deve ser ancorado em top: 1rem')
  assert.ok(content.includes('pointer-events: none;'), 'Micro-toast deve conter pointer-events: none')

  // Transição suave e suporte a prefers-reduced-motion
  assert.ok(content.includes('floating-toast-fade'), 'Deve conter transição floating-toast-fade')
  assert.ok(content.includes('prefers-reduced-motion: reduce'), 'Deve respeitar prefers-reduced-motion')
})
