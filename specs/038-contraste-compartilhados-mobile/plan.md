# Implementation Plan: F09.5.2 — Contraste Dinâmico, Estudos Compartilhados e Responsividade Mobile

**Branch**: `038-contraste-compartilhados-mobile` | **Date**: 2026-09-26 | **Spec**: [specs/038-contraste-compartilhados-mobile/spec.md](file:///c:/Users/User/caderno/specs/038-contraste-compartilhados-mobile/spec.md)

**Input**: Feature specification from `specs/038-contraste-compartilhados-mobile/spec.md`

---

## Summary

Esta feature resolve de forma definitiva e sistêmica três pontos críticos da experiência visual e ergonômica do Leitorum:
1. **Motor Centralizado de Contraste WCAG 2.1**: Implementação de um utilitário de luminância relativa e composable reativo (`useAccessibleContrast`) que injeta variáveis CSS customizadas locais no nó DOM (`--dynamic-fg`, `--dynamic-hover-fg`, etc.), erradicando cores hard-coded (`#FFFFFF !important`, `#18181b`) e garantindo taxa $\ge 4.5:1$ em todos os estados de interação (`default`, `hover`, `focus`, `active`, `selected`).
2. **Diagnóstico Estrutural e Reformulação de Estudos Compartilhados**: Identificação formal da causa raiz dos SVGs gigantes (classes utilitárias Tailwind órfãs em projeto que não usa Tailwind) e refatoração completa de `SharedStudiesList.vue` com componentes oficiais (`<Icon />`), tokens semânticos do Leitorum e estados aprimorados de busca, filtro, loading, erro e empty state contido.
3. **Arquitetura de Navegação Mobile e Rolagem de Abas**: Reformulação da grade rígida de 3 colunas em `mobile-navigation.css` para um modelo ergonômico prioritário de 5 colunas com botão "Mais" acionando gaveta inferior (*bottom sheet* `MobileMoreMenu.vue`), além de rolagem horizontal com máscara gradiente sutil (*fade mask*) para abas segmentadas em smartphones.

---

## Technical Context

**Language/Version**: TypeScript 5.8+ / Vue 3.5+ (Composition API, `<script setup>`), CSS3 Moderno (Custom Properties, Flexbox, Grid, Fade Masks), Python 3.13 (Backend).

**Primary Dependencies**: Vue 3, Vue Router 4, Lucide Vue Next (`<Icon />`), Vanilla CSS Tokens (`tokens.css`, `palettes.css`, `style.css`, `mobile-navigation.css`), FastAPI (Backend).

**Storage**: `localStorage` no navegador (persistência visual e tema), SQLite 3 no backend (`caderno.db` isolado em produção).

**Testing**: Node.js test runner (`node --test tests/contrast_engine.test.mjs`, `visual_system.test.mjs`), `vue-tsc -b` para checagem estrita de tipos, e `pytest` para integridade geral.

**Target Platform**: Navegadores modernos (Desktop, Tablet e Mobile) executados no processo local único via Windows/PowerShell e LAN/Tailscale.

**Project Type**: Web Application (Single-Page Application Vue 3 servida por backend FastAPI).

**Performance Goals**: Cálculo de luminância em tempo submilisegundo ($< 0.1\text{ms}$ por elemento); estados de hover e focus delegados às variáveis CSS locais sem disparar ciclos de re-renderização do Vue; 60fps em animações de rolagem e drawer mobile.

**Constraints**: Preservação das diretrizes anti-emoji, WCAG 2.1 nível AA para taxa de contraste em textos (mínimo 4.5:1), alvos de toque mínimos de 44x44px em botões móveis, zero dependência externa de Tailwind CSS.

**Scale/Scope**: 1 utilitário puro (`contrast.ts`), 1 composable (`useAccessibleContrast.ts`), 1 novo componente de gaveta móvel (`MobileMoreMenu.vue`), 3 componentes refatorados (`SharedStudiesList.vue`, `App.vue`, `BooksView.vue`), 2 arquivos de folha de estilo revisados (`mobile-navigation.css`, `style.css`), e 1 suíte de testes unitários (`contrast_engine.test.mjs`).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Princípio I (Privacidade e Preservação de Dados)**: A feature atua exclusivamente na camada de apresentação visual, acessibilidade e ergonomia mobile. Nenhuma leitura ou transmissão de dados do acervo é realizada.
- [x] **Princípio II (Isolamento de Testes)**: Todos os testes automatizados utilizam ambientes efêmeros isolados e executam em memória, sem conectar nem alterar o banco de dados ativo de produção.
- [x] **Princípio III (Fidelidade Tecnológica)**: Utiliza Vue 3 Composition API com TypeScript estrito, CSS Custom Properties nativas e componentes padronizados com Lucide Vue Next, sem introduzir dependências desnecessárias.
- [x] **Princípio IV (Governança por Especificação)**: Segue estritamente o ciclo Spec Kit integrado ao Antigravity (`agy`), com análise formal, especificação validada e planejamento técnico completo.
- [x] **Princípio V (Resiliência Operacional)**: A arquitetura móvel e o cálculo de contraste possuem fallbacks seguros; caso um valor de cor seja inválido ou o dispositivo não suporte certas funções, o sistema recorre de forma síncrona aos valores semânticos padrão do tema.

---

## Project Structure

### Documentation (this feature)

```text
specs/038-contraste-compartilhados-mobile/
├── spec.md                     # Especificação formal da feature (100% validada)
├── checklists/
│   └── requirements.md         # Checklist de qualidade de requisitos (100% aprovada)
├── research.md                 # Diagnóstico de SVGs, WCAG 2.1 e decisões técnicas
├── data-model.md               # Modelos de dados e tipos TypeScript
├── quickstart.md               # Roteiro de validação prática e testes
├── contracts/
│   ├── contrast-engine.contract.md    # Contrato da API de contraste e composable
│   └── mobile-navigation.contract.md  # Contrato da barra mobile e gaveta 'Mais'
├── plan.md                     # Este documento técnico
└── tasks.md                    # Próxima fase: decomposição atômica de tarefas (/speckit-tasks)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
└── frontend/
    ├── src/
    │   ├── utils/
    │   │   └── contrast.ts                    # Utilitário puro: WCAG relative luminance & contrast ratio
    │   ├── composables/
    │   │   └── useAccessibleContrast.ts       # Composable reativo: injeção de --dynamic-fg/hover/active
    │   ├── components/
    │   │   ├── navigation/
    │   │   │   └── MobileMoreMenu.vue         # Gaveta inferior (Bottom Sheet) acionada pelo botão 'Mais'
    │   │   ├── library/
    │   │   │   └── SharedStudiesList.vue      # Reformulação completa: <Icon />, tokens Leitorum, cards
    │   │   └── ui/
    │   │       └── Icon.vue                   # Componente canônico de ícones (Lucide)
    │   ├── views/
    │   │   ├── BooksView.vue                  # Abas da biblioteca com contraste dinâmico
    │   │   └── SettingsView.vue               # Abas com máscara gradiente de overflow
    │   ├── App.vue                            # Integração da barra de 5 colunas com botão 'Mais'
    │   ├── mobile-navigation.css              # Grid de 5 colunas e estilos da barra móvel
    │   └── style.css                          # Remoção de !important estáticos e adoção de tokens
    └── tests/
        └── contrast_engine.test.mjs           # Testes automatizados do motor de contraste
```

**Structure Decision**: A implementação concentra-se no frontend Vue 3 (`caderno-leitura-0.1/frontend`), mantendo o desacoplamento entre utilitários matemáticos puros (`utils/contrast.ts`), composables reativos (`composables/useAccessibleContrast.ts`), componentes de interface (`components/navigation`, `components/library`) e folhas de estilo CSS nativas.

---

## Architecture & Execution Plan

### Fases de Implementação:

1. **Fase 1 — Motor Centralizado de Contraste WCAG 2.1**:
   - Criação de `frontend/src/utils/contrast.ts` com funções `parseCssColor`, `getRelativeLuminance`, `getContrastRatio`, `blendAlpha` e `getAccessibleTextColor`.
   - Criação de `frontend/src/composables/useAccessibleContrast.ts` para geração de variáveis CSS locais reativas.
   - Criação da suíte de testes unitários `frontend/tests/contrast_engine.test.mjs`.
   - Limpeza das regras estáticas com `!important` em `frontend/src/style.css` e adoção de `--dynamic-fg`.

2. **Fase 2 — Reformulação Completa de Estudos Compartilhados**:
   - Expurgar todas as classes Tailwind inexistentes em `SharedStudiesList.vue`.
   - Substituir tags `<svg>` soltas pelo componente `<Icon />` com dimensões restritas (16px a 20px).
   - Aplicar tokens semânticos (`--color-surface`, `--color-border`, `--color-text`, etc.).
   - Refatorar a barra de busca, o filtro de `@autor`, os cartões de estudo, o esqueleto de loading e o empty state com ilustração de no máximo 120px.

3. **Fase 3 — Arquitetura de Navegação Mobile e Gaveta 'Mais'**:
   - Criar o componente `frontend/src/components/navigation/MobileMoreMenu.vue` com transição suave, backdrop e opções secundárias (`Lixeira`, `Admin`, `Conexão`, `Perfil`, `Logout`).
   - Refatorar a barra `.main-nav` em `App.vue` para exibir 5 destinos (`Início`, `Importar`, `Amigos`, `Ajustes`, `Mais`).
   - Atualizar `mobile-navigation.css` com a grade `repeat(5, minmax(0, 1fr))` e alvos de toque $\ge 44\text{px}$.
   - Aplicar classes de rolagem com máscara de desvanecimento (*fade mask*) para abas segmentadas em telas pequenas.

4. **Fase 4 — Validação Geral, Testes de Acessibilidade e Build**:
   - Execução de `node --test tests/contrast_engine.test.mjs`.
   - Execução de `npm run build` (`vue-tsc -b` + `vite build`) para garantir zero erros de tipagem.
   - Validação da experiência mobile em emulador com viewports de 360px a 412px.

---

## Complexity Tracking

*Nenhuma violação aos princípios da Constituição foi identificada.* O escopo respeita a arquitetura local do Leitorum, evita bibliotecas desnecessárias e promove reuso dos tokens canônicos já estabelecidos.
