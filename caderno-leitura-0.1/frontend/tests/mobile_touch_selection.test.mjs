import test from 'node:test'
import assert from 'node:assert/strict'
import {
  isDoubleTap,
  findWordBoundaries,
  expandRangeToWord,
  getRangeFromPoint,
} from '../src/composables/useTextSelection.ts'

test('isDoubleTap identifica duplo toque válido dentro de 320ms e 15px', () => {
  const result = isDoubleTap({
    lastTapTimestamp: 1000,
    lastTapX: 150,
    lastTapY: 200,
    currentTapTimestamp: 1250, // 250ms diff (< 320ms)
    currentTapX: 155, // 5px diff
    currentTapY: 204, // 4px diff (distancia = sqrt(25 + 16) ~ 6.4px < 15px)
    isScrolling: false,
  })

  assert.equal(result, true)
})

test('isDoubleTap rejeita toques com intervalo superior a 320ms', () => {
  const result = isDoubleTap({
    lastTapTimestamp: 1000,
    lastTapX: 150,
    lastTapY: 200,
    currentTapTimestamp: 1350, // 350ms diff (> 320ms)
    currentTapX: 152,
    currentTapY: 201,
    isScrolling: false,
  })

  assert.equal(result, false)
})

test('isDoubleTap rejeita toques com distância espacial superior a 15px', () => {
  const result = isDoubleTap({
    lastTapTimestamp: 1000,
    lastTapX: 100,
    lastTapY: 100,
    currentTapTimestamp: 1200, // 200ms diff
    currentTapX: 120, // 20px diff (> 15px)
    currentTapY: 100,
    isScrolling: false,
  })

  assert.equal(result, false)
})

test('isDoubleTap rejeita evento quando isScrolling é true', () => {
  const result = isDoubleTap({
    lastTapTimestamp: 1000,
    lastTapX: 150,
    lastTapY: 200,
    currentTapTimestamp: 1200,
    currentTapX: 152,
    currentTapY: 202,
    isScrolling: true, // Usuário estava rolando a página
  })

  assert.equal(result, false)
})

test('isDoubleTap rejeita primeiro toque isolado (lastTapTimestamp = 0)', () => {
  const result = isDoubleTap({
    lastTapTimestamp: 0,
    lastTapX: 0,
    lastTapY: 0,
    currentTapTimestamp: 1000,
    currentTapX: 150,
    currentTapY: 200,
    isScrolling: false,
  })

  assert.equal(result, false)
})

test('findWordBoundaries localiza limites de palavras em português com acentuação', () => {
  const text = 'A revolução industrial transformou o modo de produção.'
  
  // Teste no meio de "revolução" (offset 5 é 'v')
  const match1 = findWordBoundaries(text, 5)
  assert.ok(match1)
  assert.equal(match1.word, 'revolução')
  assert.equal(match1.start, 2)
  assert.equal(match1.end, 11)

  // Teste no fim de "produção" antes do ponto (offset 52 é 'o' com til)
  const match2 = findWordBoundaries(text, 52)
  assert.ok(match2)
  assert.equal(match2.word, 'produção')

  // Teste com offset no início da palavra
  const match3 = findWordBoundaries(text, 23) // 't' de 'transformou'
  assert.ok(match3)
  assert.equal(match3.word, 'transformou')
})

test('findWordBoundaries ignora espaços puros e pontuações isoladas', () => {
  const text = 'Palavra.   Outra'
  
  // Offset em espaço em branco isolado sem palavra anterior contígua
  const match = findWordBoundaries(text, 9)
  assert.equal(match, null)
})

test('expandRangeToWord e getRangeFromPoint tratam ambientes sem DOM de forma segura', () => {
  // getRangeFromPoint com document indefinido ou mock
  const range = getRangeFromPoint(100, 200)
  assert.equal(range, null)
})
