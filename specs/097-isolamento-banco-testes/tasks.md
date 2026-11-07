# Tasks: Isolamento do Banco Ativo na Suíte de Testes do Backend

**Input**: Design documents from `specs/097-isolamento-banco-testes/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md)

## Organization

As tarefas seguem as decisões D1–D5 do plano e estão mapeadas às histórias US1 (rodar a suíte sem tocar no acervo) e US2 (guarda automática contra regressão). Todo comando roda **no worktree**. Nenhuma tarefa abre, lê, copia ou consulta metadados de `C:\Users\User\caderno\caderno-leitura-0.1\backend\data\caderno.db`.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Tarefa executável em paralelo (arquivos distintos, sem dependência mútua)
- **[Story]**: Mapeamento para a história de usuário (US1, US2)
- `BACKEND` = `caderno-leitura-0.1/backend` dentro do worktree

---

## Phase 1: Setup — interpretador seguro e linha de base

**Propósito**: Garantir que os testes importem o código do worktree, e não o da cópia principal, antes de rodar qualquer coisa.

- [x] T001 Escolher o interpretador. Candidato: `C:\Users\User\caderno\caderno-leitura-0.1\backend\.venv\Scripts\python.exe` (o worktree não tem venv). Confirmar a versão 3.13 e listar **só os nomes** de arquivos `*.pth`, `__editable__*` e `*.egg-link` em `Lib\site-packages`, para saber se algum aponta para o `backend` da cópia principal.
- [x] T002 Bloqueio de segurança: a partir de `BACKEND`, com `CADERNO_DATABASE_PATH` apontando para um arquivo na pasta de rascunho da sessão, rodar `python -c` que importa só `app.core.config` e imprime `app.__file__`, `BACKEND_DIR` e `get_database_path()`. **Se `app.__file__` ou `BACKEND_DIR` apontar para fora do worktree, parar** e reportar, sem rodar `pytest`.
- [x] T003 Linha de base (US1, reproduz o defeito): conferir que `BACKEND/data/` contém só `.gitignore` e rodar `python -m pytest -q -p no:cacheprovider` a partir de `BACKEND`. Registrar aprovados, falhas e pulados. Depois, listar `BACKEND/data/`: o `caderno.db` criado no worktree e as pastas `covers/`, `avatars/` e `backups/` evidenciam o problema. Esse banco é sintético. Remover só o que a execução criou em `BACKEND/data/` do worktree, mantendo o `.gitignore`.

**Checkpoint**: interpretador confirmado como seguro; número da linha de base registrado.

---

## Phase 2: Foundational — isolamento e guarda no `conftest.py` (D1–D3)

**Propósito**: Criar o mecanismo que garante US1 e US2. Todas as tarefas desta fase alteram `BACKEND/tests/conftest.py` e por isso são sequenciais.

- [x] T004 [US1] Inserir no topo de `BACKEND/tests/conftest.py`, antes de `from app.db...` e `from app.main import app`, o bloco de isolamento:
  - importar `BACKEND_DIR`;
  - definir `_PROTECTED_DB_PATH = BACKEND_DIR / "data" / "caderno.db"`;
  - criar `_SESSION_DB_DIR` com `tempfile.mkdtemp(prefix="leitorum-pytest-")`;
  - guardar o valor original de `CADERNO_DATABASE_PATH`;
  - sobrescrever a variável com `_SESSION_DB_DIR / "caderno.db"`.
- [x] T005 [US2] No mesmo bloco, implementar `_connect_target_path()` (normalização de `str`, `bytes`, `PathLike`, URI `file:` com query e `%xx`; ignorar `:memory:` e vazio), `_is_protected_target()` (que também cobre `-wal`, `-shm` e `-journal`, comparando com `normcase(realpath)`) e `_guarded_sqlite_connect`. Essa última registra o alvo em `_ACTIVE_DB_ATTEMPTS` e levanta `RuntimeError` antes de delegar. Instalar a guarda com `sqlite3.connect = _guarded_sqlite_connect`, guardando o original.
- [x] T006 [US2] Adicionar a fixture `autouse` de função `_fail_on_active_database_attempt`. Depois de cada teste, ela copia e limpa `_ACTIVE_DB_ATTEMPTS` e chama `pytest.fail` se houver tentativas. Adicionar também a fixture de sessão `session_database_dir`, que expõe `_SESSION_DB_DIR`.
- [x] T007 [US1] Adicionar o hook `pytest_sessionfinish` (força `exitstatus = 1` se restarem tentativas) e o hook `pytest_unconfigure`. Este restaura `sqlite3.connect`, restaura ou remove `CADERNO_DATABASE_PATH` e apaga `_SESSION_DB_DIR` com `ignore_errors=True`.
- [x] T008 [US2] Conferir em processo que a guarda pega o caminho do SQLAlchemy. Com um alvo falso em `tmp_path`, `create_sqlite_engine(alvo).connect()` deve levantar `RuntimeError` pela guarda, porque o dialeto `pysqlite` chama `sqlite3.connect` como atributo do módulo. Se não pegar, voltar ao plano antes de seguir.

**Checkpoint**: o `conftest.py` carrega sem erro (`pytest --collect-only -q`), e `BACKEND/data/` continua só com `.gitignore`.

---

## Phase 3: User Story 2 — testes-guarda (D4)

**Objetivo**: Uma regressão no isolamento falha a suíte de forma explícita.
**Teste independente**: `pytest tests/test_active_database_isolation.py` passa com o isolamento e falha sem ele (T012).

- [x] T009 [US2] Criar `BACKEND/tests/test_active_database_isolation.py` com os seis testes da tabela D4 do plano: caminho fora do banco ativo, variável no diretório da sessão, `sqlite3.connect` instalado como guarda, bloqueio de alvo falso (com quatro grafias e sem criar o arquivo), permissão para outros bancos e `:memory:`, e `lifespan` sem override conectando ao banco da sessão. Nenhum teste chama `sqlite3.connect` sobre `_PROTECTED_DB_PATH` real.
- [x] T010 [US2] Rodar só o arquivo novo e corrigir até passar.

---

## Phase 4: User Story 1 — suíte completa isolada

**Objetivo**: A suíte inteira roda sem tocar no banco ativo.
**Teste independente**: depois do `pytest` completo, `BACKEND/data/` do worktree contém só `.gitignore`.

- [x] T011 [US1] Rodar `python -m pytest -q -p no:cacheprovider` a partir de `BACKEND`. Esperado: aprovados = linha de base (T003) + 6, nenhuma falha nova e nenhuma tentativa barrada pela guarda. Se a guarda acusar algum teste, investigar o caminho de código e corrigir **no teste ou no `conftest.py`**, nunca em `backend/app/`.
- [x] T012 [US2] Verificar SC-002: comentar temporariamente a linha que define `CADERNO_DATABASE_PATH` em `conftest.py` e rodar só `tests/test_active_database_isolation.py`. Ele deve falhar. Restaurar a linha, rodar de novo (deve passar) e limpar o que a execução criou em `BACKEND/data/` do worktree.
- [x] T013 [US1] Listar `BACKEND/data/` e confirmar que contém só `.gitignore` (SC-001).

---

## Phase 5: Polish — documentação e conferência final

- [x] T014 [P] Atualizar a frase de `caderno-leitura-0.1/docs/contexto/AMBIENTE-E-VALIDACAO.md:64` para descrever o isolamento real (D5).
- [x] T015 [P] Registrar no fim de `specs/097-isolamento-banco-testes/tasks.md` as evidências: interpretador, linha de base, resultado final e resultado do SC-002.
- [x] T016 Conferir `git status` e `git diff --stat`. Só devem aparecer `conftest.py`, o teste novo, o doc e `specs/086-*`, e nada em `backend/app/` (SC-004). Também não pode haver `.db`, `.zip` ou pasta de dados entre os não rastreados.
- [ ] T017 Submeter para aceite. O commit (`teste — isola o banco ativo da suíte do backend`) só é criado depois do aceite do usuário.

---

## Dependências

- T001 → T002 → T003 (bloqueio de segurança antes de qualquer `pytest`).
- T004 → T005 → T006 → T007 → T008 (mesmo arquivo).
- T009 depende de T006 (fixture `session_database_dir`) e de T005 (`_PROTECTED_DB_PATH`, `_ACTIVE_DB_ATTEMPTS`).
- T011–T013 dependem de T010.
- T014 e T015 são independentes entre si; T016 e T017 encerram.

## Fora do escopo

`backend/app/**`, migrações, frontend (`npm test`, `npm run build`: não tocados, porque nenhum arquivo do frontend muda), `iniciar.py` e o estado de F01–F10.

---

## Evidências da execução (2026-10-27, worktree)

- **T001/T002**: interpretador `caderno-leitura-0.1\backend\.venv\Scripts\python.exe` da cópia principal, Python 3.13.15, sem `.pth`, `__editable__` ou `egg-link` em `site-packages`. A partir do `backend` do worktree, `app.__file__` e `BACKEND_DIR` resolvem para o worktree. Nenhum shell tinha `CADERNO_DATABASE_PATH`, `CADERNO_COVERS_DIR` ou `CADERNO_AVATARS_DIR` definidos.
- **T003 (linha de base, sem correção)**: 453 aprovados, 4 falhas, 2 pulados. Depois da execução, `backend/data/` do worktree passou a conter `caderno.db`, o que reproduz o defeito. O arquivo sintético foi removido.
- **T008 (desvio do plano D2)**: o dialeto `pysqlite` do SQLAlchemy usa `sqlite3.dbapi2.connect`, e não `sqlite3.connect`. A guarda é instalada nos dois atributos, e `test_guard_blocks_sqlalchemy_engine` cobre esse caminho.
- **Achado adicional (mesma classe de defeito)**: a fixture `rbac_client` em `tests/test_security_privileged_access.py` usava banco em `tmp_path` só via `dependency_overrides`. As rotas `/api/backup` e `/api/backup/bundle` copiam `get_database_path()`, ou seja, na cópia principal esses três testes faziam backup do acervo real. A fixture passou a definir `CADERNO_DATABASE_PATH` para o seu banco. As três falhas da linha de base (503, por banco vazio) passaram.
- **T011 (suíte completa com correção)**: 467 aprovados (453 + 11 novos + 3 de backup corrigidos), 1 falha, 2 pulados. Nenhuma tentativa barrada pela guarda. A falha restante, `test_backup_pre_upgrade.py::test_iniciar_rejects_relative_database_path`, já existia na linha de base: no worktree não há `frontend/dist` e o `iniciar.py` aborta com "Interface ausente" antes de validar o caminho. É ambiental e não tem relação com esta feature.
- **T012 (SC-002)**: com a linha da variável comentada, `test_active_database_isolation.py` teve 3 falhas e 1 erro. O erro veio da fixture de guarda, que acusou a tentativa do `lifespan` de abrir o banco padrão. Nenhum arquivo foi criado em `backend/data/`. Com a linha restaurada: 11 aprovados.
- **T013 (SC-001)**: após a suíte completa, `backend/data/` do worktree contém só `.gitignore`.
- **Fora do escopo, observado**: em `app/routers/backups.py`, a dependência que gera o backup é declarada antes de `AdminUser`. Por isso, uma requisição anônima a `/api/backup` gera a cópia do banco antes de receber 401.
