# Feature Specification: Polimento de UI e Correções Visuais

**Feature Branch**: `027-polimento-ui-visual`  
**Created**: 2026-09-20  
**Status**: Ready for Implementation  
**Input**: User description: "Feature 0.05 - Polimento de UI e Correções Visuais (NÃO FAZER COMMIT) - 6 correções de layout e usabilidade"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Exibição Condicional da Aba Principal no Cabeçalho (Priority: P1)

Como leitor do Caderno de Leitura, desejo que o cabeçalho exiba apenas a aba principal configurada como padrão nos meus Ajustes (Dashboard ou Livros), para que a navegação seja minimalista, despoluída e reflita fielmente minha escolha de visão inicial.

**Why this priority**: Evita redundância de pontos de entrada no topo da aplicação e honra a preferência personalizada definida pelo usuário.

**Independent Test**: Alterar a preferência de tela inicial entre "Dashboard" e "Livros" nos Ajustes e verificar que o cabeçalho renderiza instantaneamente apenas a opção escolhida, mantendo os demais links ("Importar", "Ajustes", "Lixeira") inalterados.

**Acceptance Scenarios**:
1. **Given** que a tela inicial padrão é "Dashboard", **When** o cabeçalho é carregado, **Then** apenas o link "Dashboard" é visível entre os destinos principais, com "Livros" ocultado.
2. **Given** que o usuário altera a tela inicial padrão para "Livros", **When** a alteração é gravada, **Then** o cabeçalho comuta para exibir apenas "Livros", ocultando "Dashboard".
3. **Given** que o usuário navega diretamente para um livro ou estudo por link, **When** a página é renderizada, **Then** o cabeçalho mantém a coerência de navegação sem quebrar o layout.

---

### User Story 2 - Alinhamento Perfeito dos Radio Buttons na Central de Ajustes (Priority: P2)

Como leitor ajustando minhas preferências, desejo que os botões de seleção (rádio) na escolha da tela inicial fiquem verticalmente centralizados em relação ao texto e ao cartão contenedor, proporcionando uma experiência tátil equilibrada e profissional.

**Why this priority**: Corrige o desconforto visual e a assimetria estética em uma tela de alta frequência de uso.

**Independent Test**: Acessar a aba "Sistema" nos Ajustes e inspecionar visualmente o alinhamento do círculo de seleção de cada opção com a linha de texto correspondente.

**Acceptance Scenarios**:
1. **Given** a seção "Tela Inicial Padrão" nos Ajustes, **When** os cartões de opções são exibidos, **Then** o círculo de seleção (radio) está rigorosamente centralizado no eixo Y com o rótulo descritivo.
2. **Given** resoluções móveis ou texto ampliado, **When** o conteúdo quebra em duas linhas, **Then** o botão de seleção mantém alinhamento vertical flexível sem sofrer achatamento ou distorção.

---

### User Story 3 - Contraste e Legibilidade em Botões e Seletores (Priority: P1)

Como leitor utilizando temas noturnos ou modo de alto contraste, desejo que todos os botões e campos de seleção (selects) mantenham texto perfeitamente legível, para que nenhuma opção se torne invisível ou ilegível ao mudar de tema.

**Why this priority**: Garante a acessibilidade universal (WCAG AAA) e a usabilidade em ambientes escuros e com alto contraste ativado.

**Independent Test**: Ativar alternadamente temas claros e escuros (ex.: Breu, Véspera, Porcelana, E-Ink) e inspecionar botões secundários, botões de ação e campos `<select>`, certificando que o texto sempre possui contraste com o fundo.

**Acceptance Scenarios**:
1. **Given** um tema escuro ativo, **When** botões ou seletores são renderizados, **Then** a cor da fonte assume branco puro ou tom luminoso, contrastando com o fundo escuro.
2. **Given** um tema claro ativo, **When** botões secundários ou seletores são renderizados, **Then** o texto assume tom escuro de alta opacidade sobre o fundo claro.
3. **Given** as opções internas de um `<select>` (menu suspenso), **When** o usuário abre a lista, **Then** os itens exibem texto legível acompanhando o tema selecionado.

---

### User Story 4 - Coerência Cromática e Legibilidade na Seção de Estudos (Priority: P1)

Como pesquisador lendo minhas notas e fichamentos, desejo que a caixa de estudos respeite integralmente a paleta do tema ativo, para que os textos nunca fiquem escuros sobre fundos escuros nem sumam sobre fundos claros.

**Why this priority**: A leitura e a redação de anotações representam o coração da aplicação; a falha de contraste prejudica diretamente o propósito do sistema.

**Independent Test**: Abrir um estudo completo contendo título, localização, análise em abas e anotações pessoais em cada um dos 10 temas e validar a leitura contínua.

**Acceptance Scenarios**:
1. **Given** qualquer tema da aplicação (claro ou escuro), **When** a tela de estudo é aberta, **Then** o painel de análise e as anotações adotam a cor de fundo e a cor de texto primária do tema ativo.
2. **Given** títulos de estudos e links de navegação, **When** renderizados dentro de cartões de estudo, **Then** utilizam a cor canônica de texto, sem inversões indevidas de matiz.

---

### User Story 5 - Contenção de Layout no Mapa Conceitual de Estudos (Priority: P1)

Como leitor explorando a visão de Mapa, desejo que os nós de estudos e suas anotações fiquem confinados dentro da área gráfica radial, sem sobrepor o cabeçalho informativo ("Distribuição conceitual...") nem vazar as margens do cartão.

**Why this priority**: Elimina sobreposições graves de elementos de interface que impedem a leitura de textos e a interação com os nós do mapa.

**Independent Test**: Abrir a visualização de Mapa em uma obra com múltiplos estudos e verificar que a área gráfica radial está delimitada abaixo do cabeçalho de controle e que os cartões orbitais permanecem dentro da área visível.

**Acceptance Scenarios**:
1. **Given** a visualização em Mapa, **When** a página é renderizada, **Then** o cabeçalho explicativo ("Distribuição conceitual dos estudos...") permanece separado no topo do bloco, sem nenhum nó sobreposto.
2. **Given** cartões de estudos posicionados em órbitas, **When** o usuário passa o cursor ou redimensiona a tela, **Then** os títulos e botões permanecem contidos dentro da caixa delimitadora do mapa.

---

### User Story 6 - Busca Global como Modal Sobreposto (Command Palette) (Priority: P1)

Como leitor operando o sistema por atalhos de teclado (Ctrl+K ou botão Buscar), desejo que a busca global abra como um modal sobreposto centralizado com fundo escurecido (backdrop), herdando a estética da Superclasse ativa, em vez de aparecer no rodapé da página.

**Why this priority**: Transforma a busca numa ferramenta rápida de navegação (Command Palette fluida e acessível) sobreposta ao conteúdo.

**Independent Test**: Pressionar `Ctrl+K` ou clicar em "Buscar" e verificar a abertura do modal sobreposto, o foco imediato no campo de digitação, o fechamento por `Esc` e a adaptação visual à Superclasse ativa.

**Acceptance Scenarios**:
1. **Given** qualquer tela do sistema, **When** o usuário aciona a busca global, **Then** um backdrop escurecido cobre a tela inteira e o painel de busca surge centralizado na parte superior (aproximadamente a 15-20% do topo da janela).
2. **Given** a abertura da busca, **When** o modal surge, **Then** o cursor é focado imediatamente no campo de busca para digitação direta.
3. **Given** a tecla `Esc` ou clique fora do diálogo, **When** acionado, **Then** o modal fecha e o foco retorna ao elemento de origem.
4. **Given** uma Superclasse ativa (ex.: Monolítica, Mecânica, Zero-G), **When** o modal é exibido, **Then** ele herda os raios de borda, sombras e física visual da superclasse vigente.

---

## Edge Cases

- Usuário alterando a preferência de tela inicial em uma aba e comutando entre abas do navegador: o cabeçalho deve atualizar de forma reativa.
- Textos extremamente longos nos cartões do mapa conceitual: truncamento elíptico seguro sem quebrar o diâmetro da órbita.
- Modais em telas de celular: dimensionamento com margens táteis adequadas (mínimo 44px para botões de fechar e selecionar).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O componente de cabeçalho (`App.vue`) DEVE ler a preferência de tela inicial (`caderno_home_view`) e renderizar condicionalmente apenas a aba ativa escolhida ("Dashboard" ou "Livros").
- **FR-002**: A Central de Ajustes (`SettingsView.vue`) DEVE utilizar Flexbox com alinhamento vertical centralizado para os radio buttons de seleção de tela inicial.
- **FR-003**: As folhas de estilo globais DEVEM garantir alto contraste de fonte para botões e campos `<select>` (branco em fundos escuros; preto/grafite em fundos claros).
- **FR-004**: Os contêineres de estudos (`.reader-analysis`, `.study-panel`, `.markdown-content`, `.reader-notes`) DEVEM herdar explicitamente `var(--color-surface)` e `var(--color-text)`.
- **FR-005**: O componente `StudyMapView.vue` DEVE isolar a área gráfica radial dentro de um viewport dedicado (`.map-canvas-viewport`), impedindo que nós orbitais sobreponham o cabeçalho textual.
- **FR-006**: O componente `GlobalSearchModal.vue` DEVE ser renderizado via `<Teleport to="body">` com posicionamento fixo (`fixed inset-0`), backdrop translúcido, alinhamento superior (`top: ~15-20vh`) e estilos nativos sem dependência de classes utilitárias não processadas.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos 10 temas da aplicação exibem contraste nítido e legível em todos os botões e campos seletores.
- **SC-002**: Zero sobreposições entre os cartões de nós do mapa e o cabeçalho textual em resoluções desktop e mobile.
- **SC-003**: Abertura do modal de busca em menos de 100ms com foco imediato no campo de texto ao pressionar `Ctrl+K`.
- **SC-004**: 100% dos 223 testes existentes no frontend continuam passando sem regressões (`npm test`).

---

## Assumptions

- O projeto utiliza CSS nativo com tokens de design (`tokens.css`, `palettes.css`, `style.css`), não dependendo do compilador Tailwind para componentes de modal.
- As preferências de usuário continuam persistidas no `localStorage` sob a chave `caderno_home_view`.
