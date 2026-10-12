# Implementation Plan: F0.8.15 — Bateria Completa de Regressão e Consolidação do Roadmap de Responsividade

**Branch**: `081-regressao-responsiva` | **Date**: 2026-10-12 | **Spec**: [specs/081-regressao-responsiva/spec.md](spec.md)

**Input**: Feature specification from `specs/081-regressao-responsiva/spec.md`

## Summary

Consolidação final do marco de responsividade móvel (Features 076 a 081) do Caderno de Leitura. A solução compreende:
1. Validação exaustiva da matriz de 25 rotas nomeadas do Vue Router através de 8 viewports canônicas (320px, 375px, 390px, 430px, 767px, 768px, 1024px e 1440px mais orientação paisagem 844x390px), garantindo zero transbordamento horizontal (`scrollWidth === clientWidth`).
2. Auditoria e ateste formal do fechamento dos 19 problemas (P-01 a P-19) da auditoria estática inicial.
3. Criação da suíte de testes-guarda automatizada no frontend (`tests/feature-081-responsive-regression.test.mjs`), integrada ao `npm test`, blindando regras contratuais, alvos táteis ($\ge 44 \times 44\text{ px}$), offsets de navegação e breakpoints canônicos.
4. Formalização da decisão de infraestrutura de testes (mantendo execução ultrarrápida em `node --test` sem dependências pesadas de headless browsers).
5. Estabelecimento do protocolo de homologação em aparelhos físicos sob rede local/Tailscale com dados estritamente sintéticos.

## Technical Context

**Language/Version**: Python 3.13 (backend), TypeScript 5.3+ / Node.js 20+ (frontend)
**Primary Dependencies**: Vue 3.4+ (Composition API), Vue Router 4, Pinia, FastAPI, SQLAlchemy 2.0, Alembic, Vite
**Storage**: SQLite 3 local (modo WAL), bancos efêmeros descartáveis em `tmp_path` durante testes (banco ativo `caderno.db` estritamente intocado)
**Testing**: Node.js Test Runner nativo (`node --test`), pytest (backend), vue-tsc / vite build
**Target Platform**: Windows local (PC), Mobile Web (iOS Safari, Android Chrome via rede local/Tailscale)
**Project Type**: Web application monorepo (frontend em `caderno-leitura-0.1/frontend/`, backend em `caderno-leitura-0.1/backend/`)
**Performance Goals**: Execução da suíte de testes-guarda em < 500ms; carregamento instantâneo em rede local; fluidez de 60fps em animações móveis
**Constraints**: Zero emojis em código e documentação; isolamento absoluto do acervo do usuário; convenção Git 1 Feature = 1 Commit; conformidade WCAG 2.1 (alvos táteis $\ge 44 \times 44\text{ px}$); contenção estrita de largura (`scrollWidth === clientWidth`)
**Scale/Scope**: 25 rotas nomeadas, 8 viewports normativas, 19 problemas auditados, 1 suíte de testes-guarda de regressão

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I (Privacidade e Acervo)**: APROVADO. A feature não lê, exibe, resume nem transmite dados do acervo. Todos os testes utilizam dados sintéticos ou inspeção estática de componentes.
- **Princípio II (Isolamento de Testes)**: APROVADO. Nenhum teste conecta-se ou modifica `caderno.db`. Todas as validações ocorrem em memória ou via bancos efêmeros descartáveis.
- **Princípio III (Fidelidade Arquitetural)**: APROVADO. Mantém-se o ecossistema canônico (Vue 3, TypeScript, Vite, Python 3.13, FastAPI) e o processo único em `iniciar.py`. Ratificada a escolha de `node --test` nativo sem introdução de dependências pesadas de navegador (Playwright/Puppeteer).
- **Princípio IV (Governança e SDD)**: APROVADO. Execução estrita do ciclo Spec Kit (specify -> plan -> tasks -> implement), com commits atômicos (1 Feature = 1 Commit).
- **Princípio V (Resiliência e Segurança)**: APROVADO. Nenhuma alteração destrutiva ou migração de schema de banco de dados é necessária nesta consolidação de regressão.

*Gate Status: 100% Aprovado sem violações.*

## Project Structure

### Documentation (this feature)

```text
specs/081-regressao-responsiva/
├── plan.md              # Este arquivo (plano técnico de implementação)
├── research.md          # Pesquisa técnica e fechamento formal dos 19 problemas (P-01 a P-19)
├── data-model.md        # Modelagem de entidades: matriz de rotas, problemas e cenários
├── quickstart.md        # Guia de validação da suíte e homologação física
├── contracts/
│   └── regression-coverage.contract.md # Contrato normativo de cobertura de regressão
├── checklists/
│   └── requirements.md  # Checklist de requisitos da especificação
└── tasks.md             # Tarefas atômicas de implementação (gerado pelo /speckit-tasks)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── router/index.ts                  # Roteador com as 25 rotas nomeadas
│   │   ├── style.css                        # Tokens CSS, breakpoints canônicos e offsets
│   │   ├── components/                      # Componentes das rotas
│   │   └── views/                           # Vistas das rotas
│   └── tests/
│       ├── feature-076-responsive-inventory.test.mjs
│       ├── feature-077-shell-mobile.test.mjs
│       ├── feature-078-conteudo-responsivo.test.mjs
│       ├── feature-079-button-labels.test.mjs
│       ├── feature-080-mobile-views-highlights.test.mjs
│       └── feature-081-responsive-regression.test.mjs # Suíte consolidada de regressão
└── docs/
    └── contexto/
        └── RETOMADA.md                      # Atualização do encerramento do roadmap
```

**Structure Decision**: Monorepo existente em `caderno-leitura-0.1/`. O teste-guarda de regressão é adicionado diretamente em `caderno-leitura-0.1/frontend/tests/feature-081-responsive-regression.test.mjs`, executado pelo comando `npm test`.

## Complexity Tracking

> Nenhuma violação constitucional identificada. A arquitetura permanece estritamente aderente aos princípios estabelecidos.
