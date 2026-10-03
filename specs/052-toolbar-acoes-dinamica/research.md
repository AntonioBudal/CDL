# Technical Research: F 0.7.3 — Refatoração Dinâmica da Floating Actions Toolbar

**Feature**: F 0.7.3 — Refatoração Dinâmica da Floating Actions Toolbar  
**Status**: Completed  
**Artifact**: `research.md`

---

## Decisões Técnicas e Padrões de Projeto

### D1: Desacoplamento da Camada de Detalhe em `NoteQuestionPopover.vue`

- **Decisão:** Extrair completamente a interface e a lógica de anotações e perguntas de dentro de `FloatingActionsToolbar.vue` para um novo componente independente: `NoteQuestionPopover.vue`.
- **Racional:** 
  1. No design anterior, a régua de ações incluía caixas de entrada de texto e botões de confirmação no mesmo contêiner. Quando o usuário clicava em "Anotar", a régua dobrava de tamanho horizontal e vertical, desalinhava o cálculo de posicionamento na tela e encobria o texto lido.
  2. O desacoplamento permite que a régua de ações se recolha temporariamente durante a redação (conforme definido no esclarecimento Q3), deixando apenas o popover contextual ativo no viewport.
  3. `NoteQuestionPopover.vue` gerencia exclusivamente seu ciclo de vida: foco inicial (`autofocus`), validação de caracteres, atalhos de teclado e emissão de eventos limpos (`@save`, `@cancel`).
- **Alternativas consideradas:**
  - *Manter componente único com alternância de estado (`isEditingNote`):* Rejeitado porque sobrecarrega o componente com mais de 700 linhas, dificulta testes unitários isolados e perpetua o problema de recalcular coordenadas para duas geometrias completamente distintas na mesma div.

---

### D2: Marca-Texto via Split Button e Persistência Reativa com `useHighlightColorPreference.ts`

- **Decisão:** Implementar a ação de grifar como um **Split Button** (botão bipartido). A porção principal exibe o ícone de marca-texto com a tonalidade atual e aplica o destaque em **1 único clique**. A porção secundária (seta discreta) abre a paleta suspensa de 5 cores canônicas (`yellow`, `green`, `blue`, `pink`, `purple`). A cor ativa é gerenciada pelo composable `useHighlightColorPreference.ts`.
- **Racional:**
  1. 90% das interações na barra flutuante consistem em aplicar o mesmo marca-texto em trechos sequenciais. Forçar o leitor a abrir uma paleta a cada clique introduzia atrito cognitivo.
  2. A persistência no `localStorage` (`caderno_last_highlight_color`) com fallback seguro para `yellow` memoriza a escolha entre capítulos, estudos e sessões do navegador.
- **Alternativas consideradas:**
  - *Clique longo para abrir paleta:* Rejeitado por conflito com gestos de toque no mobile e ausência de semântica acessível WAI-ARIA.
  - *Botões de cores sempre visíveis:* Rejeitado por consumir espaço horizontal precioso (ocuparia mais de 200px extras na barra, estourando no mobile).

---

### D3: Tratamento de Teclado: `Enter` para Salvar, `Shift+Enter` para Nova Linha e `Escape` para Cancelar

- **Decisão:** No `<textarea>` de `NoteQuestionPopover.vue`, o evento `@keydown` intercepta:
  - `Enter` sem modificador `Shift`: Previne a quebra de linha nativa (`e.preventDefault()`) e dispara o salvamento atômico da anotação/pergunta.
  - `Shift+Enter`: Insere normalmente uma quebra de linha (`\n`), permitindo estruturar notas em múltiplos parágrafos quando o leitor desejar.
  - `Escape`: Cancela a edição, descarta o rascunho e emite `@cancel`.
- **Racional:**
  - Alinhamento rigoroso com a preferência explícita acordada na rodada de esclarecimento (Q2).
  - Oferece agilidade de preenchimento instantâneo no desktop para notas curtas e perguntas reflexivas sem exigir deslocamento do mouse para o botão "Salvar".
- **Alternativas consideradas:**
  - *`Ctrl+Enter` para salvar:* Avaliado na clarificação e descartado em favor da velocidade do `Enter` direto com `Shift+Enter` para multilinha.

---

### D4: Mobile Docking com Gaveta Inferior (*Bottom Sheet*) e Proteção via `window.visualViewport`

- **Decisão:** Em telas menores que 768px:
  1. A régua de botões mantém alvos táteis de no mínimo 44×44px e ícones puros de 22×22px (já padronizados na F 0.7.2).
  2. Ao acionar "Anotar" ou "Pergunta", o formulário abre como uma gaveta inferior (*bottom sheet*) ancorada na base da tela.
  3. Para neutralizar o problema comum do teclado virtual móvel cobrindo o campo de digitação, o componente monitora os eventos `resize` e `scroll` de `window.visualViewport`:
     $$\text{offsetBottom} = \max(0, \text{window.innerHeight} - \text{visualViewport.height} - \text{visualViewport.offsetTop})$$
     Esse deslocamento eleva a gaveta exatamente acima do teclado virtual em navegadores Chrome Android e iOS Safari.
- **Racional:**
  - Navegadores móveis não comportam `position: fixed; bottom: 0;` de maneira uniforme quando o teclado de software é invocado. A API `window.visualViewport` é o padrão W3C moderno para lidar com teclados virtuais sem rolagem quebrada.
- **Alternativas consideradas:**
  - *Deixar o navegador rolar naturalmente:* Rejeitado porque frequentemente resulta em inputs escondidos atrás do teclado ou botões fora da área visível.

---

### D5: Tolerância a Deseleção e Ciclo de Notificações

- **Decisão:** Quando o usuário clica em "Anotar" ou "Pergunta", o `SelectionContext` ativo é copiado e retido no estado do popover. Se o clique na caixa de texto fizer a seleção de texto nativa do navegador perder o foco azul, os limites de texto (`start_offset`, `end_offset`, etc.) continuam preservados no componente até o envio ou cancelamento.
- **Racional:**
  - Clicar em um `<textarea>` naturalmente move o cursor e remove a seleção visual do `window.getSelection()`. Reter o contexto no estado garante persistência sem perda de dados.
- **Alternativas consideradas:**
  - *Impedir foco com `preventDefault`:* Inviabilizaria a digitação no campo de texto.
