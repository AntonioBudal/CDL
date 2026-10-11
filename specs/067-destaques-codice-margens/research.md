# Technical Research & Architectural Decisions: F0.8.02 — Destaques: Códice e Margens Vivas

**Feature**: `067-destaques-codice-margens` | **Date**: 2026-10-11 | **Status**: Complete

---

## 1. Contexto e Diagnóstico do Estado Atual

A página de Destaques e Anotações (`/destaques` em `HighlightsLibraryView.vue`) consome o endpoint `/api/highlights/library` e renderiza componentes dedicados:
- `HighlightCard.vue`: Exibe o destaque como um cartão de dados padrão com botões de ação e edição rápida de notas.
- `HighlightFilterToolbar.vue`: Exibe busca textual, seletor de livros, seletor de tipos, seletor de visualização (Recentes vs Por Obra) e botões redondos de cores.

### Deficiências Identificadas no Diagnóstico Técnico:
1. **Quebra de Imunidade Cromática e Banners de Erro Rígidos:** O tratamento de erro em `HighlightsLibraryView.vue` utiliza cores hexadecimais estáticas (`background-color: #fef2f2; border: 1px solid #fecaca; color: #991b1b;`), quebrando a harmonia visual em todos os 10 temas nativos (especialmente temas escuros como Obsidian, Meia-noite e Café).
2. **Cores como "Bolinhas Estáticas" sem Significado Cognitivo:** Em `HighlightFilterToolbar.vue`, as cores são definidas com valores hexadecimais rígidos (`#eab308`, `#22c55e`, etc.) e rótulos genéricos ("Amarelo", "Verde", etc.), sem refletir as intenções reflexivas de estudo do leitor.
3. **Ausência de Tipografia Editorial Diferenciada:** No `HighlightCard.vue`, o trecho citado da obra e a anotação pessoal do leitor competem no mesmo plano estilístico sem tratamento de aspas clássicas ou diferenciação entre a voz do autor e a reflexão do estudante.
4. **Falta de Cópia Formatada para Produção Externa:** O leitor precisa selecionar manualmente o texto do cartão caso deseje citar o trecho em um ensaio ou artigo, sem suporte a referências ABNT ou blocos Markdown formatados.

---

## 2. Decisões Técnicas e Arquiteturais

### Decisão 1: Arquitetura Visual e Tipográfica da Ficha Literária (*Commonplace Card*)
- **O que foi escolhido:** Reformulação do componente `HighlightCard.vue` como uma "Ficha Literária" de estudo:
  - **Citação do Trecho:** Tipografia serifada/humanista destacada (`font-serif` / `--font-serif`), tamanho de fonte ligeiramente aumentado (`1.05rem` / `17px`), entrelinha confortável (`line-height: 1.6`), aspas editoriais integradas e borda lateral esquerda tonal semitransparente indicando a categoria do grifo sem poluição visual.
  - **Bloco de Anotação do Leitor:** Bloco subordinado visualmente destacado com fundo translúcido suave (`--bg-subtle` / `--color-surface-soft`), tipografia sem serifa limpa (`--font-sans`), ícone vetorial de pena/anotação (`edit-3` do catálogo `Icon.vue`) e borda suave.
  - **Rodapé de Metadados Bibliográficos:** Título da obra com link direto de navegação, capítulo associado, localização/página (quando informada) e data de criação em formato pt-BR.
- **Alternativas consideradas:**
  - Manter cartão genérico adicionando apenas tags: Rejeitado porque não atende ao objetivo do Roadmap 0.8 de transformar o Leitorum em ambiente imersivo de estudo e leitura profunda.
  - Usar fundo colorido chapado para cada cor de grifo: Rejeitado por cansar a vista e quebrar o contraste em temas escuros e alto contraste.

### Decisão 2: Mapeamento Semântico Intelectual das Cores de Grifo
- **O que foi escolhido:** Mapeamento explícito das 5 cores canônicas do sistema em intenções intelectuais de estudo:
  - `yellow`: **Ideia Central** (destaque fundamental da tese do autor)
  - `green`: **Citação-chave** (passagem memorável para referência futura)
  - `blue`: **Dúvida** (ponto obscuro ou questão a aprofundar)
  - `pink`: **Refutação** (argumento divergente ou contraposição)
  - `purple`: **Síntese** (resumo ou conclusão conceitual)
- **Implementação:**
  - Em `HighlightFilterToolbar.vue`, os botões de filtro exibem pílulas com o indicador visual de cor associado ao rótulo textual legível e contador de ocorrências.
  - Atributos `aria-label` descritivos: `aria-label="Filtrar por destaques em amarelo (Ideia Central) - {count} itens"`.
  - Remoção de todos os códigos hexadecimais estáticos: consumo estrito das classes e variáveis de cor semânticas (`--color-highlight-*` / tokens de tema).
- **Alternativas consideradas:**
  - Criar tabela de categorias configurável no banco de dados: Rejeitada para a Feature 02 para evitar migrações de schema e manter conformidade estrita com a Constituição do Projeto (reutilização do modelo existente sem alteração de banco).

### Decisão 3: Mecanismo de Cópia de Citação em Múltiplos Formatos com Microfeedback Tátil
- **O que foi escolhido:** Menu contextual compacto / botão de cópia rápida no cabeçalho de cada ficha literária:
  - **Formato ABNT / Acadêmico:**
    ```text
    "Passagem citada..." (AUTOR, Título do Livro, cap. Capítulo, p. Localização).
    ```
  - **Formato Markdown:**
    ```markdown
    > Passagem citada...
    >
    > — **Título do Livro**, Capítulo (p. Localização)
    ```
  - **Microfeedback Tátil:** Ao acionar a cópia via `navigator.clipboard.writeText`:
    1. O ícone do botão de cópia transiciona de `copy` para `check` com animação suave de 150ms.
    2. Disparo do toast flutuante (utilizando o composable `useFloatingToast.ts` já consolidado no frontend) exibindo `"Copiado para a área de transferência"` durante exatamente 1500ms.
    3. Fallback defensivo com seleção textual assistida caso o navegador bloqueie a Clipboard API em contextos sem foco.
- **Alternativas consideradas:**
  - Copiar apenas o texto puro sem referência: Rejeitado porque obriga o usuário a copiar o título do livro e capítulo manualmente em outro passo.

### Decisão 4: Expansão Suave de Contexto de Passagens Longas e Política Cinética
- **O que foi escolhido:**
  - Passagens com mais de 260 caracteres exibem truncamento defensivo inicial acompanhado de botão acessível "Expandir citação" / "Ver menos".
  - Transição de abertura suave com limite de duração $\le 180$ms acelerada por GPU (`opacity` e `transform`), sem solavancos de rolagem (*layout shifts*).
  - Respeito universal à preferência `prefers-reduced-motion: reduce`: transição instantânea (0.01ms).

### Decisão 5: Estado de Erro Acolhedor Integrado aos 10 Temas e Recuperação por Teclado
- **O que foi escolhido:** Substituição do bloco estático `.notice-error` por um componente integrado de estado de erro:
  - Fundo neutro suave (`--bg-surface`), borda sutil (`--border-subtle`), ícone de aviso acolhedor (`alert-circle`), mensagem em tom construtivo em português e botão "Tentar novamente" com classe de botão secundário do tema (`.btn-secondary`).
  - Total ausência de classes utilitárias ou regras CSS com tons vermelhos arbitrários (`#fef2f2`, `#991b1b`).
  - Foco gerenciável com anel de foco semântico (`--ring-focus`) e suporte pleno a acionamento via `Enter` e `Espaço`.

### Decisão 6: Acessibilidade Semântica (WCAG 2.1 AA) e Suporte a Leitores de Tela
- **O que foi escolhido:**
  - Alvos de toque em telas móveis e desktop preservando o mínimo de $44 \times 44$px.
  - Regiões semânticas com `aria-live="polite"` para anúncio de filtros aplicados e contagem total de itens.
  - Atributos `aria-expanded` nos botões de expansão de contexto e menus de cópia.
  - Foco cíclico defensivo em caixas de confirmação de exclusão.

### Decisão 7: Estratégia de Testes Automatizados e Preservação de Dados
- **O que foi escolhido:**
  - Garantir execução intacta dos 420 testes de backend (`pytest`) e 381+ testes de frontend (`npm test`).
  - Adição de testes automatizados específicos em `frontend/tests/`:
    - `highlight_card_editorial.test.mjs`: Validação de renderização da ficha literária, diferenciação de citação vs anotação e truncamento.
    - `highlight_filter_semantic.test.mjs`: Validação das categorias semânticas de cor, acessibilidade (`aria-label`) e atualização de filtros.
    - `highlight_citation_copy.test.mjs`: Validação dos geradores de citação ABNT/Markdown e microfeedback temporário.
    - `highlights_error_retry.test.mjs`: Validação da substituição do estado de erro e comportamento de nova tentativa (*retry*).

---

## 3. Resumo de Resoluções

Todos os tópicos técnicos de planejamento foram deliberados e aprovados, com zero marcadores `[NEEDS CLARIFICATION]` pendentes.
