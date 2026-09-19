# Implementation Plan: Dashboard de Leitura com Calendário e Timeline

**Branch**: `013-dashboard-calendario-timeline` | **Date**: 2026-09-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/013-dashboard-calendario-timeline/spec.md`

---

## Summary

Implementação da tela central de Dashboard de Leitura (T06 do Roadmap 0.3), fornecendo ao leitor uma visão integrada de produtividade e hábito:
1. **Cartões de Métricas**: Total de livros, estudos, dias com leitura, média de estudos por livro e sequência de dias ativos (streak).
2. **Mapa de Calor em Calendário**: Grade visual de frequência e intensidade (4 níveis) com corte responsivo adaptativo (12 meses no desktop, 3 a 6 meses no mobile) e dicas de contexto por data.
3. **Timeline Cronológica**: Lista reversa das atividades recentes (cadastro de livros, criação e edição de estudos), com navegação direta e suporte a filtro por clique no calendário.
4. **Respeito Estrito à Lixeira**: Ocultação imediata de itens soft-deleted e restauração retroativa precisa.

A abordagem técnica não requer novas tabelas nem migrações no banco SQLite, operando via agregações instantâneas sobre os carimbos `created_at`, `updated_at` e `deleted_at` existentes nas tabelas `books` e `studies`.

---

## Technical Context

**Language/Version**: Python 3.13 (Backend) | TypeScript 5.7+ / Node.js v24 (Frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic v2 (Backend) | Vue 3 (Composition API, `<script setup>`), Vue Router 4, Vite (Frontend)  
**Storage**: SQLite local (`caderno.db`), modo WAL, sem necessidade de alterações ou migrações de schema  
**Testing**: `pytest` com bancos descartáveis em `tmp_path` (Backend) | `node --test` com asserções estritas (Frontend)  
**Target Platform**: Windows local (PowerShell, processo único via `iniciar.py`, compatível com rede privada/Tailscale)  
**Project Type**: Aplicação Web Local (FastAPI REST API + Vue 3 SPA)  
**Performance Goals**: Tempo de resposta do endpoint `/api/dashboard` < 50ms; renderização inicial completa da tela < 1s; filtragem de timeline por data < 100ms  
**Constraints**: Banco ativo `backend/data/caderno.db` estritamente intocado em testes; conformidade total com as 5 Superclasses de Interface e os 10 temas visuais; responsividade mobile (< 360px)  
**Scale/Scope**: 1 novo router backend (`dashboard.py`), 1 service backend (`dashboard_service.py`), 1 nova view frontend (`DashboardView.vue`), 1 componente visual (`HeatmapCalendar.vue`), integração de rota e menu global.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Artigo I (Privacidade e Preservação)**: PASS. Nenhuma anotação pessoal ou texto do acervo é exposto ou transmitido para fora do processo local. As agregações são estritamente quantitativas e anonimizadas no retorno da API.
- **Artigo II (Isolamento de Testes)**: PASS. Testes automatizados executam contra bancos SQLite temporários em `tmp_path` com portas efêmeras, sem conexão ao banco ativo.
- **Artigo III (Fidelidade Tecnológica)**: PASS. FastAPI no backend, Vue 3 com TypeScript estrito no frontend, SQLite local. Sem dependência de bibliotecas pesadas de gráficos de terceiros.
- **Artigo IV (Governança e Estado do Roadmap)**: PASS. As 10 tarefas do Roadmap 0.3 continuam registradas como NÃO INICIADAS até homologação completa. Ciclo Spec Kit rigorosamente seguido.
- **Artigo V (Resiliência e Integridade)**: PASS. Como a funcionalidade utiliza carimbos já existentes nas tabelas `books` e `studies`, nenhuma migração estrutural de banco é necessária, eliminando riscos de integridade.

---

## Project Structure

### Documentation (this feature)

```text
specs/013-dashboard-calendario-timeline/
├── spec.md              # Especificação de requisitos e clarificações aprovadas
├── checklists/
│   └── requirements.md  # Checklist de qualidade (100% PASS)
├── plan.md              # Este plano técnico de implementação
├── research.md          # Decisões arquiteturais D1 a D4
├── data-model.md        # Schemas Pydantic, entidades e regras de cálculo
├── contracts/
│   └── dashboard.contract.md # Contrato da API GET /api/dashboard
├── quickstart.md        # 5 cenários executáveis de validação
└── tasks.md             # Tarefas atômicas (geradas na próxima etapa por /speckit-tasks)
```

### Source Code Modificado (Arquivos Mapeados)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── main.py                     # Registro do router /api/dashboard
│   │   ├── routers/
│   │   │   └── dashboard.py            # Endpoint GET /api/dashboard com validação de query
│   │   ├── schemas/
│   │   │   └── dashboard.py            # Schemas Pydantic: DashboardSummary, HeatmapPoint, TimelineItem
│   │   └── services/
│   │       └── dashboard_service.py    # Consultas agregadas, streak e eventos no SQLAlchemy 2
│   └── tests/
│       └── test_dashboard.py           # Testes unitários e de integração herméticos com tmp_path
└── frontend/
    ├── src/
    │   ├── App.vue                     # Inclusão do link 'Dashboard' no menu principal
    │   ├── router/
    │   │   └── index.ts                # Registro da rota /dashboard
    │   ├── types.ts                    # Interfaces TypeScript do Dashboard
    │   ├── services/
    │   │   └── api.ts                  # Método getDashboard(params) no cliente HTTP
    │   ├── components/
    │   │   └── HeatmapCalendar.vue     # Componente do mapa de calor (desktop/mobile, tooltips)
    │   └── views/
    │       └── DashboardView.vue       # View principal encapsulada em nó raiz único
    └── tests/
        └── dashboard.test.mjs          # Testes frontend para métricas, heatmap e filtros
```

---

## Plan Workflow & Milestones

1. **Fase 1: Backend de Produtividade e Métricas (US1 - MVP)**
   - Criar schemas Pydantic em `backend/app/schemas/dashboard.py`.
   - Implementar regras de negócio e agregação em `backend/app/services/dashboard_service.py` (contagens, streak e ordenação).
   - Implementar router `backend/app/routers/dashboard.py` e registrar em `backend/app/main.py`.
   - Escrever testes herméticos em `backend/tests/test_dashboard.py`.
2. **Fase 2: Visualização Frontend e Métricas Principais (US1 - MVP)**
   - Adicionar tipos em `frontend/src/types.ts` e método na API `frontend/src/services/api.ts`.
   - Criar `frontend/src/views/DashboardView.vue` com cartões de métricas, estados vazios acolhedores e envoltório raiz único `<div class="dashboard-view">`.
   - Configurar rota `/dashboard` e atalho com ícone SVG na navegação de `frontend/src/App.vue`.
3. **Fase 3: Mapa de Calor Responsivo (US2)**
   - Criar componente `frontend/src/components/HeatmapCalendar.vue`.
   - Implementar recorte adaptativo (12 meses desktop, 3 a 6 meses mobile com expansão).
   - Estilizar os 4 níveis visuais via CSS custom properties integradas aos temas e Superclasses.
   - Adicionar tooltips com dados locais e interação de seleção por clique.
4. **Fase 4: Timeline e Filtro Integrado (US3)**
   - Implementar lista cronológica reversa na `DashboardView.vue` com links diretos de leitura.
   - Conectar o clique nas células do calendário para filtrar a timeline por data em < 100ms.
   - Adicionar banner de filtro ativo com botão de limpeza.
5. **Fase 5: Validação Automatizada e Conclusão**
   - Executar suíte backend (`pytest`).
   - Executar suíte frontend (`npm test` e `npm run build`).
   - Validar cenários de teste do `quickstart.md`.

---

## Complexity Tracking

*Nenhuma violação constitucional detectada. Nenhuma dependência externa ou complexidade injustificada adicionada.*
