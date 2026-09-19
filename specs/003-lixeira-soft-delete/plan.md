# Implementation Plan: Lixeira e Restauração de Itens (Soft Delete)

**Branch**: `003-lixeira-soft-delete` | **Date**: 2026-09-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-lixeira-soft-delete/spec.md`

## Summary

Esta feature implementa o sistema de Lixeira e Exclusão Segura (*soft delete*) para o Caderno de Leitura, atendendo à entrega T02 do Roadmap 0.3. O objetivo principal é blindar o acervo pessoal do leitor contra perdas de dados acidentais ao reorganizar livros e anotações, substituindo exclusões diretas por descarte temporário com timestamp UTC (`deleted_at`). A funcionalidade compreende o envio seguro de livros e estudos para a lixeira, a ocultação automática de itens descartados no acervo ativo, a visualização unificada na nova tela `TrashView.vue`, a restauração seletiva e em cascata ascendente (reativando livro/capítulo ao restaurar um estudo), a exclusão física deliberada transacional e uma política de purga automática após 30 dias de retenção.

## Technical Context

**Language/Version**: Python 3.13.15 (64-bit Windows), TypeScript 5.9 (Node.js v24.14.1)  
**Primary Dependencies**: FastAPI 0.141.1, SQLAlchemy 2.0.52, Alembic 1.19.2, Pydantic 2.13.5, Vue 3.5.13, Vite 6.2.0  
**Storage**: SQLite local em modo WAL com chaves estrangeiras ativas (`PRAGMA foreign_keys = ON`), compatível com caminhos e acentuação no Windows  
**Testing**: pytest 9.1.1 (`backend/tests/test_trash_soft_delete.py`), node:test (`frontend/tests/`), 100% isolados via `tmp_path`  
**Target Platform**: Windows local (PowerShell), processo único local servindo desktop e dispositivos móveis (Tailscale/LAN)  
**Project Type**: Web Application monousuário pessoal (FastAPI backend REST + SPA Vue 3)  
**Performance Goals**: Tempo de resposta < 50ms para descarte e restauração; carregamento da lixeira < 100ms  
**Constraints**: Zero perda de dados acidental; transações atômicas na purga e exclusão definitiva; proteção total do banco de produção  
**Scale/Scope**: Monousuário, biblioteca pessoal com centenas de livros e milhares de anotações  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Exigência | Avaliação no Plano | Status |
|---|---|---|---|
| **Art. I: Privacidade do Acervo** | Jamais exibir ou logar textos do acervo no chat ou terminal | Todas as validações e testes utilizam exclusivamente dados sintéticos em bases efêmeras descartáveis | **PASS** |
| **Art. II: Isolamento de Testes** | Testes nunca tocam em `backend/data/caderno.db` | Suíte criada exclusivamente com fixtures `tmp_path` e portas efêmeras | **PASS** |
| **Art. III: Fidelidade Tecnológica** | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Vue 3, Vite | Mantida estritamente a stack aprovada sem introdução de novas dependências | **PASS** |
| **Art. IV: Governança SDD** | Fatias pequenas e verificáveis; T01–T10 não iniciadas | Esta fatia especifica os requisitos de T02 e T09 sem alterar status formal das tarefas | **PASS** |
| **Art. V: Resiliência Operacional** | Proteção atômica de banco antes de migrações e chaves ativas | Migração incremental do Alembic protegida pela barreira pré-upgrade da Feature 001 | **PASS** |

## Project Structure

### Documentation (this feature)

```text
specs/003-lixeira-soft-delete/
├── spec.md              # Especificação de requisitos, cenários de aceite e esclarecimentos
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas consolidadas (D1 a D4)
├── data-model.md        # Modelagem de entidades, deleted_at, índices e máquina de estados
├── quickstart.md        # Guia passo a passo de validação executável
├── contracts/           # Contratos de API REST
│   └── trash-api.md
└── checklists/
    └── requirements.md  # Checklist de qualidade (16/16 aprovado)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/                    # Modelos Book e Study com deleted_at e índices
│   │   │   ├── book.py
│   │   │   └── study.py
│   │   ├── schemas/                   # Schemas TrashItemResponse, TrashSummaryResponse
│   │   │   └── trash.py
│   │   ├── routers/
│   │   │   ├── books.py               # POST /trash, POST /restore, DELETE /permanent, filtro active
│   │   │   ├── studies.py             # POST /trash, POST /restore, DELETE /permanent, filtro active
│   │   │   └── trash.py               # GET /api/trash, POST /empty, POST /purge-expired
│   │   └── services/
│   │       └── trash_service.py       # Lógica atômica de descarte, restauração em cascata e purga
│   ├── migrations/
│   │   └── versions/                  # Migração incremental adicionando deleted_at em books e studies
│   └── tests/
│       └── test_trash_soft_delete.py  # Suíte de testes isolados cobrindo os 5 cenários
└── frontend/
    └── src/
        ├── services/api.ts            # Métodos de chamada de lixeira, restauração e expurgo
        ├── types.ts                   # Interfaces TypeScript atualizadas com deleted_at
        ├── views/
        │   ├── BookView.vue           # Botão "Mover para Lixeira" no livro e nos estudos
        │   └── TrashView.vue          # Nova view para gestão e restauração da Lixeira
        ├── components/
        │   ├── TrashConfirmModal.vue  # Diálogo de confirmação de descarte/expurgo
        │   └── Sidebar.vue ou Nav     # Link e badge de contagem de itens na Lixeira
        └── router/
            └── index.ts               # Rota /trash mapeada para TrashView
```

## Complexity Tracking

> Nenhuma violação constitucional identificada. Operações de purga e exclusão definitiva devidamente encapsuladas em transações atômicas com tratamento estrito de chaves estrangeiras.
