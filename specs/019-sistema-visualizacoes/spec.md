# Feature Specification: F01 — Sistema de Visualizações e Dashboard Responsivo

**Feature Branch**: `019-sistema-visualizacoes`  
**Created**: 2026-09-19  
**Status**: Draft  
**Input**: User description: "F01 Sistema de Visualizações, E reajuste da tela de Dashboard no celular para uma versão responsiva"

---

## 1. Overview & Business Value

O Caderno de Leitura foi concebido para o estudo aprofundado de obras e ideias complexas. Atualmente, os estudos de um livro são apresentados predominantemente em uma listagem linear estática, o que restringe a capacidade do leitor de apreender a topologia conceitual, a hierarquia de argumentos e a visão espacial do seu conhecimento.

Esta especificação define:
1. **O Sistema de Visualizações (F01)**: Uma barra seletora coesa e acessível que permite alternar instantaneamente entre cinco modos fundamentais de visualização dos estudos (**Grade**, **Lista**, **Árvore**, **Mapa** e **Canvas**), preservando o contexto e o estudo em foco sem recarregar a página.
2. **O Reajuste Responsivo do Dashboard no Celular**: Adaptação ergonômica completa da tela de Visão Geral de Produtividade para dispositivos móveis, garantindo que o mapa de calor de leitura abra focado no período atual, os cartões de indicadores formem uma grade equilibrada e a linha do tempo seja perfeitamente legível sem transbordamentos.

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 - Alternância entre Modos de Visualização no Livro (Priority: P1) 🎯 MVP

Como leitor analisando as anotações de um livro denso,  
Quero alternar facilmente entre visualizações em Grade, Lista, Árvore, Mapa e Canvas através de um seletor visual no topo do palco de estudos,  
Para que eu possa escolher a melhor perspectiva analítica para o tipo de raciocínio que estou construindo.

**Why this priority**: É o cerne da Feature F01 do Roadmap 0.4. Sem essa capacidade de troca de perspectiva, todo o restante do roadmap espacial (árvore, canvas e grafos) fica inacessível.

**Independent Test**: Abrir qualquer livro com estudos cadastrados, clicar nos ícones da barra de visualização e verificar que o conteúdo central se reorganiza imediatamente no formato selecionado, mantendo visível o estudo em foco.

**Acceptance Scenarios**:
1. **Given** que o leitor está na visão de um livro com estudos, **When** clica no modo "Grade", **Then** os estudos são dispostos em cartões amplos destacando títulos, resumos e localização da leitura.
2. **Given** que o leitor está no modo "Grade", **When** clica no modo "Lista", **Then** a apresentação transita para uma listagem compacta de alta densidade de leitura.
3. **Given** que o leitor clica nos modos "Árvore", "Mapa" ou "Canvas", **Then** a respectiva projeção estrutural, relacional ou espacial é renderizada de forma responsiva.
4. **Given** que o leitor está com um estudo específico selecionado, **When** comuta entre qualquer um dos 5 modos, **Then** o mesmo estudo permanece destacado e centrado na tela.

---

### User Story 2 - Persistência de Preferências e Acessibilidade do Seletor (Priority: P2)

Como leitor assíduo que organiza diferentes tipos de obras,  
Quero que minhas preferências de visualização sejam lembradas automaticamente e que o seletor seja totalmente acessível por teclado e leitores de tela,  
Para que eu não precise reconfigurar a visão a cada visita e possa navegar confortavelmente com tecnologia assistiva.

**Why this priority**: Garante conformidade com os princípios constitucionais de acessibilidade e continuidade de uso do Caderno de Leitura.

**Independent Test**: Definir um modo de visualização específico em um livro, recarregar a página e confirmar a restauração. Navegar até o seletor por Tab e comutar modos com setas direcionais.

**Acceptance Scenarios**:
1. **Given** que o usuário selecionou a visualização em "Árvore" no livro A, **When** recarrega a página ou retorna ao livro mais tarde, **Then** o livro A reabre automaticamente no modo "Árvore".
2. **Given** um livro novo sem preferência individual customizada, **When** aberto pela primeira vez, **Then** herda a preferência global padrão do leitor.
3. **Given** que o usuário move o foco do teclado para o seletor de visualizações, **When** pressiona as setas Esquerda ou Direita, **Then** o foco e a seleção comutam sequencialmente entre os modos disponíveis com feedback sonoro/acessível.

---

### User Story 3 - Adaptação Responsiva do Dashboard de Leitura no Celular (Priority: P3)

Como leitor consultando meu ritmo de estudos em um smartphone,  
Quero que a tela de Dashboard exiba os indicadores em grade proporcional de 2 colunas, com o mapa de calor posicionado no mês atual e linha do tempo ergonômica,  
Para que eu tenha clareza imediata do meu hábito diário de leitura sem rolagens confusas ou quebras de layout.

**Why this priority**: Resolve diretamente a queixa de responsividade no celular, transformando o Dashboard em um hub diário agradável de consulta pelo celular.

**Independent Test**: Acessar o Dashboard em um smartphone ou tela redimensionada para 375px–390px e constatar que todos os cartões, o mapa de calor ancorado no mês corrente e a linha do tempo cabem perfeitamente na tela.

**Acceptance Scenarios**:
1. **Given** a tela do Dashboard em largura móvel (< 768px), **When** os indicadores de métricas são exibidos, **Then** organizam-se em 2 colunas harmônicas, com o indicador de sequência diária (*streak*) ocupando a largura total de destaque.
2. **Given** o mapa de calor anual no celular, **When** a tela é carregada, **Then** a barra de rolagem horizontal inicializa automaticamente ancorada na data de hoje (semanas mais recentes), permitindo ver o ritmo atual imediatamente.
3. **Given** a linha do tempo de atividades no celular, **When** os cartões de eventos são renderizados, **Then** os botões de ação ("Ler estudo", "Abrir livro") possuem área de toque mínima de 44x44px e o texto não sobrepõe badges.

---

## 3. Edge Cases & Boundary Conditions

- **EC-001**: O que acontece quando o livro ou capítulo não possui nenhum estudo cadastrado ao comutar para qualquer uma das visualizações?
  - *Comportamento*: Todas as cinco visualizações exibem um estado vazio claro e elegante (*EmptyState*), orientando o leitor a importar ou cadastrar o primeiro estudo.
- **EC-002**: O que acontece quando a visualização em Mapa ou Canvas é aberta em um smartphone de tela muito estreita (360px)?
  - *Comportamento*: O renderer ativa controles de toque tátil com suporte a pinça para zoom (*pinch-to-zoom*) e arrasto mono-toque suave, prevenindo que o gesto capture acidentalmente a rolagem da página inteira.
- **EC-003**: O que acontece se o armazenamento local do navegador estiver desativado ou corrompido?
  - *Comportamento*: O sistema opera graciosamente em memória adotando a visualização em Grade ou Lista como fallback de fábrica, sem travar a interface nem gerar mensagens intrusivas de erro.
- **EC-004**: O que acontece se o usuário filtrar a linha do tempo do Dashboard por um dia sem estudos no celular?
  - *Comportamento*: O estado vazio específico é renderizado centralizado com botão claro para "Exibir todas as atividades", retornando à visão cronológica ampla com um toque.

---

## 4. Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um seletor visual de modos de exibição dos estudos com suporte a cinco alternativas canônicas: **Grade**, **Lista**, **Árvore**, **Mapa** e **Canvas**.
- **FR-002**: O sistema DEVE preservar o estudo ativo em foco ao transitar entre qualquer uma das cinco visualizações.
- **FR-003**: O sistema DEVE persistir a preferência de visualização no armazenamento local do cliente através de um modelo híbrido: a preferência individual salva para um livro específico (`caderno_preferred_view_{bookId}`) tem precedência sobre a preferência padrão global da biblioteca (`caderno_default_view`), com novos livros herdando a preferência global do leitor (Q2: Opção A).
- **FR-004**: O seletor de visualizações DEVE ser operável por teclado, implementando semântica de abas (`role="tablist"` e `role="tab"`) com navegação direcional por setas.
- **FR-005**: No ambiente móvel (< 768px), o seletor de visualizações DEVE ser renderizado como uma barra horizontal compacta no topo da área de estudos com botões táteis de no mínimo 44x44px por ícone, permitindo comutação direta com toque único (Q3: Opção A).
- **FR-006**: Na tela de Dashboard no celular (< 768px), os cartões de métricas DEVEM organizar-se em uma grade de 2 colunas com o destaque de sequência (*streak*) ocupando a largura completa da seção.
- **FR-007**: Na tela de Dashboard no celular, o mapa de calor anual DEVE posicionar a área visível no período mais recente (data atual) no momento do carregamento inicial.
- **FR-008**: Na linha do tempo do Dashboard e nos cartões de estudo, todos os botões de ação e links acionáveis DEVEM garantir área de toque ergonômica mínima de 44x44px.
- **FR-009**: Quando os modos avançados (Mapa e Canvas) forem acionados em um capítulo com poucos estudos ou sem conexões semânticas explícitas cadastradas, o sistema DEVE renderizar uma projeção espacial fluida automática distribuindo harmonicamente os nós existentes no espaço visual, evitando bloqueios ou desvios involuntários de tela (Q1: Opção A).

---

## 5. Key Entities

- **Modo de Visualização (`StudyViewMode`)**:
  - Identificador do renderer: `grid`, `list`, `tree`, `map`, `canvas`.
  - Rótulo amigável em português: "Grade", "Lista", "Árvore", "Mapa", "Canvas".
  - Ícone vetorial sóbrio associado.
- **Preferência de Visualização (`ViewPreferenceState`)**:
  - `bookId`: Identificador do livro (opcional).
  - `preferredMode`: Modo atualmente ativo.
  - `updatedAt`: Data e hora da última alteração.
- **Layout Responsivo do Dashboard (`DashboardMobileLayout`)**:
  - Grid móvel calibrado em 2 colunas.
  - Posicionamento de rolagem do mapa de calor sincronizado na extremidade direita (atualidade).

---

## 6. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue alternar entre qualquer um dos 5 modos de visualização em menos de 100ms na tela do livro, sem recarregamento da página.
- **SC-002**: 100% das transições entre visualizações conservam o estudo em foco sem perder a posição de leitura.
- **SC-003**: A tela de Dashboard em smartphones (375px a 430px de largura) não apresenta transbordamento horizontal involuntário na página (`overflow-x: hidden` no corpo da página) e exibe os indicadores principais sem necessidade de rolagem vertical excessiva.
- **SC-004**: O mapa de calor no celular abre com a data de hoje imediatamente visível na área visível inicial em 100% dos acessos.
- **SC-005**: 100% dos botões de controle e links interativos nas visualizações e no dashboard atendem ao padrão de acessibilidade física com dimensões mínimas de 44x44px.

---

## 7. Assumptions

- A infraestrutura visual com iconografia vetorial da versão 0.4 (F09) já está instalada e disponível para os ícones do seletor.
- O contêiner de layout tripartite (F06 `SplitLayout`) continua hospedando a área principal de estudos no palco central, onde os renderers de visualização operam.
- Nenhum dado pessoal do acervo do usuário é alterado no banco de dados SQLite; as preferências de visualização pertencem exclusivamente à camada de apresentação e armazenamento local do cliente.
