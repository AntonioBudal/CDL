# UI Component Contracts: F09 - Sistema Visual Profissional

**Branch**: `017-sistema-visual-profissional`  
**Feature**: F09 — Sistema Visual Profissional  
**Data**: 2026-09-19  

Este documento define os contratos de interface, props, slots, eventos e acessibilidade para os novos componentes de UI do Sistema Visual Profissional.

---

## 1. Contrato: `Icon.vue`

**Caminho do componente:** `frontend/src/components/ui/Icon.vue`  
**Objetivo:** Renderizar glifos vetoriais Lucide de forma consistente, com tree-shaking e acessibilidade garantida.

### Props

| Propriedade | Tipo | Obrigatório | Padrão | Descrição |
| :--- | :--- | :---: | :--- | :--- |
| `name` | `IconName` | Sim | — | Nome do ícone cadastrado no catálogo (ex.: `'book-open'`, `'trash'`, `'pencil'`) |
| `size` | `number \| string` | Não | `20` | Dimensão em pixels da largura e altura |
| `strokeWidth` | `number \| string` | Não | `2` | Espessura do traço vetorial (1.5 a 2.5) |
| `ariaLabel` | `string` | Não | `undefined` | Texto descritivo para leitor de tela (se presente, define `role="img"`) |

### Comportamento de Acessibilidade
- Se `ariaLabel` for informado: renderiza `<svg role="img" :aria-label="ariaLabel" ...>`
- Se `ariaLabel` for omitido: renderiza `<svg aria-hidden="true" focusable="false" ...>`

### Exemplo de Uso
```vue
<script setup lang="ts">
import Icon from '@/components/ui/Icon.vue'
</script>

<template>
  <!-- Ícone decorativo em botão com texto visível -->
  <button class="action-btn">
    <Icon name="plus" :size="16" />
    <span>Novo Estudo</span>
  </button>

  <!-- Botão de ação puramente iconográfico -->
  <button class="icon-only-btn" title="Excluir item">
    <Icon name="trash" :size="18" aria-label="Excluir item" />
  </button>
</template>
```

---

## 2. Contrato: `EmptyState.vue`

**Caminho do componente:** `frontend/src/components/ui/EmptyState.vue`  
**Objetivo:** Oferecer uma área de feedback visual acolhedora para seções e listas que não possuem itens cadastrados ou filtrados.

### Props

| Propriedade | Tipo | Obrigatório | Padrão | Descrição |
| :--- | :--- | :---: | :--- | :--- |
| `icon` | `IconName` | Sim | — | Ícone central do estado vazio |
| `title` | `string` | Sim | — | Título explicativo |
| `description` | `string` | Não | `''` | Texto complementar de orientação |
| `headingLevel` | `'h2' \| 'h3' \| 'h4'` | Não | `'h2'` | Tag de cabeçalho renderizada para estrutura semântica |

### Slots

| Slot | Descrição |
| :--- | :--- |
| `default` | Área para botões de ação ou links secundários (opcional) |

### Exemplo de Uso
```vue
<template>
  <EmptyState
    icon="trash"
    title="Lixeira limpa"
    description="Nenhum estudo ou livro foi movido para a lixeira recentemente."
  >
    <RouterLink to="/" class="button">Voltar ao Acervo</RouterLink>
  </EmptyState>
</template>
```

---

## 3. Contrato: `LoadingSkeleton.vue`

**Caminho do componente:** `frontend/src/components/ui/LoadingSkeleton.vue`  
**Objetivo:** Placeholder visual com proporções fiéis ao conteúdo em carregamento para evitar *layout shift* (CLS).

### Props

| Propriedade | Tipo | Obrigatório | Padrão | Descrição |
| :--- | :--- | :---: | :--- | :--- |
| `shape` | `'rect' \| 'circle' \| 'text'` | Não | `'rect'` | Forma geométrica do bloco |
| `width` | `string` | Não | `'100%'` | Largura em CSS |
| `height` | `string` | Não | `'1.25rem'` | Altura em CSS |
| `lines` | `number` | Não | `1` | Número de linhas simuladas para texto |
| `gap` | `string` | Não | `'0.5rem'` | Espaçamento entre linhas |

### Comportamento de Acessibilidade
- Renderiza com `aria-busy="true"` e `aria-live="polite"` no contêiner ou elemento raiz.
- Inclui texto oculto para leitores de tela: `<span class="sr-only">Carregando conteúdo…</span>`.
- Respeita `@media (prefers-reduced-motion: reduce)` desativando animações de brilho e mantendo contraste estático.

### Exemplo de Uso
```vue
<template>
  <!-- Esqueleto para um card de livro -->
  <div class="book-card-skeleton">
    <LoadingSkeleton width="100%" height="220px" shape="rect" />
    <LoadingSkeleton width="80%" height="1.5rem" shape="text" class="mt-2" />
    <LoadingSkeleton width="50%" height="1rem" shape="text" class="mt-1" />
  </div>
</template>
```

---

## 4. Contrato: `StatusBadge.vue`

**Caminho do componente:** `frontend/src/components/ui/StatusBadge.vue`  
**Objetivo:** Pílula visual para rótulos de taxonomia, categorias e contadores.

### Props

| Propriedade | Tipo | Obrigatório | Padrão | Descrição |
| :--- | :--- | :---: | :--- | :--- |
| `variant` | `'neutral' \| 'accent' \| 'warning' \| 'danger' \| 'success'` | Não | `'neutral'` | Paleta cromática |
| `icon` | `IconName` | Não | `undefined` | Ícone opcional exibido antes do texto |
| `label` | `string` | Sim | — | Rótulo textual |

### Exemplo de Uso
```vue
<template>
  <StatusBadge variant="accent" icon="book-open" label="Filosofia" />
  <StatusBadge variant="warning" icon="flame" label="3 dias seguidos" />
</template>
```
