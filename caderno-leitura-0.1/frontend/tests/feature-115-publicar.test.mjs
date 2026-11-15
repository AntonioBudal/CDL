import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

test('115: publicar na web no compartilhamento do estudo, com o que sai e o que não sai', () => {
  const card = read('components/sharing/PublishToWebCard.vue')
  assert.match(card, /<strong>Sai:<\/strong>/)
  assert.match(card, /<strong>Não sai:<\/strong> notas pessoais, fichamento da fonte, destaques, e-mail e nome de usuário/)
  assert.match(card, /api\.publishStudy\(props\.studyId\)/)
  assert.match(card, /api\.unpublishStudy\(props\.studyId\)/)
  assert.match(card, /`\/compartilhado\/\$\{props\.studyId\}`/)
  assert.match(card, /Tailscale/)
  const modal = read('components/sharing/ShareModal.vue')
  assert.match(modal, /<PublishToWebCard/)
  assert.match(read('views/StudyView.vue'), /@published-changed="state\.context\.study\.published_at = \$event"/)
})

test('115: lista em Ajustes e API', () => {
  assert.match(read('views/SettingsView.vue'), /<PublishedStudiesCard \/>/)
  assert.match(read('components/settings/PublishedStudiesCard.vue'), /api\.listPublishedStudies\(\)/)
  const api = read('services/api.ts')
  assert.match(api, /`\/studies\/\$\{studyId\}\/publication`, \{ method: 'POST' \}/)
  assert.match(api, /request<PublishedStudyItem\[\]>\('\/studies\/published'/)
})
