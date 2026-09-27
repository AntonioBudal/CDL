# UI Contract: Barra de Ações Contextuais e Interação com Destaques

**Componente Principal**: `FloatingActionsToolbar.vue`  
**Componente Secundário**: `HighlightActionPopover.vue`  
**Composables**: `useTextSelection.ts`, `useStudyHighlights.ts`  

---

## 1. FloatingActionsToolbar.vue

### Props

| Prop | Tipo | Obrigatório | Padrão | Descrição |
|:---|:---|:---:|:---|:---|
| `visible` | `boolean` | Sim | `false` | Indica se a barra deve ser renderizada na tela |
| `selection` | `TextSelectionContext \| null` | Sim | `null` | Metadados do trecho selecionado e sua caixa delimitadora |
| `studyTitle` | `string` | Sim | `""` | Título do estudo para compor metadados de citação |
| `bookTitle` | `string` | Não | `""` | Título da obra/livro |
| `chapterName`| `string` | Não | `""` | Nome do capítulo |
| `canEdit` | `boolean` | Não | `true` | Se falso, apenas a ação de citação fica habilitada |

### Emits

| Evento | Payload | Descrição |
|:---|:---|:---|
| `highlight` | `{ color: HighlightColor }` | Disparado ao selecionar uma cor de marca-texto |
| `annotate` | `{ note: string, color: HighlightColor }` | Disparado ao submeter uma reflexão para o trecho |
| `copy-quote` | `void` | Disparado ao copiar o trecho formatado como citação |
| `occlude` | `void` | Disparado para ocultar o trecho (Active Recall) |
| `ask-question` | `{ question: string }` | Disparado ao configurar uma pergunta para o trecho |
| `close` | `void` | Disparado ao fechar a barra (Escape, clique fora ou após ação) |

### Regras de Posicionamento e Responsividade
1. **Desktop (`window.innerWidth > 768px`)**:
   - `position: fixed`
   - O elemento calcula `top = selection.boundingRect.top - toolbarHeight - 10px`.
   - Se `top < 10px`, inverte para `top = selection.boundingRect.bottom + 10px`.
   - `left` é centralizado na seleção: `selection.boundingRect.left + (selection.boundingRect.width / 2) - (toolbarWidth / 2)`.
   - Aplica `clamp(10px, left, window.innerWidth - toolbarWidth - 10px)` para evitar cortes nas bordas.
2. **Mobile (`window.innerWidth <= 768px`)**:
   - `position: fixed; bottom: 0; left: 0; right: 0;`
   - Painel ancorado na base no formato *bottom action bar*.
   - Botões com tamanho mínimo de `44px x 44px` e espaçamento para toques confortáveis.
   - Respeita `env(safe-area-inset-bottom)` para evitar a barra de navegação de iPhones/Androids.

---

## 2. HighlightActionPopover.vue (Gestão do Destaque Existente)

Renderizado adjacente ao elemento `<mark>` ou `<span>` quando o usuário clica sobre um trecho já destacado.

### Ações Disponíveis
1. **Trocar Cor**: Seletor rápido de 5 cores (`yellow`, `green`, `blue`, `pink`, `purple`).
2. **Editar Nota / Pergunta**: Abre campo de texto com o valor atual para alteração.
3. **Alternar Revelação (se oculto/pergunta)**: Botão rápido para esconder ou mostrar o texto.
4. **Remover**: Ícone de lixeira para excluir a marcação e restaurar o texto padrão.
