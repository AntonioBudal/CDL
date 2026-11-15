# Implementation Plan: F0.12.09 — Seletor de idioma (só a fundação)

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-15 | **Status**: Concluída

## Technical Context

Vue 3 + TypeScript + Vite; dependência nova **`vue-i18n` 11.4.16, versão exata** (a mais recente publicada há mais de duas semanas). FastAPI + Alembic: migração `0043`
(`ADD COLUMN` simples com padrão). Testes em `node:test` e `tmp_path`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código |
| Banco ativo | Não é tocado; a migração roda pelo procedimento autorizado, depois do push |
| Segurança | CSP sem `unsafe-eval` mantida; conferida no navegador (console sem erro de CSP) |
| Lote | 4ª feature do lote 2 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `frontend/package.json`, `package-lock.json` | `vue-i18n` |
| `frontend/src/i18n/index.ts`, `messages/pt-BR.ts`, `messages/en.ts`, `format.ts` (novos) | instância, mensagens, formatos, idioma inicial |
| `frontend/src/main.ts` | instala o i18n |
| menus (`NavigationTabs`, `MobileMoreMenu`, `MobileTabBar`, `UserDropdown`), `GlobalHeader`, `App.vue` (rodapé), `router/index.ts` (títulos), atalhos | textos por chave |
| as 31 telas com `'pt-BR'` fixo | `formatDate`/`formatDateTime`/`formatNumber` |
| `views/SettingsView.vue`, `composables/usePreferences.ts`, tipos | seletor e sincronização |
| `backend/migrations/versions/0043_user_locale.py`, `models/user_preference.py`, `schemas/preferences.py`, `services/preferences_service.py` | coluna e API |
| testes | `feature-122-idioma.test.mjs`, `test_user_locale.py`; ajustes nos testes que conferem os textos dos menus |
| `VERSION`, `package.json`, `package-lock.json`, `data/versionHistory.ts` | `0.12.0-alpha.9` |
| docs | `ROADMAP-0.12.md`, `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **`vue-i18n` em vez de uma camada caseira**: pluralização, interpolação e formatos prontos, e é o caminho
   conhecido para a migração gradual do resto da interface. Mensagens em objetos TypeScript (sem compilação por
   `eval`); conferido contra a CSP.
2. **Português é a base e o fallback**: chave sem inglês mostra português.
3. **Ordem do idioma inicial**: conta (depois do login) → navegador (`localStorage`) → idioma do navegador (só se
   inglês) → português.
4. **Datas por função comum**: uma só porta de entrada para o idioma; o teste proíbe `'pt-BR'` fixo fora de `src/i18n/`.

## Riscos

| Risco | Mitigação |
|---|---|
| Biblioteca exigir `eval` (CSP) | Montagem sem compilador em tempo de execução ou mensagens já em função; console conferido |
| Testes antigos conferirem o texto literal dos menus | Passam a conferir a chave ou o texto em `pt-BR.ts` |
| Nomes em inglês não caberem nos menus | Conferência a 375 px e na faixa só de ícones (768–1259 px) |
| Data mudar de formato em português | `formatDate` em `pt-BR` reproduz o formato de hoje; teste compara |
