# Implementation Plan: Exportação de Anotações em TXT e Markdown

**Branch**: `015-exportacao-anotacoes` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/015-exportacao-anotacoes/spec.md` (T07 do Roadmap 0.3) com clarificações homologadas (Q1: A, Q2: A, Q3: A).

---

## Summary

Implementar a exportação de anotações e estudos de livros em arquivos formatados Markdown (`.md`) com Frontmatter YAML e Texto Puro (`.txt`) com divisores legíveis em UTF-8 universal. A exportação é gerada no backend (`export_service.py`), exposta via rotas REST `GET /api/books/{id}/export` e `GET /api/studies/{id}/export`, excluindo rigorosamente itens da lixeira (`deleted_at IS NULL`), e consumida no frontend através de um modal acessível (`ExportModal.vue`) acionável na tela do Livro (`BookView.vue`) e na tela do Estudo (`StudyView.vue`).

---

## Technical Context

**Language/Version**: Python 3.13 (FastAPI, SQLAlchemy 2.0) no backend; TypeScript 6.0 (Strict mode), Vue 3 (Composition API, `<script setup>`) no frontend.  
**Primary Dependencies**: FastAPI (`Response`, streaming UTF-8), SQLAlchemy ORM, Pydantic v2; Vue 3, Vue Router 4, Vite 8.  
**Storage**: SQLite local (leitura de tabelas existentes `books`, `chapters`, `studies`, `categories`), zero alteração de schema ou migrações DDL.  
**Testing**: `pytest` com banco SQLite descartável em `tmp_path` no backend (`test_export.py`); `node --test` no frontend (`export.test.mjs`).  
**Target Platform**: Windows local (host) e navegadores desktop e móveis (via rede local / Tailscale).  
**Project Type**: Web Application com API REST e SPA frontend.  
**Performance Goals**: Geração e download do arquivo em menos de 1 segundo para obras com até 50 estudos; baixo consumo de memória via montagem de texto em streaming/memória transitória.  
**Constraints**:
- UTF-8 universal sem corrupção de acentuação (*mojibake*).
- Nomes de arquivo sanitizados contra caracteres proibidos do Windows (`< > : " / \ | ? *`).
- Exclusão rigorosa de itens da lixeira (`deleted_at IS NOT NULL`).
- Acessibilidade do modal WAI-ARIA com navegação por teclado e foco inicial.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I (Privacidade e Proteção de Dados):** PASS. O acervo ativo do usuário não é exposto a terceiros; os arquivos são baixados localmente no dispositivo do usuário pelo navegador.
- **Princípio II (Isolamento de Testes):** PASS. Testes automatizados executam exclusivamente em bancos temporários descartáveis (`tmp_path`).
- **Princípio III (Fidelidade Arquitetural):** PASS. FastAPI, SQLAlchemy 2 e Vue 3 nativo.
- **Princípio IV (Governança SDD):** PASS. Ciclo formal Spec Kit respeitado; tarefas do Roadmap 0.3 continuam registradas formalmente como NÃO INICIADAS até homologação completa.
- **Princípio V (Resiliência Operacional):** PASS. A feature não realiza alterações estruturais no banco de dados ativo.

---

## Project Structure

### Documentation (this feature)

```text
specs/015-exportacao-anotacoes/
├── spec.md                  # Especificação funcional com clarificações resolvidas
├── checklists/
│   └── requirements.md     # Checklist de qualidade (16/16 PASS)
├── plan.md                  # Este plano de implementação
├── research.md              # Pesquisa técnica e decisões de arquitetura (Phase 0)
├── data-model.md            # Modelos de dados e schemas (Phase 1)
├── contracts/
│   └── export-api-contract.md # Contratos de endpoints e parâmetros (Phase 1)
├── quickstart.md            # Guia de validação automatizada e manual (Phase 1)
└── tasks.md                 # Decomposição em tarefas atômicas (Phase 2)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── schemas/
│   │   │   └── export.py              # [NEW] Schemas de opções e parâmetros de exportação
│   │   ├── services/
│   │   │   └── export_service.py       # [NEW] Lógica de montagem Markdown/TXT e sanitização de nomes
│   │   └── routers/
│   │       ├── books.py               # [MODIFY] Endpoint GET /books/{id}/export
│   │       └── studies.py             # [MODIFY] Endpoint GET /studies/{id}/export
│   └── tests/
│       └── test_export.py             # [NEW] Testes de integração isolados com tmp_path
└── frontend/
    ├── src/
    │   ├── types.ts                   # [MODIFY] Tipos TypeScript para opções de exportação
    │   ├── services/
    │   │   └── api.ts                 # [MODIFY] Métodos exportBook e exportStudy
    │   ├── components/
    │   │   └── ExportModal.vue        # [NEW] Modal de seleção de formato e seções
    │   └── views/
    │       ├── BookView.vue           # [MODIFY] Ação "Exportar anotações" no cabeçalho do livro
    │       └── StudyView.vue          # [MODIFY] Ação "Exportar estudo" no cabeçalho do estudo
    └── tests/
        └── export.test.mjs            # [NEW] Testes unitários para download e opções no frontend
```

**Structure Decision**: Funcionalidade distribuída entre serviço/rotas no backend e modal/ações nas views do frontend.

---

## Complexity Tracking

*Nenhuma violação constitucional ou complexidade anômala detectada. Sem novas dependências externas de pacotes.*
