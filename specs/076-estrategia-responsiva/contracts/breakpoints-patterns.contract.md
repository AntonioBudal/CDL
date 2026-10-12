# Contrato de Breakpoints, Padrões Táteis e Rastreabilidade

**Feature**: `076-estrategia-responsiva`  
**Escopo**: Definição normativa das faixas de viewport, regras de corte, ergonomia de toque e matriz de rastreabilidade (Features 076 a 081).

---

## 1. Faixas de Viewport e Fronteiras Canônicas

Para eliminar a divergência histórica de 15 breakpoints identificada no diagnóstico (P-11), o projeto adota estritamente três faixas canônicas, espelhando os limites já utilizados em JavaScript (`useSplitPanes.ts`):

| Faixa Canônica | Expressão CSS Normativa | Dispositivos e Contexto | Comportamento do Shell e Painéis |
|---|---|---|---|
| **Móvel** | `@media (max-width: 767px)` | Smartphones em modo retrato e telas compactas. | Barra inferior fixa (5 alvos); header minimalista; visualizações simplificadas/outline. |
| **Tablet** | `@media (min-width: 768px) and (max-width: 1023px)` | Tablets em modo retrato e telas intermediárias. | `SplitLayout` opera com painéis em gaveta (drawer); Canvas completo com alças táteis e pinch. |
| **Desktop** | `@media (min-width: 1024px)` | Desktops, notebooks e tablets em modo paisagem amplo. | `SplitLayout` opera em modo dividido simultâneo; barras laterais e cabeçalho completo. |

### Regra de Fronteira 767px vs 768px
- O limiar móvel superior é estritamente **`767px`** (`max-width: 767px`).
- O limiar tablet inferior é estritamente **`768px`** (`min-width: 768px`).
- **Política de Migração**: A unificação para `767px` ocorre pontualmente nos arquivos tocados pelas features 077 a 079, sem refatorações globais em massa que causem ruído desnecessário no git.

### Ajustes Internos por Conteúdo
- Permitidos breakpoints auxiliares contidos (`@media (max-width: 640px)` ou `@media (max-width: 480px)`) apenas quando justificados pela densidade interna de formulários ou toolbars, desde que não conflitem com as faixas canônicas do shell.

---

## 2. Container Queries no Palco de Estudos

As visualizações de estudos (`StudyGridView`, `StudyListView`, `StudyTreeView`, `StudyMapView`, `StudyCanvasView`) vivem dentro de `SplitPane#main`, cujo espaço físico é reduzido pela abertura de painéis laterais mesmo em telas desktop amplas (P-12).

### Diretriz Técnica
- O container pai do palco (`.workspace-main-panel` ou container de `SplitPane#main`) deve declarar:
  ```css
  container-type: inline-size;
  container-name: study-stage;
  ```
- Ajustes de densidade de cards e colunas devem utilizar `@container study-stage (max-width: ...)` prioritariamente a `@media (max-width: ...)`.

---

## 3. Padrões Táteis e Ergonomia Móvel

### 3.1 Detecção de Toque e Alvos Mínimos
- **Detecção de Aparelhos de Toque**: Utilizar `@media (pointer: coarse)` para expandir alças de redimensionamento e espaçamentos táteis.
- **Prevenção de Hover Congelado (P-18)**: Toda transformação de elevação ou microinteração aplicada a `:hover` deve ser envelopada em:
  ```css
  @media (hover: hover) and (pointer: fine) {
    .elemento:hover {
      transform: translateY(-2px);
    }
  }
  ```
- **Alvo Tátil Mínimo**: Todos os botões, links navegacionais e gatilhos de menu devem garantir área de toque mínima de **$44 \times 44\text{ px}$** no mobile.

---

## 4. Padrões de Componentes de Interação

### 4.1 Barra Inferior Móvel (`MobileTabBar`)
- Fixada no rodapé inferior via `position: fixed; bottom: 0; left: 0; right: 0`.
- Altura útil de $56\text{ px}$ acrescida de `padding-bottom: env(safe-area-inset-bottom)`.
- 5 colunas distribuídas simetricamente: Início, Livros, Destaques, Revisão e gatilho "Mais".
- Disponibiliza token CSS `--mobile-nav-offset: calc(56px + env(safe-area-inset-bottom, 0px))` para que elementos flutuantes (toasts, FABs, barras de lote) não sobreponham a barra.

### 4.2 Gaveta Móvel "Mais" (`MobileMoreMenu`)
- Acionada pelo 5º item da barra inferior.
- Deve cobrir 100% das rotas secundárias do sistema com badges reativos: Inbox, Amigos, Ajustes, Lixeira e Importar.

### 4.3 Menus Contextuais por Linha
- Em telas compactas, ações secundárias dispersas (ex.: lixeira, abrir, promover) agrupam-se em menu vertical acionado pelo botão de reticências ("⋯"), preservando a largura útil para o título.

---

## 5. Decisão de Infraestrutura de Teste (FR-007)

- **Decisão Ratificada**: Manter a suíte estática de alta velocidade no `node --test` complementada por protocolo/roteiro manual de validação nas features 076 a 080.
- A introdução de ferramentas de automação de navegador (ex.: Playwright/Puppeteer) e downloads de binários pesados de navegadores fica postergada para avaliação na **Feature 081**.

---

## 6. Matriz de Rastreabilidade Problema $\to$ Feature $\to$ Critério de Aceite

| ID | Tela / Componente | Gravidade | Feature de Destino | Tarefa Preliminar | Critério de Aceitação Principal | Método de Verificação |
|---|---|---|:---:|---|---|---|
| **P-01** | Shell / Navegação | Crítica | **077** | NAV-01 / NAV-02 | Em `<768px`, barra inferior ativa com 5 alvos $\ge 44\text{px}$; header sem abas; sem rolagem lateral involuntária. | Contrato template $\leftrightarrow$ CSS + roteiro 320–767px |
| **P-02** | Testes de Navegação | Alta | **077** | NAV-03 | Teste unitário falha caso a classe CSS estilizada não exista fisicamente no template do componente. | `node --test` |
| **P-03** | `ShareModal` | Alta | **077** | NAV-07 | Modal com CSS próprio usando tokens canônicos, funcional em qualquer resolução sem classes Tailwind. | Inspeção estática + teste visual |
| **P-04** | Map View (Pan/Zoom) | Alta | **080** | VIS-01 / VIS-02 | Toque com um dedo arrasta (pan) e dois dedos dão zoom (pinch) no panorama; visualização padrão é lista semântica. | Unitário + roteiro de toque |
| **P-05** | Map View (Arestas) | Média | **080** | VIS-03 | Edição e exclusão de relações executadas através de itens da lista tátil sem depender de badges SVG diminutos. | Roteiro com dados sintéticos |
| **P-06** | Canvas View (Toque) | Alta | **080** | VIS-04 / VIS-05 | No celular, página rola normalmente sem bloqueio por `touch-action: none`; alternativa em lista por moldura funcional. | Roteiro móvel e em tablet |
| **P-07** | Canvas Toolbar | Média | **080** | VIS-06 | Toolbar em tablet compacta ferramentas secundárias em menu suspenso. | Roteiro em tablet |
| **P-08** | Tree View (Toque) | Média | **080** | VIS-07 | Alça de arrasto oculta em `pointer: coarse`; reordenação executada pelo menu contextual tátil. | `study-tree*.test.mjs` + roteiro |
| **P-09** | Notificações | Média | **077** | NAV-05 | Painel de notificações ocupa largura total em viewports $\le 430\text{px}$, sem estourar margem esquerda. | Roteiro 320–430px |
| **P-10** | Elementos Fixos | Média | **077** | NAV-04 | Toasts, barra da lixeira e FAB de ajustes utilizam `--mobile-nav-offset`, sem sobreposição com a barra inferior. | Roteiro em smartphone |
| **P-11** | Breakpoints | Média | **076 $\to$ 077–080** | Contrato 076 | Padronização dos limites para 767px / 768px nos componentes modificados. | Verificação de código |
| **P-12** | Palco em SplitLayout | Média | **078 / 080** | CNT-06 / VIS-02 | Palco adapta-se via container query mesmo com painéis laterais abertos em desktop intermediário. | Roteiro com painéis abertos |
| **P-13** | CSS Morto no Shell | Baixa | **077** | NAV-06 | Remoção de estilos scoped legados de `App.vue` sem alteração no visual do desktop. | Captura de regressão em 1440px |
| **P-14** | Admin Users Table | Média | **078** | CNT-03 | Administração de usuários por cards em telas $<768\text{px}$ com ações de bloqueio por toque. | `admin.test.mjs` + roteiro |
| **P-15** | Grids de 280px | Baixa | **078** | CNT-04 | Grids com `minmax(min(280px, 100%), 1fr)` não causam overflow lateral em 320px. | Linha de base 320px |
| **P-16** | Modais com Formulário | Média | **078** | CNT-05 | Modais utilizam `dvh` e mantêm botões de ação acessíveis com teclado virtual ativo. | Roteiro com teclado emulado |
| **P-17** | BookView no Mobile | Média | **078** | CNT-01 / CNT-02 | Primeiro acesso no celular exibe estudos diretamente, mantendo gaveta de capítulos fechada por padrão. | `split-panes.test.mjs` + roteiro |
| **P-18** | Efeito Hover Preso | Baixa | **078** | CNT-07 | Efeitos `:hover` com `transform` encapsulados em `@media (hover: hover) and (pointer: fine)`. | Roteiro com toque emulado |
| **P-19** | Infraestrutura Testes | Info | **076 $\to$ 081** | REG-01 | Decisão FR-007 documentada; reavaliação de automação programada para a Feature 081. | Relatório final |
| **P-20** | Rótulos e Linhas Texto+Botão | Média | **079** | BTN-01 | Rótulos dos Tipos A e D em linha única; linhas do Tipo E empilhadas quando < 12ch; sem overflow. | `feature-079*.test.mjs` + inspeção |

