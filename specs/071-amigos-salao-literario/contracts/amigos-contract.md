# Contrato de Interface e Componentes: F0.8.06 — Amigos: Salão Literário e Círculos de Estudo

**Feature Branch**: `071-amigos-salao-literario`  
**Data**: 2026-10-11  
**Status**: Concluído (Fase 1 do Spec Kit)

---

## 1. Componente: `BookplateCard.vue` (Ex-Líbris Digital do Leitor)

Posicionado no topo de `/amigos`, este componente confere identidade visual permanente ao leitor e facilita a correspondência social.

### 1.1. Propriedades e Eventos

```typescript
export interface BookplateCardProps {
  /** Perfil do usuário logado contendo username, display_name, avatar_url e bio */
  username: string
  displayName: string
  avatarUrl?: string | null
  bio?: string | null
  /** Contagem de amigos ativos no círculo */
  friendsCount: number
  /** Contagem de solicitações pendentes recebidas */
  pendingCount?: number
}
```

```typescript
export interface BookplateCardEmits {
  /** Disparado após a cópia do identificador */
  (e: 'copied', handle: string): void
  /** Disparado ao acionar compartilhamento de perfil */
  (e: 'shared', url: string): void
}
```

### 1.2. Microinteração do Selo de Cópia (`.is-stamped`)

- **Duração**: Exatamente 1200ms.
- **Transição CSS**:
  ```css
  .copy-stamp-btn {
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1),
                background-color 0.2s ease,
                border-color 0.2s ease;
    min-height: 44px;
  }
  .copy-stamp-btn.is-stamped {
    transform: scale(1.04);
    background-color: var(--color-surface-soft);
    border-color: var(--color-primary);
  }
  @media (prefers-reduced-motion: reduce) {
    .copy-stamp-btn.is-stamped {
      transform: none;
    }
  }
  ```
- **Feedback de Voz / Acessibilidade**:
  - Elemento com `aria-live="polite"` anuncia "Identificador copiado para a área de transferência".

### 1.3. Contrato da Web Share API

- **Verificação**: `typeof navigator.share === 'function'`
- **Payload Nativo**:
  ```javascript
  await navigator.share({
    title: `${props.displayName} no Leitorum`,
    text: `Conecte-se com meu caderno literário no Leitorum:`,
    url: `${window.location.origin}/u/${props.username}`
  })
  ```
- **Fallback (Clipboard)**:
  - Caso `navigator.share` seja indefinido ou rejeitado pelo usuário sem erro fatal: copia `${window.location.origin}/u/${props.username}` e exibe selo temporário por 1200ms.

---

## 2. Componente: `FriendsView.vue` (Salão Literário)

A tela orquestra a navegação segmentada, cabeçalho e renderização dos cartões em 4 abas semânticas.

### 2.1. Estrutura WAI-ARIA das Abas

| Elemento | Papel / Atributo ARIA | Valor / Comportamento |
|---|---|---|
| Barra de Abas | `role="tablist"` | `aria-label="Abas da comunidade de amigos"` |
| Aba Círculo | `role="tab"` | `id="tab-friends"`, `aria-selected="true\|false"`, `aria-controls="panel-friends"` |
| Aba Solicitações | `role="tab"` | `id="tab-requests"`, `aria-selected="true\|false"`, `aria-controls="panel-requests"` |
| Aba Descobrir | `role="tab"` | `id="tab-discover"`, `aria-selected="true\|false"`, `aria-controls="panel-discover"` |
| Aba Bloqueados | `role="tab"` | `id="tab-blocked"`, `aria-selected="true\|false"`, `aria-controls="panel-blocked"` |
| Painel Círculo | `role="tabpanel"` | `id="panel-friends"`, `aria-labelledby="tab-friends"` |
| Painel Solicitações | `role="tabpanel"` | `id="panel-requests"`, `aria-labelledby="tab-requests"` |
| Painel Descobrir | `role="tabpanel"` | `id="panel-discover"`, `aria-labelledby="tab-discover"` |
| Painel Bloqueados | `role="tabpanel"` | `id="panel-blocked"`, `aria-labelledby="tab-blocked"` |

### 2.2. Contrato de Cartão de Conexão Literária

- **Identidade do Amigo**:
  - Avatar circular ou iniciais com contraste semântico.
  - Link de navegação direcionado para a estante pública: `/u/:username` (mantendo compatibilidade com `/@:username`).
  - Bio literária truncada elegantemente com `line-clamp-2`.
  - Data de amizade formatada em português: "Amigos desde DD de MMM de AAAA".
- **Ações**:
  - Componente `FriendActionButtons.vue` integrado com `compact="true"` no grid de amigos.

### 2.3. Contrato da Aba "Descobrir Leitores"

- **Campo de Busca**:
  - `type="search"`, `aria-label="Buscar leitores descobríveis"`.
  - Debounce de 300ms entre alterações de `searchQuery`.
  - Cancelamento de requisições anteriores durante nova digitação.
- **Sugestões Editoriais para Busca Vazia**:
  - Quando `searchQuery` estiver vazio, exibe sugestões acolhedoras de temas e perfis recomendados em vez de uma tela vazia estéril.

---

## 3. Componente: `FriendActionButtons.vue`

Gerencia as interações atômicas de relacionamento social com segurança e confirmação defensiva.

### 3.1. Diálogo Defensivo

- **Remoção de Amizade / Bloqueio**:
  - O diálogo modal deve conter `role="dialog"` e `aria-modal="true"`.
  - Botão de cancelamento primário para prevenir desconexões acidentais.
  - Botão de confirmação destrutiva com estilo defensivo.

### 3.2. Ergonomia e Acessibilidade Tátil

- **Alvos Táteis**: Todos os botões interativos (`.action-btn`, `.tab-btn`, `.copy-stamp-btn`) possuem altura mínima de 44px (`min-height: 44px`) e largura mínima de 44px em telas sensíveis ao toque.
- **Estados de Foco**: Foco claramente demarcado via `:focus-visible` respeitando `var(--color-primary)`.

---

## 4. Imunidade Cromática e Diretrizes Visuais

1. **Tokens CSS Obrigatórios**:
   - `var(--color-surface)` / `var(--color-surface-soft)` para planos de fundo de cartões e crachás.
   - `var(--color-border)` / `var(--color-border-subtle)` para delimitações e divisores.
   - `var(--color-text)` / `var(--color-text-muted)` para hierarquia de texto.
   - `var(--color-primary)` / `var(--color-accent)` para realces de marca e links ativos.
2. **Proibição de Hexadecimais Fixos**:
   - Nenhum estilo de componente pode utilizar cores fixas como `#2563eb`, `#dc2626` ou `#ffffff` diretamente em propriedades de texto ou plano de fundo sem fallback semântico.
3. **Zero Emojis**:
   - Proibido qualquer emoji no código, templates ou strings de internacionalização.
   - Todos os símbolos devem ser ícones vetoriais SVG através de `<Icon name="..." />`.
