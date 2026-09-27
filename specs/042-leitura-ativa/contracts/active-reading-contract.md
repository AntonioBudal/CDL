# Interface Contract: ActiveReadingBar.vue & Leitura Ativa

**Feature**: [spec.md](../spec.md) | **Date**: 2026-09-27

---

## 1. Componente: `ActiveReadingBar.vue`

Barra contextual de estudo ativo renderizada no topo da área de leitura do estudo quando o modo está ativado.

### Props

| Prop | Tipo | Obrigatório | Padrão | Descrição |
| :--- | :--- | :---: | :--- | :--- |
| `active` | `boolean` | Sim | `false` | Indica se a barra de estudo ativo está visível e operante |
| `revealedCount` | `number` | Sim | `0` | Quantidade de trechos revelados na seção ativa atual |
| `totalCount` | `number` | Sim | `0` | Quantidade total de trechos interativos (ocluídos + perguntas) na seção |
| `completionPercentage` | `number` | Sim | `0` | Percentual de conclusão da rodada (0 a 100) |
| `currentIndex` | `number` | Não | `-1` | Índice do trecho atualmente sob foco na navegação sequencial |

### Emits

| Evento | Payload | Descrição |
| :--- | :--- | :--- |
| `reveal-all` | `void` | Disparado ao clicar no botão "Revelar todos" |
| `hide-all` | `void` | Disparado ao clicar no botão "Ocultar todos" |
| `next` | `void` | Disparado ao clicar em "Próximo trecho" ou atalho `J` / `Seta Abaixo` |
| `previous` | `void` | Disparado ao clicar em "Trecho anterior" ou atalho `K` / `Seta Acima` |
| `close` | `void` | Disparado ao encerrar o modo de Leitura Ativa ou via tecla `Escape` |

---

## 2. Acionador no `ReaderTools.vue`

Na barra de ferramentas superior do leitor (`ReaderTools.vue`), é adicionado um controle de comutação da Leitura Ativa:

```html
<button
  type="button"
  class="tool-btn active-reading-toggle"
  :class="{ 'is-active': activeReadingEnabled }"
  :title="activeReadingEnabled ? 'Desativar Leitura Ativa' : 'Ativar Leitura Ativa (Active Recall)'"
  aria-label="Alternar modo de leitura ativa"
  @click="toggleActiveReading"
>
  <svg class="w-4 h-4" ... />
  <span>Leitura Ativa</span>
  <span v-if="interactiveCount > 0" class="badge-count">{{ interactiveCount }}</span>
</button>
```

---

## 3. Extensão do Utilitário `highlightRenderer.ts`

Para sincronizar o estado visual sem recriar elementos do DOM:

### Métodos Exportados

```ts
/**
 * Alterna todos os nós interativos dentro do root para o estado revelado ou oculto.
 */
export function setHighlightsRevealedState(
  root: HTMLElement,
  revealed: boolean,
  onToggleCallback?: (id: number, isRevealed: boolean) => void
): void

/**
 * Foca e centraliza a visão suavemente no nó DOM do destaque especificado.
 */
export function scrollAndFocusHighlight(
  root: HTMLElement,
  highlightId: number
): boolean

/**
 * Coleta a lista de identificadores dos destaques interativos presentes no DOM do container.
 */
export function collectInteractiveHighlights(
  root: HTMLElement
): { id: number; kind: 'hidden' | 'question'; isRevealed: boolean }[]
```

---

## 4. Acessibilidade e Semântica WAI-ARIA

1. **Toolbar Semântica**:
   - `role="region"` com `aria-label="Barra de Leitura Ativa"`.
   - Contador de progresso com `aria-live="polite"` para atualização anunciada a leitores de tela sem interrupção agressiva.
2. **Botões de Ação**:
   - Cada botão possui rótulo textual e `aria-label` explícito.
   - Alvos mínimos de toque em telas móveis: `min-width: 44px; min-height: 44px;`.
3. **Navegação por Teclado**:
   - Teclas `J` e `K` (ou setas direcionais) movimentam o foco entre os trechos interativos da página.
   - Tecla `Escape` fecha o modo de leitura ativa.
