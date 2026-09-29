# Implementation Plan: F0.6.5 — Histórico Automático de Versões de Estudo

**Branch**: `044-historico-automatico` | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/044-historico-automatico/spec.md`

---

## Summary

Implementar a infraestrutura completa de versionamento automático para os estudos do Leitorum, permitindo que alterações textuais sejam arquivadas sem intervenção manual do usuário, consultadas em linha do tempo cronológica, comparadas por diff visual e restauradas com total segurança atômica (incluindo texto e destaques de Leitura Ativa).

---

## Technical Context

**Language/Version**: Python 3.13 (Backend), TypeScript 6.0 / Node.js 24+ (Frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (Mapped Annotations), Alembic (Backend); Vue 3.5 (Composition API), Vite 8, Lucide Vue Next (Frontend)  
**Storage**: SQLite local em modo Write-Ahead Logging (WAL), tabela `study_versions`  
**Testing**: `pytest` com banco SQLite descartável em `tmp_path` (Backend); `node --test` e `vue-tsc` (Frontend)  
**Target Platform**: Windows 11 (PowerShell), navegadores modernos (desktop e mobile)  
**Project Type**: Aplicação Web local (FastAPI REST API + Vue 3 SPA empacotado)  
**Performance Goals**: Carregamento da linha do tempo em < 1s; cálculo e renderização de diff comparativo em < 500ms  
**Constraints**: Zero emojis na interface e no código; isolamento absoluto do banco ativo `caderno.db` durante testes; janela de coalescência de 5 minutos para edições contíguas do mesmo autor; snapshot integral contendo seções e destaques de Leitura Ativa  
**Scale/Scope**: Suporte a dezenas de versões por estudo com carregamento otimizado e diff eficiente por seções  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Proteção Absoluta do Acervo e Privacidade de Dados**: Nenhuma leitura ou exposição de dados reais de usuários no chat ou testes. Preservação de integridade de chaves e campos originais.
- [x] **II. Isolamento Estrito de Testes e Operações Locais**: Testes unitários e de integração executados exclusivamente com instâncias descartáveis em `tmp_path`.
- [x] **III. Fidelidade Arquitetural e Tecnológica**: Uso estrito da stack definida (Python 3.13, FastAPI, SQLAlchemy 2, Alembic, SQLite WAL, Vue 3 TypeScript).
- [x] **IV. Governança por Especificação Delimitada (Spec-Driven Development)**: Ciclo formal `specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement`.
- [x] **V. Resiliência Operacional, Transações e Migrações Seguras**: Migração declarativa Alembic `0021_add_study_versions.py` com rollback e integridade referencial em cascata.

---

## Project Structure

### Documentation (this feature)

```text
specs/044-historico-automatico/
├── spec.md              # Especificação de requisitos e cenários
├── checklists/
│   └── requirements.md  # Checklist de qualidade (16/16 aprovado)
├── plan.md              # Este plano técnico de implementação
├── research.md          # Decisões arquiteturais e de algoritmos
├── data-model.md        # Modelos relacionais e schema de dados
├── contracts/
│   └── study-versions-api.md # Contratos de endpoints REST
└── quickstart.md        # Cenários de validação e testes automatizados
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── study.py                     # Adicionar relationship com StudyVersion
│   │   │   └── study_version.py             # Novo modelo SQLAlchemy StudyVersion
│   │   ├── schemas/
│   │   │   └── study_version.py             # Schemas Pydantic (Summary, Detail, Diff)
│   │   ├── services/
│   │   │   └── study_version_service.py     # Lógica de gravação automática, coalescência, diff e restauração
│   │   ├── routers/
│   │   │   ├── studies.py                   # Integração do hook de salvamento de versão no patch
│   │   │   └── study_versions.py            # Endpoints REST de versões
│   │   └── main.py                          # Inclusão do router de versões
│   ├── migrations/versions/
│   │   └── 0021_add_study_versions.py       # Migração Alembic
│   └── tests/
│       └── test_study_versions.py           # Testes automatizados com banco isolado
│
└── frontend/
    └── src/
        ├── types.ts                         # Tipos TypeScript para StudyVersion e Diff
        ├── services/
        │   └── api.ts                       # Métodos de API para listar, inspecionar, diff e restaurar
        ├── components/
        │   ├── StudyHistoryModal.vue        # Modal de histórico, linha do tempo e confirmação
        │   └── StudyDiffViewer.vue          # Componente de renderização de diferenças por seção
        └── views/
            ├── StudyView.vue                # Botão de histórico e acionamento do modal
            └── StudyEditView.vue            # Acesso ao histórico no contexto de edição
```

---

## Complexity Tracking

> **Nenhuma violação aos princípios constitucionais. Não há dependências externas adicionais.**
