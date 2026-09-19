# Feature Specification: Dashboard de Leitura com Calendário e Timeline

**Feature Branch**: `013-dashboard-calendario-timeline`  
**Created**: 2026-09-19  
**Status**: Ready for Planning  
**Input**: User description: "T06: Dashboard de leitura com visualização de calendário e timeline"

---

## Clarifications

### Session 2026-09-19
- **Q1 (Definição de Atividade Contabilizada)**: O que deve ser considerado um "ponto de atividade" no calendário/mapa de calor e nas métricas de leitura?  
  → **A: Opção B** — Cada interação explícita de conteúdo pontua como atividade de estudo/leitura: criação de novos livros no acervo, criação de novos estudos e edições salvas de anotações.
- **Q2 (Alcance Temporal do Mapa de Calor)**: Qual horizonte temporal deve ser exibido por padrão no mapa de calor em diferentes dispositivos?  
  → **A: Opção C** — Recorte responsivo adaptativo: exibe os últimos 12 meses (~52 semanas) em telas de desktop e os últimos 3 a 6 meses em telas móveis/smartphones, preservando legibilidade e densidade tátil sem exigir rolagem horizontal excessiva, com controle para expandir a visão anual completa quando desejado.
- **Q3 (Impacto da Lixeira no Histórico)**: Como itens enviados para a lixeira devem impactar as métricas e o mapa de calor?  
  → **A: Opção A** — Ocultação total e imediata: livros ou estudos enviados para a lixeira deixam instantaneamente de pontuar no mapa de calor, na contagem de dias ativos e na timeline; ao restaurar o item da lixeira, seus eventos históricos retornam ao cálculo de forma consistente e íntegra.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visão Geral de Produtividade e Métricas Principais (Priority: P1) 🎯 MVP

Como leitor mantendo um caderno de estudos e leituras, quero acessar uma tela central de Dashboard com estatísticas claras do meu progresso (livros lidos/cadastrados, estudos concluídos, dias ativos e sequência de hábitos), para acompanhar minha evolução de leitura sem depender de anotações externas ou estimativas manuais.

**Why this priority**: Estabelece o núcleo de valor do painel de produtividade. Mesmo sem o mapa de calor complexo ou a timeline detalhada, o usuário obtém imediatamente uma síntese quantitativa confiável do seu volume e ritmo de leitura.

**Independent Test**: Pode ser testado acessando a rota `/dashboard` e verificando que cartões de métricas (total de livros ativos, total de estudos, média de estudos por livro, total de dias ativos e sequência atual de dias consecutivos) são exibidos com precisão matemática calculada a partir dos dados do acervo ativo.

**Acceptance Scenarios**:
1. **Given** um usuário com livros e estudos cadastrados no acervo ativo, **When** navega para o Dashboard, **Then** visualiza cartões destacados com total de livros, total de estudos registrados, dias totais com atividade de estudo (cadastro de livro, criação de estudo ou edição de anotação) e a sequência atual de dias consecutivos.
2. **Given** um usuário recém-instalado ou com acervo vazio, **When** abre o Dashboard pela primeira vez, **Then** é recepcionado por um estado vazio acolhedor e informativo, com orientações e botão direto para importar ou cadastrar o primeiro livro, sem erros ou contagens quebradas (`NaN` ou `null`).
3. **Given** o usuário recarregando a página, alternando temas ou navegando entre abas, **When** visualiza o Dashboard, **Then** nenhuma atividade artificial é gerada e as métricas mantêm estabilidade e fidelidade estrita.

---

### User Story 2 - Mapa de Calor Responsivo e Frequência em Calendário de Leitura (Priority: P2)

Como leitor que busca consistência nos estudos, quero visualizar um mapa de calor em formato de calendário (semanas e dias) mostrando a intensidade da minha atividade de leitura em cada data, com layout adaptativo para celular e computador, para que eu possa identificar períodos de alta produtividade, pausas e manter meu hábito de leitura ativo.

**Why this priority**: O mapa de calor visual é o elemento central de engajamento do leitor, permitindo uma percepção intuitiva e imediata de constância temporal sem exigir a leitura manual de tabelas de dados.

**Independent Test**: Pode ser testado gerando livros e estudos com diferentes datas e comprovando que o calendário plota cada dia no bloco correspondente com escala cromática de 4 níveis de intensidade (sem atividade, baixa, média, alta), tooltips com a data local e contagem de atividades, recorte adaptativo (12 meses em desktop, 3 a 6 meses em mobile) e interação de clique para filtrar.

**Acceptance Scenarios**:
1. **Given** o mapa de calor do Dashboard em tela desktop, **When** exibido, **Then** apresenta uma grade de 12 meses (~52 semanas) organizada por dias da semana, onde cada célula reflete a densidade de atividades de leitura naquela data específica segundo o fuso horário local do leitor.
2. **Given** o mapa de calor do Dashboard em smartphone ou tela estreita (< 640px), **When** exibido, **Then** apresenta o recorte adaptativo dos últimos 3 a 6 meses com opção de alternar/expandir, garantindo toque confortável e leitura nítida de meses e dias.
3. **Given** células do calendário com diferentes volumes de estudo/cadastro, **When** o usuário passa o cursor (ou toca no mobile) sobre um dia específico, **Then** uma dica de contexto (tooltip) informa a data formatada em português e a quantidade exata de eventos realizados (ex.: "3 atividades em 14 de setembro de 2026").
4. **Given** o usuário clicando em um dia específico do calendário, **When** aciona a célula, **Then** a timeline de atividade abaixo é instantaneamente filtrada para exibir apenas os registros e anotações pertinentes àquele dia selecionado, com opção evidente de limpar o filtro.

---

### User Story 3 - Linha do Tempo Cronológica de Atividades Recentes (Priority: P3)

Como leitor navegando pelo meu histórico, quero uma timeline cronológica reversa detalhando as ações de estudo recentes (criação de estudo, atualizações de anotações, cadastros de livros, capítulo associado), com atalhos diretos para leitura, para retomar facilmente de onde parei.

**Why this priority**: Conecta as métricas abstratas do Dashboard ao conteúdo real das leituras, fornecendo contexto e atalhos rápidos para navegação no acervo.

**Independent Test**: Pode ser testado realizando adições de livros, adições de estudos e edições de anotações, verificando que a lista cronológica exibe os eventos em ordem decrescente, com marcadores visuais de tempo relativo ("hoje às 10:15", "ontem", "há 3 dias"), ícone do tipo de atividade, título do livro/estudo e link navegável direto para a leitura do estudo.

**Acceptance Scenarios**:
1. **Given** a timeline de atividades recentes, **When** carregada, **Then** apresenta as atividades mais recentes em ordem cronológica decrescente, exibindo tipo da ação (criação de livro, criação de estudo ou edição de nota), nome do livro, capítulo, título do estudo e momento da atividade.
2. **Given** um item na timeline, **When** o usuário clica sobre ele, **Then** é redirecionado diretamente para a visualização daquele estudo no respectivo livro.
3. **Given** um livro ou estudo que foi movido para a lixeira, **When** a timeline e o mapa de calor são consultados, **Then** o item excluído deixa de ser exibido imediatamente e não polui o histórico nem o heatmap até ser eventualmente restaurado.
4. **Given** um filtro aplicado via calendário ou busca textual, **When** o leitor seleciona um critério, **Then** a timeline atualiza imediatamente sua listagem com indicação clara do filtro ativo e botão para restaurar a visão completa.

---

### Edge Cases

- **Ausência de Atividade Histórica:** Usuários novos ou acervos sem nenhum estudo concluído devem ver um painel informativo com métricas zeradas (`0 livros`, `0 estudos`, `0 dias`), incentivo à leitura e links diretos para iniciar.
- **Virada de Fuso Horário e Horário de Verão:** Registros gravados em instantes UTC universais devem ser convertidos deterministicamente para o dia civil local do leitor, evitando que um estudo feito às 23:30 apareça no dia seguinte.
- **Retries de Conexão e Recarregamento Frequente:** Múltiplas requisições idênticas ou recargas contínuas da página (F5) não podem incrementar contadores nem simular sessões de estudo falsas.
- **Exclusão e Restauração em Lixeira (Soft Delete):** Itens enviados à lixeira são imediatamente ocultados das métricas e do heatmap. Se restaurados, seus eventos passados retornam com exatidão matemática aos cálculos históricos.
- **Dispositivos com Tela Ultra-Estreita (Mobile < 360px):** O mapa de calor adaptativo deve manter acessibilidade por toque (touch targets mínimos adequados) sem truncar legendas de meses e dias da semana.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer uma tela dedicada de Dashboard acessível a partir da navegação principal da interface (rota `/dashboard`).
- **FR-002**: O sistema DEVE calcular e exibir métricas essenciais do acervo ativo: total de livros ativos, total de estudos cadastrados, total de dias distintos com atividade de estudo/leitura registrada e a sequência atual de dias consecutivos de atividade (streak).
- **FR-003**: O sistema DEVE considerar como evento de atividade de leitura: a criação de novos livros, a criação de novos estudos e a edição salva de anotações no acervo ativo.
- **FR-004**: O sistema DEVE exibir um mapa de calor visual (heatmap) em grade de dias e semanas, indicando a frequência e o volume de atividades de leitura realizadas ao longo do tempo.
- **FR-005**: O mapa de calor DEVE adotar layout responsivo adaptativo: exibindo os últimos 12 meses no desktop e os últimos 3 a 6 meses em telas móveis/smartphones, com controle para expandir a visão anual completa.
- **FR-006**: O mapa de calor DEVE utilizar uma escala perceptual de intensidade com no mínimo 4 níveis visuais (sem atividade, baixa, média, alta frequência), harmonizada com os temas visuais e as Superclasses de Interface da aplicação.
- **FR-007**: As células do mapa de calor DEVEM apresentar rótulos acessíveis e dicas contextuais (tooltips) contendo a data formatada em português e o número exato de atividades no dia.
- **FR-008**: O usuário DEVE poder clicar em qualquer dia do calendário para filtrar a timeline de atividades pelo dia selecionado, bem como desativar o filtro com um clique claro.
- **FR-009**: O sistema DEVE listar uma timeline cronológica reversa das atividades recentes de estudo, incluindo tipo de ação, título do estudo, livro, capítulo e carimbo de tempo formatado de forma relativa/absoluta.
- **FR-010**: Cada entrada na timeline DEVE conter link navegável para abrir a leitura do estudo ou livro correspondente.
- **FR-011**: Todos os cálculos de agregação por data DEVEM utilizar instantes temporais canônicos armazenados em UTC e convertidos para o fuso horário local do navegador do usuário.
- **FR-012**: Apenas ações autênticas de leitura/estudo (criação de livro, criação de estudo e edição de anotação) DEVEM ser computadas como atividade; navegação, recarregamento e alternância de temas NUNCA devem gerar registros de atividade artificial.
- **FR-013**: O sistema DEVE ocultar da contagem ativa, do heatmap e da timeline imediata os estudos e livros presentes na lixeira (*soft deleted*), devolvendo os eventos retroativamente apenas mediante restauração do item.
- **FR-014**: O sistema DEVE apresentar estados vazios amigáveis e explicativos quando não houver atividade registrada no período.
- **FR-015**: A interface do Dashboard DEVE ser totalmente responsiva, funcionando com conforto tanto em monitores de mesa quanto em celulares de tela pequena.
- **FR-016**: O Dashboard DEVE respeitar a Superclasse de Interface ativa, herdando suas físicas de elevação, microinterações e estilos visuais sem conflito.
- **FR-017**: A fonte de texto global e o tema de cores selecionados em Ajustes DEVEM ser propagados integralmente a todos os números, títulos, tooltips e cartões do Dashboard.

### Key Entities *(include if feature involves data)*

- **Resumo de Produtividade (Dashboard Summary)**: Estrutura agregada com totais de livros, estudos, dias com leitura, sequência atual de dias consecutivos e média de estudos por livro.
- **Ponto de Atividade Diária (Daily Activity Point)**: Registro de agregação por dia civil (data local, contagem de atividades concluídas, nível de intensidade no mapa de calor).
- **Entrada da Timeline (Timeline Entry)**: Registro histórico de um evento de estudo ou livro com identificador da entidade, tipo de evento (criação de livro, criação de estudo, edição de nota), título do livro, título do estudo, nome do capítulo, momento do evento e estado de visibilidade no acervo.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue visualizar suas estatísticas consolidadas de leitura em menos de 1 segundo após abrir a tela de Dashboard.
- **SC-002**: 100% dos livros e estudos criados ou atualizados no acervo ativo são refletidos com exatidão matemática nas contagens e no mapa de calor.
- **SC-003**: 0% de atividade fantasma é gerada por recargas de página, navegação entre abas ou troca de configurações estéticas.
- **SC-004**: O mapa de calor permanece legível e navegável sem quebras visuais em telas de largura a partir de 320px (mobile), apresentando o recorte adaptativo de 3 a 6 meses.
- **SC-005**: Ao clicar em uma célula de data no mapa de calor, a timeline filtra as ocorrências correspondentes em menos de 100ms.
- **SC-006**: Ao enviar itens para a lixeira, os totais e as células do mapa de calor são atualizados de imediato, e ao restaurar, a pontuação histórica retorna de forma fidedigna.

---

## Assumptions

- A aplicação continuará utilizando dados locais salvos no banco SQLite existente, sem requisições a serviços externos de telemetria.
- Os eventos primários de atividade baseiam-se nos carimbos temporais de criação e última modificação de livros e estudos já existentes no modelo de dados (`created_at` e `updated_at`).
- Sessões de cronômetro ou leitura cronometrada em tempo real permanecem fora do escopo desta feature (conforme estipulado no Roadmap 0.3), mantendo o foco em entregas de estudos e anotações.
- As preferências de tema, fonte e superclasse definidas em Ajustes são herdadas de forma nativa pelos componentes do Dashboard via variáveis CSS globais consolidadas na Feature 012.
