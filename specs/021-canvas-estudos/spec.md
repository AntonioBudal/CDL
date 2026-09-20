# Feature Specification: F03 — Canvas de Estudos

**Feature Branch**: `021-canvas-estudos`  
**Created**: 2026-09-19  
**Status**: Approved  
**Input**: User description: "F03 Canvas de Estudos: Espaço livre bidimensional (2D) infinito com pan, zoom, seleção e coordenadas isoladas"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navegação Espacial Infinita com Pan e Zoom Fluido (Priority: P1) 🎯 MVP

Como leitor e pesquisador que estuda obras densas e conceitos multidimensionais,  
quero dispor de um espaço bidimensional livre e infinito (Canvas 2D) com navegação fluida por deslocamento (pan) e aproximação/afastamento (zoom),  
para que possa contemplar panoramas conceituais amplos ou focar em detalhes de anotações sem as limitações de listas verticais ou diagramas fixos.

**Why this priority**: Constitui a fundação do espaço espacial (viewport 2D). Sem uma navegação fluida e estável a 60fps, nenhuma organização de cards ou exploração conceitual é viável.

**Independent Test**: Acessar o modo Canvas de um livro, arrastar o fundo em qualquer direção para navegar pelo espaço infinito, realizar zoom contínuo e verificar fluidez sem congelamentos ou quebra visual.

**Acceptance Scenarios**:
1. **Given** um leitor no modo de visualização Canvas, **When** ele clica e arrasta o fundo da tela (ou utiliza dois dedos no trackpad), **Then** o espaço bidimensional se desloca suavemente na direção do arrasto (pan).
2. **Given** o espaço do Canvas, **When** o leitor gira a roda do mouse ou realiza o gesto de pinça, **Then** o nível de zoom varia continuamente (com limites seguros entre 25% e 200%), mantendo como ponto focal a posição atual do ponteiro.
3. **Given** a navegação no Canvas, **When** o leitor se desloca por distâncias arbitrárias, **Then** a grade de orientação espacial de fundo ajusta sua escala e coordenadas de forma contínua, sem perda de nitidez ou limites artificiais.
4. **Given** o leitor que ajusta sua visualização, **When** recarrega a página ou retorna ao livro, **Then** o deslocamento (pan) e a escala de zoom são restaurados para o mesmo ponto onde a leitura foi interrompida.

---

### User Story 2 - Posicionamento Livre, Seleção e Persistência de Coordenadas (Priority: P2)

Como leitor que organiza ativamente o arranjo dos seus pensamentos,  
quero mover cards de estudo livremente pelo Canvas, selecionar múltiplos itens simultaneamente e ter suas posições espaciais persistidas de forma independente,  
com a certeza de que a movimentação física de um card jamais corrompa ou altere a hierarquia estrutural (árvore de estudos) ou a ordem dos capítulos.

**Why this priority**: É o cerne da montagem espacial do conhecimento. Permite aproximar temas afins, construir aglomerados temáticos e desenhar a topografia do raciocínio mantendo isolamento absoluto entre espaço e dados canônicos.

**Independent Test**: Mover cards de estudos para posições arbitrárias, selecionar múltiplos cards por área retangular (*marquee*), arrastar o bloco conjunto, recarregar a aplicação e confirmar que as posições persistem e os capítulos e relações de parentesco permanecem intactos.

**Acceptance Scenarios**:
1. **Given** um card de estudo posicionado no Canvas, **When** o leitor clica no cabeçalho/corpo do card e o arrasta para uma nova coordenada (x, y), **Then** o card acompanha o ponteiro em tempo real e se fixa na nova coordenada ao soltar.
2. **Given** a movimentação de qualquer card no Canvas, **When** a posição é salva, **Then** a paternidade estrutural (`parent_study_id`) e a vinculação de capítulo do estudo permanecem estritamente inalteradas.
3. **Given** múltiplos cards distribuídos no Canvas, **When** o leitor arrasta o ponteiro desenhando uma caixa de seleção retangular (*marquee selection*), **Then** todos os cards interceptados pela área tornam-se selecionados com destaque visual ativo.
4. **Given** um grupo de cards selecionados, **When** o leitor arrasta qualquer um dos cards do grupo, **Then** todos os cards selecionados movem-se conjuntamente mantendo suas distâncias relativas intactas.
5. **Given** múltiplos cards que se sobrepõem no espaço, **When** o leitor interage ou clica em um card, **Then** seu índice de profundidade (`z_index`) é elevado para sobrepor visualmente os nós vizinhos.

---

### User Story 3 - Orientação Espacial, Radar (Mini-mapa) e Controles de Viewport (Priority: P3)

Como pesquisador que administra dezenas de estudos espalhados em um grande território 2D,  
quero dispor de um mini-mapa de navegação (*radar view*) e botões de comando do viewport (ajustar à tela, resetar zoom e centralizar),  
para que nunca perca o senso de orientação e possa rapidamente saltar entre áreas do canvas.

**Why this priority**: Previne a desorientação espacial (*lost in space*) quando o volume de anotações cresce ou quando o leitor navega para áreas afastadas do canvas.

**Independent Test**: Afastar-se do centro dos nós, verificar a representação miniatura dos cards no mini-mapa, clicar no mini-mapa para teletransportar a visualização e acionar o botão "Ajustar à Tela" para enquadrar todos os nós perfeitamente.

**Acceptance Scenarios**:
1. **Given** cards distribuídos no espaço, **When** o leitor olha para o canto da tela, **Then** um mini-mapa exibe a silhueta dos nós existentes e um retângulo indicativo da janela visível atual.
2. **Given** o mini-mapa, **When** o leitor clica ou arrasta o retângulo de visão dentro do mini-mapa, **Then** o viewport do Canvas centraliza instantaneamente a visualização na coordenada correspondente.
3. **Given** um Canvas com estudos dispersos, **When** o leitor aciona o comando "Ajustar à Tela" (*Fit to View*), **Then** o sistema calcula o retângulo delimitador (*bounding box*) de todos os cards e ajusta suavemente o pan e zoom para enquadrar todo o acervo na tela.
4. **Given** um nível de zoom qualquer, **When** o leitor clica em "Resetar Zoom (100%)", **Then** a escala do viewport retorna exatamente para 1.0 (100%) preservando o ponto central.

---

### User Story 4 - Ergonomia Tátil Móvel e Acessibilidade Espacial (Priority: P4)

Como leitor que estuda em smartphones e tablets,  
quero interagir com o Canvas através de gestos táteis naturais e confortáveis,  
sem conflitos com a rolagem nativa do navegador e com comandos táteis alternativos acessíveis.

**Why this priority**: Assegura que a exploração espacial seja verdadeiramente multiplataforma, viabilizando o uso do Caderno de Leitura tanto na mesa quanto na poltrona ou em trânsito com celular.

**Independent Test**: Acessar o Canvas em tela sensível ao toque, navegar com gestos de pinça (*pinch-to-zoom*) e arrasto de fundo, manipular cards individualmente e utilizar botões dedicados de controle com alvos de toque mínimos de 44x44px.

**Acceptance Scenarios**:
1. **Given** um smartphone ou tablet, **When** o leitor realiza o gesto de pinça com dois dedos sobre a tela, **Then** o zoom do Canvas é ajustado suavemente proporcional à distância entre os dedos.
2. **Given** a navegação tátil no dispositivo móvel, **When** o leitor desliza o dedo pelo fundo livre da tela, **Then** a tela realiza pan sem acionar a rolagem da página inteira do navegador.
3. **Given** o usuário em dispositivo móvel, **When** precisa de comandos de aproximação ou recentralização rápida, **Then** dispõe de botões táteis flutuantes acessíveis (+, -, centralizar) com área de toque mínima de 44x44px.
4. **Given** o usuário navegando via teclado, **When** foca em um card de estudo, **Then** pode alternar o foco para cards adjacentes com `Tab` / `Shift+Tab` e ajustar a posição do card focado usando as setas direcionais do teclado.

---

### Edge Cases

- **O que acontece quando novos estudos são criados sem nenhuma coordenada espacial prévia?** O sistema aplica automaticamente um arranjo em grade inicial (*auto-grid*) organizado por capítulo a partir da origem (0, 0) com espaçamento de 24px, posicionando novos cards adjacentes aos já existentes sem gerar sobreposições acidentais.
- **O que acontece ao clicar em "Ajustar à Tela" quando não há nenhum estudo cadastrado?** O viewport centraliza na origem (0, 0) com zoom em 100% e exibe uma mensagem neutra e discreta informando que não há anotações a enquadrar.
- **O que acontece se o leitor der zoom excessivo ou afastar excessivamente?** O sistema aplica limites rígidos (*clamping*) entre 25% (0.25x) e 200% (2.0x), impedindo que os nós desapareçam ou fiquem pixelados além do limite legível.
- **O que acontece se o leitor arrastar um card em alta velocidade para fora do campo visível?** O mini-mapa expande seu cálculo de coordenadas para incluir o nó na silhueta geral, e o botão "Ajustar à Tela" permite resgatá-lo a qualquer momento.
- **O que acontece se houver conflito de concorrência ou atualização concorrente das posições de cards?** As coordenadas usam controle de concorrência otimista com atualização transacional de lotes de posições (`updated_at`), sem bloquear nem corromper dados do estudo.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um viewport bidimensional infinito (Canvas 2D) com capacidade contínua de translação (pan) e escala (zoom).
- **FR-002**: O sistema DEVE persistir e restaurar o estado do viewport (coordenadas de pan x/y e fator de zoom) localmente no navegador por livro.
- **FR-003**: O sistema DEVE renderizar cada estudo como um card interativo contendo título, resumo/trecho e metadados essenciais.
- **FR-004**: O sistema DEVE permitir o reposicionamento livre de cards no espaço bidimensional através de arrasto direto do ponteiro ou toque.
- **FR-005**: O sistema DEVE persistir as coordenadas espaciais (`pos_x`, `pos_y`, `width`, `height`, `z_index`) de forma isolada, em tabela dedicada (`study_canvas_nodes`), sem jamais modificar `parent_study_id`, `position` ou a ordem dos capítulos na tabela `studies`.
- **FR-006**: O sistema DEVE operar o Canvas de Estudos com escopo delimitado por Livro, onde cada obra possui sua própria prancha bidimensional contendo todos os estudos e capítulos daquela obra, com coordenadas e nós persistidos de forma isolada.
- **FR-007**: O sistema DEVE alocar novos estudos (ou estudos existentes sem coordenadas prévias) através de um algoritmo de distribuição automática em grade (*auto-grid* por capítulo), dispondo os cards em colunas com espaçamento regular (24px) a partir da origem (0, 0) sem sobreposição.
- **FR-008**: O sistema DEVE suportar seleção individual (clique no card) e seleção múltipla em bloco através de retângulo de seleção (*marquee selection*) no fundo livre.
- **FR-009**: O sistema DEVE permitir a movimentação conjunta de todos os cards atualmente selecionados, preservando suas distâncias relativas durante o arrasto.
- **FR-010**: O sistema DEVE exibir um mini-mapa interativo (*radar view*) posicionado no canto inferior, refletindo a distribuição de todos os nós e a janela de visão ativa, permitindo clique para teletransporte do viewport.
- **FR-011**: O sistema DEVE disponibilizar barra de ferramentas com botões de zoom in (+), zoom out (-), resetar zoom (100%) e "Ajustar à Tela" (*Fit to View*), calculando a caixa delimitadora (*bounding box*) de todos os nós.
- **FR-012**: O sistema DEVE assegurar ergonomia tátil para dispositivos móveis através de toque direto inteligente (arrasto sobre o card reposiciona o card; arrasto no fundo livre executa pan do viewport; pinça com dois dedos executa zoom) e botões flutuantes acessíveis de zoom e recentralização com alvos mínimos de 44x44px.
- **FR-013**: O sistema DEVE garantir que o deslocamento espacial utilize aceleração gráfica por hardware (`translate3d` e `scale`), mantendo taxa de quadros estável (60fps) e respeitando a preferência de movimento reduzido (`prefers-reduced-motion`).

---

### Key Entities

- **Canvas 2D (SpatialCanvas)**: Espaço euclidiano bidimensional contínuo que abriga projeções espaciais de estudos associados a uma obra ou contexto.
- **Nó de Estudo no Canvas (CanvasNode)**: Registro de layout que relaciona um estudo (`study_id`) às suas coordenadas espaciais (`pos_x`, `pos_y`), dimensões opcionais (`width`, `height`), ordem de empilhamento (`z_index`) e tag de cor visual.
- **Janela de Visão (CanvasViewport)**: Estado do observador no espaço composto por deslocamento horizontal (`pan_x`), deslocamento vertical (`pan_y`) e fator multiplicador de escala (`zoom`).
- **Mini-mapa / Radar (CanvasMinimap)**: Projeção escalar reduzida do universo de nós que calcula a razão de aspecto global e exibe o retângulo correspondente à área visível da tela.
- **Seleção Espacial (CanvasSelection)**: Conjunto transitório de nós marcados para manipulação em lote ou inspeção conjunta.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue navegar pelo Canvas com pan e zoom contínuos mantendo resposta visual imediata (latência de ponteiro < 16ms, taxa de 60fps) em cenários de até 100 cards de estudos.
- **SC-002**: A movimentação e soltura de cards de estudos reflete a persistência das coordenadas no sistema em menos de 500ms, sem bloqueio da interface.
- **SC-003**: 100% das operações de movimentação no Canvas preservam intactas a estrutura hierárquica e a ordem de capítulos dos estudos.
- **SC-004**: O comando "Ajustar à Tela" enquadra com precisão todos os cards do Canvas em uma única animação fluida em menos de 300ms.
- **SC-005**: Todas as áreas de toque em telas móveis e botões de comando do canvas cumprem a dimensão mínima de 44x44px.
- **SC-006**: Usuários de teclado conseguem alternar o foco entre nós do canvas e ajustar coordenadas sem necessidade exclusiva de dispositivo apontador.

---

## Assumptions

- O Canvas de Estudos da versão 0.4 não inclui ferramentas de desenho à mão livre (caneta/lápis) nem conexões semânticas com setas rotuladas (estas pertencem à feature F04 — Relações entre Estudos).
- As coordenadas do Canvas representam posições lógicas contínuas em pixels no espaço de coordenadas do mundo (world coordinates), mapeadas para pixels de tela via transformação matricial afim.
- A integridade do acervo físico e o banco de dados do usuário nunca são comprometidos durante testes ou migrações; testes utilizam bancos descartáveis e instâncias isoladas em `tmp_path`.
- O leitor mantém autonomia absoluta: o Canvas é uma lente de visualização intercambiável e opcional, podendo alternar a qualquer momento para Grade, Lista ou Árvore sem qualquer perda de dados.
