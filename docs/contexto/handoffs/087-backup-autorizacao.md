# Handoff — 087-backup-autorizacao

Conversa encerrada em 2026-11-07. Worktree `.claude/worktrees/vigilant-swartz-c1e0ef`, branch `claude/vigilant-swartz-c1e0ef`.

## O que foi feito

- Feature 087, pelo ciclo Spec Kit (spec → plan → tasks, com aprovação entre eles): as rotas `GET /api/backup` e `GET /api/backup/bundle` resolviam `temporary_backup` / `temporary_backup_bundle` antes de `AdminUser`. Com isso, anônimo e usuário comum geravam uma cópia completa do banco antes de receber 401/403.
- Correção: as geradoras passaram a receber `_admin: AdminUser` como primeiro parâmetro (`caderno-leitura-0.1/backend/app/routers/backups.py`). Os testes novos ficam em `tests/test_security_privileged_access.py`: recusas sem chamada de geração, caso do cabeçalho `Range` e controle positivo do administrador.
- Commit `aa31118 feature — autorização antes de gerar backup`, aceito pelo usuário. Pytest: 490 passed, 1 failed (a falha é a ambiental conhecida `test_iniciar_rejects_relative_database_path`).
- Esta conversa também abriu a sessão que corrigiu o erro "Não foi possível ler esta foto" (spec 088, `correção — digitalização usa memória comprometível`), que já está no `main`.

## Pendente

- **A 087 NÃO está no `main`.** Ela existe só no branch `claude/vigilant-swartz-c1e0ef`, sem push nem PR. Em 2026-11-07 o `main` (`d410760`) ainda tem o defeito em `backups.py`. É preciso mesclar ou cherry-pick `aa31118`.
- O `main` avançou desde então. `specs/088-*` e `specs/089-*` já existem, mas o número 087 continua livre no `main`, então a pasta `specs/087-backup-autorizacao-antes-da-geracao/` não deve colidir.

## Cuidados

- O commit `f4713b4` (086 isolamento do banco nos testes, branch `claude/intelligent-perlman-c530cd`) também não está no `main`. Sem ele, a fixture `rbac_client` copia o `data/caderno.db` padrão. No checkout principal, esse arquivo é o banco ativo. A 087 inclui na `rbac_client` a mesma linha do `f4713b4` (`CADERNO_DATABASE_PATH` → banco do `tmp_path`); o texto é idêntico e deve mesclar sem conflito.
- Colisão de número: `specs/086-digitalizar-caderno-estudo` (no `main`) e `specs/086-isolamento-banco-testes` (no `f4713b4`) usam o mesmo 086.

## Arquivos alterados e não commitados

Nenhum. O `git status` estava limpo antes deste handoff.
