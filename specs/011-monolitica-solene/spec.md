# Feature Specification: 011 — Monolítica: Superclasse Pesada & Solene (Brutalista & Arquitetura em Pedra)

**Feature Branch**: `011-monolitica-solene`  
**Created**: 2026-09-19  
**Status**: Ready  
**Input**: User description: "Implementação da Superclasse 'Monolítica' (Pesada & Solene — Brutalista, blocos densos, cantos retos, linhas sólidas e transições ponderadas)"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ativação da Superclasse Monolítica com Cantos Estritamente Retos e Ausência de Sombras Flutuantes (Priority: P1) 🎯 MVP

Como leitor explorando o acervo de livros e cadernos de estudo,  
Quero selecionar a Superclasse "Monolítica" nas opções de aparência da aplicação,  
Para que todos os recipientes, cartões de livros, painéis e botões adotem cantos estritamente retos (`0px`), ausência de sombras flutuantes difusas e contornos estruturais densos, transmitindo uma sensação de solidez arquitetônica, monumentalidade e permanência como estruturas talhadas em pedra.

**Why this priority**: É o núcleo fundacional da Superclasse Monolítica. Estabelece a assinatura geométrica brutalista e o peso visual da interface, entregando valor imediato e testável de forma independente como MVP.

**Independent Test**: Ativar "Monolítica" nas configurações de aparência, navegar para a estante de livros e constatar que:
1. Todos os cartões de livros (`.book-card`), painéis, formulários e botões possuem cantos estritamente retos (`border-radius: 0px`).
2. Sombras difusas e elevações flutuantes são totalmente ausentes; o relevo é definido pelo peso de linhas e bordas estruturais sólidas.
3. Não ocorrem inclinações 3D, flutuações magnéticas ou desmaterializações transparentes.
4. As 24 fontes tipográficas, os 10 temas de cor e os espaçamentos permanecem rigorosamente preservados.

**Acceptance Scenarios**:
1. **Given** o usuário na tela de Ajustes, **When** seleciona a Superclasse "Monolítica — Pesada & Solene", **Then** a classe `.superclass-monolitica` e o atributo `data-superclass="monolitica"` são ativados imediatamente no elemento raiz sem recarregar a página.
2. **Given** os cartões de livros e painéis sob a Monolítica, **When** renderizados na interface, **Then** todos exibem cantos retos (`0px`), contornos sólidos demarcados e nenhuma sombra difusa de repouso.
3. **Given** um botão global de ação sob a Monolítica, **When** exibido em tela, **Then** apresenta geometria retangular pura, bordas estruturais nítidas e ausência de cantos arredondados.

---

### User Story 2 - Microinterações Solenes e Inversão de Alto Contraste no Hover e Active (Priority: P2)

Como leitor interagindo com o acervo e ferramentas do caderno,  
Quero que o foco, o repouso do cursor (*hover*) e o clique (*active*) respondam com solenidade, permanência e alto contraste,  
Para sentir uma resposta ponderada e firme, como o assentamento de um bloco de pedra, sem saltos físicos levianos ou animações saltitantes.

**Why this priority**: Define a física tátil da Monolítica. Substitui movimentos de levitação ou rebotes elásticos por preenchimento lento de contraste e inversões sólidas de alto impacto visual.

**Independent Test**: Passar o cursor sobre cartões de livros e botões e observar a transição deliberada e solene de tom de fundo/contraste (em torno de ~350ms–400ms); ao pressionar o botão (*active*), verificar uma resposta firme de inversão de contraste ou reforço de borda, sem translação vertical.

**Acceptance Scenarios**:
1. **Given** um cartão de livro sob a Superclasse Monolítica, **When** o cursor do mouse entra em sua área (*hover*), **Then** o elemento transita suavemente para um preenchimento solene de contraste ou espessamento estrutural de borda com curva ponderada (~380ms).
2. **Given** um botão de ação global sob a Monolítica, **When** o usuário clica ou mantém pressionado (*active*), **Then** o botão responde com inversão de contraste de bloco ou afundamento visual sem deslocamentos flutuantes.
3. **Given** o cursor deixando o elemento interativo, **When** ocorre o retorno ao repouso, **Then** o elemento restaura o estado padrão de forma suave e ponderada, sem oscilações bruscas.

---

### User Story 3 - Transição de Rota Solene e Ponderada (Dissolução Lapidar) (Priority: P3)

Como leitor navegando entre estante, índice de capítulos e cadernos de estudo,  
Quero que as mudanças de tela ocorram com uma transição solene e estável em opacidade ponderada,  
Para vivenciar uma continuidade contemplativa e austera, sem solavancos espaciais, saltos de escala ou translações mecânicas.

**Why this priority**: Consolida a unidade estilística da Monolítica em toda a jornada de navegação, assegurando que o ritmo do aplicativo reflita a calma e permanência de uma biblioteca monumental.

**Independent Test**: Navegar entre a estante de livros e os detalhes de um livro ou estudo e verificar que a nova tela surge através de uma transição solene de opacidade ponderada em ~380ms–400ms, sem translações em X/Y ou variações de escala tridimensional.

**Acceptance Scenarios**:
1. **Given** a navegação para uma nova rota sob a Monolítica, **When** a nova página entra, **Then** o conteúdo realiza fade-in solene com duração estendida e curva ponderada (~380ms).
2. **Given** a saída da rota anterior, **When** a transição se inicia, **Then** a página anterior dissolve-se sem desvios de posição, mantendo a estabilidade vertical absoluta do viewport.

---

### User Story 4 - Multiplicador Paramétrico, Blindagem do Leitor e Acessibilidade Universal (Priority: P4)

Como leitor com sensibilidade a movimentos, usuário de tecnologia assistiva ou leitor noturno,  
Quero poder dosar a intensidade das transições ou desativá-las sumariamente via sistema ou configurações,  
Para desfrutar de leitura tranquila, com conforto visual absoluto e foco ininterrupto no texto do estudo.

**Why this priority**: Assegura conformidade estrita com a Constituição do projeto, proporcionando acessibilidade universal e preservação inviolável do ambiente de leitura.

**Independent Test**: Testar as intensidades Sutil (0.5x), Padrão (1.0x), Alta (1.5x) e Desativada (0.0x); verificar o comportamento sob `prefers-reduced-motion: reduce` e `data-motion="off"`, garantindo que todas as transições se tornem imediatas (sem retardo de tempo) e que o corpo de leitura (`.markdown-content`) permaneça rigorosamente imóvel.

**Acceptance Scenarios**:
1. **Given** a intensidade configurada como "Sutil (0.5x)", **When** ocorrem interações de hover ou transições, **Then** os tempos de transição e contrastes são suavizados proporcionalmente.
2. **Given** a intensidade configurada como "Alta (1.5x)", **When** os blocos monolíticos recebem foco ou hover, **Then** os contornos de linha e contrastes são acentuados com máxima solidez.
3. **Given** a preferência do sistema em `prefers-reduced-motion: reduce` ou o ajuste `data-motion="off"`, **When** o usuário interage ou navega, **Then** qualquer tempo de transição é neutralizado para `0ms`, apresentando cortes secos imediatos sem atrasos perceptuais.
4. **Given** a tela de leitura de capítulos e estudos (`.markdown-content`), **When** sob a Monolítica, **Then** o texto permanece 100% estático e protegido contra qualquer animação, translação ou perturbação visual.

---

### Edge Cases

- **Dispositivos Móveis e Telas Pequenas**: Os blocos densos com cantos retos adaptam-se aos limites da tela sem provocar overflow horizontal ou espessuras de borda que comprimam o texto.
- **Navegação por Teclado e Foco Acessível**: Ao navegar via tecla `Tab`, o elemento focado (`:focus-visible`) recebe um anel de foco retangular denso e de alto contraste na cor do tema, mantendo cantos rigorosamente retos.
- **Compatibilidade com Telas E-Ink e Alto Contraste**: A ausência total de sombras difusas e o uso de contornos estruturais sólidos tornam a Monolítica a superclasse nativamente otimizada para dispositivos de tinta eletrônica (E-Ink) e temas de alto contraste.
- **Transição Rápida de Cursor (*Flick*)**: A movimentação rápida do mouse entre múltiplos blocos do acervo não acumula filas de transições, mantendo a renderização imediata e estável a 60fps.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar a Superclasse "Monolítica — Pesada & Solene", ativada tanto pelo atributo `data-superclass="monolitica"` quanto pela classe CSS `.superclass-monolitica` no elemento raiz.
- **FR-002**: A Superclasse Monolítica NÃO DEVE alterar ou sobrescrever a escolha soberana do usuário quanto à fonte de leitura (24 fontes), tema cromático (10 temas), cor de destaque, alinhamento ou tamanho do texto.
- **FR-003**: Sob a Superclasse Monolítica, todos os recipientes, cartões do acervo (`.book-card`), painéis, campos de formulário e botões DEVEM adotar cantos estritamente retos (`border-radius: 0px`).
- **FR-004**: O sistema DEVE suprimir totalmente sombras flutuantes, elevações difusas e transparências de desmaterialização (`box-shadow: none`), demarcando o relevo através de blocos densos e bordas sólidas estruturais.
- **FR-005**: Botões globais sob a Monolítica DEVEM apresentar formato retangular maciço sem cantos curvos, com inversão de alto contraste ou realce solene nos estados de hover e clique.
- **FR-006**: As microinterações de repouso do cursor e foco DEVEM adotar transições ponderadas e lentas de contraste e cor (~350ms–400ms), sem deslocamentos espaciais verticais ou atração magnética.
- **FR-007**: As transições de rota entre páginas DEVEM aplicar dissolução solene em opacidade ponderada (~380ms–400ms), sem translações em eixos físicos ou distorções de escala Z.
- **FR-008**: O texto corrido de leitura (`.markdown-content` e derivados) DEVE permanecer estritamente imóvel (`transform: none !important; animation: none !important;`).
- **FR-009**: O controle de multiplicador de intensidade (`--sc-intensity`) DEVE calibrar proporcionalmente a densidade dos contrastes e durações: Sutil (0.5x), Padrão (1.0x), Alta (1.5x) e Desativada (0.0x).
- **FR-010**: O sistema DEVE neutralizar qualquer tempo de transição sob `prefers-reduced-motion: reduce` e `data-motion="off"`, garantindo respostas imediatas sem retardos.

---

### Key Entities *(include if feature involves data)*

- **SuperclassMonoliticaTokens**:
  - `--sc-border-radius`: `0px !important` (cantos estritamente retos e facetados).
  - `--sc-border-width`: `calc(var(--border-width, 1px) + 1px)` (bordas estruturais sólidas).
  - `--sc-shadow-idle`: `none` (ausência de sombras difusas).
  - `--sc-shadow-hover`: `none` (ausência de elevações flutuantes).
  - `--sc-shadow-active`: `none` (ausência de colapsos elásticos).
  - `--sc-transition-duration`: `380ms` (tempo ponderado e solene).
  - `--sc-transition-easing`: `cubic-bezier(0.25, 1, 0.5, 1)` (curva de desaceleração estável e austera).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A seleção da Superclasse Monolítica ativa a geometria de blocos densos e cantos retos em tempo real sem recarregar a página.
- **SC-002**: 100% dos cartões de livros, painéis, modais e botões sob a Monolítica adotam cantos estritamente retos (`0px`) e eliminam sombras difusas flutuantes.
- **SC-003**: 100% das 24 fontes tipográficas e dos 10 temas de cor continuam operando de forma perfeitamente preservada e sem qualquer desvio visual ou de contraste.
- **SC-004**: Transições entre telas completam-se com dissolução solene no intervalo de 350ms a 400ms, aceleradas por GPU e com estabilidade visual absoluta.
- **SC-005**: 100% do texto corrido de estudos e capítulos permanece rigorosamente estático em repouso e durante qualquer interação.
- **SC-006**: A suíte de testes unitários do frontend mantém 100% de aprovação e o build de produção (`npm run build`) conclui com zero erros de tipo.
- **SC-007**: Usuários com `prefers-reduced-motion` ou `data-motion="off"` têm todas as transições temporizadas convertidas em respostas imediatas sem qualquer perturbação visual.

---

## Assumptions

- A arquitetura existente de superclasses (`data-superclass` e `.superclass-*`) no elemento raiz fornece o isolamento necessário para aplicar as regras da Monolítica sem colisão com as superclasses anteriores (Zero-G, Mecânica, Invisível e Dimensional).
- Nenhuma modificação no banco de dados SQLite ou em endpoints do backend é requerida, sendo uma entrega estritamente focada na camada física/estilística do frontend.
- O catálogo de aparência já possui a opção `'monolitica'` registrada em `appearance-bootstrap.js` e em `appearance.d.ts`, bastando o fornecimento da folha de estilos correspondente e integração na folha global.
