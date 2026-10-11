# Modelo de Dados e Estados Reativos: F0.8.04 — Inbox: Mesa de Triagem e Despejo Intelectual

**Feature Branch**: `070-inbox-mesa-triagem`  
**Data**: 2026-10-11  
**Status**: Concluído (Fase 1 do Spec Kit)

---

## 1. Entidades de Dados (Frontend / API)

A Feature F0.8.04 utiliza os contratos já estabelecidos na API REST do backend (`backend/app/routers/inbox.py`). Nenhuma tabela ou campo do banco de dados SQLite é alterado.

### 1.1. `InboxCapture` (Registro de Captura)

Representa uma nota efêmera capturada pelo leitor antes ou durante sua triagem.

| Campo | Tipo | Descrição | Regras de Validação |
|---|---|---|---|
| `id` | `number` | Identificador único autoincrementado da captura. | Obrigatório, inteiro positivo. |
| `content` | `string` | Texto original do pensamento, citação ou reflexão. | Obrigatório, não vazio (trim), sem limite artificial rígido (suporta notas longas). |
| `source_hint` | `string \| null` | Referência ou contexto de origem (ex.: livro, autor, página). | Opcional, texto curto sanitizado. |
| `status` | `InboxStatus` | Estado da captura no ciclo de triagem. | Valores: `'inbox'`, `'promoted'`, `'linked'`, `'archived'`. |
| `book_id` | `number \| null` | Identificador do livro ao qual a captura foi associada. | Opcional, referência a livro existente. |
| `book_title` | `string \| null` | Título do livro associado (preenchido para exibição rápida). | Opcional, leitura apenas. |
| `promoted_study_id` | `number \| null` | ID do estudo gerado a partir da promoção da captura. | Opcional, presente quando `status === 'promoted'`. |
| `promoted_study_title`| `string \| null` | Título do estudo formal promovido. | Opcional, leitura apenas. |
| `created_at` | `string` | Timestamp ISO 8601 da criação do registro. | Formato UTC ISO. |
| `updated_at` | `string` | Timestamp ISO 8601 da última alteração. | Formato UTC ISO. |

---

## 2. Tipos e Enums de Triagem

### 2.1. `InboxStatus`
Representa os 4 estados fundamentais do ciclo de vida da nota:
- `'inbox'`: Nota pendente de triagem (residente na mesa ativa).
- `'promoted'`: Nota promovida a estudo formal no Ateliê de Fichamento.
- `'linked'`: Nota anexada diretamente a um livro ou estudo existente.
- `'archived'`: Nota arquivada pelo leitor (processada e retirada da mesa).

### 2.2. `TriageFilterTab`
Filtros disponíveis na barra segmentada de triagem:
```typescript
export type TriageFilterTab = 'inbox' | 'promoted' | 'linked' | 'archived' | 'all'
```

---

## 3. Modelos de Estado Reativo de Interface (UI State)

### 3.1. Estado do Quick Thought Drop (`QuickThoughtDrop.vue`)

Gerencia a digitação rápida, expansão de altura e salvamento imediato no topo da mesa.

```typescript
interface QuickThoughtDropState {
  /** Conteúdo do pensamento sendo digitado */
  content: string
  /** Dica ou fonte opcional associada ao pensamento */
  sourceHint: string
  /** Indica se a caixa está expandida (ao receber foco ou ter conteúdo digitado) */
  isFocused: boolean
  /** Indica se a requisição de salvamento está em andamento */
  isSubmitting: boolean
  /** Mensagem editorial de erro caso a persistência falhe */
  error: string | null
}
```

**Regras de Transição de Estado:**
- Ao receber foco (`focusin`): `isFocused = true` $\rightarrow$ CSS expande a caixa para até 4 linhas (~120px) em $\le 200$ms.
- Ao perder foco (`focusout`): se `content.trim() === ''`, `isFocused = false` $\rightarrow$ recolhe para 1 linha. Se contiver texto, mantém expandido para evitar perda visual.
- Ao pressionar `Ctrl+Enter` / `Cmd+Enter`:
  - Se `content.trim() === ''`: nenhuma ação (rejeição silenciosa).
  - Se válido: `isSubmitting = true`, dispara chamada de criação, emite evento `created`, limpa `content` e `sourceHint`, e recolhe a caixa.

---

### 3.2. Estado de Navegação por Teclado na Mesa (`InboxView.vue`)

Gerencia o foco contextual e atalhos ergonômicos `J`, `K` e `E`.

```typescript
interface TriageKeyboardState {
  /** Índice do cartão atualmente destacado para navegação rápida */
  selectedIndex: number
  /** Guarda de proteção contra acionamento involuntário */
  isInputFocused: boolean
}
```

**Regras de Atualização:**
- Pressionar `J`: incrementa `selectedIndex` (limitado ao total de itens visíveis - 1). Rola o cartão até a visão com suavidade se necessário.
- Pressionar `K`: decrementa `selectedIndex` (mínimo 0).
- Pressionar `E`: dispara a ação de arquivamento no item de índice `selectedIndex`. O item entra em animação de saída; `selectedIndex` permanece no mesmo índice ou recua 1 se for o último elemento da lista.
- Tecla `Ctrl+Shift+C`: foca imediatamente no `textarea` do `QuickThoughtDrop` e redefine `selectedIndex = -1`.

---

### 3.3. Estado de Animação Cinética dos Cartões

Gerencia a remoção suave dos itens arquivados ou excluídos sem saltos abruptos de layout.

```typescript
interface TriageAnimationState {
  /** Conjunto de IDs de capturas que estão em fase de transição de saída */
  exitingIds: Set<number>
  /** Duração máxima da animação antes do descarte reativo do array */
  durationMs: 180
}
```

**Ciclo de Remoção:**
1. O usuário clica em "Arquivar" ou pressiona `E`.
2. O `id` do item é adicionado a `exitingIds`.
3. O template do cartão aplica a classe CSS `.is-exiting` com `transform: translateX(30px)` e `opacity: 0` (180ms).
4. A API é invocada em paralelo (`api.updateInboxCapture(id, { status: 'archived' })`).
5. Ao término de 180ms, o item é removido do array `captures.value` e `exitingIds.delete(id)`.
6. O contador de pendências decrementa.

---

### 3.4. Contadores Dinâmicos da Barra Segmentada

Estrutura que alimenta os badges numéricos de cada segmento da barra:

```typescript
interface TriageSegmentCounts {
  inbox: number     // Total de pendências na mesa
  promoted: number  // Total de notas promovidas
  linked: number    // Total de notas vinculadas
  archived: number  // Total de notas arquivadas
  all: number       // Soma total de registros
}
```
