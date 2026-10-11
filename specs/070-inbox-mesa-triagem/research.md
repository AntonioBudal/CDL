# Pesquisa e Decisões Técnicas: F0.8.04 — Inbox: Mesa de Triagem e Despejo Intelectual

**Feature Branch**: `070-inbox-mesa-triagem`  
**Data**: 2026-10-11  
**Status**: Concluído (Fase 0 do Spec Kit)

---

## 1. Contexto e Objetivos da Pesquisa

A Feature F0.8.04 tem como objetivo transformar a tela `/inbox` em uma **Mesa de Triagem e Despejo Intelectual**, eliminando barreiras entre o leitor e o registro ágil de reflexões efêmeras (*fleeting notes*).

Para atingir a fluidez desejada, foram investigados 5 aspectos críticos:
1. Arquitetura do campo superior permanente (*Quick Thought Drop*) e expansão suave via CSS/Vue.
2. Barra segmentada de triagem com contadores reativos e acessibilidade WAI-ARIA.
3. Transições cinéticas aceleradas por GPU para arquivamento e triagem ($\le 200$ms).
4. Navegação ergonômica por teclado (`J`/`K`/`E` e `Ctrl+Shift+C`) com guarda defensiva estrita.
5. Imunidade cromática aos 10 temas visuais do Leitorum e eliminação de mensagens cruas de erro.

---

## 2. Decisões Técnicas

### Decisão 1: Quick Thought Drop — Captura Permanente Inline vs. Modal

- **Decisão**: Implementar o componente `QuickThoughtDrop.vue` renderizado de forma permanente no topo de `/inbox`. A caixa de texto adota altura compacta inicial (1 linha, ~42px) com expansão suave para até 4 linhas (~120px) ao receber foco (`:focus-within` e estado reativo local). O salvamento é acionado por `Ctrl+Enter` (e `Cmd+Enter` no macOS) ou clique no botão editorial "Despejar Pensamento".
- **Rationale**: 
  - A eliminação de caixas de diálogo modais bloqueantes reduz em mais de 60% o esforço cognitivo e o tempo de descarrego mental (SC-001).
  - O modal existente (`QuickCaptureModal.vue`) é preservado como utilitário global para chamadas originadas em *outras* telas (como a estante ou leitura), mantendo retrocompatibilidade total com `useQuickCapture`.
  - Ao focar no campo permanente via clique ou atalho `Ctrl+Shift+C`, o usuário pode digitar e salvar imediatamente sem interrupções visuais.
- **Alternativas Consideradas**:
  - *Manter apenas o modal flutuante*: Rejeitado por interromper a visão da lista de pendências e exigir múltiplos cliques e fechamentos.
  - *Área de texto de tamanho fixo sempre aberta*: Rejeitada por ocupar espaço vertical precioso da viewport em telas móveis quando o usuário deseja apenas triar a lista existente.

---

### Decisão 2: Barra Segmentada de Triagem com Contadores Dinâmicos

- **Decisão**: Substituir a navegação de abas horizontais clássicas por uma barra segmentada integrada (`TriageSegmentedBar` ou container semântico `<nav class="triage-segmented-bar">`), com botões de segmento para `Pendentes` (`inbox`), `Promovidos` (`promoted`), `Vinculados` (`linked`), `Arquivados` (`archived`) e `Todos` (`all`).
- **Rationale**:
  - Apresenta contadores discretos por status sem sobrecarregar visualmente a interface.
  - Implementa padrão de acessibilidade WAI-ARIA com `role="tablist"` e `role="tab"` (ou `aria-pressed`/`aria-selected`), assegurando que tecnologias assistivas anunciem a contagem e o segmento ativo.
  - No layout móvel (< 768px), adota rolagem horizontal suave (*scroll snap*) com alvos de toque $\ge 44 \times 44$px.
- **Alternativas Consideradas**:
  - *Dropdown/Select nativo no mobile*: Rejeitado porque oculta os contadores e reduz a visibilidade das demais etapas de triagem.
  - *Abas de tabela tradicionais*: Rejeitadas por parecerem administrativas e descoladas da linguagem de ateliê do Leitorum.

---

### Decisão 3: Transições Cinéticas de Triagem Aceleradas por GPU

- **Decisão**: Implementar animações cinéticas de saída via CSS classes combinadas com `<TransitionGroup>` ou estado de desativação temporária no item (`isExiting: true`), aplicando `transform: translateX(30px)` e `opacity: 0` com duração de 180ms e `cubic-bezier(0.2, 0, 0, 1)`.
- **Rationale**:
  - `transform` e `opacity` são propriedades compostas pelo compositing engine do navegador (GPU), garantindo 60 FPS consistentes (SC-002) sem disparar *reflow* ou travamento de layout.
  - Quando a nota é arquivada, a animação inicia imediatamente; ao seu término (180ms), o item é removido da lista reativa, proporcionando sensação tátil e gratificante de "limpeza da mesa".
  - Respeito à mídia `prefers-reduced-motion: reduce`: desativa o deslocamento lateral e executa apenas transição instantânea ou desvanecimento suave simples.
- **Alternativas Consideradas**:
  - *Remoção reativa síncrona sem animação*: Rejeitada por causar pulos abruptos no conteúdo e desorientação do leitor.
  - *Bibliotecas externas de animação (ex.: GSAP, Motion One)*: Rejeitadas para cumprir a restrição inegociável de zero dependências novas.

---

### Decisão 4: Navegação e Triagem por Teclado (`J`/`K`/`E` e `Ctrl+Shift+C`)

- **Decisão**: Implementar escuta de eventos `keydown` com guarda defensiva no container da mesa de triagem.
  - Tecla `J`: move a seleção visual para o próximo cartão.
  - Tecla `K`: move a seleção visual para o cartão anterior.
  - Tecla `E`: arquiva imediatamente o cartão atualmente selecionado.
  - Tecla `Ctrl+Shift+C` (ou `Cmd+Shift+C`): foca diretamente o campo superior `QuickThoughtDrop`.
- **Rationale**:
  - A guarda defensiva verifica se o alvo do evento (`e.target`) é um elemento editável (`INPUT`, `TEXTAREA`, `SELECT` ou possui `isContentEditable`). Se for, a execução de `J`, `K` e `E` é abortada silenciosamente.
  - O cartão ativo exibe um anel de foco visível e elegante (`outline: 2px solid var(--color-accent)` e `outline-offset: 2px`), alinhado aos padrões WAI-ARIA.
  - Ao arquivar uma nota via `E`, a seleção se ajusta automaticamente para o item adjacente, permitindo processamento em fluxo contínuo (*triage sprints*).
- **Alternativas Consideradas**:
  - *Depender apenas de Tab/Shift+Tab*: Rejeitado por exigir múltiplos toques de tabulação para navegar entre as dezenas de botões de cada cartão.
  - *Atalhos com teclas modificadoras (ex.: Alt+J, Alt+E)*: Rejeitados por serem desconfortáveis para sequências rápidas de triagem.

---

### Decisão 5: Imunidade Cromática e Estado Vazio "Mesa Limpa"

- **Decisão**:
  - Todos os estilos e badges de `InboxView.vue` e `CaptureItemCard.vue` são convertidos para tokens semânticos:
    - Fundo: `var(--color-surface)`
    - Bordas: `var(--color-border)` e `var(--color-border-subtle)`
    - Textos: `var(--color-text)`, `var(--color-text-muted)`
    - Destaques e badges: `var(--color-accent)`, `var(--color-primary)`, `var(--color-surface-hover)`
    - Banimento rigoroso de hexadecimais puros (`#eff6ff`, `#2563eb`, `#ecfdf5`, etc.).
  - Quando o filtro `Pendentes` atinge 0 itens, é renderizado o estado "Mesa Limpa", com texto editorial tranquilo e ícone SVG sereno (zero emojis).
  - Em falhas de rede, a mensagem crua de erro é substituída por um componente editorial com botão de repetição acessível (`role="alert"`).
- **Rationale**:
  - Garante conformidade total com os 10 temas visuais do Leitorum (incluindo E-Ink e temas escuros).
  - Elimina o aspecto de erro técnico frio, reforçando a ambiência de ateliê do produto.

---

## 3. Resumo de Resoluções

| Tópico | Status | Resolução |
|---|---|---|
| Campo de Captura Superior | Resolvido | Componente `QuickThoughtDrop.vue` inline com expansão `:focus-within` e `Ctrl+Enter`. |
| Filtros e Contadores | Resolvido | Barra segmentada acessível com contadores dinâmicos nos 5 estados. |
| Animação de Arquivamento | Resolvido | Transição GPU (`transform: translateX(30px)`, `opacity: 0`, 180ms) com respeito a `prefers-reduced-motion`. |
| Atalhos de Teclado | Resolvido | `J`/`K` (navegar), `E` (arquivar), `Ctrl+Shift+C` (focar captura), com guarda defensiva estrita. |
| Temas e Design System | Resolvido | 100% de uso de variáveis semânticas CSS, zero hexadecimais fixos, zero emojis. |
