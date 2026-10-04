# Feature Specification: F 0.7.8 — Redesenho do Canvas: Espaço Livre de Pensamento e Criação Espacial

**Feature Branch**: `057-redesenho-canvas`  
**Created**: 2026-10-04  
**Status**: Ready for Planning  
**Input**: User description: "F0.7.8" (Redesenho do Canvas: Espaço Livre de Pensamento e Criação Espacial — ROADMAP-0.7)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mesa de Trabalho Espacial Livre e Criação Rápida In-Place (Priority: P1) 🎯 MVP

O leitor de estudos abre a aba Canvas de um livro ou capítulo para organizar suas ideias em um espaço bidimensional infinito. Ao dar um duplo clique em qualquer coordenada livre da mesa (ou usar a ferramenta de adição rápida), surge imediatamente no ponto do ponteiro um mini-card de criação de estudo com foco automático no título e seleção de seção inicial analítica. Ao teclar `Enter`, o novo estudo é criado e persistido no capítulo, surgindo no canvas como um cartão espacial manipulável, permitindo ao leitor despejar reflexões e insights sem interromper seu fluxo de pensamento ou sair da mesa de trabalho.

**Why this priority**: É o valor central da metáfora de "quadro branco de estudos" — transformar o Canvas de uma grade passiva em um ambiente ativo e imediato de criação e exploração de ideias.

**Independent Test**: Abrir o Canvas de um capítulo; dar duplo clique em um ponto vazio do espaço; preencher título e breve anotação no mini-card; pressionar `Enter`; verificar que o novo cartão de estudo aparece posicionado exatamente nas coordenadas do clique e persiste após recarregamento.

**Acceptance Scenarios**:

1. **Given** a visualização do Canvas ativa com área vazia visível, **When** o usuário dá duplo clique em qualquer ponto do canvas com a ferramenta de seleção ativa, **Then** surge no ponto do ponteiro um mini-card inline com foco no título para criação rápida de estudo.
2. **Given** o mini-card de criação rápida aberto com título preenchido, **When** o usuário pressiona `Enter`, **Then** o estudo é registrado no capítulo ativo com as coordenadas correspondentes e seu cartão surge na mesa espacial pronto para manipulação.
3. **Given** múltiplos cartões no Canvas, **When** o usuário arrasta um cartão para uma nova coordenada, **Then** sua posição cartesiana é recalculada fluidamente e persistida de forma transparente no backend.

---

### User Story 2 - Molduras Espaciais (Frames) e Agrupamento Temático Solidário (Priority: P2)

O leitor deseja agrupar blocos conceituais afins em molduras temáticas (ex.: "Argumentos Centrais", "Objeções Históricas", "Síntese Própria") para estruturar visualmente áreas de estudo. O usuário seleciona a ferramenta de Moldura na barra de ferramentas e desenha um retângulo no canvas (ou clica no botão "Nova Moldura"). A moldura recebe um título editável inline, cor de destaque configurável e alças de redimensionamento nos cantos. Quando o usuário move a moldura pelo cabeçalho ou corpo, todos os cartões geometricamente contidos em seu interior movem-se solidariamente com ela, preservando a diagramação do grupo.

**Why this priority**: Molduras temáticas conferem estrutura visual de alto nível para grandes conjuntos de estudos, evitando que o Canvas se torne uma colcha de retalhos desorganizada.

**Independent Test**: Ativar a ferramenta de Moldura na toolbar; arrastar para desenhar uma moldura retangular ao redor de dois cartões de estudo; editar o título da moldura e alterar sua cor; arrastar e redimensionar a moldura; verificar que a moldura permanece no fundo espacial com contraste adequado e move os cartões internos de forma solidária.

**Acceptance Scenarios**:

1. **Given** a ferramenta de moldura selecionada na barra de ferramentas, **When** o usuário clica e arrasta no espaço livre do canvas, **Then** é criada uma nova moldura com dimensões delimitadas pelo arrasto, título padrão editável e cor temática selecionável.
2. **Given** uma moldura existente no canvas, **When** o usuário clica e arrasta suas alças laterais ou cantos de redimensionamento, **Then** as dimensões da moldura são ajustadas em tempo real preservando o conteúdo visível.
3. **Given** uma moldura contendo cartões de estudo posicionados em seu interior, **When** o usuário move a moldura, **Then** os cartões geometricamente contidos em seu interior movem-se solidariamente em conjunto com ela, mantendo suas posições relativas intactas.

---

### User Story 3 - Conexões Espaciais Direcionadas, Snapping Inteligente e Navegação Precisa (Priority: P3)

Para articular argumentos complexos, o usuário traça linhas de conexão direcionadas entre cartões no canvas integradas às relações semânticas com rótulos legíveis. Ao mover cartões, um sistema de guias magnéticas inteligentes (Smart Guides) projeta linhas temporárias na cor de acento com snap suave em raio de ±10px para nivelar bordas e centros. A barra de ferramentas oferece alternância clara de ferramentas (`select`, `pan`, `frame`, `connect`), zoom suave e mini-mapa reativo no canto inferior para orientação global rápida.

**Why this priority**: Fornece polimento ergonômico, alinhamento profissional e visão macro do espaço para leitores e pesquisadores que constroem mapas de argumentos densos.

**Independent Test**: Selecionar a alça de conexão de um cartão e arrastar até outro cartão; verificar que uma aresta elástica desenha-se com seletor de relação; arrastar um cartão próximo a outro e verificar as guias magnéticas de snapping; utilizar o minimapa para navegar rapidamente a uma região distante do canvas.

**Acceptance Scenarios**:

1. **Given** dois cartões no canvas, **When** o usuário conecta a alça de saída do primeiro cartão ao segundo, **Then** uma aresta direcional é criada com indicador de sentido e persistida no repositório de relações semânticas com rótulo descritivo.
2. **Given** cartões sendo movidos no canvas, **When** um cartão se aproxima das coordenadas de borda ou centro de outro cartão vizinho, **Then** guias magnéticas inteligentes projetam linhas sutis na cor de acento com snap suave em um raio de ±10px.
3. **Given** um canvas amplo com dezenas de cartões espalhados, **When** o usuário interage com o mini-mapa no canto da tela, **Then** a viewport do canvas translada instantaneamente para o quadrante selecionado, exibindo a miniatura de todos os nós e molduras.

---

### Edge Cases

- **Duplo clique acidental sobre cartão existente**: Ao dar duplo clique sobre um cartão de estudo já existente, o sistema abre o estudo para leitura/edição em vez de disparar a criação de um novo estudo naquele ponto.
- **Cartão arrastado para fora dos limites visíveis**: Se o usuário arrastar um cartão para coordenadas extremas ou se perder no espaço infinito, a ação "Ajustar à Tela" (Fit to View) na toolbar recalcula a caixa delimitadora (bounding box) de todos os elementos e centraliza a câmera suavemente.
- **Moldura vazia redimensionada para tamanho mínimo**: A moldura possui dimensões mínimas protegidas (ex.: 160×100px) impedindo que colapse para zero ou inverta suas coordenadas espaciais.
- **Tentativa de auto-conexão**: Arrastar a linha conectora de um cartão de volta para ele mesmo é terminantemente bloqueado, cancelando a linha sem gerar arestas redundantes.
- **Conflito de pan com arrasto de seleção**: Quando a ferramenta `pan` (mãozinha) está ativa, o clique e arrasto no canvas move a câmera sem selecionar ou mover cartões acidentalmente.

---

## Clarifications

### Session 2026-10-04
- **Q1: Comportamento ao mover Molduras (Frames)**: Opção A adotada. Movimento solidário automático: cartões geometricamente contidos no interior da moldura movem-se em conjunto ao arrastá-la, mantendo suas posições relativas intactas.
- **Q2: Conexões direcionadas e persistência**: Opção A adotada. Integração com o repositório de relações (`study_relations`): o conector no Canvas permite escolher o tipo semântico e persiste na tabela oficial de relações.
- **Q3: Intensidade e feedback do alinhamento magnético**: Opção A adotada. Guias magnéticas inteligentes (Smart Guides) com snap suave de centro/bordas (alcance de ±10px) e exibição temporária de linhas guias sutis na cor de acento.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir a criação instantânea de novos estudos via duplo clique em coordenadas livres da mesa de trabalho espacial, abrindo mini-card inline in-place com foco automático no título e atalho `Enter` para persistência imediata.
- **FR-002**: O sistema DEVE suportar posicionamento cartesiano livre `(x, y)` e redimensionamento individual de cartões de estudo no Canvas, persistindo as coordenadas no SQLite sem saltos visuais.
- **FR-003**: O sistema DEVE fornecer ferramenta interativa de desenho e gerenciamento de Molduras (Frames) coloridas para delimitação e categorização temática de grupos de estudos.
- **FR-004**: Cada moldura DEVE suportar edição de título inline no cabeçalho, personalização de paleta de cor temática e alças de redimensionamento bidirecional.
- **FR-005**: Ao arrastar molduras temáticas, o sistema DEVE mover solidariamente todos os cartões geometricamente contidos em seu interior, preservando suas posições relativas intactas.
- **FR-006**: O sistema DEVE permitir traçar arestas conectoras direcionadas entre cartões no Canvas integradas à tabela oficial de relações (`study_relations`), exibindo setas indicativas de sentido e badges semânticos legíveis.
- **FR-007**: O sistema DEVE disponibilizar guias magnéticas inteligentes (Smart Guides) com encaixe suave de bordas e centros em um raio de ±10px, acompanhado por projeção sutil de linhas guias na cor de acento durante o arrasto.
- **FR-008**: A Canvas Toolbar DEVE apresentar seletor claro de ferramentas ativas (`select` / ponteiro, `pan` / mãozinha, `frame` / moldura, `connect` / conexão) com atalhos de teclado (ex.: barra de espaço para pan temporário).
- **FR-009**: O sistema DEVE renderizar um mini-mapa funcional no canto inferior que reflete o viewport atual, a posição relativa de todos os cartões e molduras, e permite navegação rápida por clique/arrasto.
- **FR-010**: O sistema DEVE suportar controles de zoom suave (de 25% a 250%), ação "Ajustar à Tela" (Fit to View) e atalho de redefinição para 100%.
- **FR-011**: Em dispositivos móveis (< 768px), o sistema DEVE suportar gestos nativos de pinça para zoom, arrasto com dois dedos para pan e botões táteis no rodapé com alvos mínimos de 44×44px.
- **FR-012**: O sistema DEVE disponibilizar navegação por teclado (`Tab`, setas) e resumo alternativo acessível do conteúdo espacial para leitores de tela em conformidade WCAG 2.2.

---

### Key Entities

- **CanvasCard**: Cartão espacial de estudo posicionado no plano 2D. Atributos: `study_id`, `pos_x`, `pos_y`, `width`, `height`, `z_index`, `color_tag`.
- **CanvasFrame**: Moldura retangular temática delimitadora. Atributos: `id`, `book_id`, `title`, `pos_x`, `pos_y`, `width`, `height`, `color_tag`.
- **CanvasEdge**: Conector visual direcionado entre nós do canvas. Atributos: `id`, `source_study_id`, `target_study_id`, `relation_type`, `description`.
- **CanvasViewport**: Estado de navegação e enquadramento da câmera. Atributos: `pan_x`, `pan_y`, `zoom_level`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuário consegue criar um novo estudo em um ponto específico do Canvas via duplo clique e salvá-lo com `Enter` em menos de 5 segundos, sem recarregar a tela.
- **SC-002**: O usuário consegue criar, posicionar e redimensionar uma nova moldura temática delimitando cartões em menos de 10 segundos.
- **SC-003**: As coordenadas e dimensões de cartões e molduras persistem e recarregam com fidelidade espacial de 100%, sem desvios ou sobreposições indesejadas.
- **SC-004**: O Canvas mantém taxa de atualização de 60 quadros por segundo durante pan, zoom e arrasto contínuo em mesas com até 50 cartões e molduras.
- **SC-005**: 100% dos controles e alvos interativos no modo mobile cumprem o tamanho tátil mínimo de 44×44px.

---

## Assumptions

- O Canvas opera no contexto do livro ou capítulo ativo selecionado pelo leitor.
- As tabelas e rotas de persistência existentes para nós do canvas (`study_canvas_nodes`) e molduras (`canvas_frames`) continuam sendo a base estrutural de dados.
- O Canvas complementa a Map View (que é focada estritamente em relações semânticas cognitivas), fornecendo a liberdade espacial irrestrita de uma mesa de trabalho ou quadro branco.
- O mini-card de criação in-place reutiliza a lógica de preenchimento inicial de seção analítica garantindo conformidade com a exigência de análise do backend.

---
