# Feature Specification: F05 — Agrupamento Visual

**Feature Branch**: `023-agrupamento-visual`  
**Created**: 2026-09-19  
**Status**: Draft  
**Input**: User description: "F05 — Agrupamento Visual: Projeções modulares por categoria, hierarquia, livro, status de leitura, data e molduras no Canvas"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Agrupamento Reativo em Grade e Lista por Critérios Estruturais (Priority: P1) [MVP]

O leitor deseja reorganizar dinamicamente a apresentação visual dos estudos em visualizações de Grade e Lista através de critérios estruturais imediatos (por Capítulo, por Categoria e por Data de Estudo), sem duplicar dados, sem alterar a estrutura física dos livros e capítulos e com restauração instantânea da visualização padrão.

**Why this priority**: Estabelece a capacidade central de decomposição e reagrupamento conceitual no acervo e livro, provendo valor imediato com esforço focado exclusivamente na projeção visual sem depender de novas tabelas de banco complexas.

**Independent Test**: Abrir um livro com múltiplos estudos distribuídos em capítulos e categorias; acionar o seletor de agrupamento e escolher "Por Categoria"; constatar que os estudos são instantaneamente reparticionados em seções visuais intituladas com suas respectivas categorias (incluindo uma seção "Sem Categoria"), permitindo colapsar e expandir seções e retornar a "Por Capítulo" a qualquer momento.

**Acceptance Scenarios**:

1. **Given** um livro com estudos associados a diferentes capítulos e categorias, **When** o usuário seleciona o agrupador "Por Categoria" no seletor de visualização, **Then** a interface reorganiza os cartões em blocos/raias agrupados pelo nome de cada categoria em ordem alfabética, agrupando estudos sem categoria sob uma seção explícita "Sem Categoria".
2. **Given** a visualização de estudos agrupada por qualquer critério, **When** o usuário clica ou toca no cabeçalho de um grupo, **Then** o conteúdo daquele grupo colapsa ou se expande suavemente, preservando o estado colapsado durante a navegação daquela sessão.
3. **Given** um agrupamento ativo por "Data de Estudo", **When** o leitor visualiza os grupos, **Then** os estudos são particionados em seções temporais cronológicas relativas ("Hoje", "Esta Semana", "Este Mês", "Mais Antigos").
4. **Given** qualquer agrupamento alternativo ativo, **When** o leitor seleciona "Por Capítulo", **Then** a apresentação retorna à ordenação canônica original dos capítulos do livro.

---

### User Story 2 - Ciclo de Maturação e Agrupamento por Status de Leitura (Priority: P2)

O leitor deseja registrar o estado de maturação e progresso intelectual de cada estudo através de um ciclo editorial de status de leitura, podendo agrupar os estudos sob essas fases para identificar rapidamente notas em rascunho, estudos em aprofundamento e conclusões consolidadas.

**Why this priority**: Enriquece a prática de estudo ativo e fichamento crítico, permitindo ao leitor usar o caderno como um fluxo de trabalho progressivo de síntese e maturação do conhecimento.

**Independent Test**: Atribuir status de leitura a três estudos de um livro; escolher o agrupamento "Por Status de Leitura"; verificar a repartição em raias correspondentes aos estados de maturação e alterar o status de um estudo diretamente no cartão, observando sua transição suave para a raia correspondente.

**Acceptance Scenarios**:

1. **Given** um estudo exibido na visualização de leitura ou em cartão de grade, **When** o usuário altera o status de leitura do estudo, **Then** o novo status é persistido de forma atômica e atualizado em tempo real na interface.
2. **Given** a seleção do agrupamento "Por Status de Leitura", **When** a tela é renderizada, **Then** os estudos são particionados em raias sequenciais correspondentes ao ciclo editorial oficial de 4 estados: "Rascunho" (`rascunho`, valor padrão de entrada), "Em Estudo" (`em_estudo`), "Revisado" (`revisado`) e "Concluído" (`concluido`).
3. **Given** um estudo em uma raia de status, **When** o usuário altera seu status de leitura, **Then** o estudo é transferido para o grupo correspondente sem exigir recarregamento da página.

---

### User Story 3 - Molduras Espaciais Manuais no Canvas 2D (Priority: P3)

No Canvas livre bidimensional (F03), o leitor deseja criar caixas/molduras visuais delimitadoras (*frames*) nomeadas e coloridas para agrupar estudos espacialmente por afinidade temática livre, movendo blocos conceituais inteiros pelo palco do mundo sem romper a integridade hierárquica.

**Why this priority**: Concretiza o pensamento espacial no Canvas livre, viabilizando sínteses visuais ricas, zoneamento conceitual e manipulação ergonômica de grandes conjuntos de anotações.

**Independent Test**: Abrir o Canvas de um livro; acionar a ferramenta de nova moldura; desenhar um retângulo delimitando dois estudos e nomeá-lo "Axiomas Fundamentais"; arrastar a moldura e comprovar que os cartões e a moldura mantêm sincronização espacial e persistência após recarregamento.

**Acceptance Scenarios**:

1. **Given** o Canvas 2D de um livro ativo, **When** o usuário aciona a ferramenta "Adicionar Moldura" e clica no palco, **Then** uma moldura retangular visual com título editável e seletor de cor sutil é inserida naquelas coordenadas.
2. **Given** uma moldura que envolve espacialmente um ou mais cartões de estudos, **When** o leitor arrasta a moldura pelo Canvas, **Then** todos os cartões de estudos geometricamente contidos no seu interior deslocam-se de forma solidária em bloco mantendo suas posições relativas intactas, enquanto o arrasto de um cartão individual no interior move apenas aquele cartão.
3. **Given** o Canvas 2D com coordenadas manuais personalizadas, **When** o usuário aciona um agrupador automático (por Categoria, por Status ou por Data), **Then** os nós são organizados em raias/colunas espaciais calculadas temporariamente de forma não-destrutiva e, ao retornar para o modo "Livre / Manual", todas as coordenadas espaciais manuais originais são restauradas exatamente como estavam no banco de dados.
4. **Given** uma moldura existente, **When** o usuário altera seu título, cor ou a exclui, **Then** as alterações são persistidas no banco de dados e os estudos contidos permanecem intactos sem qualquer perda de dados.

---

### User Story 4 - Ergonomia Móvel, Cabeçalhos Aderentes e Acessibilidade (Priority: P4)

O leitor em dispositivos móveis ou navegando exclusivamente por teclado deseja consultar estudos agrupados com cabeçalhos aderentes (*sticky headers*), contadores claros de itens por grupo, alvos de toque confortáveis (mínimo 44x44px) e suporte pleno a leitores de tela WAI-ARIA.

**Why this priority**: Garante que o particionamento visual de centenas de estudos permaneça acessível, leve e confortável em qualquer dispositivo, tela tátil ou tecnologia assistiva.

**Independent Test**: Emular tela de smartphone de 375px de largura; selecionar o agrupamento por categoria; navegar verticalmente observando a fixação aderente dos cabeçalhos de grupo no topo da viewport e colapsar seções inteiras com toque confortável ou via tecla Enter/Espaço.

**Acceptance Scenarios**:

1. **Given** uma lista ou grade com dezenas de estudos em múltiplos grupos no smartphone, **When** o usuário rola verticalmente a página, **Then** o cabeçalho do grupo visível permanece fixo no topo (*sticky header*) até que o próximo grupo o substitua, mantendo o contexto de leitura claro.
2. **Given** a navegação por teclado, **When** o usuário foca no cabeçalho de um grupo e pressiona Enter ou Espaço, **Then** a seção de estudos daquele grupo expande ou colapsa alternadamente, atualizando o atributo `aria-expanded`.
3. **Given** telas sensíveis ao toque, **When** botões de colapso, seletores de agrupamento e menus de status são acionados, **Then** todos possuem áreas de toque ativas com dimensões mínimas de 44x44px.

---

### Edge Cases

- **Estudo sem Categoria ou Metadados:** Estudos sem categoria associada ou sem capítulo são obrigatoriamente reunidos sob uma raia de fallback intitulada "Sem Categoria" ou "Não Classificado", nunca sendo omitidos nem gerando seções vazias.
- **Transição de Agrupamento com Seleção Ativa:** Se o usuário tiver um estudo selecionado/aberto ao alterar o critério de agrupamento, a visualização localiza, rola e mantém o estudo em foco aberto na sua nova seção.
- **Livro Vazio ou Sem Estudos:** A interface exibe estado neutro informativo sem erros de execução de agrupamento.
- **Redimensionamento Extremo de Janela:** Seções e raias adaptam-se de colunas lado a lado no desktop amplo para fluxo vertical contínuo em larguras inferiores a 768px.
- **Exclusão de Estudo em Grupo:** Se um estudo for enviado para a lixeira enquanto visualizado em um grupo, a contagem do cabeçalho daquele grupo é decrementada em tempo real e a seção é removida caso fique vazia.
- **Moldura Vazia no Canvas:** Molduras manuais podem existir vazias sem estudos no interior, servindo como marcadores de intenção e zoneamento futuro.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um seletor unificado de agrupamento (*GroupBySelector*) integrado às barras de controle de visualização de estudos.
- **FR-002**: O sistema DEVE suportar os seguintes critérios fundamentais de agrupamento no acervo e livro:
  - `chapter`: Agrupamento por capítulo (ordenação canônica padrão).
  - `status`: Agrupamento por estado de maturação intelectual do estudo.
  - `category`: Agrupamento por taxonomia de categoria temática.
  - `date`: Agrupamento cronológico relativo por data de criação/estudo (Hoje, Esta Semana, Este Mês, Anteriores).
  - `manual`: Agrupamento livre espacial por molduras (*frames*) no Canvas 2D.
- **FR-003**: O particionamento visual de estudos NÃO DEVE duplicar registros na memória, NÃO DEVE alterar chaves primárias, NÃO DEVE modificar relacionamentos de capítulos e NÃO DEVE executar mutações no banco de dados para agrupamentos em tempo de exibição.
- **FR-004**: Cada seção agrupada DEVE exibir um cabeçalho descritivo com o título do grupo, um contador numérico com a quantidade de estudos contidos e um controle interativo de colapso/expansão.
- **FR-005**: O sistema DEVE persistir o critério de agrupamento selecionado pelo usuário no navegador (`localStorage`), restaurando-o automaticamente ao reabrir a obra ou a visualização correspondente.
- **FR-006**: O modelo de dados do estudo DEVE incorporar o campo `reading_status` como atributo persistido no banco de dados SQLite, com valor padrão e restrição de domínio canônico.
- **FR-007**: O sistema DEVE prover endpoint REST dedicado para atualização rápida e atômica do status de maturação de um estudo (`PATCH /api/studies/{id}/status`), validando concorrência otimista.
- **FR-008**: O sistema DEVE criar e gerenciar a tabela `canvas_frames` para persistência das molduras manuais retangulares associadas ao Canvas de um livro (`id`, `book_id`, `title`, `color`, `pos_x`, `pos_y`, `width`, `height`), com exclusão em cascata quando o livro for expurgado.
- **FR-009**: O sistema DEVE fornecer endpoints REST para listagem, criação, atualização e remoção transacional de molduras manuais do Canvas (`GET/POST /api/books/{id}/canvas/frames` e `PATCH/DELETE /api/canvas/frames/{id}`).
- **FR-010**: No Canvas 2D, as molduras manuais DEVEM ser renderizadas com z-index inferior aos cartões de estudo e superior ao fundo quadriculado, permitindo identificação visual clara de contenção.
- **FR-011**: Em dispositivos móveis (largura de tela inferior a 768px), os cabeçalhos de grupo DEVEM comportar-se com fixação aderente (*sticky position*) no topo da área visível durante a rolagem vertical.
- **FR-012**: Todos os elementos acionáveis de agrupamento (botões de cabeçalho, seletores e itens de menu) DEVEM possuir dimensões mínimas de área de toque de 44x44px.
- **FR-013**: As seções de grupo DEVEM utilizar estrutura semântica HTML (`<section>`) com `role="region"` ou cabeçalhos semânticos associados via `aria-labelledby`, comunicando o estado expandido/colapsado através de `aria-expanded`.
- **FR-014**: Nenhuma operação de agrupamento ou criação de molduras pode ler, modificar ou depender de dados externos ao acervo pessoal local, preservando estritamente os princípios de soberania e privacidade da Constituição do projeto.

---

### Key Entities *(include if feature involves data)*

- **Study.reading_status**: Atributo textual adicionado à entidade `Study` que registra o estado de maturação intelectual do estudo no caderno pessoal.
- **CanvasFrame**: Entidade relacional que representa uma moldura delimitadora espacial no Canvas 2D de um livro. Possui atributos `id`, `book_id` (chave estrangeira com cascata), `title` (rótulo descritivo), `color` (tag visual de destaque), `pos_x`, `pos_y`, `width` e `height` (coordenadas e geometria bidimensional finita no espaço do mundo).
- **StudyGroup**: Estrutura de dados efêmera em memória no cliente frontend representando um agrupamento projetado de estudos, contendo `id`, `title`, `count`, `is_collapsed` e a lista ordenada de estudos pertencentes.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue alternar o critério de agrupamento de um livro com mais de 50 estudos e visualizar a apresentação reorganizada em menos de 100 milissegundos sem congelamento visual da interface.
- **SC-002**: 100% dos estudos de um livro são mantidos e visíveis ao alternar entre quaisquer critérios de agrupamento (zero perda ou ocultação involuntária de registros).
- **SC-003**: Alterar o status de leitura de um estudo a partir do cartão atualiza a raia correspondente e persiste no banco de dados local com confirmação em menos de 200 milissegundos.
- **SC-004**: No Canvas 2D, a criação e movimentação de molduras retangulares opera a 60fps constantes sem causar instabilidade no viewport infinito.
- **SC-005**: 100% dos botões de controle de agrupamento e cabeçalhos de seção possuem área de toque mínima comprovada de 44x44px em resoluções móveis.
- **SC-006**: A totalidade dos testes automatizados de backend e frontend roda exclusivamente contra bancos descartáveis em memória/temporários (`tmp_path`), garantindo conformidade absoluta com o Artigo II da Constituição do projeto.

---

## Assumptions

- O agrupamento dinâmico em Grade e Lista atua prioritariamente sobre os estudos carregados no contexto do livro ou biblioteca ativa em memória, garantindo agilidade e responsividade imediata sem requisições excessivas ao servidor local.
- O campo `reading_status` utilizará valores textuais padronizados em caixa baixa (*snake_case*) no banco de dados, com tradução amigável nos componentes de interface.
- A exclusão de uma moldura (*frame*) no Canvas 2D jamais exclui os estudos localizados dentro dela; apenas o elemento delimitador visual é removido.
- A ordenação padrão inicial de qualquer livro permanece sendo por capítulo canônico (`chapter`), preservando a linearidade editorial original da obra para novos usuários.
