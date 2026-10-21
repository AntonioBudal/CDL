# Contract: Shell de Navegação e Componente AppBreadcrumb

**Feature**: `specs/082-navegacao-global-shell-responsivo`  
**Date**: 2026-10-20  

---

## 1. Contrato do Componente `AppBreadcrumb.vue`

### Props

```typescript
interface Props {
  items: BreadcrumbItem[]
}
```

### Estrutura Semântica HTML5

```html
<nav class="app-breadcrumb" aria-label="Trilha de navegação">
  <ol class="breadcrumb-list">
    <li v-for="(item, idx) in items" :key="idx" class="breadcrumb-item">
      <RouterLink
        v-if="item.to && !item.current"
        :to="item.to"
        class="breadcrumb-link"
      >
        {{ item.label }}
      </RouterLink>
      <span
        v-else
        class="breadcrumb-current"
        :aria-current="item.current ? 'page' : undefined"
      >
        {{ item.label }}
      </span>
      <span
        v-if="idx < items.length - 1"
        class="breadcrumb-separator"
        aria-hidden="true"
      >/</span>
    </li>
  </ol>
</nav>
```

### Regras de Acessibilidade
- O elemento raiz deve ser `<nav>` com atributo `aria-label="Trilha de navegação"`.
- A lista de passos deve utilizar `<ol>` para explicitar a ordem hierárquica.
- O passo final ativo deve conter `aria-current="page"`.
- O separador visual deve conter `aria-hidden="true"` para não poluir a leitura de tecnologias assistivas.
- Em dispositivos móveis e touch (`pointer: coarse`), links clicáveis devem ter área tátil confortável (padding vertical de no mínimo 8px com alvos de fácil acionamento).

---

## 2. Contrato de Offset e Casca no Mobile (`App.vue`)

### Variáveis e Dimensões
- `--mobile-nav-offset`: Variável padrão já declarada de `calc(56px + env(safe-area-inset-bottom, 0px))`.
- Margem inferior no rodapé quando o usuário está autenticado e fora do modo `cleanScreen`:
  `margin-bottom: calc(var(--mobile-nav-offset, 56px) + env(safe-area-inset-bottom, 0px) + 1.5rem);`
- Respiro inferior em `#conteudo`:
  `padding-bottom: calc(var(--mobile-nav-offset, 56px) + env(safe-area-inset-bottom, 0px));`

---

## 3. Contrato de Itens de Navegação Desktop (`NavigationTabs.vue`)

- `primaryNavItems` deve retornar uma lista estática com exatamente 5 itens:
  1. `Dashboard` (`to: '/dashboard'`)
  2. `Livros` (`to: '/livros'`)
  3. `Destaques` (`to: '/highlights'`)
  4. `Revisão` (`to: '/review'`)
  5. `Inbox` (`to: '/inbox'`)
- Não deve haver condicional baseada em `homeViewPreference` que omita qualquer um dos 5 itens primários da lista.
