# Implementation Plan: Feature 080 — Visualizações Móveis e Responsividade de Destaques

**Branch**: `080-visualizacoes-e-destaques-moveis` | **Data**: 2026-10-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/080-visualizacoes-e-destaques-moveis/spec.md`

---

## Summary

Esta feature resolve de forma definitiva dois eixos críticos de experiência em dispositivos móveis:
1. **Responsividade da Biblioteca de Destaques (`HighlightsLibraryView.vue`)**: Elimina o transbordamento horizontal da página (`scrollWidth > clientWidth`) ao reorganizar com flex-wrap a barra primária de busca (`HighlightFilterToolbar.vue`), expandindo a busca para 100% da largura em $\le 767\text{px}$ e quebrando o alternador de modo e o botão de filtros para a linha inferior. Garante que a barra inferior móvel (`MobileTabBar`) permaneça perfeitamente alinhada e ancorada sem sobrepor a paginação, através de padding inferior canônico com `--mobile-nav-offset`.
2. **Visualizações Complexas em Dispositivos Móveis (F0.8.14)**:
   - **Map View (`StudyMapView.vue`)**: Suporte a gestos táteis de pan com 1 dedo e pinch zoom com 2 dedos (delimitado em $[0.5, 2.5]$), além de modo alternativo em lista semântica de relações no celular com botões $\ge 44 \times 44\text{ px}$.
   - **Canvas View (`StudyCanvasView.vue`)**: Desbloqueio da rolagem vertical da página do leitor (`touch-action: pan-y`) em $\le 767\text{px}$ e compactação de toolbar em $< 1024\text{px}$.
   - **Tree View (`StudyTreeView.vue`)**: Supressão de alça de arrasto sob `@media (pointer: coarse)` e reordenação/aninhamento via menu contextual tátil com botões $\ge 44 \times 44\text{ px}$.

---

## Technical Context

**Language/Version**: TypeScript 5.x / Vue 3.5+ (`<script setup>`)  
**Primary Dependencies**: Vue 3, Vue Router, Lucide Vue Next, CSS autoral com tokens canônicos  
**Storage**: `localStorage` (`caderno_highlights_view_mode`, `caderno_active_view_mode`) e parâmetros de URL  
**Testing**: `node --test` (frontend) e `pytest` (backend)  
**Target Platform**: Navegadores modernos móveis e desktop (iOS Safari, Android Chrome, Windows/Mac desktop)  
**Project Type**: Web application responsiva local-first  
**Performance Goals**: 60 fps em transições e gestos táteis; zero atraso perceptual (< 16ms por frame) em pan/zoom  
**Constraints**: Zero emojis no código/documentação; sem novas bibliotecas externas pesadas; alvos táteis mínimos de $44 \times 44\text{ px}$  
**Scale/Scope**: 5 componentes de visualização/ferramenta (`HighlightsLibraryView.vue`, `HighlightFilterToolbar.vue`, `StudyMapView.vue`, `StudyCanvasView.vue`, `StudyTreeView.vue`)  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Avaliação | Justificativa / Mitigação |
|---|---|---|
| **I. Proteção do Acervo** | PASS | Alterações estritamente no frontend/CSS; nenhum dado do acervo exposto ou transmitido. |
| **II. Isolamento de Testes** | PASS | Testes automatizados executam isoladamente com stubs/dados sintéticos sem tocar no banco ativo. |
| **III. Fidelidade Arquitetural** | PASS | Vue 3 com Composition API, TypeScript estrito, CSS autoral com tokens e sem bibliotecas externas desnecessárias. |
| **IV. Governança por Spec Kit** | PASS | Ciclo formal seguido etapa por etapa (`specify` $\to$ `plan` $\to$ `tasks` $\to$ `implement`). |
| **V. Resiliência Operacional** | PASS | Sem alteração de schema SQLite ou endpoints de banco de dados. |

---

## Project Structure

### Documentation (this feature)

```text
specs/080-visualizacoes-e-destaques-moveis/
├── spec.md              # Especificação de requisitos e cenários
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas e análises de causas raízes
├── data-model.md        # Modelos de dados e estados reativos de UI
├── contracts/           # Contrato técnico normativo (mobile-views-highlights.contract.md)
├── checklists/          # Checklist de requisitos
└── quickstart.md        # Roteiro de validação ponta a ponta
```

### Source Code

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── highlights/
│   │   │   │   ├── HighlightFilterToolbar.vue  # Reorganização de linhas com flex-wrap
│   │   │   │   └── HighlightCard.vue           # Truncamento de títulos e rodapé responsivo
│   │   │   └── views/
│   │   │       ├── StudyMapView.vue            # Gestos de pan/pinch e lista semântica móvel
│   │   │       ├── StudyCanvasView.vue         # Desbloqueio de rolagem touch-action: pan-y
│   │   │       ├── StudyTreeView.vue           # Ações táteis e supressão de drag em pointer: coarse
│   │   │       └── canvas/
│   │   │           └── CanvasToolbar.vue       # Compactação de toolbar móvel
│   │   ├── views/
│   │   │   └── HighlightsLibraryView.vue       # Espaçamento inferior --mobile-nav-offset e contenção de overflow
│   │   └── mobile-navigation.css               # Ajustes globais de ancoragem da barra móvel
│   └── tests/
│       └── feature-080-mobile-views-highlights.test.mjs  # Testes automatizados
```

---

## Complexity Tracking

*Nenhuma violação identificada. O design preserva a simplicidade e a coerência da arquitetura.*
