# Feature Specification: Isolamento do Banco Ativo na Suíte de Testes do Backend

**Feature Branch**: `097-isolamento-banco-testes`

> Renumerada de 086 para 097 em 2026-11-07, ao entrar no `main` (o 086 já era `086-digitalizar-caderno-estudo`). Feita no branch `claude/intelligent-perlman-c530cd` em 2026-10-27.

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "A função `lifespan` em `backend/app/main.py` chama `get_session()` importado diretamente de `app.db.session` para purgar a lixeira, sincronizar categorias canônicas e purgar notificações. Os testes que usam `with TestClient(app)` substituem a sessão só via `app.dependency_overrides[get_session]`, o que não afeta a chamada direta do lifespan. Resultado: rodar `pytest` conecta ao banco ativo `backend/data/caderno.db` e executa essa manutenção nele, violando a Constituição II.1 e o AGENTS.md. Corrigir de forma que nenhum teste abra o banco ativo, com um teste que falhe se `get_database_path()` resolver para `backend/data/caderno.db` durante a suíte."

## Contexto e diagnóstico (fatos verificados no código, sem abrir o banco)

- `backend/app/main.py`, função `lifespan`: importa `get_session` de `app.db.session` e itera `for session in get_session()` para chamar `purge_expired_trash`, `sync_canonical_categories`, `purge_expired_notifications` e `commit_changes`. Qualquer exceção é engolida (`except Exception: pass`).
- `backend/app/db/session.py`: `get_session()` → `get_engine()` → `_get_engine_for_path(get_database_path())`. `create_sqlite_engine` cria o diretório pai e o SQLite cria o arquivo se ele não existir.
- `backend/app/core/config.py`, `get_database_path()`: sem `CADERNO_DATABASE_PATH` no ambiente, devolve `BACKEND_DIR / "data" / "caderno.db"` — o banco ativo.
- `app.dependency_overrides[get_session]` só afeta a injeção de dependências do FastAPI nas rotas; a chamada direta no `lifespan` continua usando o `get_session` original.
- 20 arquivos de teste entram em `with TestClient(app)` (ou `create_app`) e disparam o `lifespan`. Vários deles (ex.: `tests/conftest.py` fixture `google_auth_client`, `test_account_export.py`, `test_account_lifecycle.py`, `test_dashboard.py`) não definem `CADERNO_DATABASE_PATH`; nesses, a manutenção roda contra o banco ativo, com `commit`.
- Efeitos colaterais do mesmo caminho padrão: `get_covers_dir()`, `get_avatars_dir()` e `get_backup_dir()` derivam seus diretórios do pai do banco ativo quando não recebem caminho explícito, então também podem criar/escrever em `backend/data/` durante os testes.
- `tests/test_database.py` (linha ~192) remove `CADERNO_DATABASE_PATH` de propósito num subprocesso que **só imprime** o caminho resolvido para validar o padrão; esse teste não abre o arquivo e deve continuar válido.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rodar a suíte sem tocar no acervo (Priority: P1)

Como pessoa que mantém o Leitorum, quero rodar `pytest` no backend sabendo que nenhum teste abre, cria, lê ou grava `backend/data/caderno.db`, para não arriscar a lixeira, as categorias e as notificações do meu acervo real a cada execução.

**Why this priority**: É uma violação ativa da Constituição II.1: cada execução da suíte hoje pode purgar lixeira e notificações e reescrever categorias no banco real.

**Independent Test**: Numa cópia de trabalho sem `backend/data/caderno.db`, rodar a suíte completa e confirmar que o arquivo continua inexistente e que nenhum diretório `covers/`, `avatars/` ou `backups/` foi criado em `backend/data/`.

**Acceptance Scenarios**:

1. **Given** que o ambiente não define `CADERNO_DATABASE_PATH`, **When** a suíte inicia, **Then** todo código executado no processo de teste resolve o banco para um arquivo dentro de um diretório temporário exclusivo da execução.
2. **Given** um teste que entra em `with TestClient(app)` sem configurar banco próprio, **When** o `lifespan` executa a manutenção, **Then** ela atua (ou falha silenciosamente) sobre o banco temporário, nunca sobre `backend/data/caderno.db`.
3. **Given** um teste que define seu próprio `CADERNO_DATABASE_PATH` via `monkeypatch`, **When** ele termina, **Then** o valor volta ao caminho temporário da sessão, e não à ausência da variável.

---

### User Story 2 - Guarda automática contra regressão (Priority: P1)

Como pessoa que mantém o Leitorum, quero que a suíte falhe de forma explícita se, no futuro, alguma mudança fizer o processo de teste resolver ou abrir o banco ativo, para que a proteção não dependa de memória ou revisão manual.

**Why this priority**: Sem guarda, uma nova fixture ou a remoção acidental do isolamento reintroduz o problema sem sinal nenhum (o `lifespan` engole exceções).

**Independent Test**: Remover temporariamente o isolamento e verificar que o teste-guarda falha; restaurar e verificar que passa.

**Acceptance Scenarios**:

1. **Given** a suíte em execução, **When** o teste-guarda roda, **Then** ele afirma que `get_database_path()` não é `BACKEND_DIR / "data" / "caderno.db"` e que aponta para dentro do diretório temporário da sessão.
2. **Given** que algum código do processo de teste tente criar um engine SQLAlchemy para o caminho do banco ativo, **When** a suíte termina, **Then** a execução falha apontando a tentativa.

---

### Edge Cases

- Teste que roda `iniciar.py` ou `alembic` em subprocesso herdando o ambiente: herda o caminho temporário da sessão, o que é desejado.
- Teste que remove a variável num subprocesso só para imprimir o caminho padrão (`test_database.py`): permitido, porque não abre o arquivo.
- Teste que valida rejeição de caminho relativo (`test_backup_pre_upgrade.py`) usa `monkeypatch.setenv` com valor inválido: continua funcionando e o valor é restaurado ao fim.
- Banco temporário da sessão vazio, sem tabelas: a manutenção do `lifespan` falha e é engolida, como já ocorre hoje com bancos sem schema; nenhum teste depende dela.
- Execução com `pytest -k`/arquivo único: o isolamento vale igualmente, pois é configurado no `conftest.py` raiz dos testes.
- Execução paralela futura (`pytest-xdist`): cada processo deve obter seu próprio diretório temporário (fora do escopo instalar xdist; apenas não impedir).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Antes do primeiro teste, a suíte do backend MUST definir `CADERNO_DATABASE_PATH` para um caminho absoluto dentro de um diretório temporário exclusivo da execução, e restaurar o ambiente original ao final.
- **FR-002**: Nenhum código executado no processo do pytest MUST criar engine, conectar ou criar arquivo em `backend/data/caderno.db`.
- **FR-003**: Os diretórios derivados do banco (`covers/`, `avatars/`, `backups/`) MUST, por consequência, ficar sob o diretório temporário quando não houver configuração explícita.
- **FR-004**: A suíte MUST conter um teste-guarda que falhe se `get_database_path()` resolver para `BACKEND_DIR / "data" / "caderno.db"` durante a execução.
- **FR-005**: A suíte MUST falhar se qualquer tentativa de criar engine para o caminho do banco ativo ocorrer no processo de teste, mesmo que a exceção seja engolida pelo código da aplicação (caso do `lifespan`).
- **FR-006**: Testes existentes que configuram seu próprio banco via `monkeypatch.setenv("CADERNO_DATABASE_PATH", ...)` MUST continuar funcionando sem alteração.
- **FR-007**: O comportamento em produção (`iniciar.py`, servidor real) MUST permanecer inalterado: sem a variável, o padrão continua sendo `backend/data/caderno.db`.

### Decisão técnica proposta (a confirmar no plano)

- Correção restrita a `backend/tests/conftest.py`: fixture `autouse` de escopo de sessão que cria um diretório temporário (`tmp_path_factory`) e define `CADERNO_DATABASE_PATH`; mais um envoltório em `app.db.session.create_sqlite_engine` que registra (e recusa) tentativas para o caminho do banco ativo, verificado ao fim da sessão.
- Novo arquivo `backend/tests/test_active_database_isolation.py` com o teste-guarda.
- Alternativa descartada como solução principal: fazer o `lifespan` pular a manutenção sob pytest. Ela altera código de produção, deixa sem cobertura os outros consumidores de `get_database_path()` (capas, avatares, backups, `frontend.py`) e não protege contra novas chamadas diretas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Numa cópia de trabalho onde `backend/data/caderno.db` não existe, após `pytest` completo o arquivo continua inexistente e `backend/data/` contém apenas o que já continha antes.
- **SC-002**: O teste-guarda passa com o isolamento ativo e falha quando o isolamento é desativado (verificação feita uma vez durante a implementação, sem abrir o banco real).
- **SC-003**: A suíte completa do backend termina com o mesmo número de testes aprovados que antes da mudança, mais os novos testes de guarda, sem falhas novas.
- **SC-004**: Nenhum arquivo em `backend/app/` é alterado.

## Assumptions

- O banco ativo real (`caderno-leitura-0.1/backend/data/caderno.db` na cópia principal) não será aberto, lido, copiado nem inspecionado em nenhuma etapa; toda verificação é feita no worktree, onde esse arquivo não existe.
- O frontend (`npm test`) não acessa o banco e fica fora do escopo.
- Esta correção não pertence ao Roadmap 0.5 e não altera o estado de F01–F10.
- Não há necessidade de `speckit.clarify` com perguntas ao usuário: as decisões abertas estão registradas como proposta técnica acima e serão fixadas no plano.
