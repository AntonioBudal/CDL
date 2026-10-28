import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { formatBytes, shortDate, usageText, validityText } from '../src/utils/mediaFormat.ts'
import { useMediaSpace } from '../src/composables/useMediaSpace.ts'
import { useOriginalPage, ZOOM_MAX, ZOOM_MIN } from '../src/composables/useOriginalPage.ts'
import { useDigitizeDraft } from '../src/composables/useDigitizeDraft.ts'
import { ApiError } from '../src/services/api.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = relative => fs.readFileSync(path.resolve(srcDir, relative), 'utf-8')
const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
const GIB = 1024 ** 3

// Dados fictícios: nenhuma leitura real do acervo.
const item = (overrides = {}) => ({
  id: 'm1', kind: 'notebook_page', status: 'active',
  book: { id: 2, title: 'Livro de Teste', in_trash: false },
  study: { id: 31, title: 'Capítulo 1', reading_status: 'revisado', in_trash: false },
  byte_size: 356_000, width: 1500, height: 2000, keep_forever: false,
  created_at: '2026-10-27T12:00:00Z', expires_at: '2026-11-26T12:00:00Z', days_left: 30,
  ...overrides,
})
const usage = (level = 'normal') => ({
  user: { used_bytes: 312 * 1024 ** 2, quota_bytes: GIB, count: 3, percent: 30.5, level },
  server: { level: 'normal' },
  vault: { state: 'ready' },
})

// --- Formatação ----------------------------------------------------------------------------------

test('tamanhos no padrão do Windows (base 1024) e com vírgula decimal', () => {
  assert.equal(formatBytes(GIB), '1 GB')
  assert.equal(formatBytes(1.5 * GIB), '1,5 GB')
  assert.equal(formatBytes(900 * GIB), '900 GB')
  assert.equal(formatBytes(312 * 1024 ** 2), '312 MB')
  assert.equal(formatBytes(348 * 1024), '348 KB')
  assert.equal(formatBytes(10), '1 KB')
  assert.equal(usageText(312 * 1024 ** 2, GIB, 874), '312 MB de 1 GB utilizados (874 imagens)')
  assert.equal(usageText(0, GIB, 1), '0 KB de 1 GB utilizados (1 imagem)')
})

test('validade em texto: dias, hoje, mantida e não expira', () => {
  assert.equal(validityText(item()), 'expira em 30 dias')
  assert.equal(validityText(item({ days_left: 1 })), 'expira em 1 dia')
  assert.equal(validityText(item({ days_left: 0 })), 'expira hoje')
  assert.equal(validityText(item({ keep_forever: true, days_left: null })), 'Mantida permanentemente')
  assert.equal(validityText(item({ kind: 'cover', days_left: null })), 'Não expira')
  assert.match(shortDate('2026-10-27T12:00:00Z'), /^\d{2}\/\d{2}\/2026$/)
})

// --- Minhas Imagens e Espaço ------------------------------------------------------------------

function spaceGateway(overrides = {}) {
  const calls = { bulk: [], remove: [], keep: [], list: 0 }
  const items = [item(), item({ id: 'm2', byte_size: 100_000 }), item({ id: 'c1', kind: 'cover', study: null, days_left: null, expires_at: null })]
  const gateway = {
    usage: async () => usage(),
    list: async () => { calls.list++; return { items: items.slice(), next_offset: null } },
    setKeep: async (id, keep) => { calls.keep.push([id, keep]); return item({ id, keep_forever: keep, days_left: keep ? null : 30 }) },
    remove: async id => { calls.remove.push(id); return { freed_bytes: 40_000 } },
    bulk: async payload => {
      calls.bulk.push(payload)
      if (payload.dry_run) return payload.filter === 'completed_studies' ? { matched: 2, freed_bytes: 15 * 1024 ** 2, deleted: 0 } : { matched: 0, freed_bytes: 0, deleted: 0 }
      return { matched: 2, freed_bytes: 15 * 1024 ** 2, deleted: 2 }
    },
    ...overrides,
  }
  return { gateway, calls }
}

test('carrega uso, lista e as prévias de lote (dry_run)', async () => {
  const { gateway, calls } = spaceGateway()
  const space = useMediaSpace(gateway)
  await space.load()
  assert.equal(space.state.loading, false)
  assert.equal(space.state.items.length, 3)
  assert.equal(space.state.usage.user.count, 3)
  assert.equal(space.state.previews.completed.matched, 2)
  assert.ok(calls.bulk.every(payload => payload.dry_run === true), 'carregar nunca apaga')
  assert.deepEqual(space.books.value, [{ id: 2, title: 'Livro de Teste' }])
})

test('lote de concluídos: prévia com quantidade e MB, confirmação apaga e recarrega', async () => {
  const { gateway, calls } = spaceGateway()
  const space = useMediaSpace(gateway)
  await space.load()
  space.askBulk('older')
  assert.equal(space.state.pending, null, 'sem fotos antigas, nada a confirmar')
  space.askBulk('completed')
  assert.match(space.state.pending.message, /Apagar 2 fotos \(15 MB\)\?/)
  assert.match(space.state.pending.message, /Os estudos e seus textos não serão alterados\./)
  const listsBefore = calls.list
  assert.equal(await space.confirmPending(), true)
  assert.deepEqual(calls.bulk.at(-3), { filter: 'completed_studies', dry_run: false })
  assert.equal(space.state.pending, null)
  assert.match(space.state.notice, /2 imagens apagadas \(15 MB liberados\)/)
  assert.ok(calls.list > listsBefore, 'a lista e o uso são recarregados')
})

test('seleção apaga só os ids escolhidos; capa sai pela rota individual', async () => {
  const { gateway, calls } = spaceGateway()
  const space = useMediaSpace(gateway)
  await space.load()
  space.toggleSelected('m1')
  space.toggleSelected('m2')
  space.toggleSelected('m2')
  space.askSelected()
  assert.deepEqual(space.state.pending.ids, ['m1'])
  await space.confirmPending()
  assert.ok(calls.bulk.some(payload => payload.ids?.length === 1 && payload.ids[0] === 'm1' && payload.dry_run === false))
  assert.deepEqual(space.state.selected, [])

  space.askSingle(space.state.items.find(entry => entry.kind === 'cover'))
  assert.match(space.state.pending.message, /O livro fica sem capa\./)
  await space.confirmPending()
  assert.deepEqual(calls.remove, ['c1'])
})

test('manter permanentemente alterna e atualiza o cartão', async () => {
  const { gateway, calls } = spaceGateway()
  const space = useMediaSpace(gateway)
  await space.load()
  await space.toggleKeep(space.state.items[0])
  assert.deepEqual(calls.keep, [['m1', true]])
  assert.equal(space.state.items[0].keep_forever, true)
  assert.match(space.state.notice, /mantida permanentemente/)
  await space.toggleKeep(space.state.items.find(entry => entry.kind === 'cover'))
  assert.equal(calls.keep.length, 1, 'capa não tem "manter"')
})

// --- Folha original ------------------------------------------------------------------------------

test('folha original: zoom com limites, teclas, navegação e apagar a atual', async () => {
  const removed = []
  const viewer = useOriginalPage({
    list: async () => ({ items: [item(), item({ id: 'm2' })] }),
    setKeep: async (id, keep) => item({ id, keep_forever: keep, days_left: null }),
    remove: async id => { removed.push(id); return { freed_bytes: 1 } },
  })
  await viewer.load(31)
  assert.equal(viewer.count.value, 2)
  assert.equal(viewer.state.fit, true)
  for (let i = 0; i < 30; i++) viewer.zoomIn()
  assert.equal(viewer.state.zoom, ZOOM_MAX)
  for (let i = 0; i < 30; i++) viewer.zoomOut()
  assert.equal(viewer.state.zoom, ZOOM_MIN)
  assert.equal(viewer.handleKey('0'), true)
  assert.equal(viewer.state.fit, true)
  assert.equal(viewer.handleKey('+'), true)
  assert.equal(viewer.state.zoom, 1.25)
  assert.equal(viewer.handleKey('x'), false)
  viewer.handleKey('ArrowRight')
  assert.equal(viewer.current.value.id, 'm2')
  viewer.go(1)
  assert.equal(viewer.current.value.id, 'm1')
  await viewer.toggleKeep()
  assert.equal(viewer.current.value.keep_forever, true)
  assert.equal(await viewer.removeCurrent(), true)
  assert.deepEqual(removed, ['m1'])
  assert.equal(viewer.count.value, 1)
  assert.equal(viewer.current.value.id, 'm2')
})

// --- Digitalização: guardar a foto -------------------------------------------------------------

const preview = () => ({
  text: 'Capítulo 1 do Livro de Teste', lines: [], low_confidence_count: 0,
  warnings: [], engine: { name: 'motor', version: '0', reader: 'Leitor de Teste', license_status: 'VERIFIED' }, elapsed_ms: 1,
})
const photoFile = () => new File([new Uint8Array(10)], 'pagina.jpg', { type: 'image/jpeg' })

async function reviewDraft(storePhoto, keepPhoto) {
  const order = []
  const draft = useDigitizeDraft(
    {
      status: async () => ({ available: true, reason: null }),
      preview: async () => preview(),
      createStudy: async payload => { order.push('study'); return { ...payload, id: 77, reading_status: 'rascunho' } },
      storePhoto: async (studyId, file) => { order.push(['photo', studyId, file.name]); return storePhoto(studyId, file) },
    },
    { createObjectURL: () => 'blob:teste', revokeObjectURL: () => {}, today: () => new Date(2026, 9, 27) },
  )
  await draft.checkStatus()
  await draft.choose(photoFile())
  draft.state.chapterId = '5'
  draft.state.keepPhoto = keepPhoto
  return { draft, order }
}

test('caixa desmarcada (padrão): a foto não é guardada', async () => {
  const { draft, order } = await reviewDraft(async () => { throw new Error('não deveria guardar') }, false)
  assert.equal(useDigitizeDraft({ status: async () => ({}) }).state.keepPhoto, false, 'desmarcada por padrão')
  await draft.save()
  assert.deepEqual(order, ['study'])
  assert.equal(draft.state.phase, 'saved')
  assert.equal(draft.state.photoExpiresAt, null)
})

test('caixa marcada: a foto vai depois do estudo, para o estudo salvo', async () => {
  const { draft, order } = await reviewDraft(async () => ({ item: item({ expires_at: '2026-11-26T12:00:00Z' }), usage: usage() }), true)
  await draft.save()
  assert.deepEqual(order, ['study', ['photo', 77, 'pagina.jpg']])
  assert.equal(draft.state.photoExpiresAt, '2026-11-26T12:00:00Z')
  assert.equal(draft.state.photoWarning, '')
})

test('falha ao guardar a foto vira aviso e o estudo continua salvo', async () => {
  const { draft } = await reviewDraft(async () => {
    throw new ApiError('Seu espaço está cheio: 1 GB de 1 GB. Libere espaço em Minhas Imagens e Espaço.', 507, { code: 'user_quota' })
  }, true)
  const saved = await draft.save()
  assert.equal(saved.id, 77)
  assert.equal(draft.state.phase, 'saved')
  assert.match(draft.state.photoWarning, /Minhas Imagens e Espaço/)
  draft.reset()
  assert.equal(draft.state.keepPhoto, false, 'a próxima página volta desmarcada')
})

// --- Telas -------------------------------------------------------------------------------------

test('rota e atalhos para Minhas Imagens e Espaço', () => {
  const router = read('router/index.ts')
  assert.ok(router.includes("path: '/minhas-imagens'"))
  assert.ok(router.includes("title: 'Minhas Imagens e Espaço'"))
  assert.ok(read('components/layout/UserDropdown.vue').includes('to="/minhas-imagens"'))
  assert.ok(read('views/SettingsView.vue').includes('to="/minhas-imagens"'))
})

test('medidor acessível: role meter, aria-valuetext e nível em texto', () => {
  const meter = read('components/media/StorageMeter.vue')
  assert.ok(meter.includes('role="meter"'))
  assert.ok(meter.includes(':aria-valuetext="valueText"'))
  assert.ok(meter.includes('Estado: {{ levelText }}'))
  assert.ok(meter.includes("data-theme='e-ink'"), 'hachura no E-Ink')
})

test('telas novas: textos, alvos de 44 px, foco visível e nenhum emoji', () => {
  const files = [
    'views/MediaSpaceView.vue', 'components/media/MediaCard.vue', 'components/media/OriginalPageViewer.vue',
    'components/media/StorageMeter.vue',
  ]
  for (const file of files) assert.ok(!emojiRegex.test(read(file)), `sem emoji: ${file}`)
  const view = read('views/MediaSpaceView.vue')
  assert.ok(view.includes('Minhas Imagens e Espaço') && view.includes('Liberar espaço'))
  assert.ok(view.includes('Digitalizar uma página'))
  const card = read('components/media/MediaCard.vue')
  assert.ok(card.includes('loading="lazy"') && card.includes(':aria-pressed="item.keep_forever"'))
  assert.ok(card.includes('Arquivo indisponível'))
  for (const file of ['components/media/MediaCard.vue', 'components/media/OriginalPageViewer.vue', 'views/MediaSpaceView.vue']) {
    const source = read(file)
    assert.ok(source.includes('min-height: 44px'), `alvo de 44 px: ${file}`)
    assert.ok(source.includes(':focus-visible'), `foco visível: ${file}`)
  }
})

test('estudo e digitalização usam a folha original e a caixa de guardar', () => {
  const study = read('views/StudyView.vue')
  assert.ok(study.includes('Folha original ({{ originalPage.count.value }})'))
  assert.ok(study.includes('role="separator"') && study.includes('role="tablist"'))
  const digitize = read('views/DigitizeNotebookView.vue')
  assert.ok(digitize.includes('Guardar a foto com o estudo para conferência (apagada automaticamente em 30 dias)'))
  assert.ok(digitize.includes('v-model="state.keepPhoto"'))
  assert.ok(digitize.includes('storePhoto: api.storeStudyPhoto'))
  assert.ok(digitize.includes('A foto é apagada assim que a leitura termina'), 'a promessa da 086 continua sem a caixa')
})
