# Implementation Plan: F 0.7.4 — Redesenho da Grid View: Reconhecimento Visual e Cartografia de Leitura

**Branch**: `053-redesenho-grid-view` | **Date**: 2026-10-03 | **Spec**: [specs/053-redesenho-grid-view/spec.md](spec.md)

**Input**: Feature specification from `/specs/053-redesenho-grid-view/spec.md`

---

## Summary

Redesenhar a `StudyGridView.vue` para consolidar sua responsabilidade central no Caderno de Leitura: **reconhecimento visual instantâneo, densidade analítica e cartografia de leitura do capítulo**.
A implementação integra:
1. Friso vertical cromático por status de leitura (`rascunho`, `em_andamento`, `revisado`, `concluido`) na borda esquerda do cartão, harmonizado com o badge no cabeçalho.
2. Exibição de prévia analítica de 2 a 3 linhas com corte suave (*line-clamp*), priorizando `summary` e caindo em fallback para `explanation`.
3. Mini-indicadores visuais no rodapé informando a quantidade de destaques/anotações e de conexões semânticas.
4. Superfície de clique integral para leitura ágil, com botão de exclusão isolado (`@click.stop`) e diálogo de confirmação.
5. Grid responsivo de 1 a 3 colunas e telas de esqueleto (*Skeleton Screens*) animadas durante o carregamento.

---

## Technical Context

**Language/Version**: Python 3.13 (Backend) / TypeScript 5.8+ (Frontend)  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0, Vue 3 (Composition API), Vite, Tailwind/CSS  
**Storage**: SQLite local (WAL mode, sem alteração de schema em banco — apenas queries agregadas)  
**Testing**: `node --test` (Frontend unitário), `pytest` (Backend integração), `vue-tsc -b` (Tipagem estrita)  
**Target Platform**: Windows local (processo único `iniciar.py`) / Web desktop e mobile (Tailscale)  
**Project Type**: Aplicação Web híbrida (Backend REST FastAPI + Frontend SPA Vue 3)  
**Performance Goals**: Tempo de resposta da listagem < 15ms no SQLite; renderização da grade em < 50ms no cliente  
**Constraints**: Zero impacto em banco de produção (`backend/data/caderno.db`); testes em bancos efêmeros (`tmp_path`)  
**Scale/Scope**: Capítulos com até centenas de estudos; agregação em lote em 1 único round-trip SQL  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I (Privacidade e Acervo):** ✅ PASS. Nenhuma leitura de acervo real; dados sintéticos para testes.
- **Princípio II (Isolamento de Testes):** ✅ PASS. Testes usam `tmp_path` e instâncias descartáveis.
- **Princípio III (Fidelidade Arquitetural):** ✅ PASS. Stack Python 3.13 / FastAPI + Vue 3 / TS estrito.
- **Princípio IV (Spec-Driven Development):** ✅ PASS. Conduzido estritamente pelo ciclo Spec Kit.
- **Princípio V (Resiliência Operacional):** ✅ PASS. Sem migrações destrutivas de schema; dados persistidos com segurança.

---

## Project Structure

### Documentation (this feature)

```text
specs/053-redesenho-grid-view/
├── spec.md              # Especificação refinada com esclarecimentos
├── plan.md              # Este plano técnico de implementação
├── research.md          # Decisões arquiteturais D1 a D5
├── data-model.md        # Schemas e mapeamento de status
├── quickstart.md        # 5 cenários de validação fim a fim
├── contracts/           # Contratos de API e componentes
│   └── study-grid-api.md
├── checklists/
│   └── requirements.md  # Checklist de qualidade (16/16 PASS)
└── tasks.md             # Tarefas atômicas (geradas pelo /speckit-tasks)
```

### Source Code

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   └── studies.py               # Agregação em lote de contagens e summary_preview
│   │   └── schemas/
│   │       └── study.py                 # Extensão do StudySummary com novos campos
│   └── tests/
│       └── test_study_grid_summary.py   # Teste de integração backend das métricas da grade
└── frontend/
    ├── src/
    │   ├── types.ts                     # Extensão da interface StudySummary
    │   └── components/
    │       └── views/
    │           └── StudyGridView.vue    # Redesenho da grade com friso, prévia e skeletons
    └── tests/
        └── study_grid_view.test.mjs     # Testes unitários do componente e responsividade
```

**Structure Decision**: Web application padrão do repositório, com modelo modular backend FastAPI e componentes Vue 3 no frontend.

---

## Complexity Tracking

*Nenhuma violação aos princípios da Constituição.*
