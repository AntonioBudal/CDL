# Implementation Plan: Lixeira — Arquivo de Salvaguarda e Segurança

**Branch**: `073-lixeira-arquivo-salvaguarda` | **Date**: 2026-10-11 | **Spec**: [specs/073-lixeira-arquivo-salvaguarda/spec.md](spec.md)

**Input**: Feature specification from `/specs/073-lixeira-arquivo-salvaguarda/spec.md`

## Summary

Implementar a reformulação completa da visualização e gestão da lixeira (`/lixeira`), transformando-a em um cofre de salvaguarda e custódia temporária. A solução introduz cartões visuais para livros e estudos com indicador de retenção dos 30 dias e barra de progresso temporal (com destaque de urgência para $\le 5$ dias restantes), seleção individual e múltipla por caixas de seleção, barra flutuante de ações em lote para restauração e exclusão em massa, diálogo modal reforçado de segurança com semântica de alerta (`role="alertdialog"`, foco retido no botão cancelar e suporte a Escape) para esvaziamento e exclusões irreversíveis, além de animação suave de saída na restauração (180ms) e resolução transparente de estudos cujo livro de origem também estava descartado.

## Technical Context

**Language/Version**: Python 3.13 (Backend) / TypeScript 5+, Vue 3.5+ (Frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Vite, Lucide Vue Next, Vue Router
**Storage**: SQLite 3 local (modo WAL, PRAGMA foreign_keys = ON)
**Testing**: Node.js test runner (`node --test`), `pytest`
**Target Platform**: Windows 11 Desktop e navegadores modernos (Desktop e Mobile)
**Project Type**: Web Application monousuário local servida via `iniciar.py`
**Performance Goals**: Animações fluidas a 60 FPS (transição de 180ms na restauração e 200ms na barra flutuante), exibição da barra de lote em $< 300$ms
**Constraints**: Zero emojis na interface, conformidade WAI-ARIA (alvos $\ge 44 \times 44$px, suporte a teclado Tab/Espaço/Enter/Escape), isolamento total do banco ativo `caderno.db` nos testes
**Scale/Scope**: Gestão do acervo descartado (livros e estudos) em retenção de 30 dias

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Regra / Exigência | Conformidade | Justificativa |
|---|---|---|---|
| **Artigo I** | Proteção Absoluta do Acervo e Privacidade | **PASS** | Nenhuma exclusão acidental; o modal de alerta impede destruição involuntária; nenhum dado real é exposto em logs ou prompts |
| **Artigo II** | Isolamento Estrito de Testes | **PASS** | Todas as validações automatizadas utilizam mocks ou bancos SQLite descartáveis em memória/`tmp_path` |
| **Artigo III** | Fidelidade Arquitetural | **PASS** | Vue 3 Composition API com `<script setup>`, TypeScript estrito, componentes reutilizáveis e tokens semânticos de CSS |
| **Artigo IV** | Governança por Spec Kit | **PASS** | Ciclo formal de especificação, pesquisa, modelo de dados, contratos, quickstart e plano completo |
| **Artigo V** | Resiliência Operacional e Migrações Seguras | **PASS** | Nenhuma alteração de schema requerida; endpoints e contratos de banco permanecem 100% preservados e estáveis |

## Project Structure

### Documentation (this feature)

```text
specs/073-lixeira-arquivo-salvaguarda/
├── plan.md              # Este plano de implementação
├── research.md          # Decisões de arquitetura e pesquisa (Fase 0)
├── data-model.md        # Entidades, tipos e máquinas de estado (Fase 1)
├── quickstart.md        # Guia de validação automatizada e manual (Fase 1)
├── contracts/           # Contratos de componentes e interfaces (Fase 1)
│   └── trash-contracts.md
├── checklists/
│   └── requirements.md  # Checklist de qualidade da especificação
└── tasks.md             # Tarefas atômicas (geradas via /speckit-tasks)
```

### Source Code (affected paths)

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── TrashConfirmModal.vue   # Aprimoramento com role="alertdialog" e tokens semânticos
│   │   ├── views/
│   │   │   └── TrashView.vue           # Redesenho completo com barra flutuante, retenção visual e animação
│   │   └── types.ts                    # Tipos auxiliares de seleção e retenção
│   └── tests/
│       └── feature-073-lixeira-salvaguarda.test.mjs  # Nova suíte unitária da feature
```

**Structure Decision**: Aplicação Web cliente-servidor monousuário, focando as melhorias nos componentes do frontend e suíte de testes dedicada, mantendo os endpoints REST estáveis.

## Complexity Tracking

*Nenhuma violação constitucional detectada. Sem padrões complexos desnecessários.*
