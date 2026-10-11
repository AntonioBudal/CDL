# Pesquisa e Decisões Técnicas: F0.8.06 — Amigos: Salão Literário e Círculos de Estudo

**Feature Branch**: `071-amigos-salao-literario`  
**Data**: 2026-10-11  
**Status**: Concluído (Fase 0 do Spec Kit)

---

## 1. Contexto e Objetivos da Pesquisa

A Feature F0.8.06 transforma a página `/amigos` em um **Salão Literário e Círculos de Estudo**, substituindo a lista cinzenta por uma experiência estética de ateliê e correspondência intelectual.

Para alcançar a elegância e fluidez desejadas, foram investigadas 5 decisões arquiteturais críticas:
1. Arquitetura do **Cartão de Identidade do Leitor (*Bookplate Card* / Ex-Líbris Digital)** permanente no topo.
2. Microinteração do **Selo de Cópia Confirmada** com transição fluida em exatamente 1200ms acelerada por GPU.
3. Integração com **Web Share API** (`navigator.share`) para compartilhamento móvel nativo com fallback gracioso.
4. Redesenho dos cartões sociais em "Cartas de Conexão Literária" com navegação por abas e contadores discretos.
5. Imunidade cromática total aos 10 temas visuais do Leitorum e banimento absoluto de emojis.

---

## 2. Decisões Técnicas

### Decisão 1: Bookplate Card — Ex-Líbris Digital Permanente no Topo

- **Decisão**: Implementar o componente dedicado `BookplateCard.vue` renderizado de forma permanente no topo da página `/amigos`, posicionado acima da barra de navegação de abas. O cartão reúne:
  - Avatar ou iniciais elegantes do leitor.
  - Nome de exibição e `@identificador`.
  - Bio literária ou nota de interesses (se preenchida em Ajustes de Perfil).
  - Pílula de contagem de conexões do círculo.
  - Botão de cópia rápida do `@identificador` com selo visual.
  - Botão de compartilhamento de perfil (com suporte nativo a dispositivos móveis).
- **Rationale**:
  - Na versão anterior, o identificador do leitor ficava escondido dentro do estado vazio da primeira aba, sumindo completamente assim que o usuário adicionava o primeiro amigo.
  - Posicionar o Bookplate Card no topo garante acesso permanente à identidade compartilhável do leitor em qualquer uma das 4 abas sociais.
- **Alternativas Consideradas**:
  - *Manter o identificador em um modal flutuante*: Rejeitado por acrescentar cliques desnecessários.
  - *Colocar o identificador em uma barra lateral fixa*: Rejeitado para preservar a largura útil de leitura em tablets e celulares.

---

### Decisão 2: Microinteração do Selo de Cópia com Duração de 1200ms

- **Decisão**: Ao clicar no botão de cópia do `@identificador`, acionar uma microinteração de selo/lacre literário (`.is-stamped`), aplicando leve pulso (`transform: scale(1.05)`) e esmaecimento suave em exatamente 1200ms através de `setTimeout` e transições CSS de `opacity` e `transform`.
- **Rationale**:
  - O feedback tradicional genérico ("Copiado!") é impessoal. O selo de confirmação literário evoca o carimbo de um Ex-Líbris ou lacre de carta, reforçando a ambiência do salão.
  - 1200ms é o intervalo ideal: perceptível e confirmatório para o usuário sem prender a interface ou atrasar novos cliques.
  - Respeito a `prefers-reduced-motion: reduce`: suprime o pulso de escala e opera apenas com transição de opacidade/texto instantâneo.
- **Alternativas Consideradas**:
  - *Toast flutuante global*: Rejeitado por poluir a tela com notificações distantes do ponto de ação do leitor.
  - *Feedback permanente até o próximo clique*: Rejeitado por deixar o botão com estado confuso.

---

### Decisão 3: Compartilhamento Móvel Nativo (Web Share API) com Fallback

- **Decisão**: Implementar detecção de suporte a `navigator.share`.
  - Se disponível (`typeof navigator.share === 'function'`): o botão "Compartilhar Perfil" aciona a folha nativa de compartilhamento do dispositivo móvel com texto de convite formatado e link para `/u/:username`.
  - Se indisponível (desktop clássico ou navegadores antigos): o botão executa a cópia do link público do perfil diretamente para a área de transferência com feedback visual correspondente.
- **Rationale**:
  - Em smartphones e tablets, a Web Share API permite enviar o perfil diretamente via aplicativos de mensagens ou redes com 1 toque, eliminando o atrito de colar links manualmente.
  - A garantia de fallback para clipboard assegura funcionamento uniforme em 100% dos navegadores.
- **Alternativas Consideradas**:
  - *Botoeira fixa de redes sociais de terceiros (WhatsApp, Twitter, etc.)*: Rejeitada por violar a premissa de aplicativo local focado em privacidade, sem rastreadores ou scripts externos.

---

### Decisão 4: Cartões de Conexão Literária e Navegação por Abas

- **Decisão**: Redesenhar a listagem de amigos, solicitações e leitores descobertos em cartões de ateliê com:
  - Tipografia editorial e alinhamento claro.
  - Data de início da conexão amigável e formatada em português.
  - Acesso direto à estante pública do leitor (`/u/:username`).
  - Botões de ação contextuais reutilizando `FriendActionButtons.vue` com dimensões mínimas de toque de $44 \times 44$px.
  - Barra de navegação com 4 abas semânticas (`Círculo de Leitura`, `Solicitações`, `Descobrir Leitores`, `Bloqueados`), com badges dinâmicos para convites pendentes e padrão WAI-ARIA `role="tablist"` / `role="tab"`.
- **Rationale**:
  - Confere identidade de clube literário à comunidade do Leitorum.
  - Permite processar convites recebidos com agilidade e clareza.

---

### Decisão 5: Imunidade Cromática aos 10 Temas e Zero Emojis

- **Decisão**: Todos os componentes sociais (`BookplateCard.vue`, `FriendsView.vue`, `FriendActionButtons.vue`) consomem exclusivamente variáveis CSS semânticas:
  - Fundo: `var(--color-surface)` e `var(--color-bg)`
  - Bordas: `var(--color-border)` e `var(--color-border-subtle)`
  - Textos: `var(--color-text)` e `var(--color-text-muted)`
  - Destaques: `var(--color-primary)` e `var(--color-accent)`
  - Banimento absoluto de emojis em títulos, badges ou botões; uso exclusivo de ícones SVG semânticos (`<Icon name="..." />`).
- **Rationale**:
  - Mantém harmonia em todos os 10 temas visuais (incluindo E-Ink e temas escuros).
  - Cumpre rigorosamente a política de design editorial do Leitorum.

---

## 3. Resumo de Resoluções

| Tópico | Status | Resolução |
|---|---|---|
| Cartão de Identidade do Leitor | Resolvido | Componente `BookplateCard.vue` fixo no topo com `@identificador`, avatar e bio. |
| Selo de Cópia | Resolvido | Microinteração acelerada por GPU de 1200ms com feedback de selo/lacre literário. |
| Compartilhamento Móvel | Resolvido | `navigator.share` com fallback automático para cópia de link na área de transferência. |
| Cartões de Conexão | Resolvido | Cartas editoriais com link para `/u/:username`, data de conexão e botões contextuais. |
| Navegação Social | Resolvido | 4 abas segmentadas com badges dinâmicos e WAI-ARIA `role="tablist"`. |
| Temas & Ícones | Resolvido | 100% tokens CSS semânticos, zero hexadecimais rígidos e zero emojis. |
