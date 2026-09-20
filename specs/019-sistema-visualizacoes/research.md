# Research & Technical Decisions: F01 — Sistema de Visualizações e Dashboard Responsivo

**Branch**: `019-sistema-visualizacoes` | **Data**: 2026-09-19

---

## 1. Arquitetura dos Renderers Plugáveis de Visualização

### Decisão
Criar uma pasta dedicada `caderno-leitura-0.1/frontend/src/components/views/` contendo:
- `ViewSwitcher.vue`: Barra seletora de modos de visualização acessível (`role="tablist"`).
- `StudyGridView.vue`: Projeção em cartões amplos com ênfase visual em título, localização, datas e resumos.
- `StudyListView.vue`: Projeção em lista tabular compacta de alta densidade de leitura.
- `StudyTreeView.vue`: Projeção estruturada em árvore com ramos e expansão/colapso hierárquico.
- `StudyMapView.vue`: Projeção em rede conceitual com nós conectados e distribuição radial.
- `StudyCanvasView.vue`: Projeção espacial bidimensional 2D com pan/zoom e cartões flutuantes.
- `composables/useViewPreference.ts`: Composable reativo encapsulando o estado da visualização ativa, preservação do estudo em foco (`activeStudyId`) e persistência híbrida.

### Racional
- **Zero Acoplamento e Extensibilidade**: Cada renderer é um componente Vue independente que recebe `studies: StudySummary[]`, `selectedChapter: Chapter | null` e `activeStudyId: number | null`, emitindo eventos semânticos (`select-study`, `trash-study`). Isso permite que as futuras features (F02 Árvore com drag-and-drop, F03 Canvas infinito e F04 Grafo de relações) substituam ou expandam seus respectivos renderers sem tocar na barra de controle ou nas demais visualizações.
- **Transição Fluida a 60fps**: A alternância entre renderers utiliza componentes dinâmicos do Vue (`<component :is="...">`) com preservação de nós e sem destruição prematura do estado, evitando congelamentos em acervos volumosos.

### Alternativas Consideradas
- *Renderers embutidos em um único arquivo monólito em `BookView.vue`:* Rejeitado por violar o princípio de responsabilidade única e inflar excessivamente a visão do livro.
- *Bibliotecas de canvas/grafos de terceiros (como Cytoscape ou Vis.js):* Rejeitado para esta etapa fundamental; renderers SVG/CSS nativos leves garantem carregamento instantâneo, zero inchaço de dependências e compatibilidade com os temas e Superclasses.

---

## 2. Modelo Híbrido de Persistência em `localStorage`

### Decisão
Implementar estratégia de dois níveis idêntica à consagrada na F06:
1. `caderno_preferred_view_{bookId}`: Salva a preferência customizada para uma obra específica (ex.: leitor prefere analisar "Crítica da Razão Pura" no modo Árvore ou Mapa).
2. `caderno_default_view`: Salva a preferência global padrão do leitor (ex.: leitor prefere abrir livros novos em Grade ou Lista).
3. Na inicialização:
   - Se existir preferência para o livro atual, aplica-a.
   - Se não, recorre à preferência global da biblioteca.
   - Se nenhuma estiver gravada, adota o padrão de fábrica (`'grid'`).

### Racional
- Respeita diretamente a decisão ratificada pelo usuário na pergunta **Q2 (Opção A)**.
- Dá total autonomia ao leitor para personalizar livros que exigem leitura não-linear sem prejudicar a navegação sequencial de outras obras.

---

## 3. Disposição Ergonômica da Barra de Visualizações no Mobile (< 768px)

### Decisão
Implementar uma barra horizontal compacta no topo da seção de estudos com botões de alternância com área de toque mínima garantida de 44x44px, exibindo ícones vetoriais Lucide (`grid`, `list`, `network`, `canvas` e `folder`/árvore) com rótulos visíveis apenas quando o espaço permitir (ou tooltips acessíveis e `aria-label`).

### Racional
- Cumpre a escolha do usuário na pergunta **Q3 (Opção A)**.
- Permite alternar qualquer uma das cinco visualizações com um único toque direto no celular, sem exigir aberturas de menus suspensos intermediários.
- Garante conformidade com as diretrizes W3C WCAG 2.2 para dimensões mínimas de alvos de toque (Target Size: 44x44px).

---

## 4. Reajuste Responsivo e Ancoragem do Dashboard no Celular

### Decisão
1. **Grid de Indicadores**:
   - No celular (< 768px), o `.metrics-grid` passa a utilizar `grid-template-columns: repeat(2, 1fr)` com `gap: 0.75rem`.
   - O cartão de Sequência Atual (`.streak-card`) recebe `grid-column: span 2`, ocupando toda a largura inferior da grade de métricas com destaque visual.
2. **Auto-Scroll no Mapa de Calor Anual (`HeatmapCalendar.vue`)**:
   - No `onMounted`, se a largura da tela for inferior a 768px, o elemento `.heatmap-scroll-area` realiza rolagem automática suave para o fim (`scrollLeft = scrollWidth - clientWidth`).
   - Isso garante que o leitor no celular veja imediatamente o mês atual e a semana corrente, em vez de ver o início do ano passado e ter que rolar horizontalmente dezenas de semanas.
3. **Tipografia e Cartões da Linha do Tempo**:
   - Títulos adaptativos com `clamp(1.5rem, 5vw, 2rem)`.
   - Cartões da linha do tempo com links de ação ocupando largura integral ou alinhamento acessível de toque (mínimo de 44x44px).
