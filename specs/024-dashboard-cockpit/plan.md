# Implementation Plan: F07 — Dashboard 2.0 (Cockpit de Estudos e Hub de Navegação)

**Branch**: `024-dashboard-cockpit` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/024-dashboard-cockpit/spec.md`  

---

## Summary

Evoluir o Dashboard da aplicação para um **cockpit operacional de alta densidade e hub de navegação central**, oferecendo retoma imediata de estudos em 1 clique com base na última atividade real (`updated_at DESC`), identificação proativa de estudos sem vínculos conceituais (órfãos), acompanhamento das conexões semânticas recentemente estabelecidas, calibração nítida de contraste e opacidade para o calendário de 12 meses em todos os temas alternativos, e layout móvel condensado com abas e proteção contra rolagem lateral involuntária.

---

## Technical Context

**Language/Version**: Python 3.13 de 64 bits (backend) / TypeScript 5.8 e Node.js v24+ (frontend)  
**Primary Dependencies**: FastAPI 0.115+, SQLAlchemy 2.0+, Alembic, Uvicorn, Vue 3.5+ (Composition API, `<script setup>`), Vite 6+, Lucide Vue Next  
**Storage**: SQLite local em modo Write-Ahead Logging (`backend/data/caderno.db`), com isolamento absoluto e bancos descartáveis em `tmp_path` durante testes  
**Testing**: `pytest` com fixtures temporárias no backend (`pytest backend/tests`), `node --test` com asserções estritas no frontend (`npm test`)  
**Target Platform**: Windows 11 local (PowerShell, caminhos com acentos/espaços, quebras de linha preservadas) e navegadores móveis em smartphones (360px a 412px)  
**Project Type**: Aplicação web local orquestrada em processo único (`iniciar.py`)  
**Performance Goals**: Tempo de resposta do endpoint `GET /api/dashboard/summary` < 300ms no backend para acervos com milhares de estudos e relações; renderização no frontend < 100ms  
**Constraints**: Zero chamadas para nuvem ou APIs pagas; nenhum cálculo de IA em runtime; respeito estrito à política de soft delete (`deleted_at IS NULL`); alvos de toque táteis mínimos de 44x44px; prevenção total de `overflow-x` no mobile  
**Scale/Scope**: Acervos com centenas de livros e milhares de estudos e relações  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio Constitucional | Requisito / Critério de Auditoria | Status | Justificativa / Mecanismo de Garantia |
|---|---|:---:|---|
| **I. Privacidade de Dados** | Nenhum dado pessoal do acervo exposto em prompts, logs ou serviços externos | **PASS** | Toda a consolidação analítica roda em SQLite local sem envio de telemetria externa. |
| **II. Isolamento de Testes** | Banco ativo `backend/data/caderno.db` nunca é acessado por testes | **PASS** | Testes automatizados utilizam exclusivamente bancos temporários descartáveis em `tmp_path`. |
| **III. Arquitetura e Stack** | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Vue 3, Vite, SQLite | **PASS** | Tecnologias canônicas preservadas sem inclusão de novas dependências ou serviços externos. |
| **IV. Governança SDD** | Execução por fatias verificáveis (`specify` → `clarify` → `plan` → `tasks` → `implement`) | **PASS** | Ciclo SDD rigorosamente seguido; decisões de produto consolidadas no spec antes do código. |
| **V. Resiliência e Migrações** | Não quebrar o schema e preservar integridade relacional | **PASS** | Zero migrações DDL necessárias; utiliza tabelas já existentes via consultas SQL otimizadas. |

---

## Project Structure

### Documentation (this feature)

```text
specs/024-dashboard-cockpit/
├── spec.md              # Especificação de requisitos, cenários de aceite e esclarecimentos
├── plan.md              # Este plano de implementação técnica
├── research.md          # Decisões de pesquisa técnica (R01 a R04)
├── data-model.md        # Schemas Pydantic, tipagens TypeScript e persistência local
├── quickstart.md        # Cenários executáveis de validação de ponta a ponta
├── contracts/           # Contrato OpenAPI 3.0 para o endpoint unificado
│   └── dashboard-api.yaml
└── checklists/          # Checklist de qualidade de requisitos
    └── requirements.md
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── schemas/
│   │   │   └── dashboard.py               # [MODIFY] Adicionar RecentStudyActivityItem, UnlinkedStudyItem, RecentRelationItem
│   │   ├── services/
│   │   │   └── dashboard_service.py       # [MODIFY] Incluir queries otimizadas de retoma, órfãos e relações recentes
│   │   └── routers/
│   │       └── dashboard.py               # [MODIFY] Expor schema expandido em GET /api/dashboard/summary
│   └── tests/
│       └── test_dashboard_v2.py           # [NEW] Testes de integração backend para novos agregados e soft delete
│
└── frontend/
    ├── src/
    │   ├── types.ts                       # [MODIFY] Exportar tipos TypeScript estritos do Dashboard 2.0
    │   ├── services/
    │   │   └── api.ts                     # [MODIFY] Atualizar tipo de retorno de getDashboard()
    │   ├── router/
    │   │   └── index.ts                   # [MODIFY] Roteamento inicial condicional (Dashboard vs Acervo)
    │   ├── components/
    │   │   ├── HeatmapCalendar.vue        # [MODIFY] Calibração de contraste/opacidade multitema (.level-0 a .level-3)
    │   │   └── dashboard/
    │   │       ├── ResumeStudiesWidget.vue    # [NEW] Bloco "Continuar Estudos" (5 a 10 itens com link de 1 clique)
    │   │       ├── OrphanStudiesWidget.vue    # [NEW] Bloco "Estudos para Conectar" (órfãos e atalho de relação)
    │   │       ├── RecentConnectionsWidget.vue# [NEW] Bloco "Conexões Recentes" com badges conceituais
    │   │       └── QuickNavChips.vue          # [NEW] Barra de navegação rápida por chips aderentes no mobile
    │   └── views/
    │       ├── DashboardView.vue          # [MODIFY] Reestruturação em grid 2 colunas desktop e layout vertical condensado mobile
    │       └── SettingsView.vue           # [MODIFY] Adicionar seletor de tela inicial padrão (Dashboard vs Acervo)
    └── tests/
        ├── dashboard-cockpit.test.mjs         # [NEW] Testes unitários de retoma rápida, contadores e roteamento inicial
        ├── dashboard-theme-contrast.test.mjs  # [NEW] Testes de contraste e opacidade do heatmap em múltiplos temas
        └── dashboard-mobile-a11y.test.mjs     # [NEW] Testes de ergonomia móvel, abas, alvos de 44px e contenção de overflow
```

---

## Complexity Tracking

| Tópico / Ponto de Atenção | Necessidade | Alternativa Mais Simples Rejeitada |
|---|---|---|
| Rota `/` condicional via `localStorage` | Permitir ao leitor optar por Dashboard ou Acervo como tela inicial sem impor visualizações | Fixar o Dashboard obrigatoriamente sem opção de voltar ao Acervo desrespeitaria a autonomia do leitor |
| Abas comutáveis no mobile para widgets secundários | Evitar rolagem vertical infinita (*scroll fatigue*) no smartphone | Empilhar todos os cartões linearmente transformava o dashboard em uma página excessivamente longa |
| Calibração de tokens CSS para `.level-0` nos temas | Garantir discernimento imediato entre dias com e sem atividade em temas escuros e sépia | Manter cálculo único via `color-mix` deixava dias sem atividade indistinguíveis em temas com fundo escuro |
