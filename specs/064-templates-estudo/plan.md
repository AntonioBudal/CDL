# Implementation Plan: F0.7.15 — Templates Estruturados de Estudo

**Branch**: `064-templates-estudo` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/064-templates-estudo/spec.md`

---

## Summary

Oferecer 5 modelos mentais canônicos de análise pré-configurados (`classico`, `conceito`, `argumento`, `comparativo`, `resenha`) para guiar o leitor no fichamento de obras e conceitos, mantendo 100% de conformidade com os 4 pilares do banco de dados do Leitorum (`summary`, `explanation`, `concepts`, `references`). A feature introduz a persistência do campo opcional `template_id` no modelo `Study`, um catálogo canônico imutável de templates no frontend, modal de prévia/seleção acessível, salvaguarda com confirmação explícita na troca de template (com opções de "Substituir" ou "Anexar ao final") e exibição sutil do modelo na visualização do estudo.

---

## Technical Context

**Language/Version**: Python 3.13 / 3.14 (Backend) e TypeScript 5.9+ / Node.js 20+ (Frontend)

**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- Frontend: Vue 3 (Composition API), Vite, Tailwind CSS, markdown-it

**Storage**: SQLite 3 local com modo WAL ativado e chaves estrangeiras ativas

**Testing**:
- Backend: `pytest` com banco efêmero `tmp_path` e portas efêmeras
- Frontend: `node:test` e `node:assert/strict`

**Target Platform**: Windows local (processo único `iniciar.py`) atendendo PC e dispositivos móveis

**Project Type**: Web application local-first (FastAPI + Vue 3 SPA)

**Performance Goals**:
- Carregamento instantâneo do catálogo e prévia (< 10ms)
- Injeção de esqueleto Markdown no formulário sem atraso perceptível (< 50ms)

**Constraints**:
- Ausência total de emojis no frontend
- Alvos de toque $\ge 44 \times 44$px para mobile
- Não modificar o esquema canônico de 4 campos do banco de dados
- Compatibilidade absoluta com o acervo legado (`template_id` assume `'classico'` como padrão)

**Scale/Scope**: 5 templates canônicos fixos; afeta `StudyEditView.vue`, `StudyEditorFields.vue`, `StudyView.vue` e modelo `Study`.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Justificativa / Verificação |
|---|---|---|
| **I. Proteção do Acervo e Privacidade** | APROVADO | Nenhum dado real de produção é acessado. Testes e validações usam dados sintéticos em bancos efêmeros descartáveis. |
| **II. Isolamento Estrito de Testes** | APROVADO | Testes do backend utilizarão bancos temporários `tmp_path`. Nenhuma leitura ou escrita em `backend/data/caderno.db`. |
| **III. Fidelidade Arquitetural** | APROVADO | Stack oficial mantida (FastAPI, SQLAlchemy 2, Alembic, Vue 3, TS estrito). Não adiciona dependências externas ou nuvem. |
| **IV. Spec-Driven Development (SDD)** | APROVADO | Ciclo de especificação concluído (`spec.md`), planejamento técnico detalhado (`plan.md`) prévio à geração de tarefas. |
| **V. Transações e Migrações Seguras** | APROVADO | Migração Alembic `0029_add_template_id_to_studies.py` com `server_default='classico'` garantindo atomicidade e retrocompatibilidade com WAL. |

---

## Project Structure

### Documentation (this feature)

```text
specs/064-templates-estudo/
├── spec.md              # Especificação de requisitos e cenários
├── checklists/
│   └── requirements.md  # Validação de qualidade da especificação
├── research.md          # Decisões de pesquisa técnica (Phase 0)
├── data-model.md        # Modelo de dados e catálogo canônico (Phase 1)
├── contracts/
│   └── study-templates-api.yaml # Contrato OpenAPI para API de estudos (Phase 1)
├── quickstart.md        # Roteiro de testes rápidos e validação (Phase 1)
├── plan.md              # Este plano de implementação
└── tasks.md             # Tarefas de implementação (/speckit-tasks)
```

### Source Code

```text
backend/
├── app/
│   ├── models/
│   │   └── study.py                  # Adiciona coluna template_id no modelo Study
│   └── schemas/
│       └── study.py                  # Adiciona template_id nos schemas StudyCreate, StudyPatch e StudySummary
├── migrations/
│   └── versions/
│       └── 0029_add_template_id_to_studies.py # Migração Alembic
└── tests/
    └── test_study_templates.py       # Testes de integração para template_id

frontend/
├── src/
│   ├── constants/
│   │   └── studyTemplates.ts         # Catálogo canônico dos 5 templates
│   ├── types.ts                      # Tipos TypeScript para templates de estudo
│   ├── components/
│   │   ├── studies/
│   │   │   └── TemplateSelectorModal.vue # Modal acessível de prévia e seleção
│   │   └── StudyEditorFields.vue     # Seletor de template integrado e salvaguarda
│   └── views/
│       ├── StudyEditView.vue         # Suporte a template no formulário de edição
│       └── StudyView.vue             # Badge discreto indicando o template de análise
└── tests/
    └── study_templates.test.mjs      # Testes de unidade e contratos no frontend
```

---

## Complexity Tracking

*Nenhuma violação constitucional detectada. Sem complexidade desnecessária.*
