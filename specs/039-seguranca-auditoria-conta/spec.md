# Feature Specification: F10 — Segurança, Auditoria, Ciclo de Vida da Conta e Google OAuth

**Feature Branch**: `039-seguranca-auditoria-conta`

**Created**: 2026-09-26

**Status**: Ready for Planning

**Input**: User description: "F10 — Segurança, Auditoria e Ciclo de Vida da Conta: Consolidar a blindagem da aplicação, atender às melhores práticas do OWASP e conformidade com diretrizes de privacidade (LGPD / ANPD), incluindo trilha de auditoria e exportação completa de dados. Adendo Crítico: expandir para incluir autenticação Login com Google (OAuth 2.0) com botão na tela inicial, rotas de redirecionamento/callback e provisionamento/auto-associação implícita por google_id e email."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Proteção contra Ataques de Força Bruta e Enumeração (Priority: P1)

Como leitor do sistema, desejo que minhas contas e rotas sensíveis estejam protegidas contra tentativas automatizadas de adivinhação de senhas, força bruta e descoberta de contas existentes, garantindo que o servidor permaneça estável e seguro mesmo em rede local compartilhada.

**Why this priority**: É a primeira linha de defesa contra comprometimento de credenciais e abusos na camada de transporte HTTP (OWASP Top 10). Sem proteção de taxa e mensagens genéricas, atacantes podem sobrecarregar o SQLite ou enumerar usuários cadastrados.

**Independent Test**: Simular 6 tentativas consecutivas de login incorreto a partir do mesmo IP/origem; a partir da 6ª tentativa, a API deve responder imediatamente com `HTTP 429 Too Many Requests` e cabeçalho `Retry-After`. Além disso, submeter credenciais incorretas com e-mails existentes e inexistentes e verificar que ambas retornam a mensagem idêntica "Credenciais inválidas" (`HTTP 401 Unauthorized`).

**Acceptance Scenarios**:

1. **Given** um cliente não autenticado, **When** enviar mais de 5 tentativas de autenticação com falha em `/api/auth/login` dentro de uma janela de 5 minutos, **Then** o sistema bloqueia requisições adicionais com `HTTP 429 Too Many Requests` contendo o tempo restante para nova tentativa.
2. **Given** uma requisição de login com e-mail inexistente, e outra com e-mail existente mas senha incorreta, **When** processadas pela API, **Then** ambas retornam exatamente a mesma resposta genérica de erro sem expor a existência do usuário.
3. **Given** um período de cooldown esgotado, **When** o cliente tentar novamente com credenciais corretas, **Then** a requisição é processada normalmente com sucesso.

---

### User Story 2 - Autenticação Prática e Ágil com Google OAuth 2.0 (Priority: P1)

Como leitor do sistema, desejo acessar a aplicação clicando em "Entrar com o Google" na tela inicial ou tela de login, sem ter a obrigatoriedade de criar ou memorizar uma senha local, conectando-me imediatamente ao meu acervo com segurança e praticidade.

**Why this priority**: Atende à exigência prioritária de experiência do usuário e usabilidade rápida, reduzindo o atrito de entrada e aproveitando os componentes de identidade externa e Google Identity Services (GIS) já estruturados na aplicação.

**Independent Test**: Acessar a tela inicial/login sem estar autenticado, clicar no botão de login com o Google, concluir a autorização do provedor e verificar que o leitor é autenticado imediatamente. Se for o primeiro acesso com este e-mail do Google, uma nova conta de leitor é criada implicitamente e a sessão é iniciada sem exigir definição de senha.

**Acceptance Scenarios**:

1. **Given** um visitante na tela inicial de login (`LoginView.vue`), **When** visualizar a interface, **Then** um botão destacado e acessível "Entrar com o Google" está disponível e pronto para interação.
2. **Given** uma autenticação bem-sucedida pelo Google com uma conta cujo `google_id` ou e-mail ainda não existe no sistema, **When** o token for processado pela API, **Then** o sistema cria implicitamente um novo `User` com perfil ativo, vincula a `ExternalIdentity(provider='google')` e inicia uma sessão autenticada persistente.
3. **Given** um leitor já cadastrado localmente com o mesmo e-mail verificado retornado pelo Google, **When** ele clicar em "Entrar com o Google", **Then** o sistema auto-vincula com segurança a credencial Google ao leitor existente e estabelece a sessão sem duplicar contas.
4. **Given** falha na validação do token do Google (expirado, forjado ou cancelado pelo usuário), **When** a resposta retornar, **Then** o sistema exibe mensagem amigável de erro e registra a falha na trilha de auditoria sem comprometer o estado da aplicação.

---

### User Story 3 - Trilha de Auditoria Estruturada e Sem Segredos (Priority: P2)

Como administrador do sistema, desejo consultar um registro imutável de eventos de segurança da aplicação para monitorar atividades sensíveis (logins locais e via Google, alterações de permissão, exclusões e mudanças de privilégio), com garantia de que senhas e chaves privadas nunca sejam registradas.

**Why this priority**: Fundamental para conformidade com normas de governança e detecção de anomalias operacionais, além de manter conformidade estrita com o princípio constitucional de privacidade absoluta (zero segredos e dados pessoais em logs).

**Independent Test**: Executar ações críticas (login com sucesso, login com falha, login com Google, alteração de senha, concessão de perfil admin, desativação de conta) e verificar via rota administrativa que os registros correspondentes foram inseridos em `AuditLog`, confirmando a ausência total de senhas em texto puro, hashes de senha e tokens nos campos de detalhes.

**Acceptance Scenarios**:

1. **Given** um usuário que efetua login com sucesso ou falha (local ou via Google), **When** o evento é processado, **Then** um registro de auditoria é gravado com tipo de evento, timestamp UTC, endereço IP, user-agent e identificador de usuário (quando aplicável).
2. **Given** uma alteração de senha ou permissão de recurso, **When** o evento é auditado, **Then** o registro contém apenas os metadados da operação (ex.: "senha alterada", "role promovido para admin"), omitindo qualquer credencial ou token.
3. **Given** um administrador autenticado, **When** acessar a listagem de auditoria via painel administrativo, **Then** os eventos são exibidos em ordem cronológica reversa com paginação e filtros por severidade e tipo.
4. **Given** um usuário com papel comum (`USER`), **When** tentar acessar a trilha de auditoria, **Then** o sistema rejeita a requisição com `HTTP 403 Forbidden`.

---

### User Story 4 - Ciclo de Vida da Conta: Desativação Temporária e Exclusão Definitiva (Priority: P3)

Como titular da conta (em conformidade com a LGPD), desejo ter o controle total sobre a permanência dos meus dados na plataforma, podendo desativar minha conta temporariamente ou solicitar a exclusão definitiva do meu cadastro e acervo, mediante confirmação segura de senha.

**Why this priority**: Atende aos direitos fundamentais de autodeterminação informativa do titular (LGPD Art. 18), permitindo ao leitor pausar sua presença ou revogar seu cadastro com segurança e proteção contra exclusões acidentais.

**Independent Test**: Desativar a conta na central de configurações e verificar que todas as sessões ativas são revogadas e o perfil fica invisível a amigos. Em seguida, ao tentar logar com credenciais válidas, verificar a tela intermediária de reativação com confirmação explícita. Para a exclusão definitiva, solicitar a exclusão com senha e certificar que todos os livros, capítulos e estudos são excluídos em cascata física transacional do SQLite.

**Acceptance Scenarios**:

1. **Given** um usuário ativo nas configurações de conta, **When** selecionar "Desativar conta temporariamente" e confirmar sua senha, **Then** todas as suas sessões ativas são revogadas, seu status muda para `deactivated` e seu perfil deixa de aparecer nas buscas e na lista de amigos.
2. **Given** uma conta desativada, **When** o usuário submeter credenciais válidas de login (locais ou Google), **Then** o sistema bloqueia o acesso automático direto e exibe confirmação explícita em tela: *"Sua conta está desativada. Deseja reativá-la agora?"*, reativando o status para `active` somente após a confirmação do titular.
3. **Given** um usuário que decide encerrar definitivamente sua conta, **When** selecionar "Excluir conta", digitar a senha e confirmar o termo de exclusão definitiva, **Then** o sistema executa exclusão física transacional em cascata, eliminando do banco todos os livros, capítulos, estudos, anotações, comentários, categorias e permissões vinculadas, sem deixar registros órfãos.

---

### User Story 5 - Portabilidade e Exportação Completa de Dados do Titular (Priority: P4)

Como leitor do sistema, desejo baixar uma cópia integral de todo o meu acervo e dados de uso (livros, capítulos, estudos, categorias, relações e preferências) em um arquivo zip aberto e legível, garantindo portabilidade de dados sem dependência de plataforma fechada.

**Why this priority**: Cumpre o requisito explícito da F10 e a diretriz de portabilidade da LGPD (Art. 18, V), além de reforçar o compromisso de que os estudos pertencem exclusivamente ao usuário.

**Independent Test**: Executar uma chamada autenticada a `GET /api/account/export` para uma conta com livros, capítulos, estudos e categorias e verificar que o arquivo retornado é um `.zip` válido contendo hierarquia de pastas por livro e capítulo com arquivos `.md` bem formatados para os estudos e o arquivo `dados_acervo.json` estruturado na raiz.

**Acceptance Scenarios**:

1. **Given** um usuário autenticado com acervo registrado, **When** solicitar a exportação de dados em "Minha Conta", **Then** o sistema gera sob demanda e faz o download de um arquivo `caderno-dados-[username]-[data].zip`.
2. **Given** o arquivo ZIP descompactado, **When** inspecionado, **Then** contém pastas organizadas hierarquicamente por `Nome do Livro/Nome do Capítulo/Nome do Estudo.md` em Markdown legível e um arquivo `dados_acervo.json` na raiz com o histórico completo, metadados, categorias e relações semânticas.
3. **Given** uma requisição de exportação em andamento ou repetida em curto intervalo, **When** submetida novamente, **Then** o sistema utiliza cache temporário seguro ou limita requisições concorrentes para poupar I/O de disco.

---

### Edge Cases

- **Rate limiting em rede local / Tailscale**: Como múltiplos nós podem compartilhar o mesmo IP de gateway ou interface de rede, o rate limiting deve combinar endereço IP com endpoint e chave identificadora de conta (ou header de fingerprint) para evitar bloqueio indevido de usuários legítimos distintos na mesma sub-rede.
- **Tentativa de exclusão de usuário único ou admin inicial**: Se a conta a ser excluída for o único administrador do sistema, o sistema deve impedir a exclusão sem antes transferir o papel de administrador para outra conta ativa, evitando que o sistema fique sem administração.
- **Estudos compartilhados após exclusão ou desativação**: Recursos compartilhados pelo usuário com amigos devem deixar de ser visíveis imediatamente na biblioteca compartilhada dos amigos assim que a conta for desativada ou excluída.
- **Usuário criado exclusivamente via Google que deseja excluir a conta**: Se o usuário não possui senha local definida, a exclusão da conta deve exigir confirmação de reautenticação com Google ou digitação obrigatória do `@username` exato e termo de consentimento.
- **Falha transacional durante exportação ou exclusão**: Todas as etapas de limpeza de banco e exclusão de arquivos de capa devem ser executadas em transação atômica; qualquer falha desfaz as alterações e preserva a integridade referencial do SQLite.
- **Requisicões concorrentes com conta recém-desativada**: Sessões existentes devem ser invalidadas no banco de dados imediatamente no momento da desativação, fazendo com que qualquer requisição em trânsito com o token antigo receba `HTTP 401 Unauthorized`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE implementar controle de taxa de requisições (rate limiting) em endpoints sensíveis de autenticação (`/api/auth/login`, `/api/auth/register`, `/api/auth/google`, endpoints de redefinição/troca de senha), configurável por padrão para 5 tentativas a cada 5 minutos por cliente.
- **FR-002**: O sistema DEVE retornar código de status `HTTP 429 Too Many Requests` com cabeçalho `Retry-After` (em segundos) e mensagem explicativa em português sempre que o limite for ultrapassado.
- **FR-003**: O sistema DEVE padronizar mensagens de erro em tentativas inválidas de autenticação para evitar enumeração de contas, retornando `HTTP 401 Unauthorized` com a mensagem unificada "Credenciais inválidas".
- **FR-004**: O sistema DEVE disponibilizar botão visível, intuitivo e com alvo de toque adequado "Entrar com o Google" na tela inicial e de autenticação (`LoginView.vue` e `RegisterView.vue`).
- **FR-005**: O sistema DEVE suportar a autenticação com Google via Google Identity Services (GIS com ID Token em `/api/auth/google`) e fluxo OAuth 2.0 com rotas dedicadas de redirecionamento e callback (`/api/auth/google/login` e `/api/auth/google/callback`).
- **FR-006**: Ao processar uma autenticação válida do Google, o sistema DEVE:
  - Identificar o leitor caso o `google_id` (`sub`) já esteja registrado em `ExternalIdentity`.
  - Auto-vincular a identidade Google à conta existente caso já haja um usuário com o mesmo e-mail verificado pelo Google.
  - Criar implicitamente uma nova conta de usuário ativa caso o e-mail não exista previamente, com perfil padrão e sem exigência de senha local.
- **FR-007**: O sistema DEVE criar a entidade `AuditLog` para registro imutável de eventos de segurança: logins locais com sucesso/falha, logins via Google, alteração de senha, concessão/revogação de privilégios de administrador, suspensão, desativação, reativação, exclusão de conta e alteração de regras de compartilhamento.
- **FR-008**: O sistema DEVE garantir que nenhum segredo (senhas em texto puro, hashes de senha, tokens de sessão, credenciais externas) seja gravado na tabela `AuditLog` ou em logs de sistema.
- **FR-009**: O sistema DEVE disponibilizar endpoint administrativo autenticado (`GET /api/admin/audit-logs`) restrito a usuários com papel `ADMIN`, com paginação, ordenação cronológica decrescente e filtros por tipo de evento e intervalo de datas.
- **FR-010**: O sistema DEVE permitir que o próprio usuário desative temporariamente sua conta através de endpoint autenticado (`POST /api/account/deactivate`), exigindo confirmação de credenciais (senha local ou confirmação Google).
- **FR-011**: Ao desativar uma conta, o sistema DEVE encerrar imediatamente todas as sessões ativas do usuário, definir `status = 'deactivated'`, e ocultar o perfil, amigos e acervos de todas as buscas e listagens públicas.
- **FR-012**: Caso um usuário com conta desativada submeta credenciais válidas de login (local ou Google), o sistema DEVE retornar resposta indicativa de conta desativada e exibir tela de confirmação explícita de reativação; a reativação para `status = 'active'` só ocorre após confirmação do titular via endpoint `POST /api/account/reactivate`.
- **FR-013**: O sistema DEVE permitir a exclusão definitiva da conta através de endpoint autenticado (`DELETE /api/account`), exigindo confirmação explícita de credenciais e termo de ciência.
- **FR-014**: Ao confirmar a exclusão definitiva, o sistema DEVE executar exclusão física transacional em cascata de todos os livros, capítulos, estudos, anotações, categorias e permissões vinculadas ao usuário no SQLite, revogando todas as sessões.
- **FR-015**: O sistema DEVE disponibilizar endpoint autenticado (`GET /api/account/export`) que gere dinamicamente um arquivo ZIP de portabilidade com estrutura hierárquica por pastas (`Nome do Livro/Nome do Capítulo/Nome do Estudo.md`) e um arquivo `dados_acervo.json` com histórico, relações e metadados.
- **FR-016**: O sistema DEVE exibir na interface de Configurações (`SettingsView.vue`) uma nova seção dedicada a "Segurança e Privacidade", permitindo ao usuário visualizar sessões ativas, status de vinculação com o Google, desativar sua conta, solicitar a exclusão de dados e baixar a exportação completa de seu acervo.

### Key Entities *(include if feature involves data)*

- **AuditLog**:
  - `id`: UUID (Chave Primária)
  - `created_at`: DateTime UTC
  - `event_type`: String/Enum (ex.: `login_success`, `login_failed`, `login_google`, `password_changed`, `role_changed`, `account_deactivated`, `account_reactivated`, `account_deleted`, `account_exported`)
  - `user_id`: UUID (Chave Estrangeira para `users.id`, anulável para tentativas com usuário inexistente ou exclusões)
  - `actor_username`: String (Nome ou identificador informado na requisição para rastreabilidade)
  - `ip_address`: String (IP do cliente solicitante, mascarado/sanitizado se configurado)
  - `user_agent`: String (Identificador do navegador/dispositivo)
  - `details`: JSON/Texto (Dicionário de metadados contextuais estritamente não sensíveis)

- **ExternalIdentity**:
  - `id`: UUID (Chave Primária)
  - `user_id`: UUID (Chave Estrangeira para `users.id`)
  - `provider`: String (ex.: `google`)
  - `provider_user_id`: String (Identificador único e estável do provedor, claim `sub`)
  - `email`: String (E-mail associado no provedor externo)
  - `created_at`: DateTime UTC

- **User (Campos de Ciclo de Vida e Auditoria)**:
  - `status`: Enum estendido (`active`, `suspended`, `deactivated`, `deleted`)
  - `deactivated_at`: DateTime UTC (Data/hora em que a conta foi desativada, se aplicável)
  - `deleted_at`: DateTime UTC (Data/hora de exclusão definitiva)
  - `failed_login_attempts`: Integer (Contador para rate limiting e bloqueio temporário por usuário)
  - `locked_until`: DateTime UTC (Timestamp de término do bloqueio temporário por tentativas excessivas)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Tentativas de força bruta são interceptadas em no máximo 5 requisições inválidas consecutivas por cliente, respondendo com `HTTP 429` em menos de 20ms sem sobrecarga de processamento no banco SQLite.
- **SC-002**: O fluxo de autenticação com Google autentica ou provisiona uma conta em menos de 1 segundo após a autorização do provedor, sem exigir senha local.
- **SC-003**: 100% dos eventos críticos de segurança (logins locais/Google, trocas de senha, alterações de papel, desativação, reativação e exclusão) são auditados com sucesso em `AuditLog`, com verificação automatizada de ausência de segredos em 100% das asserções de teste.
- **SC-004**: A operação de desativação temporária de conta revoga 100% das sessões ativas do usuário e torna o perfil e os recursos invisíveis em menos de 100ms.
- **SC-005**: A exclusão definitiva remove transacionalmente em cascata 100% dos registros do usuário no SQLite sem deixar registros órfãos ou quebrar chaves estrangeiras (`PRAGMA foreign_key_check` limpo).
- **SC-006**: O endpoint de exportação de dados compila o arquivo ZIP estruturado com pastas Markdown e `dados_acervo.json` em menos de 3 segundos para acervos com até 500 estudos.
- **SC-007**: A interface de configurações no frontend apresenta a nova área de "Segurança e Privacidade" responsiva em resoluções desktop e mobile, com confirmações modais claras para ações destrutivas sem emojis informais.

## Assumptions

- O controle de rate limiting pode operar com armazenamento em memória no processo Uvicorn local (utilizando estrutura de janela deslizante baseada em tempo) ou cache leve no banco, suficiente para a arquitetura de processo único local do Caderno de Leitura.
- A aplicação continuará operando localmente via `iniciar.py` no PC, com acesso móvel eventual via rede Tailscale / IP local.
- Para o login com Google funcionar plenamente em ambiente local, as credenciais `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` devem ser configuradas nas variáveis de ambiente, com fallbacks amigáveis na UI caso estejam ausentes.
- A exclusão de uma conta com papel único de `admin` será bloqueada pela aplicação a menos que haja outro administrador cadastrado ou o sistema passe por procedimento explícito de bootstrap.
- A exportação em formato ZIP não inclui arquivos binários de sistema ou dependências, focando estritamente no conteúdo autoral do usuário (Markdown e JSON).
