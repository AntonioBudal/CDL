# Contrato Técnico: Padrões de Rótulos de Botões e Linhas Híbridas

**Feature**: `079-rotulos-botoes-responsivos`  
**Escopo**: Definição normativa das regras de quebra, não quebra, isenções e empilhamento de botões e linhas texto+botão.

---

## 1. Regra-Base Universal de Botões (Tipos A e D)

A regra-base de estilo em `src/style.css:31` para elementos interativos deve declarar explicitamente:

```css
button, .button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap; /* Impede quebra de rótulos entre palavras */
  flex-shrink: 0;     /* Previne colapso abaixo do conteúdo intrínseco do rótulo */
}
```

### Regras Adicionais
- Links com aparência de botão (`.btn-primary`, `.btn-action`, `.btn-mode`, etc.) herdam ou declaram `white-space: nowrap;`.
- Botões não podem ter altura fixa que impeça o ajuste do conteúdo ou corte o texto quando combinados com ícones.

---

## 2. Isenção Formal de Controles Tipo C (Botões-Cartão Multilinha)

Controles do Tipo C contêm títulos acompanhados de parágrafos explicativos ou descrições ricas. Ficam expressamente isentos da proibição de quebra e devem declarar:

```css
white-space: normal;
```

### Lista Nominal de Controles Isentos (Tipo C)
1. `.conflict-option-card` / `.confirm-choice-card` em `ConcurrencyConflictModal.vue` e `ConflictResolutionModal.vue`.
2. `.btn-rating-card` em `StudySessionView.vue`.
3. `.search-mode-banner-button` em `GlobalSearchModal.vue` (botão de alternância OR com descrição de 50 caracteres).
4. `.template-selection-card` em `TemplateSelectorModal.vue`.

Nenhum outro botão fora desta lista nominal pode conter `white-space: normal`.

---

## 3. Padrão de Reorganização de Grupos de Ações

Quando múltiplos botões compartilham um contêiner e o espaço horizontal for inferior à soma das larguras intrínsecas dos botões:

1. **Empilhamento ou Quebra de Grupo**: O contêiner pai deve utilizar `flex-wrap: wrap;` com espaçamento uniforme (`gap: 0.5rem;` ou `gap: 0.75rem;`).
2. **Variantes Curtas (.btn-text-full e .btn-text-short)**:
   - Em viewports estreitas ($\le 640\text{px}$ ou $\le 480\text{px}$), botões com rótulos longos podem exibir variante concisa:
     - "Exportar anotações" $\to$ "Exportar"
     - "Restaurar selecionados" $\to$ "Restaurar"
     - "Excluir definitivamente" $\to$ "Excluir"
     - "Explorar meus Livros e Criar Estudos" $\to$ "Explorar Livros"
   - O elemento pai ou o botão mantém `title` e `aria-label` com o texto integral descritivo da ação.
3. **Abas e Segmentos de Largura Fixa**:
   - Em telas móveis, caso abas divididas igualmente (`flex: 1`) fiquem comprimidas, o contêiner deve ativar rolagem horizontal contida (`overflow-x: auto; white-space: nowrap; scrollbar-width: none;`).

---

## 4. Padrão Normativo para Linhas Híbridas Texto + Botão (Tipo E)

Linhas que combinam títulos/legendas e botões de ação laterais (ex.: `.section-heading`, `.save-bar`, cabeçalhos de cartão):

```css
.section-heading,
.hybrid-text-action-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.section-heading-text,
.hybrid-row-text {
  flex: 1 1 12rem; /* Permite expansão, mas empilha se espaço for < 12rem */
  min-width: 0;   /* Permite quebra natural de palavras do título */
}

.section-heading-actions,
.hybrid-row-actions {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
```

### Comportamento Resultante
- Em desktop e telas amplas: título e botões permanecem na mesma linha, alinhados nas extremidades opostas.
- Em telas compactas ($< 768\text{px}$ ou viewports de 320px): se o título não tiver pelo menos `12rem` de largura útil antes de colidir com os botões, os botões descem suavemente para a linha seguinte, sem truncar nem estrangular o texto.

---

## 5. Rótulos com Dados Variáveis (Tipo B)

Botões cujo rótulo inclui dados dinâmicos do acervo (nomes de livros, capítulos, tags ou contadores longos):

```css
.btn-data-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: min(100%, 16rem);
}
```

- Obrigatório incluir atributos `title="{{ texto_completo }}"` e `aria-label="{{ texto_completo }}"`.

---

## 6. Critérios de Blindagem Contra Regressões

1. O valor de `scrollWidth` no `document.documentElement` e no `body` deve ser exatamente igual a `clientWidth` em todas as larguras de teste (320px, 375px, 390px, 430px, 767px).
2. Todo alvo tátil mantém área mínima de $44 \times 44\text{ px}$ em telas móveis.
3. Teste automatizado valida a presença de `white-space: nowrap;` na regra-base e a conformidade da lista de isentos do Tipo C.
