# Implementation Plan: F0.6.1 — Importação Inteligente

**Branch**: `040-importacao-inteligente` | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/040-importacao-inteligente/spec.md`

## Summary

Evoluir a importação de fichamentos no Leitorum para uma experiência contínua e tolerante baseada no fluxo **`Colar → Leitorum entende → Usuário confere → Salvar`**.
A abordagem técnica consiste em:
1. **Parser Semântico Tolerante (Backend)**: Expandir `import_parser.py` para reconhecer variações lexicais usuais em português (`visão geral`, `síntese`, `aprofundamento`, `termos-chave`, `fontes`), marcadores Markdown diversos (`#`, `##`, `###`, `**negrito**`), numerações ordinais e sufixos, preservando estritamente code fences (` ``` `) e a integridade de `source_response`.
2. **Fluxo Fluido e Prévia Unificada (Frontend)**: No `ImportView.vue` e `useImportDraft.ts`, disparar a prévia instantaneamente no evento de colagem (`paste`), fornecer botões de atribuição rápida (1 clique) para conteúdo não classificado, aplicar política de anexar texto residual não classificado ao final da Explicação (zero perda de dados) e recolher os 4 campos manuais legados sob um painel colapsável ("Ajuste manual detalhado").

---

## Technical Context

**Language/Version**: Python 3.13 (64-bit) no backend, TypeScript 5.x / Vue 3 no frontend  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 (ORM), Vite, Tailwind CSS / Vanilla CSS  
**Storage**: SQLite local (modo WAL), tabela `studies` já existente (sem novas migrations necessárias)  
**Testing**: `pytest` (backend) com bancos descartáveis via `tmp_path`; `vitest` / `vue-test-utils` (frontend)  
**Target Platform**: Windows local (PowerShell, Uvicorn processo único em `iniciar.py`)  
**Project Type**: Aplicação Web local (SPA Vue 3 servida por backend FastAPI)  
**Performance Goals**: Análise de texto e retorno de prévia em < 100ms para até 50.000 caracteres  
**Constraints**: Zero perda de texto; preservação estrita de `source_response`; sem dependências pesadas de NLP externo; 100% determinístico e local  
**Scale/Scope**: Operação local em processo único atendendo PC e dispositivos móveis na rede local/Tailscale  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio Constitucional | Avaliação | Status |
| :--- | :--- | :---: |
| **I. Proteção do Acervo e Privacidade** | O texto colado é processado estritamente em memória local; o texto original `source_response` é salvo na íntegra no banco sem truncamento; zero envio de dados para serviços externos. | ✅ APROVADO |
| **II. Isolamento Estrito de Testes** | Todos os novos testes unitários e de integração de importação utilizam bancos efêmeros (`tmp_path`) e fixtures isoladas. | ✅ APROVADO |
| **III. Fidelidade Arquitetural** | Respeita FastAPI, Pydantic v2, Vue 3 Composition API com `<script setup>` e TypeScript estrito. | ✅ APROVADO |
| **IV. Governança por SDD** | Execução rigorosa do fluxo Spec Kit (`speckit-specify` → `speckit-plan` → `speckit-tasks` → `speckit-implement`). | ✅ APROVADO |
| **V. Resiliência e Migrações Seguras** | Não requer alteração no schema da tabela `studies` nem migração Alembic, operando sobre colunas existentes. | ✅ APROVADO |

---

## Project Structure

### Documentation (this feature)

```text
specs/040-importacao-inteligente/
├── spec.md                  # Especificação funcional refinada e aprovada
├── checklists/
│   └── requirements.md      # Checklist de validação de qualidade (100% OK)
├── plan.md                  # Este plano de implementação técnica
├── research.md              # Pesquisa técnica e justificativas de arquitetura
├── data-model.md            # Modelo de dados e DTOs de análise
├── contracts/
│   └── import-preview-contract.md  # Contrato formal da API /api/imports/preview
└── quickstart.md            # Guia de validação automatizada e cenários manuais
```

### Source Code (repository layout)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   └── import_parser.py     # Parser sintático e léxico tolerante (Regex + Normalização)
│   │   ├── schemas/
│   │   │   └── imports.py           # DTOs Pydantic (ImportPreviewRead, ImportPreviewRequest, ImportWarningRead)
│   │   └── routers/
│   │       └── imports.py           # Endpoint POST /api/imports/preview (stateless)
│   └── tests/
│       └── unit/
│           └── test_import_parser.py # Testes de variação léxica, formatações e fences
├── frontend/
│   └── src/
│       ├── composables/
│       │   └── useImportDraft.ts    # Lógica reativa: paste trigger, atribuição rápida e política de unassigned
│       ├── views/
│       │   └── ImportView.vue       # UI: colagem direta, prévia visual em cards e painel colapsável legado
│       └── components/
│           └── StudyEditorFields.vue # Campos manuais reutilizáveis
```

**Structure Decision**: Aplicação web com separação clássica `backend/` e `frontend/`, preservando a estrutura padrão do projeto.

---

## Complexity Tracking

*Nenhuma violação aos princípios constitucionais ou padrões de projeto foi identificada. O design preserva a simplicidade, executando toda a análise em tempo real com baixo custo computacional e máxima robustez.*
