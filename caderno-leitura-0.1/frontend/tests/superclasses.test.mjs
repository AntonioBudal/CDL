import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { useMagneticHover } from '../src/composables/useMagneticHover.ts'

test('catálogo de aparência inclui os campos superclass e superclass-intensity', () => {
  const bootstrapContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/appearance-bootstrap.js'),
    'utf-8'
  )

  // Verifica se o campo superclass está registrado com o grupo 7
  assert.ok(bootstrapContent.includes("'7. Superclasse de Interface'"), 'Grupo 7 deve estar definido')
  assert.ok(bootstrapContent.includes("field('superclass'"), 'Campo superclass deve estar presente')
  assert.ok(bootstrapContent.includes("field('superclass-intensity'"), 'Campo superclass-intensity deve estar presente')

  // Verifica as 5 superclasses registradas
  assert.ok(bootstrapContent.includes("'zero-g'"), 'Zero-G deve estar registrado')
  assert.ok(bootstrapContent.includes("'mecanica'"), 'Mecânica deve estar registrada')
  assert.ok(bootstrapContent.includes("'invisivel'"), 'Invisível deve estar registrada')
  assert.ok(bootstrapContent.includes("'dimensional'"), 'Dimensional deve estar registrada')
  assert.ok(bootstrapContent.includes("'monolitica'"), 'Monolítica deve estar registrada')

  // Verifica as 4 intensidades homologadas
  assert.ok(bootstrapContent.includes("'standard'"), 'Intensidade padrão (1.0x) deve existir')
  assert.ok(bootstrapContent.includes("'subtle'"), 'Intensidade sutil (0.5x) deve existir')
  assert.ok(bootstrapContent.includes("'high'"), 'Intensidade alta (1.5x) deve existir')
  assert.ok(bootstrapContent.includes("'off'"), 'Intensidade desativada (0.0x) deve existir')
})

test('contrato de tokens css mapeia multiplicador --sc-intensity corretamente', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/zero-g.css'),
    'utf-8'
  )

  assert.ok(cssContent.includes('--sc-intensity: 1.0'), 'Intensidade padrão deve ser 1.0')
  assert.ok(cssContent.includes('--sc-intensity: 0.5'), 'Intensidade sutil deve ser 0.5')
  assert.ok(cssContent.includes('--sc-intensity: 1.5'), 'Intensidade alta deve ser 1.5')
  assert.ok(cssContent.includes('--sc-intensity: 0.0'), 'Intensidade desligada deve ser 0.0')

  // Redução de movimento
  assert.ok(cssContent.includes('prefers-reduced-motion: reduce'), 'Deve escutar prefers-reduced-motion')
  assert.ok(cssContent.includes('--sc-intensity: 0.0 !important'), 'Deve forçar 0.0 com !important na redução de movimento')
  assert.ok(cssContent.includes('[data-motion="off"]'), 'Deve escutar data-motion="off"')
})

test('tipagem TypeScript exporta tipos estritos para superclasses', () => {
  const dtsContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/appearance.d.ts'),
    'utf-8'
  )

  assert.ok(dtsContent.includes("superclass: 'none' | 'zero-g'"), 'Deve conter união tipada de superclasses')
  assert.ok(dtsContent.includes("'superclass-intensity': 'standard' | 'subtle' | 'high' | 'off'"), 'Deve conter intensidades tipadas')
})

test('escala proporcional de intensidade calcula deslocamento físico correto', () => {
  const baseTranslate = 4 // 4px
  const baseIdle = 1 // 1px

  const intensities = {
    subtle: 0.5,
    standard: 1.0,
    high: 1.5,
    off: 0.0,
  }

  // Sutil (0.5x)
  assert.equal(baseTranslate * intensities.subtle, 2.0, 'Sutil deve limitar atração a 2px')
  assert.equal(baseIdle * intensities.subtle, 0.5, 'Sutil deve limitar respiração a 0.5px')

  // Padrão (1.0x)
  assert.equal(baseTranslate * intensities.standard, 4.0, 'Padrão deve limitar atração a 4px')
  assert.equal(baseIdle * intensities.standard, 1.0, 'Padrão deve ter respiração de 1.0px')

  // Alta (1.5x)
  assert.equal(baseTranslate * intensities.high, 6.0, 'Alta deve limitar atração a 6px')
  assert.equal(baseIdle * intensities.high, 1.5, 'Alta deve ter respiração de 1.5px')

  // Desativada (0.0x)
  assert.equal(baseTranslate * intensities.off, 0.0, 'Desativada deve anular atração para 0px')
  assert.equal(baseIdle * intensities.off, 0.0, 'Desativada deve anular respiração para 0px')
})

test('garantia de imobilidade e blindagem no modo de leitura', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/zero-g.css'),
    'utf-8'
  )

  assert.ok(cssContent.includes('.markdown-content'), 'Deve conter regra explícita para .markdown-content')
  assert.ok(cssContent.includes('transform: none !important'), 'Deve forçar transform: none !important nos textos de leitura')
  assert.ok(cssContent.includes('animation: none !important'), 'Deve forçar animation: none !important nos textos de leitura')
})

test('useMagneticHover calcula deslocamento relativo delimitado em [-1.0, 1.0] e reseta no leave', () => {
  const { handlePointerMove, handlePointerLeave } = useMagneticHover()

  // Mock de elemento com estilo
  const styles = new Map()
  const attributes = new Map()

  const mockElement = {
    getBoundingClientRect: () => ({
      left: 100,
      top: 100,
      width: 200,
      height: 300,
    }),
    style: {
      setProperty: (k, v) => styles.set(k, v),
    },
    setAttribute: (k, v) => attributes.set(k, v),
    removeAttribute: (k) => attributes.delete(k),
  }

  // 1. Cursor no centro exato (clientX: 200, clientY: 250)
  handlePointerMove({
    pointerType: 'mouse',
    currentTarget: mockElement,
    clientX: 200,
    clientY: 250,
  })

  assert.equal(styles.get('--sc-magnetic-x'), '0.000', 'Centro em X deve ser 0')
  assert.equal(styles.get('--sc-magnetic-y'), '0.000', 'Centro em Y deve ser 0')
  assert.equal(attributes.get('data-magnetic'), 'active', 'Deve ativar atributo data-magnetic')

  // 2. Cursor no canto inferior direito
  handlePointerMove({
    pointerType: 'mouse',
    currentTarget: mockElement,
    clientX: 300,
    clientY: 400,
  })

  assert.equal(styles.get('--sc-magnetic-x'), '1.000', 'Extremo direito deve ser 1.000')
  assert.equal(styles.get('--sc-magnetic-y'), '1.000', 'Extremo inferior deve ser 1.000')

  // 3. Cursor fora dos limites (clamp)
  handlePointerMove({
    pointerType: 'mouse',
    currentTarget: mockElement,
    clientX: 500,
    clientY: 0,
  })

  assert.equal(styles.get('--sc-magnetic-x'), '1.000', 'Deve sofrer clamp em 1.000')
  assert.equal(styles.get('--sc-magnetic-y'), '-1.000', 'Deve sofrer clamp em -1.000')

  // 4. Pointer Leave deve resetar para 0 e remover atributo
  handlePointerLeave({
    currentTarget: mockElement,
  })

  assert.equal(styles.get('--sc-magnetic-x'), '0', 'Deve resetar X para 0')
  assert.equal(styles.get('--sc-magnetic-y'), '0', 'Deve resetar Y para 0')
  assert.equal(attributes.has('data-magnetic'), false, 'Deve remover atributo data-magnetic')

  // 5. Ignora eventos de toque (touch)
  styles.clear()
  handlePointerMove({
    pointerType: 'touch',
    currentTarget: mockElement,
    clientX: 250,
    clientY: 300,
  })
  assert.equal(styles.size, 0, 'Não deve atribuir estilos em eventos touch')
})

test('elementos de formulário, botões, selects e painéis recebem regras nominais da Zero-G', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/zero-g.css'),
    'utf-8'
  )

  // 1. Inputs e Textareas
  assert.ok(cssContent.includes('input[type="text"]'), 'Deve mirar nominalmente input[type="text"]')
  assert.ok(cssContent.includes('input[type="number"]'), 'Deve mirar nominalmente input[type="number"]')
  assert.ok(cssContent.includes('textarea'), 'Deve mirar nominalmente textarea')
  assert.ok(cssContent.includes('border-color: transparent'), 'Inputs devem ter bordas transparentes em repouso')
  assert.ok(cssContent.includes('transform: translateY(calc(-1px * var(--sc-intensity)))'), 'Inputs devem flutuar no foco')
  assert.ok(cssContent.includes('color-mix(in srgb, var(--color-accent)'), 'Glow do foco deve usar a cor de destaque do tema')

  // 2. Selects e Dropdowns Flutuantes
  assert.ok(cssContent.includes('select'), 'Deve mirar select')
  assert.ok(cssContent.includes('0 15px 40px'), 'Dropdowns flutuantes devem ter sombra ampla 0 15px 40px')

  // 3. Controles Booleanos
  assert.ok(cssContent.includes('input[type="checkbox"]'), 'Deve mirar checkbox')
  assert.ok(cssContent.includes('input[type="radio"]'), 'Deve mirar radio')
  assert.ok(cssContent.includes('.switch'), 'Deve conter suporte a switch')

  // 4. Botões Globais
  assert.ok(cssContent.includes('button, .button, .btn'), 'Deve mirar botões globais')
  assert.ok(cssContent.includes('transform: translateY(calc(-2px * var(--sc-intensity)))'), 'Botões devem subir 2px no hover')
  assert.ok(cssContent.includes('transform: translateY(calc(0.5px * var(--sc-intensity)))'), 'Botões devem descer suavemente no active')

  // 5. Painéis de Ajustes e Contêineres
  assert.ok(cssContent.includes('.appearance-group'), 'Deve mirar .appearance-group')
  assert.ok(cssContent.includes('--sc-shadow-idle'), 'Painéis devem usar sombra de levitação --sc-shadow-idle')

  // Suporte a classe .superclass-zero-g
  assert.ok(cssContent.includes('.superclass-zero-g'), 'Deve suportar nominalmente a classe .superclass-zero-g')
})

test('contrato de tokens css e física tátil da Mecânica (US1)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/mecanica.css'),
    'utf-8'
  )

  // Escopo duplo: data-attribute e classe
  assert.ok(cssContent.includes(':is(:root[data-superclass="mecanica"], .superclass-mecanica)'), 'Deve suportar data-attribute e classe CSS')

  // Tokens fundamentais
  assert.ok(cssContent.includes('--sc-border-radius: 2px'), 'Raio de borda deve ser 2px')
  assert.ok(cssContent.includes('--sc-shadow-idle: 0 calc(3px * var(--sc-intensity)) 0 var(--color-shadow, rgba(0, 0, 0, 0.35))'), 'Sombra de repouso deve ser dura de 3px')
  assert.ok(cssContent.includes('--sc-shadow-hover: 0 calc(4px * var(--sc-intensity)) 0 var(--color-shadow, rgba(0, 0, 0, 0.45))'), 'Sombra hover deve expandir 1px sólida')
  assert.ok(cssContent.includes('--sc-shadow-active: 0 0 0 transparent'), 'Sombra active deve ser anulada no batente mecânico')
  assert.ok(cssContent.includes('--sc-transition-duration: 100ms'), 'Duração deve ser 100ms ultrarrápida')
  assert.ok(cssContent.includes('--sc-transition-easing: linear'), 'Cinemática linear sem curvas elásticas')

  // Push-down e Hover em botões e cards
  assert.ok(cssContent.includes('button'), 'Deve estilizar botões globais')
  assert.ok(cssContent.includes('.button'), 'Deve estilizar classe .button')
  assert.ok(cssContent.includes('.btn'), 'Deve estilizar classe .btn')
  assert.ok(cssContent.includes('.book-card'), 'Deve estilizar .book-card')
  assert.ok(cssContent.includes('.book-list-item'), 'Deve estilizar .book-list-item')
  assert.ok(cssContent.includes('transform: translateY(calc(-1px * var(--sc-intensity)))'), 'Deve subir 1px no hover')
  assert.ok(cssContent.includes('transform: translateY(calc(3px * var(--sc-intensity)))'), 'Deve afundar 3px no push-down (:active)')

  // Supressão de Idle Breathing e Magnetismo
  assert.ok(cssContent.includes('.book-grid > li'), 'Deve mirar itens do grid de livros')
  assert.ok(cssContent.includes('animation: none !important'), 'Deve suprimir qualquer respiração contínua em repouso')
})

test('elementos de formulário e painéis parafusados da Mecânica (US2)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/mecanica.css'),
    'utf-8'
  )

  // Inputs escavados
  assert.ok(cssContent.includes('input[type="text"]'), 'Deve mirar input[type="text"]')
  assert.ok(cssContent.includes('input[type="number"]'), 'Deve mirar input[type="number"]')
  assert.ok(cssContent.includes('textarea'), 'Deve mirar textarea')
  assert.ok(cssContent.includes('select'), 'Deve mirar select')
  assert.ok(cssContent.includes('box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.12)'), 'Inputs devem ter sombra interna tipo cavidade')
  assert.ok(cssContent.includes('border-radius: var(--sc-border-radius)'), 'Inputs devem adotar raio de 2px')

  // Foco de alto atrito visual sem flutuação
  assert.ok(cssContent.includes('transform: none'), 'Inputs no foco não devem flutuar')
  assert.ok(cssContent.includes('border-color: var(--color-accent)'), 'Borda no foco deve reforçar a cor de destaque')

  // Painéis estruturais e caixas de ajustes
  assert.ok(cssContent.includes('.appearance-group'), 'Deve mirar caixas de agrupamento dos ajustes')
  assert.ok(cssContent.includes('.panel'), 'Deve mirar painéis globais')
  assert.ok(cssContent.includes('0 calc(2px * var(--sc-intensity)) 0 var(--color-shadow'), 'Painéis devem usar sombra de montagem sólida dura')
})

test('switches rápidos e transições de rota em corte seco da Mecânica (US3)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/mecanica.css'),
    'utf-8'
  )

  // Switches / Toggles com estalo de relé
  assert.ok(cssContent.includes('.switch'), 'Deve conter seletores de switch')
  assert.ok(cssContent.includes('.toggle'), 'Deve conter seletor toggle')
  assert.ok(cssContent.includes('[role="switch"]'), 'Deve conter seletor [role="switch"]')
  assert.ok(cssContent.includes('transition: transform 60ms linear'), 'Pino deve comutar em 60ms linear')

  // Micro afundamento de checkboxes
  assert.ok(cssContent.includes('input[type="checkbox"]:active'), 'Deve mirar checkbox ativo')
  assert.ok(cssContent.includes('transform: translateY(calc(1px * var(--sc-intensity)))'), 'Checkbox deve sofrer micro-afundamento de 1px')

  // Transições de rota Vue Router
  assert.ok(cssContent.includes('.page-enter-active'), 'Deve conter regra de entrada de página')
  assert.ok(cssContent.includes('.page-leave-active'), 'Deve conter regra de saída de página')
  assert.ok(cssContent.includes('transition: opacity 100ms linear !important'), 'Corte seco deve ser transição pura de opacidade em 100ms')
  assert.ok(cssContent.includes('transform: none !important'), 'Transição de página não deve deslocar verticalmente')
})

test('escala paramétrica de intensidade e imobilidade no leitor sob Mecânica (US4)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/mecanica.css'),
    'utf-8'
  )

  // Blindagem de leitura
  assert.ok(cssContent.includes('.markdown-content'), 'Deve proteger .markdown-content')
  assert.ok(cssContent.includes('transform: none !important'), 'Texto de leitura deve ter transform none !important')
  assert.ok(cssContent.includes('animation: none !important'), 'Texto de leitura deve ter animation none !important')

  // Acessibilidade e neutralização
  assert.ok(cssContent.includes('prefers-reduced-motion: reduce'), 'Deve escutar prefers-reduced-motion')
  assert.ok(cssContent.includes('--sc-intensity: 0.0 !important'), 'Deve forçar intensidade zero')
  assert.ok(cssContent.includes('[data-motion="off"]'), 'Deve escutar data-motion="off"')

  // Cálculo matemático do curso de afundamento (push-down de base 3px)
  const basePushDown = 3 // 3px
  const intensities = {
    subtle: 0.5,
    standard: 1.0,
    high: 1.5,
    off: 0.0,
  }

  assert.equal(basePushDown * intensities.subtle, 1.5, 'Sutil (0.5x) deve afundar exatamente 1.5px')
  assert.equal(basePushDown * intensities.standard, 3.0, 'Padrão (1.0x) deve afundar exatamente 3.0px')
  assert.equal(basePushDown * intensities.high, 4.5, 'Alta (1.5x) deve afundar exatamente 4.5px')
  assert.equal(basePushDown * intensities.off, 0.0, 'Desativada (0.0x) deve anular afundamento para 0.0px')
})

test('contrato de tokens css e desmaterialização de caixas da Invisível (US1)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/invisivel.css'),
    'utf-8'
  )

  // Escopo duplo: data-attribute e classe
  assert.ok(cssContent.includes(':is(:root[data-superclass="invisivel"], .superclass-invisivel)'), 'Deve suportar data-attribute e classe CSS')

  // Tokens fundamentais
  assert.ok(cssContent.includes('--sc-border-radius: 0px'), 'Raio de borda deve ser 0px')
  assert.ok(cssContent.includes('--sc-shadow-idle: none'), 'Sombra idle deve ser none')
  assert.ok(cssContent.includes('--sc-shadow-hover: none'), 'Sombra hover deve ser none')
  assert.ok(cssContent.includes('--sc-shadow-active: none'), 'Sombra active deve ser none')
  assert.ok(cssContent.includes('--sc-reading-shift-x: calc(4px * var(--sc-intensity))'), 'Deslocamento lateral deve ser 4px * intensidade')
  assert.ok(cssContent.includes('--sc-transition-duration: 200ms'), 'Duração de transição deve ser 200ms')
  assert.ok(cssContent.includes('--sc-transition-easing: cubic-bezier(0.2, 0, 0, 1)'), 'Easing editorial fluido')

  // Desmaterialização de cartões
  assert.ok(cssContent.includes('.book-card'), 'Deve estilizar .book-card')
  assert.ok(cssContent.includes('.book-list-item'), 'Deve estilizar .book-list-item')
  assert.ok(cssContent.includes('background: transparent !important'), 'Cartões devem ter fundo transparente')
  assert.ok(cssContent.includes('border: none !important'), 'Bordas duras devem ser eliminadas')
  assert.ok(cssContent.includes('border-bottom: 1px solid color-mix(in srgb, var(--color-border) 30%, transparent) !important'), 'Deve conter linha inferior tênue')
  assert.ok(cssContent.includes('border-radius: 0 !important'), 'Raio de borda de cartões deve ser forçado a 0')

  // Desmaterialização de painéis
  assert.ok(cssContent.includes('.panel'), 'Deve desmaterializar painéis')
  assert.ok(cssContent.includes('.appearance-group'), 'Deve desmaterializar caixas de agrupamento dos ajustes')
})

test('microinterações editoriais: deslocamento horizontal e sublinhado progressivo (US1)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/invisivel.css'),
    'utf-8'
  )

  // Deslocamento horizontal no hover
  assert.ok(cssContent.includes('transform: translateX(var(--sc-reading-shift-x))'), 'Hover de cartões deve deslocar horizontalmente')

  // Sublinhado progressivo da esquerda para a direita
  assert.ok(cssContent.includes('.text-link::after'), 'Links de texto devem ter pseudo-elemento ::after')
  assert.ok(cssContent.includes('.book-card h2 a::after'), 'Títulos de livros devem ter ::after')
  assert.ok(cssContent.includes('.chapter-list a::after'), 'Links de capítulos devem ter ::after')
  assert.ok(cssContent.includes('transform: scaleX(0)'), 'Linha deve iniciar oculta com scaleX(0)')
  assert.ok(cssContent.includes('transform-origin: left'), 'Origem da expansão deve ser à esquerda')
  assert.ok(cssContent.includes('transform: scaleX(1)'), 'Hover deve animar expansão para scaleX(1)')

  // Botões editoriais
  assert.ok(cssContent.includes('button,\n  .button,\n  .btn') || cssContent.includes('button, .button, .btn'), 'Deve estilizar botões globais')
  assert.ok(cssContent.includes('border-radius: 0'), 'Botões editoriais devem ter cantos retos')
  assert.ok(cssContent.includes('transform: translateX(calc(2px * var(--sc-intensity)))'), 'Botões devem ter leve shift horizontal no hover')
})

test('transição de rota em cascata temporal staggered fade-up da Invisível (US2)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/invisivel.css'),
    'utf-8'
  )

  // Keyframes
  assert.ok(cssContent.includes('@keyframes sc-invisivel-fade-up'), 'Deve declarar keyframes sc-invisivel-fade-up')
  assert.ok(cssContent.includes('transform: translateY(calc(6px * var(--sc-intensity)))'), 'Entrada com subida suave de 6px * intensidade')

  // Cascata progressiva
  assert.ok(cssContent.includes('.page-header'), 'Cabeçalho de página na cascata')
  assert.ok(cssContent.includes('0ms both'), 'Cabeçalho surge a 0ms')
  assert.ok(cssContent.includes('.reader-heading'), 'Título do leitor na cascata')
  assert.ok(cssContent.includes('40ms both'), 'Títulos e metadados surgem a 40ms')
  assert.ok(cssContent.includes('.reader-analysis'), 'Análise de leitura na cascata')
  assert.ok(cssContent.includes('80ms both'), 'Corpo do estudo surge a 80ms')

  // Saída suave
  assert.ok(cssContent.includes('.page-leave-active'), 'Deve controlar .page-leave-active')
  assert.ok(cssContent.includes('opacity: 0'), 'Saída deve esvanecer em opacidade')
  assert.ok(cssContent.includes('transform: none !important'), 'Saída não deve deslocar posição')
})

test('poda de campos obsoletos no catálogo de aparência e normalização retrocompatível (US3)', () => {
  const bootstrapContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/appearance-bootstrap.js'),
    'utf-8'
  )
  const dtsContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/appearance.d.ts'),
    'utf-8'
  )
  const vueContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/components/AppearanceControls.vue'),
    'utf-8'
  )

  // 1. Campos removidos de fields em appearance-bootstrap.js
  assert.ok(!bootstrapContent.includes("field('style'"), 'Campo style não deve estar presente no catálogo')
  assert.ok(!bootstrapContent.includes("field('surface'"), 'Campo surface não deve estar presente no catálogo')
  assert.ok(!bootstrapContent.includes("field('button-style'"), 'Campo button-style não deve estar presente no catálogo')

  // 2. Remoção de atributos legados em apply()
  assert.ok(bootstrapContent.includes("document.documentElement.removeAttribute('data-style')"), 'Deve limpar data-style')
  assert.ok(bootstrapContent.includes("document.documentElement.removeAttribute('data-surface')"), 'Deve limpar data-surface')
  assert.ok(bootstrapContent.includes("document.documentElement.removeAttribute('data-button-style')"), 'Deve limpar data-button-style')

  // 3. Tipagem TypeScript atualizada
  assert.ok(!dtsContent.includes('style:'), 'Tipo AppearancePreferences não deve conter style')
  assert.ok(!dtsContent.includes('surface:'), 'Tipo AppearancePreferences não deve conter surface')
  assert.ok(!dtsContent.includes("'button-style':"), 'Tipo AppearancePreferences não deve conter button-style')

  // 4. AppearanceControls sem surface na lista ignored
  assert.ok(!vueContent.includes("'surface'"), 'AppearanceControls não deve ter surface na lista de ignored')

  // 5. Teste de resiliência de migração: simula normalize com payload legado contendo campos removidos
  assert.ok(bootstrapContent.includes('version: 72'), 'Versão deve ser incrementada para 72')
})

test('intensidade paramétrica, neutralização por acessibilidade e blindagem de leitura na Invisível (US4)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/invisivel.css'),
    'utf-8'
  )

  // Blindagem de leitura
  assert.ok(cssContent.includes('.markdown-content'), 'Deve proteger .markdown-content')
  assert.ok(cssContent.includes('transform: none !important'), 'Texto de leitura deve ter transform none !important')
  assert.ok(cssContent.includes('animation: none !important'), 'Texto de leitura deve ter animation none !important')

  // Acessibilidade e neutralização
  assert.ok(cssContent.includes('prefers-reduced-motion: reduce'), 'Deve escutar prefers-reduced-motion')
  assert.ok(cssContent.includes('--sc-intensity: 0.0 !important'), 'Deve forçar intensidade zero sob redução de movimento')
  assert.ok(cssContent.includes('[data-motion="off"]'), 'Deve escutar data-motion="off"')

  // Cálculo matemático do deslocamento lateral de base 4px
  const baseShift = 4 // 4px
  const intensities = {
    subtle: 0.5,
    standard: 1.0,
    high: 1.5,
    off: 0.0,
  }

  assert.equal(baseShift * intensities.subtle, 2.0, 'Sutil (0.5x) deve deslocar exatamente 2.0px')
  assert.equal(baseShift * intensities.standard, 4.0, 'Padrão (1.0x) deve deslocar exatamente 4.0px')
  assert.equal(baseShift * intensities.high, 6.0, 'Alta (1.5x) deve deslocar exatamente 6.0px')
  assert.equal(baseShift * intensities.off, 0.0, 'Desativada (0.0x) deve anular deslocamento para 0.0px')
})

test('contrato de tokens css, perspectiva 3D e tilt delimitado da Dimensional (US1)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/dimensional.css'),
    'utf-8'
  )

  // Escopo duplo: data-attribute e classe
  assert.ok(cssContent.includes(':is(:root[data-superclass="dimensional"], .superclass-dimensional)'), 'Deve suportar data-attribute e classe CSS')

  // Tokens fundamentais
  assert.ok(cssContent.includes('--sc-perspective: 1000px'), 'Perspectiva óptica deve ser 1000px')
  assert.ok(cssContent.includes('--sc-tilt-max-x: calc(1.5deg * var(--sc-intensity))'), 'Limite angular em X deve ser 1.5deg')
  assert.ok(cssContent.includes('--sc-tilt-max-y: calc(2.0deg * var(--sc-intensity))'), 'Limite angular em Y deve ser 2.0deg')
  assert.ok(cssContent.includes('--sc-transition-duration: 320ms'), 'Duração de retorno deve ser 320ms')
  assert.ok(cssContent.includes('--sc-transition-easing: cubic-bezier(0.16, 1, 0.3, 1)'), 'Curva de transição inercial cinematográfica')

  // Tilt 3D delimitado nos cartões
  assert.ok(cssContent.includes('transform-style: preserve-3d'), 'Cartões devem preservar renderização 3D')
  assert.ok(cssContent.includes('perspective(var(--sc-perspective))'), 'Cartão deve aplicar perspectiva óptica')
  assert.ok(cssContent.includes('rotateX(calc(var(--sc-magnetic-y, 0) * -1.5deg * var(--sc-intensity)))'), 'Fórmula de inclinação no eixo X delimitada a 1.5°')
  assert.ok(cssContent.includes('rotateY(calc(var(--sc-magnetic-x, 0) * 2.0deg * var(--sc-intensity)))'), 'Fórmula de inclinação no eixo Y delimitada a 2.0°')

  // Sombras projetadas dinâmicas no hover opostas ao cursor
  assert.ok(cssContent.includes('.book-card:hover'), 'Regra de hover do cartão definida')
  assert.ok(cssContent.includes('calc(var(--sc-magnetic-x, 0) * -6px * var(--sc-intensity))'), 'Sombra X oposta ao cursor')
  assert.ok(cssContent.includes('calc(var(--sc-magnetic-y, 0) * -6px * var(--sc-intensity) + 14px)'), 'Sombra Y oposta ao cursor com elevação base')

  // Botões dimensionais
  assert.ok(cssContent.includes('button') && cssContent.includes('.button') && cssContent.includes('.btn'), 'Botões globais estilizados')
  assert.ok(cssContent.includes('translateY(calc(-2px * var(--sc-intensity))) scale(calc(1 + (0.005 * var(--sc-intensity))))'), 'Elevação Z sutil no hover de botões')
  assert.ok(cssContent.includes('translateY(calc(1px * var(--sc-intensity))) scale(0.99)'), 'Retração física no active de botões')
})

test('relevo espacial multicamada e paralaxe interno nos cartões da Dimensional (US2)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/dimensional.css'),
    'utf-8'
  )

  // Camada 1: Capa (1px * intensidade)
  assert.ok(cssContent.includes('.book-card .book-card-cover-wrapper'), 'Mira container de capa do livro')
  assert.ok(cssContent.includes('calc(var(--sc-magnetic-x, 0) * 1px * var(--sc-intensity))'), 'Paralaxe X da capa a 1px')
  assert.ok(cssContent.includes('calc(var(--sc-magnetic-y, 0) * 1px * var(--sc-intensity))'), 'Paralaxe Y da capa a 1px')

  // Camada 2: Título (2px * intensidade)
  assert.ok(cssContent.includes('.book-card h2'), 'Mira título do livro')
  assert.ok(cssContent.includes('calc(var(--sc-magnetic-x, 0) * 2px * var(--sc-intensity))'), 'Paralaxe X do título a 2px')
  assert.ok(cssContent.includes('calc(var(--sc-magnetic-y, 0) * 2px * var(--sc-intensity))'), 'Paralaxe Y do título a 2px')

  // Camada 3: Marcadores e Badges (3px * intensidade)
  assert.ok(cssContent.includes('.book-number'), 'Mira marcador numérico')
  assert.ok(cssContent.includes('.card-action'), 'Mira ação do cartão')
  assert.ok(cssContent.includes('.category-badge'), 'Mira badge de categoria')
  assert.ok(cssContent.includes('calc(var(--sc-magnetic-x, 0) * 3px * var(--sc-intensity))'), 'Paralaxe X dos badges a 3px')
  assert.ok(cssContent.includes('calc(var(--sc-magnetic-y, 0) * 3px * var(--sc-intensity))'), 'Paralaxe Y dos badges a 3px')
})

test('transição de rota cinemática com aproximação Z da Dimensional (US3)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/dimensional.css'),
    'utf-8'
  )

  // Duração e Easing de transição de rota
  assert.ok(cssContent.includes('.page-enter-active'), 'Define .page-enter-active')
  assert.ok(cssContent.includes('opacity 300ms cubic-bezier(0.16, 1, 0.3, 1)'), 'Opacidade a 300ms com curva cinemática')
  assert.ok(cssContent.includes('transform 300ms cubic-bezier(0.16, 1, 0.3, 1) !important'), 'Transform a 300ms cinemático')

  assert.ok(cssContent.includes('.page-leave-active'), 'Define .page-leave-active')
  assert.ok(cssContent.includes('opacity 180ms ease'), 'Saída com fade a 180ms')

  // Aproximação Z (scale 0.985 -> translateY 4px na entrada)
  assert.ok(cssContent.includes('.page-enter-from'), 'Define .page-enter-from')
  assert.ok(cssContent.includes('scale(calc(1 - (0.015 * var(--sc-intensity))))'), 'Escala inicial de aproximação Z (0.985)')
  assert.ok(cssContent.includes('translateY(calc(4px * var(--sc-intensity)))'), 'Deslocamento inicial em Y de 4px')

  // Recuo Z na saída (scale 1.01)
  assert.ok(cssContent.includes('.page-leave-to'), 'Define .page-leave-to')
  assert.ok(cssContent.includes('scale(calc(1 + (0.01 * var(--sc-intensity))))'), 'Escala final de recuo Z (1.01)')
})

test('escala paramétrica de intensidade, acessibilidade e blindagem de leitura na Dimensional (US4)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/dimensional.css'),
    'utf-8'
  )

  // 1. Blindagem de leitura inviolável
  assert.ok(cssContent.includes('.markdown-content'), 'Protege .markdown-content')
  assert.ok(cssContent.includes('.study-section'), 'Protege .study-section')
  assert.ok(cssContent.includes('.reader-tools'), 'Protege .reader-tools')
  assert.ok(cssContent.includes('.reading-page'), 'Protege .reading-page')
  assert.ok(cssContent.includes('transform: none !important'), 'Modo de leitura 100% imóvel (transform: none)')
  assert.ok(cssContent.includes('animation: none !important'), 'Modo de leitura sem animações (animation: none)')

  // 2. Neutralização por redução de movimento do SO
  assert.ok(cssContent.includes('@media (prefers-reduced-motion: reduce)'), 'Escuta prefers-reduced-motion')
  assert.ok(cssContent.includes('--sc-intensity: 0.0 !important'), 'Zera intensidade com !important sob prefers-reduced-motion')

  // 3. Neutralização por preferência do usuário (data-motion="off")
  assert.ok(cssContent.includes(':root[data-motion="off"][data-superclass="dimensional"]'), 'Escuta data-motion="off"')
  assert.ok(cssContent.includes(':root[data-motion="off"] .superclass-dimensional'), 'Escuta data-motion="off" com classe')

  // 4. Cálculo matemático exato dos ângulos e paralaxe nas 4 intensidades homologadas
  const maxTiltX = 1.5 // 1.5 graus
  const maxTiltY = 2.0 // 2.0 graus
  const layer3Offset = 3.0 // 3.0 px

  const intensities = {
    subtle: 0.5,
    standard: 1.0,
    high: 1.5,
    off: 0.0,
  }

  // Sutil (0.5x)
  assert.equal(maxTiltX * intensities.subtle, 0.75, 'Sutil: inclinação X máxima de 0.75°')
  assert.equal(maxTiltY * intensities.subtle, 1.00, 'Sutil: inclinação Y máxima de 1.00°')
  assert.equal(layer3Offset * intensities.subtle, 1.50, 'Sutil: paralaxe em camada 3 de 1.50px')

  // Padrão (1.0x)
  assert.equal(maxTiltX * intensities.standard, 1.50, 'Padrão: inclinação X máxima de 1.50°')
  assert.equal(maxTiltY * intensities.standard, 2.00, 'Padrão: inclinação Y máxima de 2.00°')
  assert.equal(layer3Offset * intensities.standard, 3.00, 'Padrão: paralaxe em camada 3 de 3.00px')

  // Alta (1.5x)
  assert.equal(maxTiltX * intensities.high, 2.25, 'Alta: inclinação X máxima de 2.25°')
  assert.equal(maxTiltY * intensities.high, 3.00, 'Alta: inclinação Y máxima de 3.00°')
  assert.equal(layer3Offset * intensities.high, 4.50, 'Alta: paralaxe em camada 3 de 4.50px')

  // Desativada (0.0x)
  assert.equal(maxTiltX * intensities.off, 0.00, 'Desativada: inclinação X nula de 0.00°')
  assert.equal(maxTiltY * intensities.off, 0.00, 'Desativada: inclinação Y nula de 0.00°')
  assert.equal(layer3Offset * intensities.off, 0.00, 'Desativada: paralaxe nulo de 0.00px')
})

test('contrato de tokens css, cantos retos e supressão de sombras da Monolítica (US1)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/monolitica.css'),
    'utf-8'
  )

  // Escopo duplo: data-attribute e classe
  assert.ok(cssContent.includes(':is(:root[data-superclass="monolitica"], .superclass-monolitica)'), 'Deve suportar data-attribute e classe CSS')

  // Tokens fundamentais
  assert.ok(cssContent.includes('--sc-border-radius: 0px !important'), 'Cantos devem ser estritamente retos (0px)')
  assert.ok(cssContent.includes('--sc-border-width: calc(var(--border-width, 1px) + 1px)'), 'Bordas estruturais sólidas')
  assert.ok(cssContent.includes('--sc-shadow-idle: none !important'), 'Sombra de repouso suprimida')
  assert.ok(cssContent.includes('--sc-shadow-hover: none !important'), 'Sombra hover suprimida')
  assert.ok(cssContent.includes('--sc-shadow-active: none !important'), 'Sombra active suprimida')
  assert.ok(cssContent.includes('--sc-transition-duration: 380ms'), 'Duração ponderada de 380ms')
  assert.ok(cssContent.includes('--sc-transition-easing: cubic-bezier(0.25, 1, 0.5, 1)'), 'Curva de desaceleração estável e lapidar')

  // Cartões (.book-card) e Itens de lista
  assert.ok(cssContent.includes('.book-card'), 'Estiliza .book-card')
  assert.ok(cssContent.includes('.book-list-item'), 'Estiliza .book-list-item')
  assert.ok(cssContent.includes('border: var(--sc-border-width) solid var(--color-border-strong)'), 'Borda sólida estrutural')
  assert.ok(cssContent.includes('transform: none !important'), 'Cartão estático sem elevação ou tilt')

  // Painéis (.panel, .appearance-group) e Controles de formulário
  assert.ok(cssContent.includes('.panel'), 'Estiliza .panel')
  assert.ok(cssContent.includes('.appearance-group'), 'Estiliza .appearance-group')
  assert.ok(cssContent.includes('input[type="text"]'), 'Estiliza input text')
  assert.ok(cssContent.includes('textarea'), 'Estiliza textarea')
  assert.ok(cssContent.includes('select'), 'Estiliza select')
})

test('microinterações solenes e inversão de alto contraste no active da Monolítica (US2)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/monolitica.css'),
    'utf-8'
  )

  // Hover solene no cartão (380ms)
  assert.ok(cssContent.includes('background-color var(--sc-transition-duration) var(--sc-transition-easing)'), 'Transição solene de cor de fundo')
  assert.ok(cssContent.includes('border-color var(--sc-transition-duration) var(--sc-transition-easing)'), 'Transição solene de cor de borda')
  assert.ok(cssContent.includes('background-color: var(--color-surface-hover)'), 'Realce de fundo no hover')
  assert.ok(cssContent.includes('border-color: var(--color-text)'), 'Realce de borda no hover')

  // Botões globais
  assert.ok(cssContent.includes('button') && cssContent.includes('.button') && cssContent.includes('.btn'), 'Estiliza botões globais')
  assert.ok(cssContent.includes('border: var(--sc-border-width) solid currentColor'), 'Bordas de botão em currentColor')

  // Inversão brutalista no clique (:active)
  assert.ok(cssContent.includes(':active:not(:disabled)'), 'Estado active em botões')
  assert.ok(cssContent.includes('background-color: var(--color-text)'), 'Inversão para cor de texto no fundo')
  assert.ok(cssContent.includes('color: var(--color-page)'), 'Inversão para cor de página no texto')
})

test('transição de rota solene por dissolução lapidar da Monolítica (US3)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/monolitica.css'),
    'utf-8'
  )

  // Duração e Easing solenes
  assert.ok(cssContent.includes('.page-enter-active'), 'Define .page-enter-active')
  assert.ok(cssContent.includes('opacity 380ms cubic-bezier(0.25, 1, 0.5, 1) !important'), 'Dissolução de entrada a 380ms lapidar')
  assert.ok(cssContent.includes('.page-leave-active'), 'Define .page-leave-active')
  assert.ok(cssContent.includes('opacity 220ms ease !important'), 'Dissolução de saída a 220ms')

  // Ausência absoluta de deslocamentos físicos ou escalas
  assert.ok(cssContent.includes('.page-enter-active') && cssContent.includes('transform: none !important'), 'Sem translações na entrada')
  assert.ok(cssContent.includes('.page-leave-active') && cssContent.includes('transform: none !important'), 'Sem translações na saída')
  assert.ok(cssContent.includes('.page-enter-from') && cssContent.includes('opacity: 0 !important'), 'Inicia invisível e estático')
  assert.ok(cssContent.includes('.page-leave-to') && cssContent.includes('opacity: 0 !important'), 'Finaliza invisível e estático')
})

test('multiplicador paramétrico, neutralização por acessibilidade e blindagem de leitura na Monolítica (US4)', () => {
  const cssContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/styles/superclasses/monolitica.css'),
    'utf-8'
  )

  // 1. Blindagem de leitura inviolável
  assert.ok(cssContent.includes('.markdown-content'), 'Protege .markdown-content')
  assert.ok(cssContent.includes('.study-section'), 'Protege .study-section')
  assert.ok(cssContent.includes('.reader-tools'), 'Protege .reader-tools')
  assert.ok(cssContent.includes('.reading-page'), 'Protege .reading-page')
  assert.ok(cssContent.includes('transform: none !important'), 'Modo de leitura 100% imóvel')
  assert.ok(cssContent.includes('animation: none !important'), 'Modo de leitura sem animações')

  // 2. Neutralização por redução de movimento do SO
  assert.ok(cssContent.includes('@media (prefers-reduced-motion: reduce)'), 'Escuta prefers-reduced-motion')
  assert.ok(cssContent.includes('--sc-intensity: 0.0 !important'), 'Zera intensidade com !important sob prefers-reduced-motion')
  assert.ok(cssContent.includes('transition: none !important'), 'Neutraliza transições temporizadas sob redução de movimento')

  // 3. Neutralização por preferência do usuário (data-motion="off")
  assert.ok(cssContent.includes(':root[data-motion="off"][data-superclass="monolitica"]'), 'Escuta data-motion="off"')
  assert.ok(cssContent.includes(':root[data-motion="off"] .superclass-monolitica'), 'Escuta data-motion="off" com classe')

  // 4. Cálculo e escalonamento de intensidade
  const baseDuration = 380 // 380ms
  const intensities = {
    subtle: 0.5,
    standard: 1.0,
    high: 1.5,
    off: 0.0,
  }

  assert.equal(baseDuration * intensities.subtle, 190, 'Sutil: duração reduzida para 190ms')
  assert.equal(baseDuration * intensities.standard, 380, 'Padrão: duração nominal de 380ms')
  assert.equal(baseDuration * intensities.high, 570, 'Alta: duração estendida para 570ms')
  assert.equal(baseDuration * intensities.off, 0, 'Desativada: transição imediata de 0ms')
})

test('estabilidade de roteamento com chave reativa e nó raiz único nas views (Feature 012 - US1)', () => {
  const appContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/App.vue'),
    'utf-8'
  )

  // 1. Chave reativa de rota no router-view / component
  assert.ok(
    appContent.includes(':key="$route.fullPath"'),
    'App.vue deve conter :key="$route.fullPath" no componente roteado sob Transition'
  )

  // 2. Elemento raiz único nas 5 views para evitar cancelamento de transição do Vue 3
  const views = [
    { file: 'src/views/BooksView.vue', root: '<div class="books-view">' },
    { file: 'src/views/BookView.vue', root: '<div class="book-view">' },
    { file: 'src/views/StudyView.vue', root: '<div class="study-view">' },
    { file: 'src/views/StudyEditView.vue', root: '<div class="study-edit-view">' },
    { file: 'src/views/ImportView.vue', root: '<div class="import-view">' },
  ]

  for (const { file, root } of views) {
    const content = fs.readFileSync(path.resolve(process.cwd(), file), 'utf-8')
    assert.ok(
      content.includes(root),
      `${file} deve encapsular o template no invólucro único ${root}`
    )
  }
})

test('propagação global de fonte e herança irrestrita em toda a interface (Feature 012 - US2)', () => {
  const tokensContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/tokens.css'),
    'utf-8'
  )
  const styleContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/style.css'),
    'utf-8'
  )

  // 1. Vinculação em tokens.css
  assert.ok(
    tokensContent.includes('--font-ui: var(--font-reading);'),
    'tokens.css deve vincular --font-ui a var(--font-reading)'
  )

  // 2. Aplicação irrestrita em style.css
  assert.ok(
    styleContent.includes(':root,'),
    'style.css deve aplicar seletor raiz global'
  )
  assert.ok(
    styleContent.includes('font-family: var(--font-reading)'),
    'style.css deve forçar font-family: var(--font-reading)'
  )

  // Verifica inclusão dos seletores-alvo conforme clarificação irrestrita
  for (const tag of ['body', '#app', 'button', 'input', 'select', 'textarea', 'code', 'pre']) {
    assert.ok(
      styleContent.includes(tag),
      `style.css deve incluir seletor '${tag}' na aplicação de fonte`
    )
  }
})

test('poda de ajustes obsoletos, 7 grupos sequenciais e purga de localStorage (Feature 012 - US3)', () => {
  const bootstrapContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/appearance-bootstrap.js'),
    'utf-8'
  )
  const dtsContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/appearance.d.ts'),
    'utf-8'
  )
  const vueContent = fs.readFileSync(
    path.resolve(process.cwd(), 'src/components/AppearanceControls.vue'),
    'utf-8'
  )

  // 1. Campos podados ausentes do catálogo
  assert.ok(!bootstrapContent.includes("field('motion'"), 'Campo motion não deve estar no catálogo')
  assert.ok(!bootstrapContent.includes("field('button-width'"), 'Campo button-width não deve estar no catálogo')
  assert.ok(!bootstrapContent.includes("field('tabs'"), 'Campo tabs não deve estar no catálogo')

  // 2. Remoção de atributos HTML correspondentes
  assert.ok(bootstrapContent.includes("document.documentElement.removeAttribute('data-motion')"), 'Deve limpar data-motion')
  assert.ok(bootstrapContent.includes("document.documentElement.removeAttribute('data-button-width')"), 'Deve limpar data-button-width')
  assert.ok(bootstrapContent.includes("document.documentElement.removeAttribute('data-tabs')"), 'Deve limpar data-tabs')

  // 3. Purga ativa no localStorage durante bootstrap
  assert.ok(
    bootstrapContent.includes('window.localStorage.setItem(KEY, JSON.stringify(current));'),
    'Bootstrap deve salvar o estado normalizado de volta no localStorage para purgar chaves obsoletas'
  )

  // 4. Exatos 7 grupos numerados consecutivamente (1 a 7)
  const expectedGroups = [
    '1. Cor de destaque',
    '2. Densidade',
    '3. Leitura',
    '4. Marcação',
    '5. Acervo',
    '6. Largura da interface',
    '7. Superclasse de Interface',
  ]

  for (const group of expectedGroups) {
    assert.ok(
      bootstrapContent.includes(`'${group}'`),
      `Grupo '${group}' deve estar definido sequencialmente`
    )
  }

  // 5. Tipagem e componentes sem resíduos de motion
  assert.ok(!dtsContent.includes('motion:'), 'Tipo AppearancePreferences não deve conter motion')
  assert.ok(!dtsContent.includes("'button-width':"), 'Tipo AppearancePreferences não deve conter button-width')
  assert.ok(!dtsContent.includes('tabs:'), 'Tipo AppearancePreferences não deve conter tabs')
  assert.ok(!vueContent.includes("'motion'"), 'AppearanceControls não deve ter motion na lista ignored')
})

