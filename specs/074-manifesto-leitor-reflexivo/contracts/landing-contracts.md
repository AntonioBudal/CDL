# Contratos de Interface e Componentes: Página Inicial sem Login (SEO) — Manifesto do Leitor Reflexivo

**Feature**: `074-manifesto-leitor-reflexivo`  
**Data**: 2026-10-11  
**Status**: Concluído (Phase 1)  

---

## 1. Arquitetura de Componentes da Landing Page

A interface `LandingView.vue` é decomposta em subcomponentes com isolamento claro de responsabilidades no diretório `frontend/src/components/landing/`:

```text
frontend/src/
├── components/
│   └── landing/
│       ├── PublicHeader.vue         # Cabeçalho com link "Pular para o conteúdo", links-âncora e Entrar
│       ├── HeroSection.vue          # Hero editorial assimétrico, manifesto e ficha de leitura
│       ├── MethodSimulator.vue      # Bancada livro aberto (Machado de Assis) + caderno em 4 abas
│       ├── ThemeShowcase.vue        # Vitrine interativa dos 10 temas com repintura em memória
│       ├── SovereigntySection.vue   # 4 princípios de soberania e linha do tempo histórica
│       └── PublicFooter.vue         # Fecho com chamada reflexiva e links institucionais
├── composables/
│   ├── useVisitorTheme.ts       # Gestor efêmero de tema para visita anônima
│   └── useSeoMeta.ts            # Gerenciador de metatags e JSON-LD Schema.org
├── data/
│   └── landingSimulator.ts      # Dados estáticos do trecho literário e das 4 dimensões
└── views/
    └── LandingView.vue          # Composição principal e landmarks semânticos
```

---

## 2. Contratos dos Componentes

### 2.1 `PublicHeader.vue`
- **Landmark**: `<header role="banner" class="public-header">`
- **Comportamento**:
  - Primeiro link focável: `<a href="#conteudo-principal" class="skip-link">Pular para o conteúdo</a>`.
  - Links de âncora: `#metodo`, `#temas`, `#principios` (ocultos em mobile para economia de espaço).
  - CTA de entrada: `<RouterLink to="/login" class="btn-login-header">Entrar</RouterLink>`.
  - Altura: 64px desktop / 56px mobile. Fundo `--color-page` com borda inferior `--color-border-divider`.

### 2.2 `HeroSection.vue`
- **Landmark**: `<section class="hero-editorial" id="conteudo-principal" aria-labelledby="hero-title">`
- **Comportamento**:
  - Grade 12 colunas no desktop: colunas 1–7 para manifesto e CTAs; colunas 9–12 para Ficha de Leitura flutuante.
  - Sobrelinha: "Caderno de leitura e estudo em camadas" em versalete.
  - Título (`h1`): "Ler devagar é uma forma de pensar."
  - Subtítulo: Parágrafo reflexivo de até 52ch.
  - CTAs: Botão primário para `/registro` ("Criar Conta Gratuita") e link secundário para `/login` ("Já possuo conta (Entrar)").
  - Ficha de Leitura: Cartão estático em `--color-surface` com citação e os 4 questionamentos do método.

### 2.3 `MethodSimulator.vue`
- **Landmark**: `<section id="metodo" class="method-simulator-section" aria-labelledby="simulator-title">`
- **Estrutura Visual**: Cartão amplo simulando um livro aberto ao lado de um caderno.
  - **Lado Esquerdo (Página da Obra)**:
    - Prólogo "Ao leitor" de *Memórias Póstumas de Brás Cubas* (1881).
    - Marcações no texto com atributos `data-dimension="resumo|explicacao|conceitos|referencias"`.
    - Nota marginal clássica na margem direita da página.
  - **Lado Direito (Caderno de Leitura)**:
    - Tablist acessível: `role="tablist"` com 4 abas (`role="tab"`, `aria-selected`, `aria-controls`).
    - Navegação por teclado: setas direcionais, Home e End para troca rápida de aba.
    - Painel ativo: `role="tabpanel"`, `tabindex="0"`, com transição suave de opacidade (150ms).
    - Altura mínima fixa (`min-height`) para garantir ausência de salto de layout (CLS = 0).
  - **Sincronização**: Ao ativar uma dimensão, as marcações daquela dimensão no livro recebem realce ativo (fundo preenchido e sublinhado duplo), enquanto as outras permanecem discretas.

### 2.4 `ThemeShowcase.vue`
- **Landmark**: `<section id="temas" class="theme-showcase-section" aria-labelledby="themes-title">`
- **Estrutura**:
  - Cabeçalho editorial explicativo sobre a importância do descanso visual e ergonomia tipográfica.
  - Reutilização do componente `ThemePreviewGrid.vue` operando em modo efêmero via `v-model="visitorTheme"`.
  - Grade 5 × 2 (desktop) e 2 × 5 (mobile).
  - Região de acessibilidade: `<div role="status" aria-live="polite" class="theme-status-msg">`.
  - Ao selecionar um tema, repinta a página inteira em memória alterando `document.documentElement.dataset.theme`.

### 2.5 `SovereigntySection.vue`
- **Landmark**: `<section id="principios" class="sovereignty-section" aria-labelledby="principles-title">`
- **Estrutura**:
  - Coluna de título fixo ou destacado à esquerda e lista de 4 garantias de soberania à direita.
  - Princípios:
    1. *Sem anúncios nem rastreadores* (zero telemetria).
    2. *Suas notas não alimentam modelos* (nenhuma transmissão para terceiros).
    3. *Você pode levar tudo embora* (exportação aberta e execução local).
    4. *Software livre sustentado por leitores* (código aberto).
  - Linha do tempo dos *Commonplace Books*: marcos do séc. XVI, John Locke (1706) e o estudo em camadas contemporâneo.

### 2.6 `PublicFooter.vue`
- **Landmark**: `<footer role="contentinfo" class="public-footer">`
- **Estrutura**:
  - Chamada reflexiva final: "Comece pelo próximo livro que você pretende ler devagar."
  - Links institucionais: Sobre (`/sobre`), Apoie (`/apoie`), Licença e Repositório GitHub.

---

## 3. Contrato do Composable `useVisitorTheme`

```typescript
export interface UseVisitorThemeReturn {
  activeTheme: Ref<CanonicalThemeId>
  statusMessage: Ref<string>
  applyTheme: (themeId: CanonicalThemeId) => void
  resetToOriginal: () => void
}
```
- **Ciclo de Vida**:
  - `onMounted`: Captura o tema atual do elemento raiz (`document.documentElement.dataset.theme || 'papel-fosco'`).
  - `applyTheme`: Define `document.documentElement.dataset.theme = themeId` e atualiza `statusMessage` com "Tema aplicado: [Nome]. A página inteira foi repintada."
  - `onBeforeUnmount`: Restaura o tema original no DOM caso não haja preferência persistida de sessão ativa.

---

## 4. Contrato de Roteamento Assíncrono (`router/index.ts`)

Todas as rotas autenticadas do sistema passam a usar importação dinâmica sob demanda:
```typescript
{
  path: '/livros',
  name: 'books',
  component: () => import('../views/BooksView.vue'),
  meta: { title: 'Livros' },
}
```
As rotas públicas iniciais permanecem otimizadas com prioridade de carregamento.
