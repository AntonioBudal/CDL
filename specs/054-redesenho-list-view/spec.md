# Feature Specification: F 0.7.5 — Redesenho da List View: Busca Rápida, Filtragem e Comparação Analítica

**Feature Branch**: `054-redesenho-list-view`

**Created**: 2026-10-03

**Status**: Draft

**Input**: User description: "/speckit-specify F 0.7.5" (F 0.7.5 — Redesenho da List View: Busca Rápida, Filtragem e Comparação Analítica)

## Clarifications

### Session 2026-10-03
- Q: Como os micro-chips de seções analíticas (R, E, C, Ref) devem ser apresentados visualmente para máxima clareza sem poluição visual? → A: 4 micro-chips fixos com siglas (`R`, `E`, `C`, `Ref`), coloridos e contrastantes quando preenchidos e cinzas/esmaecidos quando vazios, assegurando largura constante e alinhamento tabular uniforme.
- Q: Qual deve ser o comportamento sequencial de múltiplos cliques no mesmo cabeçalho de coluna da tabela? → A: Ciclo tripartite: 1º clique = Ascendente (`↑`), 2º clique = Descendente (`↓`), 3º clique = Reset para a ordem canônica do livro/capítulo.
- Q: Como a barra de busca e as pílulas de filtro por status devem ser organizadas acima da lista no celular (< 768px)? → A: Campo de busca sempre visível no topo acompanhado de botão de filtro expansível (gaveta/accordion) para as opções de status, liberando altura vertical para os estudos.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tabela Analítica Densa com Ordenação Multicritério (Priority: P1) 🎯 MVP

Como uma pessoa leitora e pesquisadora com muitos estudos registrados em um capítulo ou livro, quero uma visualização em tabela densa com cabeçalhos ordenáveis por título, status de leitura e data, para que eu possa inspecionar e comparar rapidamente todo o acervo sem a dispersão espacial de cartões.

**Why this priority**: É o valor central da List View — entregar alta densidade informacional e capacidade de ordenação com 1 clique, diferenciando-se fundamentalmente da Grid View e da Tree View.

**Independent Test**: Pode ser testado carregando um capítulo com múltiplos estudos: verificar que a tabela exibe colunas estruturadas, que clicar nos cabeçalhos altera a ordenação (ascendente e descendente) e que a preferência é lembrada.

**Acceptance Scenarios**:

1. **Given** que o usuário está na List View de um capítulo com estudos carregados, **When** a tabela é exibida no desktop, **Then** as colunas apresentam Título, Localização, Status de Leitura, Data de Atualização e Quantidade de Conexões.
2. **Given** que o usuário clica no cabeçalho de uma coluna (ex.: Título ou Data), **When** a ordenação é aplicada, **Then** as linhas são reorganizadas instantaneamente com indicador visual de direção da ordenação (`↑` ou `↓`).
3. **Given** que o usuário clica em uma linha da tabela, **When** a ação é disparada, **Then** o sistema transporta imediatamente o leitor para a tela de leitura daquele estudo.

---

### User Story 2 - Busca Textual Instantânea e Filtragem Rápida por Status (Priority: P2)

Como uma pessoa usuária buscando um tópico específico dentro de dezenas de fichamentos, quero digitar termos na barra de busca e selecionar filtros de status no topo para isolar instantaneamente os estudos relevantes em menos de 50 milissegundos.

**Why this priority**: Permite localização cirúrgica de trechos e análise segmentada (ex.: revisar apenas o que está "Em Andamento"), poupando navegações desnecessárias.

**Independent Test**: Digitar termos presentes no título ou localização e selecionar um status de filtro: a tabela deve atualizar em tempo real sem recarregar a página e exibir contador de resultados encontrados.

**Acceptance Scenarios**:

1. **Given** que o usuário digita um termo no campo de busca rápida, **When** o texto é inserido, **Then** as linhas da lista filtram em tempo real (< 50ms) mantendo apenas estudos cujo título, localização ou notas coincidam com o termo.
2. **Given** que o usuário seleciona uma pílula de status no filtro (ex.: "Em Andamento"), **When** o filtro é ativado, **Then** apenas estudos com esse status de leitura permanecem visíveis.
3. **Given** que nenhum estudo coincide com a combinação de busca e filtro, **When** o estado vazio é renderizado, **Then** a interface apresenta mensagem acolhedora com botão de ação rápida "Limpar filtros".

---

### User Story 3 - Indicadores de Seções Preenchidas e Ergonomia Mobile Compacta (Priority: P3)

Como uma pessoa usuária acessando o acervo em um smartphone ou revisando a completude dos estudos, quero ver indicadores compactos das seções analíticas preenchidas (R, E, C, Ref) e uma lista responsiva de 2 linhas por estudo, para que a leitura e a conferência sejam confortáveis em qualquer tamanho de tela.

**Why this priority**: Confere poder analítico imediato (saber de relance se o fichamento possui resumo, explicação, conceitos e referências) e assegura que a tela móvel não sofra com tabelas largas ou rolagem horizontal desconfortável.

**Independent Test**: Reduzir a viewport para largura de smartphone (< 768px): a tabela deve transicionar suavemente para uma lista densa de 2 linhas com alvos de toque mínimos de 44×44px e chips compactos de seções preenchidas visíveis.

**Acceptance Scenarios**:

1. **Given** um estudo que possua Resumo e Explicação preenchidos, mas Conceitos e Referências vazios, **When** renderizado na lista, **Then** a coluna/área de completude exibe micro-chips das 4 seções analíticas com indicação clara de preenchimento.
2. **Given** uma tela móvel (< 768px), **When** a List View é acessada, **Then** os estudos são exibidos em linhas compactas de 2 níveis (Linha 1: Título e Status; Linha 2: Localização, Data e chips de seções), sem rolagem horizontal indesejada.
3. **Given** interação por toque ou teclado no mobile, **When** os botões e linhas são acionados, **Then** os alvos interativos atendem ao tamanho confortável mínimo de 44×44px.

---

### Edge Cases

- **Estudo sem localização ou data**: A linha deve manter alinhamento tabular perfeito exibindo hífen ou espaço reservado sem quebrar a grade.
- **Termo de busca com acentos e caixa alta/baixa**: A busca deve ser insensível a maiúsculas/minúsculas e ignorar diacríticos (ex.: buscar "dialetica" encontra "Dialética").
- **Capítulo vazio**: Apresentar estado vazio acolhedor (*EmptyState*) com botão para importar estudo.
- **Múltiplos cliques rápidos na ordenação**: Alternar consistentemente sem travar a renderização reativa da tabela.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE exibir os estudos em formato de tabela estruturada de alta densidade no desktop e formato compacto de 2 linhas em dispositivos móveis.
- **FR-002**: A tabela DEVE permitir ordenação interativa de 1 clique nos cabeçalhos de coluna por Posição/Ordem Natural, Título, Status de Leitura e Data de Atualização.
- **FR-003**: O sistema DEVE persistir o critério de ordenação ativo da List View no `localStorage` por livro/capítulo.
- **FR-004**: O sistema DEVE fornecer um campo de busca rápida no topo que filtre reativamente a listagem em menos de 50ms com correspondência insensível a maiúsculas e diacríticos.
- **FR-005**: O sistema DEVE disponibilizar filtro seletor de status no topo (Todos, Rascunho, Em Andamento, Revisado, Concluído) combinável com a busca textual.
- **FR-006**: Cada estudo DEVE exibir micro-chips fixos das 4 seções analíticas com siglas (`R`, `E`, `C`, `Ref`), coloridos quando preenchidos e esmaecidos quando vazios, assegurando largura constante e identificação imediata.
- **FR-007**: A ordenação por cabeçalho DEVE seguir um ciclo tripartite a cada clique sucessivo na mesma coluna: 1º clique = Ascendente (`↑`), 2º clique = Descendente (`↓`), 3º clique = Reset para a ordem canônica original do livro/capítulo.
- **FR-008**: O layout móvel (< 768px) DEVE disponibilizar o campo de busca sempre visível no topo acompanhado de botão de filtro expansível (gaveta/accordion) para alternar as opções de status de forma ergonômica e sem consumir altura excessiva.
- **FR-009**: O sistema DEVE exibir um estado de busca sem resultados com botão "Limpar filtros" que reseta instantaneamente a busca e os filtros ativos.
- **FR-010**: A interface DEVE adotar estrutura semântica WAI-ARIA (`role="table"`, `role="row"`, `role="columnheader"`) com suporte a navegação por teclado (`Tab`, `Enter`) e alvos táteis mínimos de 44×44px.

---

### Key Entities

- **StudyListItem**: Representação tabular do estudo contendo metadados de identificação, status cromático, contagem de conexões e marcadores booleanos de seções preenchidas.
- **StudyListFilterState**: Estado dos filtros ativos, incluindo termo de busca (`searchQuery`), filtro de status (`statusFilter`) e ordenação (`sortBy`, `sortDirection`).
- **SectionPresenceChips**: Conjunto de 4 indicadores compactos correspondentes às quatro seções analíticas canônicas (`R`, `E`, `C`, `Ref`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A busca textual filtra instantaneamente a lista de estudos em menos de 50 milissegundos sem travamento perceptível.
- **SC-002**: A densidade visual de estudos por altura de tela é pelo menos 2.5× maior que a da Grid View no mesmo viewport desktop.
- **SC-003**: 100% dos cliques em cabeçalhos de coluna ordenam a tabela sem recarregamento da página.
- **SC-004**: A experiência móvel (< 768px) funciona sem barra de rolagem horizontal e com alvos táteis mínimos de 44×44px.
- **SC-005**: 100% de conformidade com os princípios da Constituição (sem vazamento de dados, isolamento de testes e dados sintéticos).

---

## Assumptions

- A lista de estudos é obtida a partir do endpoint já existente `GET /api/chapters/{chapter_id}/studies`.
- A filtragem e a ordenação ocorrem inteiramente no cliente (Vue 3 / Composition API), eliminando latência de rede.
- Os indicadores de seções preenchidas podem avaliar a presença de conteúdo nas propriedades do estudo ou no resumo prévio.
- O componente preserva a capacidade de alternar entre as 5 visualizações canônicas através do seletor existente.
