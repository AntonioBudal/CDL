# Technical Research: F0.6.3 — Leitura Ativa

**Feature**: [spec.md](spec.md) | **Date**: 2026-09-27

---

## 1. Contexto e Desafios de Engenharia

A feature **F0.6.3 — Leitura Ativa** visa transformar passagens de um fichamento em interações dinâmicas de retenção ativa (*active recall*), **sem** criar uma tela paralela ou isolada de "flashcards".

### Principais Desafios:
1. **Preservação Soberana do Texto**: A experiência deve acontecer no próprio fluxo do estudo (nas 4 abas canônicas: Resumo, Explicação, Conceitos, Referências).
2. **Efemeridade da Sessão de Revisão**: Revelar ou ocultar trechos durante a sessão não deve alterar o banco de dados nem disparar requisições de rede a cada interação.
3. **Desempenho Instantâneo (< 50ms)**: Alternar oclusões individuais ou em massa ("Ocultar todos" / "Revelar todos") não deve recriar árvores DOM completas nem provocar saltos visuais (*layout shift*).
4. **Modo Somente Leitura**: Leitores convidados devem poder revisar estudos compartilhados com a mesma fluidez do proprietário.

---

## 2. Decisões Arquiteturais e Justificativas

### Decisão 1: Gestão de Estado da Sessão via Composable Efêmero (`useActiveReadingSession.ts`)
- **Escolha**: Criar o composable reativo `useActiveReadingSession.ts` no frontend Vue 3.
- **Rationale**:
  - A sessão de leitura ativa é uma prática cognitiva em tempo real. Salvar no SQLite cada clique de revelar/ocultar causaria tráfego de rede desnecessário, lentidão e concorrência indevida.
  - Sendo gerenciado na memória reativa da página, o estado funciona perfeitamente para usuários anônimos ou convidados (`canEdit = false`) em estudos compartilhados.
- **Alternativas Consideradas**:
  - *Persistir estado no SQLite a cada revelação*: Rejeitado por overhead de I/O, latência desnecessária e problemas de permissão para convidados.
  - *Persistir no localStorage*: Descartado para o estado pontual de cada trecho (deve ser resetado a cada sessão de estudo), mas pequenas preferências de atalho podem ser salvas.

---

### Decisão 2: Alternância em Massa e Pontual via Classes DOM Sem Recriação de Nós
- **Escolha**: Manipular diretamente o estado das classes CSS `.is-revealed` e atributos `aria-expanded` nos elementos existentes renderizados pelo `highlightRenderer.ts`, além de manter um mapa reativo no Vue.
- **Rationale**:
  - `applyHighlightsToDom` já isola os nós com atributos `data-highlight-id` e `data-kind`.
  - Alternar a classe `.is-revealed` e o texto dos botões (`[Revelar]` ↔ `[Ocultar]`, `[Ver resposta]` ↔ `[Esconder resposta]`) ocorre em menos de 10ms para dezenas de nós, sem recarregar Markdown nem disparar reflow pesado.
- **Alternativas Consideradas**:
  - *Re-renderizar o Markdown com novo HTML*: Descartado por ser destrutivo, perder posições de foco e causar cintilação visual na tela.

---

### Decisão 3: Barra de Ferramentas de Estudo Ativo (`ActiveReadingBar.vue`)
- **Escolha**: Criar um componente de barra contextual de leitura ativa posicionado estrategicamente entre o cabeçalho de ferramentas do leitor e o painel de abas do estudo.
- **Componentes da Barra**:
  1. **Status e Progresso**: Badge discreto com a contagem: `X de Y revisados (Z%)` com barra de progresso visual fina.
  2. **Ações em Lote**: Botões `Ocultar todos` e `Revelar todos`.
  3. **Navegação Sequencial**: Botões `Anterior` e `Próximo` com rolagem suave centrada (`scrollIntoView({ behavior: 'smooth', block: 'center' })`) e aplicação de anel de foco acessível.
  4. **Fechar Modo**: Botão para encerrar a sessão de leitura ativa e voltar à leitura contínua.
- **Alternativas Consideradas**:
  - *Modal flutuante fixo no centro*: Rejeitado por cobrir o texto que o leitor precisa ler.
  - *Toolbar inferior fixa no Desktop*: Menos ergonômica que mantê-la no topo do leitor onde os controles de leitura já se concentram.

---

### Decisão 4: Ergonomia Móvel e Navegação por Teclado
- **Escolha**:
  - **Teclado**: Atalhos práticos quando a barra estiver ativa: tecla `J` ou `Seta para Baixo` (Próximo), tecla `K` ou `Seta para Cima` (Anterior), barra de `Espaço` ou `Enter` no botão do trecho para alternar revelação. Tecla `Escape` encerra o modo ativo.
  - **Mobile (`<= 768px`)**: Alvos de toque de no mínimo $44 \times 44\text{px}$, layout compacto com quebra em linha dupla ou barra ancorada na base sem cobrir o parágrafo em leitura.
  - **Acessibilidade**: Atributos `aria-live="polite"` no contador de progresso, `aria-expanded` nos botões de revelação e respeito irrestrito a `prefers-reduced-motion`.

---

## 3. Resumo das Decisões

| Tópico | Decisão | Rationale |
| :--- | :--- | :--- |
| **Camada de Estado** | Composable `useActiveReadingSession.ts` | Estado reativo efêmero, zero chamadas de rede no treino, suporte total a convidados. |
| **Manipulação Visual** | Classes CSS `.is-revealed` + eventos delegados | Performance instantânea (< 10ms) sem recriação de nós DOM. |
| **Interface do Leitor** | Componente `ActiveReadingBar.vue` | Barra integrada, limpa, visível durante o estudo ativo e recolhível. |
| **Navegação** | Rolagem suave centrada + teclas `J`/`K` | Fluidez em estudos extensos sem perda de contexto de leitura. |
| **Acessibilidade** | WCAG AA + 44px mobile + tema E-Ink | Inclusão de leitores móveis e preservação de alto contraste. |
