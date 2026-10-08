# Feature Specification: Sessões Estruturadas de Estudo e Auditoria de Aprendizado (F 0.7.14)

**Feature Branch**: `063-sessoes-estudo`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: "/speckit-specify F.0.7.14"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Início e Execução de Sessão Imersiva de Estudo (Priority: P1)

O leitor deseja transformar o processo de revisão em um bloco delimitado de aprendizado focado. A partir da Central de Revisão ou da visualização de um livro específico, o leitor clica em "Iniciar Sessão de Estudo", escolhe o escopo desejado (Sessão Rápida de 10 itens, Sessão por Livro/Capítulo ou Revisão Completa) e é conduzido a uma interface imersiva de tela limpa, sem distrações de menus laterais, com barra de progresso horizontal e apresentação sequencial dos cartões de recordação ativa (perguntas, oclusões e trechos-chave).

**Why this priority**: É o cerne da funcionalidade (MVP independente). Permite ao leitor ter uma experiência delimitada de estudo com início, meio e fim sem dispersão cognitiva.

**Independent Test**: Pode ser testado iniciando uma sessão de 5 a 10 itens a partir da interface, respondendo aos cartões sequencialmente com transição de progresso até o último item.

**Acceptance Scenarios**:

1. **Given** que o leitor possui destaques com perguntas ou oclusões pendentes de revisão, **When** clica em "Iniciar Sessão" na Central de Revisão e seleciona o escopo "Rápida (10 itens)", **Then** o sistema transiciona para o modo imersivo e exibe o primeiro cartão com barra de progresso indicando "Item 1 de 10".
2. **Given** que o leitor está no modo imersivo de estudo, **When** revela a resposta e avalia sua retenção (Fácil, Médio ou Difícil), **Then** o sistema registra o tempo/avaliação, avança para o próximo cartão sem recarregar a tela e atualiza a barra de progresso.
3. **Given** que o leitor tenta sair da sessão no meio do fluxo, **When** pressiona a tecla de escape ou clica em cancelar, **Then** o sistema exibe diálogo de confirmação prevenindo abandono acidental.

---

### User Story 2 - Conclusão, Resumo de Auditoria e Feedback Cognitivo (Priority: P2)

Ao avaliar o último item da sessão, o leitor é apresentado a uma tela triunfante e solene de conclusão. O resumo detalha o volume de cartões processados, a distribuição de aproveitamento (fáceis, moderados, difíceis), o tempo total dedicado e as próximas datas de repetição calculadas, consolidando a sensação de dever cumprido e aprendizado fixado.

**Why this priority**: Fecha o ciclo de estudo com feedback cognitivo positivo e audita métricas de retenção para o leitor acompanhar sua evolução.

**Independent Test**: Pode ser testado completando uma sessão e verificando se a tela de resumo exibe os cálculos consolidados corretos de itens e tempo.

**Acceptance Scenarios**:

1. **Given** que o leitor concluiu a avaliação do último cartão da sessão, **When** confirma a última resposta, **Then** o sistema finaliza formalmente a sessão e abre o painel de resumo consolidado.
2. **Given** o painel de resumo da sessão, **When** o leitor visualiza os resultados, **Then** o sistema exibe contadores claros de itens revisados, taxa de facilidade/retenção, tempo dedicado e botão para retornar à Central de Revisão ou ao Livro.

---

### User Story 3 - Histórico de Sessões e Desempenho Retrospectivo (Priority: P3)

O leitor deseja auditar sua regularidade e dedicação histórica. Na Central de Revisão ou no Dashboard, o leitor consulta o histórico de sessões anteriores concluídas, visualizando datas, quantidade de itens, duração e livro associado.

**Why this priority**: Fornece rastreabilidade no longo prazo e incentiva a consistência de hábitos de estudo sem recorrer a gamificação infantil ou rankings competitivos.

**Independent Test**: Pode ser testado navegando até o histórico após concluir múltiplas sessões e verificando a listagem ordenada cronologicamente.

**Acceptance Scenarios**:

1. **Given** que o leitor concluiu sessões de estudo anteriormente, **When** acessa a aba ou seção de Histórico de Sessões, **Then** o sistema lista as sessões com data, horário, quantidade de itens e tempo total de foco.

---

### Edge Cases

- O que acontece se o leitor iniciar uma sessão mas não houver nenhum item pendente no escopo selecionado? O sistema exibe um aviso acolhedor informando que todos os estudos daquele escopo estão em dia e sugere explorar outros livros ou revisar mais tarde.
- O que acontece se o leitor fechar o navegador abruptamente ou cancelar no meio de uma sessão? O progresso individual dos itens já avaliados é rigorosamente salvo (carimbos de repetição preservados), e a sessão é registrada com status "interrompida" no histórico, sem contabilizar como conclusão formal.
- O que acontece se o leitor solicitar uma "Sessão Rápida de 10 itens" em um livro que só possui 4 itens pendentes? O sistema inicia a sessão imediatamente com os 4 itens disponíveis, exibindo no indicador de progresso "Item 1 de 4 (todos os pendentes deste livro)" sem travar o leitor com diálogos bloqueantes.
- Como o sistema se comporta caso o leitor tente realizar duas sessões concorrentes em dispositivos sincronizados? Cada dispositivo gerencia localmente sua sessão com timestamp atômico e sincroniza ao concluir.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir ao leitor iniciar uma sessão de estudo a partir da Central de Revisão ou da visão de um Livro específico.
- **FR-002**: O sistema DEVE permitir a escolha do escopo da sessão: rápida (lote reduzido), livro específico ou todos os pendentes do acervo.
- **FR-003**: O sistema DEVE apresentar a sessão em modo imersivo e livre de distrações, ocultando navegações periféricas globais enquanto a sessão estiver ativa.
- **FR-004**: O sistema DEVE exibir indicador contínuo de progresso visual e numérico durante toda a sessão (ex.: "Item 3 de 10" e porcentagem concluída).
- **FR-005**: O sistema DEVE permitir ao leitor avaliar sua recordação ativa em cada item utilizando critérios estruturados (Fácil, Médio, Difícil).
- **FR-006**: O sistema DEVE atualizar os carimbos de revisão e agendamento dos destaques no momento da conclusão de cada item.
- **FR-007**: O sistema DEVE registrar a duração total e os contadores de acerto/dificuldade da sessão no histórico de estudos.
- **FR-008**: O sistema DEVE exibir tela de encerramento com auditoria resumida do aprendizado ao final da sessão.
- **FR-009**: O sistema DEVE proteger contra saída involuntária através de confirmação antes de descartar uma sessão em andamento.
- **FR-010**: O sistema DEVE tratar sessões abandonadas ou interrompidas preservando os itens já respondidos e gravando a sessão com status "interrompida" no histórico.
- **FR-011**: O sistema DEVE ajustar dinamicamente o tamanho da sessão quando o escopo contiver menos itens que o limite solicitado, iniciando imediatamente com os itens disponíveis sem etapas extras de confirmação.
- **FR-012**: O sistema DEVE oferecer navegação acessível por teclado durante a sessão (atalhos numéricos ou de espaço para revelar e avaliar).

### Key Entities *(include if feature involves data)*

- **Sessão de Estudo (StudySession)**: Representa o bloco delimitado de tempo e foco do leitor. Contém identificador do leitor, livro de referência (opcional), data/hora de início, data/hora de conclusão, total de itens previstos e total de itens concluídos.
- **Item da Sessão (StudySessionItem)**: Representa a resposta e interação do leitor com um destaque específico dentro de uma sessão, registrando a classificação obtida (fácil, médio, difícil) e o tempo despendido no cartão.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue iniciar uma sessão de estudo em até 3 cliques a partir da Central de Revisão ou do Livro.
- **SC-002**: A transição entre cartões de estudo durante o modo imersivo ocorre em menos de 100ms, proporcionando fluxo de foco contínuo.
- **SC-003**: 100% das sessões concluídas geram registro auditável no histórico com contagem de itens e tempo de estudo.
- **SC-004**: Zero perda de dados de revisões já respondidas caso a sessão seja finalizada de forma regular.
- **SC-005**: A interface garante acessibilidade total com alvos de toque de no mínimo 44x44px em dispositivos móveis e atalhos completos de teclado em desktop.

## Assumptions

- O leitor já possui destaques e anotações gerados com perguntas ou oclusões aptos para estudo.
- O algoritmo de espaçamento existente na Central de Revisão continuará governando os intervalos de repetição individual de cada destaque.
- A experiência de sessão é estritamente individual e privada, sem comparativos competitivos ou tabelas públicas de líderes.
- O ambiente de estudo prioriza design sóbrio, acadêmico e solene, alinhado à filosofia editorial do Leitorum.
