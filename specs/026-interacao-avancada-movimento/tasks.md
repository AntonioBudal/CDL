# Tasks: F10 — Interação Avançada, Movimento e Experiências Visuais

**Input**: Design documents from `specs/026-interacao-avancada-movimento/`  
**Status**: Ready for Implementation  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura base de estilos, tokens CSS e tipagens TypeScript para física e aceleração gráfica.

- [X] T001 Criar arquivo de tokens CSS e animações de feedback háptico em caderno-leitura-0.1/frontend/src/styles/superclasses/physics.css
- [X] T002 Exportar definições de tipos TypeScript para KinematicProfile, AccelerationEngineState e MotionState em caderno-leitura-0.1/frontend/src/types.ts
- [X] T003 [P] Configurar constantes canônicas SUPERCLASS_KINEMATIC_PROFILES e matriz de física em caderno-leitura-0.1/frontend/src/composables/useSuperclassPhysics.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Motor cinemático desacoplado e testes de fundação necessários para todas as histórias de usuário.

**CRITICAL**: Nenhuma história de usuário pode ser finalizada antes que o motor cinemático e seus testes básicos estejam operacionais.

- [X] T004 Implementar composable central useSuperclassPhysics.ts com cálculos de amortecimento, molas e detecção de ambiente em caderno-leitura-0.1/frontend/src/composables/useSuperclassPhysics.ts
- [X] T005 [P] Criar testes unitários para perfis cinemáticos das 5 superclasses em caderno-leitura-0.1/frontend/tests/superclass-kinematics.test.mjs
- [X] T006 [P] Criar testes unitários para cálculo do limiar de aceleração gráfica em caderno-leitura-0.1/frontend/tests/graph-acceleration.test.mjs

**Checkpoint**: Motor de física cinemática fundamentado e testado de forma isolada.

---

## Phase 3: User Story 1 - Cinemática e Dinâmica Física Diferenciada das Superclasses no Canvas e Mapa (Priority: P1) [MVP]

**Goal**: Conferir respostas cinemáticas nitidamente distintas às 5 Superclasses (Zero-G, Mecânica, Invisível, Dimensional e Monolítica) no Canvas e no Mapa de Estudos.

**Independent Test**: Alternar entre as 5 superclasses na Central de Aparência e manipular nós no Canvas e Mapa, constatando inércia sem fricção (Zero-G), snap em grade com amortecimento rápido (Mecânica), quiescência em repouso (Invisível), paralaxe 2.5D (Dimensional) e solidez brutalista imediata (Monolítica).

### Implementation for User Story 1

- [X] T007 [P] [US1] Integrar amortecimento e curvas inerciais por superclasse no arraste de nós e pan do Canvas em caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue
- [X] T008 [P] [US1] Integrar parâmetros cinemáticos no arraste e flutuação de nós no Mapa de Estudos em caderno-leitura-0.1/frontend/src/components/views/StudyMapView.vue
- [X] T009 [US1] Implementar atração de grade com amortecimento para Mecânica e flutuação contínua para Zero-G em caderno-leitura-0.1/frontend/src/composables/useSuperclassPhysics.ts
- [X] T010 [US1] Implementar efeito de paralaxe 2.5D para Dimensional e revelação por proximidade para Invisível em caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasConnectionsLayer.vue

**Checkpoint**: MVP concluído. O Canvas e o Mapa reagem com as características físicas e táteis únicas de cada Superclasse.

---

## Phase 4: User Story 2 - Renderização Gráfica Acelerada para Grafos Densos (Priority: P2)

**Goal**: Assegurar fluidez a 60fps no Canvas e Mapa em acervos densos através de comutação automática para camada acelerada Canvas 2D a partir de 60 nós visíveis.

**Independent Test**: Carregar um grafo com mais de 60 nós visíveis, verificar a ativação transparente da camada Canvas 2D desenhando arestas em lote sem engasgos de interface e constatar a liberação de recursos ao sair da visualização.

### Implementation for User Story 2

- [X] T011 [US2] Criar componente acelerado CanvasAcceleratedLayer.vue utilizando HTML5 Canvas 2D para desenho de arestas em lote em caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasAcceleratedLayer.vue
- [X] T012 [US2] Integrar lógica de comutação automática entre camada SVG e Canvas 2D acelerado ao atingir limiar de 60 nós em caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue
- [X] T013 [US2] Integrar suporte à camada acelerada de arestas e conexões em caderno-leitura-0.1/frontend/src/components/views/StudyMapView.vue
- [X] T014 [P] [US2] Implementar cancelamento limpo de requestAnimationFrame e desalocação no hook onUnmounted em caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasAcceleratedLayer.vue

**Checkpoint**: Grafos volumosos mantêm taxa de quadros a 60fps constantes sem sobrecarregar o DOM.

---

## Phase 5: User Story 3 - Calibração Paramétrica de Intensidade e Feedback Háptico Visual (Priority: P3)

**Goal**: Permitir calibrar a intensidade de 0% a 100% com colapso estático em 0%, e fornecer micro-respostas táteis visuais em conexões, ancoragens, na Árvore Hierárquica e em sliders.

**Independent Test**: Variar o controle de intensidade da Superclasse observando o escalonamento proporcional das forças; verificar micro-pulsos táteis (80ms) ao acoplar nós, mover nós na árvore ou manipular sliders.

### Implementation for User Story 3

- [X] T015 [P] [US3] Implementar utilitário triggerHapticPulse para injeção temporária do atributo data-haptic-pulse em caderno-leitura-0.1/frontend/src/composables/useSuperclassPhysics.ts
- [X] T016 [US3] Conectar o multiplicador de intensidade caderno_superclass_intensity aos cálculos cinemáticos em caderno-leitura-0.1/frontend/src/composables/useSuperclassPhysics.ts
- [X] T017 [US3] Adicionar feedback háptico visual na ancoragem e conexão de nós em caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasNode.vue
- [X] T018 [US3] Estender micro-respostas de snap à reorganização por arrasto de nós na Árvore Hierárquica em caderno-leitura-0.1/frontend/src/components/views/StudyTreeView.vue
- [X] T019 [US3] Integrar micro-respostas táteis na manipulação de controles deslizantes em caderno-leitura-0.1/frontend/src/views/SettingsView.vue
- [X] T020 [P] [US3] Criar testes automatizados de intensidade e feedback háptico em caderno-leitura-0.1/frontend/tests/haptic-feedback.test.mjs

**Checkpoint**: Ajuste de intensidade e micro-respostas táteis integrados harmoniosamente em todo o ecossistema.

---

## Phase 6: User Story 4 - Respeito Estrito a Redução de Movimento, Dispositivos Móveis e Eficiência Energética (Priority: P4)

**Goal**: Garantir conformidade com acessibilidade vestibular (prefers-reduced-motion), delegação ao touch nativo em smartphones e imobilidade estática durante a leitura de estudos.

**Independent Test**: Habilitar redução de movimento no sistema e verificar a desativação instantânea de qualquer inércia e mola; emular touch screen e constatar a ausência de loops contínuos de física; acessar a tela de leitura de estudo e verificar ambiente 100% estático.

### Implementation for User Story 4

- [X] T021 [US4] Implementar detecção reativa e desativação instantânea de inércia e oscilação sob prefers-reduced-motion em caderno-leitura-0.1/frontend/src/composables/useSuperclassPhysics.ts
- [X] T022 [US4] Delegar pan e scroll ao gesto tátil nativo em dispositivos móveis evitando simulações contínuas em JS em caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue
- [X] T023 [US4] Assegurar imobilidade absoluta e ausência de processamento cinemático nas telas de leitura e edição em caderno-leitura-0.1/frontend/src/views/StudyView.vue
- [X] T024 [P] [US4] Criar testes automatizados de acessibilidade e blindagem de leitura em caderno-leitura-0.1/frontend/tests/motion-accessibility.test.mjs

**Checkpoint**: Acessibilidade e ergonomia móvel homologadas com máxima segurança para o leitor.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validação de regressão completa, compilação de produção e homologação final.

- [X] T025 [P] Executar suíte completa de testes de regressão do backend em caderno-leitura-0.1/backend/tests/
- [X] T026 [P] Executar suíte de testes de regressão do frontend e compilação de produção Vite em caderno-leitura-0.1/frontend/
- [X] T027 Atualizar guia de validação executável e registrar evidências finais em specs/026-interacao-avancada-movimento/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (T001-T003)
        │
        ▼
Phase 2: Foundational (T004-T006)
        │
        ├────────────────────────────────┐
        ▼                                ▼
Phase 3: User Story 1 (T007-T010)  [MVP]  (Cinemática das 5 Superclasses no Canvas e Mapa)
        │
        ▼
Phase 4: User Story 2 (T011-T014)         (Camada Acelerada Canvas 2D para ≥ 60 nós)
        │
        ▼
Phase 5: User Story 3 (T015-T020)         (Calibração de Intensidade e Feedback Háptico)
        │
        ▼
Phase 6: User Story 4 (T021-T024)         (Acessibilidade Reduced Motion e Mobile)
        │
        ▼
Phase 7: Polish (T025-T027)               (Regressão completa, build Vite e validação)
```

### Parallel Opportunities

- **Phase 1**: T001, T002 e T003 podem ser desenvolvidos em paralelo.
- **Phase 2**: T005 e T006 (testes unitários) podem rodar em paralelo após a assinatura de T004.
- **Phase 3**: T007 e T008 podem ser executados em paralelo.
- **Phase 4**: T011 e T014 podem ser desenvolvidos em paralelo com T012 e T013.
- **Phase 5**: T015 e T020 podem rodar em paralelo com as integrações T017, T018 e T019.
- **Phase 6**: T021 e T024 podem ser executados em paralelo.
- **Phase 7**: T025 (regressão backend) e T026 (regressão frontend + build Vite) podem rodar em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Setup (T001-T003) e Foundational (T004-T006).
2. Implementar User Story 1 (T007-T010).
3. **Validar MVP**: O leitor experimenta respostas cinemáticas vivas e diferenciadas para cada uma das 5 Superclasses no Canvas e Mapa de Estudos.

### Incremental Delivery
- US2 adiciona o motor híbrido Canvas 2D para manter 60fps em acervos volumosos (≥ 60 nós).
- US3 expande a calibração de intensidade (0% a 100%) e o feedback háptico visual para a Árvore de Estudos e sliders.
- US4 blinda a acessibilidade (`prefers-reduced-motion`), dispositivos móveis táteis e a imobilidade de leitura.
- Phase 7 garante 100% de integridade com zero regressões no sistema.
