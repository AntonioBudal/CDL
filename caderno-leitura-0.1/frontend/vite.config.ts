import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { readFileSync } from 'node:fs'

export default defineConfig({
  plugins: [
  {
    name: 'appearance-before-paint',
    transformIndexHtml: {
      order: 'pre',

      handler(html) {
        const marker = '<!-- appearance-bootstrap -->'

        if (!html.includes(marker)) {
          throw new Error(
            'Falta o marcador appearance-bootstrap em index.html'
          )
        }

        const code = readFileSync(
          new URL('./src/appearance-bootstrap.js', import.meta.url),
          'utf8'
        )

        const catalogFile = readFileSync(
  new URL('./src/font-catalog.json', import.meta.url),
  'utf8'
)

const catalog = JSON.stringify(JSON.parse(catalogFile))
  .replaceAll('<', '\\u003c')

return html.replace(
  marker,
  () => `<script>window.cadernoFontCatalog=${catalog};\n${code}</script>`
)
      },
    },
  },
  vue(),
],
})
