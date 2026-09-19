# Research: 009 — Invisível: Superclasse Silenciosa & Editorial e Limpeza de Ajustes

**Date**: 2026-09-19  
**Feature**: 009 — Invisível: Superclasse Silenciosa & Editorial e Limpeza de Ajustes  
**Status**: Completed  

---

## Technical Unknowns & Architectural Decisions

### Decision 1: Folha Modular Dedicada `styles/superclasses/invisivel.css`

- **Decision**: Criar `frontend/src/styles/superclasses/invisivel.css` dedicado, importado no ponto central `style.css`.
- **Rationale**:
  - Preserva a arquitetura desacoplada e limpa inaugurada nas features 007 e 008.
  - Escopo nominal duplo `:is(:root[data-superclass="invisivel"], .superclass-invisivel)`.
- **Alternatives considered**:
  - *Condensar todas as superclasses em arquivo único*: Rejeitado para preservar manutenibilidade e testes independentes de cada motor físico.

---

### Decision 2: Técnica de Desmaterialização de Caixas

- **Decision**:
  - Cartões de livros (`.book-card`, `.book-list-item`) e painéis têm `background: transparent; border: none; box-shadow: none;`.
  - A separação entre itens é feita através de margens limpas e, quando necessário, uma linha de base tênue (`border-bottom: 1px solid color-mix(in srgb, var(--color-border) 20%, transparent)`).
- **Rationale**:
  - Em design editorial e tipográfico, o "espaço negativo" e a tipografia estabelecem os limites funcionais dos conteúdos, sem a necessidade de "caixas dentro de caixas".
- **Alternatives considered**:
  - *Manter a caixa e apenas clarear a borda*: Não atinge o propósito da Superclasse Invisível, que é a desmaterialização da carcaça do software.

---

### Decision 3: Microinterações Editoriais (Shift Lateral e Underline Progressivo)

- **Decision**:
  - No hover: `transform: translateX(calc(4px * var(--sc-intensity)))` com transição `transform 200ms cubic-bezier(0.2, 0, 0, 1)`.
  - Títulos e links utilizam pseudo-elemento `::after` com `transform: scaleX(0)` em repouso e `scaleX(1)` no `:hover` com `transform-origin: left`.
- **Rationale**:
  - O movimento horizontal segue a linha de leitura (ocidental, da esquerda para a direita). O sublinhado dinâmico fornece feedback imediato de foco sem poluição de caixas ou botões plásticos.
- **Alternatives considered**:
  - *Sublinhado nativo do CSS (`text-decoration: underline`)*: O sublinhado padrão não permite animação progressiva de largura via GPU (`scaleX`).

---

### Decision 4: Transição de Página em Cascata Temporal (*Staggered Fade-Up*)

- **Decision**:
  - A transição do Vue Router (`<Transition name="page">`) sob a Invisível implementa cascata de entrada nos blocos estruturais (`.page-header`, `.workspace > *`, `.chapter-list`, `.reader-analysis`):
    - Bloco 1 (Cabeçalho/Título): `animation-delay: 0ms`
    - Bloco 2 (Metadados/Subtítulos): `animation-delay: 40ms`
    - Bloco 3 (Conteúdo/Texto): `animation-delay: 80ms`
  - A transição de saída é suave com fade puro de 150ms.
- **Rationale**:
  - Fornece um ritmo calmo de abertura de páginas similar a abrir as páginas de um livro encadernado.
- **Alternatives considered**:
  - *Deslizamento de página inteira*: Pode causar sensação de deslize excessivo e desconforto visual.

---

### Decision 5: Estratégia de Remoção e Migração dos Campos de Ajustes Obsoletos

- **Decision**:
  - Campos a remover: `style` (formato das caixas), `surface` (contraste de cartões) e `button-style` (preenchimento de botões).
  - Em `appearance-bootstrap.js`, os campos são removidos da lista congelada `fields`.
  - Na função `normalize(value)`, chaves legadas `style`, `surface` e `button-style` são toleradas e descartadas silenciosamente se presentes no `localStorage`.
  - Em `appearance.d.ts`, as propriedades são removidas do tipo `AppearancePreferences`.
  - Em `AppearanceControls.vue`, qualquer menção ou tratamento especial desses campos é removido.
- **Rationale**:
  - O usuário ganha uma interface mais clara, moderna e com menos opções redundantes.
  - Zero risco de perda de preferências existentes (temas e fontes permanecem intocados).
- **Alternatives considered**:
  - *Deixar os campos na tela mas marcá-los como desabilitados*: Rejeitado; cria poluição visual e confusão no usuário.
