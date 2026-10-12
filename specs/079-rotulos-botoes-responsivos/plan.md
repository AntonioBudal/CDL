# Implementation Plan: Rótulos de Botões e Linhas Texto + Botão em Telas Estreitas

**Branch**: `079-rotulos-botoes-responsivos` | **Date**: 2026-10-12 | **Spec**: [spec.md](file:///c:/Users/User/caderno/specs/079-rotulos-botoes-responsivos/spec.md)

**Input**: Problema P-20 da Auditoria de Responsividade (F0.8.13.5) e Contrato Técnico de Padrões de Rótulos de Botões.

## Summary

Esta feature implementa uma solução arquitetural unificada para quebra e contenção de botões em viewports móveis e estreitas (320px a 767px):
1. **Regra-Base Universal**: Aplicação de `white-space: nowrap; flex-shrink: 0;` na regra global de botões em `style.css:31`, impedindo que rótulos de botões de ação (Tipos A e D) quebrem palavras.
2. **Isenção Explícita (Tipo C)**: Declarar `white-space: normal` nominalmente em cartões-botão explicativos (`confirm-choice-card`, `btn-rating-card`, banners de busca, etc.).
3. **Reorganização de Grupos de Botões**: Aplicar `flex-wrap: wrap` e variantes curtas de rótulo (`.btn-text-full` / `.btn-text-short`) onde o espaço for insuficiente, em especial na barra de lote da Lixeira (`TrashView.vue`), Central de Revisão (`ReviewHubView.vue`, `ReviewPedagogicalEmpty.vue`) e rodapé público.
4. **Padronização de Linhas Híbridas (Tipo E)**: Estruturar `.section-heading` e barras de salvamento com quebra responsiva limpa quando o espaço para o título for inferior a `12rem`.
5. **Rótulos com Dados (Tipo B)**: Truncamento elegante com elipse e texto completo acessível em `title` e `aria-label`.
6. **Teste-Guarda Automatizado**: Criar teste automatizado em `tests/feature-079-button-labels.test.mjs` garantindo integridade das regras e ausência de regressões.

## Technical Context

**Language/Version**: TypeScript 5.7, Vue 3.5 (`<script setup>`), CSS3 nativo.  
**Primary Dependencies**: `vue`, `vue-router`, `lucide-vue-next`.  
**Storage**: N/A (intervenção de layout/estilo).  
**Testing**: `node --test` (Frontend), `pytest` (Backend).  
**Target Platform**: Navegadores modernos (Desktop e Mobile/Tablet), Safari iOS, Chrome Android.  
**Constraints**: Zero emojis no código e documentação; 1 Feature = 1 Commit; Alvos táteis $\ge 44 \times 44\text{ px}$; Sem criação de rolagem horizontal (`scrollWidth <= clientWidth`).

## Constitution Check

- **Preservação de Dados e Privacidade**: Totalmente estática/visual no frontend; nenhum acesso ao banco do usuário nem exposição de dados.
- **Integridade do Banco**: Nenhuma alteração no backend nem no schema SQLite.
- **Convenção de Versionamento**: 1 Feature = 1 Commit após validação total de testes e build.
- **Zero Emojis**: Garantida conformidade nominal e estética sem ícones emoji.

## Project Structure

### Documentation (this feature)

```text
specs/079-rotulos-botoes-responsivos/
├── spec.md
├── plan.md
├── contracts/
│   └── button-labels-patterns.contract.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code

- `caderno-leitura-0.1/frontend/src/style.css`
- `caderno-leitura-0.1/frontend/src/views/TrashView.vue`
- `caderno-leitura-0.1/frontend/src/views/ReviewHubView.vue`
- `caderno-leitura-0.1/frontend/src/components/review/ReviewPedagogicalEmpty.vue`
- `caderno-leitura-0.1/frontend/src/components/search/GlobalSearchModal.vue`
- `caderno-leitura-0.1/frontend/src/components/landing/HeroSection.vue`
- `caderno-leitura-0.1/frontend/src/components/PublicFooter.vue`
- `caderno-leitura-0.1/frontend/tests/feature-079-button-labels.test.mjs`
