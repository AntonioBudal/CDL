# Research & Technical Decisions: 066-importar-atelie-parser

## 1. Diagnóstico do Formulário Atual (`ImportView.vue`)

- **Estrutura Existente**:
  - Formulário vertical sequencial dividido em passos numerados (Passo 1: Livro e trecho; Passo 2: Conferir e salvar).
  - Campos de Livro, Capítulo, Localização e Título ocupam altura vertical excessiva em grades completas.
  - O editor de texto possui uma barra de ferramentas estática (`MarkdownToolbar.vue`) fixa no topo do textarea.
  - A prévia das seções e dos avisos fica empilhada abaixo de toda a tela, exigindo scroll constante para ver o resultado do parsing.
- **Pontos Fortes a Preservar**:
  - `useImportDraft(api)` gerencia o ciclo de análise, salvamento, reanálise e dirty state.
  - Tratamento de promoção de capturas do Inbox (`promote_inbox_id`).
  - Atribuição de conteúdo não classificado com 1 clique (`assignUnassignedToSection`).
  - Respeito a `useUnsavedChanges` quando há modificações não salvas.
  - Tela de salvamento concluído (`state.saved`) com rotas diretas.

## 2. Padrão Arquitetural: Two-Pane Studio (Ateliê em Duas Colunas)

- **Distribuição Espacial**:
  - **Barra Superior Compacta**: 1 linha horizontal contendo Livro, Capítulo, Localização, Título e botão primário de Ação/Salvar.
  - **Área de Trabalho Principal (Split View)**:
    - Painel Esquerdo (~50% desktop): Editor da fonte bruta, contador de palavras e caracteres, botão manual de analisar e indicador de *stale*.
    - Painel Direito (~50% desktop): Cards estruturados das quatro seções semânticas (Resumo, Explicação, Conceitos, Referências) e card de conteúdo não classificado.
- **Alternância de Modos de Visualização (*View Mode Toggle*)**:
  - `split`: 50% / 50% (padrão em desktop).
  - `source`: 100% Editor (foco em digitação/leitura da fonte bruta).
  - `preview`: 100% Prévia (foco em conferência e refinamento das 4 seções).
  - Transição via CSS `transition: width 180ms cubic-bezier(0.16, 1, 0.3, 1)`.
- **Comportamento Responsivo (< 1024px)**:
  - Abas segmentadas no topo do ateliê: `[Texto da Fonte]` e `[Prévia Estruturada]`.

## 3. Barra de Ferramentas Flutuante Contextual

- **Mecânica de Exibição**:
  - Detecta seleção de texto no textarea via eventos `select`, `mouseup` e `keyup`.
  - Quando `selectionStart !== selectionEnd`, exibe a barra flutuante posicionada ergonomicamente sobre a área de seleção ou ancorada no topo do editor de forma não obstrutiva.
  - Oferece suporte a Negrito, Itálico, Título H3, Tabela, Código e Link.
  - Integra-se a atalhos de teclado universais: `Ctrl+B`, `Ctrl+I`, `Ctrl+K`.
  - Desaparece ao desmarcar o texto ou pressionar `Esc`.
  - Fallback acessível: pequenos atalhos/botões discretos no rodapé do editor para uso sem depender exclusivamente de seleção com mouse.

## 4. Performance, Debounce e Feedback Tátil

- **Pulso de Detecção Estrutural**:
  - Quando uma seção é reconhecida pelo parser, o card correspondente no preview emite uma animação de pulso luminoso:
    ```css
    @keyframes section-pulse {
      0% { box-shadow: 0 0 0 0 var(--color-accent); }
      70% { box-shadow: 0 0 0 6px transparent; }
      100% { box-shadow: 0 0 0 0 transparent; }
    }
    ```
  - Respeita `prefers-reduced-motion: reduce` desativando a animação imediatamente.
- **Debounce de Parsing**:
  - Digitação no editor utiliza debounce de 300ms antes de sinalizar recálculo ou preview automático, prevenindo jank mesmo com fontes de mais de 2.000 palavras.

## 5. Imunidade Cromática e Acessibilidade

- Uso exclusivo de tokens dos 10 temas:
  `--color-surface`, `--color-page`, `--color-text`, `--color-text-muted`, `--color-border`, `--color-border-subtle`, `--color-accent`, `--color-accent-subtle`, `--color-accent-hover`, `--radius-card`, `--radius-sm`.
- Zero emojis no código e templates.
- Alvos de clique de no mínimo 44x44px em resoluções táteis.
