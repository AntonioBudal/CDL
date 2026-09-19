# Implementation Plan: Central de Ajustes com Preview ao Vivo e Organização em Três Seções

**Branch**: `014-central-ajustes-preview` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Especificação funcional aprovada da Feature 014 (T08 do Roadmap 0.3) e clarificações resolvidas (Q1: A, Q2: A, Q3: C).

---

## Summary

Reorganizar a tela de Ajustes (`SettingsView.vue`) em três seções lógicas segmentadas (**Aparência**, **Leitura** e **Sistema**) com suporte acessível a abas (`role="tablist"`), layout desktop de 2 colunas com painel de amostra dinâmico e fixo (*sticky preview*), enriquecimento do preview de livro e abas de estudo (`AppearancePreview.vue`), e implementação da Central Completa de Diagnóstico na aba Sistema (informativo de persistência `localStorage` vs SQLite, verificação de conectividade `/api/health`, medição de armazenamento do navegador, botão de restauração de fábrica com modal de confirmação e integração com `DatabaseBackup.vue`).

---

## Technical Context

**Language/Version**: TypeScript 6.0 (Strict mode) / JavaScript ES2023, Vue 3.5+ (Composition API, `<script setup>`), Python 3.13 (FastAPI/Uvicorn para rota `/api/health` existente).  
**Primary Dependencies**: Vue 3, Vue Router 4, Vite 8.2+, CSS Custom Properties (`tokens.css`, `palettes.css`, `themes.css`, `appearance-advanced.css`).  
**Storage**: Navegador local (`window.localStorage` sob `caderno.aparencia.v2` com migração e purga de `v1`), SQLite local inalterado (`caderno.db` não armazena preferências de cliente).  
**Testing**: `node --test` para testes automatizados unitários e de componentes no frontend; `vue-tsc -b && vite build` para validação de tipagem e empacotamento.  
**Target Platform**: Navegadores modernos (Desktop e Mobile / E-Ink) rodando no Windows local ou acessados via rede privada/Tailscale.  
**Project Type**: Single-Page Application (SPA) frontend servida por backend local unificado.  
**Performance Goals**: Alternância de abas instantânea (< 10ms), reflexo visual de tema/fonte na amostra ao vivo < 50ms, zero FOUC (*Flash of Unstyled Content*) no carregamento da página.  
**Constraints**:
- Envoltório raiz único em `SettingsView.vue` (`<section class="settings-page wrap">`) para garantir transição estável no `<Transition mode="out-in">` de `App.vue`.
- Precedência rigorosa do tema `e-ink` (monocromático, sem destaques cromáticos nem animações).
- Respeito integral a `prefers-reduced-motion`.
- Áreas de toque mínimas de 44px x 44px no mobile.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I (Proteção e Privacidade):** PASS. Nenhuma leitura, listagem ou alteração de registros do acervo pessoal ou banco ativo.
- **Princípio II (Isolamento de Testes):** PASS. Testes frontend não realizam requisições externas nem tocam `caderno.db`; utilizam mocks e stubs de teste.
- **Princípio III (Fidelidade Arquitetural):** PASS. Componentes Vue 3 em TypeScript estrito, CSS custom properties nativas e APIs padronizadas.
- **Princípio IV (Governança SDD):** PASS. Ciclo formal Spec Kit respeitado; tarefas do Roadmap 0.3 preservadas como NÃO INICIADAS até aceite explícito.
- **Princípio V (Resiliência Operacional):** PASS. A feature não introduz alterações de schema nem migrações no banco de dados.

---

## Project Structure

### Documentation (this feature)

```text
specs/014-central-ajustes-preview/
├── spec.md                  # Especificação funcional com clarificações homologadas
├── checklists/
│   └── requirements.md     # Checklist de qualidade da especificação (16/16 PASS)
├── plan.md                  # Este plano de implementação
├── research.md              # Pesquisa técnica e decisões de design (Phase 0)
├── data-model.md            # Entidades, tipos e estados reativos (Phase 1)
├── contracts/
│   └── settings-ui-contract.md # Contratos de abas, health check e reset (Phase 1)
├── quickstart.md            # Roteiro de validação manual e automatizada (Phase 1)
└── tasks.md                 # Decomposição de tarefas atômicas (Phase 2)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   └── SettingsView.vue         # [MODIFY] Organização em 3 abas, layout 2 colunas e central de sistema
│   │   ├── components/
│   │   │   ├── AppearanceControls.vue   # [MODIFY] Segmentação dos controles por aba (Aparência vs Leitura)
│   │   │   ├── AppearancePreview.vue    # [MODIFY] Enriquecimento da amostra (cartão grade/lista, abas e botões)
│   │   │   └── DatabaseBackup.vue       # [PRESERVED] Integrado na aba Sistema
│   │   ├── appearance-advanced.css      # [MODIFY] Estilos para abas segmentadas, sticky preview e diagnóstico
│   │   └── appearance-bootstrap.js      # [MODIFY] Suporte a reset para defaults e purga de chaves obsoletas
│   └── tests/
│       └── settings-central.test.mjs    # [NEW] Testes automatizados da central de ajustes, abas e diagnóstico
```

**Structure Decision**: A implementação concentra-se no módulo frontend (`caderno-leitura-0.1/frontend`), integrando os contratos existentes de `/api/health` e `/api/backup`.

---

## Complexity Tracking

*Nenhuma violação constitucional ou complexidade anômala detectada. Sem novas dependências externas de pacotes.*
