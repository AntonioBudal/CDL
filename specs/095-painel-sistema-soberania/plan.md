# Implementation Plan: F0.10.03 — Painel de Sistema: Segurança, Backups e Soberania dos Dados

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-03 | **Status**: Executado em 2026-11-03

## Technical Context

Python 3.13 (FastAPI, SQLAlchemy 2, Alembic) e Vue 3 + Vite 8. Sem migração, sem dependência nova. Testes com
`tmp_path` (bancos e `.git` fictícios). Conferência no servidor de validação (porta 8010, dados fictícios).

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: o status só lê `alembic_version`, metadados de arquivo de backup (nome e data) e pragmas; nada do acervo |
| Banco ativo intocado | OK: integridade em `mode=ro`; nenhuma escrita |
| Sem caminhos expostos | OK: a resposta não traz pastas nem nomes de arquivo do servidor |
| Lote de 5 | 4ª feature; build e testes novos |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/app/core/build_info.py` (novo) | `get_build_commit()`: `LEITORUM_BUILD_COMMIT` ou leitura do `.git` (`HEAD`, ref solta, `packed-refs`, HEAD destacado), 7 caracteres, `lru_cache`; `get_expected_schema_revision()`: `ScriptDirectory` do Alembic (`get_current_head()`) |
| `backend/app/schemas/system.py` (novo) | `SystemStatus`, `BackupStatus`, `IntegrityResult` |
| `backend/app/routers/system.py` (novo) | `GET /system/status` (`CurrentUser`; bloco `backups` só se admin) e `POST /system/integrity-check` (`AdminUser`) |
| `backend/app/services/maintenance.py` | `auto_backup_status()`: liga/desliga, intervalo, `keep`, último (data), quantos, segunda cópia configurada (bool), atrasado (último > 2× intervalo); reaproveita `_auto_backups` e `auto_backup_settings` |
| `backend/app/main.py` | registrar o router `system` com prefixo `/api` |
| `frontend/vite.config.ts` | `define: { __BUILD_COMMIT__: JSON.stringify(commit) }`, commit por `execSync('git rev-parse --short=7 HEAD')` em `try` |
| `frontend/src/build-info.d.ts` (novo, no padrão de `appearance.d.ts`) | `declare const __BUILD_COMMIT__: string` |
| `frontend/src/services/api.ts` + `types.ts` | `getSystemStatus()`, `runIntegrityCheck()` e tipos |
| `frontend/src/components/settings/SystemSovereigntyCard.vue` (novo) | card com US1 a US4; avisos com `role="status"`; botão de integridade só para admin |
| `frontend/src/views/SettingsView.vue` | incluir o card na aba Sistema; commit ao lado da versão no card de conexão; `DatabaseBackup` com `v-if` de admin |
| testes | `backend/tests/test_system_status.py`, `frontend/tests/feature-095-painel-sistema.test.mjs` |
| `caderno-leitura-0.1/docs/contexto/RETOMADA.md` | registro |

## Decisões

1. **Ler o `.git` sem `git`**: o serviço roda pelo NSSM e pode não ter `git` no PATH; ler `HEAD` e as refs é
   simples, rápido e sem processo externo. Cache por processo (o commit só muda com reinício, que é justamente o
   que o aviso quer detectar).
2. **Comparação servidor × interface no navegador**: o frontend compara `__BUILD_COMMIT__` com o `commit` da
   resposta; só acusa divergência quando os dois são conhecidos.
3. **Revisão esperada pelo Alembic**: `ScriptDirectory.from_config(...).get_current_head()` lê os arquivos de
   migração; a revisão atual vem de `SELECT version_num FROM alembic_version` pela sessão.
4. **Integridade sob demanda e só para admin**: `quick_check` percorre o banco inteiro; rodar a cada abertura da aba
   seria desperdício e expõe custo a qualquer usuário.
5. **Textos fixos, não gerados**: os números (ex.: 14 backups) vêm do status; as frases são fixas e conferidas com
   o código da F0.10.02.
6. **`DatabaseBackup` para admin**: corrige a tela que oferecia botões que sempre davam 403 a quem não é admin.

## Riscos

| Risco | Mitigação |
|---|---|
| `.git` em formato inesperado (worktree, `gitdir:`) | Tratar `gitdir:` simples; em qualquer falha, "desconhecido" sem aviso |
| Build feito sem `.git` disponível | `__BUILD_COMMIT__` = "desconhecido"; sem falso aviso |
| `get_current_head()` com várias cabeças | Mostrar todas; aviso só se a atual não estiver entre elas |
