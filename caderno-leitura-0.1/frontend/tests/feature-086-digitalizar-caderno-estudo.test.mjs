import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { useDigitizeDraft, defaultTitle } from '../src/composables/useDigitizeDraft.ts'
import { ApiError } from '../src/services/api.ts'
import { DIGITIZE_EXIT_SHORTCUTS, DIGITIZE_SECTIONS, DIGITIZE_DEFAULT_SECTION } from '../src/types/digitize.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = relative => fs.readFileSync(path.resolve(srcDir, relative), 'utf-8')
const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u

// Dados fictícios: nenhuma leitura real do acervo.
const preview = () => ({
  text: 'Capítulo 1 do Livro de Teste\nlinha fictícia incerta\nterceira linha',
  lines: [
    { index: 0, text: 'Capítulo 1 do Livro de Teste', confidence: 0.95, low_confidence: false },
    { index: 1, text: 'linha fictícia incerta', confidence: 0.41, low_confidence: true },
    { index: 2, text: 'terceira linha', confidence: 0.9, low_confidence: false },
  ],
  low_confidence_count: 1,
  warnings: [{ code: 'draft', message: 'Texto lido automaticamente.' }],
  engine: { name: 'leitorum-motor', version: '0.0.0', reader: 'Leitor de Teste', license_status: 'VERIFIED' },
  elapsed_ms: 10,
})
const photo = (type = 'image/jpeg', size = 10) => new File([new Uint8Array(size)], 'pagina.jpg', { type })
const saved = payload => ({ ...payload, id: 31, reading_status: 'rascunho', created_at: '2026-10-27T12:00:00Z', updated_at: '2026-10-27T12:00:00Z' })
function deferred() {
  let resolve, reject
  const promise = new Promise((done, fail) => { resolve = done; reject = fail })
  return { promise, resolve, reject }
}
function makeDraft(gateway = {}) {
  const urls = { created: 0, revoked: [] }
  const draft = useDigitizeDraft(
    {
      status: async () => ({ available: true, reason: null }),
      preview: async () => preview(),
      createStudy: async payload => saved(payload),
      ...gateway,
    },
    {
      createObjectURL: () => `blob:teste-${++urls.created}`,
      revokeObjectURL: url => urls.revoked.push(url),
      today: () => new Date(2026, 9, 27),
    },
  )
  return { draft, urls }
}

// --- Rota e tela ----------------------------------------------------------------------------

test('rota /digitalizar mantém alias, nome, título e componente', () => {
  const router = read('router/index.ts')
  assert.ok(router.includes("path: '/digitalizar'"))
  assert.ok(router.includes("alias: ['/scan']"))
  assert.ok(router.includes("name: 'digitize-notebook'"))
  assert.ok(router.includes('component: DigitizeNotebookView'))
  assert.ok(router.includes("title: 'Digitalizar Caderno'"))
})

test('tela oferece câmera e arquivo com formatos restritos, sem getUserMedia', () => {
  const view = read('views/DigitizeNotebookView.vue')
  assert.ok(view.includes('type="file"'))
  assert.ok(view.includes('capture="environment"'), 'Tirar foto abre a câmera traseira')
  assert.equal((view.match(/type="file"/g) || []).length, 2, 'Tirar foto e Escolher imagem')
  assert.ok(view.includes(':accept="DIGITIZE_ACCEPT"'))
  assert.ok(view.includes('Tirar foto') && view.includes('Escolher imagem'))
  assert.ok(!view.includes('getUserMedia') && !view.includes('mediaDevices'))
})

test('seletores de arquivo ficam escondidos apesar da regra global input { display: block }', () => {
  const view = read('views/DigitizeNotebookView.vue')
  const globalStyle = read('style.css')
  assert.match(globalStyle, /input, textarea, select \{ display: block;/, 'premissa: a regra global existe')
  const inputs = view.match(/<input[^>]*type="file"[^>]*>/g) || []
  assert.equal(inputs.length, 2)
  for (const input of inputs) {
    assert.ok(input.includes('class="file-picker"'), 'cada seletor usa a classe que o esconde')
    assert.ok(input.includes('hidden') && input.includes('tabindex="-1"'))
  }
  const style = view.slice(view.indexOf('<style'))
  assert.match(style, /\.file-picker,\s*\.file-picker\[hidden\]\s*\{\s*display: none;\s*\}/)
})

test('tela traz aviso de rascunho, processamento local, atalhos e proteção de alterações', () => {
  const view = read('views/DigitizeNotebookView.vue')
  assert.ok(view.includes('Rascunho lido automaticamente.'))
  assert.ok(view.includes('Linhas para conferir'))
  assert.ok(view.includes('computador onde o Leitorum está instalado'))
  assert.ok(view.includes('Nada é enviado para a internet'))
  assert.ok(view.includes('DIGITIZE_EXIT_SHORTCUTS'))
  assert.ok(view.includes('to="/importar"') && view.includes('to="/inbox"'))
  assert.ok(view.includes('useUnsavedChanges('))
  assert.ok(view.includes('draft.dispose()'), 'Sair da tela cancela a leitura e libera a foto')
  assert.ok(view.includes('<EmptyState') && view.includes('<LoadingSkeleton'))
  assert.ok(!emojiRegex.test(view), 'Sem emojis')
})

test('tela segue a hierarquia de títulos, alvos de 44px e só tokens semânticos', () => {
  const view = read('views/DigitizeNotebookView.vue')
  assert.ok(view.includes('aria-labelledby="digitize-main-title"'))
  assert.ok(view.includes('<h1') && view.includes('<h2') && view.includes('<h3'))
  const style = view.slice(view.indexOf('<style'))
  assert.ok(style.includes('min-height: 44px'))
  assert.ok(style.includes(':focus-visible'))
  assert.ok(style.includes('prefers-reduced-motion'))
  assert.ok(!/#[0-9a-fA-F]{3,8}\b/.test(style), 'Sem cores hexadecimais no estilo')
  assert.ok(!/rgba?\(/.test(style), 'Sem cores rgb fixas no estilo')
  for (const token of ['--color-surface', '--color-text', '--color-muted', '--color-border', '--color-accent']) {
    assert.ok(style.includes(`var(${token}`), `Usa ${token}`)
  }
})

test('card do Ateliê de Importação deixa de dizer Em Pesquisa', () => {
  const importView = read('views/ImportView.vue')
  assert.ok(importView.includes('digitize-invitation-card'))
  assert.ok(importView.includes('to="/digitalizar"'))
  assert.ok(importView.includes('Rascunho a revisar'))
  assert.ok(!importView.includes('Em Pesquisa'))
  assert.ok(!emojiRegex.test(importView))
})

test('atalhos de saída e seções disponíveis', () => {
  assert.deepEqual(DIGITIZE_EXIT_SHORTCUTS.map(item => item.routePath), ['/importar', '/inbox'])
  assert.deepEqual(DIGITIZE_SECTIONS.map(item => item.key), ['summary', 'explanation', 'concepts', 'references'])
  assert.equal(DIGITIZE_DEFAULT_SECTION, 'summary')
})

// --- Composable --------------------------------------------------------------------------

test('status indisponível leva ao estado unavailable com o motivo', async () => {
  const { draft } = makeDraft({ status: async () => ({ available: false, reason: 'not_installed' }) })
  await draft.checkStatus()
  assert.equal(draft.state.phase, 'unavailable')
  assert.equal(draft.state.unavailableReason, 'not_installed')
  assert.equal(await draft.choose(photo()), false)
})

test('foto lida vai para revisão com texto, título padrão e linhas para conferir', async () => {
  const { draft } = makeDraft()
  await draft.checkStatus()
  assert.equal(await draft.choose(photo()), true)
  assert.equal(draft.state.phase, 'review')
  assert.equal(draft.state.text, preview().text)
  assert.equal(draft.state.title, 'Página digitalizada em 27/10/2026')
  assert.equal(draft.state.previewUrl, 'blob:teste-1')
  assert.deepEqual(draft.uncertainLines.value, [{ index: 1, number: 2, text: 'linha fictícia incerta', revised: false }])
  draft.state.text = draft.state.text.replace('linha fictícia incerta', 'linha fictícia corrigida')
  assert.equal(draft.uncertainLines.value[0].revised, true, 'Linha editada aparece como já revisada')
  assert.equal(draft.dirty.value, true)
})

test('formatos e tamanhos inválidos são recusados antes do envio', async () => {
  let calls = 0
  const { draft } = makeDraft({ preview: async () => { calls++; return preview() } })
  await draft.checkStatus()
  assert.equal(await draft.choose(photo('application/pdf')), false)
  assert.equal(draft.state.error.code, 'unsupported_format')
  draft.reset()
  assert.equal(await draft.choose(photo('image/png', 20 * 1024 * 1024 + 1)), false)
  assert.equal(draft.state.error.code, 'too_large')
  assert.equal(calls, 0)
})

test('erros da API viram mensagem em português com o código do contrato', async () => {
  const { draft, urls } = makeDraft({
    preview: async () => { throw new ApiError('Outra página está sendo lida agora.', 503, { detail: 'Outra página está sendo lida agora.', code: 'busy' }) },
  })
  await draft.checkStatus()
  assert.equal(await draft.choose(photo()), false)
  assert.equal(draft.state.phase, 'error')
  assert.deepEqual(draft.state.error, { code: 'busy', message: 'Outra página está sendo lida agora.' })
  assert.deepEqual(urls.revoked, ['blob:teste-1'], 'A foto é liberada no erro')
})

test('motor que some durante o uso leva ao estado indisponível', async () => {
  const { draft } = makeDraft({
    preview: async () => { throw new ApiError('indisponível', 503, { detail: 'indisponível', code: 'unavailable' }) },
  })
  await draft.checkStatus()
  await draft.choose(photo())
  assert.equal(draft.state.phase, 'unavailable')
})

test('cancelar aborta a leitura, libera a foto e ignora a resposta tardia', async () => {
  const pending = deferred()
  let signal
  const { draft, urls } = makeDraft({ preview: async (_file, s) => { signal = s; return pending.promise } })
  await draft.checkStatus()
  const choosing = draft.choose(photo())
  assert.equal(draft.state.phase, 'reading')
  draft.cancel()
  assert.equal(signal.aborted, true)
  assert.equal(draft.state.phase, 'idle')
  assert.deepEqual(urls.revoked, ['blob:teste-1'])
  pending.resolve(preview())
  assert.equal(await choosing, false)
  assert.equal(draft.state.phase, 'idle')
  assert.equal(draft.state.preview, null)
})

test('salvar monta o estudo com a seção escolhida e a leitura bruta como origem', async () => {
  let payload
  const { draft } = makeDraft({ createStudy: async value => { payload = value; return saved(value) } })
  await draft.checkStatus()
  await draft.choose(photo())
  Object.assign(draft.state, { bookId: '2', chapterId: '7', section: 'explanation' })
  draft.state.text = 'Texto revisado de teste'
  const result = await draft.save()
  assert.equal(result.id, 31)
  assert.deepEqual(payload, {
    chapter_id: 7,
    title: 'Página digitalizada em 27/10/2026',
    location: '',
    source_response: preview().text,
    summary: '', explanation: 'Texto revisado de teste', concepts: '', references: '',
    notes: '',
  })
  assert.equal(draft.state.phase, 'saved')
  assert.equal(draft.dirty.value, false)
})

test('seção padrão é Resumo e salvar não roda duas vezes (uma foto, um estudo)', async () => {
  let calls = 0
  const pending = deferred()
  const { draft } = makeDraft({ createStudy: async value => { calls++; await pending.promise; return saved(value) } })
  await draft.checkStatus()
  await draft.choose(photo())
  Object.assign(draft.state, { bookId: '2', chapterId: '7' })
  const first = draft.save()
  const second = await draft.save()
  assert.equal(second, null)
  pending.resolve()
  const study = await first
  assert.equal(study.summary, preview().text)
  assert.equal(await draft.save(), null, 'Depois de salvo, só uma nova página salva de novo')
  assert.equal(calls, 1)
})

test('sem capítulo, título ou texto o salvamento fica bloqueado', async () => {
  const { draft } = makeDraft()
  await draft.checkStatus()
  await draft.choose(photo())
  assert.equal(draft.canSave.value, false, 'Sem capítulo')
  Object.assign(draft.state, { bookId: '2', chapterId: '7' })
  assert.equal(draft.canSave.value, true)
  draft.state.text = '   '
  assert.equal(draft.canSave.value, false, 'Texto vazio')
  draft.state.text = 'algo'
  draft.state.title = ' '
  assert.equal(draft.canSave.value, false, 'Título vazio')
})

test('falha ao salvar volta para a revisão e mantém o texto', async () => {
  const { draft } = makeDraft({ createStudy: async () => { throw new ApiError('Falha de rede', 0) } })
  await draft.checkStatus()
  await draft.choose(photo())
  Object.assign(draft.state, { bookId: '2', chapterId: '7' })
  draft.state.text = 'Texto revisado de teste'
  assert.equal(await draft.save(), null)
  assert.equal(draft.state.phase, 'review')
  assert.equal(draft.state.text, 'Texto revisado de teste')
  assert.equal(draft.state.error.code, 'save_failed')
})

test('nova página mantém o destino e limpa o resto; dispose libera a foto', async () => {
  const { draft, urls } = makeDraft()
  await draft.checkStatus()
  await draft.choose(photo())
  Object.assign(draft.state, { bookId: '2', chapterId: '7', section: 'concepts' })
  draft.reset()
  assert.equal(draft.state.phase, 'idle')
  assert.equal(draft.state.bookId, '2')
  assert.equal(draft.state.chapterId, '7')
  assert.equal(draft.state.section, 'summary')
  assert.equal(draft.state.text, '')
  assert.deepEqual(urls.revoked, ['blob:teste-1'])
  await draft.choose(photo())
  draft.dispose()
  assert.deepEqual(urls.revoked, ['blob:teste-1', 'blob:teste-2'])
})

test('título padrão usa a data local em DD/MM/AAAA', () => {
  assert.equal(defaultTitle(new Date(2026, 0, 5)), 'Página digitalizada em 05/01/2026')
})
