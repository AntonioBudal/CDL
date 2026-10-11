# Feature Specification: F0.8.03 — Revisão: Bancada de Fixação Cognitiva

**Feature Branch**: `068-revisao-bancada-fixacao`

**Created**: 2026-10-11

**Status**: Ready for Planning

**Input**: User description: "Feature 03: Revisão — Bancada de Fixação Cognitiva (Roadmap 0.8 — Redesign Estrutural e Arquitetura Visual)"

---

## 1. Visão Geral e Contexto Editorial

A Central de Revisão (`/revisao`) é o espaço de consolidação do conhecimento adquirido no Leitorum, onde o leitor exercita a prática de *Active Recall* (recuperação ativa da memória) e repetição espaçada sobre as dúvidas, perguntas e termos ocultos (*clozes*) extraídos de suas leituras.

Atualmente, o cabeçalho da tela apresenta 5 caixas retangulares enfileiradas com números "0" destacados em cores saturadas, emulando um painel administrativo analítico de SaaS que afasta a serenidade do estudo profundo. Além disso, o estado inicial sem itens pendentes é frio e genérico, não ensinando ao leitor como alimentar sua rotina de revisão a partir do acervo.

Esta especificação transforma a Central de Revisão em uma **Bancada de Fixação Cognitiva**:
1. **Barra Unificada de Prontidão Intelectual:** Substituição dos 5 cards numéricos desconexos por uma seção integrada de prontidão diária, exibindo o saldo de cartões a revisar, a distribuição entre perguntas e termos ocultos e o tempo estimado de dedicação em minutos.
2. **Disparador Proeminente de Prática:** Um gatilho central e convidativo ("Praticar Revisão Agora") que inicia instantaneamente o ciclo de estudo ativo.
3. **Bancada Imersiva de Estudo Ativo:** Interface de exercício limpa e livre de distrações periféricas, com revelação fluida de respostas, classificação tátil de retenção em múltiplos níveis e suporte ergonômico a atalhos rápidos de teclado.
4. **Estado Vazio Pedagógico e Convidativo:** Quando não há itens pendentes, a tela apresenta um guia visual acolhedor contendo uma demonstração interativa de termo oculto que se revela ao clique, instruindo de forma prática como transformar trechos da leitura em desafios intelectuais.
5. **Conclusão Serena de Sessão:** Ao zerar os cartões da rodada, transição para um painel comemorativo discreto que celebra a constância do leitor sem recorrer a ruídos visuais espalhafatosos.

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 - Barra Unificada de Prontidão Intelectual e Disparador de Sessão (Priority: P1) [MVP]

O leitor acessa a Central de Revisão para conferir seus compromissos cognitivos do dia e iniciar sua prática diária:
1. **Painel Integrado de Prontidão:** Em vez de blocos dispersos com contadores frios, o topo da tela apresenta uma faixa editorial coesa indicando o volume de itens pendentes para o dia atual e a estimativa de tempo recomendada para a sessão (ex.: *15 cartões prontos • ~8 minutos sugeridos*).
2. **Distribuição Semântica de Conteúdo:** Indicadores discretos sinalizam a proporção de desafios entre perguntas abertas elaboradas e termos ocultos extraídos dos estudos.
3. **Disparador Primário de Sessão:** Um botão de ação de destaque ("Praticar Revisão Agora") convida o leitor a entrar no ciclo de estudo imediatamente com um único clique ou toque.

**Why this priority**: Estabelece o ponto focal da experiência de estudo diário, eliminando a sobrecarga de dashboards e oferecendo um convite claro à ação imediata de fixação.

**Independent Test**: Navegar até a página de revisão com itens pendentes, verificar que o resumo de prontidão consolida contadores e tempo estimado em uma faixa harmônica única e que o botão primário inicia a rodada de estudo.

**Acceptance Scenarios**:
1. **Given** um usuário com 12 cartões pendentes de revisão, **When** a página é carregada, **Then** o cabeçalho exibe a contagem consolidada, o tempo estimado de dedicação e a ação "Praticar Revisão Agora" em destaque.
2. **Given** itens pendentes distribuídos entre perguntas e termos ocultos, **When** o usuário observa a barra de prontidão, **Then** os dois formatos de desafio são quantificados de forma equilibrada sem poluição visual.
3. **Given** a barra de prontidão renderizada, **When** visualizada em qualquer um dos temas do sistema, **Then** as cores consomem exclusivamente as variáveis semânticas do tema ativo sem caixas retangulares azuis ou verdes artificiais.

---

### User Story 2 - Bancada Imersiva de Active Recall com Operação por Teclado (Priority: P1) [MVP]

Ao iniciar uma sessão de revisão, o leitor entra em um ambiente focado e sereno projetado para maximizar a concentração:
1. **Cartão de Desafio em Destaque:** O cartão exibe a questão reflexiva ou a passagem com omissão de palavra (*cloze*) em tipografia ampla e legível, ocultando menus laterais e elementos dispensáveis.
2. **Revelação Suave da Resposta:** O verso do cartão (resposta correta, contexto original e anotação do livro) é revelado com uma transição suave e fluida ao clicar em "Mostrar Resposta" ou pressionar a barra de espaço.
3. **Classificação Ergonômica da Retenção:** O leitor classifica sua facilidade/retenção em opções semânticas claras (Errei, Difícil, Bom, Fácil), alimentando o algoritmo de repetição espaçada.
4. **Atalhos Rápidos de Teclado:** O ciclo completo pode ser executado sem tirar as mãos do teclado (`Espaço` para revelar e teclas `1`, `2`, `3`, `4` para atribuir o grau de retenção).

**Why this priority**: É o cerne operacional do produto; uma experiência fluida de revisão por repetição espaçada precisa ser ágil, confortável e totalmente utilizável via teclado.

**Independent Test**: Iniciar uma sessão de estudo, navegar pelos cartões alternando frente e verso com a barra de espaço, classificar as respostas pelas teclas numéricas e validar o avanço progressivo do contador da rodada.

**Acceptance Scenarios**:
1. **Given** uma sessão de estudo em andamento, **When** o usuário pressiona a tecla `Espaço`, **Then** a resposta do cartão atual é revelada instantaneamente com transição visual elegante.
2. **Given** a resposta revelada, **When** o usuário pressiona a tecla `3` (Bom), **Then** a resposta é registrada com o respectivo nível de retenção e o próximo cartão da fila é apresentado.
3. **Given** a exibição de um termo oculto (*cloze*), **When** a resposta é apresentada, **Then** a palavra omitida ganha destaque visual claro no contexto da frase da qual foi extraída.

---

### User Story 3 - Estado Vazio Pedagógico com Demonstração Interativa (Priority: P2)

Quando o leitor ainda não possui itens cadastrados ou já concluiu todas as revisões do dia:
1. **Substituição de Telas Vazias Estáticas:** A página elimina mensagens cruas como "Nenhum item encontrado" e "0 itens", adotando um espaço acolhedor e instrutivo.
2. **Demonstração Interativa de Termo Oculto:** O leitor visualiza uma citação de exemplo contendo um termo camuflado (*[cloze]*). Ao clicar ou tocar sobre a lacuna, a palavra é revelada com uma microinteração didática que demonstra o princípio da fixação mental.
3. **Guia Passo a Passo de Criação:** Breves orientações ilustradas ensinam como grifar trechos durante a leitura de livros no aplicativo e transformá-los em perguntas ou termos ocultos para alimentar a bancada de revisão.

**Why this priority**: Desmistifica a prática de *Active Recall* para novos leitores, estimulando a criação contínua de conteúdo sem causar a sensação de uma tela abandonada ou quebrada.

**Independent Test**: Acessar a Central de Revisão em uma conta sem cartões pendentes, interagir com o componente pedagógico de termo oculto para validar a revelação ao clique e confirmar que as orientações de leitura estão visíveis e claras.

**Acceptance Scenarios**:
1. **Given** nenhum item elegível para revisão, **When** a página é renderizada, **Then** a interface apresenta o estado pedagógico com o exemplo prático interativo de termo oculto.
2. **Given** o cartão de demonstração interativo, **When** o leitor clica no espaço oculto, **Then** a palavra oculta é revelada com microanimação suave acompanhada de texto explicativo sobre o método.
3. **Given** o leitor no estado vazio, **When** busca orientação para começar, **Then** encontra um atalho direto ou instrução clara para abrir seus livros e criar seus primeiros grifos.

---

### User Story 4 - Conclusão Serena de Sessão e Histórico de Prática (Priority: P2)

Ao responder ao último cartão da rodada diária:
1. **Microinteração de Encerramento Sereno:** O leitor é saudado com uma mensagem serena de dever cumprido e feedback de constância intelectual (ex.: *Meta de hoje consolidada • Sua memória agradece*), sem explosões de confete ou ruídos invasivos.
2. **Resumo Qualitativo da Rodada:** O cartão de conclusão exibe um balanço do tempo total investido na sessão e a distribuição das classificações atribuídas (fáceis, médias, difíceis).
3. **Aba de Histórico de Sessões Estruturadas:** Acesso preservado à aba de sessões anteriores, exibindo a linha do tempo das práticas concluídas com datas, duração e aproveitamento em uma listagem alinhada à nova estética visual do sistema.

**Why this priority**: Fecha o ciclo de recompensa intrínseca do estudo, valorizando a constância do leitor e fornecendo visibilidade histórica sobre seu progresso duradouro.

**Independent Test**: Completar todos os cartões de uma sessão de revisão, validar a transição suave para a tela de conclusão serena com o resumo dos tempos e acessar o histórico confirmando o registro da sessão finalizada.

**Acceptance Scenarios**:
1. **Given** a classificação do último cartão pendente da fila, **When** o registro é concluído, **Then** a tela transiciona suavemente para o resumo sereno comemorativo.
2. **Given** a tela de conclusão de sessão, **When** o usuário consulta o resumo, **Then** são exibidos o número de cartões revisados, o tempo total e opções para retornar ao acervo ou revisar novamente se desejar.
3. **Given** a aba "Histórico de Sessões" selecionada, **When** carregada, **Then** apresenta as sessões anteriores em cartões limpos com data, escopo e contagem de itens avaliados.

---

### User Story 5 - Filtros Contextuais e Experiência Móvel sem Distrações (Priority: P3)

O leitor deseja focar em um livro específico ou revisar no celular durante um deslocamento:
1. **Filtros Contextuais de Estudo:** Capacidade de filtrar os cartões por Obra (livro específico), Capítulo ou Modalidade (apenas Perguntas ou apenas Termos Ocultos), adaptando a sessão às prioridades imediatas de estudo.
2. **Experiência Móvel Adaptada:** Em telas de smartphones (< 768px), o modo de revisão ocupa a área útil de forma imersiva, com botões de resposta e classificação em formato de barra inferior tátil com alvos de toque generosos ($\ge 44\times 44$px).
3. **Prevenção de Rolagem Indesejada:** O cartão de revisão adapta sua altura e tipografia de forma defensiva para evitar rolagens acidentais durante a passagem rápida entre perguntas.

**Why this priority**: Garante que o leitor consiga estudar de forma focada no celular em qualquer ambiente físico, mantendo o controle sobre quais tópicos revisar primeiro.

**Independent Test**: Aplicar filtro de obra na revisão para validar que apenas itens daquele livro entram na sessão, e redimensionar a tela para dimensões móveis para validar os alvos de toque de 44px e layout em tela cheia.

**Acceptance Scenarios**:
1. **Given** a seleção de um livro específico no seletor de escopo, **When** a sessão é iniciada, **Then** apenas os cartões pertencentes àquela obra são incluídos na rodada.
2. **Given** um dispositivo com tela de 375px de largura, **When** a revisão é executada, **Then** os botões de ação e classificação respeitam dimensões táteis mínimas de 44x44px e o cabeçalho utilitário é compactado.
3. **Given** a alternância de filtros entre "Todos", "Perguntas" e "Termos Ocultos", **When** o filtro é alterado, **Then** o contador de prontidão na barra superior recalcula imediatamente os itens elegíveis.

---

### Edge Cases

- **Cartão com pergunta ou contexto muito extenso:** O texto da questão deve possuir rolagem interna suave e limites de altura balanceados para não extravasar a área visível nem cobrir os botões de ação.
- **Sessão interrompida pelo usuário antes da conclusão:** Se o usuário fechar a página ou voltar para o acervo antes do término da rodada, o progresso dos cartões já avaliados deve ser mantido e os cartões restantes permanecem como pendentes.
- **Leitor com preferências de movimento reduzido ativas (`prefers-reduced-motion`):** Transições de virada de cartão e animações de conclusão devem suprimir transformações tridimensionais, adotando transição simples e imediata de visibilidade.
- **Nenhum item correspondente ao filtro de livro selecionado:** Caso o leitor selecione uma obra que não possui itens pendentes, o sistema deve exibir aviso contextual específico sugerindo trocar o filtro ou revisar todas as obras.

---

## 3. Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE exibir uma barra unificada de prontidão intelectual no topo da Central de Revisão, consolidando o volume total de itens a revisar no dia, a estimativa em minutos e a divisão por tipo de desafio.
- **FR-002**: O sistema DEVE fornecer um botão primário destacado ("Praticar Revisão Agora") que inicia imediatamente a sessão de fixação com um único clique ou toque.
- **FR-003**: O sistema DEVE apresentar os desafios de revisão (perguntas e termos ocultos) em cartões focados com distinção visual clara entre a frente (pergunta/omissão) e o verso (resposta/contexto revelado).
- **FR-004**: O sistema DEVE permitir a revelação da resposta de qualquer cartão através do botão de ação ou do pressionamento da tecla `Espaço`.
- **FR-005**: O sistema DEVE permitir a classificação da retenção do cartão em quatro níveis cognitivos (Errei, Difícil, Bom, Fácil), suportando atalhos diretos de teclado pelas teclas numéricas `1`, `2`, `3` e `4`.
- **FR-006**: O sistema DEVE calcular e exibir o tempo decorrido da sessão e o progresso quantitativo de cartões respondidos versus o total planejado.
- **FR-007**: Quando não houver itens pendentes para revisão, o sistema DEVE renderizar um estado vazio pedagógico demonstrando visualmente o funcionamento de um termo oculto interativo e fornecendo instruções sobre como criar novas perguntas nos livros.
- **FR-008**: O sistema DEVE apresentar um painel de conclusão sereno ao término da sessão comemorando a constância do leitor e resumindo os resultados de tempo e facilidade.
- **FR-009**: O sistema DEVE permitir a filtragem opcional da sessão de revisão por Obra, Capítulo e Tipo de item (Perguntas, Ocultamentos ou Ambos), recalculando a contagem de prontidão instantaneamente.
- **FR-010**: O sistema DEVE manter abas navegáveis entre a área de "Prática de Revisão" e o "Histórico de Sessões", permitindo consultar sessões anteriores com data, duração e índice de acertos.
- **FR-011**: O sistema DEVE garantir que todos os botões e seletores na interface de revisão em dispositivos móveis possuam áreas de toque mínimas de 44x44px.
- **FR-012**: O sistema DEVE consumir exclusivamente as variáveis semânticas dos temas cromáticos ativos do Leitorum, abstendo-se de classes com cores hexadecimais fixas ou caixas com tonalidades arbitrárias.

---

### Key Entities *(data representation)*

- **Item de Revisão (Review Item):** Representa o elemento de estudo individual elegível para prática de repetição espaçada. Contém o tipo de desafio (pergunta direta ou termo oculto), texto do enunciado, contexto da passagem, resposta esperada, livro/capítulo de origem e metadados de agendamento e histórico de retenção.
- **Sessão de Estudo (Study Session):** Representa um ciclo pontual de prática iniciado pelo leitor. Registra data/hora de início e término, escopo aplicado (geral, por livro ou por capítulo), volume de cartões processados, contagem por grau de retenção (errei, difícil, bom, fácil) e duração total em segundos.
- **Registro de Item de Sessão (Session Item Evaluation):** Registro da resposta de um item específico dentro de uma sessão, capturando a avaliação de retenção atribuída pelo leitor e o tempo de reflexão dispensado no cartão.

---

## 4. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue iniciar uma sessão de revisão em menos de 3 segundos a partir do momento em que acessa a página `/revisao`.
- **SC-002**: 100% dos cartões de revisão podem ser avançados e avaliados exclusivamente via teclado (`Espaço` e teclas `1-4`) sem necessidade de uso do mouse ou ponteiro.
- **SC-003**: A transição visual de revelação da resposta de um cartão e a passagem para o próximo ocorrem em menos de 250ms em qualquer dispositivo.
- **SC-004**: No estado vazio, 100% dos novos usuários encontram na tela uma explicação prática e interativa de como funciona a metodologia de termos ocultos.
- **SC-005**: A interface de revisão atende integralmente aos 10 temas cromáticos do sistema sem qualquer quebra de contraste ou vazamento de cores fixas incompatíveis.
- **SC-006**: Todos os botões interativos e alvos de toque na visão mobile possuem dimensões iguais ou superiores a 44x44px (conformidade com WCAG 2.1 Critério 2.5.5).

---

## 5. Assumptions

- A infraestrutura de cálculo de repetição espaçada e os endpoints de dados de revisão existentes permanecem preservados como fonte de dados para a bancada.
- O leitor possui livros ou estudos previamente cadastrados quando desejar praticar com dados próprios; na ausência deles, o estado vazio pedagógico orientará o primeiro fluxo de leitura.
- As sessões de estudo são realizadas localmente no dispositivo do usuário, mantendo a privacidade estrita das notas e histórico de retenção.
- A navegação entre a aba de prática e o histórico de sessões preserva os filtros selecionados pelo leitor durante a mesma navegação de página.
