import test from 'node:test'
import assert from 'node:assert/strict'
import { renderMarkdown } from '../src/services/markdown.ts'

test('renderiza parágrafos, listas, ênfase, negrito e links', () => {
  const html = renderMarkdown('Um **resumo** com *ênfase*.\n\nOutro parágrafo.\n\n- Conceito A\n- Conceito B\n\n[Fonte](https://example.org)')
  assert.match(html, /<p>Um <strong>resumo<\/strong> com <em>ênfase<\/em>\.<\/p>/)
  assert.match(html, /<p>Outro parágrafo\.<\/p>/)
  assert.match(html, /<ul>\s*<li>Conceito A<\/li>\s*<li>Conceito B<\/li>\s*<\/ul>/)
  assert.match(html, /href="https:\/\/example.org"/)
  assert.match(html, /target="_blank" rel="noopener noreferrer"/)
})

test('HTML e eventos ficam como texto; scripts e imagens não viram elementos', () => {
  const html = renderMarkdown('<script>alert(1)</script>\n\n<img src=x onerror=alert(1)>\n\n<svg onload=alert(1)>\n\n![Imagem](https://example.org/image.png)')
  assert.doesNotMatch(html, /<(script|img|svg)\b/i)
  assert.match(html, /&lt;script&gt;/)
  assert.match(html, /&lt;img/)
})

for (const url of ['javascript:alert(1)', 'JaVaScRiPt:alert(1)', 'javascript&#58;alert(1)', 'vbscript:msgbox(1)', 'data:text/html;base64,PHNjcmlwdD4=', 'file:///C:/secret.txt']) {
  test(`não cria link ativo com protocolo perigoso: ${url.split(':')[0]}`, () => {
    const html = renderMarkdown(`[Clique](${url})`)
    assert.doesNotMatch(html, /<a\b/i)
  })
}

test('código cercado permanece literal, sem executar nem interpretar HTML', () => {
  const html = renderMarkdown('```html\n<script>alert(1)</script>\n```')
  assert.match(html, /<pre><code/)
  assert.match(html, /&lt;script&gt;/)
  assert.doesNotMatch(html, /<script\b/)
})
