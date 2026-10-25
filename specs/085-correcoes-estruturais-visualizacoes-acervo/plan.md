# Implementation Plan: Correções Estruturais nas Visualizações do Acervo

**Branch**: `085-correcoes-estruturais-visualizacoes-acervo` | **Date**: 2026-10-24 | **Spec**: [specs/085-correcoes-estruturais-visualizacoes-acervo/spec.md](spec.md)

**Input**: Feature specification from `specs/085-correcoes-estruturais-visualizacoes-acervo/spec.md`

## Summary

Esta feature implementa o conjunto de refinamentos estruturais, prevenção de cortes visuais (*clipping*) e alinhamento geométrico nas duas visualizações ativas do acervo do Leitorum: [`StudyListView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue) e [`StudyGridView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/views/StudyGridView.vue), além do componente [`StudyStatusBadge.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/StudyStatusBadge.vue).

As soluções contemplam:
1. Eliminação definitiva de cortes de borda no menu suspenso de status de leitura, refinando o limiar de cálculo da direção ascendente (`opensUpward`) e elevando o contexto de empilhamento (`z-index: 1000`) nas linhas e cartões com menu ativo.
2. Garantia de herança de cor do ícone SVG de ordenação nos cabeçalhos da tabela (`stroke: currentColor` e `fill: none`), assegurando legibilidade e alto contraste em todos os 10 temas oficiais.
3. Padronização estrita da malha geométrica de grid CSS compartilhada entre cabeçalho (`.list-header-row`), dados (`.study-row-item`) e linhas de carregamento (`.skeleton-row`), com centralização uniforme nas colunas de seções e ações operacionais.

---

## Technical Context

**Language/Version**: TypeScript 5.6+, Vue 3.5+ (Composition API, `<script setup>`), CSS3 Moderno, Python 3.13 (Backend de suporte)  
**Primary Dependencies**: Vue 3, Vite, lucide-vue-next, FastAPI (API local)  
**Storage**: SQLite local em modo WAL (inalterado nesta feature de UI/UX)  
**Testing**: Node.js test runner (`node --test`), `npm test`, `pytest`  
**Target Platform**: Navegadores modernos desktop (1024px a 2560px) e mobile (Windows, macOS, iOS, Android)  
**Project Type**: Web Application SPA Local (Leitorum)  
**Performance Goals**: Abertura de menu e ordenação de tabela instantâneas (< 16ms / 60fps), sem reflows ou layout thrashing  
**Constraints**: Zero emojis, sem adição de bibliotecas externas, conformidade com WCAG AA em todos os 10 temas canônicos  
**Scale/Scope**: Listas e grades contendo de 1 a 200+ estudos por livro ou capítulo  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I (Privacidade Absoluta de Dados)**: PASS. Nenhuma leitura de dados reais do acervo; apenas mock e classes de layout.
- **Princípio II (Isolamento de Testes)**: PASS. Todos os testes de unidade operam sobre cópias em memória ou arquivos estáticos sem tocar em `backend/data/caderno.db`.
- **Princípio III (Fidelidade Arquitetural)**: PASS. Vue 3 Composition API com TypeScript estrito, CSS Scoped com variáveis de tokens dos temas oficiais.
- **Princípio IV (Governança Spec-Driven)**: PASS. Ciclo formal Spec Kit respeitado sequencialmente.
- **Princípio V (Resiliência Operacional)**: PASS. Sem alterações em banco de dados ou migrações de schema.

---

## Project Structure

### Documentation (this feature)

```text
specs/085-correcoes-estruturais-visualizacoes-acervo/
├── spec.md              # Especificação de requisitos da feature
├── plan.md              # Este plano de implementação técnica
├── research.md          # Pesquisa técnica e diagnóstico das causas de layout
├── data-model.md        # Mapeamento de tipos e estados reativos
├── quickstart.md        # Guia de validação automatizada e manual
├── contracts/           # Contratos de componentes e malha de layout
│   └── study-views-layout.contract.md
└── checklists/
    └── requirements.md  # Checklist de qualidade da especificação
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── StudyStatusBadge.vue               # Refinamento de opensUpward e z-index
    │   │   └── views/
    │   │       ├── StudyListView.vue              # Grid estrito, stroke currentColor, overflow visible
    │   │       └── StudyGridView.vue              # Elevação de z-index no cartão com dropdown aberto
    └── tests/
        ├── study_layout_and_contrast_fixes.test.mjs  # Testes legados de layout
        └── feature-085-study-views-layout.test.mjs   # Nova suíte focada na feature F04
```

**Structure Decision**: As alterações são concentradas nos componentes de visualização do acervo (`StudyListView.vue`, `StudyGridView.vue`, `StudyStatusBadge.vue`) e na criação de uma suíte de testes unitários dedicada (`feature-085-study-views-layout.test.mjs`), preservando a integridade das suítes existentes.

---

## Complexity Tracking

*Nenhuma violação constitucional registrada.*
