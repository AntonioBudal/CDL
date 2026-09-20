# Quickstart & Validation Guide: F10 — Interação Avançada, Movimento e Experiências Visuais

**Feature Branch**: `026-interacao-avancada-movimento`  
**Date**: 2026-09-19  
**Specification**: [spec.md](./spec.md)  
**Research**: [research.md](./research.md)  
**Contracts**: [contracts/kinematics-api.md](./contracts/kinematics-api.md)  
**Data Model**: [data-model.md](./data-model.md)  
**Implementation Status**: **100% Validated & Implemented** (All 27 tasks complete)  

---

## 1. Pré-Requisitos e Ambiente

- **Node.js v20+** e npm no frontend: `caderno-leitura-0.1/frontend`
- **Navegador moderno** com suporte a HTML5 Canvas 2D e Pointer Events
- **Isolamento Absoluto**: A feature opera 100% no cliente frontend, sem chamadas de banco ou gravação no arquivo ativo `backend/data/caderno.db`.

---

## 2. Cenários Executáveis de Validação

### Cenário 1: Cinemática e Amortecimento Específicos por Superclasse
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/superclass-kinematics.test.mjs
  ```
- **Resultado Esperado**:
  - `zero-g` exibe desaceleração inercial prolongada (fricção 0.96) sem encaixe abrupto em grade.
  - `mecanica` aplica atração à grade com passos de 20px e amortecimento elástico rápido.
  - `invisivel` calcula distância de proximidade (140px) e opacidade progressiva das arestas.
  - `dimensional` calcula coeficientes de paralaxe 2.5D proporcionais ao zoom.
  - `monolitica` cessa movimento instantaneamente (fricção 0) sem oscilação elástica.

### Cenário 2: Transição Automática para Aceleração Gráfica em Grafos Densos (≥ 60 nós)
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/graph-acceleration.test.mjs
  ```
- **Resultado Esperado**:
  - Quando a contagem de nós visíveis no Canvas/Mapa for menor que 60, a camada vetorial SVG é mantida.
  - Quando a contagem atinge ou ultrapassa 60 nós, `shouldAccelerate` retorna `true` e a camada acelerada Canvas 2D assume o desenho das arestas.
  - Ao desmontar a view (`onUnmounted`), todos os laços de animação são cancelados sem vazamento de memória.

### Cenário 3: Calibração de Intensidade Paramétrica (0% a 100%)
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/motion-intensity.test.mjs
  ```
- **Resultado Esperado**:
  - Com intensidade em 0.0 (0%), todas as inércias e oscilações são suprimidas (imobilidade estática imediata).
  - Com intensidade em 1.0 (100%), o alcance da inércia e da paralaxe opera em escala máxima.
  - Valores intermediários (ex.: 0.5) escalam proporcionalmente as forças cinemáticas.

### Cenário 4: Respeito a `prefers-reduced-motion` e Modos de Leitura
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/motion-accessibility.test.mjs
  ```
- **Resultado Esperado**:
  - Com `prefers-reduced-motion: reduce` simulado, todas as transições inerciais são imediatamente desligadas.
  - Nas telas de leitura textual e edição de fichamentos (`StudyView.vue`), nenhum loop cinemático de física permanece ativo.

### Cenário 5: Feedback Háptico Visual em Ações Críticas
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/haptic-feedback.test.mjs
  ```
- **Resultado Esperado**:
  - A função `triggerHapticPulse` injeta temporariamente o atributo `data-haptic-pulse="snap"` e remove após 80ms.
  - Ocorre ativação em eventos de snap na grade, conexão de nós no Canvas/Mapa e reordenação na Árvore Hierárquica.

---

## 3. Evidências de Validação Automatizada

| Suíte de Validação | Escopo / Comando | Resultado Registrado | Status |
|---|---|---|---|
| **Cinemática das Superclasses** | `node --test tests/superclass-kinematics.test.mjs` | 6/6 testes aprovados | APROVADO |
| **Aceleração Gráfica Canvas 2D** | `node --test tests/graph-acceleration.test.mjs` | 5/5 testes aprovados (limiar 60 nós) | APROVADO |
| **Feedback Háptico e Intensidade** | `node --test tests/haptic-feedback.test.mjs` | 5/5 testes aprovados (80ms, 0% colapso) | APROVADO |
| **Acessibilidade e Blindagem** | `node --test tests/motion-accessibility.test.mjs` | 6/6 testes aprovados (reduced motion, touch) | APROVADO |
| **Regressão Completa Frontend** | `npm test` (`node --test`) | 223/223 testes aprovados | APROVADO |
| **Compilação de Produção Vite** | `npm run build` (`vue-tsc -b && vite build`) | Compilação limpa em 3.26s (dist/ gerado) | APROVADO |
| **Regressão Completa Backend** | `pytest backend/tests/` | 199 passed, 1 skipped (0 falhas) | APROVADO |
| **Integridade de Dados** | Auditoria de segurança de banco | `backend/data/caderno.db` não modificado | APROVADO |

