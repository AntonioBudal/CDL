# Implementation Plan: F0.11.09 — Receptor KOReader/Readest

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-12 | **Status**: Executado em 2026-11-12

## Technical Context

FastAPI + SQLAlchemy 2 + Alembic, Vue 3 + TS. **Migração `0038`** (tabela nova). Testes em `tmp_path` e `node:test`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código, documentação pública e dados fictícios |
| Banco ativo | Não é tocado; a `0038` fica pendente com `0034`–`0037` |
| Segurança | Token aleatório de 32 bytes, só o hash guardado; isenção de origem restrita a `/api/receptor/`; nada de token ou texto em log |
| Lote | 4ª feature do lote 2 do 0.11 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/migrations/versions/0038_receiver_tokens.py`, `models/receiver_token.py`, `models/__init__.py` | tabela e modelo |
| `backend/app/services/receiver_tokens.py` (novo) | gerar, revogar, estado, autenticar |
| `backend/app/services/ereader_import/koreader.py`, `readwise.py` (novos), `__init__.py`, `service.py` | parsers; detecção; gravação automática |
| `backend/app/routers/receiver.py` (novo), `routers/account.py`, `main.py` | rotas |
| `backend/app/core/origin_guard.py` | isenção de `/api/receptor/` |
| `backend/app/schemas/receiver.py` (novo) | corpo Readwise, estado do token, respostas |
| `frontend/src/components/settings/ReceiverTokenCard.vue` (novo), `views/SettingsView.vue` | seção "Receber destaques" |
| `frontend/src/views/EreaderImportView.vue`, menus | "Importar de leitor digital"; aceita `.json` |
| `frontend/src/services/api.ts`, `types.ts` | chamadas e tipos |
| testes | `test_receiver.py`, `test_ereader_koreader.py`, `test_migration_0038.py`, `feature-111-receptor.test.mjs` |
| docs | `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **Imitar a API do Readwise** em vez de inventar uma: o Readest já fala com ela e deixa trocar a URL; nada a
   instalar no celular.
2. **KOReader por arquivo**: o único alvo de rede configurável dele (Joplin) exigiria imitar outra API inteira; o JSON
   do exportador é estável e documentado.
3. **Mesma porta de entrada da F0.11.03**: deduplicação, livro sugerido e Mesa já existem; o receptor só escolhe o
   livro sozinho (sugerido ou novo), porque não há prévia num envio automático.
4. **Um token por leitor**, hash SHA-256 (token de alta entropia dispensa hash lento), comparação pelo hash.

## Riscos

| Risco | Mitigação |
|---|---|
| Readest mudar o cliente Readwise | Testes com o corpo documentado; campos extras ignorados |
| Livro errado escolhido automaticamente | Mesma regra de título/autor da F0.11.03; capturas ficam na Mesa para triagem |
| Abuso do receptor | Token obrigatório, limites de tamanho, 401 sem detalhes |
| Isenção de origem ampla demais | Prefixo exato `/api/receptor/`; rotas só aceitam token, nunca cookie |
