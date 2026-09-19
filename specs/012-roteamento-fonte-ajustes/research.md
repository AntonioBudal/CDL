# Technical Research: Correção de Roteamento, Fonte Global e Limpeza de Ajustes

**Feature**: `012-roteamento-fonte-ajustes`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Decisões Técnicas

### D1: Resolução da Causa-Raiz do Bug da Tela Vazia no Vue Router + Transition

- **Diagnóstico Técnico:**
  - Em Vue 3, o componente `<Transition mode="out-in">` exige **estritamente um único nó raiz** no componente filho. Quando uma view associada à rota possui múltiplos elementos na raiz do `<template>` (fragmentos com tags irmãs como `<header>` e `<div>`, ou múltiplos nós com diretivas estruturais `v-if`/`v-else`), a transição não consegue rastrear a entrada e saída dos elementos do DOM. O componente de saída é desmontado, mas o componente de entrada falha silenciosamente na montagem, deixando o container `<main>` completamente vazio até que ocorra um recarregamento forçado (F5).
  - Além disso, a ausência de uma chave unívoca no `<component :is="Component">` impedia a destruição e remontagem limpa de componentes durante navegações entre rotas irmãs ou mudanças em parâmetros de query (`?chapter=...`).
- **Decisão Arquitetural:**
  1. No arquivo [`frontend/src/App.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/App.vue), utilizar a chave de rota completa no componente renderizado:
     ```vue
     <RouterView v-slot="{ Component }">
       <Transition name="page" mode="out-in">
         <component :is="Component" :key="$route.fullPath" />
       </Transition>
     </RouterView>
     ```
  2. Envelopar todas as views com múltiplos nós raiz em containers únicos semânticos com classes dedicadas:
     - `BooksView.vue`: Envelopar em `<div class="books-view">`
     - `BookView.vue`: Envelopar em `<div class="book-view">`
     - `StudyView.vue`: Envelopar em `<div class="study-view">`
     - `StudyEditView.vue`: Envelopar em `<div class="study-edit-view">`
     - `ImportView.vue`: Envelopar em `<div class="import-view">`
- **Alternativas Rejeitadas:**
  - *Remover `<Transition>`*: Destruiria a identidade física e cinemática entregue pelas 5 Superclasses de Interface (Zero-G, Mecânica, Invisível, Dimensional e Monolítica).
  - *Usar `:key="$route.path"`*: Não remonta quando parâmetros de query mudam (ex.: mudar capítulo em `BookView` via query `?chapter=`), mantendo estados reativos stale.

---

### D2: Elevação da Variável de Fonte para a Casca Global e Aplicação Irrestrita (Opção B)

- **Diagnóstico Técnico:**
  - Em `frontend/src/fonts.css`, as 24 regras de fonte configuravam exclusivamente a variável `--font-reading`:
    ```css
    :root[data-font="inter"] { --font-reading: "Caderno Inter", sans-serif; }
    ```
  - Em `frontend/src/tokens.css`, a tipografia de interface era definida como:
    ```css
    --font-ui: var(--font-sans);
    --font-reading: var(--font-ui);
    ```
  - E no `frontend/src/style.css`, `:root` recebia `font-family: var(--font-ui);`.
  - Como resultado, quando o usuário trocava a fonte nos Ajustes, apenas `--font-reading` se alterava, afetando somente o corpo do texto dentro de `.markdown-content`. A interface global (cabeçalhos, menus, botões, formulários e o próprio painel de Ajustes) permanecia imóvel com a fonte do sistema (`--font-sans`).
- **Decisão Arquitetural:**
  1. Fazer com que a variável de interface `--font-ui` derive diretamente de `--font-reading` em `tokens.css`:
     ```css
     --font-ui: var(--font-reading);
     ```
  2. Conforme esclarecido pelo usuário (Opção B), aplicar a tipografia selecionada de forma irrestrita a 100% dos elementos da aplicação:
     ```css
     :root, body, #app, button, input, select, textarea, code, pre {
       font-family: var(--font-reading);
     }
     ```
  3. Com essa elevação, qualquer mudança no atributo `data-font` do elemento `<html>` reavalia `--font-reading`, propagando a nova tipografia instantaneamente (em < 50ms) para toda a página.
- **Alternativas Rejeitadas:**
  - *Preservar monospace em blocos de código*: Rejeitado explicitamente pelo usuário na sessão de clarificação (escolha da Opção B: abrangência irrestrita).
  - *Criar seletor separado para fonte de interface*: Rejeitado por sobrecarregar o painel de ajustes com mais opções em vez de simplificá-lo.

---

### D3: Poda de Ajustes Redundantes, Purga de `localStorage` e Renumeração Sequencial Limpa

- **Diagnóstico Técnico:**
  - O formulário de Ajustes apresentava 11 grupos de opções. A consolidação das 5 Superclasses de Interface (Zero-G, Mecânica, Invisível, Dimensional e Monolítica) assumiu completamente a física de movimento, geometria de botões e estética de navegação.
  - A manutenção de `motion`, `button-width` e `tabs` gerava redundância técnica e visual.
- **Decisão Arquitetural:**
  1. **Remoção de Campos**:
     - Remover `'motion'` de `fields` em `appearance-bootstrap.js`.
     - Remover `'button-width'` de `fields` em `appearance-bootstrap.js`.
     - Remover `'tabs'` de `fields` em `appearance-bootstrap.js`.
  2. **Purga Automática no `localStorage`**:
     - Na inicialização de `appearance-bootstrap.js`, a função `normalize()` filtra e remove ativamente resíduos de chaves antigas, regravando o objeto limpo no `localStorage` e removendo atributos residuais do DOM (`data-motion`, `data-button-width`, `data-tabs`):
       ```javascript
       document.documentElement.removeAttribute('data-motion');
       document.documentElement.removeAttribute('data-button-width');
       document.documentElement.removeAttribute('data-tabs');
       ```
  3. **Renumeração Limpa (1 a 7)**:
     - Aparência básica: Tema
     - 1. Cor de destaque (`accent`)
     - 2. Densidade (`density`)
     - 3. Leitura (`font`, `reader-size`, `align`)
     - 4. Marcação (`highlight`)
     - 5. Acervo (`library`) — *renumerado de 9 para 5*
     - 6. Largura da interface (`container`) — *renumerado de 10 para 6*
     - 7. Superclasse de Interface (`superclass`, `superclass-intensity`) — *renumerado de 11 para 7*
  4. **Tipagem TypeScript**:
     - Atualizar [`frontend/src/appearance.d.ts`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/appearance.d.ts) removendo `motion`, `button-width` e `tabs` da interface `AppearancePreferences`.
- **Alternativas Rejeitadas:**
  - *Apenas esconder via CSS*: Manteria código morto, chaves salvas desnecessariamente e testes confusos.
