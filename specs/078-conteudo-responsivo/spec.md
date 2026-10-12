# Feature Specification: Leitor e Disposição de Conteúdo Responsivo

**Feature Branch**: `078-conteudo-responsivo`  
**Created**: 2026-10-12  
**Status**: Draft  
**Input**: Problemas P-11, P-12, P-14, P-15, P-16, P-17 e P-18 da Auditoria de Responsividade (F0.8.13).

Esta feature otimiza a leitura e a disposição de conteúdo em dispositivos móveis e telas estreitas. Ela garante que a gaveta de capítulos em `BookView` inicie fechada por padrão no celular, agrupa ações secundárias do livro em um menu compacto, converte a tabela administrativa de 8 colunas em cartões adaptativos em `< 768px`, blinda grids contra estouro em viewports de 320px, padroniza modais com altura dinâmica `dvh` e protege interações de hover em telas sensíveis ao toque.

---

## User Scenarios & Testing

### User Story 1 - Leitor Focado e Navegação de Capítulos sem Bloqueio (Priority: P1)
Como leitor acessando uma obra no celular (< 768px), quero abrir o livro e ver imediatamente o conteúdo ou área principal de leitura, com a gaveta de capítulos recolhida por padrão e ações secundárias recolhidas em menu, para poder ler sem que gavetas laterais ocupem toda a tela logo no carregamento.

**Why this priority**: O problema P-17 causa fricção grave na experiência de leitura móvel: ao abrir um livro, a gaveta lateral de capítulos sobrepõe todo o conteúdo, forçando o leitor a fechá-la manualmente toda vez antes de começar a ler. Além disso, múltiplos botões soltos no cabeçalho provocam quebras de linha e desordem visual.

**Independent Test**: Carregar um livro em viewport de 375px; verificar que o painel de capítulos inicia recolhido (fechado) e que as ações secundárias do cabeçalho estão organizadas de forma limpa. Ao acionar o botão de capítulos, a gaveta abre suavemente para seleção.

**Acceptance Scenarios**:
1. **Dado** uma viewport móvel `< 768px`, **quando** o leitor navega para `/books/:bookId`, **então** o painel esquerdo de capítulos (`leftCollapsed`) inicia fechado por padrão se não houver preferência salva, permitindo visualização imediata do conteúdo da obra.
2. **Dado** o cabeçalho de `BookView` em telas `< 768px`, **quando** renderizado, **então** as ações secundárias (exportar, editar e mover para lixeira) são acomodadas em menu contextual acessível ou disposição compacta, mantendo alvos táteis mínimos de 44x44px.
3. **Dado** a gaveta de capítulos em modo móvel, **quando** o leitor clica no botão de alternância de capítulos, **então** a gaveta é expandida com transição limpa e pode ser recolhida ao selecionar um capítulo ou tocar no botão de fechar.

---

### User Story 2 - Gestão Administrativa em Cartões Adaptativos (Priority: P1)
Como administrador acessando o painel de usuários em um tablet pequeno ou smartphone (< 768px), quero visualizar as contas em cartões verticais legíveis com rótulos claros e botões de ação confortáveis, em vez de uma tabela achatada com 8 colunas e rolagem horizontal excessiva.

**Why this priority**: O problema P-14 torna a gestão de usuários inoperante no mobile; 8 colunas de dados forçam rolagem horizontal desajeitada e truncam identificadores, papéis e botões de suspensão e revogação.

**Independent Test**: Acessar a tabela de administração de usuários (`AdminUsersTable.vue`) em 375px e 320px; constatar que os usuários são exibidos em formato de cartão individual sem quebra de overflow na página, com todos os dados essenciais e ações disponíveis com área tátil mínima de 44x44px.

**Acceptance Scenarios**:
1. **Dado** o componente `AdminUsersTable.vue` em viewport `< 768px`, **quando** a listagem de usuários é exibida, **então** a estrutura em tabela tradicional com `thead` e 8 colunas horizontais é substituída por cartões verticais responsivos.
2. **Dado** cada cartão de usuário móvel, **quando** renderizado, **então** exibe identidade (nome, usuário, e-mail), crachás de papel (Administrador/Leitor) e status (Ativo/Suspenso), estatísticas de estudos e sessões, data de último acesso e botões de ação operacional.
3. **Dado** uma viewport de desktop ($\ge 768\text{px}$), **quando** o administrador acessa a tela, **então** a tabela tradicional com cabeçalhos de coluna continua sendo exibida sem regressões.

---

### User Story 3 - Blindagem de Grids em 320px e Telas Ultra-Estreitas (Priority: P2)
Como leitor utilizando um smartphone compacto (320px de largura, como iPhone SE de primeira geração), quero navegar pelas telas de Amigos, Administração e Institucional sem barras de rolagem horizontal espúrias, para ter uma experiência fluida e sem cortes de layout.

**Why this priority**: O problema P-15 decorre de declarações CSS com `minmax(280px, 1fr)` que, ao somarem paddings laterais e margens internas do container, ultrapassam os 320px da tela física, forçando overflow horizontal na página inteira.

**Independent Test**: Inspecionar telas que utilizam grids declaradas (`FriendsView`, `AdminView`, `SovereigntySection`) em 320px; constatar que a largura horizontal total da página permanece exatamente em 320px sem overflow nem scroll horizontal.

**Acceptance Scenarios**:
1. **Dado** uma viewport com largura mínima de 320px, **quando** renderizadas as grades de cartões em `FriendsView`, `AdminView` e seções da página inicial, **então** o tamanho mínimo das colunas adapta-se com `minmax(min(100%, 280px), 1fr)` ou valores seguros, impedindo qualquer estouro horizontal.
2. **Dado** qualquer container dessas visualizações em 320px, **quando** medido o `scrollWidth` em relação ao `clientWidth`, **então** não há rolagem horizontal indesejada no corpo do documento.

---

### User Story 4 - Modais com Altura Dinâmica `dvh` e Blindagem de Hover Tátil (Priority: P2)
Como leitor no celular interagindo com janelas modais e cartões, quero que os modais caibam perfeitamente na área visível da tela mesmo quando as barras do navegador ou o teclado virtual aparecem, e que cartões não fiquem travados em estado flutuante após um toque.

**Why this priority**: O problema P-16 corta o rodapé de modais devido ao cálculo de `vh` tradicional em navegadores móveis (Safari iOS e Chrome Android possuem barras retráteis). O problema P-18 faz com que efeitos de elevação `:hover` fiquem presos permanentemente após toque em celulares.

**Independent Test**: Abrir `BookEditModal`, `ExportModal`, `StudyHistoryModal` e outros modais em navegador móvel; verificar que a altura máxima respeita `dvh` com rolagem interna acessível. Tocar em cartões com elevação; verificar ausência de travamento visual em `:hover`.

**Acceptance Scenarios**:
1. **Dado** as janelas modais do sistema (`BookEditModal`, `ExportModal`, `StudyHistoryModal`, `SettingsView`), **quando** renderizadas, **então** utilizam `max-height: min(90dvh, ...)` ou declarações duplas com `dvh` sobre `vh` como fallback progressivo.
2. **Dado** elementos com animação ou elevação no estado `:hover` (`.book-card`, etc.), **quando** aplicados efeitos como `transform: translateY`, **então** são condicionados à capacidade real do ponteiro através de `@media (hover: hover) and (pointer: fine)`, evitando efeitos presos após toques em telas capacitivas.

---

## Functional Requirements

- **FR-001**: Em `useSplitPanes.ts`, inicializar `leftCollapsed` como `true` por padrão quando o modo inicial de layout for `mobile` (`< 768px`) e não houver dimensões salvas previamente.
- **FR-002**: Em `BookView.vue`, reorganizar o cabeçalho da obra em telas `< 768px` para evitar superlotação de botões, preservando alvos táteis mínimos de 44x44px.
- **FR-003**: Em `AdminUsersTable.vue`, criar renderização responsiva em cartões verticais ativada em viewports `< 768px`, contendo todas as informações de identidade, crachás de status e papel, métricas e botões de ação rápida.
- **FR-004**: Manter a tabela convencional em `AdminUsersTable.vue` para telas $\ge 768\text{px}$.
- **FR-005**: Atualizar declarações de grid com colunas mínimas rígidas de 280px (`FriendsView.vue`, `AdminView.vue`, `SovereigntySection.vue`) para fórmulas fluidas baseadas em `minmax(min(100%, 260px), 1fr)` ou equivalentes que comportem viewports de 320px sem overflow.
- **FR-006**: Atualizar a altura de modais chave (`BookEditModal.vue`, `ExportModal.vue`, `StudyHistoryModal.vue`, `SettingsView.vue`) para utilizar unidades de viewport dinâmico (`dvh`) com fallback seguro para `vh`.
- **FR-007**: Encapsular elevações de cartão em `:hover` (em `style.css` e componentes) dentro de `@media (hover: hover) and (pointer: fine)`.
- **FR-008**: Criar suíte de testes unitários automatizados validando a integridade das alterações de layout e comportamento responsivo da Feature 078.

---

## Success Criteria

- **SC-001**: `BookView` em 375px inicia com painel de capítulos fechado sem sobrepor a leitura do livro.
- **SC-002**: `AdminUsersTable` exibe cartões verticais em viewports `< 768px` com alvos táteis $\ge 44 \times 44\text{ px}$.
- **SC-003**: Nenhuma tela inspecionada apresenta barra de rolagem horizontal em 320px de viewport.
- **SC-004**: Modais utilizam unidades dinâmicas `dvh` mantendo rolagem interna sem cortes por barras de endereço móveis.
- **SC-005**: 100% dos testes unitários e de build (`npm test`, `npm run build`, `pytest`) passam com sucesso.
