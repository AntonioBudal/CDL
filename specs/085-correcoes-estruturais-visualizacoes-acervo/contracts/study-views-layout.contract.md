# Contrato de Interface e Layout: Visualizações do Acervo

**Feature**: `085-correcoes-estruturais-visualizacoes-acervo`
**Data**: 2026-10-24
**Status**: Concluído

---

## 1. Contrato de Componente: StudyStatusBadge.vue

### 1.1 Props
| Prop | Tipo | Padrão | Descrição |
|------|------|--------|-----------|
| `status` | `ReadingStatus \| string` | `'rascunho'` | Status de leitura do estudo. |
| `studyId` | `number \| undefined` | `undefined` | ID do estudo (necessário para persistência automática). |
| `interactive` | `boolean` | `false` | Se `true`, exibe gatilho com chevron e menu suspenso de seleção. |
| `disabled` | `boolean` | `false` | Se `true`, desabilita interatividade. |

### 1.2 Emissões (Events)
| Evento | Payload | Descrição |
|--------|---------|-----------|
| `change` | `newStatus: ReadingStatus` | Emitido quando o usuário seleciona um novo status de leitura. |
| `toggle-open` | `isOpen: boolean` | Emitido quando o dropdown se abre (`true`) ou se fecha (`false`), permitindo elevação de z-index no elemento pai. |

### 1.3 Contrato de Estilo e Posicionamento
- `.study-status-badge-container.is-open`: DEVE possuir `z-index: 1000; position: relative;`.
- `.status-dropdown-menu`:
  - `position: absolute;`
  - `z-index: 1200;`
  - `min-width: 155px;`
  - Padrão descendente: `top: calc(100% + 4px);`
  - Inversão ascendente (`.opens-upward`): `top: auto; bottom: calc(100% + 4px);`

---

## 2. Contrato de Layout Tabular: StudyListView.vue

### 2.1 Colunas da Tabela Desktop (Grid CSS)
A malha de colunas DEVE ser idêntica em `.list-header-row`, `.study-row-item` e `.skeleton-row`:

```css
grid-template-columns: minmax(200px, 4fr) minmax(130px, 2fr) minmax(140px, 2fr) minmax(110px, 1.5fr) minmax(115px, 1fr) 52px;
gap: 1.25rem;
padding-left: 1rem;
padding-right: 1rem;
align-items: center;
```

### 2.2 Distribuição e Alinhamento das Células
1. **Coluna 1 (Título)**: `align-items: center; justify-content: flex-start; text-overflow: ellipsis;`
2. **Coluna 2 (Status)**: `align-items: center; justify-content: flex-start; overflow: visible;`
3. **Coluna 3 (Localização)**: `align-items: center; justify-content: flex-start;`
4. **Coluna 4 (Data)**: `align-items: center; justify-content: flex-start; font-variant-numeric: tabular-nums;`
5. **Coluna 5 (Seções)**: `align-items: center; justify-content: center;`
6. **Coluna 6 (Ações)**: `align-items: center; justify-content: center;`

### 2.3 Contrato de Ordenação e Ícones SVG
- Botões de ordenação: `.header-sort-btn`
- Ícone indicador: `.sort-indicator`
  - `stroke: currentColor;`
  - `fill: none;`
  - `color: currentColor;`
  - `:deep(.sort-indicator svg)`: `stroke: currentColor; fill: none;`

### 2.4 Prevenção de Corte (Clipping)
- `.study-tabular-list`: `overflow: visible;`
- `.study-row-item.has-dropdown-open`, `.study-row-item:has(.is-open)`: `z-index: 1000; position: relative;`

---

## 3. Contrato de Layout em Grade: StudyGridView.vue

### 3.1 Prevenção de Sobreposição nos Cartões
- `.study-card.has-dropdown-open`, `.study-card:has(.is-open)`:
  - `z-index: 50;`
  - `position: relative;`
- Escuta do evento `@toggle-open`: Sincroniza `activeDropdownStudyId` no componente pai para aplicar `.has-dropdown-open`.
