# Feature Specification: F 0.7.7 — Redesenho da Map View (Criação e Edição de Grafo Semântico)

**Feature Branch**: `056-redesenho-map-view`  
**Created**: 2026-10-04  
**Status**: Draft  
**Input**: User description: "/speckit-specify F0.7.7"  

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualização Radial Semântica e Destaque do Estudo Núcleo (Priority: P1) 🎯 MVP

O leitor acessa a aba "Mapa" (Map View) de um capítulo ou livro para compreender visualmente a teia de relações cognitivas e argumentativas entre seus estudos. O estudo ativo ou foco principal aparece destacado no centro como "Estudo Núcleo" com tipografia proeminente, elevação visual e halo dimensional, enquanto os estudos conectados orbitam ao redor em raios proporcionais, unidos por arestas direcionadas com setas e rótulos semânticos legíveis.

**Why this priority**: É a essência e o valor primário da Map View (MVP). Sem uma visualização relacional clara que distinga o estudo central das ramificações periféricas, a navegação em grafo perde sua finalidade analítica.

**Independent Test**: Carregar um capítulo com estudos interconectados por relações semânticas existentes; alternar para a Map View; verificar que o estudo focal é exibido como nó central destacado e os estudos relacionados aparecem conectados por arestas direcionadas com rótulos visíveis e navegação suave de pan/zoom.

**Acceptance Scenarios**:
1. **Given** um capítulo com múltiplos estudos e relações semânticas cadastradas, **When** o usuário entra na Map View, **Then** o estudo central/selecionado é renderizado no ponto focal com realce visual distintivo e os estudos relacionados aparecem posicionados ao redor com arestas direcionadas conectando-os.
2. **Given** o mapa carregado, **When** o usuário interage através de pan (arrasto com mouse/dois dedos) ou zoom (scroll da roda do mouse ou gesto de pinça), **Then** o viewport responde com fluidez a 60fps mantendo os nós e rótulos de conexões nítidos e legíveis.
3. **Given** o mapa visível, **When** o usuário clica em um nó periférico, **Then** o sistema seleciona o nó, destaca suas conexões imediatas e permite navegar para a leitura integral daquele estudo.

---

### User Story 2 - Traçado Interativo de Conexões e Mini-Popover de Relações (Priority: P2)

O leitor deseja conectar duas ideias ou argumentos diretamente no mapa sem precisar navegar por formulários externos. Ao passar o cursor ou tocar em um nó de estudo, surge uma alça de conexão; ao arrastar dessa alça até outro nó de estudo no mapa, uma linha elástica guia o movimento. Ao soltar sobre o nó de destino, abre-se um mini-popover contextual no próprio ponto de soltura permitindo selecionar o tipo canônico da relação (*Fundamenta*, *Desdobra*, *Contradiz*, *Sintetiza*, *Cita*, *Complementa*) e opcionalmente uma breve justificativa, persistindo a relação imediatamente na base de dados.

**Why this priority**: Transforma a Map View de uma visualização puramente passiva em um instrumento ativo de síntese e modelagem conceitual.

**Independent Test**: Arrastar a alça de conexão de um Estudo A até um Estudo B; confirmar que o popover se abre exibindo as opções semânticas orientadas; selecionar "fundamenta" e salvar; verificar que a aresta com o rótulo é renderizada e salva via API de relações.

**Acceptance Scenarios**:
1. **Given** dois nós no mapa sem relação direta, **When** o usuário arrasta a alça conectora do nó A e solta sobre o nó B, **Then** um mini-popover contextual abre-se ancorado no nó de destino apresentando as opções semânticas de conexão com indicação clara da direção do raciocínio.
2. **Given** o popover de conexão aberto, **When** o usuário escolhe um tipo de relação e confirma, **Then** uma nova relação semântica é criada e persistida via API, e a aresta correspondente passa a ser desenhada com seu rótulo e sentido direcional no grafo.
3. **Given** uma aresta existente selecionada, **When** o usuário clica sobre ela ou em seu rótulo, **Then** o popover permite alterar o tipo da relação, editar a justificativa ou remover a conexão com confirmação instantânea.

---

### User Story 3 - Criação Direta de Estudos no Mapa e Ergonomia Mobile (Priority: P3)

Durante a exploração do grafo, o leitor percebe uma lacuna conceitual e deseja criar um novo estudo diretamente naquele ponto do raciocínio. Através de um duplo clique em uma área livre do mapa ou do botão flutuante "+ Novo Estudo", abre-se um cartão de criação rápida in-place (solicitando Título e Seção Inicial). O estudo é criado imediatamente e, caso o usuário tenha iniciado a ação a partir de um nó existente, a conexão entre eles já é gerada atomicamente. Em dispositivos móveis (< 768px), a criação e o traçado de conexões operam com ergonomia assistida por toque (botão tátil "Conectar a...") e alvos mínimos de 44×44px.

**Why this priority**: Fecha o ciclo de pensamento vivo, permitindo que novas ideias sejam capturadas no exato instante em que emergem na exploração relacional, com plena acessibilidade em telas táteis.

**Independent Test**: Executar duplo clique em área livre ou tocar no botão flutuante no mobile; preencher título; confirmar; verificar que o novo nó aparece no grafo posicionado e registrado no capítulo. No mobile, acionar o modo assistido de conexão e validar os alvos de 44px.

**Acceptance Scenarios**:
1. **Given** a Map View em tela ampla, **When** o usuário faz duplo clique em uma coordenada livre do mapa, **Then** surge um cartão de criação rápida no ponto exato, permitindo informar o título e registrar o estudo no capítulo ativo sem sair do mapa.
2. **Given** um nó selecionado, **When** o usuário clica na ação "Desdobrar novo estudo", **Then** o novo estudo é criado e automaticamente conectado ao nó original com a relação selecionada.
3. **Given** visualização em dispositivo móvel (< 768px), **When** o usuário toca em um nó, **Then** uma barra de ações táteis de rodapé oferece botões de 44×44px para "Conectar a...", "Ver Estudo" e "Novo Estudo Conectado", viabilizando a conexão sem exigir arrasto touch impreciso.

---

### Edge Cases

- **Tentativa de Auto-relação**: O que acontece se o usuário arrastar a linha conectora de volta para o próprio nó de origem? O sistema bloqueia a ação, cancela a linha elástica e não abre o popover de criação de relação.
- **Relação Duplicada**: O que acontece se já existir uma conexão idêntica no mesmo sentido entre os nós A e B? O popover sinaliza que a conexão já existe e oferece a opção de editá-la ou invertê-la, impedindo duplicação no banco de dados.
- **Grafo com Muitos Nós (Alta Densidade)**: Como o sistema se comporta em capítulos com 30 ou mais estudos? O mapa aplica escala dinâmica e permite filtrar nós por tipo de relação ou focar em subgrafos de 1 a 2 graus de separação a partir do nó núcleo para manter a legibilidade.
- **Capítulo sem Estudos ou Estudo Isolado**: O que acontece em capítulos com apenas 1 estudo ou sem relações? O sistema renderiza o estudo central em destaque com estado acolhedor explicando como puxar conexões ou usar o botão "+" para criar o próximo nó.
- **Falha de Rede ao Criar Relação**: Se a requisição de criação de relação falhar (ex.: erro 500 ou perda de conexão), a linha elástica é desfeita e uma notificação de erro amigável é exibida sem travar o canvas.

---

## Clarifications

### Session 2026-10-04
- **Q1: Padrão de layout e disposição dos nós**: Opção A adotada. Layout radial concêntrico automático com anéis orbitais e algoritmo de repulsão suave que evita sobreposição de cartões e mantém estabilidade visual determinística.
- **Q2: Fluxo de criação rápida de novo estudo**: Opção A adotada. Mini-card inline no próprio ponto de clique do mapa com foco automático no título e seletor rápido de tipo de seção (Resumo, Conceito ou Explicação), salvando com `Enter` sem abrir modais intrusivos.
- **Q3: Convenção de sentido e orientação das relações**: Opção A adotada. Sentido orientado ativo com setas direcionais nas arestas, oração ativa no popover (*"Estudo A [fundamenta / desdobra / contradiz / complementa / sintetiza / cita] Estudo B"*) e botão de inversão rápida (`⇄`) para alternar a direção do argumento em 1 clique.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE renderizar os estudos de um capítulo ou livro na Map View com clara diferenciação visual do Estudo Núcleo (maior dimensão, contraste realçado e halo indicativo) em relação aos nós periféricos.
- **FR-002**: O sistema DEVE traçar arestas direcionadas entre estudos interconectados, exibindo setas indicativas de sentido e rótulos semânticos legíveis (*fundamenta*, *desdobra*, *contradiz*, *sintetiza*, *cita*, *complementa*).
- **FR-003**: O sistema DEVE permitir traçar novas conexões diretamente na interface do mapa através de arrasto de alça conectora entre dois nós de estudo.
- **FR-004**: Ao soltar a conexão entre dois estudos válidos, o sistema DEVE abrir um mini-popover contextual (`MapRelationPopover`) permitindo selecionar o tipo canônico da relação sem recarregar ou trocar de página.
- **FR-005**: O sistema DEVE proibir terminantemente auto-relações (conectar um estudo a si mesmo) e rejeitar a criação de relações idênticas redundantes.
- **FR-006**: O sistema DEVE permitir criar um novo estudo diretamente na Map View (via botão flutuante "+" ou duplo clique em ponto livre do mapa), persistindo o estudo no capítulo ativo e posicionando-o no grafo.
- **FR-007**: O sistema DEVE permitir criar um novo estudo vinculado atomicamente a um estudo existente, gerando simultaneamente o registro do estudo e sua relação semântica correspondente.
- **FR-008**: O sistema DEVE suportar navegação fluida pelo mapa através de pan (arrasto do fundo) e zoom suave (roda do mouse, botões +/- e gesto pinça no mobile).
- **FR-009**: Em dispositivos móveis (< 768px), o sistema DEVE disponibilizar modo assistido de conexão por toque com alvos táteis mínimos de 44×44px, dispensando a necessidade de arrasto contínuo com os dedos.
- **FR-010**: O sistema DEVE fornecer uma visão textual/tabela alternativa acessível para leitores de tela com a lista de estudos e suas relações semânticas para conformidade WCAG 2.2.
- **FR-011**: O sistema DEVE organizar automaticamente o grafo em layout radial concêntrico com anéis orbitais ao redor do Estudo Núcleo e física de repulsão suave para evitar sobreposição de nós.
- **FR-012**: O sistema DEVE disponibilizar mini-card inline in-place para criação rápida de novos estudos diretamente no ponto do clique (solicitando Título e Seção Inicial), salvando com tecla Enter e inserindo o nó imediatamente no grafo.
- **FR-013**: O sistema DEVE representar relações semânticas como conexões orientadas ativas com setas direcionadas e disponibilizar no popover oração ativa de sentido com botão de inversão rápida (⇄) para alternar a direção em 1 clique.

---

### Key Entities

- **StudyNode (Nó do Grafo)**: Representa um estudo dentro do grafo espacial. Atributos: `id`, `title`, `location`, `reading_status`, `is_core` (se é o estudo núcleo selecionado), coordenadas visuais `(x, y)` e grau de conexões.
- **StudyRelationEdge (Aresta do Grafo)**: Representa uma conexão semântica direcionada entre dois estudos. Atributos: `id`, `source_study_id`, `target_study_id`, `relation_type` (*fundamenta*, *desdobra*, *contradiz*, *sintetiza*, *cita*, *complementa*), `description` (justificativa opcional) e coordenadas calculadas de ancoragem.
- **MapViewport**: Estado de navegação da câmera no espaço bidimensional. Atributos: deslocamento horizontal `pan_x`, deslocamento vertical `pan_y` e escala de aproximação `zoom_level`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuário consegue traçar uma nova relação semântica entre dois estudos e salvá-la em menos de 10 segundos, sem qualquer recarregamento de página.
- **SC-002**: O tempo de renderização inicial do grafo e resposta de pan/zoom mantém taxa estável de 60 quadros por segundo em capítulos com até 40 estudos conectados.
- **SC-003**: 100% das tentativas de auto-relação ou criação de conexões inválidas são interceptadas na interface com feedback claro e sem erros de console.
- **SC-004**: Em telas móveis (< 768px), o usuário consegue conectar dois estudos através do modo assistido de toque em até 3 toques com botões respeitando as dimensões mínimas de 44×44px.

---

## Assumptions

- A tabela `study_relations` e seus serviços de backend existentes continuam sendo o repositório canônico de dados das relações semânticas entre estudos.
- A visualização em mapa complementa a Tree View e a Grid/List View, tendo como missão cognitiva exclusiva o raciocínio em rede e argumentação não-linear.
- A criação de frames/molduras livres coloridas é uma prerrogativa exclusiva da Canvas View (F 0.7.8), mantendo a Map View focada estritamente em relações semânticas e grafos de argumentos.
