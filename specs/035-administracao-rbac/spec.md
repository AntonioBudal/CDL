# Feature Specification: F08 — Administração e RBAC

**Feature Branch**: `035-administracao-rbac`

**Created**: 2026-09-26

**Status**: Draft

**Input**: User description: "F08 - Administração e RBAC"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Painel de Gestão de Contas e Visualização Administrativa (Priority: P1) 🎯 MVP

Como administrador do sistema, quero acessar uma área de administração centralizada para visualizar todos os usuários cadastrados na plataforma com seus respectivos papéis, status de conta, data de cadastro, último acesso e volume de estudos, para que eu possa monitorar a utilização e a governança da comunidade de leitores.

**Why this priority**: É a fundação do RBAC e da governança administrativa. Sem a listagem e visualização com controle de acesso rigoroso, nenhuma operação de moderação ou gestão de privilégios pode ser executada com segurança.

**Independent Test**: Pode ser testado de forma independente criando uma conta de administrador e uma conta de usuário leitor. Ao acessar o painel administrativo, o administrador visualiza todas as contas com dados consolidados e filtros de busca; o usuário comum ao tentar acessar a mesma rota recebe resposta de acesso proibido.

**Acceptance Scenarios**:

1. **Given** um usuário com papel de administrador autenticado, **When** ele acessa a área administrativa (`/admin`), **Then** o sistema exibe a tabela completa de usuários com colunas de identificador, nome de exibição, nome de usuário, e-mail institucional/pessoal, provedor de autenticação, data de cadastro, último acesso, papel (`admin` / `user`), status da conta e contagem de estudos.
2. **Given** um leitor convencional (papel `user`) autenticado, **When** ele tenta acessar a rota do painel administrativo ou consultar os dados de gestão de contas, **Then** o sistema recusa a requisição com mensagem explícita de acesso negado (403 Forbidden).
3. **Given** um visitante não autenticado, **When** ele tenta acessar os recursos de administração, **Then** o sistema exige login (401 Unauthorized).
4. **Given** um administrador no painel, **When** ele filtra a listagem por status (`ativo`, `suspenso`) ou digita um termo no campo de busca (nome, @username ou e-mail), **Then** a lista reflete dinamicamente apenas as contas correspondentes.

---

### User Story 2 - Moderação de Contas: Suspensão, Reativação e Revogação de Sessões (Priority: P2)

Como administrador do sistema, quero suspender contas que violem termos de uso ou apresentem comportamento anômalo, e posteriormente reativá-las caso apropriado, garantindo o encerramento forçado de suas sessões ativas para impedir novos acessos enquanto suspensas.

**Why this priority**: É o mecanismo fundamental de proteção da integridade da plataforma contra abuso, spam ou comprometimento de credenciais.

**Independent Test**: Um administrador suspende uma conta ativa de um leitor que possui sessão aberta em outro navegador. A sessão do usuário suspenso é invalidada imediatamente e qualquer tentativa de leitura ou mutação é bloqueada. Ao reativar a conta, o leitor consegue autenticar-se e voltar a usar a aplicação normalmente.

**Acceptance Scenarios**:

1. **Given** uma conta de leitor ativa, **When** o administrador seleciona a ação "Suspender Conta", **Then** o status da conta é alterado para "suspenso", todas as sessões ativas do usuário são invalidadas imediatamente no servidor e a ação é confirmada na interface.
2. **Given** um usuário cuja conta está suspensa, **When** ele tenta realizar qualquer operação ou fazer novo login, **Then** o sistema recusa o acesso informando que a conta está suspensa pelo administrador.
3. **Given** uma conta suspensa, **When** o administrador seleciona a ação "Reativar Conta", **Then** o status da conta retorna para "ativo" e o leitor volta a poder se autenticar e navegar.
4. **Given** um administrador inspecionando uma conta com múltiplas sessões abertas, **When** ele aciona a revogação de sessões, **Then** todas as sessões ativas daquele usuário são desconectadas forçadamente sem suspender a conta.

---

### User Story 3 - Gestão de Papéis e Proteção contra Auto-Bloqueio (Priority: P3)

Como administrador do sistema, quero promover leitores de confiança a administradores ou rebaixar administradores a usuários convencionais, com salvaguardas invioláveis que impeçam um administrador de revogar o próprio acesso ou suspender a si próprio caso seja o único administrador ativo no sistema.

**Why this priority**: Garante governança de equipe e segurança operacional, prevenindo situações catastróficas de "lockout" em que a plataforma fique sem nenhum administrador com acesso.

**Independent Test**: Um administrador tenta rebaixar seu próprio papel ou suspender a si próprio quando não há outro admin cadastrado; o sistema recusa a ação. Ao promover um segundo usuário a admin, o sistema passa a permitir a alteração do primeiro, garantindo que sempre exista pelo menos um administrador ativo.

**Acceptance Scenarios**:

1. **Given** um usuário com papel de leitor convencional, **When** um administrador aciona a promoção de papel para `admin`, **Then** o papel do usuário é atualizado e ele passa a ter privilégios administrativos no próximo acesso.
2. **Given** um administrador no sistema, **When** ele tenta suspender a sua própria conta ativa, **Then** o sistema recusa a operação com mensagem de proteção contra auto-bloqueio.
3. **Given** o único administrador ativo do sistema, **When** ele tenta rebaixar o seu próprio papel para `user`, **Then** o sistema bloqueia a alteração com alerta de que o sistema não pode ficar sem administradores.
4. **Given** dois ou mais administradores ativos, **When** um administrador altera o papel do outro para `user`, **Then** a alteração é concluída com sucesso.

---

### User Story 4 - Provisionamento e Inicialização Segura do Administrador Inicial (Priority: P4)

Como mantenedor ou operador do servidor local, quero um comando de linha de comando (CLI) determinístico e seguro para criar ou promover a conta de administrador inicial da plataforma via terminal, garantindo que a governança possa ser iniciada em ambientes recém-instalados ou após migrações.

**Why this priority**: Permite que o primeiro administrador seja configurado de forma controlada, auditada e sem depender de inserções manuais vulneráveis diretamente no banco SQLite.

**Independent Test**: Executar o comando CLI em um ambiente de banco limpo ou existente para criar um administrador; em seguida, fazer login na interface web com as credenciais criadas e constatar acesso imediato ao painel administrativo.

**Acceptance Scenarios**:

1. **Given** o terminal do sistema operacional no diretório do projeto, **When** o operador executa o comando CLI de criação de administrador informando credenciais válidas, **Then** a conta de administrador é criada com senha protegida por hash e papel `admin`.
2. **Given** um usuário leitor já existente na base, **When** o operador executa o comando CLI para promover o usuário a administrador informando o `@username`, **Then** a conta é promovida para `admin` com sucesso.
3. **Given** dados inválidos ou senha fraca no comando CLI, **When** o operador submete a operação, **Then** o comando recusa a criação informando os requisitos mínimos de validação.

---

### Edge Cases

- **Tentativa de Acesso Direto à API Administrativa**: Requisições de usuários comuns forjadas diretamente nos endpoints `/api/admin/*` devem ser rejeitadas no nível da dependência do servidor com `403 Forbidden`.
- **E-mails Confidenciais**: O endereço de e-mail de usuários nunca deve vazar em rotas públicas ou sociais da plataforma; apenas administradores autenticados têm visibilidade desse dado na visão de gestão.
- **Sessão Concorrente do Usuário Suspenso**: Se o usuário suspenso estiver no meio de uma leitura ou edição, a próxima chamada de API deve retornar erro de conta inativa, abortando a persistência e redirecionando para login.
- **Proteção do Proprietário Canônico Inicial**: Em modo multiusuário, o usuário de transição canônica inicial pode ser administrado normalmente, desde que as salvaguardas de unicidade de admin sejam respeitadas.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um controle de acesso baseado em papéis (RBAC) com suporte aos papéis `user` (leitor convencional) e `admin` (administrador da plataforma).
- **FR-002**: Todas as operações e rotas sob a área administrativa no servidor DEVEM exigir estritamente que o usuário solicitante possua sessão autenticada e papel `admin`, rejeitando qualquer outro usuário com código HTTP 403 Forbidden.
- **FR-003**: O painel administrativo DEVE disponibilizar uma visão tabular com paginação, busca textual e filtros de status, apresentando identificadores, username, nome de exibição, e-mail (exclusivo para admins), provedor de login, datas de criação e último acesso, status e contagem de estudos.
- **FR-004**: O sistema DEVE permitir ao administrador suspender e reativar contas de usuários a qualquer momento.
- **FR-005**: Ao suspender uma conta de usuário, o sistema DEVE invalidar e revogar imediata e atomicamente todas as sessões ativas existentes no banco de dados (`revoked_at = timestamp`), desconectando forçadamente o usuário de todos os dispositivos e rejeitando requisições subsequentes com HTTP 401/403.
- **FR-006**: O sistema DEVE permitir a alteração de papéis entre `user` e `admin`, com proteção estrita impedindo que o último administrador ativo do sistema seja rebaixado ou suspenso.
- **FR-007**: O sistema DEVE impedir que um administrador suspenda a sua própria conta através da interface.
- **FR-008**: O frontend DEVE exibir um link destacado para a área de Administração (`/admin`) na barra de navegação superior (`App.vue`), visível exclusivamente para usuários autenticados com papel `admin`.
- **FR-009**: O sistema DEVE fornecer um utilitário CLI em Python no terminal (`backend/scripts/create_admin.py` e/ou `python -m app.cli create-admin`) para criação interativa com senha oculta ou promoção determinística de um usuário existente informado via `@username`.
- **FR-010**: O frontend DEVE proteger a rota `/admin` com guardas de navegação que redirecionem leitores não administradores para a página inicial com aviso amigável de acesso restrito.

---

### Key Entities *(include if feature involves data)*

- **User**: Entidade central de usuário que armazena `id`, `username`, `email`, `display_name`, `role` (`user`, `admin`), `status` (`ativo`, `suspenso`), `created_at` e `updated_at`.
- **UserSession**: Registros de sessões ativas do usuário, com identificador de dispositivo, token criptográfico e timestamp de expiração ou revogação.
- **AdminAuditLog**: Registro simples de ações administrativas sensíveis (suspensão, reativação, alteração de papéis) registrando quem executou, qual usuário foi afetado, tipo de ação e data/hora.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Administradores autenticados conseguem carregar a lista de usuários e filtrar por status ou buscar por nome/username em menos de 1 segundo em bases de até 10.000 usuários.
- **SC-002**: Tentativas de acesso a rotas administrativas por usuários não-admin resultam em 100% de bloqueios invioláveis (HTTP 403 Forbidden no backend e redirecionamento no frontend).
- **SC-003**: A suspensão de um usuário interrompe imediatamente o acesso de todas as suas sessões ativas sem exigir reinicialização do servidor.
- **SC-004**: 100% de proteção contra "lockout": o sistema jamais permite que o número de administradores ativos chegue a zero através de operações na aplicação.
- **SC-005**: Cobertura hermética de testes cobrindo todas as 4 histórias de usuário no backend e no frontend, com zero toques no banco de produção.

---

## Assumptions

- O modelo `User` já possui as colunas `role` e `status` no schema SQLite existente, com valores padrão `'user'` e `'ativo'`.
- O sistema de sessões existente (`UserSession`) já possui mecanismo de busca e revogação por usuário.
- O sistema é voltado para implantações locais ou pequenos grupos (instalação pessoal / servidor doméstico compartilhado), logo operações administrativas diretas atendem plenamente às necessidades de governança.
- O isolamento de testes seguirá a regra estrita de bancos temporários (`tmp_path`) e alvos táteis de 44px na interface.
