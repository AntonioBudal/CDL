import test from 'node:test'
import assert from 'node:assert/strict'
import { useFloatingToast } from '../src/composables/useFloatingToast.ts'

test('useFloatingToast inicializa em estado inativo e vazio', () => {
  const { visible, message, colorDot } = useFloatingToast()

  assert.equal(visible.value, false)
  assert.equal(message.value, '')
  assert.equal(colorDot.value, null)
})

test('showToast ativa visibilidade e propaga mensagem e cor', () => {
  const { visible, message, colorDot, showToast } = useFloatingToast()

  showToast({
    message: 'Destaque aplicado',
    colorDot: '#fef08a',
  })

  assert.equal(visible.value, true)
  assert.equal(message.value, 'Destaque aplicado')
  assert.equal(colorDot.value, '#fef08a')
})

test('showToast desaparece automaticamente após a duração configurada', async () => {
  const { visible, showToast } = useFloatingToast(50) // 50ms para teste ágil

  showToast({ message: 'Trecho ocultado para revisão' })
  assert.equal(visible.value, true)

  await new Promise((resolve) => setTimeout(resolve, 80))

  assert.equal(visible.value, false)
})

test('substituição atômica: novo showToast cancela timer anterior e atualiza dados', async () => {
  const { visible, message, showToast } = useFloatingToast(250)

  showToast({ message: 'Primeira ação' })
  assert.equal(message.value, 'Primeira ação')

  // Após 60ms, dispara segunda ação com duração de 250ms
  await new Promise((resolve) => setTimeout(resolve, 60))
  showToast({ message: 'Segunda ação' })
  assert.equal(message.value, 'Segunda ação')
  assert.equal(visible.value, true)

  // Aos 100ms após a segunda ação, a segunda continua ativa
  await new Promise((resolve) => setTimeout(resolve, 100))
  assert.equal(visible.value, true)
  assert.equal(message.value, 'Segunda ação')

  // Aos 220ms após (total > 250ms da segunda ação), deve ter expirado
  await new Promise((resolve) => setTimeout(resolve, 220))
  assert.equal(visible.value, false)
})

test('hideToast encerra o micro-toast imediatamente', () => {
  const { visible, showToast, hideToast } = useFloatingToast(2000)

  showToast({ message: 'Anotação salva' })
  assert.equal(visible.value, true)

  hideToast()
  assert.equal(visible.value, false)
})
