# Briefing de Arquitetura e Disposição de Itens: Página Inicial sem Login (SEO) — Manifesto do Leitor Reflexivo

> **Contexto do Projeto**: Leitorum — Caderno de Leitura e Estudos em Camadas (FastAPI, Vue 3, SQLite local, modo WAL, 10 temas canônicos, tipografia editorial).  
> **Feature**: F0.8.09 (Feature 09 do Roadmap 0.8) — Página Inicial Pública / Vitrine de Conversão e SEO (`/` para usuários desconectados).

---

## 1. Missão da Tarefa

Você já possui o contexto integral do projeto **Leitorum**. Sua missão agora é **planejar minuciosamente a disposição espacial, arquitetura de componentes, hierarquia de conteúdo e estados interativos** da nova **Página Inicial sem Login (Landing Page & Manifesto)**.

A página pública atual (`LandingView.vue`) possui um formato padronizado de startup SaaS (hero centralizado genérico, botões repetitivos e 4 cartões com ícones). Ela precisa ser completamente reformulada para se tornar um **Manifesto Editorial do Leitor Reflexivo**: um ambiente acolhedor, solene e intelectual, que comunique o método do Leitorum através de simuladores interativos sem login e garanta excelência técnica em SEO e performance.

---

## 2. Requisitos Mandatórios do Roadmap 0.8 (Feature 09)

1. **Hero Editorial Assimétrico**:
   - Composição de abertura assimétrica, elegante e tipográfica (EB Garamond / Source Sans 3).
   - Mensagem de impacto que confronte a dispersão da leitura rasa na internet contemporânea e apresente o Leitorum como um refúgio de concentração e estudo em camadas.
   - Botões de conversão claros e desprovidos de apelos agressivos: `"Criar Conta Gratuita"` e `"Já possuo conta (Entrar)"`.

2. **Simulador Interativo do Fichamento em 4 Dimensões (In-Place)**:
   - O visitante deve poder vivenciar o método de estudo do Leitorum **diretamente na landing page**, sem criar conta e sem dependência de chamadas de API.
   - Trecho literário/filosófico exemplar pré-carregado (ex.: trecho de Machado de Assis, Montaigne, Virginia Woolf ou Marco Aurélio).
   - Abas interativas das 4 dimensões analíticas:
     - **Resumo Analítico** (ideia central e síntese da tese);
     - **Explicação Aprofundada** (desdobramento das premissas e argumentos);
     - **Conceitos-Chave** (vocabulário filosófico e termos-chave destacados);
     - **Referências & Conexões** (citações cruzadas e referências à obra).
   - Transição suave de esmaecimento do texto ao alternar entre as 4 dimensões (150ms).

3. **Demonstrador Interativo dos 10 Temas Canônicos**:
   - Exibição de amostras cromáticas com caixas de paleta real estilo Windows 11 para os 10 temas oficiais:
     - `papel-fosco`, `noite-suave`, `cinza-neutro`, `grafite`, `monocromatico`, `pergaminho`, `e-ink`, `solario`, `fiorde` e `voltagem`.
   - Ao clicar em uma paleta na landing page, as variáveis de estilo da bancada demonstrativa (ou da própria página) devem alternar instantaneamente, permitindo ao visitante comprovar o conforto ergonômico antes do cadastro.

4. **Manifesto de Soberania de Dados e Princípios**:
   - Declaração de soberania: dados 100% locais (*local-first*), zero anúncios, zero rastreadores de telemetria e nenhum modelo de IA devorando notas pessoais.
   - Natureza de software livre sustentado pela comunidade literária (com link para `/apoie` e `/sobre`).

5. **Infraestrutura de SEO e Performance**:
   - Dados estruturados Schema.org (`SoftwareApplication` e `EducationalApplication`) embutidos via JSON-LD.
   - Metatags completas de Open Graph (`og:title`, `og:description`, `og:image`, `og:type`) e Twitter Cards.
   - Taxa de contraste mínima de 7:1 (WCAG AAA) nos textos de leitura contínua.
   - Compatibilidade estrita com motores de busca (conteúdo vital indexável no HTML renderizado).
   - Meta de pontuação 95+ no Google Lighthouse (Performance, Acessibilidade, SEO).

6. **Regra Constitucional do Sistema Visual**:
   - **Zero Emojis**: É estritamente proibido o uso de emojis no código ou na interface. Todos os glifos devem utilizar `<Icon name="..." />` da biblioteca `lucide-vue-next`.

---

## 3. O que você deve entregar neste planejamento

Forneça um documento de especificação detalhada cobrindo:

### A. Wireframe Estrutural e Disposição dos Blocos (Layout Top-to-Bottom)
- Desenhe a árvore visual da página de cima a baixo, especificando a disposição em grade/colunas para Desktop ($\ge 1024$px), Tablet ($768$–$1023$px) e Mobile ($< 768$px).
- Defina o espaçamento vertical, alinhamentos, larguras máximas (`max-width`) e pontos focais de cada seção:
  1. *Header de Boas-Vindas Público*;
  2. *Hero Editorial com Manifesto e CTAs*;
  3. *Bancada do Simulador das 4 Dimensões*;
  4. *Ateliê Vitrine dos 10 Temas Canônicos*;
  5. *Seção de Soberania, Local-First e Privacidade*;
  6. *Depoimentos / Método Editorial / Commonplace Books*;
  7. *Rodapé Institucional e Chamada Final de Conversão*.

### B. Microcopy e Conteúdo Editorial Específico
- Sugira os textos reais e o tom de voz para:
  - Título e subtítulo do Hero (estilo manifesto ensaístico).
  - O trecho literário exato escolhido para o Simulador e os textos pré-carregados das 4 dimensões (Resumo, Explicação, Conceitos e Referências).
  - Textos explicativos da soberania de dados.
  - Rótulos acessíveis (`aria-label`) para cada controle interativo.

### C. Especificação Detalhada dos Componentes Interativos
- **Simulador das 4 Dimensões**:
  - Como os botões de aba são organizados (estilo abas de códice, chips ou livro aberto).
  - Como a citação original se posiciona em relação à anotação analítica (lado a lado em desktop vs coluna empilhada em mobile).
  - Indicadores de destaque visual e citações marginais.
- **Showcase dos 10 Temas**:
  - Como os cartões com as 4 amostras de cores (`--color-page`, `--color-surface`, `--color-text`, `--color-accent`) serão organizados na vitrine pública.
  - Qual o efeito visual ao selecionar um tema (anel de foco, pré-visualização ao vivo).

### D. Decomposição de Componentes Vue 3
- Identifique a modularização recomendada para a pasta `frontend/src/`:
  - `LandingView.vue` (container e SEO meta);
  - Subcomponentes isolados sugeridos (ex.: `LandingHero.vue`, `LandingStudySimulator.vue`, `LandingThemeShowcase.vue`, `LandingSovereigntyBanner.vue`).
- Props, eventos e estado reativo de cada componente.

### E. Checklist de Acessibilidade e SEO
- Estrutura de cabeçalhos (`<h1>`, `<h2>`, `<h3>`).
- Semântica ARIA para o simulador (`role="tablist"`, `role="tab"`, `role="tabpanel"`) e para o seletor de temas (`role="radiogroup"` / `role="radio"`).
- Alvos de toque móveis ($\ge 44 \times 44$px).
- Bloco JSON-LD exato para Schema.org.
