# Feature Specification: F0.8.14 — Visualizações Móveis e Responsividade da Biblioteca de Destaques

**Feature Branch**: `080-visualizacoes-e-destaques-moveis`  
**Created**: 2026-10-12  
**Status**: Draft  
**Input**: User description: "0.8.14, além das views adicoine também a responsivibilidade da tela de destaques em dispositivos móveis, que atualmente está ultrapassando a largura da página e a aba inferior estão desconfiguradas"

---

## 1. Visão Geral e Contexto do Problema

Esta especificação cobre a entrega conjunta de dois eixos essenciais de ergonomia e acessibilidade em dispositivos móveis:

1. **Adaptação das Visualizações Complexas de Estudos (Map, Canvas e Tree)**:
   - **Map View (`StudyMapView.vue`)**: Atualmente restrito a interações com mouse (arrasto e roda do mouse), sem suporte a toques múltiplos (pan e pinch zoom) e com arestas relacionais difíceis de selecionar no celular devido a mini-badges diminutos.
   - **Canvas View (`StudyCanvasView.vue`)**: Bloqueia a rolagem vertical natural da página do leitor em smartphones através de `touch-action: none` em um palco de 680px, além de possuir uma barra de ferramentas com botões dispersos que se comprimem em telas estreitas.
   - **Tree View (`StudyTreeView.vue`)**: Apresenta alças de arrasto invisíveis em dispositivos de toque (`pointer: coarse`) e carece de mecanismos acessíveis por toque para reordenação e rebaixamento hierárquico.
   - **Palco de Estudos (`SplitLayout`)**: Necessita de adaptação flexível baseada no contêiner do palco (container queries), prevenindo deformações quando gavetas e painéis laterais estiverem abertos.

2. **Correção de Responsividade da Biblioteca de Destaques (`HighlightsLibraryView.vue`)**:
   - **Transbordamento Horizontal da Página**: A barra de ferramentas de busca e filtros (`HighlightFilterToolbar.vue`) utiliza uma linha primária flexível rígida (`.toolbar-primary-row`) sem permissão de quebra (`flex-wrap: wrap`), somando mais de 480px de largura mínima fixa. Isso força a página a ultrapassar a largura do viewport (`scrollWidth > clientWidth`), criando uma rolagem horizontal inconveniente em telas de 320px a 430px.
   - **Desconfiguração e Sobreposição da Barra Inferior (`MobileTabBar`)**: A navegação fixa inferior sofre deslocamentos e distorções visuais quando a página sofre rolagem horizontal. Adicionalmente, a tela de destaques não reserva espaçamento inferior suficiente com `--mobile-nav-offset`, fazendo com que os controles de paginação e o rodapé fiquem escondidos ou sobrepostos sob a barra inferior fixa.

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 - Biblioteca de Destaques sem Transbordamento e com Navegação Inferior Íntegra (Priority: P1)

Como leitor acessando minha biblioteca de destaques no celular (320px a 767px),  
quero que a tela se ajuste perfeitamente à largura do meu aparelho sem rolagem horizontal, com o campo de busca e filtros reorganizados em linhas confortáveis, e que a barra de navegação inferior permaneça fixa e perfeitamente ancorada sem encobrir a paginação ou o último destaque.

**Why this priority**: É um defeito visual crítico e imediatamente perceptível que compromete a navegação global do sistema e impede a consulta fluida dos grifos e notas de estudo.

**Independent Test**: Acessar a rota `/destaques` em emuladores de 320px, 375px e 430px; verificar que `document.documentElement.scrollWidth === document.documentElement.clientWidth`, que a busca e os seletores quebram sem transbordar, que a paginação fica totalmente visível acima da barra inferior e que a aba "Destaques" exibe estado ativo.

**Acceptance Scenarios**:
1. **Dado** um smartphone com largura entre 320px e 767px na rota `/destaques`, **quando** a página for renderizada, **então** a largura do documento não excede o viewport e nenhuma barra de rolagem horizontal surge na tela.
2. **Dado** a barra primária de filtros (`HighlightFilterToolbar`), **quando** visualizada em viewport móvel ($\le 767\text{px}$), **então** o campo de busca ocupa a linha superior integralmente (100% de largura) e os controles de modo ("Recentes" / "Por Obra") e o gatilho de filtros com badge quebram suavemente para a linha inferior.
3. **Dado** a lista de destaques com múltiplas páginas, **quando** o usuário rola até o fim da tela, **então** os botões de paginação mantêm espaçamento seguro acima da barra inferior móvel (`MobileTabBar`), sem qualquer sobreposição.
4. **Dado** a barra inferior móvel fixa, **quando** o usuário navega na tela de destaques, **então** a barra permanece 100% ancorada na base da tela, ocupando 100% da largura visual sem descolamentos ou cortes.

---

### User Story 2 - Navegação Tátil e Alternativa Acessível no Mapa de Estudos (Priority: P1)

Como estudante utilizando o modo Mapa (`StudyMapView`) no celular ou tablet,  
quero interagir com o grafo através de gestos naturais de toque (arrasto com um dedo para pan e pinça com dois dedos para zoom), além de poder alternar para uma visão em lista/outline semântico de relações que permita ler e gerenciar conexões sem depender de cliques precisos em arestas SVG microscópicas.

**Why this priority**: Gráficos radiais sem gestos táteis ou sem visualização textual alternativa tornam-se completamente inacessíveis e frustrantes em telas de toque.

**Independent Test**: Abrir o modo Mapa em viewport móvel; arrastar a tela com um dedo e verificar pan suave; fazer gesto de pinça e verificar zoom delimitado; alternar para a visão em lista semântica e executar edição/exclusão de uma relação através de botões táteis com alvo $\ge 44 \times 44\text{ px}$.

**Acceptance Scenarios**:
1. **Dado** o palco do Mapa em dispositivo de toque, **quando** o usuário arrasta a superfície com um dedo, **então** o centro do grafo se desloca suavemente acompanhando o toque (pan).
2. **Dado** o palco do Mapa, **quando** o usuário executa o gesto de pinça com dois dedos, **então** o nível de zoom se ajusta proporcionalmente dentro dos limites mínimo (0.5x) e máximo (2.5x).
3. **Dado** uma tela compacta ($\le 767\text{px}$), **quando** o mapa for aberto, **então** a interface oferece um alternador claro entre visualização radial e lista semântica de conexões.
4. **Dado** a lista semântica de conexões no celular, **quando** o leitor seleciona uma relação, **então** ações de alterar tipo de vínculo, inverter direção e desvincular são acionáveis por botões táteis com alvos $\ge 44 \times 44\text{ px}$.

---

### User Story 3 - Rolagem Vertical e Exploração Tátil no Canvas de Estudos (Priority: P2)

Como leitor navegando em um capítulo com múltiplos estudos no Canvas (`StudyCanvasView`) no smartphone,  
quero poder rolar a página verticalmente sem que o palco do canvas prenda o gesto do meu dedo com `touch-action: none`, e quero explorar os estudos organizados em blocos/molduras legíveis sem que a toolbar horizontal estoure as margens da tela.

**Why this priority**: O bloqueio de rolagem por `touch-action: none` prende o usuário na tela, impedindo que ele alcance o restante da página e do conteúdo.

**Independent Test**: Navegar para um capítulo no modo Canvas em tela móvel; verificar que deslizar o dedo verticalmente na tela rola a página normalmente; verificar que ferramentas do canvas ficam agrupadas em menu suspenso ou toolbar compacta em telas $< 1024\text{px}$.

**Acceptance Scenarios**:
1. **Dado** a visualização Canvas em tela de smartphone ($\le 767\text{px}$), **quando** o usuário toca e desliza o dedo verticalmente sobre o palco, **então** a página do navegador rola normalmente sem ser bloqueada.
2. **Dado** o modo Canvas no celular, **quando** renderizado, **então** os estudos são apresentados em um fluxo responsivo de cartões ou molduras verticais com navegação assistida por toque.
3. **Dado** a barra de ferramentas do Canvas em telas móveis e tablets ($< 1024\text{px}$), **quando** o espaço for restrito, **então** controles secundários são compactados em menu suspenso, preservando espaço útil e sem estourar a largura do contêiner.

---

### User Story 4 - Hierarquia e Reordenação Acessível na Árvore de Estudos (Priority: P2)

Como usuário organizando a árvore de estudos (`StudyTreeView`) em um tablet ou celular,  
quero visualizar os ramos com linhas guias nítidas e poder reordenar ou rebaixar nós através de ações contextuais explícitas ("Subir", "Descer", "Aninhar sob..."), sem depender exclusivamente do arrasto de mouse incompatível com telas sensíveis ao toque.

**Why this priority**: Drag-and-drop de árvore de precisão em mobile frequentemente gera conflitos de rolagem de página e falhas de soltura.

**Independent Test**: Abrir a Árvore de Estudos em emulação de toque (`pointer: coarse`); confirmar que cada item da árvore oferece menu contextual tátil ("⋯") com opções acessíveis de movimentação que persistem a nova ordenação e hierarquia.

**Acceptance Scenarios**:
1. **Dado** um dispositivo de toque com `pointer: coarse`, **quando** a Árvore de Estudos é exibida, **então** alças de arrasto invisíveis/inoperantes são ocultadas e o menu contextual de ações de cada nó fica evidenciado com alvo de toque $\ge 44 \times 44\text{ px}$.
2. **Dado** o menu contextual de um nó da árvore, **quando** o usuário seleciona "Mover para cima" ou "Mover para baixo", **então** a ordem entre irmãos é alterada imediatamente e persistida.
3. **Dado** ramos aninhados em telas estreitas, **quando** a indentação atinge mais de 3 níveis, **então** a árvore aplica compressão proporcional das margens para evitar que o texto do nó seja espremido contra a margem direita.

---

## 3. Casos de Borda (Edge Cases)

1. **Card de destaque com citação muito longa e livro com título extenso**:
   - O título do livro e do capítulo no cabeçalho do `HighlightCard` devem truncar com reticências (`text-overflow: ellipsis; white-space: nowrap`), sem empurrar as badges semânticas para fora do card.
   - O botão "Abrir no Estudo" e o botão de exclusão no rodapé do card devem quebrar suavemente em linha única ou empilhar em alvos táteis completos em $\le 360\text{px}$.
2. **Teclado virtual aberto durante a busca de destaques**:
   - O campo de busca deve manter o foco sem que a gaveta de filtros ou a barra inferior móvel causem salto visual ou cubram o campo ativo.
3. **Capítulo sem estudos no Mapa ou Canvas**:
   - Estados vazios devem renderizar ícone e mensagem acolhedora sem altura fixa desproporcional nem distorções em telas verticais de 320px.
4. **Alternância rápida entre orientação Retrato e Paisagem no smartphone**:
   - A barra inferior e os palcos de visualização devem recalcular suas dimensões reativamente sem reter larguras obsoletas ou criar overflow residual.

---

## 4. Requisitos *(mandatory)*

### Requisitos Funcionais

- **FR-001**: O sistema DEVE garantir que a rota `/destaques` apresente `scrollWidth <= clientWidth` em todas as larguras de tela entre 320px e 767px.
- **FR-002**: A barra de ferramentas `HighlightFilterToolbar` DEVE permitir quebra de linha (`flex-wrap: wrap`) em sua linha primária, expandindo o campo de busca para 100% da largura em viewports móveis ($\le 767\text{px}$).
- **FR-003**: Os controles de modo de visualização e o botão de acionamento de filtros da `HighlightFilterToolbar` DEVEM posicionar-se lado a lado abaixo do campo de busca em telas móveis, garantindo alvos de toque $\ge 44 \times 44\text{ px}$.
- **FR-004**: A visualização `HighlightsLibraryView` DEVE aplicar espaçamento inferior dinâmico utilizando `--mobile-nav-offset`, prevenindo que a barra de paginação e o último card sejam encobertos pela barra inferior móvel (`MobileTabBar`).
- **FR-005**: O componente `MobileTabBar` DEVE manter posicionamento fixo ancorado e largura consistente de 100% da janela visual sem sofrer distorções quando o usuário interagir com a tela de destaques.
- **FR-006**: O modo Mapa (`StudyMapView`) DEVE suportar gestos de toque com pan (um dedo) e zoom proporcional (pinça com dois dedos) em telas sensíveis ao toque.
- **FR-007**: O modo Mapa DEVE oferecer um modo de exibição alternativo em lista semântica de relações no celular, permitindo leitura e edição de arestas sem depender de cliques em elementos gráficos diminutos.
- **FR-008**: O modo Canvas (`StudyCanvasView`) DEVE desativar o bloqueio irrestrito de rolagem vertical (`touch-action: none`) em smartphones ($\le 767\text{px}$), permitindo que o usuário role a página normalmente.
- **FR-009**: A barra de ferramentas do Canvas DEVE compactar ações secundárias em menu suspenso acessível em viewports menores que 1024px.
- **FR-010**: A Árvore de Estudos (`StudyTreeView`) DEVE oferecer ações contextuais de reordenação ("Mover para cima", "Mover para baixo") e aninhamento no menu tátil de cada nó, suprimindo alças de arrasto dependentes de mouse sob `@media (pointer: coarse)`.
- **FR-011**: O palco central de estudos dentro do `SplitLayout` DEVE adotar container queries (`container-type: inline-size; container-name: study-stage`) para adaptar a densidade das visualizações ao espaço real disponível.
- **FR-012**: Todos os elementos interativos, botões de ação e itens de menu introduzidos ou ajustados DEVEM respeitar a área de toque mínima de $44 \times 44\text{ px}$ no mobile.
- **FR-013**: O código e documentação DEVEM manter estrita conformidade com a política de Zero Emojis do projeto.

### Entidades e Componentes Relevantes

- **HighlightFilterToolbar**: Componente de busca instantânea, alternador de modo ("Recentes" / "Por Obra") e filtros por livro, tipo e cor semântica.
- **HighlightCard**: Cartão individual de destaque com citação, nota reflexiva, badges e ações de contexto.
- **HighlightsLibraryView**: View principal da rota `/destaques` com listagem paginada, agrupamentos e barra de paginação.
- **StudyMapView**: Componente de visualização radial de estudos e grafo de conexões.
- **StudyCanvasView**: Componente de organização espacial livre de estudos.
- **StudyTreeView**: Componente de navegação em árvore hierárquica de estudos.
- **MobileTabBar**: Barra de navegação inferior global com 5 destinos primários.

---

## 5. Critérios de Sucesso *(mandatory)*

### Resultados Mensuráveis

- **SC-001**: 100% das páginas testadas na rota `/destaques` e nos 3 modos de estudo (Map, Canvas, Tree) apresentam zero rolagem horizontal (`scrollWidth === clientWidth`) em viewports de 320px, 375px, 390px, 430px e 767px.
- **SC-002**: A barra de navegação inferior (`MobileTabBar`) permanece visível, funcional e sem sobreposição sobre o conteúdo em 100% das telas da biblioteca de destaques.
- **SC-003**: 100% dos botões, inputs e gatilhos de menu nas telas ajustadas possuem área de toque comprovada $\ge 44 \times 44\text{ px}$ em visualizações móveis.
- **SC-004**: Gestos de toque de arrasto (pan) e pinça (zoom) respondem com fluidez em dispositivos de toque no Map View sem travar a interface.
- **SC-005**: 100% das suítes de testes (`npm test`, `pytest`, `npm run build`) executam com sucesso e zero falhas de regressão.

---

## 6. Suposições e Restrições de Escopo

- **Persistência de Preferências**: As escolhas de modo de visualização continuam sendo persistidas no `localStorage` sob as chaves existentes (`caderno_highlights_view_mode`, `caderno_active_view_mode`).
- **Isolamento de Dados**: Toda validação em tempo de execução deve empregar exclusivamente bancos descartáveis e dados sintéticos, em respeito ao Artigo I e II da Constituição.
- **Fronteira Tecnológica**: Não serão adicionadas bibliotecas externas de gráficos ou gestos (o projeto continua com Vue 3 nativo e CSS autoral sem Tailwind).
