# Feature Specification: F0.9.01 — Arquitetura de Navegação Global e Shell Responsivo

**Feature Branch**: `082-navegacao-global-shell-responsivo`  
**Created**: 2026-10-20  
**Status**: Draft  
**Input**: User description: "F01 — Arquitetura de Navegação Global e Shell Responsivo (Roadmap 0.9)"

---

## Contexto e Propósito

No âmbito da versão **0.9 — Revisão Geral de UI/UX, Ergonomia e Estabilização**, a **Feature F0.9.01** atua como a fundação estrutural da aplicação (*App Shell*). 

A auditoria de interface identificou três fragilidades de alto impacto na navegação:
1. **Ocultação Involuntária do Acervo no Desktop:** Em [`NavigationTabs.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/layout/NavigationTabs.vue), a primeira aba da barra de navegação é governada por `homeViewPreference`. Quando o usuário opta por iniciar no Dashboard, o link para a biblioteca de Livros desaparece da barra desktop e do menu secundário, exigindo cliques indiretos.
2. **Sobreposição da Barra Fixa Móvel:** A barra inferior ([`MobileTabBar.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/layout/MobileTabBar.vue)) é fixada na base da tela (`position: fixed; inset: auto 0 0; z-index: 80`). Na ausência de compensação vertical centralizada no contêiner principal ([`App.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/App.vue)), o rodapé global e os botões inferiores de páginas roláveis sofrem colisão ou corte visual.
3. **Dispersão e Inconsistência de Breadcrumbs:** As telas de Livro, Leitor, Editor e Perfil utilizam marcações ad-hoc de breadcrumbs, algumas com links para `"/"` que provocam desvios indesejados para a landing ou cockpit.

Esta especificação define o redesenho e a padronização desses três elementos fundamentais sem introduzir alterações no banco de dados nem quebrar a compatibilidade com os 10 temas do sistema.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Acesso Simultâneo a Dashboard e Acervo de Livros no Desktop (Priority: P1) - MVP

Como leitor utilizando o Leitorum no computador ou tablet em modo paisagem, quero ter acesso direto e visível tanto ao "Dashboard" quanto aos "Livros" na barra de navegação superior, independentemente de qual tela foi definida como minha tela inicial padrão, para alternar entre minhas métricas e meus livros com 1 clique.

**Why this priority**: Elimina um bloqueio ergonômico crítico onde usuários que optavam pelo Cockpit perdiam o acesso em 1 clique à biblioteca de livros.

**Independent Test**: Definir a preferência inicial como "dashboard" e depois como "books"; em ambos os casos, verificar que os botões "Dashboard" e "Livros" permanecem visíveis, clicáveis e com destaque de rota ativa correto na barra de navegação desktop.

**Acceptance Scenarios**:
1. **Dado** um usuário com `caderno_home_view = 'dashboard'`, **quando** ele acessa o sistema no desktop (`>= 768px`), **então** a barra superior exibe explicitamente as abas "Dashboard" (apontando para `/dashboard`) e "Livros" (apontando para `/livros`).
2. **Dado** um usuário navegando dentro de um livro (`/livros/1`), **quando** ele clica no item "Dashboard" na barra superior, **então** é redirecionado imediatamente para `/dashboard` sem etapas intermediárias.
3. **Dado** a preferência `caderno_home_view`, **quando** o usuário clica no logotipo textual "Leitorum" no canto superior esquerdo, **então** ele é direcionado à sua tela inicial preferida sem alterar a presença das abas na barra.

---

### User Story 2 - Respiro Inferior Dinâmico no Mobile sem Sobreposição (Priority: P1)

Como leitor navegando no smartphone, quero rolar qualquer página até o final e visualizar claramente o rodapé e todos os botões de ação sem que a barra inferior móvel sobreponha ou corte o conteúdo.

**Why this priority**: Previne que botões secundários, avisos e links institucionais fiquem inacessíveis ou parcialmente ocultados atrás da barra fixa.

**Independent Test**: Abrir páginas longas (como `/ajustes`, `/lixeira`, `/amigos` e `/livros`) em viewport móvel (390x844px e 360x740px); rolar até o fim da página e constatar que há um respiro livre de pelo menos 1.5rem entre o último elemento e o topo da `MobileTabBar`.

**Acceptance Scenarios**:
1. **Dado** um dispositivo com viewport móvel (`<= 767px`) e usuário autenticado, **quando** qualquer página padrão é renderizada, **então** o contêiner `#conteudo` aplica margem inferior calculada considerando `--mobile-nav-offset` (56px) mais a área segura do dispositivo (`env(safe-area-inset-bottom, 0px)`).
2. **Dado** a tela de sessão de estudos (`/estudo/sessao/:sessionId`), **quando** aberta com `meta.cleanScreen = true`, **então** a barra móvel e o cabeçalho global não são renderizados e o contêiner não recebe compensação de offset.
3. **Dado** o rodapé global (`.app-footer`), **quando** visualizado no celular, **então** permanece totalmente legível e acima da barra inferior.

---

### User Story 3 - Trilha de Navegação Universal e Previsível (AppBreadcrumb) (Priority: P2)

Como leitor navegando na hierarquia de um livro ou estudo, quero uma trilha visual clara de onde estou (Livros > Título da Obra > Capítulo > Estudo) que me permita voltar com facilidade ao nível anterior sem me desviar para a página inicial.

**Why this priority**: Fornece senso espacial imediato e reduz cliques desnecessários ao navegar entre capítulos e anotações.

**Independent Test**: Acessar um estudo em `/livros/1/estudos/2`; inspecionar a árvore do DOM e constatar a presença de `<nav aria-label="Trilha de navegação">` com links válidos para o Acervo (`/books`) e para o Livro (`/livros/1?chapter=...`), finalizando com o título do estudo ativo marcado com `aria-current="page"`.

**Acceptance Scenarios**:
1. **Dado** o leitor em `StudyView.vue`, **quando** ele clica no primeiro nível do breadcrumb, **então** é direcionado para a biblioteca de livros (`/books`) e não para a landing ou dashboard.
2. **Dado** um estudo com título longo, **quando** visualizado em tela estreita, **então** o breadcrumb trunca suavemente com elipse sem quebrar o layout nem causar rolagem horizontal na página.
3. **Dado** um usuário de leitor de tela, **quando** ele navega pelo breadcrumb, **então** o componente anuncia os níveis com clareza e indica o item correspondente à página atual.

---

## Edge Cases

- **Navegação com Histórico Vazio:** Ao acessar diretamente um link profundo de estudo via URL digitada, o breadcrumb deve montar a árvore com base nos dados do contexto retornado pela API sem depender do histórico do navegador.
- **Transição de Rota entre Desktop e Mobile (Giro de Tela):** Se o usuário girar o tablet ou redimensionar a janela entre 767px e 768px, a transição entre `NavigationTabs` e `MobileTabBar` deve ocorrer sem tremor (*layout shift*) e sem duplicação de instâncias.
- **Telas Deslogadas (Landing, Login, Registro):** O shell não deve exibir a barra inferior móvel e o cabeçalho deve operar no modo público sem quebras.
- **Títulos de Livros Extremos:** Títulos com mais de 80 caracteres devem ser truncados com reticências visuais no breadcrumb, preservando o acesso ao link do livro.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O componente `NavigationTabs.vue` DEVE exibir simultaneamente as abas "Dashboard" (rota `/dashboard`) e "Livros" (rota `/livros` ou `/books`) como itens primários no desktop.
- **FR-002**: O indicador de aba ativa em `NavigationTabs.vue` DEVE destacar exclusivamente "Dashboard" na rota `/dashboard` e "Livros" nas rotas de acervo, livro e estudos (`books`, `book`, `study`, `study-edit`).
- **FR-003**: O logotipo textual "Leitorum" no `GlobalHeader.vue` DEVE redirecionar para a preferência de tela inicial (`/dashboard` ou `/livros`) do usuário autenticado.
- **FR-004**: O contêiner principal `#conteudo` em `App.vue` DEVE aplicar espaçamento inferior correspondente à altura da barra inferior móvel (`--mobile-nav-offset`) acrescido do respiro de segurança do sistema operacional.
- **FR-005**: DEVE ser criado o componente universal `frontend/src/components/ui/AppBreadcrumb.vue` aceitando uma lista de itens `{ label: string, to?: string | RouteLocationRaw, current?: boolean }`.
- **FR-006**: O componente `AppBreadcrumb.vue` DEVE ser integrado em `BookView.vue`, `StudyView.vue`, `StudyEditView.vue` e `UserProfileView.vue`, substituindo as marcações dispersas anteriores.
- **FR-007**: No mobile (`<= 767px`), o botão duplicado `.mobile-more-trigger` dentro de `GlobalHeader.vue` DEVE ser suprimido de forma limpa, mantendo o botão "Mais" exclusivamente como o 5º item na `MobileTabBar.vue`.
- **FR-008**: Todas as alterações DEVEM preservar estritamente os 10 temas cromáticos do sistema sem introduzir cores hexadecimais fixas.

### Non-Functional Requirements

- **Acessibilidade (WCAG AA):** Alvos de toque na barra de navegação móvel e nos breadcrumbs devem ter no mínimo 44x44px em ponteiros táteis (`pointer: coarse`).
- **Desempenho:** A alternância de rotas e o redimensionamento responsivo não devem disparar recálculos síncronos forçados de layout (*layout thrashing*), sustentando 60 FPS.
- **Consistência de Estilo:** Nenhuma mensagem, documentação ou marcação visual deve conter emojis.

---

## Success Criteria *(mandatory)*

- **SC-001 (Acesso Direto ao Acervo):** 100% dos usuários no desktop conseguem navegar entre Dashboard e Livros com exatamente 1 clique a partir de qualquer página autenticada.
- **SC-002 (Zero Sobreposição no Mobile):** Em 100% das páginas com rolagem vertical testadas em viewports de 360px a 767px, o conteúdo final e o rodapé mantêm folga livre de no mínimo 1.5rem em relação ao topo da `MobileTabBar`.
- **SC-003 (Padronização de Trilhas):** 100% das páginas com estrutura hierárquica (Livro, Leitor, Editor e Perfil) utilizam o componente `AppBreadcrumb.vue`, sem desvios para rotas incorretas.
- **SC-004 (Imunidade de Testes):** 100% dos testes existentes no frontend (`npm test`) continuam passando sem falhas após a refatoração do App Shell.

---

## Assumptions & Dependencies

- **A-001:** O roteador Vue já possui as rotas nomeadas `dashboard`, `books`, `book`, `study`, `study-edit` e `user-profile`.
- **A-002:** A variável `--mobile-nav-offset` está declarada nos estilos globais como `calc(56px + env(safe-area-inset-bottom, 0px))`.
- **D-001:** Nenhuma dependência externa nova de npm será instalada. O componente `AppBreadcrumb.vue` utiliza componentes nativos do Vue Router (`RouterLink`) e ícones existentes via `Icon.vue`.

---

## Contratos de Dados e Tipagem

```typescript
// frontend/src/types/navigation.ts

export interface BreadcrumbItem {
  label: string
  to?: string | { name: string; params?: Record<string, any>; query?: Record<string, any> }
  current?: boolean
}
```
