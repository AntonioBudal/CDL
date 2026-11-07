# Implementation Plan: F0.10.08 — Landing: Confiança, Desafio F12 e Custo com Fontes

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-07 | **Status**: Executado em 2026-11-07

## Technical Context

Vue 3 + TypeScript, só frontend. Sem dependência nova. Testes com `node:test`. Conferência no servidor de validação
(que envia a CSP real) com a landing pública.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: a landing não lê dados |
| Banco ativo intocado | OK: sem backend |
| Afirmações públicas verificáveis | Painel ao vivo + CSP lida do cabeçalho; preços só com fonte e data |
| Lote | 4ª feature do lote 2: build e testes novos (suítes completas no fecho, depois da F0.10.10) |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `frontend/src/utils/networkAudit.ts` (novo) | agrupamento de entradas de desempenho por origem; resumo da CSP |
| `frontend/src/components/landing/TrustChallengeSection.vue` (novo) | passos do F12, painel "Conferir nesta página", CSP |
| `frontend/src/components/landing/costSources.ts` (novo) | linhas de custo com `sourceUrl` e `checkedAt` |
| `frontend/src/components/landing/CostComparison.vue` (novo) | tabela "Quanto custa" |
| `frontend/src/views/LandingView.vue` | inclui as seções depois de `SovereigntySection` |
| testes | `frontend/tests/feature-101-landing-confianca.test.mjs` |
| `caderno-leitura-0.1/docs/contexto/RETOMADA.md` | registro |

## Decisões

1. **Prova no próprio navegador** (Resource Timing + cabeçalho CSP), não um selo: o visitante vê o dado cru.
2. **Readwise e Notion**: o Readwise é o equivalente mais direto (destaques, revisão diária, exportação); o Notion
   entrou a pedido do usuário, marcado como caderno geral. Preços das páginas oficiais (planos anual e mensal), em
   dólar, com a data; sem conversão de câmbio (seria mais um número sem fonte fixa).
3. **Leitorum sem "custo estimado"**: energia e máquina variam demais; dizer "não estimamos" é mais honesto.
4. **Dados estáticos e datados** em arquivo próprio, com teste que barra preço sem fonte ou sem data.

## Riscos

| Risco | Mitigação |
|---|---|
| Preço do Readwise mudar | Data visível e nota "confira na fonte"; arquivo único para atualizar |
| Painel parecer vazio no Vite (sem CSP) | Mensagem explícita de cabeçalho ausente |
| Buffer de Resource Timing cheio (150 entradas) | `performance.setResourceTimingBufferSize(500)` ao montar, quando existir |
