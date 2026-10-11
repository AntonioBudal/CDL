import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')

test('US2: ReviewCard implementa listeners globais com atalhos de teclado (Espaço e 1-4) e proteção defensiva', () => {
  const cardPath = path.resolve(srcDir, 'components/review/ReviewCard.vue')
  assert.ok(fs.existsSync(cardPath), 'ReviewCard.vue deve existir')

  const content = fs.readFileSync(cardPath, 'utf-8')

  // Listeners de teclado
  assert.ok(content.includes('window.addEventListener(\'keydown\', handleKeydown)'), 'Deve registrar listener no window ao montar')
  assert.ok(content.includes('window.removeEventListener(\'keydown\', handleKeydown)'), 'Deve desregistrar listener ao desmontar')

  // Proteção defensiva de foco
  assert.ok(content.includes("tag === 'input' || tag === 'textarea' || tag === 'select'"), 'Deve ignorar atalhos quando o usuário focar em inputs')

  // Atalhos de reveal e classificação
  assert.ok(content.includes("event.code === 'Space' || event.key === ' '"), 'Deve reconhecer tecla Espaço')
  assert.ok(content.includes("emit('reveal')"), 'Espaço deve emitir evento reveal')
  assert.ok(content.includes("event.key === '1'"), 'Deve reconhecer tecla 1 para Difícil')
  assert.ok(content.includes("emit('rate', 'hard')"), 'Tecla 1 deve emitir hard')
  assert.ok(content.includes("event.key === '2'"), 'Deve reconhecer tecla 2 para Médio')
  assert.ok(content.includes("emit('rate', 'medium')"), 'Tecla 2 deve emitir medium')
  assert.ok(content.includes("event.key === '3'"), 'Deve reconhecer tecla 3 para Fácil')
  assert.ok(content.includes("event.key === '4'"), 'Deve reconhecer tecla 4 para Fácil')
  assert.ok(content.includes("emit('rate', 'easy')"), 'Tecla 3/4 deve emitir easy')

  // Atributos de acessibilidade
  assert.ok(content.includes('role="region"'), 'Card deve ser uma região semântica')
  assert.ok(content.includes('aria-live="polite"'), 'Deve conter anúncio em tempo real para leitor de tela')
  assert.ok(content.includes('kbd-shortcut'), 'Deve exibir etiquetas visuais kbd de atalhos')

  // Estilo mobile tátil (mínimo 44px ou 48px)
  assert.ok(content.includes('min-height: 48px') || content.includes('min-height: 44px') || content.includes('min-h-[44px]'), 'Deve garantir ergonomia tátil')

  // Banimento de emojis
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'ReviewCard.vue não deve conter emojis')
})

test('US4: ReviewSummaryModal exibe balanço de sessão sereno com tempo decorrido e design semântico', () => {
  const modalPath = path.resolve(srcDir, 'components/review/ReviewSummaryModal.vue')
  assert.ok(fs.existsSync(modalPath), 'ReviewSummaryModal.vue deve existir')

  const content = fs.readFileSync(modalPath, 'utf-8')

  // Métricas do resumo
  assert.ok(content.includes('elapsedSeconds'), 'Deve aceitar prop elapsedSeconds')
  assert.ok(content.includes('formattedTime'), 'Deve computar tempo de foco formatado')
  assert.ok(content.includes('summary.total'), 'Deve apresentar total de cartões revisados')
  assert.ok(content.includes('hardPercent'), 'Deve computar percentual difícil')
  assert.ok(content.includes('mediumPercent'), 'Deve computar percentual médio')
  assert.ok(content.includes('easyPercent'), 'Deve computar percentual fácil')

  // Ações de encerramento
  assert.ok(content.includes("emit('finish')"), 'Deve emitir evento finish para encerramento sereno')

  // Imunidade cromática
  assert.ok(!content.includes('#16a34a'), 'Não deve conter verde rígido #16a34a')
  assert.ok(!content.includes('#2563eb'), 'Não deve conter azul rígido #2563eb')

  // Banimento de emojis
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'ReviewSummaryModal.vue não deve conter emojis')
})

test('Lógica de Estimativa de Tempo de Prontidão Intelectual', () => {
  // Simulação do algoritmo: 0.6 minutos (~36s) por cartão com mínimo de 1 minuto para fila não-vazia
  function calculateEstimatedMinutes(pendingCount) {
    if (pendingCount <= 0) return 0
    return Math.max(1, Math.ceil(pendingCount * 0.6))
  }

  assert.equal(calculateEstimatedMinutes(0), 0, 'Zero cartões deve resultar em 0 minutos')
  assert.equal(calculateEstimatedMinutes(1), 1, '1 cartão deve estimar 1 minuto')
  assert.equal(calculateEstimatedMinutes(5), 3, '5 cartões devem estimar 3 minutos')
  assert.equal(calculateEstimatedMinutes(10), 6, '10 cartões devem estimar 6 minutos')
  assert.equal(calculateEstimatedMinutes(20), 12, '20 cartões devem estimar 12 minutos')
})
