# Auditoria de Nomenclatura e Preparação para o Domínio Leitorum (`leitorum.com`)

> **Documento de Governança Técnica e Diagnóstico Preliminar**  
> **Status:** Concluído (Fase de Análise — Nenhuma alteração no código-fonte)  
> **Data:** 26 de setembro de 2026  
> **Domínio Alvo:** `leitorum.com`  
> **Novo Nome Visual / Marca:** `Leitorum`  
> **Identificador Técnico Geral:** `caderno1` (quando aplicável)  
> **Arquitetura de Exposição:** Localhost (Windows) via Cloudflare Tunnel (`cloudflared`)

---

## 1. Resumo Executivo

Esta auditoria realizou uma varredura completa por análise estática de código (AST e regex contextual) em todos os diretórios do repositório, inspecionando o backend FastAPI, frontend Vue 3, scripts utilitários, automações batch/powershell, suítes de testes automatizados e arquivos de infraestrutura.

O objetivo é planejar com segurança e previsibilidade a futura transição da aplicação:
- Do nome institucional atual **Caderno de Leitura** para o nome público **Leitorum**.
- Da nomenclatura técnica interna de projeto (`caderno`, `caderno-leitura`) para **`caderno1`**.
- Do ambiente estritamente local (`127.0.0.1:8000`) para o domínio público seguro **`leitorum.com`**, servido pelo próprio computador pessoal do usuário através de **Cloudflare Tunnel** (sem abertura de portas no roteador doméstico e sem exposição direta de IP).

### Quantitativo Consolidado de Ocorrências

| Categoria / Subsistema | Ocorrências de Nomes / Identificadores | Ocorrências de Rede / Configuração / Portas | Total | Impacto Técnico |
| :--- | :---: | :---: | :---: | :--- |
| **Backend (Python / FastAPI)** | 52 | 68 | **120** | Médio (Strings de metadados, manifesto de backup, env vars e cookies) |
| **Frontend (Vue 3 / TypeScript / CSS)** | 85 | 42 | **127** | Médio-Alto (Títulos de tela, brand no header, chaves de localStorage e fontes) |
| **Fontes Locais (@font-face CSS)** | 76 (19 famílias) | 0 | **76** | Baixo (Prefixos `Caderno <Nome>` em `fonts.css`) |
| **Testes Automatizados (Pytest / Node)** | 59 | 185 | **244** | Alto em caso de refactor (Asserções de títulos, cookies e banco) |
| **Scripts de Inicialização (.cmd / .py)** | 18 | 24 | **42** | Baixo (Mensagens de terminal, banners e flags de porta) |
| **Configurações e Build (Vite, npm, ini)** | 9 | 12 | **21** | Baixo (package.json, vite.config.ts) |
| **Documentação Histórica e Specs (.md)** | 1.549 | 602 | **2.151** | Informativo / Histórico (Não quebra execução) |
| **TOTAL GERAL** | **1.848** | **933** | **2.781** | — |

### Diagnóstico de Prontidão para o Domínio `leitorum.com`

> [!TIP] **Conclusão Principal da Auditoria**  
> A arquitetura da aplicação está **excepcionalmente bem preparada** para rodar sob o domínio `leitorum.com` via Cloudflare Tunnel. Não existem URLs absolutas (`http://localhost:8000`) codificadas no cliente HTTP do frontend; todas as chamadas de API utilizam rotas relativas (`/api/...`), e o backend atua como servidor de arquivos estáticos da mesma origem (`LocalFrontend`). Os cookies de sessão não especificam atributo `domain` fixo (adotando isolamento automático de *host-only*) e já inspecionam o cabeçalho `X-Forwarded-Proto` injetado pelo Cloudflare para ativar a flag `Secure`.

---

## 2. Ocorrências Mapeadas por Categoria

Abaixo, detalham-se todas as ocorrências encontradas no código-fonte, agrupadas nas categorias formais de análise:

### Categoria 1: Nome Visual da Aplicação (`"Caderno de Leitura"`)
Ocorrências onde o nome é exibido diretamente ao usuário na interface gráfica, telas de autenticação, relatórios ou documentação OpenAPI.

| Arquivo | Linha | Trecho / Ocorrência | Contexto / Uso | Risco de Alteração |
| :--- | :---: | :--- | :--- | :--- |
| `frontend/src/App.vue` | 134 | `<RouterLink class="brand" to="/">Caderno de Leitura</RouterLink>` | Logotipo/Marca na barra de navegação superior | Muito Baixo |
| `frontend/src/router/index.ts` | 93 | ``document.title = `${String(to.meta.title)} · Caderno de Leitura``` | Título da aba do navegador | Baixo (Afeta testes) |
| `frontend/src/views/LoginView.vue` | 67 | `<h1 class="auth-title">Caderno de Leitura</h1>` | Título da tela de login | Muito Baixo |
| `frontend/src/views/LoginView.vue` | 125 | `<span v-else>Entrar no Caderno</span>` | Botão de submissão de login | Muito Baixo |
| `frontend/src/views/RegisterView.vue` | 89 | `<p class="auth-subtitle">Cadastre seu próprio caderno de leitura independente</p>` | Subtítulo da tela de registro | Muito Baixo |
| `frontend/src/views/SettingsView.vue` | 483 | `Defina como você é reconhecido por outros leitores na rede do Caderno.` | Seção de perfil em configurações | Muito Baixo |
| `frontend/src/views/SettingsView.vue` | 798 | `Escolha qual tela deve ser carregada por padrão ao abrir o Caderno de Leitura...` | Opções de tela inicial | Muito Baixo |
| `frontend/src/views/SettingsView.vue` | 835 | `...reside com segurança no banco de dados SQLite local (caderno.db)...` | Diagnóstico do banco | Muito Baixo |
| `frontend/src/views/FriendsView.vue` | 89, 197 | `...gerencie sua rede social no Caderno.`, `Você ainda não possui amigos no seu caderno.` | Textos do módulo social | Muito Baixo |
| `frontend/src/views/DashboardView.vue` | 173, 199, 347, 375 | `...indicadores do caderno`, `Seu caderno ainda não possui livros ativos`, etc. | Textos de estado vazio e cockpits | Muito Baixo |
| `backend/app/main.py` | 53 | `title="Caderno de Leitura"` | Título da documentação Swagger/OpenAPI | Baixo (Afeta testes) |
| `backend/app/main.py` | 55 | `description="API local do caderno pessoal de leitura."` | Descrição OpenAPI | Muito Baixo |
| `backend/app/core/config.py` | 9 | `DEFAULT_OWNER_DISPLAY_NAME: str = "Proprietário do Caderno"` | Nome padrão do usuário inicial | Médio (Persistido no DB) |
| `backend/app/schemas/backups.py` | 16 | `generator: str = "Caderno de Leitura Backup Engine"` | Assinatura no manifesto de backup | Alto (Compatibilidade) |
| `backend/app/services/backups.py` | 220 | `generator="Caderno de Leitura Backup Engine"` | Criação de manifesto de backup | Alto (Compatibilidade) |
| `backend/app/services/export_service.py` | 78, 255 | `lines.append('app: "Caderno de Leitura"')` | Metadados frontmatter em exportações Markdown | Médio (Afeta testes) |
| `iniciar.py` | 25, 110, 130 | `description="Caderno de Leitura Alpha 0.2"`, etc. | Ajuda CLI e mensagens de erro de porta | Muito Baixo |
| `instalar.py` | 17 | `description="Instalar o Caderno de Leitura Alpha 0.1."` | Ajuda CLI de instalação | Muito Baixo |

---

### Categoria 2: Identificador Técnico de Aplicação e Serviços
Identificadores utilizados em pacotes, payloads de saúde e interfaces de bibliotecas.

| Arquivo | Linha | Trecho / Ocorrência | Contexto / Uso | Risco de Alteração |
| :--- | :---: | :--- | :--- | :--- |
| `frontend/package.json` | 2 | `"name": "caderno-leitura"` | Identificador do projeto npm | Muito Baixo |
| `backend/app/routers/health.py` | 14 | `service="caderno-leitura"` | Resposta JSON de `GET /api/health` | Alto (Afeta testes e monitoramento) |
| `frontend/src/services/api.ts` | 620 | `throw new Error('A resposta recebida não corresponde à API do Caderno de Leitura.')` | Validação de payload de health check | Médio (Valida o service) |
| `scripts/instalar-fontes.py` | 53 | `headers={"User-Agent": "CadernoFontInstaller/0.2"}` | User agent em download de fontes | Baixo |

---

### Categoria 3: Nome de Componente
Varredura realizada em todos os componentes Vue em `frontend/src/components/**/*.vue` e views em `frontend/src/views/*.vue`.
- **Resultado:** Nenhum componente Vue utiliza `Caderno` ou `CadernoLeitura` como nome de tag, nome de arquivo ou propriedade `name`. Os componentes possuem nomenclaturas semânticas modulares: `DatabaseBackup.vue`, `StudyEditorFields.vue`, `ShareModal.vue`, `BookCard.vue`, `StudyGridView.vue`, `FriendsView.vue`, `SettingsView.vue`, etc.
- **Risco:** Zero.

---

### Categoria 4: Nome de Arquivo
Arquivos no disco com o prefixo ou termo em seu nome.

| Arquivo | Contexto / Uso | Risco de Alteração |
| :--- | :--- | :--- |
| `backend/data/caderno.db` | Arquivo do banco de dados SQLite local ativo. | **Crítico**: Alterar o nome exige migrar dados reais e alterar caminhos em múltiplos módulos. |
| `backend/data/caderno-pre-migracao-*.db` | Snapshots automáticos criados antes de rodar Alembic. | Médio (Padrão de glob em `maintenance.py`). |
| `backend/data/caderno-pre-restauracao-*.db` | Snapshots automáticos de salvaguarda antes de restauração. | Médio (Padrão de glob em `maintenance.py`). |
| `backend/data/caderno-backup-*.zip` | Arquivos compactados de backup universal. | Médio (Formato de download sugerido na API). |
| `backend/data/caderno-*.db` | Cópias pontuais do banco SQLite exportadas pelo usuário. | Baixo. |
| `.agents/rules/caderno-leitura.md` | Regras do workspace para agentes de IA. | Muito Baixo. |

---

### Categoria 5: Nome de Pasta
Diretórios do sistema de arquivos contendo o nome.

| Diretório | Contexto / Uso | Risco de Alteração |
| :--- | :--- | :--- |
| `c:\Users\User\caderno\` | Diretório raiz do projeto no disco do usuário. | **Alto**: Altera o path do workspace, git e scripts batch. |
| `caderno-leitura-0.1/` | Subpasta da aplicação contendo backend, frontend e scripts. | **Alto**: Referenciada por scripts de automação e regras. |
| Prefixos de TempDir (`caderno-bundle-*`, `caderno-inspect-*`, etc.) | Diretórios temporários criados em memória/disco durante backups. | Baixo. |

---

### Categoria 6: Rotas e Navegação (Frontend)
Varredura em `frontend/src/router/index.ts`.
- **Resultado:** Nenhuma rota Vue contém `caderno` em sua URL. As rotas são: `/`, `/library`, `/study/:id`, `/trash`, `/canvas`, `/settings`, `/friends`, `/dashboard`, `/admin`, `/login`, `/register`.
- **Risco:** Zero.

---

### Categoria 7: URLs e Endereços Externos
URLs declaradas no código-fonte.

| Arquivo | Linha | URL / Ocorrência | Finalidade | Risco de Alteração |
| :--- | :---: | :--- | :--- | :--- |
| `frontend/src/composables/useGoogleIdentity.ts` | 46 | `https://accounts.google.com/gsi/client` | SDK oficial do Google Identity Services | Nulo (Dependência externa) |
| `frontend/src/components/StudyEditorFields.vue` | 18 | `https://exemplo.com` | Exemplo de sintaxe Markdown para links | Nulo (Texto estático) |
| `scripts/instalar-fontes.py` | 91 | `https://registry.npmjs.org/@fontsource%2F{ident}/{VERSION}` | Registro npm para download de WOFF2 | Nulo (Script utilitário) |
| `frontend/public/fonts/**/LICENSE` | Vários | `http://scripts.sil.org/OFL`, repositórios GitHub | Licenças OFL das fontes tipográficas | Nulo (Arquivos de licença) |

---

### Categoria 8: Endpoints da API (Backend)
Varredura em todos os 18 arquivos em `backend/app/routers/*.py`.
- **Resultado:** **Zero endpoints** utilizam `caderno` no caminho da URL. Todos os 128 endpoints REST seguem padrões semânticos de domínio:
  - `/api/health`, `/api/auth/*`, `/api/admin/*`, `/api/users/*`, `/api/friends/*`
  - `/api/books/*`, `/api/chapters/*`, `/api/studies/*`, `/api/canvas/*`
  - `/api/backups/*`, `/api/categories/*`, `/api/trash/*`, `/api/covers/*`
  - `/api/dashboard/*`, `/api/search/*`, `/api/sync/*`, `/api/profile/*`
- **Risco:** Zero quebra de contratos de rotas HTTP.

---

### Categoria 9: Variáveis de Ambiente
Variáveis de ambiente lidas por `os.environ.get()` em `backend/app/core/config.py`.

| Variável de Ambiente | Padrão (Fallback) | Finalidade | Risco se Renomeada |
| :--- | :--- | :--- | :--- |
| `CADERNO_DATABASE_PATH` | `backend/data/caderno.db` | Sobrescreve o caminho absoluto da base SQLite. | **Alto**: Se alterada para `CADERNO1_DATABASE_PATH` ou `LEITORUM_DATABASE_PATH` sem manter fallback para a anterior, scripts existentes e suítes de testes quebrarão. |
| `CADERNO_COVERS_DIR` | `backend/data/covers` | Diretório para armazenamento de capas locais. | Médio (Mesmo critério de fallback). |
| `CADERNO_AVATARS_DIR` | `backend/data/avatars` | Diretório de imagens de avatar dos usuários. | Médio (Mesmo critério de fallback). |
| Demais Variáveis (`REQUIRE_AUTH`, `ALLOW_REGISTRATION`, `GOOGLE_CLIENT_ID`, `SESSION_COOKIE_SECURE`) | N/A | Genéricas, não utilizam prefixo de marca. | Nenhum. |

---

### Categoria 10: Chaves de Configuração
Constantes de configuração interna no backend.

| Arquivo | Linha | Chave / Constante | Valor Atual | Observação |
| :--- | :---: | :--- | :--- | :--- |
| `backend/app/core/config.py` | 12 | `SESSION_COOKIE_NAME` | `"caderno_session"` | Nome do cookie de autenticação emitido pelo backend. |
| `backend/app/core/config.py` | 9 | `DEFAULT_OWNER_DISPLAY_NAME` | `"Proprietário do Caderno"` | Nome atribuído ao primeiro usuário migrado. |
| `backend/app/services/backups.py` | 220 | Manifesto `generator` | `"Caderno de Leitura Backup Engine"` | Chave de assinatura interna de integridade do ZIP. |

---

### Categoria 11: Referência em Documentação e Histórico
Total de **~1.640 ocorrências** em arquivos Markdown de documentação e especificações (`docs/`, `specs/`, `ACEITE-0.1.md`, etc.).
- **Diagnóstico:** São registros históricos de evolução arquitetural (Roadmaps 0.1 a 0.5, ADRs, transcrições de sprints).
- **Recomendação:** Devem ser mantidos como histórico imutável do projeto. Apenas documentos de visão ativa (ex.: `PROJETO.md`, `README.md`) devem receber uma nota explicativa sobre a nova identidade `Leitorum`.

---

### Categoria 12: Título de Página, Metadados e Favicon
Varredura em `frontend/index.html` e `frontend/src/router/index.ts`.

| Elemento | Estado Atual | Localização | Diagnóstico para `leitorum.com` |
| :--- | :--- | :--- | :--- |
| **Favicon** | **Inexistente** | `frontend/index.html` | Não há `<link rel="icon">` nem arquivo `favicon.ico`. O navegador requisita `/favicon.ico` e recebe 404. É necessário criar um favicon oficial com a marca Leitorum. |
| **`<title>` HTML estático** | **Inexistente** | `frontend/index.html` | Falta a tag `<title>Leitorum</title>` no HTML base (aparece em branco até o JavaScript carregar). |
| **Título Dinâmico (JS)** | `${title} · Caderno de Leitura` | `frontend/src/router/index.ts:93` | O router Vue injeta o sufixo dinâmico após cada navegação. Deve ser alterado para `${title} · Leitorum`. |
| **Metatags OpenGraph / SEO** | **Inexistentes** | `frontend/index.html` | Ausência total de `og:title`, `og:description`, `og:image`, `og:url` e `<meta name="description">`. Essencial para compartilhamento social de links de `leitorum.com`. |

---

### Categoria 13: Cookies de Sessão HTTP

| Propriedade | Valor Configurado | Arquivo / Linha | Comportamento no Domínio `leitorum.com` |
| :--- | :--- | :--- | :--- |
| **Nome** | `caderno_session` | `core/config.py:12` | Pode permanecer `caderno_session` ou mudar para `leitorum_session` com suporte de leitura dupla. |
| **HttpOnly** | `True` | `session_service.py:192` | Protege contra roubo via XSS. Excelente. |
| **SameSite** | `"lax"` | `session_service.py:193` | Permite navegação direta a partir de links externos mantendo a sessão. |
| **Path** | `"/"` | `session_service.py:194` | Válido para toda a aplicação. |
| **Domain** | *(Não definido — omitido)* | `session_service.py:188` | **Host-only Cookie (RFC 6265)**: Funciona perfeitamente e de forma idêntica tanto em `127.0.0.1` quanto em `leitorum.com`. |
| **Secure** | Dinâmico via `resolve_cookie_secure` | `session_service.py:170-178` | **Comportamento Ideal**: Detecta automaticamente `X-Forwarded-Proto: https` enviado pelo Cloudflare Tunnel e ativa `Secure=True` automaticamente! |

---

### Categoria 14: Eventos Customizados JavaScript (Frontend)

O frontend utiliza o barramento de eventos nativo do DOM (`window.dispatchEvent` / `window.addEventListener`) para sincronização reativa entre componentes independentes:

| Nome do Evento | Arquivos que Disparam | Arquivos que Escutam | Finalidade | Risco se Renomeado |
| :--- | :--- | :--- | :--- | :--- |
| `'caderno_auth_changed'` | `stores/auth.ts` (linhas 64, 81, 102, 119, 146) | `views/SettingsView.vue` | Notifica mudança de status de login/logout/registro | Médio (Exige sincronia exata entre disparo e escuta) |
| `'caderno:sync-applied'` | `composables/useSync.ts` (linha 49) | `composables/usePreferences.ts` | Notifica aplicação de alterações remotas de sincronização | Médio |
| `'caderno_home_view_changed'` | `views/SettingsView.vue` (linha 342) | `App.vue` (linhas 58, 80) | Notifica alteração da preferência de tela inicial | Médio |

---

### Categoria 15: Chaves de Armazenamento Local (`localStorage`)

O frontend persiste configurações de usuário e estados de UI no `localStorage` do navegador:

| Chave Atual | Arquivo de Origem | Conteúdo / Finalidade | Impacto ao Renomear |
| :--- | :--- | :--- | :--- |
| `caderno.aparencia.v2` | `appearance-bootstrap.js:6` | Tema, contraste, fonte, densidade e superclasse de UI | **Alto**: Se renomeada sem migração, o usuário perde o tema customizado. |
| `caderno_home_view` | `App.vue:40`, `router/index.ts:80` | Rota inicial preferida (`/library` ou `/dashboard`) | Médio |
| `caderno_user_preferences` | `usePreferences.ts:12` | Preferências de leitura e navegação | Médio |
| `caderno_last_sync_time` | `useSync.ts:5` | Timestamp da última sincronização bem-sucedida | Médio |
| `caderno_library_view_mode` | `useLibraryFilter.ts:5` | Modo de visualização do acervo (`grid` ou `list`) | Baixo |
| `caderno_library_sort` | `useLibraryFilter.ts:6` | Critério de ordenação da biblioteca | Baixo |
| `caderno_pane_sizes_global` | `useSplitPanes.ts:4` | Largura dos painéis redimensionáveis (geral) | Baixo |
| `caderno_pane_sizes_book_*` | `useSplitPanes.ts:5` | Largura dos painéis por livro específico | Baixo |
| `caderno_study_group_by` | `useStudyGrouping.ts:76` | Agrupamento de estudos (por data, capítulo, etc.) | Baixo |
| `caderno_tree_expanded_ch_*` | `useStudyHierarchy.ts:113` | Nós expandidos na árvore de capítulos | Baixo |
| `caderno_default_view` | `useViewPreference.ts:4` | Visualização padrão de estudos | Baixo |
| `caderno_preferred_view_*` | `useViewPreference.ts:5` | Visualização preferida por livro específico | Baixo |
| `caderno_canvas_viewport_*` | `useCanvasViewport.ts:25` | Coordenadas de zoom e pan do Canvas | Baixo |
| `caderno_dashboard_blocks_visibility` | `views/DashboardView.vue:50` | Visibilidade dos blocos do cockpit | Baixo |
| `caderno_dashboard_mobile_tab` | `views/DashboardView.vue:55` | Aba ativa no layout mobile do dashboard | Baixo |
| `caderno_group_by_grid_*` | `StudyGridView.vue:35` | Agrupamento na grade de estudos | Baixo |
| `caderno_group_by_list_*` | `StudyListView.vue:35` | Agrupamento na lista de estudos | Baixo |

> [!WARNING] **Bug Pré-existente Identificado na Auditoria**  
> Em `frontend/src/views/SettingsView.vue:200`, a contagem de chaves para diagnóstico do sistema faz `if (key.startsWith('caderno.'))`. Esse teste captura apenas `caderno.aparencia.v2` e ignora todas as outras 16 chaves que começam com `caderno_`! Na futura transição, esse filtro deve ser ajustado para cobrir tanto o prefixo novo quanto o legado.

---

### Categoria 16: Tipografia e Famílias de Fontes CSS

Em `frontend/src/fonts.css`, 19 famílias de fontes locais estão mapeadas com o prefixo `"Caderno <Nome>"` para evitar colisões com fontes instaladas no sistema operacional do usuário:

| Família de Fonte CSS | Declarações `@font-face` | Arquivo WOFF2 Local |
| :--- | :---: | :--- |
| `"Caderno Literata"` | 4 | `/fonts/literata/5.3.0/*.woff2` |
| `"Caderno Inter"` | 4 | `/fonts/inter/5.3.0/*.woff2` |
| `"Caderno Merriweather"` | 4 | `/fonts/merriweather/5.3.0/*.woff2` |
| `"Caderno Lora"` | 4 | `/fonts/lora/5.3.0/*.woff2` |
| `"Caderno EB Garamond"` | 4 | `/fonts/eb-garamond/5.3.0/*.woff2` |
| `"Caderno Bitter"` | 4 | `/fonts/bitter/5.3.0/*.woff2` |
| `"Caderno Noto Serif"` / `"Caderno Noto Sans"` | 8 | `/fonts/noto-*/5.3.0/*.woff2` |
| `"Caderno IBM Plex Sans"` / `"Caderno IBM Plex Serif"` | 8 | `/fonts/ibm-plex-*/5.3.0/*.woff2` |
| Demais famílias mono e display (10 famílias) | 40 | `/fonts/*/5.3.0/*.woff2` |

- **Script de Origem:** `scripts/instalar-fontes.py:154` (`family = f"Caderno {name}"`).
- **Objeto Global:** `window.cadernoFontCatalog` injetado pelo plugin Vite em `frontend/vite.config.ts:36`.
- **Recomendação:** A alteração desse prefixo para `"Leitorum <Nome>"` exige rodar novamente o script gerador ou fazer substituição atômica em `fonts.css` e `font-catalog.json`. Como é um recurso puramente estético e isolado no CSS, pode ser renomeado com baixo risco caso desejado.

---

## 3. Tabela Canônica de Renomeações Propostas

A tabela a seguir consolida todas as recomendações de renomeação, categorizando a necessidade, o impacto e a estratégia recomendada:

| Item / Elemento Atual | Novo Nome Proposto | Tipo | Alterar? | Estratégia e Observações |
| :--- | :--- | :--- | :---: | :--- |
| **Marca visual no header** (`Caderno de Leitura`) | `Leitorum` | Nome Visual | **SIM** | Alterar em `App.vue:134`. Impacto imediato e positivo na identidade visual. |
| **Título das abas do navegador** (`· Caderno de Leitura`) | `· Leitorum` | Metadados | **SIM** | Alterar em `router/index.ts:93` e adicionar `<title>Leitorum</title>` no `index.html`. |
| **Títulos de Login e Registro** | `Leitorum` | Nome Visual | **SIM** | Atualizar textos em `LoginView.vue` e `RegisterView.vue`. |
| **Textos institucionais em Settings e Dashboard** | `Leitorum` | Nome Visual | **SIM** | Substituir menções textuais na UI mantendo o tom editorial. |
| **Título do OpenAPI / Swagger** (`Caderno de Leitura`) | `Leitorum API` | Nome Técnico | **SIM** | Alterar em `main.py:53`. Atualizar asserções correspondentes nos testes. |
| **Nome no package.json** (`"caderno-leitura"`) | `"caderno1"` ou `"leitorum"` | Identificador Técnico | **SIM** | Identificador de empacotamento npm. Sem impacto em tempo de execução. |
| **Serviço no Health Check** (`service="caderno-leitura"`) | `service="caderno1"` | Endpoint / Payload | **SIM** | Alterar em `routers/health.py:14`. **Atenção:** Atualizar teste unitário e validação em `api.ts:620`. |
| **Cookie de Sessão** (`caderno_session`) | `leitorum_session` | Cookie HTTP | **OPCIONAL** | Se renomeado, usuários logados precisarão autenticar-se novamente. Recomendado manter suporte de transição (ler ambos). |
| **Variável de Banco** (`CADERNO_DATABASE_PATH`) | `CADERNO1_DATABASE_PATH` | Variável de Ambiente | **SIM (com Fallback)** | Adicionar suporte prioritário a `CADERNO1_DATABASE_PATH` ou `LEITORUM_DATABASE_PATH`, mantendo `CADERNO_DATABASE_PATH` como segundo fallback. |
| **Variáveis de Pastas** (`CADERNO_COVERS_DIR`, `CADERNO_AVATARS_DIR`) | `CADERNO1_*` / `LEITORUM_*` | Variável de Ambiente | **SIM (com Fallback)** | Mesma regra de fallback duplo para preservar compatibilidade de ambientes. |
| **Nome do arquivo de banco** (`caderno.db`) | `caderno.db` | Arquivo de Banco | **NÃO (Manter)** | **Manter rigidamente.** Alterar esse nome quebraria a restauração de backups históricos `.zip` existentes que validam a presença de `caderno.db`. |
| **Estrutura interna do Backup ZIP** (`caderno.db`, `manifest.json`) | Inalterada | Formato de Dados | **NÃO (Manter)** | O motor de restauração (`restore_service.py:54`) exige expressamente `caderno.db`. Não alterar o nome do arquivo interno. |
| **Gerador no Manifesto** (`"Caderno de Leitura Backup Engine"`) | `"Leitorum Backup Engine"` | Metadados de Dados | **CONDICIONAL** | O validador de restauração deve aceitar tanto a assinatura legada quanto a nova para não invalidar backups criados na versão atual. |
| **Exportações Markdown** (`app: "Caderno de Leitura"`) | `app: "Leitorum"` | Metadados Frontmatter | **SIM** | Atualizar em `export_service.py` e ajustar testes de exportação. |
| **Chaves de localStorage** (`caderno.*`, `caderno_*`) | `leitorum.*` / `caderno1_*` | Armazenamento Web | **SIM (com Migração)** | Implementar migrador automático no bootstrap: se existir chave antiga e não existir nova, copia o valor e preserva preferências do usuário. |
| **Eventos Customizados JS** (`caderno_auth_changed`, etc.) | `leitorum:auth-changed`, etc. | Eventos DOM | **SIM** | Renomear de forma coordenada entre emissores e receptores. |
| **Fontes Locais CSS** (`"Caderno Literata"`, etc.) | `"Leitorum Literata"`, etc. | Tipografia CSS | **OPCIONAL** | Renomear via script `instalar-fontes.py` ou manter caso não haja necessidade visual urgente. |
| **Diretório raiz do disco** (`c:\Users\User\caderno`) | Inalterado | Sistema de Arquivos | **NÃO (Manter)** | Manter o caminho no disco local do usuário para evitar problemas de workspace no Git e no Antigravity. |
| **Scripts de Terminal** (`iniciar.py`, `iniciar.cmd`) | Textos e Banners | Interface de Linha de Comando | **SIM** | Atualizar mensagens informativas ("Leitorum rodando em http://127.0.0.1:8000"). |

---

## 4. Análise do Domínio Público: `leitorum.com`

### O que PRECISA conhecer o domínio `leitorum.com`

1. **Google Identity Services (Autenticação Google / GIS):**
   - **Requisito Crítico:** O fluxo OAuth do Google exige que as origens JavaScript autorizadas sejam cadastradas no Google Cloud Console.
   - **Ação Necessária:** No console do projeto Google Cloud, na seção *APIs & Services > Credentials > OAuth 2.0 Client IDs*, adicionar:
     - **Authorized JavaScript origins:** `https://leitorum.com` (e também manter `http://127.0.0.1:8000` para desenvolvimento local).
     - Não é necessário Redirect URI porque o projeto utiliza a API moderna de botão rendered (`credential_response` via postmessage client-side).

2. **Metatags de Compartilhamento Social e SEO (`frontend/index.html`):**
   - Quando links forem compartilhados em redes sociais ou mensageiros (WhatsApp, Telegram, Twitter/X, Discord), o crawler precisa receber as metatags canônicas ancoradas em `leitorum.com`:
     ```html
     <link rel="canonical" href="https://leitorum.com" />
     <meta property="og:site_name" content="Leitorum" />
     <meta property="og:title" content="Leitorum — Caderno Pessoal de Leitura e Estudos" />
     <meta property="og:description" content="Ambiente dedicado ao registro, estudo e reflexão de livros." />
     <meta property="og:url" content="https://leitorum.com" />
     <meta property="og:image" content="https://leitorum.com/og-cover.png" />
     <meta name="twitter:card" content="summary_large_image" />
     ```

3. **Favicon e Manifest Web:**
   - Adicionar os arquivos de ícone na pasta `frontend/public/` e referenciá-los no `index.html`:
     ```html
     <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
     <link rel="alternate icon" href="/favicon.ico" />
     <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
     ```

4. **Futuros E-mails Transacionais ou Links de Compartilhamento:**
   - Caso venha a existir envio de e-mail de recuperação de senha ou convites de amizade públicos, uma variável `APP_PUBLIC_URL=https://leitorum.com` deverá ser configurada no backend para montagem de links absolutos externos.

---

### O que NÃO PRECISA conhecer o domínio `leitorum.com`

1. **Cliente HTTP do Frontend (`frontend/src/services/api.ts`):**
   - Todas as requisições utilizam caminhos relativos (`fetch('/api' + path)`).
   - O navegador direciona automaticamente para a mesma origem em que a página está aberta (`https://leitorum.com/api/...`). Nenhuma alteração é necessária no código de chamadas de API!

2. **Cookies de Sessão (`backend/app/services/session_service.py`):**
   - Ao não declarar o parâmetro `domain`, o cookie é tratado pelo navegador como *Host-only cookie*. Ele se amarra automaticamente a `leitorum.com` quando acessado pelo domínio, e a `127.0.0.1` quando acessado localmente.
   - A flag `Secure` já é ativada dinamicamente quando a requisição vem por HTTPS (`X-Forwarded-Proto`).

3. **CORS (Cross-Origin Resource Sharing):**
   - Não há necessidade de configurar headers de CORS no backend FastAPI para a aplicação web, pois a API e o Frontend compilado são servidos no mesmo processo e sob a mesma origem através de `LocalFrontend`.

4. **Roteador Vue (`frontend/src/router/index.ts`):**
   - O roteador utiliza `createWebHistory()`, que opera de maneira agnóstica em relação ao host, baseando-se exclusivamente no pathname (`/`, `/library`, `/study/123`).

---

## 5. Arquitetura de Infraestrutura: Cloudflare Tunnel

A publicação da aplicação local via Cloudflare Tunnel para o domínio `leitorum.com` oferece a melhor relação de segurança, praticidade e desempenho para aplicações servidas a partir de computadores pessoais.

### Topologia de Rede

```
                                  NUVEM CLOUDFLARE                              COMPUTADOR DO USUÁRIO (WINDOWS)
                               ┌─────────────────────┐                          ┌──────────────────────────────┐
                               │                     │   Conexão de Saída TLS   │                              │
[ Usuário / Celular ] ────────>│  Edge / DNS / SSL   │═════════════════════════>│  cloudflared.exe (Daemon)    │
   https://leitorum.com        │  leitorum.com       │      (Porta 7844/443)    │      │ (Reverse Proxy Local) │
                               │  WAF & DDoS Protect │                          │      ▼                       │
                               │  X-Forwarded-Proto  │                          │  FastAPI (Uvicorn)           │
                               │                     │                          │  http://127.0.0.1:8000       │
                               └─────────────────────┘                          │  (Banco: SQLite WAL)         │
                                                                                └──────────────────────────────┘
```

### Vantagens e Características Técnicas

1. **Zero Exposição de Portas e IP:**
   - O daemon `cloudflared` estabelece uma conexão de **saída** (outbound) persistente para os edge servers da Cloudflare.
   - Nenhuma porta precisa ser aberta no roteador doméstico (sem port forwarding, sem DMZ, imune a varreduras de IP na internet).
   - O IP residencial do usuário permanece completamente anônimo e oculto.

2. **Terminação SSL/TLS Automática:**
   - A Cloudflare gerencia automaticamente a emissão e renovação dos certificados SSL/TLS para `leitorum.com`.
   - O tráfego da internet para a borda da Cloudflare é criptografado com TLS 1.3. O tráfego do túnel para o PC do usuário é encapsulado em túnel criptografado.

3. **Propagação de Cabeçalhos Reversos:**
   - O túnel injeta automaticamente os cabeçalhos padrão de proxy:
     - `X-Forwarded-Proto: https` (permitindo ao backend ativar cookies `Secure=True`).
     - `CF-Connecting-IP` / `X-Forwarded-For` (permitindo auditoria e controle de taxa por IP real no futuro).

4. **Suporte a Conexões Persistentes:**
   - O Cloudflare Tunnel suporta nativamente HTTP/2, HTTP/3, WebSockets e Server-Sent Events (SSE), viabilizando sincronização em tempo real sem qualquer configuração adicional.

5. **Proteção de Camada de Aplicação (WAF / Access):**
   - O usuário pode configurar regras de WAF no painel da Cloudflare para bloquear ataques comuns.
   - É possível aplicar **Cloudflare Access** (autenticação prévia por e-mail/código) especificamente para rotas sensíveis como `/admin` ou `/api/admin/*`, adicionando uma camada de autenticação antes mesmo que a requisição chegue ao computador local.

---

## 6. Mapeamento de Riscos e Diretrizes de Mitigação

Antes de iniciar qualquer refatoração de código, foram mapeados os seguintes riscos críticos, acompanhados de suas respectivas estratégias de mitigação:

### Risco 1: Quebra de Suíte de Testes Automatizados (59 Ocorrências)
- **Problema:** Existem 20 arquivos de teste que contêm asserções estritas sobre nomes e identificadores:
  - `assert app.title == "Caderno de Leitura"`
  - `assert data["service"] == "caderno-leitura"`
  - `assert 'app: "Caderno de Leitura"' in markdown`
  - `assert "caderno_session" in response.headers["set-cookie"]`
  - `assert "caderno.db" in zip_file.namelist()`
- **Mitigação:** Qualquer renomeação no backend deve ser acompanhada da atualização coordenada de suas respectivas asserções nos testes. Os testes nunca devem ser alterados antes do código, nem o código sem atualizar os testes.

### Risco 2: Incompatibilidade com Pacotes de Backup Existentes
- **Problema:** Usuários podem possuir arquivos `.zip` de backup gerados na versão atual. Se o backend passar a exigir `caderno1.db` ou `leitorum.db` dentro do arquivo compactado, backups antigos não poderão mais ser restaurados, violando o princípio fundamental de salvaguarda do acervo.
- **Mitigação:** 
  1. O arquivo interno do banco dentro do ZIP deve permanecer chamado `caderno.db`.
  2. O validador de manifesto (`restore_service.py`) deve aceitar tanto `generator="Caderno de Leitura Backup Engine"` quanto `generator="Leitorum Backup Engine"`.

### Risco 3: Perda de Preferências Locais do Usuário no Navegador
- **Problema:** Se as chaves de `localStorage` forem alteradas abruptamente (ex.: de `caderno.aparencia.v2` para `leitorum.aparencia.v2`), todos os usuários que abrirem o sistema terão seu tema, tamanho de fonte e customizações resetados para o padrão de fábrica.
- **Mitigação:** No script de bootstrap (`appearance-bootstrap.js`), adicionar uma rotina transparente de migração:
  ```javascript
  // Se a chave nova não existe, mas a legada existe, migra os dados
  if (localStorage.getItem('leitorum.aparencia.v2') === null) {
    const legacy = localStorage.getItem('caderno.aparencia.v2');
    if (legacy !== null) {
      localStorage.setItem('leitorum.aparencia.v2', legacy);
    }
  }
  ```

### Risco 4: Quebra de Scripts em Lote do Windows (.cmd / .py)
- **Problema:** Scripts como `INICIAR.cmd`, `INICIAR-REDE.cmd` e `INSTALAR.cmd` contêm caminhos relativos e invocações de arquivos específicos. Se diretórios como `caderno-leitura-0.1` forem renomeados no disco, os atalhos do Windows e scripts de inicialização quebrarão.
- **Mitigação:** Não renomear os diretórios do sistema de arquivos (`c:\Users\User\caderno` e `caderno-leitura-0.1`) nesta fase. A identidade pública e visual da aplicação não depende da renomeação da pasta física no disco.

### Risco 5: Desconexão Abrupta de Sessões Ativas
- **Problema:** A renomeação imediata da chave do cookie de `caderno_session` para `leitorum_session` deslogará todos os usuários ativos.
- **Mitigação:** Implementar tolerância de transição no backend em `app/dependencies.py`: buscar a sessão primariamente no cookie `leitorum_session` e, caso ausente, buscar em `caderno_session`.

### Risco 6: Bloqueio do Login Google em Produção
- **Problema:** Se o usuário tentar realizar login via Google em `https://leitorum.com` sem que o domínio tenha sido adicionado no Google Cloud Console, a biblioteca GSI retornará erro `origin_mismatch`.
- **Mitigação:** Adicionar uma verificação/aviso na documentação e no painel administrativo orientando o registro do domínio no console OAuth antes da ativação pública.

---

## 7. Roteiro Recomendado para as Próximas Etapas

1. **Etapa 1: Aprovação deste Relatório pelo Usuário.**
2. **Etapa 2 (Visual / Não-invasiva):** Iniciar a atualização do Nome Visual (`Leitorum`) no Frontend (`App.vue`, `router/index.ts`, `LoginView.vue`, títulos de páginas).
3. **Etapa 3 (Identidade Gráfica):** Criação e inclusão do Favicon oficial e das Metatags OpenGraph/SEO em `frontend/index.html`.
4. **Etapa 4 (Identificadores Técnicos com Retrocompatibilidade):** Atualização dos identificadores técnicos (`caderno1`), com migração transparente de `localStorage`, fallback de variáveis de ambiente e suporte retrocompatível a backups.
5. **Etapa 5 (Preparação de Infraestrutura):** Configuração externa do Cloudflare Tunnel e credenciais do Google Cloud Console quando for o momento da publicação externa.
