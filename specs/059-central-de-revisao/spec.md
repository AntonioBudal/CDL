# Feature Specification: F 0.7.10 — Central de Revisão de Perguntas e Clozes

**Feature Branch**: `059-central-de-revisao`  
**Created**: 2026-10-04  
**Status**: Draft  
**Input**: User description: "/speckit-specify 0.7.10"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hub Central de Revisão e Seleção por Escopo (Priority: P1) 🎯 MVP

O leitor acessa a nova área centralizada de **Revisão** no menu principal (`/review`) para ter uma visão consolidada de todos os itens interativos de estudo cadastrados no seu acervo (perguntas de fixação e termos ocultos/clozes), podendo inspecionar contadores e filtrar por livro ou capítulo específico antes de iniciar uma rodada de estudo.

**Why this priority**: É a porta de entrada indispensável. Atualmente, os itens de Active Recall só podem ser exercitados se o leitor abrir cada estudo individualmente. O hub responde à pergunta central: *"O que eu tenho para revisar no Livro X ou em todo o meu caderno hoje?"*.

**Independent Test**: Navegar para `/review`; verificar que o painel lista as estatísticas de itens interativos totais; aplicar filtro por livro existente e verificar que o botão "Iniciar Revisão" atualiza a contagem de itens do lote correspondente.

**Acceptance Scenarios**:

1. **Given** um usuário com livros contendo perguntas e termos ocultos cadastrados, **When** ele clica no item "Revisão" na barra de navegação, **Then** o sistema exibe o painel com total de itens elegíveis, distribuição por tipo (perguntas vs clozes) e seletores de livro e capítulo.
2. **Given** o filtro de livro selecionado com 8 perguntas e 4 clozes, **When** o usuário clica em "Iniciar Revisão", **Then** a sessão é iniciada carregando os itens daquele livro.
3. **Given** um acervo sem nenhuma pergunta ou cloze cadastrado, **When** o usuário acessa `/review`, **Then** o sistema exibe um estado vazio acolhedor explicando como criar perguntas e termos ocultos na leitura dos estudos com atalho para os livros.

---

### User Story 2 - Sessão Interativa de Active Recall em Tela Limpa (Priority: P2)

O leitor exercita sua memória em uma interface de foco sem distrações: o item é apresentado com a resposta oculta (pergunta com resposta escondida ou texto com lacuna `[...]`); o leitor reflete ativamente; revela a resposta (via clique ou `Barra de Espaço`); avalia sua assimilação (*Fácil*, *Médio* ou *Difícil*, ou teclas `1`, `2`, `3`); e o sistema avança para o próximo item registrando o evento.

**Why this priority**: É o cerne da prática cognitiva deliberada (Active Recall). Precisa ser fluida, confortável e acessível tanto no Desktop quanto no Mobile, com suporte a teclado rápido.

**Independent Test**: Iniciar uma rodada; visualizar uma pergunta; acionar o botão "Revelar Resposta" (ou pressionar `Espaço`); conferir a resposta revelada; clicar em "Fácil" (ou pressionar `3`); confirmar que o sistema avança automaticamente para o item seguinte e incrementa o contador de progresso da rodada.

**Acceptance Scenarios**:

1. **Given** um card de pergunta em exibição, **When** a resposta ainda está oculta, **Then** o botão de revelação está em destaque e os botões de avaliação (*Difícil*, *Médio*, *Fácil*) permanecem desabilitados ou ocultos.
2. **Given** a resposta revelada pelo usuário, **When** o leitor pressiona a tecla `1` no teclado, **Then** o sistema classifica a resposta como "Difícil", emite anúncio acessível via `aria-live` e carrega o próximo card.
3. **Given** um termo oculto (cloze) em exibição, **When** o usuário clica em "Revelar Resposta", **Then** a lacuna `[...]` é preenchida pelo termo original com destaque visual luminoso suave.

---

### User Story 3 - Conclusão de Sessão, Estatísticas de Assimilação e Feedback (Priority: P3)

Ao esgotar os itens da rodada selecionada, o leitor recebe um painel de conclusão celebrando o hábito de revisão, exibindo o balanço de retenção da sessão (quantos itens classificados como *Fácil*, *Médio*, *Difícil*), com opções para "Revisar mais itens" ou "Voltar ao Caderno".

**Why this priority**: O fechamento de ciclo fornece sensação tangível de progresso, reforça o hábito de estudo e orienta o leitor sobre quais conteúdos demandam nova leitura atenta.

**Independent Test**: Completar todos os itens de uma rodada de revisão de 10 perguntas; confirmar que a tela final exibe o resumo com as contagens exatas de respostas fáceis, médias e difíceis, sem recarregar a aplicação.

**Acceptance Scenarios**:

1. **Given** o último item de uma sessão respondido, **When** o usuário confirma a avaliação, **Then** a tela transiciona para o painel de resumo da sessão exibindo total revisado e percentuais de assimilação.
2. **Given** a tela de conclusão de sessão, **When** o usuário clica em "Revisar mais itens", **Then** uma nova rodada é montada com os itens pendentes do filtro ativo.
3. **Given** a tela de conclusão de sessão, **When** o usuário clica em "Concluir e voltar ao acervo", **Then** a aplicação redireciona suavemente para a rota dos livros.

---

### Edge Cases

- O que acontece se todos os itens de um livro já tiverem sido revisados hoje? O sistema informa com clareza: *"Todos os itens deste livro foram revisados hoje! Deseja revisar novamente mesmo assim ou praticar outro livro?"*.
- O que ocorre se um estudo for movido para a lixeira (`deleted_at` preenchido)? Todos os seus destaques e perguntas associados deixam imediatamente de aparecer na fila de revisão.
- Como o sistema se comporta se o leitor recarregar o navegador ou sair no meio da rodada? As respostas já avaliadas permanecem persistidas individualmente com seu registro de data e avaliação; ao voltar à revisão, os itens já avaliados não se repetem na mesma rodada imediata.
- O que acontece se uma pergunta possuir texto longo ou formatação Markdown? O card de revisão renderiza Markdown com segurança, preservando legibilidade, quebras de linha e tipografia editorial do tema ativo.

---

## Clarifications

### Session 2026-10-04
- **Q1 (Critério de Ordenação dos Cards)**: Prioridade Inteligente Simples — itens nunca revisados aparecem primeiro, seguidos pelos revisados há mais tempo e pelos que receberam classificação "Difícil" na última rodada. -> **Option A (Accepted)**
- **Q2 (Tamanho da Rodada de Revisão)**: Blocos Focados de 10 Itens — a rodada padrão carrega 10 cards, com tela de conclusão e opções para "Revisar mais 10" ou "Revisar tudo disponível". -> **Option A (Accepted)**
- **Q3 (Escopo de Itens Elegíveis no Hub)**: Fila Unificada com Pílulas de Filtro — carrega perguntas e termos ocultos juntos por padrão, com pílulas para filtrar rapidamente ("Todos", "Perguntas", "Termos Ocultos"). -> **Option A (Accepted)**

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar uma rota e visão dedicada de Central de Revisão (`/review`) acessível pelo menu de navegação principal da aplicação.
- **FR-002**: O sistema DEVE consolidar todos os itens interativos de estudo do usuário ativo criados a partir de destaques do tipo oculto (`kind='hidden'`) e pergunta (`kind='question'`), excluindo estudos descartados na lixeira.
- **FR-003**: O painel DEVE fornecer filtros opcionais por Livro e por Capítulo, recalculando em tempo real o número de itens disponíveis para a rodada.
- **FR-004**: O sistema DEVE priorizar a ordenação dos cards na fila de revisão por relevância de fixação: itens nunca revisados aparecem primeiro, seguidos pelos itens revisados há mais tempo e priorizando aqueles classificados como "Difícil" na última rodada.
- **FR-005**: O sistema DEVE organizar as rodadas de estudo em blocos focados padrão de 10 itens por sessão, permitindo ao leitor continuar com "Revisar mais 10" ou praticar todos os itens disponíveis.
- **FR-006**: O sistema DEVE apresentar por padrão uma fila unificada de perguntas e termos ocultos (clozes), disponibilizando pílulas de alternância rápida de filtro por tipo ("Todos", "Perguntas", "Termos Ocultos").
- **FR-007**: A interface da sessão de revisão DEVE suportar atalhos de teclado ergonômicos no Desktop (`Barra de Espaço` para revelar; `1`, `2`, `3` para classificar *Difícil*, *Médio*, *Fácil*) e alvos táteis mínimos de $44 \times 44$px no Mobile.
- **FR-008**: O sistema DEVE persistir o evento de avaliação de cada item, registrando a data e hora da última revisão (`last_reviewed_at`), o incremento da contagem total de revisões (`review_count`) e a última classificação atribuída (`last_rating`).

---

### Key Entities *(include if feature involves data)*

- **ReviewItem**: Representação do item interativo em revisão, contendo identificador do destaque (`highlight_id`), estudo de origem (`study_id`, `study_title`), livro e capítulo (`book_id`, `book_title`, `chapter_id`, `chapter_name`), tipo (`hidden` para cloze ou `question` para pergunta direta), texto da pergunta/contexto, resposta oculta (`expected_answer`), data da última revisão e contagem histórica.
- **ReviewSessionSummary**: Registro em memória da rodada concluída, contendo total de cards praticados, contagem por classificação (`easy`, `medium`, `hard`) e duração aproximada da sessão.
- **ReviewRating**: Classificação de retenção escolhida pelo leitor (`easy`, `medium`, `hard`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue iniciar uma rodada de revisão e visualizar o primeiro card em menos de 2 cliques a partir do menu principal.
- **SC-002**: A alternância entre estado oculto e resposta revelada ocorre de forma instantânea (< 50ms) sem recarga visual da página.
- **SC-003**: 100% das operações de revelação e classificação podem ser executadas exclusivamente por teclado no desktop ou por toque ergonômico no mobile ($\ge 44 \times 44$px).
- **SC-004**: Zero itens pertencentes a estudos na lixeira (`deleted_at IS NOT NULL`) aparecem na fila de revisão em qualquer cenário de consulta.
- **SC-005**: Zero perda de registros de avaliação e integridade mantida com 100% de testes verdes (`npm test`, `pytest`, `npm run build`).

---

## Assumptions

- A primeira versão da Central de Revisão não adota algoritmos matemáticos complexos de repetição espaçada (como SuperMemo SM-2 ou FSRS); ela estabelece a infraestrutura essencial de registro e auditoria de revisão.
- Os destaques existentes criados em `study_highlights` com `kind IN ('hidden', 'question')` serão enriquecidos com metadados de revisão sem quebra de compatibilidade com os registros atuais.
- A aplicação é individual/multiusuário local, de modo que cada usuário revisa exclusivamente seus próprios itens de estudo ativos.
