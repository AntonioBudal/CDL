# Pesquisa Técnica e Arquitetura: Página Inicial sem Login (SEO) — Manifesto do Leitor Reflexivo

**Feature**: `074-manifesto-leitor-reflexivo`  
**Data**: 2026-10-11  
**Status**: Concluído (Phase 0)  

---

## 1. Indexabilidade Orgânica em SPA e Conteúdo Vital

### Questão
O Leitorum é uma Single Page Application (Vue 3 + Vite). Por padrão, `index.html` contém apenas `<div id="app"></div>` e metatags no `<head>`. Rastreamentos de mecanismos de busca que penalizam ou atrasam a execução de scripts em JavaScript pesado precisam encontrar o conteúdo vital (título, manifesto, trecho literário e dimensões) no próprio HTML inicial.

### Decisão
Injetar no `index.html`, dentro de `<div id="app">`, uma versão estática acessível e semântica do manifesto (h1, subtítulo, citação de Machado de Assis, as 4 perguntas do método e princípios). Quando a aplicação Vue monta no navegador (`app.mount('#app')`), o Vue substitui naturalmente o conteúdo do `#app` pela aplicação reativa completa.

### Racional
- Zero dependências de build complexas ou ferramentas de SSR de terceiros.
- Mecanismos de busca tradicionais, bots de redes sociais e navegadores em modo texto (ex.: lynx, curl) recebem imediatamente o conteúdo vital indexável.
- Nenhum conflito de hidratação no cliente, pois o Vue 3 em modo cliente limpa o nó interno ao montar o componente raiz.
- Previne qualquer penalização de SEO por página em branco no primeiro byte.

### Alternativas Consideradas
- *Server-Side Rendering (SSR) via Nuxt ou Node server*: Rejeitado por violar o Princípio III da Constituição (servidor único FastAPI local com distribuição estática leve via `iniciar.py`).
- *Prerender plugin no Vite*: Rejeitado para evitar complexidade adicional de tooling e headless browser no ambiente Windows local.

---

## 2. Acessibilidade Visual e Conformidade WCAG AAA (7:1) nos 10 Temas

### Questão
A especificação estabelece contraste de pelo menos 7:1 (WCAG AAA) para textos de leitura contínua. A auditoria de contraste revelou que no tema `solario`, o texto `--color-text` (`#3F5962`) sobre `--color-page` (`#FDF6E3`) tem razão de 6,9:1 e sobre `--color-surface` (`#EEE8D5`) atinge apenas 6,1:1. Além disso, `--color-muted` fica abaixo de 7:1 em múltiplos temas.

### Decisão
1. **Regra de Tipografia Editorial**: Todo texto de leitura contínua da landing page (título, subtítulo, manifesto, trecho de Brás Cubas, notas analíticas e princípios) utilizará a variável `--color-text` e fundos em `--color-page` ou `--color-surface`. A variável `--color-muted` fica restrita a rótulos de suporte e metadados secundários que exigem apenas 4,5:1 (WCAG AA).
2. **Ajuste Fino do Tema Solário**: Ajustar `--color-text` no tema `solario` em `palettes.css` de `#3F5962` para `#2E4249` (e seu correspondente no catálogo canônico em `settings.ts`).
   - `#2E4249` sobre `#FDF6E3` (`page`) = **8,9:1** (supera 7:1).
   - `#2E4249` sobre `#EEE8D5` (`surface`) = **7,5:1** (supera 7:1).
3. **Tema Monocromático E-Ink**: Incorporar reforços geométricos (sublinhado duplo, molduras e bordas sólidas) nas marcações do simulador, garantindo distinção imediata mesmo na ausência de contraste de matiz cromática.

### Alternativas Consideradas
- *Declarar exceção para o Solário*: Rejeitada pois o Solário é um dos temas emblemáticos de estudo prolongado (Solarized Light) e o ajuste refinado de luminância preserva sua atmosfera visual enquanto garante conformidade formal.

---

## 3. Otimização Crítica de Performance para Meta Lighthouse $\ge 95$

### Questão
O carregamento atual da aplicação importa estaticamente 24 views no `router/index.ts`, obrigando qualquer visitante anônimo a carregar todo o código do editor, do canvas gráfico e dos módulos administrativos. Além disso, `fonts.css` declara `font-display: block` para as 24 famílias locais, gerando bloqueio de renderização (FOIT) de tipografia.

### Decisão
1. **Code-Splitting no Roteador**: Converter todas as rotas privadas/pesadas em `router/index.ts` para importações dinâmicas assíncronas (`() => import('../views/BooksView.vue')`, etc.). Apenas as rotas públicas essenciais compartilham os pedaços comuns.
2. **`font-display: swap`**: Atualizar as declarações `@font-face` em `fonts.css` de `font-display: block` para `font-display: swap`. O texto é renderizado imediatamente na fonte do sistema enquanto a fonte web carrega, eliminando telas congeladas.
3. **Preload de Fontes Críticas**: Incluir no `<head>` do `index.html` tags de pré-carregamento com prioridade alta para:
   - `latin-400-normal.woff2` de EB Garamond (`/fonts/eb-garamond/5.3.0/latin-400-normal.woff2`)
   - `latin-400-normal.woff2` e `latin-600-normal.woff2` de Source Sans 3 (`/fonts/source-sans-3/5.3.0/...`)
4. **Zero Layout Shift (CLS = 0)**: A bancada do simulador define altura mínima calculada pelo maior painel de dimensões, impedindo que a alternância entre abas mova o restante da página.

---

## 4. Simulador das 4 Dimensões em Domínio Público e Estado em Memória

### Questão
O simulador deve operar 100% no cliente sem login, sem dependências de rede e sem acessar dados do banco de dados ativo do usuário (Princípio I da Constituição).

### Decisão
Utilizar um módulo de dados estáticos imutáveis (`frontend/src/data/landingSimulator.ts`):
- **Obra**: *Memórias Póstumas de Brás Cubas* (1881), de Machado de Assis.
- **Trecho**: O prólogo canônico "Ao leitor", contendo 3 parágrafos curtos.
- **Marcações**: Três trechos anotados com cores e sublinhados vinculados a cada dimensão:
  - Dimensão 1 (Resumo): Síntese formal do propósito da dedicatória póstuma.
  - Dimensão 2 (Explicação): Análise da ironia machadiana e da inversão da perspectiva narrativa.
  - Dimensão 3 (Conceitos): Definição de conceitos como *narrador defunto*, *pessimismo lúcido* e *estilo livre*.
  - Dimensão 4 (Referências): Conexões com Laurence Sterne (*Tristram Shandy*), Xavier de Maistre e a tradição satírica ocidental.
- **Sincronização Visual**: Quando a aba ativa muda, as marcações no texto do livro recebem classe `.is-active-highlight` (sublinhado duplo e realce de fundo), enquanto as outras mantêm sublinhado simples.

---

## 5. Troca Efêmera de Temas via Composable `useVisitorTheme`

### Questão
A vitrine dos 10 temas permite ao leitor experimentar as paletas repintando a página inteira. Essa experiência não deve sobregravar preferências persistidas no `localStorage` de usuários cadastrados nem deixar rastros indesejados.

### Decisão
Criar o composable `frontend/src/composables/useVisitorTheme.ts`:
- Na montagem do componente, guarda o tema original presente em `document.documentElement.dataset.theme`.
- Ao selecionar uma paleta na vitrine, altera diretamente `document.documentElement.dataset.theme = themeId`.
- No `onBeforeUnmount`, restaura o tema anterior salvo, garantindo idempotência e ausência de efeitos colaterais ao navegar para `/login` ou `/registro`.
- Emite anúncio acessível via região `aria-live="polite"`: `"Tema aplicado: [Nome do Tema]. A página inteira foi repintada."`

---

## 6. Padronização Schema.org e Metadados de Compartilhamento

### Questão
A especificação requer dados estruturados Schema.org válidos e metatags completas de Open Graph e Twitter Cards.

### Decisão
1. Atualizar `buildWebApplicationSchema` em `useSeoMeta.ts` para estruturar `@type: ['SoftwareApplication', 'WebApplication']` com `applicationCategory: 'EducationalApplication'`.
2. Adicionar propriedades de identificação do software: `operatingSystem: 'All'`, `author: { '@type': 'Organization', name: 'Leitorum' }`, `offers: { '@type': 'Offer', price: '0', priceCurrency: 'BRL' }`.
3. Garantir `meta[name="twitter:card"]` como `summary_large_image` e `og:image` apontando para o asset oficial.
