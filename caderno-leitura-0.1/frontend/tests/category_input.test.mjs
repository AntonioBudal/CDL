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
