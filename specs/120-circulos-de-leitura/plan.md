# Implementation Plan: F0.12.07 — Círculos de leitura com trava anti-spoiler

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-15 | **Status**: Concluída

## Technical Context

FastAPI + SQLAlchemy 2 + Alembic, Vue 3 + TypeScript. Migração `0042` (só cria quatro tabelas; nada muda nos dados
existentes). Testes em `tmp_path` com o harness de vários usuários (`sharing_harness`) e `node:test`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código e dados fictícios (dois leitores de teste) |
| Banco ativo | Não é tocado; a migração roda nele pelo procedimento autorizado, depois do push |
| Privacidade | Só amigos entram; quem não é membro recebe 404; a trava é aplicada no servidor; bloqueio respeitado |
| Lote | 2ª feature do lote 2 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/migrations/versions/0042_reading_circles.py` (novo) | quatro tabelas e índices |
| `backend/app/models/reading_circle.py` (novo), `models/__init__.py` | modelos |
| `backend/app/schemas/reading_circle.py` (novo) | entrada e saída |
| `backend/app/services/reading_circle_service.py` (novo) | regras, trava, bloqueio, exemplar |
| `backend/app/routers/reading_circles.py` (novo), `main.py` | rotas `/api/circles…` |
| `frontend/src/views/CirclesView.vue`, `CircleView.vue` (novos), `router/index.ts` | páginas |
| `frontend/src/components/...` (menu "Mais", menu do livro), `services/api.ts`, `types` | entrada e chamadas |
| contratos de rota (`specs/076`, `specs/081`) | `/circulos` e `/circulos/:id` |
| `VERSION`, `package.json`, `package-lock.json`, `data/versionHistory.ts` | `0.12.0-alpha.7` |
| testes | `test_reading_circles.py`, `feature-120-circulos.test.mjs` |
| docs | `ROADMAP-0.12.md`, `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **Partes próprias do círculo** (não os capítulos de cada um): são as únicas medidas comuns a todos os membros.
   Começam iguais aos capítulos do livro de quem criou.
2. **Progresso = parte atual** (0 = não comecei; última+1 = terminei). Vejo as mensagens das partes até a minha.
3. **Trava no servidor**: a resposta nunca traz o texto de mensagens à frente, só a contagem. A tela não precisa
   esconder nada.
4. **Partes só crescem no fim**: renomear e acrescentar; apagar só a última sem mensagens. Reordenar mudaria o
   significado do progresso de todos.
5. **Sem sininho no 0.12**: evita recriar a tabela de notificações; o convite fica na página e no contador do menu.
6. **Texto simples**: sem Markdown nas mensagens (nada a sanitizar além do escape padrão do Vue).

## Riscos

| Risco | Mitigação |
|---|---|
| Vazar spoiler por outra rota (lista, contagem, busca) | Uma única função monta as mensagens visíveis; teste que procura o texto à frente em todas as respostas |
| Convite a quem bloqueou | Checagem bilateral no convite e no aceite |
| Página pesada com muitas mensagens | Mensagens carregadas por parte, ao abrir a parte |
