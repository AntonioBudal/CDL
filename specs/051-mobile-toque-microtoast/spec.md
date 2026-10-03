# Feature Specification: Responsividade Mobile, Toque Nativo e Micro-Toast de Ferramentas

**Feature Branch**: `051-mobile-toque-microtoast`  
**Created**: 2026-10-03  
**Status**: Ready for Planning  
**Input**: User description: "F 0.7.2 — Melhorar responsividade no celular, seleção de texto por dois cliques/toques, ferramentas apenas com ícones no celular e div flutuante temporária (micro-toast) informando a ferramenta selecionada."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Seleção Rápida de Palavra por Duplo Toque / Duplo Clique (Priority: P1)

Como um leitor utilizando o Leitorum em smartphone ou tablet, quero dar dois toques rápidos (duplo toque) em qualquer palavra do texto do estudo e tê-la selecionada imediatamente sem ter que arrastar alças manuais imprecisas, para que eu possa marcar trechos ou criar perguntas com rapidez e sem esforço motor.

**Why this priority**: No celular, arrastar alças nativas de seleção de texto frequentemente causa rolagem acidental de tela ou cancela a seleção, gerando atrito e frustração durante a leitura ativa.

**Independent Test**: Pode ser validado em viewport móvel tocando duas vezes em qualquer palavra de um parágrafo do estudo, verificando que a palavra é selecionada e a barra flutuante de ações surge imediatamente.

**Acceptance Scenarios**:
1. **Given** o usuário visualizando uma seção do estudo em dispositivo com tela de toque, **When** executa um duplo toque (ou duplo clique) sobre uma palavra, **Then** a palavra é delimitada como seleção ativa e a barra contextual de ações é exibida.
2. **Given** o usuário com uma palavra ou trecho selecionado, **When** arrasta ou ajusta a seleção sem soltar, **Then** a barra de ações atualiza seus limites sem quebrar o layout da página.
3. **Given** uma seleção ativa, **When** o usuário toca em uma área neutra de leitura fora de qualquer ferramenta, **Then** a seleção é desfeita e a barra fecha de forma limpa.

---

### User Story 2 - Barra de Ações Mobile Apenas com Ícones Puros de 44x44px (Priority: P1)

Como um leitor em tela pequena, quero que a barra de ferramentas flutuante na base da tela exiba apenas ícones autoexplicativos confortáveis (com tamanho de toque de no mínimo 44x44px) em vez de rótulos textuais compridos ("Destacar", "Anotar", "Ocultar"), para que a barra não fique apertada, ilegível ou desproporcional.

**Why this priority**: Textos compridos em botões móveis comprimem os elementos horizontalmente ou empilham ícones e legendas, consumindo altura vertical e tornando os toques imprecisos.

**Independent Test**: Pode ser validado em viewport móvel (< 768px), conferindo que os botões da barra exibem apenas os ícones canônicos com espaçamento harmônico e alvos de toque de no mínimo 44x44px, mantendo rótulos acessíveis via atributos `aria-label`.

**Acceptance Scenarios**:
1. **Given** um trecho de texto selecionado no celular, **When** a barra de ações é exibida na base, **Then** todos os botões de ferramentas (Marca-texto, Cores, Anotação, Citação, Oclusão, Pergunta e Fechar) exibem exclusivamente ícones visuais nítidos.
2. **Given** os botões com ícones no celular, **When** inspecionados, **Then** cada botão possui área de toque mínima de 44x44 pixels (WCAG 2.1 Critério 2.5.5) e atributos `aria-label` descritivos para leitores de tela.
3. **Given** a barra em telas desktop (≥ 768px), **When** renderizada, **Then** o layout desktop com texto + ícone permanece preservado normalmente.

---

### User Story 3 - Micro-Toast Flutuante de Confirmação da Ferramenta Selecionada (Priority: P1)

Como um leitor em dispositivo móvel, ao tocar em uma ferramenta na barra de ícones, quero ver uma pequena notificação flutuante elegante (micro-toast) aparecer no topo da aba de leitura por alguns segundos indicando a ferramenta acionada, para ter certeza instantânea de qual ação foi executada sem precisar de textos poluindo a barra inferior.

**Why this priority**: Substitui com elegância os textos fixos da barra, fornecendo feedback tátil e visual confirmatório imediato ("Trecho destacado", "Criar anotação", "Ocultado para revisão").

**Independent Test**: Pode ser testado selecionando um texto no mobile e tocando em qualquer ferramenta (ex.: Marca-texto, Oclusão ou Citação), constatando que uma div flutuante sutil surge no topo da aba, permanece visível por aproximadamente 1.5 a 2 segundos e desaparece com fade-out suave, sem bloquear interações.

**Acceptance Scenarios**:
1. **Given** um texto selecionado no celular, **When** o usuário toca no botão de Marca-texto, **Then** o destaque é aplicado e um micro-toast com texto ("Destaque aplicado") e ícone correspondente surge suavemente no topo da área do estudo.
2. **Given** o micro-toast visível, **When** transcorrem aproximadamente 1.5 a 2 segundos (ou quando o usuário realiza uma nova ação), **Then** a div desaparece com transição suave sem deixar resíduos no DOM.
3. **Given** o usuário tocando em uma ação como "Citação", **When** o texto é copiado para a área de transferência, **Then** o micro-toast exibe "Citação formatada copiada".

---

### User Story 4 - Submenus e Prompts Móveis de Anotação e Pergunta sem Quebra (Priority: P2)

Como um leitor móvel adicionando uma anotação ou formulando uma pergunta, quero que os painéis secundários (paleta de cores, campo de anotação, campo de pergunta) ocupem a largura do leitor com ergonomia, sem sobrepor o teclado virtual ou vazar as margens.

**Why this priority**: No celular, ao abrir a caixa de texto de uma pergunta ou anotação, o teclado virtual se expande; o painel precisa manter botões de confirmação e cancelamento ao alcance do polegar.

**Independent Test**: Pode ser validado tocando em "Anotar" ou "Pergunta" no celular, verificando que o formulário de entrada é exibido com campos confortáveis, botões "Salvar" e "Cancelar" de 44px e encerramento limpo.

**Acceptance Scenarios**:
1. **Given** um texto selecionado no celular, **When** o usuário clica em "Anotar", **Then** a barra se expande suavemente exibindo o campo de anotação e os botões "Salvar" e "Voltar".
2. **Given** o usuário preenchendo a anotação, **When** confirma, **Then** a anotação é salva, o micro-toast confirma ("Anotação salva") e a barra fecha.

---

### Edge Cases

- **Toque Acidental Durante Rolagem (Scroll)**: Se o usuário estiver deslizando a tela para ler, o início do toque não deve selecionar palavras indesejadas nem interromper a rolagem fluida.
- **Micro-Toasts Sucessivos**: Se o usuário aplicar duas ações em rápida sucessão, o micro-toast anterior deve ser substituído imediatamente pelo novo, reiniciando o temporizador de exibição sem sobreposição de mensagens.
- **Teclado Virtual em Telas Muito Pequenas (< 360px)**: Prompts de anotação e pergunta devem ter altura contida para não empurrar os botões de ação para fora da tela quando o teclado virtual estiver ativo.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE aprimorar o composable de seleção de texto (`useTextSelection.ts`) para suportar seleção de palavras por duplo toque/duplo clique em dispositivos móveis e desktops.
- **FR-002**: A seleção de texto em dispositivos móveis NÃO DEVE ser cancelada por pequenos toques de rolagem acidental (`touchmove` além do limite de tolerância de clique).
- **FR-003**: No modo mobile (`isMobile === true` / viewport < 768px), os botões da barra flutuante (`FloatingActionsToolbar.vue`) DEVEM ocultar completamente os textos de legenda, exibindo exclusivamente os ícones visuais das ferramentas.
- **FR-004**: Todos os botões de ferramentas na barra mobile DEVEM possuir dimensões mínimas de 44x44 pixels para garantir alvos de toque em conformidade com WCAG 2.1 AA.
- **FR-005**: O micro-toast flutuante DEVE ser posicionado no topo da área/aba ativa de leitura de estudos (`top: 1rem; left: 50%; transform: translateX(-50%)`), garantindo visibilidade clara acima do texto e não sendo obstruído pela mão do usuário na base da tela.
- **FR-006**: O micro-toast DEVE permanecer visível por exatamente 1.8 segundos (1800ms) antes de realizar fade-out suave de 250ms, fechando antecipadamente sem conflito se uma nova ferramenta for selecionada.
- **FR-007**: Ao acionar uma ferramenta no celular (Marca-texto, Anotação, Citação, Oclusão, Pergunta), o sistema DEVE disparar o micro-toast indicando a ferramenta executada com mensagem concisa.
- **FR-008**: O micro-toast DEVE possuir `pointer-events: none` para nunca bloquear toques ou gestos de leitura subsequentes do usuário.
- **FR-009**: O micro-toast DEVE suportar animação suave de entrada e saída (`transition`) com aceleração natural e respeitar a preferência do sistema por movimento reduzido (`prefers-reduced-motion`).
- **FR-010**: A paleta de seleção de cores de marca-texto no mobile DEVE apresentar círculos de cor aumentados (mínimo de 36x36px) com espaçamento de toque confortável.
- **FR-011**: No Desktop (viewport ≥ 768px), a barra flutuante DEVE manter a exibição dos textos das ferramentas ao lado dos ícones, garantindo que a experiência em telas grandes não sofra regressão.
- **FR-012**: O leitor de tela DEVE anunciar a ferramenta acionada via atributo acessível `role="status"` ou `aria-live="polite"` no micro-toast.

---

### Key Entities

- **FloatingToastState**: Estado reativo da notificação flutuante contendo `visible: boolean`, `message: string`, `icon?: string`, `duration: number`, `timerId: number | null`.
- **TextTouchSelectionState**: Estado de captura de toques móveis registrando timestamp do último toque, coordenadas de início e término para diferenciar toque simples de rolagem e duplo toque.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em dispositivos móveis, a largura total da barra de ações flutuante é reduzida em pelo menos 30% devido à remoção de textos desnecessários, eliminando transbordamento horizontal.
- **SC-002**: 100% dos botões de ação na barra mobile atendem à área de toque mínima de 44x44px.
- **SC-003**: O micro-toast surge em menos de 50ms após o toque na ferramenta e desaparece suavemente sem travar a thread de animação (60 FPS).
- **SC-004**: Usuários em telas de toque conseguem selecionar palavras individuais com exatamente 2 toques rápidos sem necessidade de arrastar alças manuais.
- **SC-005**: 100% dos testes existentes e novos testes de seleção e micro-toast passam sem nenhuma regressão.

---

## Assumptions

- O micro-toast é um elemento leve estilizado com variáveis CSS existentes (`--color-surface`, `--color-text-primary`, `--radius-full`, `--shadow-md`).
- A seleção nativa do navegador (`window.getSelection()`) é a base do mecanismo, com aprimoramento na detecção e conversão em coordenadas.
- Não há impacto no backend, banco de dados ou APIs.
