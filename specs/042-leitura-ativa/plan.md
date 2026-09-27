# Implementation Plan: F0.6.3 — Leitura Ativa

**Branch**: `042-leitura-ativa` | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/042-leitura-ativa/spec.md`

---

## Summary

Implementação da experiência de **Leitura Ativa** (*active recall*) integrada diretamente ao fluxo de leitura dos fichamentos no leitor de estudos, **sem criar uma tela paralela de flashcards**. 

A solução utiliza um estado efêmero e reativo no frontend (`useActiveReadingSession.ts`), acionado por uma nova barra de ferramentas (`ActiveReadingBar.vue`), operando sobre os trechos já identificados de oclusão (`hidden`) e perguntas (`question`) da feature F0.6.2. Permite mascaramento em lote ("Ocultar todos" / "Revelar todos"), revelação pontual durante a leitura, navegação sequencial com atalhos de teclado e contador de progresso, com zero impacto sobre o texto Markdown salvo e compatibilidade irrestrita com estudos compartilhados em modo somente leitura.

---

## Technical Context

**Language/Version**: Python 3.13 de 64 bits (backend) / TypeScript 5.6+ em modo estrito & Vue 3.5+ (frontend)  
**Primary Dependencies**: Vue 3 (Composition API, `<script setup>`), Vite 8, `markdown-it`, Uvicorn, FastAPI, SQLAlchemy 2.0  
**Storage**: SQLite local (modo WAL). Zero mutações de persistência durante a sessão de leitura ativa; reutilização dos registros relacionais da tabela `study_highlights`.  
**Testing**: `node --test` para testes unitários de frontend (`npm test`), `pytest` para integridade geral do backend  
**Target Platform**: Windows local (PowerShell, CRLF/LF) atendendo navegadores modernos no Desktop e dispositivos móveis (`<= 768px`)  
**Project Type**: Aplicação Web SPA (Vue 3) servida por API REST FastAPI  
**Performance Goals**: Alternância de revelação em menos de 10ms; ativação do modo ativo e rolagem de trecho em menos de 50ms; zero recriação destrutiva de nós DOM.  
**Constraints**: Zero emojis informais em `src/`; alvos de toque $\ge 44 \times 44\text{px}$; aderência aos 10 temas visuais e tema E-Ink; preservação estrita do Markdown puro.  
**Scale/Scope**: Fichamentos extensos com dezenas de parágrafos e múltiplos trechos interativos nas 4 seções de análise.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio Constitucional | Avaliação | Status |
| :--- | :--- | :---: |
| **I. Proteção do Acervo e Privacidade** | Nenhuma informação do acervo real é exposta. O texto Markdown original permanece 100% puro e sem mutações no banco. | ✅ APROVADO |
| **II. Isolamento Estrito de Testes** | Testes de backend utilizam bancos temporários `tmp_path`. Testes de frontend utilizam suites unitárias puras via `node --test`. | ✅ APROVADO |
| **III. Fidelidade Arquitetural** | Stack mantida rigorosamente: Vue 3 + TypeScript estrito + Vite + FastAPI + SQLite. | ✅ APROVADO |
| **IV. Governança por SDD** | Segue estritamente o ciclo Spec Kit (`speckit-specify` → `speckit-plan` → `speckit-tasks` → `speckit-implement`). | ✅ APROVADO |
| **V. Resiliência Operacional** | Estado da sessão de estudo é efêmero na memória do navegador, eliminando concorrência de escrita, locks no SQLite e conflitos de rede. | ✅ APROVADO |

---

## Project Structure

### Documentation (this feature)

```text
specs/042-leitura-ativa/
├── spec.md                  # Especificação funcional refinada
├── checklists/
│   └── requirements.md      # Checklist de validação de qualidade (100% aprovado)
├── plan.md                  # Este plano técnico de arquitetura
├── research.md              # Pesquisa técnica e justificativas de arquitetura
├── data-model.md            # Entidades de dados em memória e máquina de estados
├── contracts/
│   └── active-reading-contract.md # Contratos do componente ActiveReadingBar e utilitários
└── quickstart.md            # Roteiro de validação automatizada e cenários manuais
```

### Source Code (repository layout)

```text
caderno-leitura-0.1/
└── frontend/
    └── src/
        ├── types.ts                           # Tipos ActiveStudyNode, ActiveReadingSessionState
        ├── composables/
        │   └── useActiveReadingSession.ts     # Composable reativo de sessão de estudo ativo
        ├── utils/
        │   └── highlightRenderer.ts           # Métodos setHighlightsRevealedState e scrollAndFocusHighlight
        ├── components/
        │   ├── ActiveReadingBar.vue           # Barra contextual com progresso, lote e navegação
        │   ├── ReaderTools.vue                # Acionador de Leitura Ativa com badge
        │   ├── StudyTabs.vue                  # Propagação e sincronização com o container da aba ativa
        │   └── MarkdownContent.vue            # Suporte estilístico aos trechos interativos
        └── views/
            └── StudyView.vue                  # Integração da barra no leitor e controle de teclado
```

---

## Complexity Tracking

*Nenhuma violação aos princípios constitucionais ou padrões arquiteturais foi identificada. O design mantém o texto Markdown original intocado e adota uma camada leve de controle na memória do navegador para garantir latência zero e experiência inclusiva para convidados.*
