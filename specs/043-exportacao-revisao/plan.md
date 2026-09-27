# Implementation Plan: F0.6.4 — Exportação com Destaques e Caderno de Revisão

**Branch**: `043-exportacao-revisao` | **Date**: 2026-09-27 | **Spec**: [specs/043-exportacao-revisao/spec.md](spec.md)

**Input**: Feature specification from `specs/043-exportacao-revisao/spec.md`

---

## Summary

Estender o subsistema de exportação do Leitorum nos formatos Markdown (`.md`) e Texto Puro (`.txt`) para:
1. **Estudo e Livro Completo com Destaques**: Injetar visualmente os grifos e vincular anotações/perguntas ativas através de notas de rodapé padrão Markdown (`==texto==[^N]` + `[^N]: [Tipo] Anotação`) usando algoritmo de percurso reverso por offset, garantindo imunidade a descolamento de índices.
2. **Caderno de Revisão (Digest)**: Criar modalidade dedicada de exportação (estudo ou livro consolidado) que compila perguntas ativas, termos ocluídos e notas marginais organizados por capítulo e estudo.
3. **Modos de Estudo e Exercício**: Permitir alternância entre Modo Exercício (respostas omitidas com linhas de preenchimento `_______` e reunidas em um Gabarito Final) e Modo Estudo (respostas expostas inline).
4. **Interface Intuitiva**: Estender `ExportModal.vue` com abas/seletores acessíveis, compatibilidade total com os 10 temas visuais e conformidade com a Constituição do Leitorum.

---

## Technical Context

**Language/Version**: Python 3.13 (Backend) | TypeScript 5.6+ / Vue 3.5+ (Frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic v2, Vite, markdown-it  
**Storage**: SQLite local (modo WAL), tabelas relacionais `books`, `chapters`, `studies`, `study_highlights`  
**Testing**: pytest com `tmp_path` e `$env:REQUIRE_AUTH="false"` (Backend) | Vitest com Vue Test Utils (Frontend)  
**Target Platform**: Windows local (PowerShell, Uvicorn em processo único local através de `iniciar.py`)  
**Project Type**: Web application (FastAPI backend + Vue 3 SPA frontend)  
**Performance Goals**: Tempo de exportação de estudo individual < 1s; compilação de livro completo com 20+ estudos < 3s  
**Constraints**: Zero mutações no acervo original (operação estritamente de leitura); zero emojis no código de `frontend/src`; respeito total ao WCAG AA (botões $\ge 44 \times 44\text{px}$)  
**Scale/Scope**: Suporte a livros com 50+ estudos e centenas de destaques sem estouro de memória  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Princípio I (Proteção do Acervo & Privacidade)**: Operação puramente somente leitura (`SELECT`). O Markdown original salvo na base nunca é sobrescrito nem alterado. Zero vazamento de dados do usuário em logs ou serviços externos.
- [x] **Princípio II (Isolamento de Testes)**: Toda a suíte de testes unitários e de integração roda em bancos SQLite descartáveis criados em `tmp_path`, sem jamais acessar `backend/data/caderno.db`.
- [x] **Princípio III (Fidelidade Arquitetural)**: Stack 100% aderente a Python 3.13, FastAPI, SQLAlchemy 2.0, Vue 3 (`<script setup>`), TypeScript estrito e Vite. Zero dependências externas de nuvem ou APIs pagas.
- [x] **Princípio IV (Governança SDD)**: O ciclo formal de especificação e desenho técnico (`specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement`) é rigidamente observado.
- [x] **Princípio V (Resiliência & Transações)**: Não há alterações no schema do banco (a tabela `study_highlights` já foi introduzida em F0.6.1). Nenhum script de migração arriscado é requerido.

**Status dos Gates**: **100% APROVADO** (Nenhuma violação constitucional).

---

## Project Structure

### Documentation (this feature)

```text
specs/043-exportacao-revisao/
├── spec.md                  # Especificação funcional ratificada com esclarecimentos Q1 e Q2
├── plan.md                  # Este plano de implementação técnica
├── research.md              # Phase 0: Decisões técnicas e algoritmos de injeção
├── data-model.md            # Phase 1: Modelos de dados e schemas intermediários
├── quickstart.md            # Phase 1: Roteiro de validação automatizada e manual
├── contracts/
│   └── export-contract.md   # Phase 1: Contrato HTTP da API de exportação e frontend
└── tasks.md                 # Phase 2: Decomposição de tarefas (/speckit-tasks)
```

### Source Code (repository layout)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── schemas/
│   │   │   └── export.py              # ExportOptions estendido (export_type, include_highlights, exercise_mode)
│   │   ├── services/
│   │   │   └── export_service.py       # Funções de injeção reversa, format_study_digest e format_book_digest
│   │   └── routers/
│   │       ├── books.py               # Rota GET /api/books/{id}/export com novos query params
│   │       └── studies.py             # Rota GET /api/studies/{id}/export com novos query params
│   └── tests/
│       └── test_export.py             # Testes de regressão e novas asserções de destaques e digest
└── frontend/
    └── src/
        ├── types.ts                   # Interface ExportConfig e ExportType estendidos
        ├── services/
        │   └── api.ts                 # Atualização de buildExportQuery para novos parâmetros
        └── components/
            ├── ExportModal.vue        # Interface com seleção de modo (Completo vs Caderno de Revisão)
            └── __tests__/
                └── ExportModal.spec.ts # Testes unitários do modal de exportação
```

**Structure Decision**: Padrão de aplicação web existente preservado com separação estrita de backend FastAPI e frontend Vue 3.

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|:---|:---|:---|
| *Nenhuma violação identificada* | N/A | N/A |

---

## Phases & Execution Milestones

### Phase 0: Outline & Research
- Algoritmo de injeção reversa para inserção de grifos e notas de rodapé sem descolamento de índices.
- Definição do formato canônico do Caderno de Revisão e suporte ao Modo Exercício.
- Documentado em [specs/043-exportacao-revisao/research.md](research.md).

### Phase 1: Design & Contracts
- Modelagem de dados e esquemas intermediários de agregação em [specs/043-exportacao-revisao/data-model.md](data-model.md).
- Especificação formal de endpoints e payloads em [specs/043-exportacao-revisao/contracts/export-contract.md](contracts/export-contract.md).
- Guia de validação ponta a ponta em [specs/043-exportacao-revisao/quickstart.md](quickstart.md).
- Reavaliação constitucional concluída com aprovação total.

### Next Step
Prosseguir para `/speckit-tasks` para geração de tarefas atômicas e ordenadas de implementação.
