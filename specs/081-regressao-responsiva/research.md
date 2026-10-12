# Pesquisa e Decisões Técnicas: F0.8.15 — Bateria Completa de Regressão e Consolidação do Roadmap de Responsividade

**Feature**: `081-regressao-responsiva`  
**Data**: 2026-10-12  
**Status**: Concluído  

---

## 1. Decisão sobre Infraestrutura de Automação e Ferramentas de Teste

### Contexto
Na Feature 076 (FR-007), foi estabelecido que as features 076 a 080 utilizariam testes estáticos rápidos em `node --test` acompanhados por roteiro manual, postergando para a Feature 081 a decisão definitiva sobre a eventual introdução de dependências pesadas de automação de navegador (ex.: Playwright, Puppeteer ou Selenium).

### Avaliação de Alternativas
1. **Alternativa A: Instalação de Playwright / Puppeteer**:
   - *Vantagens*: Permite medição direta em runtime de `window.innerWidth`, `scrollWidth` e simulação automatizada de touch no headless browser.
   - *Desvantagens*: Exige o download de 300MB a 1GB de binários de navegadores headless; lenta inicialização no Windows; incompatibilidade frequente com ambientes restritos/offline; violação do espírito de agilidade do projeto e potencial atrito no CI/CD local.
2. **Alternativa B: Suíte Leve Integrada (Nativa `node --test` + Testes Contratuais + Protocolo de Homologação)** (Escolhida):
   - *Vantagens*: Zero dependências externas; execução sub-segundo; inspeção analítica profunda de templates Vue, tokens CSS, declarações de `@media`, `touch-action` e alvos táteis; complementada por protocolo reprodutível em navegador real e em smartphone físico via rede local/Tailscale.
   - *Alinhamento*: Plena aderência ao Princípio III (Fidelidade Tecnológica e Execução Local Ágil) da Constituição.

### Decisão
Manter a infraestrutura leve e canônica em **`node --test`**, criando uma suíte abrangente de teste-guarda (`tests/feature-081-responsive-regression.test.mjs`) que audita regras contratuais e integridade de código, acompanhada do protocolo de homologação para dispositivos físicos.

---

## 2. Auditoria e Mapeamento de Fechamento dos 19 Problemas (P-01 a P-19)

A tabela abaixo consolida a auditoria final dos problemas diagnosticados na auditoria estática inicial e suas respectivas soluções implementadas no roadmap:

| ID | Descrição do Problema | Gravidade | Feature Resolvedora | Componentes / Arquivos Tocados | Status Final |
|---|---|:---:|:---:|---|:---:|
| **P-01** | Shell e navegação móvel: sobreposição e header desconfigurado | Crítica | **077** | `App.vue`, `MobileTabBar.vue`, `MobileMoreMenu.vue` | **Resolvido** |
| **P-02** | Testes de navegação desconectados de classes físicas | Alta | **077** | `tests/feature-077-*.test.mjs`, `App.vue` | **Resolvido** |
| **P-03** | `ShareModal` com dependência residual de Tailwind | Alta | **077** | `ShareModal.vue` | **Resolvido** |
| **P-04** | Map View: pan e zoom inacessíveis no mobile | Alta | **080** | `StudyMapView.vue` | **Resolvido** |
| **P-05** | Map View: arestas e badges SVG diminutos para toque | Média | **080** | `StudyMapView.vue` (Lista Semântica) | **Resolvido** |
| **P-06** | Canvas View: `touch-action: none` bloqueando scroll da página | Alta | **080** | `StudyCanvasView.vue` (`touch-action: pan-y`) | **Resolvido** |
| **P-07** | Canvas Toolbar: excesso de botões sem quebra no tablet | Média | **080** | `CanvasToolbar.vue` (Menu compacto) | **Resolvido** |
| **P-08** | Tree View: alça de arrasto em telas de toque | Média | **080** | `StudyTreeNodeItem.vue` (`pointer: coarse`) | **Resolvido** |
| **P-09** | Notificações: estouro lateral em telas $\le 430\text{px}$ | Média | **077** | `NotificationsDropdown.vue` | **Resolvido** |
| **P-10** | Elementos fixos colidindo com barra inferior móvel | Média | **077 / 080** | `style.css` (`--mobile-nav-offset`), `HighlightsLibraryView.vue` | **Resolvido** |
| **P-11** | Divergência de 15 breakpoints no CSS | Média | **076 $\to$ 080** | Contrato 076, `style.css`, unificação 767px/768px | **Resolvido** |
| **P-12** | Palco estrangulado com SplitLayout aberto | Média | **078 / 080** | `style.css` (Container Query `@container study-stage`) | **Resolvido** |
| **P-13** | CSS morto e regras scoped residuais no shell | Baixa | **077** | `App.vue` | **Resolvido** |
| **P-14** | Admin View: tabela de usuários inacessível no celular | Média | **078** | `AdminView.vue` (Layout de cartões móveis) | **Resolvido** |
| **P-15** | Grids com coluna mínima de 280px estourando em 320px | Baixa | **078** | `style.css` (`minmax(min(280px, 100%), 1fr)`) | **Resolvido** |
| **P-16** | Modais com altura fixa estourando teclado virtual | Alta | **078** | Modais globais (`min(90dvh, 720px)`) | **Resolvido** |
| **P-17** | BookView: gaveta de capítulos aberta por padrão no mobile | Média | **078** | `BookView.vue` | **Resolvido** |
| **P-18** | Efeito hover travado/congelado em telas de toque | Baixa | **078** | `style.css` (`@media (hover: hover) and (pointer: fine)`) | **Resolvido** |
| **P-19** | Rótulos de botões quebrando em 2 linhas e desalinhando | Alta | **079** | `style.css`, botões de ação e linhas texto+botão | **Resolvido** |

---

## 3. Matriz de Resoluções e Dispositivos-Alvo

A homologação abrange três categorias canônicas:
- **Smartphones Compactos e Médios (320px a 430px)**:
  - 320px: Largura mínima extrema (iPhone SE 1ª geração).
  - 375px: Padrão iPhone SE 2ª/3ª geração e compactos Android.
  - 390px: Smartphones modernos (iPhone 12/13/14/15 padrão).
  - 430px: Smartphones amplos (iPhone 14/15/16 Pro Max, Galaxy Ultra).
- **Limiares de Fronteira Móvel/Tablet (767px e 768px)**:
  - 767px: Limite superior móvel (`max-width: 767px`).
  - 768px: Limite inferior tablet (`min-width: 768px`).
- **Desktops e Widescreen (1024px e 1440px)**:
  - 1024px: Tablet paisagem e laptops compactos.
  - 1440px: Monitores desktop padrão.
- **Orientação Paisagem Móvel (844×390px)**:
  - Comportamento de safe area e altura reduzida.
