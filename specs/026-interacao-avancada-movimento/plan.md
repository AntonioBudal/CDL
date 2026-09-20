# Implementation Plan: F10 — Interação Avançada, Movimento e Experiências Visuais

**Branch**: `026-interacao-avancada-movimento` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/026-interacao-avancada-movimento/spec.md`

---

## Summary

Amadurecer as 5 Superclasses de interface (Zero-G, Mecânica, Invisível, Dimensional e Monolítica) com modelos de física inercial calibrados, micro-respostas táteis (feedback háptico visual) e uma arquitetura de renderização gráfica híbrida de alta performance. Quando o Canvas de Estudos ou o Mapa de Relações atingir ou superar 60 nós visíveis simultaneamente, as arestas e curvas de relacionamento são automaticamente comutadas para uma camada acelerada em HTML5 Canvas 2D desenhada a 60fps no fundo, mantendo os cartões em DOM/Vue 3 com rica estilização Tailwind e total acessibilidade. A física inercial se estende harmoniosamente à reorganização por arrasto na Árvore Hierárquica (`StudyTreeView`) e aos controles deslizantes, respeitando de forma absoluta `prefers-reduced-motion: reduce`, dispositivos móveis táteis e a imobilidade completa nas telas de leitura textual.

---

## Technical Context

**Language/Version**: TypeScript 5.8 / Node.js 20+ (Frontend Vue 3), Python 3.13 (Backend - zero alterações no backend necessárias para F10)  
**Primary Dependencies**: Vue 3 (Composition API, `<script setup>`), Vite 8, Tailwind CSS, HTML5 Canvas 2D API nativa (zero novas bibliotecas npm)  
**Storage**: `localStorage` (`caderno_superclass`, `caderno_superclass_intensity`, `caderno_graph_acceleration`), zero impacto no banco de dados ativo (`caderno.db` intocado)  
**Testing**: Node Test Runner (`node --test tests/*.test.mjs`) com suítes dedicadas de cinemática, aceleração gráfica, acessibilidade e feedback háptico  
**Target Platform**: Navegador web desktop e mobile (Windows/Chrome/Edge/Firefox/Safari) operando sobre servidor local único  
**Project Type**: Single-Page Application (SPA) modular com arquitetura híbrida (Canvas 2D + DOM)  
**Performance Goals**: 60 fps estáveis durante pan, zoom e arraste de nós; tempo de frame < 16.6ms; comutação para Canvas 2D ao atingir ≥ 60 nós visíveis; zero impacto no carregamento inicial do aplicativo (< 100ms)  
**Constraints**: Respeito obrigatório a `prefers-reduced-motion: reduce`; isolamento e limpeza de contextos gráficos no hook `onUnmounted`; zero aquecimento ou drenagem de bateria em dispositivos móveis; imobilidade absoluta nas visualizações de leitura e fichamento  
**Scale/Scope**: 5 Superclasses com perfis cinemáticos matematicamente calibrados; componentes `StudyCanvasView.vue`, `CanvasConnectionsLayer.vue`, `CanvasAcceleratedLayer.vue`, `StudyMapView.vue`, `StudyTreeView.vue` e `SettingsView.vue`  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Proteção Absoluta do Acervo e Privacidade de Dados**: Nenhum dado pessoal, texto de fichamento ou registro do acervo é lido, exposto ou transmitido para serviços externos.
- [x] **II. Isolamento Estrito de Testes e Operações Locais**: O banco ativo local (`backend/data/caderno.db`) não é acessado nem modificado. Todos os testes são herméticos no frontend.
- [x] **III. Fidelidade Arquitetural e Tecnológica**: Uso rigoroso de Vue 3, TypeScript estrito, Vite e HTML5 Canvas 2D nativo, sem bibliotecas pesadas de terceiros ou runtime de IA.
- [x] **IV. Governança por Especificação Delimitada (Spec-Driven Development)**: Segue estritamente o ciclo formal do Spec Kit (`specify` → `plan` → `tasks` → `analyze` → `implement`).
- [x] **V. Resiliência Operacional, Transações e Migrações Seguras**: Zero alterações de schema ou DDL no banco de dados; nenhuma migração Alembic necessária.

---

## Project Structure

### Documentation (this feature)

```text
specs/026-interacao-avancada-movimento/
├── spec.md              # Especificação formal com requisitos refinados
├── plan.md              # Plano de implementação técnica (este arquivo)
├── research.md          # Pesquisa técnica e justificativas arquiteturais (Phase 0)
├── data-model.md        # Modelo de dados e tipos TypeScript de cinemática (Phase 1)
├── quickstart.md        # Guia executável de validação de cenários (Phase 1)
├── contracts/           # Contratos de interfaces e tokens cinemáticos (Phase 1)
│   └── kinematics-api.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Tarefas atômicas (geradas na fase /speckit-tasks)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
└── frontend/
    ├── src/
    │   ├── composables/
    │   │   ├── useSuperclassPhysics.ts      # [NEW] Motor de cinemática inercial e interpolação
    │   │   ├── useCanvasConnections.ts      # [MODIFY] Integração de limiar de aceleração (60 nós)
    │   │   ├── useMagneticHover.ts          # [MODIFY] Calibração de amortecimento por superclasse
    │   │   └── useStudyHierarchy.ts         # [MODIFY] Micro-resposta de snap na árvore hierárquica
    │   ├── components/
    │   │   └── views/
    │   │       ├── canvas/
    │   │       │   ├── CanvasAcceleratedLayer.vue  # [NEW] Camada acelerada Canvas 2D para conexões densas
    │   │       │   └── CanvasConnectionsLayer.vue  # [MODIFY] Suporte a comutação híbrida com SVG
    │   │       ├── StudyCanvasView.vue             # [MODIFY] Acoplamento do motor acelerado e física
    │   │       ├── StudyMapView.vue                # [MODIFY] Aplicação de cinemática e camada acelerada
    │   │       └── StudyTreeView.vue               # [MODIFY] Feedback háptico visual no drag & drop
    │   └── styles/
    │       └── superclasses/
    │           └── physics.css              # [NEW] Tokens CSS cinemáticos e animação de pulso háptico
    └── tests/
        ├── superclass-kinematics.test.mjs   # [NEW] Testes de constantes cinemáticas das 5 superclasses
        ├── graph-acceleration.test.mjs      # [NEW] Testes de comutação automática a partir de 60 nós
        ├── motion-intensity.test.mjs        # [NEW] Testes de escalonamento de intensidade (0% a 100%)
        ├── motion-accessibility.test.mjs    # [NEW] Testes de prefers-reduced-motion e blindagem de leitura
        └── haptic-feedback.test.mjs         # [NEW] Testes de injeção temporária de feedback háptico visual
```

---

## Complexity Tracking

> *Nenhuma violação constitucional detectada. A solução adota a API nativa de HTML5 Canvas 2D sem adicionar pacotes npm externos.*

| Item | Decisão Adotada | Alternativa Rejeitada e Motivo |
|---|---|---|
| Motor de Aceleração | Camada híbrida Canvas 2D nativa no fundo | Pixi.js/Three.js rejeitados pelo aumento substancial do bundle e risco de perda de contexto WebGL. |
| Simulação de Física | Composable analítico leve (`useSuperclassPhysics`) | Motores de física completos (Matter.js) rejeitados por complexidade desnecessária para nós 2D. |
