# Technical Research: Ajustes — Ateliê de Preferências e Leitura Viva

**Feature**: `072-ajustes-atelie-preferencias`
**Date**: 2026-10-11
**Status**: Concluído

## 1. Pesquisa de Padrões e Decisões Técnicas

### 1.1 Cartões de Pré-Visualização de Temas (Inspirados no Windows 11)

- **Contexto**: O sistema atualmente apresenta uma lista suspensa (`<select>`) simples para os 10 temas canônicos. O usuário solicitou explicitamente: *"melhora das previsualizações tipo no windows 11 que tem previews dos temas com boxes mostrando as cores, não apeans um nome crie um box de prévisualização para cada tema com as cores do tema"*.
- **Decisão**: Criar o componente `ThemePreviewCard.vue` e organizar a seleção em `ThemePreviewGrid.vue` (ou integrados em `ThemePreviewGrid.vue`).
  - Cada cartão conterá uma miniatura visual composta por:
    1. Uma base retangular colorida com a cor de fundo do tema (`--color-page`).
    2. Uma camada interna simulando uma janela/superfície do caderno (`--color-surface`).
    3. Linhas tipográficas sintéticas na cor do texto (`--color-text`).
    4. Um chip/ponto de destaque na cor de acento do tema (`--color-accent`).
    5. O nome canônico do tema posicionado de forma legível.
  - No estado ativo, o cartão recebe um anel de destaque (`outline` ou borda reforçada com a cor de acento) e um indicador visual de seleção.
  - Para o tema `e-ink`, o box exibe a natureza estritamente monocromática (fundo `#FFFFFF`, superfície `#FFFFFF`, linhas `#000000` e borda `#000000`), sem cor colorida artificial.
- **Acessibilidade (WAI-ARIA)**:
  - O contêiner da grade terá `role="radiogroup"` com `aria-label="Seleção de temas visuais"`.
  - Cada cartão terá `role="radio"`, `aria-checked="true|false"`, `tabindex="0"` no selecionado e `-1` nos demais, com navegação fluida por teclas direcionais (`ArrowUp`, `ArrowDown`, `ArrowLeft`, `ArrowRight`, `Home`, `End`).
- **Alternativas consideradas**:
  - *Manter `<select>` e colocar um preview embaixo*: Rejeitado porque não oferece comparação visual simultânea e imediata de todos os temas.
  - *Color picker livre*: Rejeitado porque violaria o contrato constitucional dos 10 temas canônicos do Leitorum.

### 1.2 Layout Responsivo: Navegação Lateral Vertical e Bancada de Leitura Viva

- **Contexto**: A tela de ajustes possui 5 grupos densos ("Perfil & Privacidade", "Aparência", "Leitura", "Sistema", "Conta & Dispositivos") anteriormente organizados em abas horizontais no topo. A amostra ao vivo ficava espremida em uma barra lateral estática.
- **Decisão**:
  - **Desktop ($\ge 1024\text{px}$)**:
    - Coluna de navegação vertical à esquerda (`.settings-nav`) com os 5 grupos de opções identificados por ícones vetoriais semânticos e títulos legíveis.
    - Coluna central de formulários (`.settings-main`) onde o formulário da seção ativa é renderizado.
    - Coluna da direita fixa/persistente (`.settings-preview-col`) acomodando a bancada de leitura viva (`AppearancePreview.vue`).
  - **Tablet / Mobile ($< 1024\text{px}$)**:
    - Navegação superior compacta e deslizável ou menu retrátil.
    - O simulador de leitura converte-se em um painel inferior (*bottom sheet* retrátil / expansível) acionado por botão flutuante ergonômico, permitindo inspecionar a legibilidade em tela cheia móvel e recolher rapidamente para ajustar parâmetros.
- **Sincronização com URL**:
  - A aba ativa é sincronizada bidirecionalmente com `route.query.tab` (`/ajustes?tab=aparencia`), permitindo links diretos para cada seção e preservando a navegação de retorno do navegador (`history.replaceState` ou `router.replace`).

### 1.3 Bancada de Leitura Viva (Sincronia Imediata a 60 FPS)

- **Contexto**: O simulador deve refletir instantaneamente ajustes de fonte, tamanho percentual, alinhamento, espaçamento e temas.
- **Decisão**:
  - `AppearancePreview.vue` recebe `preferences` reativo e mapeia estilos em escopo local com variáveis CSS:
    - `--reader-font-size: ${(preferences['reader-size'] || 100)}%`
    - Tipografia literária aplicada via classe e família do catálogo `cadernoFontCatalog`.
    - Alinhamento de parágrafo (`text-align: left | justify`).
  - O texto fictício pré-definido (Machado de Assis, Guimarães Rosa) garante conformidade total com a Constituição (zero leitura do acervo real do usuário).

### 1.4 Curadoria de Avatar e Preservação de Segurança

- **Contexto**: Ajustes de perfil exigem atualização segura de avatar e dados de conta.
- **Decisão**:
  - Validação estrita no frontend para imagens: formatos `image/png`, `image/jpeg`, `image/webp` com limite rigoroso de 2MB.
  - Exibição de prévia recortada redonda/quadrada suavizada antes do envio.
  - Preservação intacta de todas as rotas e métodos de API existentes:
    - `POST /api/profile` (ou endpoints já configurados)
    - Gestão de sessões ativas e revogação
    - Troca de senha autenticada
    - Diagnóstico de persistência e backup de dados locais

## 2. Matriz dos 10 Temas Canônicos para a Grade de Pré-Visualização

| Tema | ID | Fundo (`--color-page`) | Superfície (`--color-surface`) | Texto (`--color-text`) | Acento (`--color-accent`) | Esquema |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Papel Fosco** | `papel-fosco` | `#f5f5f5` | `#ffffff` | `#333333` | `#475569` | Claro |
| **Noite Suave** | `noite-suave` | `#1e1e24` | `#26262e` | `#d4d4d4` | `#64748b` | Escuro |
| **Cinza Neutro** | `cinza-neutro` | `#e8e8e8` | `#f0f0f0` | `#2b2b2b` | `#52525b` | Claro |
| **Grafite** | `grafite` | `#222222` | `#2a2a2a` | `#cccccc` | `#78716c` | Escuro |
| **Monocromático** | `monocromatico`| `#ffffff` | `#f8fafc` | `#111111` | `#111111` | Claro |
| **Sépia** | `pergaminho` | `#E7CCA0` | `#F2DDB6` | `#35200F` | `#873018` | Claro |
| **E-Ink** | `e-ink` | `#FFFFFF` | `#FFFFFF` | `#000000` | `#000000` | E-Ink |
| **Solarized** | `solario` | `#FDF6E3` | `#EEE8D5` | `#3F5962` | `#00686D` | Claro |
| **Nord** | `fiorde` | `#2E3440` | `#3B4252` | `#ECEFF4` | `#98D0E0` | Escuro |
| **Cyber** | `voltagem` | `#181820` | `#22222E` | `#ECEAF4` | `#F6FF00` | Escuro |

## 3. Conclusão da Pesquisa

Todas as decisões técnicas respeitam integralmente os pilares de acessibilidade, performance, ausência de emojis e blindagem de dados do projeto. Não restam dúvidas ou marcadores de clarificação abertos.
