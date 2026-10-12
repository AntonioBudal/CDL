# Implementation Plan: Correções Visuais, de Cor e de Disposição

**Branch**: `075-correcoes-visuais-disposicao` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/075-correcoes-visuais-disposicao/spec.md`

---

## Summary

Resolução de 14 pendências visuais no frontend abrangendo adaptação consistente de temas (eliminando a causa raiz de 115 variáveis CSS não declaradas via camada de compatibilidade em `tokens.css`), alinhamento de grade e capas de livros, ergonomia e contraste das visualizações de estudo em `/livros/:id`, despoluição do cabeçalho e rodapé, e persistência do tema da visita entre páginas públicas.

---

## Technical Context

**Language/Version**: TypeScript 5.x, Vue 3.5 (Composition API, `<script setup>`), CSS3 nativo (CSS Custom Properties).  
**Primary Dependencies**: Vue Router 4, Pinia (se aplicável), Vite 5. Sem adição de novas dependências externas.  
**Storage**: `sessionStorage` para persistência efêmera do tema da visita pública (`caderno_visitor_theme`); zero alteração em banco de dados SQLite.  
**Testing**: Node.js test runner (`node --test`), Vitest / Vue Test Utils (`npm test`), build de produção Vite (`npm run build`).  
**Target Platform**: Navegadores modernos desktop e mobile (Chrome, Firefox, Safari, Edge) em ambiente local Windows / rede privada.  
**Project Type**: Aplicação Web SPA (Frontend em `caderno-leitura-0.1/frontend`).  
**Performance Goals**: Tempo de montagem $< 50$ms, troca instantânea de tema sem recarregar página e sem piscar (*flash of unstyled theme*).  
**Constraints**: Zero emojis em todo o código e interface; isolamento estrito de testes; zero alteração em backend ou banco ativo; cumprimento das diretrizes de acessibilidade WCAG AA (contraste $\ge 4,5:1$ para textos e $\ge 3:1$ para controles).  
**Scale/Scope**: 15 componentes e estilos de frontend modificados; 1 teste automatizado de integridade CSS criado; zero migrações de backend.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Avaliação no Pré-Planejamento | Avaliação Pós-Design (Fase 1) | Justificativa |
|---|:---:|:---:|---|
| **I. Proteção do Acervo e Privacidade** | PASS | PASS | A feature atua 100% no frontend visual. Nenhum dado do acervo real ou banco de dados é lido ou transmitido. |
| **II. Isolamento de Testes** | PASS | PASS | O teste de validação de tokens CSS é puramente estático (`node --test`), sem conexão a banco ou servidores. |
| **III. Fidelidade Arquitetural** | PASS | PASS | Vue 3, TypeScript estrito, CSS Custom Properties e Vite mantidos sem introdução de frameworks paralelos. |
| **IV. Governança por SDD** | PASS | PASS | Execução estrita do fluxo Spec Kit (`speckit-plan` após `speckit-specify`). |
| **Regra Constitucional: Zero Emojis** | PASS | PASS | 100% dos textos, labels e ícones utilizam exclusivamente SVG/ícones semânticos, sem nenhum emoji. |

---

## Project Structure

### Documentation (this feature)

```text
specs/075-correcoes-visuais-disposicao/
├── spec.md              # Especificação de requisitos e cenários de aceite
├── plan.md              # Este plano de implementação técnica
├── research.md          # Decisões de arquitetura e resolução de causa raiz (Fase 0)
├── data-model.md        # Entidades e modelos de estado de interface (Fase 1)
├── quickstart.md        # Guia de execução e roteiro de testes (Fase 1)
├── contracts/           # Contratos formais de tokens e componentes (Fase 1)
│   ├── theme-tokens-compatibility.contract.md
│   └── ui-components.contract.md
└── checklists/
    └── requirements.md  # Checklist de validação de requisitos
```

### Source Code (repository root)

```text
caderno-leitura-0.1/frontend/
├── src/
│   ├── tokens.css                              # Camada de compatibilidade de tokens (115 variáveis)
│   ├── appearance-advanced.css                 # Ajuste de .book-grid com auto-fill e alinhamento à esquerda
│   ├── components/
│   │   ├── BookCover.vue                       # Ocultar título em miniaturas pequenas size="sm"
│   │   ├── CategoryBadge.vue                   # Fundo transparente e borda temática
│   │   ├── LibraryToolbar.vue                  # Seletor de visualizações e cores da busca
│   │   ├── StudyStatusBadge.vue                # Fundo transparente e indicadores semânticos acessíveis
│   │   ├── layout/
│   │   │   ├── AppFooter.vue                   # Alinhamento distribuído e responsividade mobile
│   │   │   └── UserDropdown.vue                # Gatilho contendo apenas avatar de 44x44px
│   │   ├── ui/
│   │   │   └── EmptyState.vue                  # Remoção de fundos brancos fixos
│   │   ├── views/
│   │   │   ├── StudyListView.vue               # Alinhamento de cabeçalhos e ícone de ordenação
│   │   │   ├── StudyTreeNodeItem.vue           # Banimento de --color-inverse-bg em textos e ícones
│   │   │   └── StudyMapView.vue                # Contraste de zoom e barra mobile oculta em desktop
│   │   └── landing/
│   │       └── PublicFooter.vue                # Atualização do link para AntonioBudal/CDL
│   ├── views/
│   │   ├── BooksView.vue                       # Botão limpo "Adicionar Livro" sem "+" duplo
│   │   ├── FriendsView.vue                     # Estado vazio padronizado de bloqueados
│   │   └── SupportView.vue                     # Explicação serena de apoio comunitário e código aberto
│   └── composables/
│       └── useVisitorTheme.ts                  # Persistência em sessionStorage sem reversão no unmount
tests/
└── feature-075-css-tokens-integrity.test.mjs   # Teste automatizado de cobertura de variáveis CSS
```

**Structure Decision**: A implementação concentra-se no pacote de frontend `caderno-leitura-0.1/frontend/src/` e adiciona uma suíte de teste de integridade CSS em `tests/`, mantendo total conformidade com a estrutura monorrepo da aplicação.

---

## Complexity Tracking

*Nenhuma violação constitucional identificada. Arquitetura limpa e focada em design tokens nativos e refatoração de CSS/Vue.*
