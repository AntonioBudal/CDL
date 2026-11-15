# Implementation Plan: F0.12.08 — Simplificação de nomes

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-15 | **Status**: Concluída

## Technical Context

Vue 3 + TypeScript (textos), uma frase no backend. **Sem migração.** Testes em `node:test` e `tmp_path`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código |
| Banco ativo | Não é tocado; estudos já gravados não mudam |
| Lote | 3ª feature do lote 2 |

## Abordagem

1. **Inventário por busca**: para cada nome antigo, listar as ocorrências em `src/` e separar **texto visível** (troca)
   de **nome interno** (fica: `InboxView`, `useInboxCount`, `dashboard` em rotas, classes CSS, chaves de
   armazenamento).
2. **Troca tela a tela**, conferindo menu do computador (`NavigationTabs.vue`), menu do celular
   (`MobileMoreMenu.vue`), barra do celular (`MobileTabBar.vue`), menu do usuário, `router/index.ts` (`meta.title`), a
   tela em si e os avisos que apontam para ela.
3. **Guarda** `feature-121-nomes.test.mjs`: lê os `.vue` e `.ts` de `src/` (sem `data/versionHistory.ts`, que é
   histórico), tira comentários e procura os nomes antigos em texto visível; também confere os nomes novos nos menus
   e nos `meta.title`.
4. Testes antigos que conferiam um texto antigo passam a conferir o novo (mesmo comportamento).

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `frontend/src/**` (≈ 30 arquivos com texto visível) | textos |
| `backend/app/services/inbox_service.py` | frase da nota capturada |
| `frontend/tests/*.test.mjs` antigos que conferem textos | texto novo |
| testes | `feature-121-nomes.test.mjs`; ajuste no teste do serviço da caixa de entrada |
| `VERSION`, `package.json`, `package-lock.json`, `data/versionHistory.ts` | `0.12.0-alpha.8` |
| docs | `ROADMAP-0.12.md`, `RETOMADA.md`, `HANDOFF.md` |

## Riscos

| Risco | Mitigação |
|---|---|
| Trocar um nome interno por engano e quebrar código | Só texto em template, `meta.title`, rótulos e mensagens; type check e build |
| Nome antigo sobrar num canto | Guarda automática por busca |
| Rótulo mais longo quebrar o menu do celular | Conferência a 375 px |
