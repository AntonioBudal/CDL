# Component Contract: `DropdownMenu.vue`

**Componente**: `frontend/src/components/ui/DropdownMenu.vue`  
**Objetivo**: Fornecer um contêiner suspenso reutilizável e totalmente acessível para ações secundárias e utilitárias.

---

## 1. Props

| Prop | Tipo | Padrão | Descrição |
|---|---|---|---|
| `align` | `'left' \| 'right'` | `'right'` | Alinhamento horizontal da lista suspensa em relação ao botão disparador. |
| `ariaLabel` | `string` | `'Mais opções'` | Rótulo acessível atribuído ao botão disparador para leitores de tela. |
| `disabled` | `boolean` | `false` | Se o disparador do menu está desabilitado para interação. |

---

## 2. Slots

| Slot | Parâmetros | Descrição |
|---|---|---|
| `trigger` | `{ isOpen: boolean, toggle: () => void }` | Slot opcional para customizar o botão disparador. Se omitido, renderiza o botão padrão com ícone `•••`. |
| `default` | `{ close: () => void }` | Conteúdo interno do menu suspenso (itens, links e botões). |

---

## 3. Emits

| Evento | Payload | Descrição |
|---|---|---|
| `open` | `void` | Emitido quando o menu suspenso é aberto. |
| `close` | `void` | Emitido quando o menu suspenso é fechado. |

---

## 4. Contrato Semântico e Acessibilidade (WAI-ARIA)

```html
<div class="dropdown-menu-container">
  <button
    type="button"
    class="dropdown-trigger"
    aria-haspopup="menu"
    :aria-expanded="isOpen"
    :aria-label="ariaLabel"
    @click="toggle"
    @keydown="onTriggerKeydown"
  >
    <!-- Slot trigger ou ícone padrão ••• -->
  </button>

  <div
    v-if="isOpen"
    role="menu"
    class="dropdown-content"
    aria-orientation="vertical"
    tabindex="-1"
    @keydown="onMenuKeydown"
  >
    <slot :close="close" />
  </div>
</div>
```

---

## 5. Eventos de Teclado Suportados

- **No disparador**:
  - `Enter` / `Space` / `ArrowDown`: abre o menu e foca no primeiro item elegível.
- **Dentro do menu**:
  - `Escape`: fecha o menu e retorna o foco para o disparador.
  - `ArrowDown`: move o foco para o próximo item (circular).
  - `ArrowUp`: move o foco para o item anterior (circular).
  - `Home`: move o foco para o primeiro item.
  - `End`: move o foco para o último item.
  - `Tab`: fecha o menu e permite navegação natural do documento.
