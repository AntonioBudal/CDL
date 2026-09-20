import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

// =============================================================================
// User Story 4: Ergonomia Móvel, Busca Rápida e Acessibilidade (T022 - T025)
// =============================================================================

test('CreateRelationModal.vue implementa acessibilidade WAI-ARIA rigorosa', () => {
  const modalPath = path.resolve('src/components/relations/CreateRelationModal.vue')
  const content = fs.readFileSync(modalPath, 'utf-8')

  // Diálogo modal
  assert.ok(content.includes('role="dialog"'), 'Deve possuir role="dialog"')
  assert.ok(content.includes('aria-modal="true"'), 'Deve possuir aria-modal="true"')
  assert.ok(content.includes('aria-labelledby="modal-title"'), 'Deve associar o título via aria-labelledby')

  // Lista de candidatos
  assert.ok(content.includes('role="listbox"'), 'Lista de candidatos deve ter role="listbox"')
  assert.ok(content.includes('role="option"'), 'Opções candidatas devem ter role="option"')
  assert.ok(content.includes(':aria-selected='), 'Opções candidatas devem indicar seleção via aria-selected')

  // Seletor de tipos conceituais
  assert.ok(content.includes('role="radiogroup"'), 'Seletor de tipo deve ter role="radiogroup"')
  assert.ok(content.includes('role="radio"'), 'Opções de tipo devem ter role="radio"')
  assert.ok(content.includes(':aria-checked='), 'Opções de tipo devem indicar estado ativo via aria-checked')

  // Controle por teclado
  assert.ok(content.includes("event.key === 'Escape'"), 'Deve fechar com tecla Escape')
  assert.ok(content.includes('@keydown="handleKeyDown"'), 'Deve capturar eventos de teclado')
  assert.ok(content.includes('searchInputRef.value?.focus()'), 'Deve aplicar foco automático no campo de busca ao abrir')
})

test('CreateRelationModal.vue cumpre requisitos de ergonomia móvel e alvos de toque de 44px', () => {
  const modalPath = path.resolve('src/components/relations/CreateRelationModal.vue')
  const content = fs.readFileSync(modalPath, 'utf-8')

  // Alvos táteis mínimos
  assert.ok(content.includes('min-height: 44px'), 'Input de busca, opções e botões devem ter min-height de 44px')
  assert.ok(content.includes('min-height: 48px'), 'Linhas de candidatos devem ter altura confortável de toque (>= 44px)')
  assert.ok(content.includes('width: 44px;'), 'Botão de fechar deve ter 44px de largura mínima')
  assert.ok(content.includes('height: 44px;'), 'Botão de fechar deve ter 44px de altura mínima')

  // Busca incremental com debounce
  assert.ok(content.includes('debounceTimer'), 'Deve gerenciar timer de debounce para busca não-bloqueante')
  assert.ok(content.includes('searchCandidateStudies'), 'Deve invocar busca incremental transversal')
})

test('StudyRelationsList.vue garante alvos de toque mínimos de 44x44px e semântica de tela', () => {
  const listPath = path.resolve('src/components/relations/StudyRelationsList.vue')
  const content = fs.readFileSync(listPath, 'utf-8')

  assert.ok(content.includes('aria-labelledby="relations-heading"'), 'Painel deve ter aria-labelledby')
  assert.ok(content.includes('min-height: 44px'), 'Botões de ação rápida devem ter min-height de 44px')
  assert.ok(content.includes('width: 44px;'), 'Botão de remover e editar devem ter 44px')
  assert.ok(content.includes('height: 44px;'), 'Botão de remover e editar devem ter 44px de altura')
  assert.ok(content.includes('class="edit-relation-btn"'), 'Deve conter botão de edição rápida')
  assert.ok(content.includes('class="remove-relation-btn"'), 'Deve conter botão de remoção')
})

test('StudyView.vue integra StudyRelationsList e CreateRelationModal de forma reativa', () => {
  const viewPath = path.resolve('src/views/StudyView.vue')
  const content = fs.readFileSync(viewPath, 'utf-8')

  assert.ok(content.includes('<StudyRelationsList'), 'StudyView deve conter StudyRelationsList')
  assert.ok(content.includes('<CreateRelationModal'), 'StudyView deve conter CreateRelationModal')
  assert.ok(content.includes('@open-create-modal="createRelationModalOpen = true"'), 'Deve abrir o modal ao solicitar criação')
  assert.ok(content.includes('handleRelationCreated'), 'Deve atualizar a listagem após criação de relação')
})
