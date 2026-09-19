# Research: 008 — Mecânica: Superclasse Tátil & Responsiva

**Date**: 2026-09-19  
**Feature**: 008 — Mecânica: Superclasse Tátil & Responsiva  
**Status**: Completed  

---

## Technical Unknowns & Architectural Decisions

### Decision 1: Folha Modular Dedicada `styles/superclasses/mecanica.css`

- **Decision**: Criar um arquivo CSS modular dedicado em `frontend/src/styles/superclasses/mecanica.css`, importado pelo ponto central `style.css` e incluído no `index.html`.
- **Rationale**: 
  - Preserva a separação rigorosa de preocupações de cada Superclasse.
  - Permite ativar o arquétipo através do seletor composto `:is(:root[data-superclass="mecanica"], .superclass-mecanica)`, garantindo suporte tanto aos atributos injetados por `cadernoAppearance` quanto à classe CSS direta.
- **Alternatives considered**:
  - *Arquivo único concentrando todas as superclasses*: Rejeitado para evitar arquivos de centenas de linhas e dificultar a manutenção individual de cada física.

---

### Decision 2: Mecânica de Push-Down com Compensação de Sombra Dura

- **Decision**: No estado de clique (`:active`), o elemento desce exatamente `translateY(calc(3px * var(--sc-intensity)))` enquanto a sombra sólida zera (`box-shadow: 0 0 0 transparent`).
- **Rationale**:
  - Em teclados mecânicos e botões industriais, a tecla física tem um relevo que projeta sombra sólida abaixo de si. Ao ser pressionada até o fim de curso (*bottom out*), o espaço entre a tecla e o chassi fecha-se completamente.
  - Como a sombra de repouso tem altura de 3px e o deslocamento no clique é de exatamente 3px para baixo, a base do elemento encosta perfeitamente na linha inferior da carcaça, entregando uma resposta tátil imediata e hiper-realista.
- **Alternatives considered**:
  - *Apenas mudar a cor do botão no clique*: Não transmite a sensação física de teclado mecânico.
  - *Transição de afundamento com inércia lenta*: Rejeitado; switches mecânicos respondem de forma linear rápida (100ms).

---

### Decision 3: Supressão Absoluta de Respiração de Repouso e Magnetismo

- **Decision**: Sob a Superclasse Mecânica, nenhuma regra de *idle breathing* ou rastreamento magnético de cursor é ativada (`animation: none !important;`).
- **Rationale**:
  - A Superclasse Mecânica representa hardware físico rígido e parafusado. Elementos flutuando ou perseguindo o mouse descaracterizariam a identidade de solidez e precisão tátil.
- **Alternatives considered**:
  - *Manter uma oscilação mecânica como engrenagem*: Rejeitado para evitar distrações e respeitar a especificação do usuário (repouso 100% estático).

---

### Decision 4: Transições de Rota Vue Router em Corte Seco (100ms)

- **Decision**: Definir estilos para `<Transition name="page">` sob `.superclass-mecanica`:
  - Duração de 100ms com curva `linear`.
  - Transição pura de opacidade (sem translação em Y), funcionando como um corte limpo.
- **Rationale**:
  - Equipamentos de precisão e interfaces táteis devem responder instantaneamente sem delays visuais ornamentais.
- **Alternatives considered**:
  - *Transição com wipe de tela complexo*: Poderia introduzir jank em computadores mais lentos; a transição de opacidade rápida de 100ms é acelerada por hardware na GPU.

---

### Decision 5: Isolamento Absoluto do Modo de Leitura

- **Decision**: Manter a cláusula pétrea de imobilidade: `.markdown-content`, ferramentas de leitura e seções de estudo continuam forçando `transform: none !important; animation: none !important;`.
- **Rationale**:
  - A soberania e a ergonomia de leitura prolongada não podem ser perturbadas por animações ou deslocamentos durante o estudo.
