# Implementation Plan: F0.12.10 — Pequenas melhorias de usabilidade

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-15 | **Status**: Concluída

## Technical Context

Vue 3 + TypeScript. **Sem migração, sem mudança no backend.** Testes em `node:test`; fecho do lote com `pytest`
completo em banco descartável.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código e dados fictícios |
| Banco ativo | Não é tocado |
| Lote | 5ª feature do lote 2: suítes completas no fecho |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `components/HeatmapCalendar.vue` | período, dias da semana dentro da grade, marca do dia escolhido |
| `views/DashboardView.vue` | `days` pelo período, filtro do ano passado, título/contagem/"Ver todas", rolagem no celular |
| `components/StudyActionsBar.vue` (novo) | barra fixa (lógica e eventos do `FloatingActionsToolbar.vue`, que sai) |
| `views/StudyView.vue` | barra acima de `StudyTabs`; espaçamento do cabeçalho |
| `components/ui/DropdownMenu.vue`, `utils/menuPlacement.ts` (novo) | encaixe na tela (função pura testável) |
| testes | `feature-123-usabilidade.test.mjs`; ajustes nos testes que conferem a barra flutuante |
| `VERSION`, `package.json`, `package-lock.json`, `data/versionHistory.ts` | `0.12.0-alpha.10` |
| docs | `ROADMAP-0.12.md` (0.12 concluído), `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **Dias da semana na grade**: o rótulo vira a primeira "coluna" da própria grade (mesma altura e espaçamento das
   células), em vez de uma coluna paralela que pode desalinhar.
2. **Barra sempre visível e desativada sem seleção**: é o que o Word e o Docs fazem; evita a barra pular pela tela.
   O clique usa `mousedown.prevent` para não tirar a seleção.
3. **Encaixe do menu por medição** depois de abrir (e ao redimensionar), numa função pura testada; nada muda nos 3
   lugares que usam o componente.
4. **"Ano passado" no cliente**: 730 dias já cobrem o ano anterior inteiro; filtrar as datas evita mexer na API.

## Riscos

| Risco | Mitigação |
|---|---|
| Testes antigos presos à barra flutuante | Ajustar para a barra nova, conferindo os mesmos eventos |
| Barra presa no alto cobrir o texto ao rolar | `position: sticky` abaixo do cabeçalho global; conferência a 375/768/1366 px |
| Seleção perdida no celular ao tocar na barra | Guardar a última seleção válida (como a flutuante já faz) e conferir por toque |
