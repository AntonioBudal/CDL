# Feature Specification: Hierarquia e Ergonomia de Header Actions no Leitor

**Feature Branch**: `050-ergonomia-header-actions`  
**Created**: 2026-10-03  
**Status**: Ready for Planning  
**Input**: User description: "F 0.7.1 — Hierarquia e Ergonomia de Header Actions no Leitor (StudyView.vue)"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Experiência Desktop: Hierarquia Editorial e Ação Primária em Destaque (Priority: P1)

Como um leitor estudando no computador desktop, quero que o cabeçalho do estudo tenha uma separação visual nítida entre o título, o status e as ações disponíveis, com o botão "Editar estudo" em posição de destaque e as ações secundárias organizadas sem ruído, para que a leitura seja imersiva e livre de distrações visuais desnecessárias.

**Why this priority**: No desktop, a dispersão causada por 5 botões de mesmo peso lado a lado empobrece a experiência editorial e desvaloriza a ação mais importante do leitor (editar suas anotações). Organizar essa barra é a fundação de ergonomia da versão 0.7.

**Independent Test**: Pode ser validado acessando qualquer estudo em tela desktop (largura > 768px), conferindo que o botão primário "Editar" tem destaque visual inequívoco, a ação de colaboração ("Compartilhar") permanece acessível e as ações utilitárias ("Exportar", "Histórico de versões", "Mover para lixeira") estão reunidas de forma elegante em um menu suspenso compacto `•••`.

**Acceptance Scenarios**:
1. **Given** um usuário visualizando um estudo próprio em tela desktop (resolução ≥ 1024px), **When** a página é renderizada, **Then** o cabeçalho exibe o breadcrumb, status clicável, título editorial, botão de destaque "Editar estudo", botão "Compartilhar" e um botão acionador de menu suspenso `•••` ("Mais opções").
2. **Given** o usuário no leitor desktop, **When** clica no botão `•••` de mais opções, **Then** um menu suspenso se abre exibindo as opções secundárias ("Exportar estudo", "Histórico de versões", "Mover para a lixeira"), com ícones e rótulos claros.
3. **Given** o menu suspenso aberto, **When** o usuário clica fora dele ou pressiona a tecla `Escape`, **Then** o menu é fechado imediatamente sem afetar a área de leitura.

---

### User Story 2 - Experiência Mobile: Linha Única Compacta e Alvos de Toque Acessíveis (Priority: P1)

Como um leitor utilizando o Leitorum em smartphone ou tablet, quero que o cabeçalho do estudo não ocupe metade da tela com quebras de linha irregulares de múltiplos botões, apresentando um topo conciso, com título legível e alvos de toque confortáveis (mínimo de 44x44px), para que o texto do estudo comece logo na área visível da tela.

**Why this priority**: No celular, a disposição atual quebra os botões em duas a três linhas desiguais, empurrando o texto principal para baixo da dobra e gerando toques acidentais em botões perigosos (como "Mover para lixeira").

**Independent Test**: Pode ser validado redimensionando o navegador para resolução mobile (360px a 480px de largura) e constatando que as ações do cabeçalho não quebram em mais de uma linha, os botões possuem área de toque de pelo menos 44x44px e o menu suspenso é acionado sem transbordar horizontalmente da tela.

**Acceptance Scenarios**:
1. **Given** um usuário acessando o estudo em dispositivo móvel (largura < 768px), **When** a página é carregada, **Then** o cabeçalho mantém altura contida, com alinhamento em linha única para as ações e preservando a área nobre da tela para o conteúdo.
2. **Given** o usuário em tela móvel, **When** interage com qualquer botão ou o menu suspenso do cabeçalho, **Then** a área de toque efetiva é de no mínimo 44x44 pixels, prevenindo toques erráticos em elementos adjacentes.
3. **Given** o menu suspenso aberto em tela móvel, **When** exibido, **Then** o menu se posiciona defensivamente dentro dos limites do viewport sem provocar barra de rolagem horizontal.

---

### User Story 3 - Acessibilidade WAI-ARIA e Navegação por Teclado (Priority: P2)

Como um usuário que navega exclusivamente por teclado ou leitor de tela, quero que o menu de ações do cabeçalho cumpra os padrões semânticos de acessibilidade (WAI-ARIA Menu), para que eu possa acionar, percorrer as opções com setas e fechá-lo sem armadilhas de foco.

**Why this priority**: O leitor de estudos deve ser universalmente operável. O menu suspenso não pode perder foco nem impedir a navegação fluida por teclado.

**Independent Test**: Pode ser testado navegando pelo cabeçalho via tecla `Tab`, abrindo o menu com `Enter` ou `Space`, percorrendo os itens com `ArrowDown`/`ArrowUp` e fechando com `Escape`, verificando retorno do foco para o botão disparador.

**Acceptance Scenarios**:
1. **Given** foco no botão acionador `•••`, **When** o usuário pressiona `Enter` ou `Space`, **Then** o menu é aberto, o primeiro item recebe foco ativo e o atributo `aria-expanded` passa para `true`.
2. **Given** o menu aberto com foco em um item, **When** o usuário pressiona `Escape`, **Then** o menu se fecha e o foco do teclado retorna ao botão acionador `•••`.
3. **Given** o menu aberto, **When** o usuário navega com `ArrowDown` e `ArrowUp`, **Then** o foco circula entre os itens válidos sem sair do menu.

---

### User Story 4 - Modo Somente Leitura e Visualização de Convidado (Priority: P2)

Como um convidado ou leitor visualizando um estudo compartilhado sem permissão de escrita, quero ver um cabeçalho adaptado que oculte ações que não posso executar (como "Editar" e "Mover para lixeira"), mantendo apenas as utilidades pertinentes (como "Exportar estudo"), sem espaço vazio ou controles desativados confusos.

**Why this priority**: Evita poluição de interface para quem está apenas consumindo conteúdo compartilhado por outro usuário.

**Independent Test**: Pode ser validado abrindo um estudo em modo visitante (`canEdit === false`), constatando a ausência do botão "Editar", da opção "Mover para lixeira" e a permanência limpa da opção "Exportar".

**Acceptance Scenarios**:
1. **Given** um leitor visualizando um estudo de outro usuário sem permissão de edição, **When** o cabeçalho é exibido, **Then** o botão "Editar estudo" e a opção "Mover para lixeira" não são renderizados.
2. **Given** o leitor visitante, **When** acessa as ações do cabeçalho, **Then** apenas opções de consumo (ex.: "Exportar estudo") estão disponíveis, de forma limpa e contextual.

---

### Edge Cases

- **Títulos de Estudo Extremamente Longos**: Títulos com mais de 80 caracteres em telas móveis devem truncar elegantemente ou quebrar sem empurrar o bloco de ações para fora da tela.
- **Telas com Largura Ultra-Estreita (< 340px)**: Em aparelhos antigos ou janelas redimensionadas ao extremo, o cabeçalho deve manter espaçamento mínimo defensivo sem quebrar layout.
- **Teclas de Atalho de Active Recall Concorrentes**: O uso das teclas `j`, `k`, `Escape` do modo de memorização ativa não pode conflitar com a navegação interna do menu suspenso quando este estiver aberto.
- **Abertura do Menu Próxima à Borda Direita**: O dropdown deve abrir alinhado à direita para evitar transbordamento (`overflow-x`).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O cabeçalho de `StudyView.vue` DEVE diferenciar visualmente a ação primária ("Editar estudo") das ações utilitárias secundárias.
- **FR-002**: O sistema DEVE fornecer um componente reutilizável de menu suspenso (`DropdownMenu.vue`) para agrupar ações secundárias sob um botão acionador `•••` ("Mais opções").
- **FR-003**: No Desktop (viewport ≥ 768px), o botão "Editar estudo" DEVE ser renderizado com destaque primário, o botão "Compartilhar" DEVE permanecer imediatamente visível e as ações "Exportar estudo", "Histórico de versões" e "Mover para a lixeira" DEVEM estar agrupadas no menu `•••`.
- **FR-004**: No Mobile (viewport < 768px), a barra de ações DEVE permanecer contida em uma única linha horizontal, sem empurrar a área de leitura.
- **FR-005**: No Mobile (viewport < 768px), o cabeçalho DEVE expor diretamente apenas o botão de ação primária "Editar" (com ícone e destaque visual) e o botão acionador do menu `•••`, mantendo todas as ações secundárias (Compartilhar, Histórico de versões, Exportar estudo e Mover para a lixeira) centralizadas dentro do menu suspenso, preservando espaço máximo para o título.
- **FR-006**: Em viewports móveis estreitas (< 640px), a trilha de navegação (breadcrumb) DEVE colapsar em um botão acessível de retorno `← Voltar ao capítulo` (exibindo o nome do capítulo com truncamento defensivo caso necessário), otimizando a altura vertical e garantindo alvo tátil de retorno de fácil alcance.
- **FR-007**: O menu suspenso DEVE fechar automaticamente ao detectar clique fora de sua área (`click-outside`) ou pressionamento da tecla `Escape`.
- **FR-008**: O menu suspenso DEVE implementar os atributos WAI-ARIA `aria-haspopup="menu"`, `aria-expanded` dinâmico e suportar navegação via setas do teclado (`ArrowDown` / `ArrowUp`).
- **FR-009**: Todos os elementos interativos do cabeçalho em viewports móveis DEVEM ter área de toque mínima de 44x44 pixels.
- **FR-010**: O componente de status de estudo (`StudyStatusBadge.vue`) DEVE manter sua interatividade de troca rápida com 1 clique para proprietários, com alinhamento coeso junto aos metadados do cabeçalho.
- **FR-011**: Quando o estudo for visualizado em modo somente leitura (`canEdit === false`), as ações restritas de mutação DEVEM ser omitidas, exibindo apenas as ações permitidas.
- **FR-012**: O item "Mover para a lixeira" no menu suspenso DEVE ser estilizado com indicação semântica de perigo (`danger`) e abrir a confirmação pré-existente antes de qualquer ação.

---

### Key Entities *(include if feature involves data)*

- **HeaderActionItem**: Representa um item de menu secundário (rótulo, ícone SVG, variante visual `default` ou `danger`, manipulador de clique ou rota de navegação, condição de visibilidade por permissão).
- **StudyHeaderState**: Estado reativo da interface do leitor contendo status de carregamento, modo de permissão (`canEdit`), visibilidade do dropdown de ações e disparadores dos modais vinculados (compartilhamento, exportação, histórico, exclusão).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em viewports de qualquer tamanho (320px até 4K), as ações do cabeçalho ocupam exatamente 1 linha horizontal, eliminando 100% das quebras desiguais de botões.
- **SC-002**: A altura vertical ocupada pelo cabeçalho no mobile é reduzida em pelo menos 35% em relação ao leiaute anterior com botões espalhados, trazendo o conteúdo textual do estudo imediatamente para a dobra superior da tela.
- **SC-003**: 100% dos elementos clicáveis no cabeçalho mobile respeitam o tamanho mínimo de toque de 44x44px, conforme WCAG 2.1 Critério 2.5.5.
- **SC-004**: O menu de ações pode ser completamente operado usando apenas o teclado (`Tab`, `Enter`, `Setas`, `Escape`), sem qualquer armadilha de foco.
- **SC-005**: 100% dos testes unitários e de integração existentes de `StudyView.vue` continuam passando sem regressão.

---

## Assumptions

- A feature não altera modelos de banco de dados, migrações ou endpoints de backend.
- Os modais existentes (`ShareModal`, `ExportStudyModal`, `StudyHistoryModal`, confirmação de lixeira) são preservados na íntegra; apenas seus botões disparadores são reorganizados no cabeçalho e menu.
- A biblioteca de ícones SVG segue o padrão inline já adotado no projeto (`Heroicons` em formato SVG puro, sem dependências externas de ícones pesadas).
- As superclasses cinemáticas e tokens de cor (`--color-surface`, `--color-text-primary`, `--color-danger`, etc.) são reutilizados para total aderência aos temas da aplicação.
