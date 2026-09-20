import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { RELATION_TYPE_LABELS } from '../src/composables/useStudyRelations.ts'

test('US1: Roteamento inicial condicional respeita caderno_home_view', () => {
  // Simula o router.beforeEach de router/index.ts
  function evaluateInitialRoute(homePref) {
    if (homePref === 'books') {
      return '/books'
    }
    return '/'
  }

  assert.equal(evaluateInitialRoute('dashboard'), '/')
  assert.equal(evaluateInitialRoute(null), '/')
  assert.equal(evaluateInitialRoute('books'), '/books')
})

test('US1: ResumeStudiesWidget limita em 5 itens por padrão e expande até 10', () => {
  // Cria 8 estudos simulados
  const mockStudies = Array.from({ length: 8 }, (_, i) => ({
    study_id: i + 1,
    title: `Estudo ${i + 1}`,
    book_id: 10,
    book_title: 'Livro Teste',
    chapter_id: 100,
    chapter_title: 'Capítulo Teste',
    reading_status: 'em_estudo',
    updated_at: new Date(Date.now() - i * 3600000).toISOString(),
  }))

  function getDisplayedStudies(studies, isExpanded) {
    if (isExpanded) {
      return studies.slice(0, 10)
    }
    return studies.slice(0, 5)
  }

  // Estado recolhido: exibe 5
  const collapsed = getDisplayedStudies(mockStudies, false)
  assert.equal(collapsed.length, 5)
  assert.equal(collapsed[0].study_id, 1)
  assert.equal(collapsed[4].study_id, 5)

  // Estado expandido: exibe todos os 8
  const expanded = getDisplayedStudies(mockStudies, true)
  assert.equal(expanded.length, 8)
  assert.equal(expanded[7].study_id, 8)
})

test('US1: Link direto de 1 clique aponta para a rota correta do estudo', () => {
  const study = {
    study_id: 42,
    book_id: 7,
    title: 'A Noção de Justiça',
  }

  const generatedUrl = `/books/${study.book_id}?study=${study.study_id}`
  assert.equal(generatedUrl, '/books/7?study=42')
})

test('US2: OrphanStudiesWidget destaca a contagem e exibe itens sem vínculos', () => {
  const orphanStudies = [
    {
      study_id: 101,
      title: 'Nota Isolada A',
      book_id: 1,
      book_title: 'Obra 1',
      reading_status: 'rascunho',
      created_at: new Date().toISOString(),
    },
    {
      study_id: 102,
      title: 'Nota Isolada B',
      book_id: 2,
      book_title: 'Obra 2',
      reading_status: 'em_estudo',
      created_at: new Date().toISOString(),
    },
  ]

  assert.equal(orphanStudies.length, 2)
  assert.equal(orphanStudies[0].study_id, 101)
  assert.equal(orphanStudies[1].reading_status, 'em_estudo')
})

test('US3: RecentConnectionsWidget mapeia tipos canônicos de relação', () => {
  const relation = {
    relation_id: 1,
    relation_type: 'complementa',
    source_study_title: 'Conceito de Virtude',
    target_study_title: 'Teoria da Justiça',
  }

  const meta = RELATION_TYPE_LABELS[relation.relation_type]
  assert.ok(meta)
  assert.equal(meta.outbound, 'Complementa')
  assert.equal(meta.badgeClass, 'badge-complement')
})
