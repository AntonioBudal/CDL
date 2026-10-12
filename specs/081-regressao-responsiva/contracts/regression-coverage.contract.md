# Contrato Normativo: Cobertura de Regressão e Integridade Responsiva

**Feature**: `081-regressao-responsiva`  
**Data**: 2026-10-12  
**Versão**: 1.0.0  
**Status**: Ratificado  

---

## 1. Escopo e Propósito

Este contrato normativo estabelece os requisitos técnicos e as cláusulas invioláveis para garantir a ausência de regressões no comportamento responsivo do **Caderno de Leitura**, consolidando o marco de responsividade (Features 076 a 081).

---

## 2. Cláusulas Normativas de Responsividade

### Cláusula 1: Contenção Absoluta de Transbordamento Horizontal
Em todas as 25 rotas mapeadas de `router/index.ts`, a largura de rolagem do documento e de qualquer contêiner principal DEVE ser estritamente igual à largura visível da viewport:
$$\text{scrollWidth} = \text{clientWidth}$$
É proibido qualquer elemento que provoque rolagem horizontal global na página em qualquer uma das 8 viewports normativas (320px, 375px, 390px, 430px, 767px, 768px, 1024px, 1440px) ou na orientação paisagem (844×390px).

### Cláusula 2: Dimensões Mínimas de Alvos Táteis (WCAG 2.1 - 2.5.5)
Em dispositivos móveis ou sob contexto de toque (`pointer: coarse` / telas $\le 767\text{px}$):
- Todos os botões interativos, links, ícones de ação e abas DEVEM possuir área mínima de toque de **$44 \times 44\text{ px}$** (física ou via preenchimento/padding de toque).
- Alças de arrasto de desktop (ex.: ordenação manual na árvore de estudos) DEVEM ser suprimidas sob `pointer: coarse` para não interferir na rolagem natural do usuário.

### Cláusula 3: Compensação Canônica da Barra Inferior Móvel
Qualquer elemento fixo, flutuante ou barra de rodapé exibido no celular (modais, toasts, botões flutuantes de ação, barra de ações em lote da lixeira) DEVE respeitar o espaçamento canônico definido pela variável CSS `--mobile-nav-offset`. Nenhum elemento pode ficar oculto sob a barra de navegação móvel.

### Cláusula 4: Unificação e Disciplina de Breakpoints
O sistema reconhece estritamente os seguintes limites canônicos de responsividade:
- **Mobile**: `@media (max-width: 767px)`
- **Tablet / Desktop**: `@media (min-width: 768px)`
- **Desktop Amplo**: `@media (min-width: 1024px)` e `@media (min-width: 1440px)`
- **Palco de Estudos**: `@container study-stage (max-width: ...)`

É expressamente proibida a reintrodução de breakpoints arbitrários ou fragmentados que colidam com esses limites.

### Cláusula 5: Gestos Táteis e Visualizações Especializadas
- **Mapa de Estudos (`StudyMapView.vue`)**: DEVE suportar gestos de pinça limitados a $[0.5, 2.5]$ e oferecer alternativa acessível via lista semântica de conexões.
- **Canvas de Estudos (`StudyCanvasView.vue`)**: DEVE utilizar `touch-action: pan-y` para permitir a rolagem suave da página móvel sem aprisionamento de gesto.
- **Árvore de Estudos (`StudyTreeView.vue`)**: DEVE comprimir indentação de ramos aninhados no celular e suprimir drag handles.

### Cláusula 6: Política de Testes e Fidelidade Operacional
- A automação de testes DEVE ser executada nativamente via `node --test` e `npm test`, mantendo tempo de execução inferior a 2 segundos para o ecossistema completo.
- Fica ratificada a dispensa de download de binários pesados de navegadores headless (Playwright/Puppeteer).
- Homologações dinâmicas de gestos e teclados virtuais DEVEM seguir o protocolo formal de dispositivos físicos sob rede local ou Tailscale.

---

## 3. Matriz de Cobertura das 25 Rotas e Viewports

| # | Rota (`router/index.ts`) | 320px | 375px | 390px | 430px | 767px | 768px | 1024px | 1440px | 844×390px |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 01 | `login` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 02 | `register` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 03 | `setup-owner` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 04 | `landing` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 05 | `about` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 06 | `dashboard` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 07 | `inbox` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 08 | `books` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 09 | `highlights` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 10 | `review` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 11 | `study-session` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 12 | `book` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 13 | `study` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 14 | `study-direct` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 15 | `study-edit` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 16 | `import` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 17 | `digitize-notebook` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 18 | `friends` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 19 | `connection` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 20 | `settings` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 21 | `trash` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 22 | `user-profile` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 23 | `admin` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 24 | `support` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 25 | `not-found` | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |

---

## 4. Requisitos da Suíte de Testes-Guarda

A suíte `tests/feature-081-responsive-regression.test.mjs` DEVE verificar programaticamente:
1. Mapeamento de 100% das rotas de `router/index.ts` contra este contrato.
2. Presença dos tokens `--mobile-nav-offset` em `style.css` e nos componentes de exibição flutuante.
3. Conformidade das regras de `touch-action: pan-y` em `StudyCanvasView.vue`.
4. Conformidade de desativação de drag handle em `StudyTreeNodeItem.vue` sob `pointer: coarse`.
5. Ausência de classes proibidas e dependências espúrias de Tailwind (verificando `ShareModal.vue`).
6. Presença de regras para evitar quebra em 2 linhas de botões de ação fixos.
7. Conformidade estrita de zero emojis nos arquivos auditados.
