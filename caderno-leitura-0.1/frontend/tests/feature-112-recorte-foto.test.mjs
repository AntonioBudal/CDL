import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import {
  CROP_MIN,
  clampCrop,
  describeCrop,
  drawTransform,
  initialCrop,
  isWholeImage,
  keyboardDelta,
  moveCrop,
  moveHandle,
  outputSize,
  rotate,
  rotateCrop,
  rotatedSize,
  sourceOffset,
} from '../src/utils/photoCrop.ts'
import { useDigitizeDraft } from '../src/composables/useDigitizeDraft.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')
const near = (a, b) => Object.keys(b).forEach((k) => assert.ok(Math.abs(a[k] - b[k]) < 1e-6, `${k}: ${a[k]} ≠ ${b[k]}`))

test('112: recorte inicial, alças e mover', () => {
  near(initialCrop(), { x: 0.04, y: 0.04, w: 0.92, h: 0.92 })
  const c = { x: 0.1, y: 0.1, w: 0.5, h: 0.5 }
  near(moveHandle(c, 'nw', 0.05, 0.05), { x: 0.15, y: 0.15, w: 0.45, h: 0.45 })
  near(moveHandle(c, 'se', 0.1, 0.2), { x: 0.1, y: 0.1, w: 0.6, h: 0.7 })
  near(moveHandle(c, 'e', 1, 0), { x: 0.1, y: 0.1, w: 0.9, h: 0.5 })
  near(moveHandle(c, 'n', 0, -1), { x: 0.1, y: 0, w: 0.5, h: 0.6 })
  near(moveHandle(c, 'w', 0.9, 0), { x: 0.6 - CROP_MIN, y: 0.1, w: CROP_MIN, h: 0.5 })
  near(moveHandle(c, 'move', 0.8, -0.5), { x: 0.5, y: 0, w: 0.5, h: 0.5 })
  near(moveCrop(c, -1, 0), { x: 0, y: 0.1, w: 0.5, h: 0.5 })
  near(clampCrop({ x: 0.95, y: -0.2, w: 0.01, h: 2 }), { x: 0.9, y: 0, w: 0.1, h: 1 })
})

test('112: giro do recorte e da imagem', () => {
  const c = { x: 0.1, y: 0.2, w: 0.3, h: 0.4 }
  near(rotateCrop(c, 'right'), { x: 0.4, y: 0.1, w: 0.4, h: 0.3 })
  near(rotateCrop(rotateCrop(c, 'right'), 'left'), c)
  let r = c
  for (let i = 0; i < 4; i++) r = rotateCrop(r, 'right')
  near(r, c)
  assert.equal(rotate(0, 'right'), 90)
  assert.equal(rotate(0, 'left'), 270)
  assert.equal(rotate(270, 'right'), 0)
  assert.deepEqual(rotatedSize(4000, 3000, 90), { width: 3000, height: 4000 })
  assert.deepEqual(drawTransform(90, 3000, 4000), { tx: 3000, ty: 0, angle: Math.PI / 2 })
  assert.deepEqual(drawTransform(180, 4000, 3000), { tx: 4000, ty: 3000, angle: Math.PI })
  assert.deepEqual(drawTransform(270, 3000, 4000), { tx: 0, ty: 4000, angle: -Math.PI / 2 })
  assert.deepEqual(sourceOffset(4000, 3000, { x: 0.5, y: 0.25, w: 0.5, h: 0.5 }, 90), { x: 1500, y: 1000 })
})

test('112: tamanho de saída, foto inteira, descrição e teclado', () => {
  assert.deepEqual(outputSize(4000, 3000, { x: 0, y: 0, w: 0.5, h: 0.5 }, 0), { width: 2000, height: 1500, scale: 1 })
  const big = outputSize(10000, 8000, { x: 0, y: 0, w: 1, h: 1 }, 90)
  assert.ok(big.width * big.height <= 40_000_000 * 1.001 && big.scale < 1)
  assert.ok(Math.abs(big.width / big.height - 8000 / 10000) < 0.01, 'proporção mantida')
  assert.ok(isWholeImage({ x: 0, y: 0, w: 1, h: 1 }, 0))
  assert.ok(!isWholeImage({ x: 0, y: 0, w: 1, h: 1 }, 90))
  assert.ok(!isWholeImage(initialCrop(), 0))
  assert.equal(describeCrop(initialCrop()), 'Recorte: 4% a 96% na largura, 4% a 96% na altura.')
  assert.deepEqual(keyboardDelta('ArrowLeft', false), { dx: -0.01, dy: 0 })
  assert.deepEqual(keyboardDelta('ArrowDown', true), { dx: 0, dy: 0.05 })
  assert.equal(keyboardDelta('a', false), null)
})

function makeDraft() {
  const sent = []
  const urls = { created: 0, revoked: [] }
  const draft = useDigitizeDraft(
    {
      status: async () => ({ available: true, reason: null }),
      preview: async (file) => {
        sent.push(file.name)
        return { text: 'Texto fictício.', lines: [], low_confidence_count: 0, warnings: [], engine: { name: 'x', version: '0', reader: 'x', license_status: 'VERIFIED' }, elapsed_ms: 1 }
      },
      createStudy: async (p) => ({ ...p, id: 1 }),
    },
    { createObjectURL: () => `blob:t-${++urls.created}`, revokeObjectURL: (u) => urls.revoked.push(u), today: () => new Date(2026, 10, 12) },
  )
  return { draft, sent, urls }
}
const file = (name, type = 'image/jpeg') => new File([new Uint8Array(10)], name, { type })

test('112: composable — prepare, ler o recortado, descartar', async () => {
  const { draft, sent, urls } = makeDraft()
  await draft.checkStatus()
  assert.equal(draft.prepare(file('original.jpg')), true)
  assert.equal(draft.state.phase, 'adjust')
  assert.equal(draft.state.previewUrl, 'blob:t-1')
  assert.equal(await draft.read(file('recortada.jpg')), true)
  assert.equal(draft.state.phase, 'review')
  assert.deepEqual(sent, ['recortada.jpg'])
  assert.ok(urls.revoked.includes('blob:t-1'), 'a prévia da original é liberada')

  const second = makeDraft()
  await second.draft.checkStatus()
  assert.equal(second.draft.prepare(file('nao.gif', 'image/gif')), false)
  assert.equal(second.draft.state.phase, 'error')
  const third = makeDraft()
  await third.draft.checkStatus()
  third.draft.prepare(file('outra.jpg'))
  third.draft.discardAdjust()
  assert.equal(third.draft.state.phase, 'idle')
  assert.equal(await third.draft.read(file('x.jpg')), false, 'fora da etapa de recorte não lê')
})

test('112: tela usa o recortador entre escolher e ler', () => {
  const view = read('views/DigitizeNotebookView.vue')
  assert.match(view, /draft\.prepare\(file\)/)
  assert.match(view, /<PhotoCropper\s+v-else-if="state\.phase === 'adjust' && chosenFile"/)
  assert.match(view, /@confirm="readPhoto"/)
  const cropper = read('components/digitize/PhotoCropper.vue')
  for (const label of ['Ler a página', 'Usar a foto inteira', 'Escolher outra foto', 'Girar à esquerda', 'Girar à direita']) {
    assert.ok(cropper.includes(label), label)
  }
  assert.match(cropper, /aria-live="polite"/)
  assert.match(cropper, /touch-action: none/)
  assert.match(cropper, /imageOrientation: 'from-image'/)
  assert.match(cropper, /Canto superior esquerdo do recorte/)
  assert.ok(cropper.includes('event.stopPropagation() // a alça não move também o recorte inteiro'))
})
