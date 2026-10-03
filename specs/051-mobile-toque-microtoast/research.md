# Research & Decisões Arquiteturais: Responsividade Mobile, Toque Nativo e Micro-Toast de Ferramentas

**Feature**: `051-mobile-toque-microtoast`  
**Data**: 2026-10-03  
**Status**: Concluído

---

## 1. Decisão 1: Detecção e Estabilidade de Seleção por Duplo Toque no Mobile

- **Contexto**: Em smartphones e tablets, selecionar uma palavra arrastando alças nativas gera frustração, pois micro-deslocamentos durante o toque cancelam a seleção ou disparam rolagem da página.
- **Decisão**:
  - Aprimorar `frontend/src/composables/useTextSelection.ts` com rastreamento leve de eventos de toque (`touchstart`, `touchend`):
    - Se dois eventos `touchend` ocorrerem no mesmo elemento dentro de um intervalo de 320ms e com deslocamento espacial inferior a 15px, um duplo toque é identificado.
    - Se a seleção nativa do navegador não tiver selecionado a palavra automaticamente, o composable localiza o nó de texto e o offset sob o toque (via `document.caretRangeFromPoint` / `document.caretPositionFromPoint`) e expande a seleção para os limites da palavra (respeitando pontuação e espaços).
  - Ignorar eventos `touchmove` com deslocamento superior a 10px (tratando-os como rolagem intencional, sem limpar seleções válidas preexistentes).
- **Rationale**: Proporciona a mesma agilidade do duplo clique desktop para usuários de tela sensível ao toque, sem depender exclusivamente da sensibilidade das alças nativas do sistema operacional móvel.
- **Alternativas Consideradas**:
  - *Depender apenas do evento `dblclick` nativo*: Rejeitado porque navegadores móveis (especialmente Safari no iOS) frequentemente interceptam o duplo toque para zoom de viewport (`double-tap to zoom`), suprimindo ou atrasando o `dblclick`.
  - *Biblioteca externa de gestos (Hammer.js / ZingTouch)*: Rejeitado por adicionar dependência obsoleta e pesada para uma interação simples de duplo toque.

---

## 2. Decisão 2: Barra Flutuante Mobile com Ícones Puros de 44x44px

- **Contexto**: A barra flutuante (`FloatingActionsToolbar.vue`) exibia ícones empilhados com textos longos ("Destacar", "Anotar", "Citação", "Ocultar", "Pergunta"), consumindo até 56px de altura e sobrecarregando a largura da tela em celulares pequenos (< 400px).
- **Decisão**:
  - Em viewports móveis (`isMobile === true` / `< 768px`), ocultar totalmente as legendas textuais das ferramentas na barra principal de ações (`.is-mobile .toolbar-btn .btn-text { display: none; }`).
  - Cada botão passa a exibir exclusivamente seu ícone de traço nítido (20x20px), centrado em um alvo tátil generoso de 44x44px com `justify-content: center` e `align-items: center`.
  - Preservar atributos `aria-label` e `title` descritivos em todos os botões para acessibilidade por leitores de tela.
  - Manter os textos visíveis no desktop (≥ 768px) para preservar a clareza da experiência em telas grandes.
- **Rationale**: Reduz a largura horizontal e a altura vertical da barra móvel em mais de 35%, eliminando quebras ou botões espremidos, cumprindo WCAG 2.1 Critério 2.5.5.
- **Alternativas Consideradas**:
  - *Encolher a fonte dos textos para 10px*: Rejeitado por prejudicar a legibilidade em telas de alta densidade de pixels.
  - *Carrossel com rolagem horizontal na barra*: Rejeitado por exigir gestos adicionais para alcançar ferramentas fundamentais como Oclusão e Pergunta.

---

## 3. Decisão 3: Notificação Flutuante (Micro-Toast) no Topo da Área de Leitura

- **Contexto**: Como a barra mobile não exibe texto nos botões, o leitor precisa de uma confirmação instantânea da ferramenta executada sem ruído.
- **Decisão (Alinhada com o Usuário - Q1: A e Q2: A)**:
  - Criar um mecanismo leve de micro-toast via composable `frontend/src/composables/useFloatingToast.ts` consumido em `StudyView.vue`:
  - **Posicionamento**: No topo da aba/área ativa de leitura de estudos (`position: fixed; top: 1rem; left: 50%; transform: translateX(-50%); z-index: 10001;`).
  - **Duração**: Exibição por exatamente **1.8 segundos** (1800ms) com animação suave de fade-out de 250ms.
  - **Interatividade**: `pointer-events: none` absoluto, garantindo que o micro-toast nunca intercepte toques do usuário na leitura.
  - **Substituição Atômica**: Se uma nova ferramenta for selecionada enquanto um toast estiver visível, o timer anterior é limpo imediatamente e o novo texto assume o lugar sem piscar ou acumular múltiplos balões.
- **Rationale**: Mantém o feedback na linha de visão do leitor, sem ser bloqueado pela mão do usuário na base da tela, oferecendo confirmação visual e tátil com atrito zero.

---

## 4. Decisão 4: Mensagens Canônicas dos Micro-Toasts por Ferramenta

| Ferramenta Acionada | Mensagem Exibida no Micro-Toast | Ícone SVG Associado |
|---|---|---|
| **Marca-texto (Amarelo/Verde/etc)** | `"Destaque aplicado"` | Ponto da cor selecionada |
| **Troca de Cor** | `"Cor do marca-texto alterada"` | Paleta de cores |
| **Anotar (abertura de prompt)** | `"Adicionar anotação"` | Ícone de lápis / anotação |
| **Anotar (salvamento)** | `"Anotação salva"` | Ícone de check / checkmark |
| **Citação (cópia)** | `"Citação copiada"` | Ícone de aspas |
| **Ocultar (Active Recall)** | `"Trecho ocultado para revisão"` | Ícone de olho riscado / oclusão |
| **Pergunta (abertura de prompt)**| `"Criar pergunta de fixação"` | Ícone de interrogação |
| **Pergunta (salvamento)** | `"Pergunta cadastrada"` | Ícone de interrogação / check |
