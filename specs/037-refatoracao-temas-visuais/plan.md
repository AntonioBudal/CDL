# Implementation Plan: F09.5 — Refatoração de Temas, Persistência e Correções Visuais

**Branch**: `037-refatoracao-temas-visuais` | **Date**: 2026-09-26 | **Spec**: [specs/037-refatoracao-temas-visuais/spec.md](file:///c:/Users/User/caderno/specs/037-refatoracao-temas-visuais/spec.md)

**Input**: Feature specification from `specs/037-refatoracao-temas-visuais/spec.md`

---

## Summary

Esta feature consolida a simplificação e reestruturação estética do sistema visual do Leitorum, resolvendo um bug crítico de persistência de tema (F5 e transições de rotas revertiam para o padrão) e sanando distorções de escala em elementos vetoriais e falhas de contraste em componentes fundamentais da interface. O catálogo de temas é consolidado em exatamente 10 opções (5 minimalistas de baixo contraste adicionadas, 5 clássicas com nomes simplificados preservadas e 5 distrativas expurgadas), com leitura síncrona no bootstrap e aplicação de regras estritas de contenção e contraste dinâmico.

---

## Technical Context

**Language/Version**: TypeScript 5.8+ / Vue 3.5+ (Composition API, `<script setup>`), CSS3 Moderno (Custom Properties, `:root[data-theme]`), Python 3.13 (Backend).

**Primary Dependencies**: Vue 3, Vue Router 4, Lucide Vue Next, Tailwind CSS / Vanilla CSS Variables, FastAPI (Backend).

**Storage**: `localStorage` no navegador (`caderno.aparencia.v2` e `caderno_user_preferences`), SQLite 3 no backend (tabela `user_preferences`).

**Testing**: Node.js test runner (`npm test` cobrindo `visual_system.test.mjs`, contratos de tokens e testes de componentes) e pytest para integridade do backend.

**Target Platform**: Navegadores modernos (Desktop e Mobile) atendidos pelo processo local único do Leitorum via Windows/PowerShell e LAN/Tailscale.

**Project Type**: Web Application (Single-Page Application Vue 3 servida por backend FastAPI).

**Performance Goals**: Leitura e aplicação de tema em 0ms no boot (sem FOUC ou renderização intermediária no tema errado); zero travamentos em transições de rotas.

**Constraints**: Preservação estrita das regras visuais anti-emoji (`visual_system.test.mjs`), WCAG 2.1 nível AA para taxa de contraste em textos (mínimo 4.5:1), alvos de toque mínimos de 44x44px em botões móveis.

**Scale/Scope**: 10 temas canônicos calibrados; 5 componentes Vue modificados (`ExportModal.vue`, `SharedStudiesList.vue`, `StudyView.vue`, `GroupSection.vue`, `StudyStatusBadge.vue`); 2 módulos de configuração visual (`palettes.css`, `appearance-bootstrap.js`).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Princípio I (Privacidade e Preservação de Dados)**: A feature atua no sistema de temas e layout visual. Nenhuma leitura ou transmissão de dados do acervo é realizada.
- [x] **Princípio II (Isolamento de Testes)**: Todos os testes automatizados utilizam ambientes isolados e bancos descartáveis em `tmp_path`, sem tocar no banco ativo.
- [x] **Princípio III (Fidelidade Tecnológica)**: Utiliza Vue 3 Composition API com TypeScript estrito, CSS Custom Properties e arquitetura desacoplada.
- [x] **Princípio IV (Governança por Especificação)**: Segue estritamente o ciclo Spec Kit integrado ao Antigravity (`agy`).
- [x] **Princípio V (Resiliência Operacional)**: O tema é blindado por migração automática caso o usuário possua um tema excluído salvo no navegador, garantindo que a aplicação nunca abra em tela branca ou quebrada.

---

## Project Structure

### Documentation (this feature)

```text
specs/037-refatoracao-temas-visuais/
├── spec.md                     # Especificação formal da feature
├── checklists/
│   └── requirements.md         # Checklist de qualidade de requisitos (100%)
├── research.md                 # Decisões técnicas e diagnósticos de persistência/SVG
├── data-model.md               # Modelagem dos 10 temas e mapa de migração
├── quickstart.md               # Roteiro de validação prática e testes
├── contracts/
│   ├── theme-tokens.json       # JSON Schema dos tokens CSS de tema
│   └── visual-corrections-contract.md # Contratos dimensionais e de contraste
├── plan.md                     # Este documento técnico
└── tasks.md                    # Próxima fase: decomposição atômica de tarefas
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── frontend/
│   ├── index.html                               # Script de bootstrap no <head>
│   ├── src/
│   │   ├── appearance-bootstrap.js              # Catálogo de temas e normalizador síncrono
│   │   ├── appearance.d.ts                      # Tipos de temas
│   │   ├── palettes.css                         # Variáveis e paletas dos 10 temas canônicos
│   │   ├── main.ts                              # Leitura síncrona antes de app.mount()
│   │   ├── composables/
│   │   │   └── usePreferences.ts                # Store de preferências unificada sem override genérico
│   │   ├── components/
│   │   │   ├── ExportModal.vue                  # Contenção de SVGs e herança de cores
│   │   │   ├── StudyStatusBadge.vue             # Contraste adaptativo de status e menu
│   │   │   ├── library/
│   │   │   │   └── SharedStudiesList.vue        # Contenção de 120px no empty state
│   │   │   └── views/
│   │   │       └── GroupSection.vue             # Contraste dinâmico no cabeçalho colapsável
│   │   └── views/
│   │       ├── StudyView.vue                    # Botão Compartilhar com flex, 1.2em e nowrap
│   │       └── SettingsView.vue                 # Seletor com os 10 temas simplificados
│   └── tests/
│       └── theme_refactor.test.mjs              # Testes automatizados da Feature 9.5
└── backend/
    └── app/
        └── models/user_preferences.py           # Compatibilidade de persistência
```

---

## Architecture & Execution Plan

### Fase 1: Arquitetura de Persistência Síncrona (US1)
1. **Bootstrap Precoce**: Ajustar `appearance-bootstrap.js` para mapear imediatamente temas legados (`porcelana` -> `papel-fosco`, etc.) e carregar `data-theme` no `document.documentElement` antes de qualquer execução de framework.
2. **Hidratação do Vue**: Em `main.ts`, ler o tema ativo de `caderno.aparencia.v2` e inicializar `usePreferences().loadFromLocal()` de forma síncrona antes de chamar `app.mount('#app')`.
3. **Desativação de Sobrescrita Genérica**: Em `usePreferences.ts`, eliminar a atribuição arbitrária de `theme_mode` genérico (`dark`/`light`) sobre `data-theme`.

### Fase 2: Catálogo de 10 Temas e Paletas Minimalistas (US2)
1. **Limpeza de Temas Obsoletos**: Remover as classes e seletores de `porcelana`, `breu`, `vinil`, `sequoia`, `vespera` em `palettes.css`, `style.css`, `appearance-advanced.css` e `appearance-bootstrap.js`.
2. **Definição dos 5 Novos Temas**:
   - `papel-fosco` (Padrão claro)
   - `noite-suave` (Escuro)
   - `cinza-neutro` (Claro)
   - `grafite` (Escuro)
   - `monocromatico` (Claro)
3. **Renomeação Simplificada**: Ajustar os rótulos dos 5 temas preservados para `Sépia`, `E-Ink`, `Solarized`, `Nord` e `Cyber`.
4. **Atualização da Interface de Ajustes**: Refletir os 10 novos nomes e valores no seletor de `SettingsView.vue`.

### Fase 3: Correções Dimensionais de Ícones e SVGs (US3)
1. **Empty State de Estudos Compartilhados**: Aplicar classe e regras CSS no SVG do empty state em `SharedStudiesList.vue` travando o tamanho máximo em 120px.
2. **Botão Compartilhar em StudyView**: Ajustar `.share-action` com `display: inline-flex; align-items: center; gap: 8px; white-space: nowrap;` e ícone com `width: 1.2em; height: 1.2em; flex-shrink: 0;`.
3. **Modal Exportar Estudo**: Travar as caixas e SVGs de inputs/radios em 24x24px, garantindo que o fluxo flex/grid posicione o ícone à esquerda e os textos à direita sem sobreposição.

### Fase 4: Contraste Dinâmico e Herança de Cores (US4)
1. **Cores do Modal de Exportação**: Substituir variáveis inexistentes por `--color-surface`, `--color-text`, `--color-muted` e `--color-border`.
2. **Status de Leitura**: Calibrar classes dos badges de status e do dropdown para manter legibilidade nítida sob fundos claros e escuros.
3. **Cabeçalho de Agrupamento (`GroupSection.vue`)**: Configurar `.group-toggle-btn` e `.group-title` para calcular e herdar contraste dinâmico em relação ao fundo ativo (garantindo fonte e traço brancos em fundos escuros/saturados e escuros em fundos claros).

---

## Complexity Tracking

*Nenhuma violação ou exceção às regras da Constituição detectada.*
