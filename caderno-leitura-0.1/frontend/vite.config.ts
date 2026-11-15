import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { readFileSync } from 'node:fs'
import { execSync } from 'node:child_process'

// Commit da interface (F0.10.03), comparado no painel de Sistema com o do servidor para avisar quando o serviço
// não foi reiniciado depois de um build. Sem git disponível, fica "desconhecido" e o painel não acusa divergência.
function buildCommit(): string {
  try {
    return execSync('git rev-parse --short=7 HEAD', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim() || 'desconhecido'
  } catch {
    return 'desconhecido'
  }
}

// Versão do app (F0.12.01): fonte única em caderno-leitura-0.1/VERSION (SemVer 2.0.0), lida também pelo backend.
function appVersion(): string {
  try {
    return readFileSync(new URL('../VERSION', import.meta.url), 'utf8').trim() || '0.0.0-desconhecida'
  } catch {
    return '0.0.0-desconhecida'
  }
}

// Tema e fonte aplicados antes da primeira pintura (F0.10.02): no build, o bootstrap sai como arquivo clássico e
// bloqueante (appearance-bootstrap.js), para a CSP não precisar de script inline; no dev, segue inline.
const MARKER = '<!-- appearance-bootstrap -->'
const BOOTSTRAP_FILE = 'appearance-bootstrap.js'

function readBootstrap(): string {
  const code = readFileSync(new URL('./src/appearance-bootstrap.js', import.meta.url), 'utf8')
  const catalogFile = readFileSync(new URL('./src/font-catalog.json', import.meta.url), 'utf8')
  const catalog = JSON.stringify(JSON.parse(catalogFile)).replaceAll('<', '\u003c')
  return [`window.cadernoFontCatalog=${catalog};`, code].join('\n')
}

export default defineConfig({
  define: {
    __BUILD_COMMIT__: JSON.stringify(buildCommit()),
    __APP_VERSION__: JSON.stringify(appVersion()),
    // F0.12.09: vue-i18n só com a Composition API, sem devtools em produção e com JIT (sem eval; CSP sem unsafe-eval).
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __INTLIFY_PROD_DEVTOOLS__: false,
    __INTLIFY_JIT_COMPILATION__: true,
    __INTLIFY_DROP_MESSAGE_COMPILER__: false,
  },
  plugins: [
    {
      name: 'appearance-before-paint',
      transformIndexHtml: {
        order: 'pre',
        handler(html, ctx) {
          if (!html.includes(MARKER)) {
            throw new Error('Falta o marcador appearance-bootstrap em index.html')
          }
          if (ctx?.server) {
            return html.replace(MARKER, () => `<script>${readBootstrap()}</script>`)
          }
          return html.replace(MARKER, () => `<script src="/${BOOTSTRAP_FILE}"></script>`)
        },
      },
      generateBundle() {
        this.emitFile({ type: 'asset', fileName: BOOTSTRAP_FILE, source: readBootstrap() })
      },
    },
    vue(),
  ],
})
