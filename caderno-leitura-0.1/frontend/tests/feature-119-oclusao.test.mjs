import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const read = (rel) => fs.readFileSync(path.resolve(process.cwd(), 'src', rel), 'utf-8')

test('119: editor SVG de oclusão (relativo 0–1, toque, teclado, 50 áreas, salvar em lote)', () => {
  const editor = read('components/ImageOcclusionEditor.vue')
  assert.match(editor, /viewBox="0 0 1 1" preserveAspectRatio="none"/)
  assert.match(editor, /touch-action: none/)
  assert.match(editor, /@pointerdown="startDraw"/)
  assert.match(editor, /event\.key === 'Delete' \|\| event\.key === 'Backspace'/)
  assert.match(editor, /const MAX_BOXES = 50/)
  assert.match(editor, /api\.saveOcclusions\(props\.studyId, props\.mediaId, cards\)/)
  assert.match(editor, /mantida para sempre/)
  const api = read('services/api.ts')
  assert.match(api, /\/studies\/\$\{studyId\}\/media\/\$\{encodeURIComponent\(mediaId\)\}\/occlusions/)
  assert.match(api, /method: 'PUT', body: JSON\.stringify\(\{ cards \}\)/)
})

test('119: entrada pela Folha original e pelo menu do estudo', () => {
  const viewer = read('components/media/OriginalPageViewer.vue')
  assert.match(viewer, /emit\('occlude', current\.id\)/)
  assert.match(viewer, /Criar cartões nesta imagem/)
  assert.match(viewer, /desenhados nela também serão apagados/)
  const study = read('views/StudyView.vue')
  assert.match(study, /@occlude="openOcclusion"/)
  assert.match(study, /Adicionar imagem para cartões/)
  assert.match(study, /<ImageOcclusionEditor/)
})

test('119: revisão com o tipo Imagens (filtro, cartão e nota)', () => {
  assert.match(read('components/review/ReviewStatsHeader.vue'), /@click="setKind\('image'\)"[\s\S]*?Imagens/)
  const card = read('components/review/ReviewCard.vue')
  assert.match(card, /item\.kind === 'image' && item\.media_id/)
  assert.match(card, /<OcclusionImage/)
  const image = read('components/review/OcclusionImage.vue')
  assert.match(image, /\/api\/media\/\$\{encodeURIComponent\(mediaId\)\}\/content/)
  assert.match(image, /isTarget\(region\) \? \(revealed \? 'occlusion-open' : 'occlusion-target'\) : 'occlusion-cover'/)
  const session = read('composables/useReviewSession.ts')
  assert.match(session, /item\.kind === 'image'\) await reviewApi\.recordImageRating\(item\.id, rating\)/)
  assert.match(session, /state\.ratings\[`\$\{item\.kind\}:\$\{item\.id\}`\]/)
})
