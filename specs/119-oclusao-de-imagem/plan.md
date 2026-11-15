# Implementation Plan: F0.12.06 — Oclusão de imagem

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-15 | **Status**: Concluída

## Technical Context

FastAPI + SQLAlchemy 2 + Alembic, Vue 3 + TypeScript. Migração `0041` (só cria tabela; nada muda nos dados existentes).
Imagem pelo cofre que já existe. SVG feito à mão no Vue (sem biblioteca nova). Testes em `tmp_path` e `node:test`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código e dados fictícios; imagem sintética gerada no teste |
| Banco ativo | Não é tocado; a migração roda nele só pelo procedimento autorizado, depois do push |
| Privacidade | Imagem continua cifrada no cofre e servida pela rota protegida; cartões só do dono |
| Lote | 1ª feature do lote 2 (suítes completas na 10ª) |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/migrations/versions/0041_image_occlusion_cards.py` (novo) | tabela e índices |
| `backend/app/models/image_occlusion_card.py` (novo), `models/__init__.py` | modelo |
| `backend/app/services/image_occlusion_service.py` (novo) | salvar/listar, validação, revisão (itens, baldes, nota) |
| `backend/app/routers/media.py`, `routers/review.py`, `schemas/review.py` | rotas e campos do cartão de imagem |
| `frontend/src/components/ImageOcclusionEditor.vue` (novo) | editor SVG |
| `frontend/src/views/StudyView.vue` | botão no painel "Folha original"; abrir o editor |
| `frontend/src/components/review/ReviewCard.vue`, `ReviewHubView.vue`, `composables/useReviewSession.ts` | modo imagem |
| `frontend/src/services/api.ts`, `types` | chamadas e tipos |
| contratos de rota (`specs/076`, `specs/081`) | rotas novas registradas |
| `VERSION`, `package.json`, `package-lock.json`, `data/versionHistory.ts` | `0.12.0-alpha.6` |
| testes | `test_image_occlusion.py`, `feature-119-oclusao.test.mjs` |
| docs | `ROADMAP-0.12.md`, `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **Tabela própria**, como os cartões de conceito: os destaques estão presos a trechos de texto (seção e posições).
2. **Coordenadas relativas (0–1)**: valem em qualquer largura de tela e sobrevivem a uma imagem guardada em outro tamanho.
3. **Salvar em lote com ids**: o editor manda a lista inteira; quem tem id é atualizado (mantém o histórico), quem não
   tem é criado, quem sumiu é apagado. Simples e sem estados intermediários.
4. **Foto com cartões não expira** (`keep_forever`): senão o cartão perderia a imagem quando o estudo fosse concluído.
5. **Modo "todas cobertas, uma destacada"**: é o que testa a área sem dar pista pelas vizinhas.

## Riscos

| Risco | Mitigação |
|---|---|
| Desenho por toque conflitar com a rolagem da página | `touch-action: none` só na área da imagem durante o editor |
| Imagem grande pesada na revisão | Usa a imagem já reduzida e em WebP do cofre; carregamento preguiçoso |
| Cofre trancado | Mensagens que já existem; cartões não somem |
