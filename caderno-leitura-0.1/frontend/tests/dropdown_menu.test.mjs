import test from 'node:test'
import assert from 'node:assert/strict'

// Modelagem e máquina de estados isolada de DropdownMenu
function createDropdownController(options = {}) {
  const align = options.align || 'right'
  const disabled = options.disabled || false
  let isOpen = false
  let focusedIndex = -1
  let closeCount = 0
  let openCount = 0

  function open(itemsCount = 0) {
    if (disabled || isOpen) return false
    isOpen = true
    openCount++
    focusedIndex = itemsCount > 0 ? 0 : -1
    return true
  }

  function close() {
    if (!isOpen) return false
    isOpen = false
    closeCount++
    focusedIndex = -1
    return true
  }

  function toggle(itemsCount = 0) {
    if (isOpen) return close()
    return open(itemsCount)
  }

  function handleKeydown(key, itemsCount = 0) {
    if (!isOpen) {
      if (['ArrowDown', 'Enter', ' '].includes(key)) {
        open(itemsCount)
        return { handled: true, isOpen, focusedIndex }
      }
      return { handled: false, isOpen, focusedIndex }
    }

    if (key === 'Escape') {
      close()
      return { handled: true, isOpen, focusedIndex: -1, shouldRestoreTriggerFocus: true }
    }

    if (itemsCount === 0) return { handled: false, isOpen, focusedIndex }

    if (key === 'ArrowDown') {
      focusedIndex = focusedIndex >= 0 && focusedIndex < itemsCount - 1 ? focusedIndex + 1 : 0
      return { handled: true, isOpen, focusedIndex }
    }

    if (key === 'ArrowUp') {
      focusedIndex = focusedIndex > 0 ? focusedIndex - 1 : itemsCount - 1
      return { handled: true, isOpen, focusedIndex }
    }

    if (key === 'Home') {
      focusedIndex = 0
      return { handled: true, isOpen, focusedIndex }
    }

    if (key === 'End') {
      focusedIndex = itemsCount - 1
      return { handled: true, isOpen, focusedIndex }
    }

    if (key === 'Tab') {
      close()
      return { handled: true, isOpen, focusedIndex: -1 }
    }

    return { handled: false, isOpen, focusedIndex }
  }

  function shouldStopPropagation(key) {
    return ['Escape', 'ArrowDown', 'ArrowUp', 'Home', 'End'].includes(key)
  }

  return {
    get isOpen() { return isOpen },
    get focusedIndex() { return focusedIndex },
    get openCount() { return openCount },
    get closeCount() { return closeCount },
    align,
    disabled,
    open,
    close,
    toggle,
    handleKeydown,
    shouldStopPropagation
  }
}

test('DropdownController - Estado inicial fechado e alinhamento', () => {
  const dropdown = createDropdownController({ align: 'right' })
  assert.equal(dropdown.isOpen, false)
  assert.equal(dropdown.align, 'right')
  assert.equal(dropdown.focusedIndex, -1)
})

test('DropdownController - Toggle e abertura/fechamento', () => {
  const dropdown = createDropdownController()
  assert.equal(dropdown.open(3), true)
  assert.equal(dropdown.isOpen, true)
  assert.equal(dropdown.focusedIndex, 0)
  assert.equal(dropdown.openCount, 1)

  // Abrir novamente não duplica evento
  assert.equal(dropdown.open(3), false)
  assert.equal(dropdown.openCount, 1)

  // Fechar
  assert.equal(dropdown.close(), true)
  assert.equal(dropdown.isOpen, false)
  assert.equal(dropdown.closeCount, 1)

  // Toggle abre se fechado e fecha se aberto
  dropdown.toggle(4)
  assert.equal(dropdown.isOpen, true)
  assert.equal(dropdown.focusedIndex, 0)
  dropdown.toggle(4)
  assert.equal(dropdown.isOpen, false)
})

test('DropdownController - Não abre se disabled === true', () => {
  const dropdown = createDropdownController({ disabled: true })
  assert.equal(dropdown.open(3), false)
  assert.equal(dropdown.isOpen, false)
  assert.equal(dropdown.toggle(3), false)
  assert.equal(dropdown.isOpen, false)
})

test('DropdownController - Navegação cíclica por teclado (ArrowDown, ArrowUp, Home, End)', () => {
  const dropdown = createDropdownController()
  dropdown.open(3) // 3 itens: índices 0, 1, 2
  assert.equal(dropdown.focusedIndex, 0)

  // ArrowDown avança
  dropdown.handleKeydown('ArrowDown', 3)
  assert.equal(dropdown.focusedIndex, 1)

  dropdown.handleKeydown('ArrowDown', 3)
  assert.equal(dropdown.focusedIndex, 2)

  // ArrowDown no último item faz wrap-around para o primeiro (0)
  dropdown.handleKeydown('ArrowDown', 3)
  assert.equal(dropdown.focusedIndex, 0)

  // ArrowUp no primeiro item faz wrap-around para o último (2)
  dropdown.handleKeydown('ArrowUp', 3)
  assert.equal(dropdown.focusedIndex, 2)

  // Home vai para 0, End vai para 2
  dropdown.handleKeydown('Home', 3)
  assert.equal(dropdown.focusedIndex, 0)
  dropdown.handleKeydown('End', 3)
  assert.equal(dropdown.focusedIndex, 2)
})

test('DropdownController - Tecla Escape fecha e solicita retorno de foco', () => {
  const dropdown = createDropdownController()
  dropdown.open(3)
  assert.equal(dropdown.isOpen, true)

  const result = dropdown.handleKeydown('Escape', 3)
  assert.equal(result.handled, true)
  assert.equal(result.isOpen, false)
  assert.equal(result.shouldRestoreTriggerFocus, true)
  assert.equal(dropdown.isOpen, false)
})

test('DropdownController - Isolamento contra atalhos de Active Recall (stopPropagation)', () => {
  const dropdown = createDropdownController()
  // Teclas do dropdown devem conter propagação
  assert.equal(dropdown.shouldStopPropagation('Escape'), true)
  assert.equal(dropdown.shouldStopPropagation('ArrowDown'), true)
  assert.equal(dropdown.shouldStopPropagation('ArrowUp'), true)
  // Teclas comuns de digitação não são contidas
  assert.equal(dropdown.shouldStopPropagation('j'), false)
  assert.equal(dropdown.shouldStopPropagation('k'), false)
})
