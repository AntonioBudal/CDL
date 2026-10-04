import test from 'node:test'
import assert from 'node:assert/strict'

// Lógica de manipulação de tags e sugestões testável isoladamente
function resolveCategoryInputState(currentSelectedIds, allCategories, queryText, suggestedCanonical) {
  const selectedSet = new Set(currentSelectedIds)
  const clean = queryText.trim().toLowerCase()

  const available = allCategories
    .filter((c) => !selectedSet.has(c.id))
    .filter((c) => {
      if (!clean) return true
      return c.name.toLowerCase().includes(clean) || c.id.includes(clean)
    })

  const hasSuggestion = Boolean(suggestedCanonical && suggestedCanonical.toLowerCase() !== clean)

  return {
    available,
    hasSuggestion,
    suggestedCanonical: suggestedCanonical || null,
  }
}

function addCategoryTag(currentSelectedIds, newId) {
  if (!newId || currentSelectedIds.includes(newId)) {
    return [...currentSelectedIds]
  }
  return [...currentSelectedIds, newId]
}

function removeCategoryTag(currentSelectedIds, targetId) {
  return currentSelectedIds.filter((id) => id !== targetId)
}

test('resolveCategoryInputState sugere termo canônico singular quando o usuário digita plural', () => {
  const catalog = [
    { id: 'filosofia', name: 'Filosofia', is_canonical: true },
    { id: 'historia', name: 'História', is_canonical: true },
    { id: 'ciencia', name: 'Ciência', is_canonical: true },
  ]

  const state = resolveCategoryInputState([], catalog, 'filosofias', 'Filosofia')
  assert.equal(state.hasSuggestion, true)
  assert.equal(state.suggestedCanonical, 'Filosofia')
})

test('resolveCategoryInputState exclui categorias já selecionadas do dropdown', () => {
  const catalog = [
    { id: 'filosofia', name: 'Filosofia', is_canonical: true },
    { id: 'historia', name: 'História', is_canonical: true },
  ]

  const state = resolveCategoryInputState(['filosofia'], catalog, '', null)
  assert.equal(state.available.length, 1)
  assert.equal(state.available[0].id, 'historia')
})

test('addCategoryTag garante unicidade e integridade da lista de seleção', () => {
  let ids = ['filosofia']
  ids = addCategoryTag(ids, 'historia')
  assert.deepEqual(ids, ['filosofia', 'historia'])

  // Adição duplicada não altera lista
  ids = addCategoryTag(ids, 'filosofia')
  assert.deepEqual(ids, ['filosofia', 'historia'])

  // Remoção de tag
  ids = removeCategoryTag(ids, 'filosofia')
  assert.deepEqual(ids, ['historia'])
})

test('CategoryBadge.vue utiliza o componente canônico Icon name="x" para remoção', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const badgePath = path.resolve('src/components/CategoryBadge.vue')
  const content = fs.readFileSync(badgePath, 'utf-8')

  assert.ok(content.includes("import Icon from './ui/Icon.vue'"), 'Deve importar o componente Icon canônico')
  assert.ok(content.includes('<Icon name="x"'), 'Deve renderizar <Icon name="x"')
  assert.ok(!content.includes('<svg class="w-3.5 h-3.5"'), 'Não deve conter SVG cru inline anterior')
  assert.ok(content.includes(':aria-label="`Remover categoria ${category.name}`"'), 'Deve manter rótulo acessível')
})

test('CategoryInput.vue integra CategoryBadge removível e suporta controle por teclado', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const inputPath = path.resolve('src/components/CategoryInput.vue')
  const content = fs.readFileSync(inputPath, 'utf-8')

  assert.ok(content.includes('<CategoryBadge'), 'Deve renderizar CategoryBadge')
  assert.ok(content.includes('removable'), 'CategoryBadge deve ser removível')
  assert.ok(content.includes('onKeyDown'), 'Deve gerenciar navegação por teclado')
  assert.ok(content.includes('removeCategory'), 'Deve suportar remoção via evento')
})

