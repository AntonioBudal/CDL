# Implementation Plan: Edição Completa de Metadados de Livros, Capítulos e Anotações

**Branch**: `002-edicao-livros-estudos` | **Date**: 2026-09-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-edicao-livros-estudos/spec.md`

## Summary

Esta feature implementa a capacidade integral de curadoria e refinamento do acervo, cobrindo a edição de livros (título obrigatório, autor/subtítulo/ano opcionais), renomeação e reordenação atômica de capítulos (botões subir/descer) e edição refinada de anotações com preservação da resposta original importada. Para garantir que nenhuma edição seja perdida quando o leitor utiliza alternadamente o PC e o celular, introduz-se controle de concorrência otimista via timestamp `updated_at`, recusando escritas conflitantes com HTTP 409 e preservando 100% dos dados digitados no formulário. A evolução de schema é gerenciada com segurança pelo Alembic sob a proteção da barreira de snapshot pré-migração estabelecida na Feature 001.

## Technical Context

**Language/Version**: Python 3.13.15 (64-bit Windows), TypeScript 5.9 (Node.js v24.14.1)  
**Primary Dependencies**: FastAPI 0.141.1, SQLAlchemy 2.0.52, Alembic 1.19.2, Pydantic 2.13.5, Vue 3.5.13, Vite 6.2.0  
**Storage**: SQLite local (WAL em execução, DELETE nas cópias de backup), compatível com caminhos especiais no Windows  
**Testing**: pytest 9.1.1 (`backend/tests/test_edit_acervo.py`), node:test (`frontend/tests/`), 100% isolados via `tmp_path`  
**Target Platform**: Windows local (PowerShell), processo único servindo desktop e mobile (Tailscale/LAN)  
**Project Type**: Web Application monousuário pessoal (FastAPI backend servindo API REST e Vue 3 SPA compilado)  
**Performance Goals**: Atualizações em tempo de resposta < 50ms; reordenação atômica de capítulos instantânea  
**Constraints**: Imutabilidade estrita de `source_response`; bloqueio gracioso de concorrência com 409; zero vazamento de dados privados  
**Scale/Scope**: Monousuário, biblioteca pessoal de estudos com milhares de anotações  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Exigência | Avaliação no Plano | Status |
|---|---|---|---|
| **Art. I: Privacidade do Acervo** | Jamais exibir ou logar textos do acervo no chat ou terminal | Todas as validações e testes utilizam dados sintéticos em bases efêmeras descartáveis | **PASS** |
| **Art. II: Isolamento de Testes** | Testes nunca tocam em `backend/data/caderno.db` | Suíte criada exclusivamente com fixtures `tmp_path` | **PASS** |
| **Art. III: Fidelidade Tecnológica** | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Vue 3, Vite | Mantida estritamente a stack aprovada sem introdução de novas dependências | **PASS** |
| **Art. IV: Governança SDD** | Fatias pequenas e verificáveis; T01–T10 não iniciadas | Esta fatia especifica os requisitos de T01 e T09 sem alterar status formal das tarefas | **PASS** |
| **Art. V: Resiliência Operacional** | Proteção atômica de banco antes de migrações | Migração incremental do Alembic protegida pela barreira da Feature 001 | **PASS** |

## Project Structure

### Documentation (this feature)

```text
specs/002-edicao-livros-estudos/
├── spec.md              # Especificação de requisitos e cenários de aceite
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas consolidadas (D1 a D4)
├── data-model.md        # Modelagem de entidades, validações e concorrência
├── quickstart.md        # Guia passo a passo de validação executável
├── contracts/           # Contratos de API REST
│   └── api-contracts.md
└── checklists/
    └── requirements.md  # Checklist de qualidade (100% aprovado)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/                    # Modelos Book, Chapter e Study com novos metadados e updated_at
│   │   ├── schemas/                   # Schemas Pydantic (BookPatch, ChapterPatch, StudyPatch)
│   │   ├── routers/
│   │   │   ├── books.py               # PATCH /books/{id}
│   │   │   ├── chapters.py            # PATCH e POST /move para capítulos
│   │   │   └── studies.py             # PATCH /studies/{id} com concorrência otimista
│   │   └── services/
│   │       └── persistence.py         # Tratamento de commit e validação de concorrência
│   ├── migrations/
│   │   └── versions/                  # Nova migração incremental do Alembic
│   └── tests/
│       └── test_edit_acervo.py        # Suíte de testes isolados da feature
└── frontend/
    └── src/
        ├── services/api.ts            # Métodos de chamada de edição e movimentação
        ├── types.ts                   # Interfaces TypeScript atualizadas (Book, Chapter, Study)
        ├── views/
        │   ├── BookView.vue           # Modal de edição de livro e botões subir/descer capítulos
        │   └── StudyEditView.vue      # Tratamento de erro 409 e banner de preservação de texto
        └── components/
            └── BookEditModal.vue      # Modal de edição de metadados do livro
```

**Structure Decision**: A implementação estende os módulos de backend existentes (`routers`, `schemas`, `models`) e os componentes do frontend Vue sem criar camadas artificiais.

## Complexity Tracking

> Nenhuma violação constitucional identificada.
