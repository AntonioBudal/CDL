# Planejamento — Página Inicial sem Login: Manifesto do Leitor Reflexivo (F0.8.09)

* **Preparado por:** Claude Code, em 2026-10-11, a pedido do usuário
* **Natureza:** documento de planejamento para o agente do frontend (Antigravity). Não é spec do Spec Kit nem
  altera código: serve de insumo para `speckit.specify` / `speckit.plan` da feature.
* **Base:** leitura (sem alteração) de `frontend/src/views/LandingView.vue`, `composables/useSeoMeta.ts`,
  `components/ThemePreviewGrid.vue`, `types/settings.ts`, `palettes.css`, `tokens.css`, `fonts.css`, `index.html`,
  `router/index.ts` e `backend/app/services/seo_service.py`.

---

## 0. Achados no código que mudam o plano

Sete pontos que o briefing não cobre e que precisam de decisão antes do desenho:

1. **Não há HTML renderizado no servidor.** O site é uma SPA: `index.html` traz só metatags estáticas e um
   `<div id="app">` vazio; o backend serve apenas `robots.txt`, `sitemap.xml` e o manifesto. O requisito "conteúdo
   vital indexável no HTML renderizado" **não é atendido hoje** e não se resolve só com Vue. Opções:
   - **(a) Recomendada:** pré-renderizar a rota `/` no build (`renderToString` de `vue/server-renderer`, que já vem
     com o Vue — sem dependência nova) e injetar o HTML em `index.html`; no cliente, hidratar.
   - **(b) Mínima:** escrever à mão, dentro de `#app`, um bloco estático com `h1`, manifesto e links, que o Vue
     substitui ao montar. Zero risco de hidratação, mas o texto fica duplicado em dois lugares.
2. **O tema `solario` não atinge 7:1.** Medi os dez temas: texto sobre página dá 6,9:1 e sobre superfície 6,1:1
   no `solario`; os outros nove ficam entre 9,9:1 e 21:1. Além disso, `--color-muted` fica abaixo de 7:1 em seis
   temas (4,5:1 no `grafite`). Consequências: (i) texto de leitura contínua da landing usa **sempre**
   `--color-text`, nunca `--color-muted`; (ii) o `solario` precisa de ajuste de token ou de uma exceção declarada.
3. **"EducationalApplication" não é um tipo do Schema.org.** É um valor de `applicationCategory`. Os tipos válidos
   são `SoftwareApplication` e seu subtipo `WebApplication` (o que o projeto já usa). O JSON-LD da seção E segue isso.
4. **Fontes com `font-display: block`.** `fonts.css` declara as 24 famílias assim, o que atrasa a primeira pintura
   do título. Para a meta de Lighthouse, a landing precisa de `swap` (ou `optional`) e `preload` só dos arquivos
   que usa: EB Garamond 400/500 e Source Sans 3 400/600.
5. **Todas as telas entram no pacote inicial.** `router/index.ts` importa as views de forma estática; o visitante
   baixa o código do editor, do canvas e da administração para ver a landing. Carregar as rotas autenticadas sob
   demanda (`() => import(...)`) é pré-requisito realista para Performance ≥ 95.
6. **Os temas só existem em `:root[data-theme]`.** Não dá para aplicar um tema a um trecho da página sem duplicar
   seletores. A troca "ao vivo" mais simples e fiel é trocar o tema **da página inteira** (ver seção C.2).
7. **Dois textos do briefing podem não ser verdadeiros como estão.**
   - "Dados 100% locais": vale para quem hospeda a própria instância. Quem cria conta em `leitorum.com` guarda os
     dados no servidor do Leitorum. O texto precisa dizer o que é verdade para o visitante daquela página.
   - "Nenhum modelo de IA devorando notas": o projeto pesquisa leitura automática de páginas manuscritas, com
     modelos rodando localmente. A formulação segura é "nenhuma nota é enviada a serviços de IA de terceiros nem
     usada para treinar modelos".
   - **Depoimentos:** não existem depoimentos reais. Publicar depoimentos inventados é enganoso; a seção 6 abaixo
     troca depoimentos pela tradição histórica do método, que é verificável.

Também há um componente pronto a reaproveitar: `ThemePreviewGrid.vue` já implementa `radiogroup`/`radio` com
teclado, sobre `CANONICAL_THEME_PREVIEWS`. E o mapa de ícones (`Icon.vue`) tem 76 nomes; os novos precisam ser
acrescentados lá e em `IconName`.

---

## A. Wireframe estrutural (de cima para baixo)

**Grade base:** contêiner `max-width: 1200px`, 12 colunas, calha de 24 px (16 px no mobile), margem lateral de
`clamp(16px, 4vw, 48px)`. Texto corrido nunca passa de `68ch`. Ritmo vertical entre seções:
`clamp(64px, 9vw, 128px)`. Alinhamento predominante à esquerda — a assimetria vem de deslocar o texto para as
colunas 1–7 e deixar a coluna da direita para um elemento menor, não de centralizar.

### 1. Header público

```text
Desktop / Tablet                                   Mobile
┌──────────────────────────────────────────────┐   ┌──────────────────────────┐
│ Leitorum      Método  Temas  Princípios  Entrar │   │ Leitorum          Entrar │
└──────────────────────────────────────────────┘   └──────────────────────────┘
```

- Altura 64 px (56 px no mobile), fundo `--color-page`, linha inferior de 1 px `--color-border-divider`. Não fixo:
  some ao rolar; a chamada final cuida da conversão.
- Marca em EB Garamond 500, 22 px. Links-âncora (`#metodo`, `#temas`, `#principios`) em Source Sans 3 15 px;
  no mobile somem (a página é linear) e fica só "Entrar".
- Primeiro elemento focável: link "Pular para o conteúdo".

### 2. Hero editorial com manifesto e chamadas

```text
Desktop (≥ 1024)
┌───────────────────────────────────────────────┬──────────────────────────┐
│ col 1–7                                       │ col 9–12                 │
│ SOBRELINHA (versalete)                        │  ┌────────────────────┐  │
│ Título em três linhas,                        │  │ Ficha de leitura   │  │
│ EB Garamond, clamp(40px, 5.2vw, 72px)         │  │ (cartão estático:  │  │
│                                               │  │ epígrafe + 4 linhas│  │
│ Subtítulo, 20 px, até 52ch                    │  │ rotuladas do método)│ │
│                                               │  └────────────────────┘  │
│ [Criar Conta Gratuita]  Já possuo conta       │  deslocado 48 px abaixo  │
└───────────────────────────────────────────────┴──────────────────────────┘
Tablet (768–1023): texto em col 1–8; ficha abaixo, col 5–12 (alinhada à direita).
Mobile (< 768): coluna única; ficha depois dos botões; botões empilhados, largura total.
```

- `padding-block: clamp(56px, 10vw, 144px) clamp(48px, 7vw, 96px)`.
- Ponto focal: o título. Sem imagem de fundo e sem ilustração pesada — o maior elemento visível é texto, o que
  mantém o LCP baixo.
- A "ficha de leitura" é decorativa-informativa (HTML e CSS, não imagem): antecipa a bancada da seção seguinte.
- Botão primário: `--color-accent` / `--color-on-accent`, 48 px de altura. Secundário: link sublinhado, sem caixa.
  Sem selos, contadores ou "grátis para sempre".

### 3. Bancada do simulador das 4 dimensões (`#metodo`)

```text
Desktop
┌──────────────────────────────────────────────────────────────────────────┐
│ h2 + parágrafo de abertura (col 1–7)                                     │
├─────────────────────────────────────┬────────────────────────────────────┤
│ col 1–6  PÁGINA DA OBRA             │ col 7–12  CADERNO                  │
│ epígrafe (autor, obra, ano)         │ [Resumo][Explicação][Conceitos][Ref]│
│ trecho em EB Garamond 20/1.65       │ ───────────────────────────────────│
│ com trechos marcados                │ painel da dimensão ativa           │
│ nota marginal (col. estreita)       │ (altura mínima fixa)               │
└─────────────────────────────────────┴────────────────────────────────────┘
Tablet: mesma divisão em 6/6 até 900 px; abaixo disso, empilha.
Mobile: trecho primeiro (recolhível após 8 linhas, com "Ler o trecho inteiro"),
        abas em faixa rolável horizontal, painel abaixo.
```

- A bancada é um único cartão (`--color-surface`, borda de 1 px, raio do tema), com a "dobra" central marcada por
  uma linha vertical de 1 px — a imagem é a de um livro aberto ao lado do caderno.
- Altura mínima do painel fixada pelo maior dos quatro textos, para a troca de aba não deslocar a página (CLS zero).

### 4. Ateliê vitrine dos 10 temas (`#temas`)

```text
Desktop: h2 + texto (col 1–5)  |  grade 5 × 2 de cartões (col 6–12)
Tablet:  texto em cima; grade 5 × 2 em largura total
Mobile:  texto em cima; grade 2 × 5
```

- Cada cartão ≥ 120 × 96 px no desktop e ≥ 44 px de altura útil no mobile.
- Abaixo da grade, uma linha de estado: "Tema atual: Pergaminho. A página inteira foi repintada."

### 5. Soberania, local-first e privacidade (`#principios`)

```text
Desktop: h2 à esquerda (col 1–4, fixo ao rolar dentro da seção) | lista de 4 princípios (col 6–12)
Tablet:  h2 em cima; princípios em 2 × 2
Mobile:  coluna única
```

- Cada princípio: ícone de traço (24 px), título `h3`, um parágrafo. Sem cartões com sombra: separados por filete.
- Fecha com dois links de texto: "Como o Leitorum se sustenta" (`/apoie`) e "Sobre o projeto e o método" (`/sobre`).

### 6. O método e sua tradição (no lugar de depoimentos)

```text
Desktop: três colunas de texto (col 1–4, 5–8, 9–12), cada uma com data em versalete, título h3 e parágrafo
Tablet:  três colunas mais estreitas ou 1 + 2
Mobile:  coluna única, com filete entre os itens
```

- Fundo `--color-surface-soft` de borda a borda, para marcar pausa de leitura.

### 7. Chamada final e rodapé

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ frase de fecho (EB Garamond 32–40 px, col 2–10)                          │
│ [Criar Conta Gratuita]   Já possuo conta (Entrar)                        │
├──────────────────────────────────────────────────────────────────────────┤
│ AppFooter existente: Sobre · Apoie · licença · repositório               │
└──────────────────────────────────────────────────────────────────────────┘
```

- Mesmos dois rótulos do hero, sem variação de texto (consistência para leitor de tela e para o visitante).

---

## B. Microcopy e conteúdo editorial

**Tom:** ensaístico, em segunda pessoa do singular implícita ("você"), frases completas, sem imperativos
publicitários, sem superlativos, sem pontos de exclamação. Nenhum emoji.

### B.1 Hero

- **Sobrelinha:** `Caderno de leitura e estudo em camadas`
- **Título (`h1`):** `Ler devagar é uma forma de pensar.`
- **Subtítulo:** `A internet ensinou a passar os olhos. O Leitorum é um caderno para o movimento contrário: voltar
  ao texto, anotar o que ele diz, explicar com as próprias palavras e guardar o que merece ficar.`
- **Alternativas de título para escolha:** `Contra a leitura que não deixa rastro.` ·
  `Um caderno para quem lê para compreender.`
- **Ficha de leitura (cartão do hero):** rótulo `Ficha de leitura` e quatro linhas — `Resumo: o que o texto afirma`
  · `Explicação: por que afirma` · `Conceitos: as palavras que sustentam a ideia` · `Referências: com quem o texto
  conversa`.
- **Botões:** `Criar Conta Gratuita` · `Já possuo conta (Entrar)`.

### B.2 Simulador

**Abertura da seção** — `h2`: `Um trecho, quatro leituras` · texto: `Todo estudo no Leitorum passa pelas mesmas
quatro perguntas. Experimente com um parágrafo de Machado de Assis: nada sai desta página e nada é enviado.`

**Trecho escolhido** — Machado de Assis, *Memórias Póstumas de Brás Cubas* (1881), prólogo "Ao leitor". Obra em
domínio público, original em português (dispensa tradução e direitos de tradutor) e, de quebra, fala de leitores:

> Que Stendhal confessasse haver escrito um de seus livros para cem leitores, coisa é que admira e consterna. O que
> não admira, nem provavelmente consternará é se este outro livro não tiver os cem leitores de Stendhal, nem
> cinquenta, nem vinte, e quando muito, dez. Dez? Talvez cinco. Trata-se, na verdade, de uma obra difusa, na qual
> eu, Brás Cubas, se adotei a forma livre de um Sterne, ou de um Xavier de Maistre, não sei se lhe meti algumas
> rabugens de pessimismo.

**Atenção:** transcrevi o trecho de memória. Antes de publicar, conferir palavra por palavra e a pontuação com uma
edição de referência (por exemplo, a da Biblioteca Digital do MEC/NUPILL ou a da Academia Brasileira de Letras).

**Marcas no trecho** (três, cada uma ligada a uma dimensão): `cem leitores` (Referências), `Dez? Talvez cinco.`
(Resumo/Explicação), `forma livre` e `rabugens de pessimismo` (Conceitos).
**Nota marginal:** `O narrador fala depois de morto: não tem mais a quem agradar.`

**Textos das quatro dimensões** (redação própria, para o painel):

1. **Resumo analítico** — `O narrador prevê que o livro terá pouquíssimos leitores e não lamenta. Atribui isso à
   natureza da obra: difusa, de forma livre, tocada de pessimismo. A tese implícita é que um livro pode escolher
   seus leitores em vez de cortejá-los.`
2. **Explicação aprofundada** — `Brás Cubas parte de um autor consagrado para rebaixar a própria expectativa: de cem
   leitores a cinco, em contagem regressiva. O gesto é irônico em duas direções. Finge modéstia, mas se põe ao lado
   de Stendhal, Sterne e Xavier de Maistre. E avisa o leitor, desde a primeira página, de que o livro não vai
   seguir a ordem esperada de um romance: quem continuar já aceitou o pacto.`
3. **Conceitos-chave** — `Forma livre: narrativa que se permite digressões, capítulos curtos e interrupções, sem
   obedecer à progressão linear do enredo. Obra difusa: aquela que não se concentra em um único fio. Rabugens de
   pessimismo: o humor desencantado que colore o livro. Pacto de leitura: o acordo tácito entre quem escreve e
   quem lê sobre o tipo de texto que se tem em mãos.`
4. **Referências e conexões** — `Stendhal, que teria escrito para poucos leitores. Laurence Sterne, "A Vida e as
   Opiniões do Cavalheiro Tristram Shandy" (1759–1767), modelo da narrativa digressiva. Xavier de Maistre, "Viagem
   à Roda do Meu Quarto" (1794). Conexão possível no seu caderno: os prefácios em que Montaigne também se dirige ao
   leitor para desencorajá-lo.`

**Legenda sob a bancada:** `No seu caderno, cada estudo guarda essas quatro camadas, ligadas ao livro e ao capítulo
de onde vieram.`

### B.3 Temas

- `h2`: `Dez papéis para a mesma página`
- Texto: `Ler por horas depende de onde os olhos descansam. Escolha um tema e veja esta página mudar. A escolha
  vale só para esta visita.`

### B.4 Soberania e princípios

Texto a confirmar contra o que é verdade na instância pública (ver achado 7):

- `h2`: `O caderno é seu`
- **Sem anúncios nem rastreadores** — `O Leitorum não vende atenção. Não há publicidade, pixels de rastreamento nem
  telemetria de uso.`
- **Suas notas não alimentam modelos** — `O que você escreve não é enviado a serviços de inteligência artificial de
  terceiros nem usado para treinar modelo algum.`
- **Você pode levar tudo embora** — `Seus estudos saem em formatos abertos quando você quiser. E o programa pode
  rodar no seu próprio computador, com os dados guardados só nele.`
- **Software livre, sustentado por leitores** — `O código é aberto e o projeto vive de apoio voluntário, não de
  investidores.`

### B.5 Método e tradição

- `h2`: `Um hábito antigo, com ferramentas novas`
- **Século XVI — os cadernos de lugares-comuns:** `Leitores copiavam passagens e as organizavam por tema para
  reencontrá-las. O caderno era a memória do leitor.`
- **1706 — o método de Locke:** `John Locke publicou um sistema de índice para esses cadernos, para que nenhuma
  anotação se perdesse.`
- **Hoje — o fichamento em camadas:** `O Leitorum mantém o gesto e acrescenta o que o papel não fazia: ligar notas
  entre obras, revisar no tempo certo e buscar em tudo o que você já leu.`

(Datas e atribuições a conferir antes de publicar; não usar citações diretas sem fonte.)

### B.6 Chamada final

- Frase: `Comece pelo próximo livro que você pretende ler devagar.`

### B.7 Rótulos acessíveis

| Controle | Rótulo |
| :--- | :--- |
| Link de salto | `Pular para o conteúdo` |
| Navegação do header | `aria-label="Seções da página"` |
| Lista de abas | `aria-label="Dimensões do fichamento"` |
| Cada aba | texto visível (`Resumo analítico`, `Explicação aprofundada`, `Conceitos-chave`, `Referências e conexões`) |
| Trecho | `figure` com `figcaption`: `Machado de Assis, Memórias Póstumas de Brás Cubas, 1881. Prólogo "Ao leitor".` |
| Trecho marcado | `mark` com texto oculto: `trecho destacado, ligado a Conceitos-chave` |
| Botão de expandir trecho (mobile) | `Ler o trecho inteiro` / `Recolher o trecho`, com `aria-expanded` |
| Grupo de temas | `aria-label="Temas visuais do Leitorum"` |
| Cada tema | `aria-label="Papel Fosco, tema claro"` (nome + claro/escuro) |
| Estado do tema | região `aria-live="polite"`: `Tema aplicado: Pergaminho` |
| Botões de conversão | o próprio texto visível; sem `aria-label` divergente |

---

## C. Componentes interativos

### C.1 Simulador das 4 dimensões

- **Abas como marcadores de códice:** quatro abas no topo do painel direito, com a ativa "colada" ao painel (sem
  borda inferior) e as demais recuadas 2 px. Rótulo em Source Sans 3 600, 15 px; ícone opcional de 16 px à
  esquerda. Altura de 44 px.
- **Mobile:** as abas viram uma faixa com rolagem horizontal e `scroll-snap`; a ativa rola para a área visível.
- **Relação trecho × anotação:** lado a lado no desktop (trecho à esquerda, na ordem de leitura); empilhado no
  mobile, trecho primeiro.
- **Ligação visual:** ao ativar uma aba, as marcas do trecho ligadas àquela dimensão ganham fundo cheio
  (`--color-selected-bg`) e as demais ficam só sublinhadas. A ligação nunca depende só de cor: marca ativa também
  recebe sublinhado duplo.
- **Nota marginal:** coluna estreita à esquerda do trecho no desktop (EB Garamond itálico, 15 px); no mobile, vira
  nota recuada abaixo do trecho.
- **Transição:** 150 ms de `opacity` no conteúdo do painel (sai em 75 ms, entra em 75 ms). Com
  `prefers-reduced-motion: reduce` ou no tema `e-ink` (que já zera animações), troca instantânea.
- **Teclado (padrão de abas com ativação automática):** setas esquerda/direita mudam e ativam a aba; `Home`/`End`
  vão à primeira/última; `Tab` sai da lista e entra no painel (`tabindex="0"` no painel).
- **Renderização:** os quatro painéis existem no HTML desde o início (os inativos com `hidden`), para que o
  conteúdo seja indexável e para que a troca não dependa de rede. Nenhuma requisição.
- **Estado inicial:** aba "Resumo analítico".

### C.2 Vitrine dos 10 temas

- **Cartão estilo paleta:** miniatura de página (fundo `page`) com um "papel" interno (`surface`) contendo duas
  linhas de texto falso (`text`) e uma faixa de destaque (`accent`); abaixo, o nome do tema. As quatro cores vêm de
  `CANONICAL_THEME_PREVIEWS`, que já as traz.
- **Reaproveitamento:** partir de `ThemePreviewGrid.vue` (já tem `radiogroup`, `radio`, `aria-checked` e setas).
  Se o visual pedir mudanças, parametrizar o componente em vez de duplicar.
- **Seleção:** anel de 2 px em `--color-accent` com 2 px de afastamento, mais um ícone `check` no canto — o estado
  não depende só da cor do anel.
- **Efeito ao selecionar — recomendação: repintar a página inteira.** Define-se `data-theme` em
  `document.documentElement`, em memória. É o que prova o conforto de leitura e é a única forma que usa os tokens
  completos de cada tema (ver achado 6).
  - Não gravar em `localStorage` nem chamar a API de preferências.
  - Ao sair da landing (`onBeforeUnmount`), restaurar o tema anterior.
  - Opcional, a decidir: levar a escolha para o cadastro (`/registro?tema=pergaminho`).
- **Alternativa mais contida:** repintar só a bancada, aplicando as quatro cores como variáveis locais. É menos
  fiel (faltam bordas, tons suaves e estados) e não é a recomendada.
- **Transição:** 150 ms em `background-color` e `color`, respeitando `prefers-reduced-motion`.
- **Tema inicial:** o do sistema (`prefers-color-scheme`): `papel-fosco` no claro, `noite-suave` no escuro.

---

## D. Decomposição de componentes Vue 3

```text
frontend/src/
├── views/LandingView.vue                     # contêiner, SEO, tema da visita
├── components/landing/
│   ├── LandingHeader.vue
│   ├── LandingHero.vue
│   ├── LandingStudySimulator.vue
│   ├── LandingStudyExcerpt.vue               # trecho com marcas e nota marginal
│   ├── LandingThemeShowcase.vue              # usa ThemePreviewGrid
│   ├── LandingSovereignty.vue
│   ├── LandingTradition.vue
│   └── LandingFinalCta.vue
├── composables/useVisitorTheme.ts            # aplica e restaura data-theme, sem persistir
└── constants/landingContent.ts               # todo o texto e o conteúdo do simulador
```

| Componente | Props | Eventos | Estado próprio |
| :--- | :--- | :--- | :--- |
| `LandingView` | — | — | chama `useSeoMeta` e `useVisitorTheme`; repassa `theme` |
| `LandingHeader` | `sections: {id, label}[]` | — | nenhum |
| `LandingHero` | `overline`, `title`, `subtitle`, `card: {label, lines[]}` | — | nenhum (links são `RouterLink`) |
| `LandingStudySimulator` | `excerpt`, `dimensions: Dimension[]`, `initialId?` | `change(id)` | `activeId: Ref<DimensionId>`; ids únicos das abas e painéis |
| `LandingStudyExcerpt` | `excerpt`, `activeId` | — | `expanded: Ref<boolean>` (só no mobile) |
| `LandingThemeShowcase` | `modelValue: CanonicalThemeId` | `update:modelValue` | nenhum (controlado pelo pai) |
| `LandingSovereignty` | `principles: {icon, title, text}[]`, `links` | — | nenhum |
| `LandingTradition` | `items: {period, title, text}[]` | — | nenhum |
| `LandingFinalCta` | `phrase` | — | nenhum |

Tipos em `landingContent.ts`:

```ts
export type DimensionId = 'resumo' | 'explicacao' | 'conceitos' | 'referencias'
export interface Dimension { id: DimensionId; label: string; icon: IconName; body: string }
export interface ExcerptMark { text: string; dimension: DimensionId }
export interface Excerpt { author: string; work: string; year: number; section: string
                           paragraphs: string[]; marks: ExcerptMark[]; marginNote: string }
```

`useVisitorTheme()` devolve `{ theme: Ref<CanonicalThemeId>, setTheme(id) }`, lê o tema atual do `html` ao montar,
aplica a troca em `document.documentElement.dataset.theme` e o restaura em `onBeforeUnmount`. Precisa ser seguro
fora do navegador (pré-renderização): não tocar em `document` fora de `onMounted`.

Regras para todos: nenhum componente da landing faz requisição; todo texto vem de `landingContent.ts` (uma fonte
só, também usada pela pré-renderização); ícones só por `<Icon name="..." />`; os nomes novos (`quote`, `palette`,
`library`, `feather` ou equivalentes) entram em `Icon.vue` e em `IconName`.

---

## E. Checklist de acessibilidade e SEO

### E.1 Estrutura de cabeçalhos

```text
h1  Ler devagar é uma forma de pensar.
  h2  Um trecho, quatro leituras
    h3  (título do painel ativo — cada painel tem o seu)
  h2  Dez papéis para a mesma página
  h2  O caderno é seu
    h3  Sem anúncios nem rastreadores
    h3  Suas notas não alimentam modelos
    h3  Você pode levar tudo embora
    h3  Software livre, sustentado por leitores
  h2  Um hábito antigo, com ferramentas novas
    h3  Século XVI — os cadernos de lugares-comuns
    h3  1706 — o método de Locke
    h3  Hoje — o fichamento em camadas
  h2  (chamada final, pode ser visualmente a frase de fecho)
```

Um único `h1`. Landmarks: `header`, `nav`, `main#conteudo`, `footer`. A sobrelinha do hero é `p`, não cabeçalho.

### E.2 ARIA

- **Simulador:** contêiner das abas com `role="tablist"` e `aria-label`; cada aba é um `button` com `role="tab"`,
  `id`, `aria-selected`, `aria-controls` e `tabindex` 0 (ativa) ou −1; cada painel com `role="tabpanel"`,
  `aria-labelledby` e `tabindex="0"`; painéis inativos com `hidden`.
- **Temas:** `role="radiogroup"` com `aria-label`; cada cartão `role="radio"` com `aria-checked`; foco itinerante
  (um só elemento na ordem de tabulação); setas mudam e selecionam; região `aria-live="polite"` anuncia o tema.
- **Trecho:** `figure` > `blockquote` + `figcaption`; marcas em `mark`.
- Sem `aria-label` em elementos que já têm texto visível equivalente.

### E.3 Toque, foco e movimento

- [ ] Todo alvo interativo com pelo menos 44 × 44 px (abas, cartões de tema, botões, links do header no mobile).
- [ ] Foco visível em todos os temas: contorno de 2 px com afastamento, contraste ≥ 3:1 contra o fundo adjacente.
- [ ] `prefers-reduced-motion` respeitado em abas, temas e rolagem por âncora.
- [ ] Página utilizável a 200 % de zoom e a 320 px de largura, sem rolagem horizontal.

### E.4 Contraste

- [ ] Texto de leitura contínua em `--color-text` sobre `--color-page` ou `--color-surface`: ≥ 7:1 em todos os
      temas. **Pendente no `solario`** (6,9:1 e 6,1:1).
- [ ] `--color-muted` não usado em parágrafos; só em metadados curtos, e mesmo assim ≥ 4,5:1 (falha por pouco no
      `grafite`: 4,5:1 — conferir o arredondamento).
- [ ] Botão primário (`--color-on-accent` sobre `--color-accent`): ≥ 4,5:1. Hoje 4,8:1 em `noite-suave` e
      `grafite` — passa em AA, não em AAA.
- [ ] Marcas do trecho legíveis nos dez temas, inclusive no `e-ink` (que não tem cor).

### E.5 SEO e desempenho

- [ ] HTML inicial de `/` contém `h1`, subtítulo, trecho, os quatro painéis e os princípios (achado 1).
- [ ] `title` (≤ 60 caracteres): `Leitorum — caderno de leitura e estudo em camadas`.
- [ ] `meta description` (≤ 155): `Um caderno para ler devagar: fichamento em quatro camadas, dez temas de leitura,
      sem anúncios nem rastreadores. Software livre.`
- [ ] `link rel="canonical"`, `og:title`, `og:description`, `og:url`, `og:type=website`, `og:image` (1200 × 630, com
      `og:image:alt`), `og:locale=pt_BR`, `twitter:card=summary_large_image` e pares. O `index.html` já tem quase
      tudo; faltam `og:image:alt` e `og:locale`, e os textos precisam bater com os novos.
- [ ] `html lang="pt-BR"`.
- [ ] Fontes: `preload` de EB Garamond 400/500 e Source Sans 3 400/600 em WOFF2; `font-display: swap`; pilha de
      reserva com métricas próximas (`Georgia` e `system-ui`) para evitar salto de layout.
- [ ] Rotas autenticadas carregadas sob demanda (achado 5).
- [ ] Sem imagens acima da dobra; se houver alguma, com `width`/`height` e `loading="lazy"` abaixo da dobra.
- [ ] CLS: altura mínima do painel do simulador fixada; troca de tema sem reflow.
- [ ] `sitemap.xml` e `robots.txt` (já servidos pelo backend) incluem `/`, `/sobre` e `/apoie`.
- [ ] Lighthouse ≥ 95 nas quatro categorias, medido em modo anônimo, perfil móvel, sobre o build de produção.

### E.6 JSON-LD

Bloco único em `index.html` (e espelhado em `buildWebApplicationSchema`). `EducationalApplication` entra como
categoria, não como tipo. Nenhuma nota ou contagem de avaliações inventada.

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": "https://leitorum.com/#website",
      "url": "https://leitorum.com/",
      "name": "Leitorum",
      "inLanguage": "pt-BR",
      "description": "Caderno de leitura e estudo em camadas."
    },
    {
      "@type": ["SoftwareApplication", "WebApplication"],
      "@id": "https://leitorum.com/#app",
      "name": "Leitorum",
      "url": "https://leitorum.com/",
      "description": "Caderno pessoal de leitura e estudo: fichamento em quatro camadas (resumo, explicação, conceitos e referências), dez temas de leitura, sem anúncios nem rastreadores.",
      "applicationCategory": "EducationalApplication",
      "applicationSubCategory": "Caderno de leitura e fichamento",
      "operatingSystem": "Web",
      "browserRequirements": "Requer JavaScript e um navegador atual.",
      "inLanguage": "pt-BR",
      "isAccessibleForFree": true,
      "featureList": [
        "Fichamento em quatro camadas",
        "Biblioteca organizada por livro, capítulo e estudo",
        "Destaques e notas de margem",
        "Dez temas de leitura",
        "Revisão espaçada"
      ],
      "offers": { "@type": "Offer", "price": "0", "priceCurrency": "BRL" },
      "image": "https://leitorum.com/assets/og-cover.png"
    }
  ]
}
```

Conferir antes de publicar: a `featureList` só pode listar o que existe na versão publicada, e a `license` pode ser
acrescentada com a URL da licença real do repositório.

---

## Decisões que ficam com o usuário

1. Como tornar o conteúdo indexável: pré-renderização no build (recomendada) ou bloco estático em `index.html`.
2. `solario`: ajustar os tokens para 7:1 ou declarar exceção.
3. Troca de tema: página inteira (recomendada) ou só a bancada; e se a escolha segue para o cadastro.
4. Redação final da seção de soberania, conforme o que é verdade em `leitorum.com`.
5. Título do hero (três opções em B.1) e confirmação do trecho de Machado.
6. Aceitar a troca de "depoimentos" por "tradição do método".
7. Carregamento sob demanda das rotas autenticadas entra nesta feature ou vira feature própria.
