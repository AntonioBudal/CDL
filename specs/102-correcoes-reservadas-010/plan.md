# Implementation Plan: F0.10.10 — Correções Reservadas do Roadmap 0.10

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-07 | **Status**: Executado em 2026-11-07

## Technical Context

Vue 3 + FastAPI. Sem migração, sem dependência nova. Seis correções pequenas e independentes, um commit
(`correção — itens reservados do 0.10`). Fecho do lote 2 com as suítes completas.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK |
| Banco ativo intocado | OK; `pytest` completo com banco descartável e variáveis do HANDOFF |
| Textos públicos fiéis | Item 2 alinha o rodapé ao que o repositório tem |
| Lote | Última do lote 2: `npm test`, `pytest` completo (sozinho, sem build em paralelo) e build |

## Arquivos e mudanças

| Item | Arquivos |
|---|---|
| 1 | `views/ReviewHubView.vue`, `components/review/ReviewStatsHeader.vue`, `components/review/ReviewSummaryModal.vue` |
| 2 | `App.vue`, `components/layout/AppFooter.vue`, `views/SupportView.vue` |
| 3 | `composables/useDigitizeDraft.ts`, `views/DigitizeNotebookView.vue` |
| 4 | `backend/app/services/seo_service.py`, `backend/tests/test_seo_and_public_presence.py`, `backend/tests/test_seo_public_pages_flag.py` (novo) |
| 5 | `utils/referenceScopes.ts`, `views/StudyView.vue` |
| 6 | `frontend/tests/superclasses.test.mjs` |
| testes | `frontend/tests/feature-102-correcoes-reservadas.test.mjs`; ajustes em testes que fixem os textos antigos |
| docs | `RETOMADA.md`, `docs/contexto/HANDOFF.md` (fecho do lote) |

## Decisões

1. **Duas entradas na Revisão**: "Praticar agora" (rápida, no hub) e "Sessão registrada" (histórico, retomável). É a
   diferença real entre as funções; o terceiro botão era a mesma coisa do primeiro.
2. **Licença**: corrigir o texto, não escolher licença — isso é decisão do dono.
3. **Erros passageiros**: só `busy` e `low_memory` (o servidor já manda "tente de novo"); `timeout` e
   `engine_failed` podem ser da própria foto e continuam como estão.
4. **Flag no SEO** em vez de apagar o código do sitemap: o 1.0 liga quando a rota existir.
5. **Um commit** para os seis itens: são correções pequenas da mesma feature reservada (1 feature = 1 commit).

## Riscos

| Risco | Mitigação |
|---|---|
| Testes antigos fixarem "Prática Rápida neste Hub", "Revisar mais 10", "Software Livre", `Allow: /compartilhado/` | Atualizar as asserções para o comportamento novo, no mesmo commit |
| `pytest` completo achar falha de feature anterior | Commit próprio de correção, como combinado |
