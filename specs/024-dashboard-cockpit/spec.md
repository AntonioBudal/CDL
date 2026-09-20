# Feature Specification: F07 — Dashboard 2.0 (Cockpit de Estudos e Hub de Navegação)

**Feature Branch**: `024-dashboard-cockpit`

**Created**: 2026-09-19

**Status**: Draft

**Input**: User description: "F07 — Dashboard 2.0: Hub de navegação e cockpit de retoma com blocos dinâmicos, conexões semânticas recentes e estudos para revisão (F07 do Roadmap 0.4)"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retomada Imediata do Trabalho Intelectual (Priority: P1) [MVP]

Como leitor e pesquisador do Caderno de Leitura, desejo abrir a aplicação e visualizar imediatamente os últimos livros e estudos nos quais trabalhei, com data de atualização relativa e atalho direto de 1 clique para continuar a leitura exatamente de onde parei.

**Why this priority**: É o valor central do Dashboard 2.0: transformar a tela inicial em um cockpit operacional de trabalho em vez de um relatório passivo, reduzindo o atrito cognitivo de navegação e permitindo a imersão imediata no estudo.

**Independent Test**: Com um acervo populado com estudos atualizados em diferentes momentos, abrir o Dashboard; verificar o bloco "Continuar Estudos" exibindo os itens ordenados cronologicamente por modificação recente; clicar em um estudo e constatar que a rota carrega o livro com a visualização correspondente e o estudo focado.

**Acceptance Scenarios**:

1. **Given** múltiplos estudos cadastrados com diferentes datas de alteração, **When** o leitor acessa o Dashboard, **Then** o bloco "Continuar Estudos" exibe os estudos mais recentemente atualizados com título do estudo, nome do livro e capítulo correspondente.
2. **Given** a lista de estudos recentes, **When** o leitor clica no botão "Continuar estudo", **Then** a aplicação navega diretamente para `/books/{bookId}?study={studyId}`, destacando o estudo sem passos intermediários.
3. **Given** um estudo que foi enviado para a lixeira (`deleted_at IS NOT NULL`), **When** o Dashboard é carregado, **Then** esse estudo não deve figurar no bloco de retoma.

---

### User Story 2 - Identificação de Estudos Sem Vínculos e Apoio à Sistematização (Priority: P2)

Como leitor que busca construir uma rede conectada de ideias, desejo identificar facilmente estudos que ainda não possuem relações semânticas ("estudos isolados/órfãos"), para que eu possa aprofundá-los, revisá-los ou conectá-los a outras obras do acervo.

**Why this priority**: Evita que reflexões e notas de leitura fiquem esquecidas em silos isolados, estimulando a síntese transversal e o enriquecimento do grafo de conhecimento estabelecido na F04.

**Independent Test**: Cadastrar estudos com e sem relações na tabela `study_relations`; acessar o Dashboard; constatar que o contador e o widget "Estudos para Conectar" listam com precisão apenas os estudos ativos sem nenhuma relação de entrada ou saída, permitindo clicar no estudo e abrir o modal de criação de relações.

**Acceptance Scenarios**:

1. **Given** estudos sem conexões ativas na tabela `study_relations`, **When** o Dashboard é gerado, **Then** o widget exibe a quantidade exata de estudos sem vínculos e uma lista selecionável com os estudos mais relevantes para integração.
2. **Given** um estudo órfão exibido no widget, **When** o usuário clica no atalho "Criar relação", **Then** o leitor é conduzido à tela do estudo com o modal de relações pronto para vincular.
3. **Given** que o usuário conecta um estudo a outro, **When** o Dashboard é recarregado, **Then** o contador de estudos sem vínculos diminui em 1 e o estudo deixa de figurar na lista de órfãos.

---

### User Story 3 - Conexões Semânticas Recentes e Pulso do Grafo (Priority: P3)

Como pesquisador, desejo acompanhar as relações conceituais recentemente estabelecidas entre estudos (ex.: *complementa*, *contradiz*, *depende de*), para ter uma visão dinâmica de como os conceitos dialogam entre si no acervo.

**Why this priority**: Reforça o pensamento relacional e interdisciplinar, tornando visíveis as pontes intelectuais mais novas criadas pelo leitor entre autores e obras distintas.

**Independent Test**: Criar novas relações semânticas com diferentes tipos canônicos; acessar o Dashboard; verificar o bloco "Conexões Recentes" exibindo os pares de estudos, os livros de origem/destino e o badge semântico colorido com o rótulo correto.

**Acceptance Scenarios**:

1. **Given** relações semânticas ativas no banco de dados, **When** o Dashboard é renderizado, **Then** o bloco "Conexões Recentes" lista as últimas relações criadas em ordem decrescente de data.
2. **Given** uma conexão entre o Estudo A e o Estudo B, **When** o card da conexão é exibido, **Then** ele apresenta o título de ambos os estudos, seus livros e o badge visual correspondente ao tipo semântico canônico.
3. **Given** que um dos estudos vinculados é movido para a lixeira, **When** o Dashboard é consultado, **Then** essa relação latente é omitida da lista de conexões ativas recentes.

---

### User Story 4 - Linha do Tempo e Panorama Topológico Integrado com Calibração de Temas (Priority: P4)

Como leitor, desejo visualizar um panorama agregado sóbrio e condensado do acervo (volume total de estudos, categorias ativas, densidade média do grafo), acessar o calendário/timeline da versão 0.3 sem lentidão de tela e conseguir discernir nitidamente os dias com atividade dos dias sem atividade no calendário de 12 meses em qualquer tema de cores ativo.

**Why this priority**: Garante continuidade às métricas analíticas estabelecidas na versão anterior, proporcionando orientação temporal e espacial de longo prazo de forma integrada ao novo cockpit, com acessibilidade visual e contraste calibrado em todos os temas.

**Independent Test**: Carregar o Dashboard com centenas de estudos distribuídos em vários meses; alternar entre temas clássico, escuro, sépia, solarizado e e-ink; constatar que em todos os temas as células com atividade do calendário destacam-se inequivocamente dos dias sem atividade por opacidade e contraste diferenciados, e que os blocos de resumo e o heatmap carregam em menos de 300ms.

**Acceptance Scenarios**:

1. **Given** o acervo geral com dados históricos, **When** o leitor rola até o bloco inferior do Dashboard, **Then** o heatmap de leitura e a timeline são renderizados com dados consolidados.
2. **Given** telas de smartphone (<768px), **When** o Dashboard é exibido, **Then** os blocos se empilham ordenadamente (Retomar Leitura no topo, seguido de Estudos para Conectar e Histórico), com todos os alvos de toque respeitando o mínimo de 44x44px.
3. **Given** qualquer tema alternativo ativo (ex.: escuro, sépia, solarizado, e-ink ou superclasses visuais), **When** o calendário de 12 meses é renderizado, **Then** as células sem atividade (`level-0`) possuem fundo atenuado/opacidade reduzida e as células com atividade (`level-1` a `level-3`) possuem contraste e intensidade marcantes, diferenciando-se com clareza imediata.

---

### Edge Cases

- **Acervo Vazio**: Quando o usuário instala o Caderno ou não possui livros/estudos, o Dashboard deve exibir um estado vazio acolhedor e informativo, orientando a importação do primeiro estudo ou cadastro de livro, sem erros de divisão por zero na densidade de grafo.
- **Acervo Sem Conexões (Fase Inicial)**: Se houver centenas de estudos mas nenhuma relação semântica criada, o bloco de "Conexões Recentes" não deve quebrar nem emitir erro 500; deve exibir um estado neutro convidando a conectar ideias.
- **Estudos Excluídos (Soft Delete)**: Estudos ou livros com `deleted_at IS NOT NULL` devem ser rigorosamente excluídos de todos os agregados, listas de retoma e conexões do Dashboard.
- **Falha de Conectividade ou Latência**: A requisição do resumo do dashboard deve retornar todo o pacote consolidado em um único payload atômico `GET /api/dashboard/summary`, evitando "waterfall" de chamadas e renderização piscante.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer o endpoint `GET /api/dashboard/summary` consolidando métricas gerais, lista de estudos recentes para retoma, estudos sem vínculos e conexões recentes em uma única chamada atômica.
- **FR-002**: O bloco "Continuar Estudos" DEVE listar os últimos estudos atualizados (`updated_at DESC`), trazendo título, identificador, livro (`book_id`, `book_title`), capítulo (`chapter_id`, `chapter_title`), status de leitura (`reading_status`) e tempo relativo.
- **FR-003**: O endpoint DEVE identificar com precisão os estudos órfãos ativos (estudos que não aparecem nem como `source_study_id` nem como `target_study_id` em `study_relations`), fornecendo a contagem total e uma amostra prioritária para enriquecimento.
- **FR-004**: O bloco "Conexões Recentes" DEVE listar as últimas relações semânticas ativas criadas no acervo (`created_at DESC`), incluindo os identificadores, títulos e livros dos estudos de origem e destino, além do `relation_type` canônico.
- **FR-005**: O resumo topológico DEVE calcular métricas reais do acervo: total de livros ativos, total de estudos ativos, total de relações semânticas ativas e total de categorias ativas, sem nenhuma métrica artificial ou inventada.
- **FR-006**: Todos os dados exibidos no Dashboard DEVEM ignorar registros marcados com `deleted_at IS NOT NULL` (conformidade estrita com a política de soft delete e lixeira).
- **FR-007**: A interface DEVE disponibilizar navegação direta em 1 clique a partir dos cards de estudo recente para a tela de leitura correspondente, preservando o foco visual.
- **FR-008**: O layout do Dashboard DEVE ser responsivo: grade balanceada de 2 a 3 colunas em desktop (>=1024px) e organização em fluxo móvel estruturado e condensado em celulares e telas pequenas (<768px).
- **FR-009**: Todos os botões, links de estudo e gatilhos de ação DEVEM possuir áreas mínimas de toque de 44x44px em conformidade com as diretrizes de ergonomia móvel.
- **FR-010**: A rota inicial padrão (`/`) da aplicação DEVE abrir o Dashboard 2.0 (Cockpit de Estudos), disponibilizando uma opção na Central de Configurações para que o leitor possa alternar a rota padrão para o Acervo de Livros (`/books`), caso prefira.
- **FR-011**: O layout do Dashboard DEVE possuir uma estrutura balanceada por padrão, permitindo que cada bloco (Retomar Estudos, Estudos para Conectar, Conexões Recentes, Linha do Tempo / Calendário) possa ser colapsado ou ocultado individualmente, com preferência persistida no `localStorage`.
- **FR-012**: O bloco "Continuar Estudos" DEVE exibir por padrão os 5 estudos mais recentemente atualizados (`updated_at DESC`), com botão de ação rápida "Ver mais" para expandir a lista para até 10 estudos.
- **FR-013**: O componente de Mapa de Calor de 12 Meses (`HeatmapCalendar`) DEVE calibrar opacidades, bordas e níveis de preenchimento em todos os temas suportados (`clássico`, `dark`, `sepia`, `solarized`, `e-ink` e superclasses de interface), garantindo contraste inequívoco e nítida distinção visual entre dias com atividade (`level-1` a `level-3`) e dias sem atividade (`level-0`).
- **FR-014**: Em resoluções móveis (<768px), o Dashboard DEVE adotar uma hierarquia visual vertical condensada e organizada:
  1. Topo: barra de indicadores métricos compacta em grade 2x2 ou fita de rolagem horizontal sutil, eliminando cartões volumosos que empurram o conteúdo principal para fora da tela.
  2. Primeiro campo de visão: bloco "Continuar Estudos" em destaque prioritário, com cartões de estudo ocupando 100% da largura útil com tipografia legível e alvos táteis confortáveis.
  3. Seções secundárias ("Estudos para Conectar" e "Conexões Recentes"): organizadas em abas comutáveis (*tabs*) ou seções expansíveis compactas (*accordions*), evitando rolagem vertical excessiva (*scroll fatigue*).
  4. Bloco inferior: Calendário de atividades com modo de período compacto ativado por padrão e rolagem horizontal suave (*momentum scrolling*).
- **FR-015**: Em smartphones e dispositivos táteis (<768px), o Dashboard DEVE assegurar ergonomia móvel rigorosa:
  1. Blindagem total contra rolagem horizontal involuntária da página principal (`overflow-x: hidden` no contêiner da visualização com contenção estrita de largura).
  2. Barra ou fita de navegação rápida por chips aderentes (*sticky navigation chips*) permitindo saltar diretamente entre as seções ("Retomar", "Conectar", "Histórico").
  3. Respeito à zona natural do polegar (*thumb zone*), margens laterais mínimas de 16px e alvos de toque nunca inferiores a 44x44px.

---

### Key Entities *(include if feature involves data)*

- **DashboardSummaryResponse**: Schema unificado que agrupa:
  - `stats`: Totais gerais (livros, capítulos, estudos, relações, categorias).
  - `recent_studies`: Lista de `RecentStudyActivityItem` (estudos para retoma rápida).
  - `unlinked_studies`: Amostra e contagem de estudos sem conexões ativas.
  - `latest_relations`: Lista de `RecentRelationItem` com metadados semânticos completos.
  - `timeline_preview`: Dados de frequência temporal para o heatmap.
- **RecentStudyActivityItem**: Representa a atividade recente de um estudo:
  - `study_id`: ID numérico.
  - `title`: Título do estudo.
  - `book_id` e `book_title`: Dados do livro pai.
  - `chapter_id` e `chapter_title`: Dados do capítulo pai.
  - `reading_status`: Estado no ciclo de maturação (`rascunho`, `em_estudo`, `revisado`, `concluido`).
  - `updated_at`: Timestamp UTC da última modificação.
- **RecentRelationItem**: Representa uma conexão recém-criada no grafo:
  - `relation_id`: ID da relação.
  - `relation_type`: Tipo semântico canônico da F04.
  - `source_study_id`, `source_study_title`, `source_book_title`: Origem.
  - `target_study_id`, `target_study_title`, `target_book_title`: Destino.
  - `created_at`: Data de criação do vínculo.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O endpoint `GET /api/dashboard/summary` responde em menos de 300ms no backend para bases com mais de 2.000 estudos e 1.000 relações.
- **SC-002**: O leitor consegue retomar a leitura de um estudo recente a partir do Dashboard com exatamente 1 clique do mouse ou 1 toque no celular.
- **SC-003**: 100% dos dados, contagens e agrupamentos apresentados são derivados de registros reais do banco SQLite local, com zero métricas inventadas ou estimativas opacas.
- **SC-004**: Todas as metas de acessibilidade são cumpridas: marcos estruturais com títulos `<h2>`, navegação lógica por Tab e alvos de toque mínimos de 44x44px em 100% dos elementos interativos.
- **SC-005**: 100% dos testes automatizados de backend e frontend executam com aprovação, sem tocar no banco ativo `backend/data/caderno.db`.
- **SC-006**: Em todos os temas e esquemas de cores disponíveis, o contraste visual entre células com atividade (`level-1` a `level-3`) e células sem atividade (`level-0`) no calendário de 12 meses atende a critérios nítidos de legibilidade e diferenciação visual imediata.
- **SC-007**: Em resoluções móveis de 360px a 412px (smartphones), o Dashboard é plenamente navegável sem quebras visuais, sem sobreposição de conteúdo e sem rolagem horizontal involuntária da página inteira.

---

## Assumptions

- O banco de dados já possui as migrações aplicadas até a revisão `0009` (incluindo `studies.reading_status` e tabelas `study_relations` e `canvas_frames`).
- Nenhuma alteração estrutural no banco de dados (DDL) é necessária para esta feature; as informações necessárias já existem nas tabelas relacionais do sistema e são consolidadas via queries SQL otimizadas.
- O Dashboard 2.0 não substitui o Acervo de Livros (`/books`), mas oferece uma porta de entrada panorâmica e operacional que potencializa o fluxo de estudo.
- Não serão implementados contadores de gamificação, streaks diários obrigatórios ou sistemas de pontuação que divirjam do rigor intelectual e sobriedade do projeto.
