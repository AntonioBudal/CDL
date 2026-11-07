# Implementation Plan: Isolamento do Banco Ativo na Suíte de Testes do Backend

**Branch**: `097-isolamento-banco-testes` | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/097-isolamento-banco-testes/spec.md`

## Summary

A suíte do backend passa a rodar inteira apontando `CADERNO_DATABASE_PATH` para um arquivo num diretório temporário criado no carregamento do `tests/conftest.py`, **antes** de `app.main` ser importado. Uma guarda instalada no mesmo ponto intercepta `sqlite3.connect` e recusa, sem abrir o arquivo, qualquer conexão ao banco ativo. Cada tentativa fica registrada e faz o teste em curso falhar, mesmo quando a aplicação engole a exceção, como no `lifespan`. Um arquivo de testes novo prova que o isolamento e a guarda estão ativos. Nenhum arquivo de `backend/app/` muda.

## Technical Context

**Language/Version**: Python 3.13 (venv do projeto em `backend/.venv`)
**Primary Dependencies**: pytest, FastAPI `TestClient`, SQLAlchemy 2 (dialeto `pysqlite`), `sqlite3` da biblioteca padrão
**Storage**: SQLite; banco descartável por execução da suíte em `%TEMP%\leitorum-pytest-*\caderno.db`
**Testing**: `pytest` a partir de `backend/` (`pytest.ini`: `testpaths = tests`, `pythonpath = .`)
**Target Platform**: Windows local (caminhos com espaços, acentos e diferença de maiúsculas/minúsculas)
**Project Type**: Web application (só a parte de testes do backend é tocada)
**Constraints**: não abrir, ler, copiar nem consultar metadados de `backend/data/caderno.db` em nenhuma etapa
**Scale/Scope**: 1 arquivo alterado (`tests/conftest.py`), 1 arquivo novo de testes, 1 correção de documentação

## Constitution Check

- **I (Privacidade do acervo)**: PASS. Nenhum dado real é lido; a guarda recusa a conexão antes de o SQLite tocar o arquivo.
- **II.1 (Zero impacto no acervo ativo)**: PASS. É o objetivo desta feature: o processo de teste deixa de resolver e de conseguir conectar ao banco ativo.
- **II.2 (Bancos descartáveis)**: PASS. O banco padrão da sessão vive num diretório temporário removido ao fim.
- **II.3 (Servidores efêmeros com `CADERNO_DATABASE_PATH` explícito)**: PASS. Subprocessos herdam o caminho temporário quando o teste não define outro.
- **III (Fidelidade arquitetural)**: PASS. Sem dependências novas e sem mudança na aplicação.
- **IV (Governança SDD)**: PASS. Ciclo fatiado: spec aprovada, este plano aguarda aprovação.
- **V.4 (Contrato único de caminhos)**: PASS. A correção usa o próprio contrato `CADERNO_DATABASE_PATH` lido por `get_database_path()`.

## Decisões técnicas

### D1 — Configurar o ambiente no carregamento do `conftest.py`, não numa fixture

A spec sugeria uma fixture `autouse` de sessão. Ela chega tarde demais: `tests/conftest.py` importa `app.main` na linha 16, e `app.main` executa `app = create_app()` no import. `create_app()` chama `register_frontend()`, que chama `get_database_path()`. Isso só resolve o caminho e não abre o arquivo, mas mostra que código da aplicação roda durante a coleta, antes de qualquer fixture.

Por isso o bloco de isolamento fica **no topo do `conftest.py`, antes de qualquer import de `app.*` além de `app.core.config`**:

1. `_SESSION_DB_DIR = Path(tempfile.mkdtemp(prefix="leitorum-pytest-"))`.
2. Guardar o valor original de `CADERNO_DATABASE_PATH` (ou a ausência dele).
3. Sobrescrever **incondicionalmente** `os.environ["CADERNO_DATABASE_PATH"] = str(_SESSION_DB_DIR / "caderno.db")`. Assim, mesmo que o shell de quem roda a suíte tenha a variável apontando para o banco real, os testes não a usam.
4. Instalar a guarda de `sqlite3.connect` (D2).

O hook `pytest_unconfigure` restaura o valor original da variável, reinstala o `sqlite3.connect` original e remove o diretório temporário com `shutil.rmtree(..., ignore_errors=True)`. No Windows, engines em cache podem manter o arquivo aberto; nesse caso sobra uma pasta vazia ou pequena em `%TEMP%`, sem efeito no acervo.

O `mkdtemp` também dá um diretório próprio por processo, então não impede o uso futuro de `pytest-xdist`.

### D2 — Guarda em `sqlite3.connect`, e não em `create_sqlite_engine`

A spec propunha envolver `create_sqlite_engine`. O plano troca o ponto da guarda para `sqlite3.connect`, por três motivos:

- **Cobertura**: `create_sqlite_engine` só cobre o caminho SQLAlchemy. `app/services/backups.py` (linhas 42, 66, 128, 136) e `app/services/maintenance.py:140` chamam `sqlite3.connect` diretamente, com URIs `file:...?mode=ro`, sobre `get_database_path()` quando não recebem origem explícita.
- **Ligação de nomes**: 15 arquivos de teste fazem `from app.db.session import create_sqlite_engine`, e `_get_engine_for_path` usa o nome global do módulo. Substituir a função depende da ordem de import. Já o dialeto `pysqlite` do SQLAlchemy chama `sqlite3.connect` como atributo do módulo `sqlite3` no momento da conexão, e nenhum código usa `from sqlite3 import connect`. Substituir o atributo cobre todos os chamadores.
- **Momento**: o engine do SQLAlchemy é preguiçoso. A conexão real acontece no `connect`, que é exatamente o que precisa ser impedido.

Comportamento da guarda (`_guarded_sqlite_connect(database, *args, **kwargs)`):

1. Normaliza o alvo:
   - `str`, `bytes` ou `PathLike` vira texto;
   - com `uri=True` ou prefixo `file:`, remove o esquema e a query string e decodifica `%xx`;
   - ignora `:memory:` e alvos vazios;
   - compara `os.path.normcase(os.path.realpath(alvo))` com o mesmo cálculo sobre o caminho protegido. No Windows isso trata maiúsculas/minúsculas, barras e `..`.
2. Se o alvo for o banco protegido, ou um dos auxiliares `-wal`, `-shm` ou `-journal`: registra o alvo em `_ACTIVE_DB_ATTEMPTS` e levanta `RuntimeError("Teste tentou abrir o banco ativo: ...")` **antes** de chamar o `sqlite3.connect` original.
3. Caso contrário, delega para o original sem alterar argumentos.

O caminho protegido é `BACKEND_DIR / "data" / "caderno.db"`, calculado a partir de `app.core.config.BACKEND_DIR`. Ele fica numa variável de módulo (`_PROTECTED_DB_PATH`) para o teste-guarda poder trocá-la por um alvo falso via `monkeypatch` (D3).

### D3 — Falha mesmo quando a aplicação engole a exceção

O `lifespan` faz `except Exception: pass`, então o `RuntimeError` da guarda não aparece sozinho. Uma fixture `autouse` de função, `_fail_on_active_database_attempt`, roda depois de cada teste. Se `_ACTIVE_DB_ATTEMPTS` não estiver vazia, ela copia, limpa e chama `pytest.fail(...)` com os alvos. Assim a falha aparece no teste que causou a tentativa.

Tentativas durante a coleta (import de módulos) aparecem na desmontagem do primeiro teste. Para não depender disso, `pytest_sessionfinish` também verifica a lista e força `session.exitstatus = 1` se sobrar algo.

### D4 — Arquivo novo `tests/test_active_database_isolation.py`

Nenhum teste chama `sqlite3.connect` sobre o banco ativo real. Se a guarda estivesse quebrada, esse teste abriria o acervo. Toda verificação do mecanismo usa um alvo falso em `tmp_path`.

| Teste | O que prova |
| --- | --- |
| `test_database_path_is_not_active_database` | `get_database_path()` ≠ `BACKEND_DIR / "data" / "caderno.db"` e está dentro de `_SESSION_DB_DIR` (exposto por uma fixture `session_database_dir`). É o teste pedido no requisito FR-004. |
| `test_environment_points_to_session_temp_dir` | `os.environ["CADERNO_DATABASE_PATH"]` é absoluto e fica sob o diretório temporário da sessão. |
| `test_sqlite_connect_is_guarded` | `sqlite3.connect` é a função de guarda instalada pelo `conftest`. |
| `test_guard_blocks_protected_target_without_creating_it` | Com `monkeypatch` trocando `_PROTECTED_DB_PATH` por `tmp_path / "ativo_falso.db"`, conectar por `str`, `Path`, URI `file:...?mode=ro` e grafia com maiúsculas trocadas levanta `RuntimeError`, e o arquivo falso **não** é criado. O teste limpa as tentativas registradas. |
| `test_guard_allows_other_databases` | Conectar a `tmp_path / "outro.db"` e a `:memory:` funciona normalmente. |
| `test_lifespan_maintenance_runs_on_session_database` | `with TestClient(app)`, sem nenhum override, dispara o `lifespan`. Depois a lista de tentativas está vazia e o arquivo do banco da sessão existe, o que prova que a manutenção conectou ali. |

### D5 — Correção de documentação

`docs/contexto/AMBIENTE-E-VALIDACAO.md:64` afirma que todas as suítes já usam `tmp_path` e estão isoladas, o que não era verdade para o `lifespan`. A frase passa a descrever o isolamento real: banco temporário da sessão no `conftest.py` mais a guarda de `sqlite3.connect`.

## Project Structure

```text
caderno-leitura-0.1/
├── backend/
│   └── tests/
│       ├── conftest.py                          # ALTERADO: bloco de isolamento no topo, guarda, hooks e fixtures
│       └── test_active_database_isolation.py    # NOVO: testes-guarda
└── docs/contexto/AMBIENTE-E-VALIDACAO.md        # ALTERADO: uma frase sobre o isolamento
specs/097-isolamento-banco-testes/
├── spec.md
└── plan.md
```

Fora do escopo: `backend/app/**` (inclusive `main.py`/`lifespan`), migrações, frontend, `iniciar.py`.

## Verificação

1. **Execução**: `pytest` a partir de `caderno-leitura-0.1/backend` **no worktree**, com o interpretador do venv do projeto. O worktree não tem `backend/.venv`; a primeira tarefa confirma qual interpretador 3.13 com as dependências usar (por exemplo, o venv da cópia principal executado com o diretório atual no worktree, já que `BACKEND_DIR` vem do `__file__` do worktree). Não há instalação de pacotes sem aviso.
2. **Linha de base**: antes de alterar o `conftest.py`, rodar a suíte uma vez no worktree para registrar quantos testes passam. Na linha de base, a ausência de isolamento cria um `caderno.db` **no worktree** (`backend/data/` do worktree, que hoje só tem `.gitignore`). Esse arquivo é sintético, não é o acervo, e é apagado em seguida. Isso também reproduz o defeito descrito na spec.
3. **SC-002**: com a correção aplicada, desativar temporariamente a linha que define a variável e rodar só `test_active_database_isolation.py`. Ele deve falhar. Depois, restaurar a linha.
4. **SC-001/SC-003**: suíte completa com a correção. `backend/data/` do worktree volta a conter só `.gitignore`, e o número de aprovados é a linha de base mais os testes novos.
5. **SC-004**: `git diff --stat` sem nada em `backend/app/`.

## Riscos

- **Teste que depende do caminho padrão em processo**: nenhum encontrado. O único que inspeciona o padrão (`test_database.py:192`) usa subprocesso com a variável removida e só imprime o caminho.
- **Falso positivo da guarda** (um teste legítimo usar um arquivo chamado `caderno.db` em `tmp_path`): não acontece, porque a comparação é por caminho completo, e não por nome.
- **Arquivo do banco temporário preso no Windows ao fim**: tratado com `ignore_errors=True`; não afeta o resultado.

## Commit

Um único commit em português ao fim, depois do `pytest` verde, por exemplo `teste — isola o banco ativo da suíte do backend`, com o trailer de coautoria. Ele só é criado com o seu aceite.
