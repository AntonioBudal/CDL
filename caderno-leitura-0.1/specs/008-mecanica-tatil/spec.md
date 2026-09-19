# Feature Specification: 008 — Mecânica: Superclasse Tátil & Responsiva

**Feature Branch**: `008-mecanica-tatil`  
**Created**: 2026-09-19  
**Status**: Ready  
**Input**: User description: "Implementação da Superclasse Mecânica (Tátil & Responsiva). O objetivo é criar uma física tátil, pesada e de resposta imediata, simulando equipamentos físicos e teclados mecânicos. Regras de ouro: Fronteira Estática (não tocar em tipografia, cores ou densidade), Escopo Sistêmico (aplicado a painéis, botões, modais, inputs e ajustes), Multiplicador de Intensidade (--sc-intensity). Variáveis: cantos secos (2px), sombras sólidas duras sem desfoque (3px idle, 4px hover, 0 active), transição rápida linear (100ms). Efeito push-down nos botões e cards (afunda 3px e zera a sombra). Inputs escavados com sombra interna e foco com atrito visual. Toggles com estalo de 50-80ms. Painéis parafusados e transições de rota secas (corte de 100ms)."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ativação da Superclasse Mecânica e Feedback Tátil Push-Down em Botões e Cards (Priority: P1) 🎯 MVP

Como usuário do Caderno de Leitura,  
Quero selecionar a Superclasse "Mecânica" nas configurações de aparência,  
Para que botões, cartões da estante e controles interativos transmitam uma resposta física de teclado mecânico industrial, com cantos quase retos, sombras sólidas duras e um afundamento (*push-down*) nítido ao clicar, sem alterar minhas cores ou fontes favoritas.

**Why this priority**: Estabelece o arquétipo visual e cinemático da Mecânica. Entrega valor e diferenciação perceptível imediata em toda a aplicação como MVP.

**Independent Test**: Ativar "Mecânica" nas configurações de aparência, navegar para a estante ou clicar nos botões da página e constatar que:
1. Os cartões e botões adotam cantos quase retos (`border-radius: 2px`) e sombras sólidas sem blur (`0 3px 0 rgba(...)`).
2. Não há qualquer oscilação de repouso (*idle breathing*) ou magnetismo de cursor; o repouso é 100% rígido e firme.
3. No hover, o elemento sobe 1px de forma quase instantânea (100ms linear) e a sombra sólida aumenta para 4px.
4. No clique (`:active`), o elemento afunda 3px (`push-down`) e a sombra se anula instantaneamente (`0 0 0 transparent`), simulando a depressão física de um switch de tecla mecânica.

**Acceptance Scenarios**:
1. **Given** o usuário no painel de Ajustes, **When** seleciona a opção "Mecânica — Tátil & Precisa", **Then** a interface adota imediatamente a física mecânica e cantos secos em tempo real sem recarregar a página.
2. **Given** um botão ou cartão de livro sob a Superclasse Mecânica em repouso, **When** o usuário observa a tela, **Then** nenhum movimento automático ou oscilação é renderizado, permanecendo o elemento em repouso rígido.
3. **Given** um botão ou cartão, **When** o cursor do mouse passa sobre ele (*hover*), **Then** o elemento desloca-se suavemente para cima (`translateY(calc(-1px * var(--sc-intensity)))`) e a sombra sólida expande para 4px em transição de 100ms.
4. **Given** um botão ou cartão, **When** o usuário clica e mantém pressionado (*active*), **Then** o elemento desce imediatamente para baixo (`translateY(calc(3px * var(--sc-intensity)))`) e a sombra sólida zera completamente, simulando o fim de curso de uma tecla.

---

### User Story 2 - Escopo Sistêmico em Formulários, Inputs Escavados e Caixas de Ajustes (Priority: P2)

Como usuário preenchendo dados ou personalizando o aplicativo,  
Quero que os campos de formulário e painéis de agrupamento pareçam peças de hardware tátil de alta precisão,  
Para que toda a experiência de digitação e navegação transmita firmeza e atrito mecânico.

**Why this priority**: Garante a consistência sistêmica da Superclasse em todas as superfícies da aplicação, evitando que a sensação tátil fique restrita apenas a botões.

**Independent Test**: Abrir a tela de Ajustes e telas com formulários (como cadastro de livro) sob a Superclasse Mecânica e verificar que os campos de texto possuem cantos de 2px, sombras internas escavadas, e que os painéis de ajustes parecem blocos de chassi parafusados.

**Acceptance Scenarios**:
1. **Given** campos de texto (`input[type="text"]`, `input[type="number"]`, `textarea`), **When** em repouso sob Mecânica, **Then** apresentam borda sólida de 1px a 2px, cantos de 2px e leve sombra interna (*inset*), parecendo cravados/escavados na superfície do painel.
2. **Given** um campo de texto, **When** recebe o foco do usuário (*focus*), **Then** a borda engrossa ou reforça seu contraste instantaneamente em vez de flutuar ou emitir brilho difuso, gerando alto atrito visual.
3. **Given** as caixas de agrupamento da tela de Ajustes (`.appearance-group`), **When** renderizadas sob Mecânica, **Then** apresentam cantos rígidos (`2px`), borda bem demarcada e sombra sólida dura, parecendo blocos mecânicos fixados à carcaça.
4. **Given** seletores suspensos (`<select>`), **When** exibidos em Mecânica, **Then** acompanham os cantos rígidos e sombra sólida de hardware.

---

### User Story 3 - Controles Booleanos com Estalo e Transições de Rota em Corte Seco (Priority: P3)

Como usuário interagindo com alternâncias e navegando entre rotas,  
Quero que interruptores cliquem como relés/switches e as trocas de página ocorram em cortes rápidos e diretos,  
Para que a navegação seja ágil, precisa e sem delays cinemáticos artificiais.

**Why this priority**: Remove a inércia lenta e fluidos flutuantes, reforçando a identidade de máquina funcional e responsiva.

**Independent Test**: Alternar um switch/checkbox e navegar entre telas (Acervo $\leftrightarrow$ Ajustes $\leftrightarrow$ Detalhes) e verificar a resposta do switch em ~50-80ms e transição de página em corte rápido de ~100ms.

**Acceptance Scenarios**:
1. **Given** um switch de alternância sob Mecânica, **When** ativado ou desativado, **Then** o pino não desliza de forma vagarosa; ele se desloca em tempo ultrarrápido (50ms a 80ms), simulando um estalo mecânico.
2. **Given** uma caixa de seleção (*checkbox*), **When** clicada, **Then** sofre um micro-afundamento tátil (*push-down*) antes da marcação se firmar.
3. **Given** a navegação de rotas pelo Vue Router (`<Transition name="page">`), **When** o usuário troca de página sob Mecânica, **Then** a transição ocorre em corte rápido e limpo de 100ms sem deslocamentos verticais flutuantes.

---

### User Story 4 - Calibração de Intensidade Paramétrica e Neutralização Universal de Movimento (Priority: P4)

Como usuário com preferências específicas de curso ou sensibilidade a movimento,  
Quero que o afundamento dos botões seja dosado pelo controle de intensidade e que a redução de movimento seja respeitada,  
Para ter total controle sobre a física tátil do sistema.

**Why this priority**: Garante acessibilidade universal e integração perfeita com o controle de intensidade introduzido na arquitetura de Superclasses.

**Independent Test**: Comutar a intensidade entre Sutil, Padrão, Alta e Desativada e verificar a escala proporcional do afundamento dos botões, além de testar sob *prefers-reduced-motion*.

**Acceptance Scenarios**:
1. **Given** a intensidade configurada como "Sutil (0.5x)", **When** um botão é pressionado, **Then** o deslocamento de afundamento é de 1.5px (`3px * 0.5`) e a sombra de repouso é de 1.5px.
2. **Given** a intensidade configurada como "Alta (1.5x)", **When** um botão é pressionado, **Then** o deslocamento de afundamento é de 4.5px (`3px * 1.5`) e a sombra de repouso é de 4.5px.
3. **Given** a intensidade configurada como "Desativada (0.0x)" ou sistema com *prefers-reduced-motion*, **When** qualquer controle for utilizado, **Then** todo deslocamento de afundamento é suprimido (`0px`), preservando apenas a geometria estática dos cantos rígidos.
4. **Given** a leitura de capítulos e textos de estudo, **When** exibidos sob Mecânica, **Then** todo o texto contínuo permanece 100% imóvel.

---

### Edge Cases

- **Dispositivos Touch**: Em toques em telas móveis, o estado `:active` ativa instantaneamente o *push-down* sem que o estado `:hover` gere anomalias de cursor.
- **Botões Desabilitados (`:disabled`)**: Botões inativos não reagem ao hover nem ao active, mantendo sua posição e sombra neutras.
- **Campos de Texto com Foco Rápido via Tabulação**: Ao navegar pelo teclado (`Tab`), o anel ou borda de foco engrossa instantaneamente com alta visibilidade para navegação por teclado.
- **Alternância entre Zero-G e Mecânica em Tempo Real**: A transição entre os dois arquétipos no painel de Ajustes deve ser instantânea, com a remoção imediata das sombras difusas e flutuações e adoção das sombras duras e cantos secos.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer suporte à Superclasse "Mecânica (Tátil & Precisa)", ativada tanto pelo atributo `data-superclass="mecanica"` quanto pela classe CSS `.superclass-mecanica`.
- **FR-002**: A Superclasse Mecânica NÃO DEVE alterar ou interferir nas escolhas do usuário de tipografia (24 fontes), cores de temas, cores de destaque, densidade de espaçamento ou largura de leitura.
- **FR-003**: A geometria sob a Superclasse Mecânica DEVE adotar cantos quase retos através da variável `--sc-border-radius: 2px;` em botões, cartões, inputs, selects e painéis.
- **FR-004**: O sistema DEVE adotar sombras sólidas duras sem desfoque para a Superclasse Mecânica, utilizando a variável `--sc-shadow-idle: 0 calc(3px * var(--sc-intensity)) 0 var(--color-shadow, rgba(0,0,0,0.4));`.
- **FR-005**: Ao passar o cursor sobre botões e cartões (*hover*), o sistema DEVE aplicar uma transição ultrarrápida linear de 100ms para a sombra `--sc-shadow-hover: 0 calc(4px * var(--sc-intensity)) 0 ...` com deslocamento de `translateY(calc(-1px * var(--sc-intensity)))`.
- **FR-006**: Ao acionar o estado de clique (*active*), botões e cartões DEVEM sofrer afundamento físico de tecla (*push-down*) com `translateY(calc(3px * var(--sc-intensity)))` e anulação total da sombra (`0 0 0 transparent`).
- **FR-007**: A Superclasse Mecânica NÃO DEVE aplicar qualquer animação de respiração de repouso (*idle breathing*) ou atração magnética de cursor, mantendo todos os elementos em repouso estático.
- **FR-008**: Os campos de entrada de texto e textareas DEVEM apresentar bordas sólidas, cantos secos (`--sc-border-radius`) e sombra interna (*inset*) sutil em repouso.
- **FR-009**: No estado de foco (*focus*), os campos de texto NÃO DEVEM flutuar nem emitir brilho difuso suave, devendo engrossar ou reforçar a borda de forma imediata com alto atrito visual.
- **FR-010**: Os switches de ativação e toggles DEVEM transicionar o pino de forma rápida (50ms a 80ms), simulando um estalo mecânico.
- **FR-011**: As caixas de agrupamento de opções da tela de Ajustes (`.appearance-group`) e painéis DEVEM adotar cantos secos (`2px`) e bordas sólidas ou sombras duras, conferindo a sensação de placas parafusadas.
- **FR-012**: As transições de rota do Vue Router sob a Superclasse Mecânica DEVEM operar como cortes rápidos de 100ms, sem qualquer deslocamento vertical flutuante.
- **FR-013**: Todo o texto corrido de capítulos e anotações de estudo DEVE permanecer 100% estático e imóvel.
- **FR-014**: O sistema DEVE neutralizar imediatamente qualquer deslocamento de *push-down* ou transição quando o controle de movimento estiver desativado ou sob `prefers-reduced-motion`.

---

### Key Entities *(include if feature involves data)*

- **SuperclassMecanicaTokens**:
  - `--sc-border-radius`: `2px`
  - `--sc-shadow-idle`: `0 calc(3px * var(--sc-intensity)) 0 rgba(0,0,0,0.4)`
  - `--sc-shadow-hover`: `0 calc(4px * var(--sc-intensity)) 0 rgba(0,0,0,0.5)`
  - `--sc-shadow-active`: `0 0 0 transparent`
  - `--sc-transition-duration`: `100ms`
  - `--sc-transition-easing`: `linear`
- **SuperclassIntensityMultiplier**:
  - `--sc-intensity`: `0.5` (Sutil), `1.0` (Padrão), `1.5` (Alta), `0.0` (Desativada).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A seleção da Superclasse Mecânica atualiza visualmente e cineticamente a tela em tempo real sem necessidade de recarregar a página web.
- **SC-002**: O efeito de *push-down* em botões e cartões no estado `:active` afunda exatamente `calc(3px * var(--sc-intensity))` e anula a sombra no mesmo frame.
- **SC-003**: 100% dos botões e cartões possuem cantos com raio estrito de 2px sob a Superclasse Mecânica.
- **SC-004**: A duração das transições cinéticas é estritamente inferior ou igual a 100ms, eliminando qualquer curva de inércia elástica lenta.
- **SC-005**: 100% dos textos de leitura de capítulos e estudos permanecem rigorosamente imóveis em repouso e durante qualquer interação.
- **SC-006**: Sob a opção de intensidade "Sutil", o afundamento máximo de clique atinge 1.5px; sob "Alta", atinge 4.5px; sob "Desativada", atinge 0px.
- **SC-007**: 100% das 24 fontes tipográficas e dos 10 temas de cor continuam operando de forma totalmente inalterada.

---

## Assumptions

- A Superclasse Mecânica reaproveita o catálogo e o controle de intensidade já estabelecidos na arquitetura de Superclasses em `cadernoAppearance`.
- As sombras duras utilizam cores com transparência compatíveis tanto com temas claros (como Porcelana) quanto com temas escuros (como Breu e Fiorde).
- O efeito de corte rápido de rota em 100ms melhora a percepção de performance e agilidade na navegação do aplicativo.
