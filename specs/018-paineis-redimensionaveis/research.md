# Research & Technical Decisions: F06 — Painéis Redimensionáveis

**Branch**: `018-paineis-redimensionaveis` | **Feature**: F06 — Painéis Redimensionáveis | **Data**: 2026-09-19

---

## 1. Arquitetura de Redimensionamento: Nativo PointerEvents vs Biblioteca de Terceiros

### Decisão
Construir uma solução nativa e modular com Vue 3 (Composition API) utilizando a API padrão de `PointerEvents` (`pointerdown`, `pointermove`, `pointerup`, `setPointerCapture`), encapsulada no composable `useSplitPanes.ts` e em três componentes declarativos: `SplitLayout.vue`, `SplitPane.vue` e `SplitGutter.vue`.

### Racional
- **Zero Dependências Externas**: O ecossistema de bibliotecas de split panes (como `splitpanes`) frequentemente introduz overhead, dificuldades de estilização com variáveis CSS modernas, problemas de tipagem TypeScript estrita e complexidade ao lidar com transições das 5 Superclasses de interface.
- **Unificação Mouse/Touch**: A API nativa `PointerEvents` unifica cliques de mouse, trackpad e toques em telas capacitivas com uma única implementação.
- **Isolamento de Performance**: O cálculo durante o arrasto opera alterando diretamente variáveis CSS de largura (`--pane-left-width`, `--pane-right-width`) ou flex-basis, evitando re-renderizações completas do Virtual DOM a cada pixel deslocado e mantendo 60fps constantes.

### Alternativas Consideradas
- *Biblioteca `splitpanes`:* Avaliada, mas rejeitada por inflar o bundle do frontend, dificultar a acessibilidade WAI-ARIA personalizada (`role="separator"`) e não suportar nativamente a alternância para gavetas deslizantes no mobile.
- *Layout CSS puro com `resize: horizontal`:* Rejeitado por não permitir botões de colapso rápido, persistência programática nem suporte a controle por teclado acessível.

---

## 2. Captura de Ponteiro e Neutralização de Seleção de Texto

### Decisão
Utilizar `event.target.setPointerCapture(event.pointerId)` no início do arrasto (`pointerdown`) no componente `SplitGutter.vue`, liberando-o no `pointerup`/`pointercancel`. Adicionar classe CSS utilitária `.split-resizing` no contêiner raiz durante o arrasto, definindo `user-select: none !important; cursor: col-resize;`.

### Racional
- Quando o usuário arrasta o mouse rapidamente, o ponteiro frequentemente se desloca para fora da barra divisora de 6-8px de largura. Sem `setPointerCapture`, o evento de `pointermove` é perdido ou o texto da área de leitura é selecionado em bloco azul, degradando a experiência.
- O travamento garante rastreamento contínuo e suave em qualquer ponto da janela.

### Alternativas Consideradas
- *Ouvintes globais em `window.addEventListener('mousemove', ...)`:* Funciona para mouse, mas é frágil para toques múltiplos e exige limpeza manual propensa a memory leaks.

---

## 3. Modelo Híbrido de Persistência em `localStorage`

### Decisão
Implementar persistência em dois níveis:
1. `caderno_pane_sizes_global`: Armazena a largura padrão global preferida pelo leitor (ex.: `{ left: 320, right: 300 }`).
2. `caderno_pane_sizes_book_{bookId}`: Caso o usuário redimensione as colunas em um livro específico, a configuração daquele livro é salva individualmente.
3. Se existir configuração para o livro atual, ela tem precedência; caso contrário, aplica-se a configuração global; se nenhuma existir, adota-se o padrão de fábrica (`left: 300px, right: 300px`, com painel direito recolhido por padrão conforme ratificado na especificação).

### Racional
- Respeita diretamente a decisão do usuário na clarificação Q3 (Opção C).
- Proporciona comodidade imediata ao navegar por diferentes obras, permitindo que livros densos com nomes de capítulos extensos tenham layout adaptado sem afetar os demais.

### Alternativas Consideradas
- *Apenas global:* Descartado pela escolha do usuário.
- *Apenas por livro:* Forçaria o usuário a reconfigurar as proporções da tela a cada novo livro cadastrado.

---

## 4. Estratégia de Acessibilidade (WAI-ARIA e Teclado)

### Decisão
- As divisórias (`SplitGutter.vue`) recebem `role="separator"`, `tabindex="0"`, `aria-orientation="vertical"`, `aria-valuenow`, `aria-valuemin="240"`, `aria-valuemax="600"`, com `aria-label="Separador redimensionável da navegação"`.
- Navegação por teclado:
  - `Seta Esquerda` / `Seta Direita`: Altera a largura em passos regulares de 10px.
  - `Home` / `End`: Ajusta diretamente para a largura mínima (240px) ou máxima (600px).
  - `Enter` / `Espaço`: Alterna o estado de colapso/expansão do painel correspondente.
  - `Duplo clique`: Restaura a largura padrão de fábrica (300px).
- Conforme ratificado na clarificação Q2 (Opção C), atalhos globais de teclado foram dispensados para evitar interferência na digitação livre de notas.

### Racional
- Conformidade total com o padrão W3C ARIA Authoring Practices Guide para `separator` (window splitter).
- Zero conflitos de digitação no editor de anotações e markdown.

---

## 5. Adaptação Responsiva: Três Colunas (Desktop) vs Gavetas (Mobile/Tablet)

### Decisão
- **Desktop (>= 1024px)**: Três colunas com divisores arrastáveis. Painel esquerdo aberto, painel direito colapsado na primeira abertura (Q1: Opção A). Palco central garantido com mínimo de 360px.
- **Tablet (768px a 1023px)**: Coluna esquerda presente, painel de contexto inicia colapsado e abre-se como gaveta lateral sobreposta suave (*drawer*).
- **Mobile (< 768px)**: Desativação total do redimensionamento arrastável. Navegação e Contexto tornam-se gavetas completas de tela cheia ou *bottom sheets*, abertas por botões táteis no topo/barra de leitura com área mínima de 44x44px.

### Racional
- Monitores pequenos não comportam 3 colunas simultâneas legíveis. A substituição por gavetas preserva a ergonomia e cumpre o princípio constitucional de acessibilidade e foco na leitura.
