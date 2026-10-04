import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const reviewCardPath = path.resolve('src/components/review/ReviewCard.vue')

// ============================================================================
// User Story 2: Sessão Interativa de Active Recall em Tela Limpa (P2)
// ============================================================================

test('US2: ReviewCard.vue existe e possui atributos WAI-ARIA de acessibilidade', () => {
  assert.ok(fs.existsSync(reviewCardPath), 'ReviewCard.vue deve existir')
  const content = fs.readFileSync(reviewCardPath, 'utf-8')

  // Região acessível e anúncio para leitor de tela
  assert.match(content, /role="region"/)
  assert.match(content, /aria-label="Card de revisão atual"|aria-label/)
  assert.match(content, /aria-live="polite"/)
})

test('US2: ReviewCard.vue implementa atalhos de teclado (Espaço, 1, 2, 3)', () => {
  const content = fs.readFileSync(reviewCardPath, 'utf-8')

  // Atalhos de teclado
  assert.match(content, /handleKeydown|keydown/)
  assert.match(content, /Space|' '|code === 'Space'/)
  assert.match(content, /Digit1|'1'/)
  assert.match(content, /Digit2|'2'/)
  assert.match(content, /Digit3|'3'/)
})

test('US2: ReviewCard.vue garante alvos táteis mínimos de 44x44px no mobile', () => {
  const content = fs.readFileSync(reviewCardPath, 'utf-8')

  // Alvos mínimos de toque
  assert.match(content, /min-height:\s*44px|min-h-\[44px\]/)
  assert.match(content, /reveal-btn|btn-reveal/)
  assert.match(content, /rating-btn|rate-btn/)
})

test('US2: ReviewCard.vue renderiza conteúdo cognitivo e resposta revelada in-place', () => {
  const content = fs.readFileSync(reviewCardPath, 'utf-8')

  // Exibição da pergunta, cloze e resposta
  assert.match(content, /expected_answer|expectedAnswer/)
  assert.match(content, /question_text|questionText/)
  assert.match(content, /isRevealed/)
})
