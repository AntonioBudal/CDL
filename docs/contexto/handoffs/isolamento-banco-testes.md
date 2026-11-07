# Handoff — isolamento-banco-testes

**O que foi feito.** Ciclo Spec Kit completo da correção "nenhum teste do backend abre `backend/data/caderno.db`". Resultado no commit `f4713b4 teste — isola o banco ativo da suíte do backend`, na branch `claude/intelligent-perlman-c530cd`:
- `caderno-leitura-0.1/backend/tests/conftest.py`: no topo, antes de importar `app.main`, aponta `CADERNO_DATABASE_PATH` para um banco num `mkdtemp`. Também instala uma guarda em `sqlite3.connect` **e** `sqlite3.dbapi2.connect` (o SQLAlchemy usa o segundo), que recusa o banco ativo e faz falhar o teste responsável.
- `tests/test_active_database_isolation.py`: 11 testes-guarda.
- Fixture `rbac_client` de `tests/test_security_privileged_access.py`: passa a apontar `CADERNO_DATABASE_PATH` para o banco do próprio teste. Antes, as rotas `/api/backup` faziam backup do acervo real.
- A frase de isolamento em `caderno-leitura-0.1/docs/contexto/AMBIENTE-E-VALIDACAO.md` foi corrigida.
- Artefatos em `specs/086-isolamento-banco-testes/` (spec, plan e tasks com as evidências).
- `pytest` no worktree em 2026-10-27: 467 aprovados, 1 falha ambiental (`test_iniciar_rejects_relative_database_path`, causada pela falta de `frontend/dist` no worktree), 2 pulados.

**Pendente.**
- `f4713b4` **não está na `main`**. O `conftest.py` da `main` continua sem isolamento: rodar `pytest` na cópia principal ainda conecta ao banco ativo. Precisa de merge ou cherry-pick, com conflito provável, porque a `main` avançou bastante.
- **Colisão de numeração**: a `main` já tem `specs/086-digitalizar-caderno-estudo`. Ao integrar, renumerar `specs/086-isolamento-banco-testes` para o próximo número livre (a `main` vai até 096).
- A feature 087 (autorização antes de gerar backup, commit `aa31118`), feita em outra sessão, está na branch `claude/vigilant-swartz-c1e0ef` e também **fora da `main`**. O número 087 pode colidir do mesmo jeito.

**Cuidados.**
- Depois de integrar, confirmar que a suíte da `main` passa com a guarda ativa. Testes novos da `main` podem depender do banco padrão e passariam a falhar (a guarda acusa a tentativa); a correção deve ser feita no teste, não em `backend/app/`.
- Nunca validar abrindo o banco real; verificar num worktree onde `backend/data/` só tem `.gitignore`.
- O worktree não tem venv; usar `C:\Users\User\caderno\caderno-leitura-0.1\backend\.venv\Scripts\python.exe` a partir do `backend` do worktree, depois de confirmar que `app.__file__` aponta para o worktree.

**Arquivos alterados e não commitados (git status em 2026-11-07):** nenhum. A árvore de trabalho estava limpa antes deste handoff.
