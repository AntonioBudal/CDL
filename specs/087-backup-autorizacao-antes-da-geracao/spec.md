# Feature Specification: Autorização Antes da Geração de Backup

**Feature Branch**: `087-backup-autorizacao-antes-da-geracao`

**Created**: 2026-10-27

**Status**: Accepted

**Input**: Correção de segurança: as rotas de download de backup geram a cópia do banco antes de verificar se quem pede é administrador.

## 1. Contexto

As rotas `GET /api/backup` (cópia `.db`) e `GET /api/backup/bundle` (pacote `.zip` com banco, capas e manifesto), em `caderno-leitura-0.1/backend/app/routers/backups.py`, declaram a dependência que gera o arquivo (`temporary_backup` / `temporary_backup_bundle`) **antes** da dependência de autorização `_admin: AdminUser`. O FastAPI resolve as dependências na ordem declarada; por isso, uma requisição anônima ou de usuário comum dispara uma cópia completa do acervo (e, no pacote, de todas as capas) em diretório temporário e só depois recebe 401/403.

O arquivo não chega a ser entregue, mas cada requisição não autorizada:

- lê o acervo inteiro e grava uma cópia em disco, ainda que temporária;
- ocupa o banco pela API de backup do SQLite e pode devolver 503/`Retry-After` em vez de 401/403, revelando estado interno;
- permite a qualquer pessoa na rede local/Tailscale provocar trabalho caro de disco e CPU repetidamente.

A rota `POST /api/backup/restore` já declara `_admin` como primeiro parâmetro e não faz parte do problema.

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 — Visitante anônimo não provoca backup (Priority: P1)

Como dono do caderno, quero que uma requisição sem sessão às rotas de backup seja recusada antes de qualquer leitura do acervo, para que ninguém de fora consiga fazer o servidor copiar meus dados.

**Independent Test**: Com autenticação obrigatória, chamar `GET /api/backup` e `GET /api/backup/bundle` sem cookie, com as funções de geração substituídas por registradores de chamada; verificar 401 e zero chamadas.

**Acceptance Scenarios**:

1. **Given** autenticação obrigatória e nenhuma sessão, **When** a pessoa pede `GET /api/backup`, **Then** recebe 401 e nenhuma cópia do banco é gerada.
2. **Given** a mesma situação, **When** a pessoa pede `GET /api/backup/bundle`, **Then** recebe 401 e nenhum pacote é gerado.

### User Story 2 — Usuário comum não provoca backup (Priority: P1)

Como dono do caderno, quero que um usuário autenticado sem papel de administrador seja recusado antes de qualquer leitura do acervo.

**Independent Test**: Mesmo teste da US1, com cookie de sessão de usuário `role="user"`; verificar 403 e zero chamadas.

**Acceptance Scenarios**:

1. **Given** um usuário comum com sessão válida, **When** pede `GET /api/backup` ou `GET /api/backup/bundle`, **Then** recebe 403 ("Acesso restrito a administradores.") e nenhuma geração ocorre.

### User Story 3 — Administrador continua baixando normalmente (Priority: P1)

Como administrador, quero que os downloads de backup continuem funcionando exatamente como antes.

**Independent Test**: Os testes existentes de download e de RBAC para administrador continuam passando.

**Acceptance Scenarios**:

1. **Given** um administrador com sessão válida, **When** pede qualquer das duas rotas, **Then** recebe 200 com o mesmo arquivo, nome, tipo e cabeçalhos de hoje.

## 3. Edge Cases

- **Cabeçalho `Range` em requisição não autorizada**: hoje devolve 416 antes da autenticação. Após a correção, a autorização vem primeiro: anônimo recebe 401 e usuário comum 403, mesmo com `Range`. Para administrador, `Range` continua devolvendo 416.
- **Banco ocupado ou ausente em requisição não autorizada**: não deve mais aparecer 503/404 para quem não é administrador, porque a geração nem é tentada.
- **Autenticação não obrigatória (modo legado)**: o comportamento atual se mantém; a requisição anônima resolve para o proprietário canônico, que é administrador. Esta feature não muda essa regra.

## 4. Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `GET /api/backup` MUST resolver a autorização de administrador antes de chamar `create_database_backup`.
- **FR-002**: `GET /api/backup/bundle` MUST resolver a autorização de administrador antes de chamar `create_backup_bundle`.
- **FR-003**: A garantia de ordem MUST ser estrutural (a geração depende da autorização), e não apenas depender da posição dos parâmetros na função da rota.
- **FR-004**: Respostas a anônimo (401) e a usuário comum (403) MUST manter os mesmos códigos e mensagens de hoje.
- **FR-005**: Respostas a administrador MUST manter conteúdo, nome de arquivo, `media_type` e cabeçalhos (`Cache-Control`, `X-Content-Type-Options`, `Accept-Ranges`) atuais, assim como o 416 para `Range`.
- **FR-006**: Um teste automatizado MUST provar, para anônimo e para usuário comum, nas duas rotas, que a função de geração não é chamada.

### Non-Functional & Governance Restrictions

- **NFR-001**: Testes usam apenas bancos descartáveis em `tmp_path`; nenhum acesso ao banco ativo.
- **NFR-002**: Escopo restrito ao roteador de backups e aos testes; nenhuma mudança em `app/services/backups.py`, em `app/dependencies.py` ou no frontend.
- **NFR-003**: Pronto quando o `pytest` do backend estiver verde, salvo a falha ambiental conhecida `test_iniciar_rejects_relative_database_path` (falta `frontend/dist` no worktree).
- **NFR-004**: Um commit único da feature, em português, após o aceite do usuário.

## 5. Success Criteria *(mandatory)*

- **SC-001**: Em 4 combinações (2 rotas × anônimo/usuário comum), o registrador de chamadas da função de geração fica vazio e o status é 401/403.
- **SC-002**: Os testes existentes de backup e de RBAC (`test_backup_bundle.py`, `test_security_privileged_access.py`, `test_admin_and_rbac.py` e demais) continuam passando sem alteração de expectativa.
- **SC-003**: O novo teste falha contra o código atual (comprova o defeito) e passa após a correção.

## 6. Assumptions & Dependencies

- O FastAPI resolve subdependências antes da dependência que as declara; uma dependência que recebe `AdminUser` como parâmetro só executa seu corpo depois da autorização. Com o cache por requisição, `require_admin` executa uma única vez mesmo se citado também na rota.
- A fixture de RBAC usada em `test_security_privileged_access.py` (usuários admin e comum em banco `tmp_path`, `REQUIRE_AUTH=true`) serve de modelo para o teste novo.
