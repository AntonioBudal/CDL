import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { STUDY_TEMPLATES, STUDY_TEMPLATE_MAP, getStudyTemplate } from '../src/constants/studyTemplates.ts'
import { useStudyEdit } from '../src/composables/useStudyEdit.ts'
import { useImportDraft } from '../src/composables/useImportDraft.ts'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

const EMOJI_REGEX = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1FA00}-\u{1FAFF}]/u

test('Catálogo STUDY_TEMPLATES contém exatamente os 5 modelos canônicos', () => {
  assert.equal(STUDY_TEMPLATES.length, 5)
  const ids = STUDY_TEMPLATES.map((t) => t.id)
  assert.deepEqual(ids, ['classico', 'conceito', 'argumento', 'comparativo', 'resenha'])
})

test('Todos os templates contêm as 4 seções analíticas completas', () => {
  const expectedKeys = ['summary', 'explanation', 'concepts', 'references']

  for (const tpl of STUDY_TEMPLATES) {
    assert.ok(tpl.id, 'Template deve ter id')
    assert.ok(tpl.name, 'Template deve ter name')
    assert.ok(tpl.badgeLabel, 'Template deve ter badgeLabel')
    assert.ok(tpl.shortDescription, 'Template deve ter shortDescription')
    assert.ok(tpl.detailedPurpose, 'Template deve ter detailedPurpose')

    for (const key of expectedKeys) {
      const section = tpl.sections[key]
      assert.ok(section, `Template ${tpl.id} deve ter seção ${key}`)
      assert.equal(section.key, key)
      assert.ok(section.label && section.label.trim().length > 0, `Seção ${key} deve ter label`)
      assert.ok(section.hint && section.hint.trim().length > 0, `Seção ${key} deve ter hint`)
      assert.ok(section.skeleton && section.skeleton.trim().length > 0, `Seção ${key} deve ter skeleton`)
    }
  }
})

test('getStudyTemplate retorna template correto e aplica fallback gracioso para "classico"', () => {
  const classico = getStudyTemplate('classico')
  assert.equal(classico.id, 'classico')

  const conceito = getStudyTemplate('conceito')
  assert.equal(conceito.id, 'conceito')

  const fallback1 = getStudyTemplate('desconhecido')
  assert.equal(fallback1.id, 'classico')

  const fallback2 = getStudyTemplate(null)
  assert.equal(fallback2.id, 'classico')

  const fallback3 = getStudyTemplate(undefined)
  assert.equal(fallback3.id, 'classico')
})

test('Catálogo de templates tem conformidade visual estrita: ZERO EMOJIS', () => {
  for (const tpl of STUDY_TEMPLATES) {
    assert.ok(!EMOJI_REGEX.test(tpl.name), `Template ${tpl.id} name não pode conter emojis`)
    assert.ok(!EMOJI_REGEX.test(tpl.badgeLabel), `Template ${tpl.id} badgeLabel não pode conter emojis`)
    assert.ok(!EMOJI_REGEX.test(tpl.shortDescription), `Template ${tpl.id} shortDescription não pode conter emojis`)
    assert.ok(!EMOJI_REGEX.test(tpl.detailedPurpose), `Template ${tpl.id} detailedPurpose não pode conter emojis`)

    for (const [key, section] of Object.entries(tpl.sections)) {
      assert.ok(!EMOJI_REGEX.test(section.label), `Seção ${key} label não pode conter emojis`)
      assert.ok(!EMOJI_REGEX.test(section.hint), `Seção ${key} hint não pode conter emojis`)
      assert.ok(!EMOJI_REGEX.test(section.skeleton), `Seção ${key} skeleton não pode conter emojis`)
    }
  }
})

test('Arquivos Vue de template não contêm emojis no código-fonte', () => {
  const modalPath = path.resolve(__dirname, '../src/components/studies/TemplateSelectorModal.vue')
  const fieldsPath = path.resolve(__dirname, '../src/components/StudyEditorFields.vue')

  const modalContent = fs.readFileSync(modalPath, 'utf-8')
  const fieldsContent = fs.readFileSync(fieldsPath, 'utf-8')

  assert.ok(!EMOJI_REGEX.test(modalContent), 'TemplateSelectorModal.vue não deve conter emojis')
  assert.ok(!EMOJI_REGEX.test(fieldsContent), 'StudyEditorFields.vue não deve conter emojis')
})

test('Acessibilidade e alvos táteis mínimos (>= 44px) nos componentes de template', () => {
  const modalPath = path.resolve(__dirname, '../src/components/studies/TemplateSelectorModal.vue')
  const fieldsPath = path.resolve(__dirname, '../src/components/StudyEditorFields.vue')

  const modalContent = fs.readFileSync(modalPath, 'utf-8')
  const fieldsContent = fs.readFileSync(fieldsPath, 'utf-8')

  // Acessibilidade semântica
  assert.ok(modalContent.includes('role="dialog"'), 'TemplateSelectorModal deve ter role="dialog"')
  assert.ok(modalContent.includes('aria-modal="true"'), 'TemplateSelectorModal deve ter aria-modal="true"')
  assert.ok(modalContent.includes('aria-labelledby'), 'TemplateSelectorModal deve ter aria-labelledby')

  assert.ok(fieldsContent.includes('role="dialog"'), 'Diálogo de confirmação deve ter role="dialog"')
  assert.ok(fieldsContent.includes('aria-modal="true"'), 'Diálogo de confirmação deve ter aria-modal="true"')

  // Alvos táteis >= 44px
  assert.ok(modalContent.includes('min-height: 44px'), 'Botões do modal de seleção devem ter min-height >= 44px')
  assert.ok(fieldsContent.includes('min-height: 44px'), 'Botões de troca e confirmação devem ter min-height >= 44px')
})

test('useStudyEdit gerencia template_id no ciclo de vida, patch e dirty state', async () => {
  let patchSent = null
  const fakeStudy = {
    id: 10,
    chapter_id: 1,
    title: 'Estudo Teste',
    location: 'p. 10',
    template_id: 'classico',
    summary: 'Resumo',
    explanation: 'Explicação',
    concepts: 'Conceito',
    references: 'Ref',
    notes: 'Nota',
    source_response: '',
    version: 1,
    created_at: '2026-10-10T00:00:00Z',
    updated_at: '2026-10-10T00:00:00Z',
  }

  const editor = useStudyEdit({
    updateStudy: async (id, patch) => {
      patchSent = patch
      return { ...fakeStudy, ...patch, version: fakeStudy.version + 1 }
    },
  })

  editor.load(fakeStudy)
  assert.equal(editor.state.template_id, 'classico')
  assert.equal(editor.dirty.value, false)

  // Modificar template_id
  editor.state.template_id = 'conceito'
  assert.equal(editor.dirty.value, true)

  const saved = await editor.save()
  assert.ok(saved)
  assert.equal(patchSent.template_id, 'conceito')
  assert.equal(editor.state.template_id, 'conceito')
})

test('useImportDraft inclui template_id configurado por padrão como "classico"', async () => {
  let payloadSent = null
  const draft = useImportDraft({
    preview: async (source) => ({
      source_response: source,
      summary: 'Resumo prévia',
      explanation: '',
      concepts: '',
      references: '',
      unassigned_text: '',
      warnings: [],
    }),
    createStudy: async (payload) => {
      payloadSent = payload
      return {
        id: 99,
        chapter_id: payload.chapter_id,
        title: payload.title || 'Novo',
        location: payload.location,
        template_id: payload.template_id,
        summary: payload.summary,
        explanation: payload.explanation,
        concepts: payload.concepts,
        references: payload.references,
        notes: payload.notes,
        source_response: payload.source_response,
        version: 1,
        created_at: '2026-10-10T00:00:00Z',
        updated_at: '2026-10-10T00:00:00Z',
      }
    },
  })

  assert.equal(draft.state.template_id, 'classico')

  draft.state.bookId = '1'
  draft.state.chapterId = '2'
  draft.state.sourceResponse = 'Texto de teste'
  await draft.prepare()

  // Altera template antes de salvar
  draft.state.template_id = 'resenha'
  const saved = await draft.save()

  assert.ok(saved)
  assert.equal(payloadSent.template_id, 'resenha')
})
