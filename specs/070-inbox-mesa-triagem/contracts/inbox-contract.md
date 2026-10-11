# Contratos de Interface & UI: F0.8.04 — Inbox: Mesa de Triagem e Despejo Intelectual

**Feature Branch**: `070-inbox-mesa-triagem`  
**Data**: 2026-10-11  
**Status**: Concluído (Fase 1 do Spec Kit)

---

## 1. Contratos de Componentes Vue

### 1.1. `QuickThoughtDrop.vue` (Campo Permanente Superior)

Componente dedicado posicionado no topo da Mesa de Triagem para captura imediata.

#### Props
```typescript
interface QuickThoughtDropProps {
  /** Placeholder customizado (opcional) */
  placeholder?: string
  /** Se o componente deve receber foco automático na montagem (opcional, default: false) */
  autoFocus?: boolean
}
```

#### Emits
```typescript
interface QuickThoughtDropEmits {
  /** Emitido imediatamente após o salvamento bem-sucedido de uma nova captura */
  (e: 'created', capture: InboxCapture): void
}
```

#### Elementos e Classes Semânticas
- Container: `.quick-thought-drop`, com modificador `:focus-within` $\rightarrow$ `.is-expanded`.
- Área de Texto: `textarea.quick-drop-input`, com `rows="1"` e transição de altura para 4 linhas (`min-height: 110px`, $\le 200$ms).
- Barra de Ações: `.quick-drop-actions`, visível quando expandido.
  - Campo de Origem: `input.quick-drop-source`, placeholder `"Fonte / autor (opcional)"`.
  - Atalho Visual: `kbd.shortcut-hint` com texto `"Ctrl+Enter para despejar"`.
  - Botão Primário: `button.button.primary.quick-drop-submit` com texto `"Despejar Pensamento"`.

#### Acessibilidade (WAI-ARIA)
- `aria-label="Campo de descarrego mental rápido para o Inbox"`
- `aria-keyshortcuts="Control+Enter"`
- Mensagens de erro de envio renderizadas com `role="alert"` e estilo editorial.

---

### 1.2. `CaptureItemCard.vue` (Redesenho do Cartão de Triagem)

Exibe cada nota com ferramentas contextuais de triagem direta e animação cinética de saída.

#### Props
```typescript
interface CaptureItemCardProps {
  /** Objeto de captura a ser exibido */
  capture: InboxCapture
  /** Indica se o cartão está selecionado via teclado (J/K) */
  isSelected?: boolean
  /** Indica se o cartão está em fase de saída/animação */
  isExiting?: boolean
}
```

#### Emits
```typescript
interface CaptureItemCardEmits {
  /** Aciona a promoção para estudo formal */
  (e: 'promote', capture: InboxCapture): void
  /** Abre o modal de vinculação a livro/estudo */
  (e: 'link', capture: InboxCapture): void
  /** Dispara arquivamento da nota */
  (e: 'archive', capture: InboxCapture): void
  /** Dispara desarquivamento da nota */
  (e: 'unarchive', capture: InboxCapture): void
  /** Notifica atualização inline (edição de texto) */
  (e: 'updated', capture: InboxCapture): void
  /** Notifica exclusão do registro */
  (e: 'deleted', captureId: number): void
}
```

#### Ferramentas de Triagem e Ações no Rodapé
- **Promover**: `button.button-triage-promote` $\rightarrow$ Navega para `/importar?promote_inbox_id={id}`.
- **Vincular**: `button.button-triage-link` $\rightarrow$ Abre `LinkToStudyModal.vue`.
- **Arquivar**: `button.button-triage-archive` $\rightarrow$ Executa transição cinética de saída e altera status para `'archived'`.
- **Desarquivar** (para notas na aba Arquivados): `button.button-triage-unarchive` $\rightarrow$ Retorna nota para status `'inbox'`.
- **Excluir**: `button.button-triage-delete` $\rightarrow$ Confirmação defensiva e remoção permanente.

#### Estilos e Transição Cinética
- Classe de saída: `.is-exiting`:
  ```css
  .capture-card.is-exiting {
    transform: translateX(30px);
    opacity: 0;
    transition: transform 180ms cubic-bezier(0.2, 0, 0, 1), opacity 180ms ease;
    pointer-events: none;
  }
  @media (prefers-reduced-motion: reduce) {
    .capture-card.is-exiting {
      transform: none;
      opacity: 0;
      transition: opacity 100ms ease;
    }
  }
  ```
- Seleção por Teclado: `.is-keyboard-selected`:
  ```css
  .capture-card.is-keyboard-selected {
    outline: 2px solid var(--color-accent);
    outline-offset: 2px;
  }
  ```

---

### 1.3. `InboxView.vue` (Mesa de Triagem)

Estrutura mestre que orquestra a captura, os filtros e a listagem.

#### Estrutura Visual
1. **Cabeçalho Editorial**:
   - Título: `"Mesa de Triagem"`
   - Subtítulo: `"Descarrego imediato e organização de notas provisórias do seu ateliê."`
2. **Quick Thought Drop**:
   - Instância de `QuickThoughtDrop.vue` no topo, conectada ao array `captures.value`.
3. **Barra Segmentada de Triagem**:
   - Elemento `<nav class="triage-segmented-bar" role="tablist">`
   - Segmentos:
     - `Pendentes` (`inbox`): com badge numérico destacado.
     - `Promovidos` (`promoted`)
     - `Vinculados` (`linked`)
     - `Arquivados` (`archived`)
     - `Todos` (`all`)
   - Busca inline: campo de busca integrado com debounce (250ms).
4. **Área de Conteúdo**:
   - Estado de Carregamento: spinner editorial.
   - Estado de Erro Editorial: container com `role="alert"`, título amigável e botão "Tentar novamente" (banimento de "Not Found" cru).
   - Estado Vazio "Mesa Limpa": mensagem serena para leitor com mesa vazia e ícone vetorial SVG (zero emojis).
   - Lista de Capturas: grid responsivo renderizando instâncias de `CaptureItemCard.vue`.

---

## 2. Contratos de Acessibilidade (WAI-ARIA & Teclado)

| Alvo | Atributo / Padrão | Comportamento |
|---|---|---|
| Barra Segmentada | `role="tablist"` | Agrupa os botões de filtro. |
| Botões de Segmento | `role="tab"`, `aria-selected="true\|false"`, `aria-controls="triage-list"` | Informa o estado de seleção ativo para leitores de tela. |
| Campo Quick Drop | `aria-label`, `aria-keyshortcuts="Control+Enter"` | Identifica o propósito e atalho de acionamento. |
| Atalhos `J` / `K` | `keydown` sem input ativo | Percorre os cartões da mesa ajustando `is-keyboard-selected`. |
| Atalho `E` | `keydown` sem input ativo | Arquiva o cartão selecionado via teclado. |
| Atalho `Ctrl+Shift+C` | Global `keydown` | Foca o campo `QuickThoughtDrop` em qualquer ponto da tela `/inbox`. |
| Alvos Móveis | `min-height: 44px`, `min-width: 44px` | Ergonomia tátil para toque em smartphones e tablets. |

---

## 3. Contratos de Imunidade Cromática (Design System dos 10 Temas)

Todos os elementos da Mesa de Triagem consomem estritamente os tokens CSS declarados no tema ativo:

| Token Semântico | Aplicação no Inbox |
|---|---|
| `var(--color-bg)` | Fundo geral da página. |
| `var(--color-surface)` | Fundo dos cartões, caixa do Quick Drop e barra segmentada. |
| `var(--color-surface-hover)` | Fundo em hover e segmento inativo ao passar o mouse. |
| `var(--color-border)` | Borda padrão dos cartões e separadores. |
| `var(--color-border-subtle)` | Divisores internos suaves e borda de cartões desativados. |
| `var(--color-text)` | Títulos, conteúdo principal das notas e rótulos. |
| `var(--color-text-muted)` | Datas, fontes de citação e dicas de atalhos. |
| `var(--color-primary)` | Botão principal de despejo e badge de pendências. |
| `var(--color-accent)` | Anel de foco acessível e indicadores ativos. |

**Proibição Absoluta**: Nenhuma cor hexadecimal pura (como `#2563eb`, `#111827`, etc.) pode ser utilizada diretamente nos arquivos CSS/Vue da feature.
