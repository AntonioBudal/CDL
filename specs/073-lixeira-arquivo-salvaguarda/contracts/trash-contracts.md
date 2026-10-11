# Contratos de Componentes e Interface: Lixeira — Arquivo de Salvaguarda

Este documento estabelece os contratos de componentes Vue, propriedades, eventos, semântica WAI-ARIA e classes CSS para a Feature F0.8.8.

---

## 1. Contrato da Visualização Principal (`TrashView.vue`)

### Estrutura de Layout e Classes Semânticas

```html
<div class="trash-container wrap">
  <!-- Cabeçalho com título, introdução e botão de esvaziamento seguro -->
  <header class="page-header trash-header">
    <div class="title-area">
      <p class="eyebrow">Gerenciamento de Acervo</p>
      <h1>Lixeira</h1>
      <p class="intro">
        Itens descartados são mantidos por até 30 dias antes do expurgo automático permanente.
      </p>
    </div>
    <div class="header-actions">
      <button type="button" class="secondary danger-btn" @click="confirmEmptyOpen = true">
        Esvaziar lixeira
      </button>
    </div>
  </header>

  <!-- Filtros por Abas -->
  <div class="filters-bar" role="tablist" aria-label="Filtros da lixeira">
    <button role="tab" class="filter-tab" :class="{ active: activeFilter === 'all' }">
      Todos ({{ totalCount }})
    </button>
    <button role="tab" class="filter-tab" :class="{ active: activeFilter === 'books' }">
      Livros ({{ booksCount }})
    </button>
    <button role="tab" class="filter-tab" :class="{ active: activeFilter === 'studies' }">
      Estudos individuais ({{ studiesCount }})
    </button>
  </div>

  <!-- Cartão de Item Descartado -->
  <li class="trash-card panel" :class="{ 'is-selected': isSelected(item), 'is-restoring': restoringId === item.id }">
    <!-- Caixa de Seleção -->
    <label class="item-checkbox-label">
      <input
        type="checkbox"
        class="trash-item-checkbox"
        :checked="isSelected(item)"
        :aria-label="`Selecionar ${item.type} ${item.title}`"
        @change="toggleSelect(item)"
      />
    </label>

    <!-- Informações e Indicador de Retenção -->
    <div class="trash-card-info">
      <div class="badge-row">
        <span class="type-badge" :class="item.type + '-badge'">{{ item.typeLabel }}</span>
        <div class="retention-pill" :class="{ 'urgency-urgent': item.isUrgent }">
          <Icon name="clock" :size="12" />
          <span class="purge-text">Expurgo em {{ item.daysRemaining }} dias</span>
          <div class="retention-progress-bar" :style="{ width: item.elapsedPercentage + '%' }" />
        </div>
      </div>
      <h3 class="trash-card-title">{{ item.title }}</h3>
      <!-- Metadados de Livro ou Hierarquia de Estudo -->
      ...
    </div>

    <!-- Ações Rápidas Individuais -->
    <div class="trash-card-actions">
      <button class="primary button-sm" @click="handleRestore(item)">Restaurar</button>
      <button class="secondary danger-btn button-sm" @click="handleDelete(item)">Excluir definitivamente</button>
    </div>
  </li>

  <!-- Barra Flutuante de Ações em Lote -->
  <aside
    v-if="selectedCount > 0"
    class="trash-batch-bar"
    role="region"
    aria-label="Ações em lote da lixeira"
  >
    <div class="batch-bar-content">
      <span class="batch-count">{{ selectedCount }} {{ selectedCount === 1 ? 'item selecionado' : 'itens selecionados' }}</span>
      <div class="batch-actions">
        <button type="button" class="secondary button-sm" @click="toggleSelectAll">
          {{ isAllSelected ? 'Desmarcar todos' : 'Selecionar todos' }}
        </button>
        <button type="button" class="primary button-sm" :disabled="batchLoading" @click="handleBatchRestore">
          Restaurar selecionados
        </button>
        <button type="button" class="secondary danger-btn button-sm" :disabled="batchLoading" @click="handleBatchDelete">
          Excluir definitivamente
        </button>
        <button type="button" class="batch-close-btn" aria-label="Limpar seleção" @click="clearSelection">
          <Icon name="x" :size="16" />
        </button>
      </div>
    </div>
  </aside>
</div>
```

---

## 2. Contrato do Diálogo de Salvaguarda (`TrashConfirmModal.vue`)

### Propriedades (Props)

| Prop | Tipo | Padrão | Descrição |
|---|---|---|---|
| `open` | `boolean` | **Obrigatório** | Controla se o diálogo está aberto e visível no DOM via Teleport |
| `title` | `string` | **Obrigatório** | Título principal do diálogo de confirmação |
| `message` | `string` | **Obrigatório** | Mensagem explicativa das consequências da ação |
| `confirmLabel` | `string` | `'Confirmar'` | Texto do botão de confirmação |
| `cancelLabel` | `string` | `'Cancelar'` | Texto do botão de cancelamento |
| `danger` | `boolean` | `false` | Se verdadeiro, aplica semântica de alerta (`role="alertdialog"`), estilo de perigo e foca no botão de cancelar por padrão |
| `loading` | `boolean` | `false` | Indica requisição destrutiva em processamento |

### Eventos (Emits)

| Evento | Parâmetros | Descrição |
|---|---|---|
| `close` | N/A | Disparado ao clicar em Cancelar, no backdrop, no botão fechar ou ao pressionar Escape |
| `confirm` | N/A | Disparado ao clicar no botão de confirmação deliberada |

### Acessibilidade (WAI-ARIA)
- Atributos do container: `role="alertdialog"` quando `danger === true`, `role="dialog"` quando `danger === false`.
- `aria-modal="true"` e `aria-labelledby="confirm-title"`.
- *Focus Trap*: Retenção de foco entre os botões de ação enquanto o modal estiver aberto.
- Atalho `Escape`: Executa fechamento seguro sem side-effects.

---

## 3. Contrato de Animações e Estilos

### Animação de Saída de Restauração Individual
```css
.trash-card.is-restoring {
  transform: translateY(-20px);
  opacity: 0;
  transition: transform 180ms ease-out, opacity 180ms ease-out;
  pointer-events: none;
}
```

### Animação da Barra Flutuante de Lote
```css
.trash-batch-bar {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1), opacity 200ms ease;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.18);
  border-radius: 9999px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 0.5rem 1.25rem;
}
```

### Indicador de Retenção Visual
```css
.retention-pill {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.78rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  overflow: hidden;
}

.retention-pill.urgency-urgent {
  border-color: var(--color-danger, #e53e3e);
  color: var(--color-danger, #e53e3e);
  font-weight: 600;
}

.retention-progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  background: var(--color-border);
}

.urgency-urgent .retention-progress-bar {
  background: var(--color-danger, #e53e3e);
}
```
