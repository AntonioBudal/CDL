import test from 'node:test'
import assert from 'node:assert/strict'
import { EDITORIAL_TERMS } from '../src/constants/editorial.ts'

test('EDITORIAL_TERMS define nomenclatura canônica para Fichamento da Fonte', () => {
  assert.equal(EDITORIAL_TERMS.SOURCE_STUDY_LABEL, 'Fichamento da Fonte')
  assert.ok(EDITORIAL_TERMS.SOURCE_STUDY_HINT.includes('Texto-base'))
  assert.equal(EDITORIAL_TERMS.IMPORT_TITLE, 'Importar Fichamento')
})

test('EDITORIAL_TERMS não contém menções a IA, robôs ou ChatGPT', () => {
  const allTerms = Object.values(EDITORIAL_TERMS).join(' ')
  assert.ok(!allTerms.toLowerCase().includes('chatgpt'), 'Termo ChatGPT não deve estar presente')
  assert.ok(!allTerms.toLowerCase().includes(' ia '), 'Termo IA não deve estar presente')
  assert.ok(!allTerms.toLowerCase().includes('prompt'), 'Termo prompt não deve estar presente')
})

test('EDITORIAL_TERMS possui títulos claros para estados vazios sem emojis', () => {
  assert.equal(EDITORIAL_TERMS.EMPTY_TRASH_TITLE, 'Lixeira vazia')
  assert.equal(EDITORIAL_TERMS.EMPTY_LIBRARY_TITLE, 'Nenhum livro cadastrado')
  assert.equal(EDITORIAL_TERMS.EMPTY_CHAPTER_TITLE, 'Selecione um capítulo')
  assert.equal(EDITORIAL_TERMS.EMPTY_STUDIES_TITLE, 'Organize seu primeiro estudo')

  const emojisRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u
  for (const [key, value] of Object.entries(EDITORIAL_TERMS)) {
    assert.ok(!emojisRegex.test(value), `Termo ${key} não deve conter emojis`)
  }
})

test('código-fonte em frontend/src não contém emojis residuais ou menção a ChatGPT', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const srcDir = path.resolve(new URL('.', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'), '../src')
  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u

  function checkDir(dir) {
    const entries = fs.readdirSync(dir)
    for (const entry of entries) {
      const full = path.join(dir, entry)
      const stat = fs.statSync(full)
      if (stat.isDirectory()) {
        checkDir(full)
      } else if (entry.endsWith('.vue') || entry.endsWith('.ts')) {
        const content = fs.readFileSync(full, 'utf8')
        assert.ok(!emojiRegex.test(content), `Arquivo ${entry} não deve conter emojis informais`)
        assert.ok(!content.toLowerCase().includes('chatgpt'), `Arquivo ${entry} não deve conter referência a ChatGPT`)
      }
    }
  }

  checkDir(srcDir)
})
