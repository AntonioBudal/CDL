# Research: F0.9.01 — Arquitetura de Navegação Global e Shell Responsivo

**Feature**: `specs/082-navegacao-global-shell-responsivo`  
**Date**: 2026-10-20  

---

## 1. Problema e Diagnóstico: Ocultação da Aba de Livros no Desktop

### Pergunta de Pesquisa
Por que o acesso à biblioteca de livros (`/books` ou `/livros`) é perdido quando o usuário escolhe iniciar no Dashboard?

### Evidências no Código
No arquivo [`frontend/src/components/layout/NavigationTabs.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/layout/NavigationTabs.vue#L43-L51):
```typescript
const primaryNavItems = computed<PrimaryNavItem[]>(() => {
  const isDashboardHome = props.homeViewPreference === 'dashboard'
  return [
    {
      to: isDashboardHome ? '/dashboard' : '/livros',
      label: isDashboardHome ? 'Dashboard' : 'Livros',
      routes: ['books', 'book', 'study', 'study-edit', 'dashboard'],
      icon: isDashboardHome ? 'layout-dashboard' : 'book-open',
    },
    ...
```

### Análise e Decisão
1. **Falha de Design:** A primeira aba alternava dinamicamente entre Dashboard ou Livros de acordo com `homeViewPreference`. Como a rota não selecionada não constava nem em `primaryNavItems` nem em `secondaryNavItems`, o usuário ficava sem rota direta para o acervo.
2. **Decisão:** Separar as duas rotas em abas explícitas na barra superior:
   - Item 1: `Dashboard` (`to: '/dashboard'`, `routes: ['dashboard']`, `icon: 'layout-dashboard'`)
   - Item 2: `Livros` (`to: '/livros'`, `routes: ['books', 'book', 'study', 'study-edit']`, `icon: 'book-open'`)
   - Item 3: `Destaques` (`to: '/highlights'`, `routes: ['highlights']`, `icon: 'pencil'`)
   - Item 4: `Revisão` (`to: '/review'`, `routes: ['review', 'study-session']`, `icon: 'rotate-ccw'`)
   - Item 5: `Inbox` (`to: '/inbox'`, `routes: ['inbox']`, `icon: 'inbox'`)
   - Menu Retrátil: `Mais ▾` (Importar, Amigos, Ajustes, Lixeira, Admin)
3. **Comportamento da Preferência `homeViewPreference`:** A preferência continuará ativa para definir o link do logotipo "Leitorum" no `GlobalHeader` e o redirecionamento pós-login, mas não suprime abas de navegação.

---

## 2. Problema e Diagnóstico: Sobreposição da Barra Fixa Móvel no App Shell

### Pergunta de Pesquisa
Por que o rodapé (`.app-footer`) e o conteúdo final de telas móveis sofrem sobreposição pela barra fixa inferior?

### Evidências no Código
No arquivo [`frontend/src/App.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/App.vue#L163-L175):
```css
.app-footer {
  width: min(100% - var(--page-gutter, 2rem), var(--workspace-max-width, 74rem));
  margin: calc(var(--space-unit, 1rem) * 4) auto calc(var(--space-unit, 1rem) * 3);
  ...
}
```
No arquivo [`frontend/src/components/layout/MobileTabBar.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/layout/MobileTabBar.vue#L100-L110):
```css
.mobile-tab-bar {
  position: fixed;
  inset: auto 0 0;
  z-index: 80;
  min-height: 56px;
  height: var(--mobile-nav-offset, calc(56px + env(safe-area-inset-bottom, 0px)));
}
```

### Análise e Decisão
1. **Falha de Design:** A `MobileTabBar` tem posicionamento fixo (`position: fixed; bottom: 0`). Como `.app-footer` possui margem inferior padrão sem considerar a altura fixa da barra móvel (`56px + safe-area`), o rodapé fica ocultado sob a barra.
2. **Decisão:** No arquivo `App.vue`, adicionar regra responsiva para dispositivos móveis (`max-width: 767px`) quando o usuário estiver autenticado:
```css
@media (max-width: 767px) {
  .app-footer {
    margin-bottom: calc(var(--mobile-nav-offset, 56px) + env(safe-area-inset-bottom, 0px) + 1.5rem);
  }
}
```
Adicionalmente, assegurar que o contêiner `#conteudo` possua respiro inferior seguro em páginas sem rodapé.

---

## 3. Problema e Diagnóstico: Trilha de Navegação (Breadcrumb) Dispersa e com Desvio de Rota

### Pergunta de Pesquisa
Quais componentes usam breadcrumbs atualmente e por que ocorrem redirecionamentos para a raiz `"/"`?

### Evidências no Código
- [`BookView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/BookView.vue#L311): `<RouterLink to="/">Meus livros</RouterLink>`
- [`StudyView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/StudyView.vue#L484): `<RouterLink to="/">Meus livros</RouterLink>`
- [`StudyEditView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/StudyEditView.vue#L133): `<RouterLink to="/">Meus livros</RouterLink>`
- [`UserProfileView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/UserProfileView.vue#L89): `<RouterLink to="/" class="back-link">`

### Análise e Decisão
1. **Falha de Design:** O rótulo "Meus livros" aponta para `"/"`. Se a preferência for `dashboard`, o leitor clica em "Meus livros" e cai no Dashboard. Além disso, cada tela implementa sua própria estilização com `<span>/</span>`, violando padrões de semântica e acessibilidade.
2. **Decisão:** Criar componente canônico `frontend/src/components/ui/AppBreadcrumb.vue`:
   - Utiliza `<nav aria-label="Trilha de navegação">` e lista `<ol>`/`<li>`.
   - Elemento atual recebe `aria-current="page"`.
   - Primeiro item sempre aponta explicitamente para `/livros` ou `/books` quando o rótulo for "Livros" ou "Meus livros".
   - Tipagem compartilhada em `frontend/src/types/navigation.ts`.
   - Truncamento gracioso via CSS (`text-overflow: ellipsis`) para títulos longos de livros e estudos.

---

## 4. Problema e Diagnóstico: Duplicidade de Gatilhos "Mais" no Mobile

### Pergunta de Pesquisa
Por que o gatilho `.mobile-more-trigger` em `GlobalHeader.vue` está oculto por `display: none !important`?

### Evidências no Código
Em [`GlobalHeader.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/layout/GlobalHeader.vue#L146-L154):
```html
<button
  type="button"
  class="mobile-more-trigger mobile-only"
  aria-label="Mais opções de navegação móvel"
  @click="emit('open-mobile-more')"
>
  <Icon name="more-horizontal" :size="20" />
</button>
```
E no CSS (linha 458):
```css
@media (max-width: 767px) {
  .mobile-more-trigger {
    display: none !important;
  }
}
```

### Análise e Decisão
1. **Falha de Design:** O botão existia tanto no cabeçalho quanto na barra de abas inferior móvel ([`MobileTabBar.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/layout/MobileTabBar.vue#L73-L89)), criando duplicação. Uma regra de CSS ocultou forçadamente o botão do header, mas o elemento continua sendo instanciado no template.
2. **Decisão:** Remover o botão inoperante do `GlobalHeader.vue`, mantendo o menu "Mais" exclusivamente como o 5º botão da `MobileTabBar.vue`.
