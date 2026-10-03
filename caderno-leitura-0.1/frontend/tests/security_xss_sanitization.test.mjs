import test from 'node:test'
import assert from 'node:assert/strict'

import { isSafeUrl, sanitizeHtml } from '../src/services/sanitizer.ts'
import { renderMarkdown } from '../src/services/markdown.ts'

test('isSafeUrl aceita exclusivamente protocolos seguros e caminhos relativos', () => {
  assert.equal(isSafeUrl('https://leitorum.com'), true)
  assert.equal(isSafeUrl('http://localhost:8000/api'), true)
  assert.equal(isSafeUrl('mailto:contato@leitorum.com'), true)
  assert.equal(isSafeUrl('/livros/1'), true)
  assert.equal(isSafeUrl('#capitulo-2'), true)

  // Rejeita esquemas perigosos
  assert.equal(isSafeUrl('javascript:alert(1)'), false)
  assert.equal(isSafeUrl('JAVASCRIPT:alert(document.cookie)'), false)
  assert.equal(isSafeUrl('javascript :alert(1)'), false)
  assert.equal(isSafeUrl('vbscript:msgbox(1)'), false)
  assert.equal(isSafeUrl('data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg=='), false)
  assert.equal(isSafeUrl(''), false)
})

test('sanitizeHtml elimina tags executáveis mantendo estrutura semântica', () => {
  const payload = '<p>Texto legítimo</p><script>alert("xss")</script><blockquote>Citação</blockquote>'
  const sanitized = sanitizeHtml(payload)
  assert.ok(!sanitized.includes('<script>'))
  assert.ok(!sanitized.includes('alert("xss")'))
  assert.ok(sanitized.includes('<p>Texto legítimo</p>') || sanitized.includes('Texto legítimo'))
  assert.ok(sanitized.includes('Citação'))
})

test('sanitizeHtml remove atributos de evento maliciosos (onload, onerror, onclick)', () => {
  const payload = '<img src="invalido.jpg" onerror="alert(1)"><span onclick="steal()">Texto</span>'
  const sanitized = sanitizeHtml(payload)
  assert.ok(!sanitized.includes('onerror'))
  assert.ok(!sanitized.includes('onclick'))
  assert.ok(!sanitized.includes('steal()'))
  assert.ok(sanitized.includes('Texto'))
})

test('sanitizeHtml neutraliza links com esquemas javascript: em atributos href', () => {
  const payload = '<a href="javascript:alert(1)">Clique aqui</a>'
  const sanitized = sanitizeHtml(payload)
  assert.ok(!sanitized.includes('javascript:alert(1)'))
  assert.ok(sanitized.includes('Clique aqui'))
})

test('sanitizeHtml preserva elementos de leitura ativa intactos', () => {
  const payload = `
    <p>
      Estudo com <mark class="study-highlight hl-yellow" data-highlight-id="1">termo destacado</mark>
      e <span class="study-occlusion" data-highlight-id="2">conteúdo oculto <button class="study-occlusion-btn">Revelar</button></span>
    </p>
  `
  const sanitized = sanitizeHtml(payload)
  assert.ok(sanitized.includes('study-highlight'))
  assert.ok(sanitized.includes('hl-yellow'))
  assert.ok(sanitized.includes('termo destacado'))
  assert.ok(sanitized.includes('study-occlusion'))
  assert.ok(sanitized.includes('study-occlusion-btn'))
  assert.ok(sanitized.includes('Revelar'))
})

test('renderMarkdown neutraliza URLs javascript e adiciona noopener noreferrer', () => {
  const markdown = '[Link Malicioso](javascript:alert(1))\n\n[Link Seguro](https://leitorum.com)'
  const html = renderMarkdown(markdown)

  assert.ok(!html.includes('href="javascript:alert(1)"'))
  assert.ok(html.includes('https://leitorum.com'))
  assert.ok(html.includes('rel="noopener noreferrer"'))
  assert.ok(html.includes('target="_blank"'))
})
