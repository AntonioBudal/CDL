# Feature Specification: F 0.7.6 — Redesenho da Tree View: Hierarquia Cognitiva e Estruturação de Tópicos

**Feature Branch**: `055-redesenho-tree-view`  
**Created**: 2026-10-04  
**Status**: Draft  
**Input**: User description: "F0.7.6 — Redesenho da Tree View: Hierarquia Cognitiva e Estruturação de Tópicos"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualização Hierárquica Elegante e Controles Globais de Ramos (Priority: P1) 🎯 MVP

Como uma pessoa leitora organizando fichamentos e notas conceituais, quero visualizar a árvore de estudos conectada por linhas guias sutis com opções de expandir e recolher ramos individualmente ou em lote, para compreender de imediato a subordinação entre estudos pais e subestudos sem poluição visual.

**Why this priority**: Constitui a fundação da visualização em árvore. Sem uma representação limpa de subordinação visual com conexões evidentes e controles eficientes de expansão, a Tree View perde seu propósito principal em relação às outras visualizações.

**Independent Test**: Carregar um capítulo com estudos aninhados em múltiplos níveis; verificar a renderização de linhas guias elegantes unindo ancestrais aos descendentes e acionar os botões "Expandir Todos" e "Recolher Todos", confirmando que todos os ramos respondem instantaneamente e que o estado persiste no `localStorage`.

**Acceptance Scenarios**:

1. **Given** um capítulo contendo estudos organizados em múltiplos níveis de subordinação, **When** a Tree View é renderizada, **Then** linhas guias finas e discretas conectam visualmente cada nó ancestral aos seus respectivos nós descendentes.
2. **Given** uma árvore com diversos ramos recolhidos, **When** a pessoa clica no botão "Expandir Todos", **Then** todos os ramos e sub-ramos são abertos simultaneamente.
3. **Given** uma árvore com nós abertos, **When** a pessoa clica no botão "Recolher Todos", **Then** todos os nós filhos são colapsados, mantendo apenas a visão consolidada de topo.
4. **Given** que a pessoa expande ou recolhe nós específicos, **When** a página é recarregada ou a navegação retorna àquele livro, **Then** as preferências individuais de expansão/recolhimento são restauradas fielmente do `localStorage`.

---

### User Story 2 - Percepção e Indicadores de Progresso Agregado por Ramo (Priority: P2)

Como uma pessoa estudante revisando um tópico complexo com vários subestudos, quero visualizar indicadores de progresso agregado nos nós ancestrais (mostrando quantos subestudos daquele ramo já foram concluídos ou revisados), para saber de relance quais partes do conteúdo exigem mais dedicação.

**Why this priority**: Transforma a Tree View de uma lista mecânica recuada em uma ferramenta ativa de diagnóstico e síntese da leitura, permitindo avaliar o amadurecimento dos tópicos e subtópicos.

**Independent Test**: Criar um estudo pai com 4 subestudos com diferentes status de leitura (ex.: 2 concluídos, 1 em andamento, 1 rascunho); verificar que o nó pai apresenta indicador de progresso agregado computando com precisão o estado do ramo.

**Acceptance Scenarios**:

1. **Given** um estudo que possui subestudos vinculados, **When** renderizado na árvore, **Then** o nó pai exibe um indicador sutil de progresso refletindo a proporção de estudos concluídos do ramo.
2. **Given** que um subestudo tem seu status de leitura atualizado (ex.: de "Rascunho" para "Concluído"), **When** a árvore atualiza reativamente, **Then** os indicadores de progresso de todos os seus ancestrais diretos são recalculados instantaneamente.
3. **Given** um nó folha (sem filhos), **When** renderizado, **Then** o indicador de progresso agregado não é exibido, evitando ruído em estudos que não possuem ramificações.

---

### User Story 3 - Reorganização Magnética, Bloqueio de Ciclos e Ergonomia Mobile (Priority: P3)

Como uma pessoa leitora organizando suas notas no computador ou no celular, quero poder reorganizar a árvore via drag-and-drop com indicação visual evidente de inserção (irmão antes, irmão depois ou aninhamento como filho) e proteção contra ciclos e excesso de profundidade, além de contar com ações táteis acessíveis no mobile.

**Why this priority**: Garante integridade topológica estrutural (sem loops infinitos nem profundidade excessiva > 5 níveis) e assegura que usuários em smartphones consigam reorganizar a árvore sem frustrações de arrasto manual na tela de toque.

**Independent Test**: Arrastar um nó sobre outro e verificar a distinção visual clara entre "soltar como irmão" e "aninhar como filho"; tentar soltar um ancestral dentro de seu próprio filho e verificar que a ação é terminantemente bloqueada; em viewport móvel (< 768px), verificar que os alvos de chevron e os botões de ação atendem à área de toque mínima de 44×44px.

**Acceptance Scenarios**:

1. **Given** o arrasto de um nó sobre um nó destino, **When** o cursor se posiciona no topo ou base do card, **Then** uma linha guia indica reordenação linear antes/depois; **When** o cursor se posiciona no centro do card destino, **Then** uma moldura magnética com estilo e cor distintos indica que o nó será aninhado como filho.
2. **Given** uma tentativa de arrastar um nó pai para dentro de um de seus próprios descendentes, **When** o cursor atinge o alvo proibido, **Then** o sistema sinaliza proibição visual imediata e impede o drop, prevenindo formação de ciclos.
3. **Given** um nó já posicionado no nível 4 (profundidade máxima permitida de 5 níveis), **When** há tentativa de aninhar outro estudo sob ele, **Then** o sistema bloqueia o aninhamento indicando que o limite foi atingido.
4. **Given** acesso em dispositivo móvel (< 768px), **When** a pessoa interage com a árvore, **Then** os botões de expandir/recolher e o menu tátil de ordenação ("Mover para cima", "Mover para baixo", "Promover", "Recuar") oferecem alvos de toque confortáveis de no mínimo 44×44px.

---

### Edge Cases

- **Árvore vazia no capítulo**: Renderizar estado vazio acolhedor (*EmptyState*) com link convidando a importar o primeiro estudo.
- **Ramo com mais de 30 subestudos**: Garantir renderização reativa suave e computeds memoizados em tempo constante, sem engasgos de interface.
- **Mudança concorrente de hierarquia**: Se um dispositivo reorganizar nós simultaneamente, interceptar erro HTTP 409 e apresentar mensagem explicativa com recarregamento seguro da árvore.
- **Títulos longos de estudos em níveis profundos de aninhamento**: Garantir que o texto quebre ou apresente truncamento suave com reticências, sem causar quebra desproporcional ou transbordamento horizontal da tela.

---

## Clarifications

### Clarification Decisions

- **Q1 (Formato do Indicador de Progresso)**: Micro-badge com fração textual e barra sutil (ex.: `2/4 concluídos` com tooltip detalhando os status de leitura).
- **Q2 (Escopo de Contabilização do Progresso)**: Todos os descendentes recursivos do ramo (filhos + netos + bisnetos), considerando como etapas consolidadas os estudos com status `concluido` e `revisado`.
- **Q3 (Estado Inicial de Abertura da Árvore)**: Totalmente expandida por padrão no primeiro acesso, permitindo visão panorâmica imediata de todos os tópicos e persistindo no `localStorage` os recolhimentos manuais subsequentes.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE exibir a árvore de estudos com linhas guias finas e semânticas conectando os nós ancestrais aos seus respectivos descendentes em todos os níveis visíveis.
- **FR-002**: O sistema DEVE disponibilizar botões globais no topo da Tree View para "Expandir Todos" e "Recolher Todos" os ramos em um único clique.
- **FR-003**: O sistema DEVE persistir a lista de IDs de nós expandidos no `localStorage` por livro/capítulo, restaurando-a ao retornar à visualização.
- **FR-004**: O sistema DEVE calcular e exibir em cada nó pai um indicador de progresso agregado dos subestudos do seu ramo no formato de micro-badge com fração textual e barra sutil (ex.: "2/4 concluídos" com tooltip informativo).
- **FR-005**: O cálculo de progresso agregado do ramo DEVE considerar recursivamente todos os descendentes do nó (filhos, netos e bisnetos), computando como completude consolidada os estudos com status `concluido` e `revisado`.
- **FR-006**: Ao carregar a Tree View pela primeira vez sem histórico registrado no `localStorage`, o sistema DEVE iniciar com a árvore totalmente expandida por padrão, permitindo visão panorâmica de todos os tópicos e persistindo recolhimentos subsequentes.
- **FR-007**: O sistema DEVE travar o limite máximo de profundidade da árvore em exatamente 5 níveis (níveis 0 a 4).
- **FR-008**: O mecanismo de reordenação DEVE bloquear determinística e preventivamente qualquer tentativa de aninhar um nó dentro de si mesmo ou de seus próprios descendentes.
- **FR-009**: O drag-and-drop DEVE diferenciar visualmente com alta clareza a inserção linear (linhas guias superior/inferior) do aninhamento subordinado (moldura de absorção no nó destino).
- **FR-010**: A interface DEVE adotar estrutura semântica WAI-ARIA Treeview (`role="tree"`, `role="treeitem"`, `aria-expanded`, `aria-level`), navegação completa por teclado e alvos táteis mínimos de 44×44px no mobile.

---

### Key Entities

- **StudyTreeNode**: Objeto enriquecido do estudo contendo identificador, chave do estudo pai (`parent_study_id`), posição ordinal de ordenação (`position`), profundidade relativa (`depth`), lista de filhos imediatos (`children`) e métricas calculadas do ramo.
- **BranchProgress**: Representação agregada da completude do ramo temático (total de subestudos, quantidade de estudos concluídos/revisados e percentual acumulado).
- **TreeExpansionState**: Conjunto reativo de identificadores de nós expandidos sincronizado com o `localStorage`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: As ações de "Expandir Todos" e "Recolher Todos" executam e atualizam o estado de renderização em menos de 100ms para até 100 nós.
- **SC-002**: 100% dos nós pais com subestudos exibem indicador de progresso de ramo atualizado reativamente com precisão matemática.
- **SC-003**: Zero ciclos topológicos permitidos: 100% das tentativas de aninhamento em descendentes são bloqueadas preventivamente.
- **SC-004**: Em dispositivos móveis (< 768px), 100% dos botões de controle, expansão e menu de movimentação possuem alvos de toque de no mínimo 44×44px.
- **SC-005**: Conformidade estrita com a Constituição do projeto (preservação do acervo, isolamento de testes e dados sintéticos).

---

## Assumptions

- A hierarquia apoia-se no campo `parent_study_id` já existente no modelo `Study` do backend.
- A persistência de movimentação utiliza a rota existente `POST /api/studies/{study_id}/move`.
- Não há necessidade de alterações estruturais no schema do banco SQLite.
- A árvore opera dentro do escopo de um capítulo selecionado ou do conjunto ativo de estudos.
