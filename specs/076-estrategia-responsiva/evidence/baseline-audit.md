# Evidências e Medições da Linha de Base — Feature 076

**Feature**: `076-estrategia-responsiva`  
**Escopo**: Registro empírico das medições e validação dos problemas P-01 a P-19 com dados sintéticos.

---

## 1. Verificação de Rolagem Horizontal por Viewport (T006)

Inspeção da propriedade `scrollWidth > clientWidth` em banco temporário descartável:

| Viewport Testada | Resolução | Resultado de Overflow Horizontal | Observações de Layout |
|---|---|:---:|---|
| **V-320** | 320 × 568 px | **Detectado em formulários com min-width rígido** | `FriendsView` e `AdminView` apresentam estouro leve em 320px devido a `minmax(280px, 1fr)` com padding. Requer `min(280px, 100%)` (P-15). |
| **V-375** | 375 × 667 px | **Detectado no Map View** | Map View possui palco vetorial fixo em 800×560px sem pan por toque; anéis radiais cortam nas margens (P-04). |
| **V-390** | 390 × 844 px | **OK** no fluxo principal | Notificações sofrem risco de corte à esquerda (P-09). |
| **V-430** | 430 × 932 px | **OK** no fluxo principal | Cabeçalho superior apresenta 5 abas aglomeradas no header (P-01). |
| **V-767** | 767 × 1024 px | **OK** | Comportamento móvel ativo; ausência de barra inferior confirmada. |
| **V-768** | 768 × 1024 px | **OK** | Ponto de transição para drawer do `SplitLayout`. |
| **V-1024** | 1024 × 768 px | **OK** | Transição para SplitLayout com painéis fixos. |
| **V-1440** | 1440 × 900 px | **OK** | Workspace perfeitamente centrado dentro do container de 74rem. |
| **V-LAND** | 844 × 390 px | **OK** | Altura útil reduzida em modais quando teclado virtual ativado (P-16). |

---

## 2. Evidências Específicas por Problema

### P-01 / P-02: Barra Móvel e Header Superior
- **Inspeção**: No arquivo `mobile-navigation.css:195`, o seletor `.app-header .main-nav` continua estilizado com regras de barra inferior fixa (`position: fixed; bottom: 0`).
- **Constatação**: Nenhum template Vue utiliza `.main-nav`. O componente de abas utiliza `.navigation-tabs`.
- **Efeito Visual**: Em `<768px`, as 5 abas ficam comprimidas no topo ao lado do logo e dos botões de ação, enquanto o `#app` mantém `padding-bottom: 4rem` reservando espaço vazio para uma barra inexistente.

### P-03: `ShareModal.vue` e Tailwind Ausente
- **Inspeção**: Linhas 200 a 240 de `ShareModal.vue` utilizam classes `fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50`.
- **Constatação**: Como o projeto não possui Tailwind CSS instalado, o modal renderiza no fluxo normal do documento, sem backdrop, sem centralização absoluta e sem moldura.

### P-04 / P-05: Map View em Telas Sensíveis ao Toque
- **Inspeção**: `StudyMapView.vue` define listeners de mouse (`mousedown`, `mousemove`, `mouseup`) no viewport do mapa.
- **Constatação**: Dispositivos móveis não disparam pan nem pinch. O palco de 800×560px mantém o estudo-núcleo visível, mas os nós distribuídos nos raios de 165px e 265px ficam inacessíveis. Badges de aresta SVG medem 72×20px, insuficientes para toque confiável de 44px.

### P-06 / P-07: Canvas View em Smartphone
- **Inspeção**: `StudyCanvasView.vue` possui `.canvas-viewport` com `touch-action: none`.
- **Constatação**: No celular, o usuário que deslizar o dedo sobre o canvas não rola a página nem move o canvas com gestos intuitivos. A toolbar superior agrupa 12 botões de 44px em linha contínua sem barra de rolagem visível.

### P-08: Tree View em Níveis Profundos
- **Inspeção**: Em `StudyTreeNodeItem.vue`, cada nível adiciona indentação fixa de `1.25rem` (20px).
- **Constatação**: Em 320px de largura e nível 5 de profundidade ($5 \times 20 = 100\text{px}$ apenas de recuo), sobram menos de 100px para título, chevron e menu de ações.

### P-09 / P-10: Dropdown de Notificações e Offsets Inferiores
- **Inspeção**: `NotificationsDropdown.vue` utiliza `min-width: 360px` com `right: 0` ancorado no sino.
- **Constatação**: Quando o sino de notificações está a 40px da margem direita em viewport de 375px, o painel estende-se até $375 - 40 - 360 = -25\text{px}$ (estouro da borda esquerda).
- **Offsets**: Toasts em `StudyView.vue` usam `bottom: 2rem` fixo, o que colidirá com a barra inferior de 56px + safe-area.

### P-13: CSS Morto em `App.vue`
- **Inspeção**: `App.vue` retém cerca de 200 linhas de CSS scoped relacionadas a `.user-chip`, `.user-avatar-icon`, `.header-actions`, que foram migradas para `GlobalHeader.vue`.
- **Constatação**: Podem ser removidas na Feature 077 sem qualquer efeito visual na interface.
