import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const read = (rel) => fs.readFileSync(path.resolve(process.cwd(), 'src', rel), 'utf-8')

test('117: endereços dos feeds em Ajustes → Publicados na web', () => {
  const card = read('components/settings/PublishedStudiesCard.vue')
  for (const p of ['/feed.xml', '/feed.atom', '/feed.json']) assert.ok(card.includes(`path: '${p}'`), p)
  assert.match(card, /copyFeed\(feed\.path\)/)
  assert.match(card, /class="quiet published-button" @click="copyFeed/)
})
