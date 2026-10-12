# Modelagem de Entidades: F0.8.15 — Bateria Completa de Regressão e Consolidação do Roadmap de Responsividade

**Feature**: `081-regressao-responsiva`  
**Data**: 2026-10-12  
**Status**: Aprovado  

---

## 1. Entidade: Entrada da Matriz de Regressão de Rotas (`RouteRegressionMatrixEntry`)

Representa o contrato de validação para cada uma das 25 rotas nomeadas de `router/index.ts` através das 8 viewports normativas e no modo paisagem móvel.

### Atributos

| Campo | Tipo | Descrição | Regra de Validação |
|---|---|---|---|
| `route_name` | String | Identificador nomeado no Vue Router | Deve existir em `src/router/index.ts` |
| `path` | String | Padrão de URL da rota | Deve corresponder à rota canônica |
| `component_path` | String | Caminho do componente Vue associado | Arquivo deve existir em `src/views/` |
| `screen_tier` | Enum | Nível de complexidade da tela (1 a 5) | 1: Leitura, 2: Gestão, 3: Grafo/Mapa, 4: Canvas, 5: Pública/Auth |
| `viewports` | Array<Number> | Lista de larguras testadas | `[320, 375, 390, 430, 767, 768, 1024, 1440]` |
| `landscape_support` | Boolean | Validação na resolução 844x390px | Obrigatório (`true`) |
| `overflow_contained` | Boolean | Contenção estrita de transbordamento | `scrollWidth === clientWidth` (zero scroll horizontal) |
| `touch_targets_valid` | Boolean | Alvos de toque acessíveis no mobile | Todos os botões $\ge 44 \times 44\text{ px}$ |
| `mobile_nav_offset` | Boolean | Respeito à barra de navegação móvel | Elementos fixos aplicam `--mobile-nav-offset` |

### Tabela Canônica das 25 Rotas Auditadas

| # | `route_name` | `path` | Componente | Tier | Status de Overflow | Alvos Táteis |
|---|---|---|---|:---:|:---:|:---:|
| 01 | `login` | `/login` | `views/LoginView.vue` | 5 | Contido | $\ge 44\text{px}$ |
| 02 | `register` | `/registro` | `views/RegisterView.vue` | 5 | Contido | $\ge 44\text{px}$ |
| 03 | `setup-owner` | `/primeiro-acesso` | `views/SetupOwnerView.vue` | 5 | Contido | $\ge 44\text{px}$ |
| 04 | `landing` | `/` | `views/LandingView.vue` | 5 | Contido | $\ge 44\text{px}$ |
| 05 | `about` | `/sobre` | `views/AboutView.vue` | 5 | Contido | $\ge 44\text{px}$ |
| 06 | `dashboard` | `/dashboard` | `views/DashboardView.vue` | 2 | Contido | $\ge 44\text{px}$ |
| 07 | `inbox` | `/inbox` | `views/InboxView.vue` | 2 | Contido | $\ge 44\text{px}$ |
| 08 | `books` | `/books` | `views/BooksView.vue` | 2 | Contido | $\ge 44\text{px}$ |
| 09 | `highlights` | `/highlights` | `views/HighlightsLibraryView.vue` | 2 | Contido | $\ge 44\text{px}$ |
| 10 | `review` | `/review` | `views/ReviewHubView.vue` | 2 | Contido | $\ge 44\text{px}$ |
| 11 | `study-session` | `/estudo/sessao/:sessionId` | `views/StudySessionView.vue` | 1 | Contido | $\ge 44\text{px}$ |
| 12 | `book` | `/livros/:bookId` | `views/BookView.vue` | 1 | Contido | $\ge 44\text{px}$ |
| 13 | `study` | `/livros/:bookId/estudos/:studyId` | `views/StudyView.vue` | 1 | Contido | $\ge 44\text{px}$ |
| 14 | `study-direct` | `/estudos/:studyId` | `views/StudyView.vue` | 1 | Contido | $\ge 44\text{px}$ |
| 15 | `study-edit` | `/livros/:bookId/estudos/:studyId/editar` | `views/StudyEditView.vue` | 2 | Contido | $\ge 44\text{px}$ |
| 16 | `import` | `/importar` | `views/ImportView.vue` | 2 | Contido | $\ge 44\text{px}$ |
| 17 | `digitize-notebook` | `/digitalizar` | `views/DigitizeNotebookView.vue` | 2 | Contido | $\ge 44\text{px}$ |
| 18 | `friends` | `/amigos` | `views/FriendsView.vue` | 2 | Contido | $\ge 44\text{px}$ |
| 19 | `connection` | `/conexao` | `views/ConnectionView.vue` | 5 | Contido | $\ge 44\text{px}$ |
| 20 | `settings` | `/ajustes` | `views/SettingsView.vue` | 5 | Contido | $\ge 44\text{px}$ |
| 21 | `trash` | `/lixeira` | `views/TrashView.vue` | 2 | Contido | $\ge 44\text{px}$ |
| 22 | `user-profile` | `/@:username` | `views/UserProfileView.vue` | 5 | Contido | $\ge 44\text{px}$ |
| 23 | `admin` | `/admin` | `views/AdminView.vue` | 2 | Contido | $\ge 44\text{px}$ |
| 24 | `support` | `/apoie` | `views/SupportView.vue` | 5 | Contido | $\ge 44\text{px}$ |
| 25 | `not-found` | `/:pathMatch(.*)*` | `views/NotFoundView.vue` | 5 | Contido | $\ge 44\text{px}$ |

---

## 2. Entidade: Registro de Fechamento de Problema Auditado (`AuditedIssueResolutionRecord`)

Estrutura formal de rastreabilidade de cada um dos 19 problemas (P-01 a P-19) diagnosticados no início do ciclo de responsividade móvel.

### Atributos

| Campo | Tipo | Descrição |
|---|---|---|
| `issue_id` | String | Identificador padronizado (`P-01` a `P-19`) |
| `title` | String | Título sumário do problema auditado |
| `severity` | Enum | `Crítica`, `Alta`, `Média`, `Baixa` |
| `resolving_feature` | String | Feature do roadmap responsável pelo fechamento |
| `core_artifacts` | Array<String> | Arquivos de código-fonte modificados |
| `guard_test_file` | String | Arquivo de teste automatizado que blinda a regra |
| `resolution_evidence` | String | Síntese da solução técnica comprovada |
| `status` | Enum | Estritamente `Resolvido` |

---

## 3. Entidade: Cenário de Verificação em Aparelho Físico (`DeviceVerificationScenario`)

Estrutura para documentação e condução de testes táteis e de contexto de hardware em aparelhos físicos sob rede local ou Tailscale.

### Atributos

| Campo | Tipo | Descrição |
|---|---|---|
| `scenario_id` | String | Código de identificação (`SCEN-01` a `SCEN-05`) |
| `target_device_profile` | String | Modelo representativo e dimensões em pontos CSS |
| `orientation` | Enum | `portrait` ou `landscape` |
| `operational_focus` | String | Foco operacional (Gestos, Teclado Virtual, Safe Area) |
| `user_interaction_flow` | Array<String> | Passo a passo de navegação e toque |
| `expected_visual_state` | String | Critérios de sucesso visual e ausência de travamentos |
