# Feature Specification: F0.8.04 — Inbox: Mesa de Triagem e Despejo Intelectual

**Feature Branch**: `070-inbox-mesa-triagem`  
**Created**: 2026-10-11  
**Status**: Draft  
**Input**: Roadmap 0.8 — Feature 04: "Inbox — Mesa de Triagem e Despejo Intelectual" (Área: `/inbox`, Capturas rápidas e triagem de notas não estruturadas).

---

## 1. Contexto & Visão de Produto

A Caixa de Entrada (`/inbox`) do Leitorum atua como o ponto focal para o descarrego mental imediato (*fleeting notes*, citações avulsas e pensamentos transitórios) antes de sua consolidação no acervo duradouro de livros e estudos.

Atualmente, a interface opera com limitações que geram fricção cognitiva:
1. **Fricção de Captura**: Registrar uma ideia rápida exige clicar em um botão distante "+ Nova Captura" que abre um diálogo modal bloqueante, interrompendo o fluxo de pensamento do leitor.
2. **Sensação de Lista Administrativa Fria**: A listagem de capturas se assemelha a um gerenciador de tarefas genérico, sem a sensação fluida e acolhedora de uma "Mesa de Triagem".
3. **Falta de Transições de Saída**: Quando um item é arquivado ou promovido, a remoção da tela ocorre de forma abrupta, sem feedback tátil de progresso.
4. **Tratamento de Falhas Indesejado**: Erros eventuais de requisição exibem mensagens cruas de "Not Found" descoladas do design system editorial.

O redesenho transforma `/inbox` em uma **Mesa de Triagem e Despejo Intelectual**:
- Um campo superior permanente de descarrego mental (*Quick Thought Drop*) que expande com suavidade ao foco e salva imediatamente via `Ctrl+Enter`.
- Cartões com ferramentas contextuais de triagem direta (Promover a Estudo, Vincular a Livro, Arquivar, Excluir) com animação cinética acelerada por GPU.
- Uma barra de triagem moderna e segmentada com contadores discretos por status.
- Navegação ergonômica por teclado (`J`/`K` para percorrer notas, `E` para arquivar, `Ctrl+Enter` para salvar).
- Estado vazio acolhedor ("Mesa Limpa") e tratamento robusto de erros dentro dos 10 temas visuais do Leitorum.

---

## 2. User Scenarios & Testing *(Prioritised)*

### User Story 1 - Despejo Rápido Permanente no Topo (*Quick Thought Drop*) (Priority: P1) [MVP]

**Objetivo**: Como leitor imerso em reflexões, desejo digitar um pensamento no campo superior permanente da tela do Inbox e salvá-lo instantaneamente via `Ctrl+Enter` sem abrir caixas de diálogo modais, para esvaziar minha mente com zero fricção.

**Why this priority**: É a essência do Inbox: descarregar ideias efêmeras (*fleeting notes*) na velocidade do pensamento.

**Independent Test**: Acessar `/inbox`, focar no campo superior, digitar uma reflexão, pressionar `Ctrl+Enter` e constatar que a nota surge imediatamente no topo da fila de pendentes sem recarga de tela.

**Acceptance Scenarios**:
1. **Given** um usuário na tela `/inbox`,  
   **When** ele foca no campo superior de captura rápida,  
   **Then** a área de texto expande suavemente de 1 linha para 4 linhas (`:focus-within`) revelando os controles de apoio e a dica de atalho.
2. **Given** um pensamento digitado no campo superior,  
   **When** o leitor pressiona `Ctrl+Enter` (ou clica no botão "Despejar Pensamento"),  
   **Then** a captura é criada com sucesso, o campo é limpo e recolhido, e o novo cartão surge no topo da lista com feedback visual imediato.
3. **Given** um campo de texto vazio ou contendo apenas espaços em branco,  
   **When** o usuário tenta submeter via `Ctrl+Enter`,  
   **Then** nenhuma requisição é disparada e o sistema previne submissões vazias de forma silenciosa.

---

### User Story 2 - Barra Segmentada de Triagem com Contadores Dinâmicos (Priority: P1) [MVP]

**Objetivo**: Como leitor que organiza suas anotações, desejo visualizar o fluxo de triagem através de uma barra segmentada com contadores em tempo real, para saber exatamente quantas notas estão pendentes, promovidas, vinculadas ou arquivadas.

**Why this priority**: Substitui as abas frias de tabela administrativa por um painel de controle claro e coerente com os 10 temas.

**Independent Test**: Alternar entre os segmentos da barra (Pendentes, Promovidos, Vinculados, Arquivados, Todos) e confirmar a filtragem correta da listagem e a contagem precisa.

**Acceptance Scenarios**:
1. **Given** a barra de triagem no topo da listagem,  
   **When** visualizada pelo leitor,  
   **Then** apresenta botões de segmento para `Pendentes`, `Promovidos`, `Vinculados`, `Arquivados` e `Todos`, exibindo o contador numérico de pendências em destaque sutil.
2. **Given** a seleção do segmento `Arquivados`,  
   **When** o usuário clica no botão correspondente,  
   **Then** a lista atualiza instantaneamente exibindo apenas notas arquivadas, com indicador acessível de seleção ativa (`aria-selected="true"`).

---

### User Story 3 - Triagem Contextual com Transição Cinética Suave (Priority: P1) [MVP]

**Objetivo**: Como leitor processando minhas notas, desejo acionar ações de triagem (Arquivar, Promover a Estudo, Vincular a Livro, Excluir) diretamente no cartão e ver o item deslizar suavemente para fora da mesa de pendências.

**Why this priority**: Elimina a sensação estática de CRUD e confere a satisfação tátil de processar e "limpar a mesa" de trabalho.

**Independent Test**: Clicar na ação "Arquivar" de um cartão pendente e validar que o item desliza para o lado com desvanecimento suave ($\le 200$ms) e a lista inferior sobe com animação fluida sem pulos abruptos.

**Acceptance Scenarios**:
1. **Given** um cartão de captura na visualização de pendentes,  
   **When** o usuário clica no botão de ação rápida "Arquivar",  
   **Then** o cartão realiza transição de saída (`transform: translateX(30px)` e `opacity: 0` em $\le 200$ms), o contador de pendências decrementa e a lista se reorganiza suavemente.
2. **Given** um cartão de captura pendente,  
   **When** o usuário clica em "Promover a Estudo",  
   **Then** o sistema redireciona imediatamente para o Ateliê de Fichamento (`/importar?promote_inbox_id={id}`) pré-populando o rascunho com o conteúdo da nota.
3. **Given** a intenção de vincular uma nota a um livro existente,  
   **When** o usuário clica em "Vincular",  
   **Then** o modal de busca e seleção de livro/capítulo é apresentado com foco retido e acessibilidade completa.
4. **Given** a ação de exclusão de uma captura,  
   **When** o usuário aciona o botão de exclusão,  
   **Then** um diálogo ou confirmação inline defensiva é solicitada antes de purgar o registro definitivamente.

---

### User Story 4 - Operação 100% por Teclado e Acessibilidade (Priority: P2)

**Objetivo**: Como leitor que valoriza ergonomia e velocidade no teclado, desejo navegar entre as notas via teclas `J`/`K` e arquivar com a tecla `E`, sem precisar mover as mãos para o mouse.

**Why this priority**: Permite processamento rápido em lote (*triage sprints*) com mínima fricção física.

**Independent Test**: Na listagem de notas, usar `J` para descer o foco, `K` para subir, e pressionar `E` para arquivar a nota atualmente focalizada.

**Acceptance Scenarios**:
1. **Given** a lista de capturas ativa,  
   **When** o usuário pressiona `J` ou `K` (sem estar digitando em campo de texto),  
   **Then** o anel de foco visual se desloca para o próximo cartão (ou anterior).
2. **Given** um cartão focalizado via teclado,  
   **When** o usuário pressiona a tecla `E`,  
   **Then** o item é arquivado instantaneamente e o foco se desloca para a nota subsequente.
3. **Given** o atalho global `Ctrl+Shift+C`,  
   **When** acionado em qualquer lugar da tela,  
   **Then** o foco do cursor salta imediatamente para o campo de captura rápida no topo da página.

---

### User Story 5 - Estado Vazio "Mesa Limpa" e Tratamento Elegante de Erros (Priority: P3)

**Objetivo**: Como leitor que concluiu toda a triagem diária, desejo contemplar uma tela de "Mesa Limpa" serena, e na eventualidade de falhas de rede, receber uma notificação amigável integrada aos 10 temas visuais.

**Why this priority**: Reforça a atmosfera acolhedora e confiável do Leitorum, eliminando mensagens cruas de erro e telas impessoais.

**Independent Test**: Esvaziar a fila de pendências para verificar a tela de "Mesa Limpa", e simular erro de conexão confirmando o cartão editorial de erro com botão "Tentar Novamente".

**Acceptance Scenarios**:
1. **Given** que todas as capturas pendentes foram processadas,  
   **When** o segmento `Pendentes` é visualizado,  
   **Then** a interface apresenta a mensagem editorial "Mesa Limpa: Todos os seus pensamentos foram acolhidos e integrados ao seu acervo" com ilustração vetorial serena (zero emojis).
2. **Given** uma falha momentânea de rede,  
   **When** a listagem não puder ser obtida,  
   **Then** a mensagem crua de erro é substituída por um componente editorial com botão de repetição acessível (`role="alert"` e foco nítido).
3. **Given** qualquer um dos 10 temas visuais ativos,  
   **When** o Inbox é renderizado,  
   **Then** todas as cores consomem tokens semânticos (`var(--color-surface)`, `var(--color-text)`, `var(--color-accent)`, etc.), sem cores hexadecimais fixas e com alvos móveis $\ge 44 \times 44$px.

---

## 3. Edge Cases

- **Texto Muito Longo no Despejo Rápido**: Se o usuário colar um texto extenso (> 1000 caracteres) no campo de captura superior, a caixa de texto deve suportar rolagem interna suave sem quebrar o layout da página.
- **Conflito de Atalhos com Digitação**: As teclas `J`, `K` e `E` devem ser estritamente ignoradas quando o foco do cursor estiver em elementos `<textarea>`, `<input>` ou `<select>`, evitando arquivamento acidental durante a edição.
- **Remoção Concorrente ou Múltipla**: Se o usuário arquivar notas rapidamente em sequência via teclado, a lista deve gerenciar o estado reativo sem congelamento de interface ou dessincronização de contadores.
- **Dispositivos Móveis e Telas Estreitas (< 768px)**: A barra segmentada deve permitir rolagem horizontal suave (*scroll snap*) sem quebrar a largura da viewport, e os botões de ação contextuais devem garantir tamanho mínimo de toque de 44px.

---

## 4. Requirements *(Mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer no topo da página `/inbox` um componente permanente de captura rápida (*Quick Thought Drop*) permitindo digitação direta sem abertura de modal.
- **FR-002**: O campo de captura rápida DEVE expandir com transição suave ($\le 200$ms) ao receber foco e exibir botão "Despejar Pensamento" e atalho explicativo.
- **FR-003**: O sistema DEVE suportar o atalho `Ctrl+Enter` (e `Cmd+Enter` no macOS) no campo de captura rápida para salvar o pensamento e inseri-lo imediatamente no topo da lista de pendentes.
- **FR-004**: O sistema DEVE disponibilizar uma barra segmentada de triagem substituindo as abas legadas, contendo os filtros: `Pendentes` (`inbox`), `Promovidos` (`promoted`), `Vinculados` (`linked`), `Arquivados` (`archived`) e `Todos` (`all`).
- **FR-005**: O contador de notas pendentes DEVE ser exibido de forma destacada e atualizado dinamicamente a cada criação, arquivamento ou exclusão.
- **FR-006**: Cada cartão de captura DEVE expor ferramentas de triagem direta: Promover a Estudo, Vincular a Livro/Capítulo, Arquivar/Desarquivar e Excluir.
- **FR-007**: A ação de arquivar DEVE animar o cartão deslizando-o para a lateral com redução de opacidade antes de removê-lo da fila de pendentes.
- **FR-008**: O sistema DEVE implementar navegação e triagem rápida por teclado na lista de capturas: `J` para avançar seleção, `K` para retroceder e `E` para arquivar a nota selecionada, com guarda defensiva que ignora atalhos dentro de campos de digitação.
- **FR-009**: O atalho global `Ctrl+Shift+C` DEVE deslocar o foco imediatamente para o campo de captura rápida no topo do Inbox.
- **FR-010**: A interface DEVE exibir um estado vazio editorial acolhedor ("Mesa Limpa") quando a fila de pendentes estiver vazia, incentivando a serenidade do leitor.
- **FR-011**: Eventuais falhas de requisição DEVEM ser tratadas com componente editorial de erro no tema ativo, contendo botão "Tentar Novamente", banindo mensagens cruas de "Not Found".

### Non-Functional & Quality Constraints

- **NR-001 (Imunidade Cromática)**: Estilização 100% aderente aos 10 temas visuais do Leitorum via variáveis CSS semânticas, sem cores hexadecimais saturadas fixas.
- **NR-002 (Zero Emojis)**: Banimento absoluto de emojis em textos e botões; uso exclusivo de ícones SVG semânticos.
- **NR-003 (Acessibilidade WAI-ARIA)**: Rótulos `aria-label`, estados `aria-selected`, regiões `aria-live` para anúncios de triagem e anéis de foco visíveis (`:focus-visible`).
- **NR-004 (Ergonomia Tátil)**: Alvos de toque $\ge 44 \times 44$px para todos os botões no layout móvel.
- **NR-005 (Preservação de Dados e Backend)**: Nenhuma alteração nas tabelas de banco, migrações Alembic ou lógica de negócio existente do backend (`backend/app/routers/inbox.py`).

---

## 5. Success Criteria *(Mandatory)*

### Measurable Outcomes

- **SC-001**: O tempo necessário para um leitor abrir `/inbox`, digitar um pensamento e salvá-lo via `Ctrl+Enter` é inferior a 5 segundos (redução de 60% no tempo em relação ao fluxo modal antigo).
- **SC-002**: A animação de triagem e saída do cartão conclui em $\le 200$ms com aceleração por GPU, mantendo taxa estável de 60 FPS.
- **SC-003**: 100% das ações de triagem (arquivar, promover, vincular, excluir) podem ser operadas via teclado sem necessidade do cursor do mouse.
- **SC-004**: 100% das suítes de testes (`npm test`, `npm run build`, `pytest backend/tests`) são aprovadas com zero falhas e zero erros de tipo.

---

## 6. Assumptions & Dependencies

- **Endpoints de Backend Preservados**: A API existente `/api/inbox/captures` (GET, POST, PATCH, DELETE) atende 100% às necessidades da Mesa de Triagem; nenhuma alteração de schema ou endpoint é necessária.
- **Fluxo de Promoção**: A ação "Promover" continuará navegando para `/importar?promote_inbox_id={id}` para transformar o rascunho em fichamento estruturado.
- **Modal de Vinculação**: O componente `LinkToStudyModal.vue` existente continuará sendo utilizado para a vinculação a livros/estudos.
