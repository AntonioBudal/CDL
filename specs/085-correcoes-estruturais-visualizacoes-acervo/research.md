# Pesquisa Técnica: Correções Estruturais nas Visualizações do Acervo

**Feature**: `085-correcoes-estruturais-visualizacoes-acervo`
**Data**: 2026-10-24
**Status**: Concluída

---

## 1. Diagnóstico do Problema de Corte (*Clipping*) do Dropdown de Status

### 1.1 Causa Raiz
Na visualização em lista de estudos ([`StudyListView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue)), o menu suspenso de seleção de status de leitura (`.status-dropdown-menu`) é gerado dentro do componente [`StudyStatusBadge.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/StudyStatusBadge.vue).

Foram identificados os seguintes fatores de corte visual:
1. **Limites Verticais na Primeira e na Última Linha**:
   - O menu suspenso possui 4 opções de status (`min-height: 44px` cada, totalizando aproximadamente 195px de altura com paddings e bordas).
   - O cálculo anterior de abertura para cima (`opensUpward`) utilizava um limiar fixo de 185px (`window.innerHeight - rect.bottom < 185`), insuficiente quando o espaço residual inferior está entre 185px e 205px, fazendo com que o menu se projete para baixo e tenha seus últimos itens cortados pelo fim do contêiner ou da viewport.
2. **Contexto de Empilhamento (*Stacking Context*)**:
   - Cada linha da lista (`.study-row-item`) e cada cartão da grade (`.study-card`) são elementos irmãos.
   - Quando o dropdown de status é aberto, a linha ou cartão ativo necessita de elevação explícita de `z-index` e `position: relative`, assegurando que o menu sobreponha irrestritamente as linhas ou cartões subsequentes na árvore DOM.
   - Em `StudyGridView.vue`, a classe de elevação não estava sincronizada com o estado de abertura do dropdown de status.

### 1.2 Decisão de Arquitetura
- **Ajuste Dinâmico e Posicionamento Relativo Seguro**:
  - Em `StudyStatusBadge.vue`, refinar a heurística de `opensUpward` comparando o espaço disponível abaixo e acima (`window.innerHeight - rect.bottom < 210 && rect.top > 210`, ou quando o espaço superior for maior que o inferior em caso de contêiner apertado).
  - Em `StudyListView.vue`, consolidar `overflow: visible` na tabela e em `.col-status`, garantindo que `.study-row-item.has-dropdown-open` e `.study-row-item:has(.is-open)` mantenham `z-index: 1000; position: relative;`.
  - Em `StudyGridView.vue`, sincronizar a classe `has-dropdown-open` no cartão de estudo ativo com `z-index: 50; position: relative;` para sobrepor cartões adjacentes sem necessidade de teletransporte global complexo.

---

## 2. Investigação do Ícone SVG de Ordenação nos 10 Temas Oficiais

### 2.1 Causa Raiz
O componente [`Icon.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/ui/Icon.vue) instancia ícones SVG da biblioteca Lucide (`ArrowUp` e `ArrowDown`).
Em certos temas com fundos texturizados ou escuros (`pergaminho`, `sepia`, `noturno`, `crepusculo`):
- O SVG de ordenação dependia apenas de herança indireta.
- Faltava explicitar `stroke: currentColor` e `fill: none` tanto no contêiner `.sort-indicator` quanto em `:deep(.sort-indicator svg)`, prevenindo qualquer herança espúria de regras globais de SVG.

### 2.2 Decisão Técnica
- Declarar de forma estrita em `StudyListView.vue`:
  ```css
  .sort-indicator {
    display: inline-flex;
    align-items: center;
    stroke: currentColor;
    fill: none;
    color: currentColor;
    flex-shrink: 0;
    font-size: 0.85rem;
    font-weight: bold;
  }

  :deep(.sort-indicator svg) {
    stroke: currentColor;
    fill: none;
  }
  ```
- O botão `.header-sort-btn` ativo já recebe `color: var(--color-text, #0f172a)` e `:hover` recebe `color: var(--color-accent)`. Com `currentColor`, a seta herda perfeitamente a cor exata do texto do cabeçalho em todos os 10 temas canônicos.

---

## 3. Investigação do Alinhamento Geométrico do Grid em Telas Largas

### 3.1 Causa Raiz
Na visualização em lista, existem 3 elementos que compartilham a geometria tabular:
1. `.list-header-row` (linha de cabeçalho com 6 colunas)
2. `.study-row-item` (linhas de dados dos estudos)
3. `.skeleton-row` (esqueleto de carregamento)

Anteriormente:
- Os valores de `grid-template-columns` estavam duplicados como strings literais independentes nos seletores CSS.
- Não havia uma variável CSS compartilhada ou padronização explícita com frações harmoniosas para telas largas (>= 1440px), gerando descompassos visuais em monitores de alta densidade.
- Algumas células de dados não possuíam `align-items: center` explícito, gerando micro-desalinhamentos verticais de 1 a 2px entre o texto do título e as pílulas de status.

### 3.2 Decisão Técnica
- Unificar a malha de colunas através de um padrão compartilhado:
  `grid-template-columns: minmax(200px, 4fr) minmax(130px, 2fr) minmax(140px, 2fr) minmax(110px, 1.5fr) minmax(115px, 1fr) 52px;`
- Aplicar exatamente a mesma regra em `.list-header-row`, `.study-row-item` e `.skeleton-row`.
- Adicionar `gap: 1.25rem` e padding horizontal unificado de `1rem`.
- Adicionar `display: flex; align-items: center;` universalmente nas células de dados e cabeçalhos, centralizando `col-sections` e `col-actions`.

---

## 4. Conformidade Constitucional
- Não há acesso nem manipulação direta do banco de dados `caderno.db`.
- Todas as alterações são estritamente de UI/UX, CSS e apresentação no frontend Vue 3.
- Os 10 temas oficiais permanecem preservados e sem uso de cores hexadecimais fixas conflitantes.
