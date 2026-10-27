# Implementation Plan: Autorização Antes da Geração de Backup

**Branch**: `087-backup-autorizacao-antes-da-geracao` | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

## Summary

Fazer as dependências geradoras `temporary_backup` e `temporary_backup_bundle` receberem `_admin: AdminUser` como primeiro parâmetro. O FastAPI resolve as subdependências antes de executar o corpo da dependência que as declara, então nenhuma cópia é gerada sem um administrador resolvido (FR-001 a FR-003). Nas duas rotas, `_admin` também passa a ser o primeiro parâmetro, por clareza; o cache de dependências por requisição garante que `require_admin` rode uma única vez. Um teste com registradores no lugar das funções de geração prova a ordem (FR-006).

## Technical Context

- **Linguagem/versão**: Python 3.13; FastAPI 0.141.1 (`requirements.txt`).
- **Arquivo alterado**: `caderno-leitura-0.1/backend/app/routers/backups.py`.
- **Escopo de dependência**: as geradoras usam `Depends(..., scope="request")`. O FastAPI 0.141 só proíbe que uma dependência `"request"` dependa de outra com escopo explícito `"function"` (`fastapi/dependencies/utils.py`, ~linha 309). `AdminUser` → `require_admin` → `get_current_user` → `get_session` não declaram escopo, portanto a composição é válida.
- **Cache**: `require_admin` aparece na geradora e na rota com a mesma chamada e `use_cache=True`, então resolve uma vez por requisição e devolve o mesmo `User`.
- **Ponto de interceptação no teste**: o roteador importa os nomes (`from app.services.backups import create_backup_bundle, create_database_backup`), então o `monkeypatch` atua em `app.routers.backups.create_database_backup` e `app.routers.backups.create_backup_bundle`.
- **Isolamento**: o teste reaproveita a fixture `rbac_client` de `tests/test_security_privileged_access.py`, que usa banco em `tmp_path`, `REQUIRE_AUTH=true`, um usuário admin e um comum com sessões por cookie. O `conftest.py` da 086 já aponta `CADERNO_DATABASE_PATH` para um banco temporário e bloqueia o banco ativo.

## Constitution Check

| Princípio | Situação |
| --- | --- |
| I. Proteção do acervo | Reforçado: requisições não autorizadas deixam de ler e copiar o acervo. |
| II. Isolamento de testes | Banco em `tmp_path` e funções de geração substituídas; nada toca o banco ativo. |
| III. Fidelidade arquitetural | Usa só o mecanismo nativo de dependências do FastAPI; sem bibliotecas novas. |
| IV. SDD | Ciclo spec → plan → tasks com aprovação entre artefatos. |
| V. Backup via API oficial | `create_database_backup` e `create_backup_bundle` não mudam. |

Nenhuma violação.

## Project Structure

### Documentation (this feature)

```text
specs/087-backup-autorizacao-antes-da-geracao/
├── spec.md
├── plan.md      # este arquivo
└── tasks.md     # próximo artefato
```

Sem `research.md`, `data-model.md`, `contracts/` ou `quickstart.md`: não há entidade nova, contrato novo nem incerteza técnica além do que está registrado em Technical Context.

### Source Code

```text
caderno-leitura-0.1/backend/
├── app/routers/backups.py                        # alterado
└── tests/test_security_privileged_access.py      # testes novos ao lado da fixture rbac_client
```

## Design

### Roteador

```python
def temporary_backup(_admin: AdminUser, request: Request) -> Iterator[Path]:
    ...  # corpo inalterado

def temporary_backup_bundle(_admin: AdminUser, request: Request) -> Iterator[Path]:
    ...  # corpo inalterado

def download_backup(
    _admin: AdminUser,
    path: Annotated[Path, Depends(temporary_backup, scope="request")],
) -> FileResponse: ...

def download_backup_bundle_endpoint(
    _admin: AdminUser,
    path: Annotated[Path, Depends(temporary_backup_bundle, scope="request")],
) -> FileResponse: ...
```

A checagem de `Range` (416) fica depois da autorização, como a spec aceita (Edge Cases).

### Testes

Em `tests/test_security_privileged_access.py`:

1. Fixture `backup_calls(monkeypatch)`: substitui as duas funções do roteador por registradores que anotam `("db" | "bundle", path)` e gravam bytes fictícios no `path`, para que um eventual 200 consiga servir o arquivo.
2. `test_unauthorized_backup_requests_never_generate_backup`, parametrizado nas duas rotas × {anônimo → 401, usuário comum → 403}: confere o status e que a lista de chamadas está vazia (SC-001).
3. Controle positivo `test_admin_backup_request_reaches_generation`, parametrizado nas duas rotas: o administrador recebe 200 e há exatamente uma chamada. Isso impede que o teste negativo passe por erro de alvo do `monkeypatch`.
4. Caso de borda: usuário comum com cabeçalho `Range` recebe 403 (e não 416), sem chamadas.

Antes da correção, os casos 2 e 4 devem falhar e o 3 deve passar (SC-003).

## Implementation Phases (para o speckit.tasks)

1. Linha de base: confirmar `app.__file__` no worktree e rodar o `pytest` do backend.
2. Testes primeiro: escrever os testes e vê-los falhar contra o código atual.
3. Correção no roteador.
4. Validação: testes novos e `pytest` completo (exceção conhecida: `test_iniciar_rejects_relative_database_path`).
5. Commit após aceite do usuário.

## Complexity Tracking

Nenhuma complexidade a justificar.
