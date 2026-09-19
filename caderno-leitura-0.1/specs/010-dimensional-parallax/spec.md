# Feature Specification: 010 — Dimensional: Superclasse Cinemática & Profunda (3D Parallax Espacial)

**Feature Branch**: `010-dimensional-parallax`  
**Created**: 2026-09-19  
**Status**: Ready  
**Input**: User description: "Implementação da Superclasse 'Dimensional' (Cinemática & Profunda — 3D Parallax, relevo em camadas e tilt microcontrolado)"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ativação da Superclasse Dimensional com Tilt 3D Microcontrolado e Sombras em Perspectiva (Priority: P1) 🎯 MVP

Como leitor explorando o acervo de livros e cadernos de estudo,  
Quero selecionar a Superclasse "Dimensional" nas opções de aparência do aplicativo,  
Para que os cartões de livros e painéis ganhem profundidade física, perspectiva tridimensional e inclinação sutil (*tilt 3D*) em resposta ao movimento do mouse, transmitindo sensação de relevo palpável e materialidade elegante.

**Why this priority**: É o núcleo fundacional da Superclasse Dimensional. Transforma a experiência sensorial do acervo de uma superfície plana para um ambiente com profundidade de galeria física, entregando valor imediato e testável de forma independente como MVP.

**Independent Test**: Ativar "Dimensional" nas configurações de aparência, navegar para a estante de livros e constatar que:
1. Ao passar o mouse sobre um cartão de livro (`.book-card`), o cartão inclina-se suavemente nos eixos X e Y em direção ao cursor com limites estritos (máximo de 1.5° em X e 2.0° em Y).
2. A sombra do cartão projeta-se dinamicamente na direção oposta à inclinação, acentuando a percepção de iluminação espacial.
3. Ao retirar o cursor do cartão, ele retorna com desaceleração inercial suave para o plano neutro (`0deg`), sem rebotes exagerados.
4. As cores do tema, as fontes e os espaçamentos permanecem rigorosamente inalterados.

**Acceptance Scenarios**:
1. **Given** o usuário na tela de Ajustes, **When** seleciona a Superclasse "Dimensional — Cinemática & Profunda", **Then** a classe `.superclass-dimensional` e o atributo `data-superclass="dimensional"` são ativados imediatamente no elemento raiz sem recarregar a página.
2. **Given** um cartão de livro sob a Superclasse Dimensional, **When** o cursor do mouse se move sobre os quadrantes do cartão, **Then** o elemento calcula rotações angulares proporcionais limitadas a `rotateX(±1.5deg)` e `rotateY(±2.0deg)` com perspectiva de 1000px.
3. **Given** o cartão inclinado sob ação do cursor, **When** o mouse deixa a área do cartão (*pointer leave*), **Then** o cartão restaura a orientação neutra de repouso em transição cinemática suave (`~350ms`).
4. **Given** um botão de ação global sob a Dimensional, **When** o cursor passa sobre ele, **Then** ele apresenta leve elevação de profundidade Z com sombra projetada direcional.

---

### User Story 2 - Relevo Espacial Multicamada e Parallax Interno nas Capas e Cartões (Priority: P2)

Como leitor visualizando livros com ilustrações de capa e anotações,  
Quero que os elementos internos do cartão (miniatura da capa, título, autor e marcadores) se desloquem em profundidades ópticas diferenciadas durante o movimento,  
Para perceber uma sensação refinada de camadas e relevo artesanal sem qualquer poluição visual.

**Why this priority**: Eleva o refinamento visual da Dimensional, diferenciando uma simples rotação 3D estática de um ecossistema com profundidade física real em camadas visuais coordenadas.

**Independent Test**: Interagir com cartões de livros que contenham capa, títulos e metadados na visualização em grade ou lista e verificar que o plano da capa desloca-se em 1px, o título em 2px e os marcadores de estudo em 3px sob o efeito do cursor, gerando sensação de paralaxe volumétrica.

**Acceptance Scenarios**:
1. **Given** um cartão de livro com miniatura de capa sob a Dimensional, **When** o cartão é inclinado pelo cursor, **Then** a imagem da capa e os blocos tipográficos internos movem-se com defasagem relativa de profundidade (1px para a capa, 2px para títulos e 3px para badges).
2. **Given** a visualização em lista do acervo, **When** o usuário passa o cursor sobre os itens, **Then** o marcador lateral e os metadados do autor respondem com relevo tátil coeso.

---

### User Story 3 - Transição de Rota Cinemática com Profundidade Espacial (Priority: P3)

Como usuário navegando entre o acervo, capítulos e a tela de leitura,  
Quero que a transição entre telas dê a sensação de aproximação suave e contínua no plano do observador,  
Para sentir uma navegação fluida e sofisticada sem cortes abruptos ou deslocamentos secos.

**Why this priority**: Fecha a experiência holística da Superclasse Dimensional ao assegurar que as mudanças de tela participem da mesma física espacial de câmera e profundidade que governa os componentes.

**Independent Test**: Navegar entre a estante de livros e os detalhes de um livro ou capítulo e observar que a nova tela emerge do plano de profundidade com leve aproximação escalar (`scale(0.985) → scale(1.0)`) e fade-in suave de opacidade em ~300ms.

**Acceptance Scenarios**:
1. **Given** a navegação para uma nova rota sob a Superclasse Dimensional, **When** o novo componente é montado, **Then** a transição de entrada aproxima o conteúdo com curva cinemática `cubic-bezier(0.16, 1, 0.3, 1)` em ~300ms.
2. **Given** a transição de saída de uma rota, **When** o usuário clica em voltar ou navegar, **Then** a página atual recua suavemente em profundidade e opacidade antes da entrada do novo destino, sem solavancos de scroll.

---

### User Story 4 - Multiplicador Paramétrico de Profundidade, Blindagem do Leitor e Acessibilidade (Priority: P4)

Como usuário com necessidades específicas de acessibilidade ou sensibilidade a movimento,  
Quero poder calibrar a intensidade dos efeitos 3D ou desativá-los completamente via sistema ou configurações,  
Para desfrutar do aplicativo com conforto visual e estabilidade total na leitura.

**Why this priority**: Garante total conformidade com a Constituição do projeto, acessibilidade universal e preservação absoluta da concentração durante o estudo.

**Independent Test**: Testar os níveis de intensidade Sutil (0.5x), Padrão (1.0x), Alta (1.5x) e Desativada (0.0x); testar o sistema com `prefers-reduced-motion: reduce` e `data-motion="off"`, garantindo que todo tilt 3D e paralaxe sejam imediatamente suprimidos e que `.markdown-content` permaneça 100% estático.

**Acceptance Scenarios**:
1. **Given** a intensidade em "Sutil (0.5x)", **When** o cursor inclina um cartão, **Then** a rotação máxima é reduzida proporcionalmente para `0.75°` em X e `1.0°` em Y.
2. **Given** a intensidade em "Alta (1.5x)", **When** o cursor inclina um cartão, **Then** a rotação máxima atinge `2.25°` em X e `3.0°` em Y, mantendo a geometria estável.
3. **Given** a preferência do sistema em `prefers-reduced-motion: reduce` ou o ajuste `data-motion="off"`, **When** o usuário navega e interage, **Then** qualquer rotação 3D, escala de transição ou paralaxe é anulada (`0deg`, sem transições espaciais), preservando o layout em repouso absoluto.
4. **Given** a leitura de capítulos e estudos (`.markdown-content`), **When** sob a Dimensional, **Then** o texto permanece rigorosamente imóvel e protegido contra qualquer oscilação ou inclinação.

---

### Edge Cases

- **Dispositivos Móveis e Telas Touch**: Em telas sensíveis ao toque (onde não há cursor flutuante contínuo), os eventos de *pointermove* são filtrados para evitar inclinações falsas durante a rolagem com o dedo; os cartões mantêm sua elevação estável de repouso.
- **Rápida Saída do Cursor (*Flick*)**: Se o usuário mover o cursor bruscamente para fora do cartão, o sistema cancela a interpolação ativa e executa um retorno cinemático amortecido sem solavancos visuais.
- **Navegação por Teclado e Foco Acessível**: Ao navegar via tecla `Tab`, o elemento em foco (`:focus-visible`) recebe uma leve elevação frontal estática com anel de foco nítido na cor de destaque, sem inclinações assimétricas que dificultem a leitura do rótulo.
- **Telas Pequenas / Responsividade**: Em larguras de tela inferiores a 720px, a perspectiva e a profundidade de sombra são atenuadas para garantir performance impecável de 60fps em dispositivos portáteis.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar a Superclasse "Dimensional — Cinemática & Profunda", ativada tanto pelo atributo `data-superclass="dimensional"` quanto pela classe CSS `.superclass-dimensional`.
- **FR-002**: A Superclasse Dimensional NÃO DEVE alterar ou sobrescrever a escolha soberana do usuário quanto à fonte de leitura (24 fontes), tema cromático (10 temas), cor de destaque, alinhamento ou tamanho do texto.
- **FR-003**: Sob a Superclasse Dimensional, os cartões do acervo (`.book-card`) e itens de lista DEVEM suportar perspectiva tridimensional de 1000px e inclinação dinâmica nos eixos X e Y (*tilt 3D*) proporcional à posição do cursor, respeitando os limites estritos de rotação (`rotateX: ±1.5°`, `rotateY: ±2.0°`).
- **FR-004**: O sistema DEVE projetar sombras multicamada em perspectiva dinâmica que desloquem o vetor de iluminação na direção oposta ao ângulo de inclinação do elemento.
- **FR-005**: Capas de livros e elementos internos de títulos e marcadores DEVEM exibir deslocamento em camadas de paralaxe diferenciadas (1px a 3px) sob interação de cursor.
- **FR-006**: Botões e controles globais sob a Dimensional DEVEM apresentar elevação frontal refinada no hover e resposta elástica controlada no clique (`:active`).
- **FR-007**: As transições de rota entre páginas DEVEM aplicar aproximação cinemática em profundidade (`scale(0.985) → scale(1.0)` e `translateY(4px → 0)`) com curva suave em ~300ms.
- **FR-008**: O texto corrido de leitura (`.markdown-content` e derivados) DEVE permanecer estritamente imóvel (`transform: none !important; animation: none !important;`).
- **FR-009**: O controle de multiplicador de intensidade (`--sc-intensity`) DEVE dosar proporcionalmente a amplitude do tilt 3D e do paralaxe: Sutil (0.5x), Padrão (1.0x), Alta (1.5x) e Desativada (0.0x).
- **FR-010**: O sistema DEVE neutralizar sumariamente qualquer rotação 3D, aproximação espacial ou efeito de paralaxe sob `prefers-reduced-motion: reduce` e `data-motion="off"`.

---

### Key Entities *(include if feature involves data)*

- **SuperclassDimensionalTokens**:
  - `--sc-border-radius`: `calc(var(--radius-card, 8px))` (cantos refinados harmonizados com o tema).
  - `--sc-perspective`: `1000px`.
  - `--sc-tilt-max-x`: `calc(1.5deg * var(--sc-intensity))`.
  - `--sc-tilt-max-y`: `calc(2.0deg * var(--sc-intensity))`.
  - `--sc-shadow-idle`: `0 6px 16px -2px rgba(0, 0, 0, 0.08), 0 16px 36px -6px rgba(0, 0, 0, 0.06)`.
  - `--sc-shadow-hover`: `0 14px 32px -4px rgba(0, 0, 0, 0.14), 0 28px 64px -8px rgba(0, 0, 0, 0.10)`.
  - `--sc-transition-duration`: `320ms`.
  - `--sc-transition-easing`: `cubic-bezier(0.16, 1, 0.3, 1)` (desaceleração inercial cinemática).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A seleção da Superclasse Dimensional ativa a perspectiva 3D e sombras cinemáticas em tempo real sem necessidade de recarregar a página.
- **SC-002**: 100% dos cartões de livros no acervo sob a Dimensional inclinam-se de forma delimitada e estável, nunca ultrapassando os limites rígidos de ±1.5° (eixo X) e ±2.0° (eixo Y) na intensidade padrão (1.0x).
- **SC-003**: 100% das 24 fontes tipográficas e dos 10 temas de cor continuam operando de forma perfeitamente preservada e sem qualquer desvio estético.
- **SC-004**: Transições entre telas completam-se no intervalo de 300ms a 350ms, aceleradas por GPU, mantendo taxa estável de 60fps sem engasgos na viewport.
- **SC-005**: 100% do texto corrido de estudos e capítulos permanece rigorosamente estático em repouso e durante interações.
- **SC-006**: A suíte de testes unitários do frontend mantém 100% de aprovação e o build de produção (`npm run build`) conclui com zero erros de tipo.
- **SC-007**: Usuários com `prefers-reduced-motion` ou `data-motion="off"` têm 100% dos efeitos tridimensionais, tilts e aproximações de escala suprimidos de forma imediata.

---

## Assumptions

- A interação 3D nos cartões aproveita ou estende os princípios inerciais de captura de coordenadas do cursor presentes na arquitetura do frontend (`pointermove` e `pointerleave`), com throttling automático acelerado por hardware.
- Eventos de toque (*touch*) em smartphones e tablets são desconsiderados para cálculo de tilt dinâmico, evitando instabilidade de leitura durante a rolagem vertical da tela.
- Zero impacto no banco de dados SQLite ou backend: toda a funcionalidade é 100% frontend.
