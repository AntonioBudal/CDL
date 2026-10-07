# Feature Specification: F0.7.13 — Caixa de Entrada de Capturas (Inbox de Conhecimento)

**Feature Branch**: `062-inbox-capturas`

**Created**: 2026-10-10

**Status**: Ready for Planning

**Input**: User description: "/speckit-specify F0.7.13" (F 0.7.13 — Caixa de Entrada de Capturas / Inbox de Conhecimento)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Captura Rápida Global de Pensamentos e Citações (Priority: P1) 🎯 MVP

Como leitor em meio a uma leitura dinâmica ou reflexão, quero registrar rapidamente uma ideia solta, citação textual ou trecho provisório através de um modal ou atalho sem precisar criar previamente um estudo estruturado completo (com livro, capítulo e 4 seções), para que meu fluxo de pensamento não seja interrompido.

**Why this priority**: É a essência e porta de entrada da feature. Sem uma forma instantânea e descompromissada de despejo mental, o usuário continua com fricção e evita registrar ideias preliminares.

**Independent Test**: Pressionar o atalho global (`Ctrl+Shift+C`) ou clicar no botão de captura rápida no cabeçalho/menu; preencher o campo de texto livre com um pensamento e opcionalmente uma referência da fonte; salvar em menos de 5 segundos e verificar o fechamento imediato do modal com toast de confirmação e incremento do contador no menu.

**Acceptance Scenarios**:

1. **Given** um usuário navegando em qualquer tela do sistema, **When** ele aciona o atalho `Ctrl+Shift+C` (ou botão de ação rápida "Capturar"), **Then** o modal `QuickCaptureModal.vue` é exibido em primeiro plano com foco automático no campo de texto.
2. **Given** o formulário de captura rápida aberto, **When** o usuário digita o texto da ideia e clica em "Salvar" (ou pressiona `Ctrl+Enter`), **Then** a captura é gravada com status `inbox` e uma notificação sutil confirma a gravação sem redirecionar a tela atual.
3. **Given** o formulário de captura rápida aberto, **When** o usuário pressiona a tecla `Escape` ou clica em cancelar, **Then** o modal é fechado sem salvar alterações e sem travar a navegação.

---

### User Story 2 - Central de Triagem e Gerenciamento do Inbox (Priority: P2)

Como leitor organizando meu acervo de conhecimento, quero acessar uma tela dedicada de Caixa de Entrada (`/inbox`) para visualizar todas as capturas pendentes não processadas, filtrá-las, editar notas provisórias e descartar anotações irrelevantes com facilidade.

**Why this priority**: Garante que as capturas rápidas não virem um "cemitério de ideias esquecidas", provendo um ambiente claro de triagem e curadoria de notas.

**Independent Test**: Acessar a rota `/inbox` pelo menu lateral; verificar a listagem cronológica reversa das capturas pendentes em cartões individuais (`CaptureItemCard.vue`); realizar busca textual, editar o conteúdo de um cartão inline/modal e descartar uma captura indesejada.

**Acceptance Scenarios**:

1. **Given** um leitor com capturas pendentes no sistema, **When** ele navega para `/inbox`, **Then** a interface lista todas as capturas ativas com badges de status, data relativa de criação, fonte de referência (se houver) e prévia do texto.
2. **Given** a lista de capturas no Inbox, **When** o usuário pesquisa por termos no campo de busca do topo, **Then** os cartões são filtrados instantaneamente pelo conteúdo textual e pela referência de fonte.
3. **Given** uma captura que o usuário não deseja mais manter, **When** ele clica no botão "Descartar", **Then** uma confirmação rápida é solicitada e o item é removido da lista ativa, decrementando o badge do menu lateral.

---

### User Story 3 - Promoção de Captura para Estudo Formal ou Vinculação a Estudo Existente (Priority: P3)

Como leitor que amadureceu uma ideia capturada anteriormente, quero promover a anotação para um Estudo formal no meu acervo (com 1 clique) ou vinculá-la a um estudo já existente, mantendo o histórico de origem e limpando o item da lista de pendências da caixa de entrada.

**Why this priority**: Conclui o Ciclo do Conhecimento do Leitorum (`[CAPTURAR] -> [ORGANIZAR] -> [CONECTAR]`), fazendo a ponte entre anotações rápidas e a base analítica duradoura.

**Independent Test**: No cartão de uma captura pendente na Central de Inbox, clicar em "Promover para Estudo"; verificar a abertura do formulário de estudo com os dados da captura injetados no campo de Resumo; salvar o estudo e comprovar que a captura no Inbox passa para o status `promoted` com link rastreável para o estudo criado.

**Acceptance Scenarios**:

1. **Given** uma captura pendente com texto e livro associado, **When** o usuário clica em "Promover para Estudo", **Then** o sistema redireciona para o editor de estudos com o texto pré-preenchido na seção de Resumo, a fonte na seção de Referências e o livro pré-selecionado, marcando a captura como promovida no backend após a gravação bem-sucedida do estudo.
2. **Given** uma captura pendente sem livro ou obra previamente especificada, **When** o usuário clica em "Promover para Estudo", **Then** o editor é aberto exigindo a seleção obrigatória de um livro e capítulo existentes no formulário antes de permitir salvar o estudo promovido.
3. **Given** uma captura pendente que complementa um estudo que já existe, **When** o usuário seleciona a opção "Vincular a Estudo Existente", **Then** um modal de busca permite selecionar o estudo de destino; após a confirmação, o texto da captura formatado é anexado ao final da seção de Referências do estudo escolhido e a captura no Inbox é marcada como vinculada/arquivada (`linked`), decrementando as pendências do Inbox.

---

### Edge Cases

- **Capturas volumosas de texto longo**: O campo de texto suporta colar trechos de múltiplos parágrafos; na visualização do cartão do Inbox, textos com mais de 300 caracteres são colapsados com botão "Ver mais...".
- **Sem livro associado no momento da captura**: O usuário pode capturar ideias totalmente agnósticas a obras (ex.: uma reflexão filosófica avulsa). O campo de livro é estritamente opcional no momento da captura.
- **Exclusão de livro vinculado a capturas**: Caso um livro associado a capturas pendentes seja enviado para a lixeira, a captura não é excluída nem corrompida; o campo `book_id` mantém integridade ou exibe indicação neutra da obra.
- **Desistência ou cancelamento na tela de promoção**: Se o usuário iniciar a promoção para estudo mas cancelar o formulário sem salvar, a captura original permanece intacta com status `inbox` sem gerar estudos órfãos.
- **Uso offline ou desconexão temporária**: Formulário local previne perda do texto digitado caso ocorra falha de rede ao submeter, exibindo toast de erro com retenção do conteúdo digitado no modal.
- **Teclado e acessibilidade móvel**: O modal de captura no mobile respeita a área visível do teclado virtual (`visualViewport`) e provê botão de ação flutuante (FAB) de fácil alcance para o polegar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar um modal global de Captura Rápida (`QuickCaptureModal.vue`), acionável via atalho de teclado (`Ctrl+Shift+C`) e botão de ação rápida no cabeçalho da aplicação em qualquer rota.
- **FR-002**: O modal de captura DEVE conter um campo de texto livre de alta prioridade (com auto-foco) e campos opcionais para indicação de fonte/referência textual (`source_hint`) e seleção opcional de livro do acervo (`book_id`).
- **FR-003**: O sistema DEVE persistir as capturas na tabela relacional dedicada `inbox_captures`, contendo `id`, `user_id`, `book_id`, `content`, `source_hint`, `status`, `promoted_study_id`, `created_at` e `updated_at`.
- **FR-004**: O sistema DEVE disponibilizar rota dedicada `/inbox` (`InboxView.vue`) listando as capturas pendentes, com filtros por status (`inbox`, `promoted`, `linked`, `archived`), busca textual e suporte a paginação.
- **FR-005**: O menu lateral de navegação DEVE exibir um item "Inbox" com badge numérico reativo indicando a quantidade de capturas pendentes com status `inbox`.
- **FR-006**: O sistema DEVE fornecer endpoint `GET /api/inbox/count` leve para atualização dinâmica do contador do badge sem sobrecarregar a listagem completa.
- **FR-007**: Cada item do Inbox DEVE dispor de ações imediatas: editar conteúdo/fonte, descartar/arquivar, promover para estudo e vincular a estudo existente.
- **FR-008**: O fluxo de promoção para estudo DEVE redirecionar o usuário para o editor de estudos com dados pré-preenchidos (texto no Resumo e fonte nas Referências); ao salvar o estudo, a API atualiza a captura para status `promoted` associando `promoted_study_id`. Se a edição for cancelada, a captura original permanece no status `inbox`.
- **FR-009**: Ao promover uma captura sem livro pré-definido, o sistema DEVE exigir a seleção obrigatória de uma obra e capítulo válidos no formulário do editor antes de permitir concluir o salvamento do estudo.
- **FR-010**: Ao selecionar "Vincular a Estudo Existente", o sistema DEVE abrir um seletor modal de estudos e, mediante confirmação, anexar o conteúdo da captura formatado ao final da seção de Referências do estudo alvo via `POST /api/inbox/{id}/link`, atualizando a captura para status `linked` e decrementando as pendências do Inbox.
- **FR-011**: O sistema DEVE assegurar isolamento multiusuário estrito em todas as operações de leitura, escrita e contagem de capturas (`user_id`).
- **FR-012**: Todos os elementos da interface do Inbox e do modal de captura DEVEM respeitar critérios de acessibilidade (foco ao abrir modal, fechamento com `Escape`, rótulos `aria-label`, alvos de clique $\ge 44 \times 44$px no mobile).

### Key Entities *(include if feature involves data)*

- **InboxCapture**: Registro relacional de captura rápida:
  - `id`: Identificador numérico inteiro (PK)
  - `user_id`: UUID do proprietário (FK users)
  - `book_id`: ID opcional do livro referenciado (FK books, nullable)
  - `content`: Conteúdo textual em formato markdown da anotação/ideia
  - `source_hint`: Texto descritivo da fonte (ex.: "Capítulo 3, pág. 45" ou citação externa)
  - `status`: Estado atual da captura (`inbox`, `promoted`, `linked`, `archived`)
  - `promoted_study_id`: ID do estudo gerado pela promoção (FK studies, nullable)
  - `created_at`: Data e hora de registro
  - `updated_at`: Data e hora da última modificação

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuário consegue abrir o modal de captura e registrar uma ideia em menos de 5 segundos a partir de qualquer página da aplicação.
- **SC-002**: O badge numérico de capturas pendentes no menu lateral atualiza reativamente de forma imediata após qualquer criação, exclusão, vinculação ou promoção de captura.
- **SC-003**: 100% do texto e das notas de fonte inseridas em uma captura são preservados sem truncamento ou perda de formatação ao serem promovidos ou vinculados a um estudo.
- **SC-004**: 100% de isolamento multiusuário em todas as rotas e queries da tabela `inbox_captures`.
- **SC-005**: Tempo de resposta do endpoint `GET /api/inbox/count` inferior a 50ms em SQLite local.

## Assumptions

- O usuário utiliza o Inbox como caixa de descarrego mental provisório, não como substituto definitivo dos estudos com 4 seções analíticas.
- A aplicação roda em processo local e a persistência é no banco SQLite com suporte à migração Alembic (`0026_add_inbox_captures_table.py`).
- O modal de captura funciona em dispositivos móveis e desktop, integrando-se suavemente ao layout existente em `App.vue`.
- Não há processamento de OCR ou transcrição de áudio nesta versão.
