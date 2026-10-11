# Implementation Plan: F0.3.5 — Tela Placeholder do Document Intelligence (Digitalizar Caderno)

**Branch**: `069-document-intelligence-placeholder` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/069-document-intelligence-placeholder/spec.md`

---

## Summary

Implementação de uma rota estática dedicada no frontend (`/digitalizar`, com alias `/scan`) que funciona como um placeholder transparente e honesto para a pesquisa de conversão de cadernos manuscritos em estudos estruturados (`document-intelligence/`). A funcionalidade comunica com ênfase a soberania e a privacidade estritamente local (processamento no próprio computador do usuário, sem transmissão de imagens para nuvens externas), apresenta a Matriz Didática de Maturidade com 4 etapas estáticas, exibe ilustração conceitual rotulada e fornece atalhos rápidos para fluxos de estudo operacionais (`/importar` e `/inbox`). O ponto de entrada visual é integrado no Ateliê de Importação (`/importar`) como um card editorial destacado.

---

## Technical Context

**Language/Version**: TypeScript 5.6+ / Vue 3.5+ (Composition API com `<script setup>`)  
**Primary Dependencies**: Vue Router 4.5+, Vite 8.2+ (nenhuma dependência nova adicionada)  
**Storage**: N/A (tela puramente declarativa e estática; sem persistência em banco de dados)  
**Testing**: `node:test` (testes de asserção estrutural, WAI-ARIA e ausência de emojis), `vue-tsc -b`, `vite build`  
**Target Platform**: Navegadores modernos (Desktop e Mobile responsivo), Windows 10/11 local  
**Project Type**: Web SPA (Frontend do Caderno de Leitura)  
**Performance Goals**: Renderização inicial $\le 100$ms, zero requisições HTTP (`network request count === 0`), 100% resiliente offline  
**Constraints**:
- Nenhuma alteração em arquivos de backend Python, banco SQLite, Alembic ou endpoints da API.
- Nenhuma alteração em qualquer arquivo dentro do subprojeto `document-intelligence/`.
- Nenhum upload de arquivo (`input[type="file"]`), acesso a câmera (`getUserMedia`) ou zona de soltura de arquivo.
- Imunidade cromática total aos 10 temas visuais do Leitorum e zero emojis no código ou interface.  
**Scale/Scope**: 1 nova View Vue (`DigitizeNotebookView.vue`), 1 card integrado em `ImportView.vue`, 1 rota em `router/index.ts`, 1 suíte de testes.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Conformidade | Justificativa |
|:---|:---:|:---|
| **I. Proteção Absoluta do Acervo & Privacidade** | **PASS** | A tela é puramente estática e não lê, não consulta e não transmite dados reais do usuário. A ilustração usa texto fictício. |
| **II. Isolamento Estrito de Testes** | **PASS** | Nenhum teste toca no banco de produção `caderno.db`. A suíte de testes executa asserções estáticas no frontend com `node:test`. |
| **III. Fidelidade Arquitetural & Tecnológica** | **PASS** | Respeita a stack Vue 3 + TypeScript estrito, com componentes modulares e sem bibliotecas de terceiros adicionais. |
| **IV. Governança por Spec Kit (SDD)** | **PASS** | Fluxo rigoroso seguindo `specify` ➔ `plan` ➔ `tasks` ➔ `analyze` ➔ `implement`. Status do Roadmap 0.5 inalterado. |
| **V. Resiliência Operacional & Migrações Seguras** | **PASS** | Não há migrações de banco nem alterações de schema. |

*Resultado do Gate*: **100% APROVADO**.

---

## Project Structure

### Documentation (this feature)

```text
specs/069-document-intelligence-placeholder/
├── spec.md              # Especificação de requisitos aprovada
├── checklists/
│   └── requirements.md  # Checklist de qualidade de requisitos validada
├── plan.md              # Este plano de implementação técnica
├── research.md          # Decisões de arquitetura e pesquisa (Fase 0)
├── data-model.md        # Modelos e constantes de apresentação TypeScript (Fase 1)
├── contracts/
│   └── digitize-contract.md # Contrato de UI, acessibilidade e rotas (Fase 1)
├── quickstart.md        # Roteiro de validação rápida e cenários de teste (Fase 1)
└── tasks.md             # Tarefas de implementação (gerado pelo /speckit-tasks)
```

### Source Code Impacted

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── router/
│   │   │   └── index.ts                         # Registro da rota /digitalizar e alias /scan
│   │   ├── views/
│   │   │   ├── DigitizeNotebookView.vue         # Nova view dedicada com a proposta, matriz e saídas
│   │   │   └── ImportView.vue                   # Integração do card editorial de convite à digitalização
│   │   ├── types/
│   │   │   └── digitize.ts                      # Interfaces de apresentação (MaturityStage, ExitShortcut)
│   │   └── style.css                            # Classes utilitárias/semânticas da bancada editorial (se necessário)
│   └── tests/
│       └── feature-069-document-intelligence-placeholder.test.mjs # Suíte de testes unitários da feature
```

---

## Phase 0: Research Summary

Consolidado em [`research.md`](research.md):
1. **Ponto de Entrada**: Card editorial discreto e acolhedor dentro de `ImportView.vue` (`/importar`), mantendo o menu global limpo e sereno.
2. **View Dedicada**: `DigitizeNotebookView.vue` estruturada com seções semânticas (Hero, Manifesto de Privacidade, 4 Etapas de Maturidade, Ilustração Conceitual rotulada e Ações de Saída).
3. **Isolamento**: Zero acoplamento com o subprojeto de pesquisa `document-intelligence/`.
4. **Temas & Acessibilidade**: Consumo estrito de variáveis CSS dos 10 temas visuais do Leitorum e alvo de toque $\ge 44$px.

---

## Phase 1: Design & Contracts Summary

Consolidado em:
- [`data-model.md`](data-model.md): Contrato TypeScript para `MaturityStage`, `DOCUMENT_INTELLIGENCE_STAGES` e `DIGITIZE_EXIT_SHORTCUTS`.
- [`contracts/digitize-contract.md`](contracts/digitize-contract.md): Contratos de roteamento, acessibilidade WAI-ARIA e integração no Hub de Importação.
- [`quickstart.md`](quickstart.md): Guia de validação ponta a ponta com 4 cenários de teste manual e comandos automatizados.

---

## Complexity Tracking

*Nenhuma violação aos princípios constitucionais. Nenhuma exceção necessária.*
