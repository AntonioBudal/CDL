# Contrato de Decisões de Responsividade e Matriz de Cobertura

**Feature**: `076-estrategia-responsiva`  
**Escopo**: Mapeamento oficial de 100% das 25 rotas nomeadas de `caderno-leitura-0.1/frontend/src/router/index.ts`, das 5 visualizações de estudos, do shell compartilhado e dos overlays globais.

---

## 1. Classificação Canônica de Estratégia de Adaptação

| Código | Significado | Descrição |
|---|---|---|
| **1** | Adaptação Integral | Layout fluido que funciona identicamente em todas as viewports apenas com regras de fluxo e grids auto-ajustáveis. |
| **2** | Reorganização de Interface | Elementos reordenados, recolhidos em gavetas/menus ou dispostos verticalmente sem perda de recursos. |
| **3** | Versão Móvel Simplificada | Interface principal apresentada em modo adaptado/linear (ex.: lista semântica), mantendo recursos críticos em abas/modais. |
| **4** | Desktop com Alternativa Móvel | Ferramenta complexa disponível integralmente em tablets/desktops (≥768px), fornecendo alternativa direta (outline/lista) no celular. |
| **5** | Sem Alteração Necessária | Telas centralizadas com largura contida (máx. 420–500px) que já atendem todas as viewports por construção. |

---

## 2. Matriz de Cobertura por Rota Nomeada

| Nome da Rota (`name`) | Caminho (`path`) | Classificação | Justificativa de Engenharia e Recursos a Preservar |
|---|---|:---:|---|
| `landing` | `/` | **1** | Página de apresentação com seções de texto e cards. Preservar responsividade de grids em 320px (`minmax(min(280px, 100%), 1fr)`). |
| `about` | `/sobre` | **1** | Conteúdo textual editorial e pilares metodológicos. Fluido por construção com `max-width: 68ch`. |
| `support` | `/apoie` | **1** | Painéis de apoio e cópia de chave PIX. Preservar alvos táteis mínimos de 44px para o botão de cópia. |
| `login` | `/login` | **5** | Formulário de autenticação contido com `max-width: 420px`. Totalmente fluido. |
| `register` | `/registro` | **5** | Formulário de criação de conta contido com `max-width: 420px`. |
| `setup-owner` | `/primeiro-acesso` | **5** | Assistente de primeiro acesso contido com `max-width: 420px`. |
| `dashboard` | `/dashboard` | **1** | Cockpit analítico com abas, cartões métricos e heatmap rolável horizontalmente por intenção. |
| `books` | `/books` (alias `/livros`) | **1** | Acervo de livros. Em `<640px` toolbar empilha e grade adota coluna única (`auto-fill`). |
| `book` | `/livros/:id` | **2** | `BookView` com `SplitLayout`. Gaveta de capítulos nasce fechada no mobile por padrão; ações secundárias agrupadas em menu dropdown. |
| `study` | `/livros/:bookId/estudos/:studyId` | **2** | Visualização de estudo completo. Toolbar flutuante de leitura ativa, alternador de modo foco e popover de anotações. |
| `study-direct` | `/estudos/:studyId` | **2** | Redirecionamento e abertura direta de estudo resolvendo contexto de livro. |
| `study-edit` | `/livros/:bookId/estudos/:studyId/editar` | **1** | Editor de fichamento. Formulário de 4 seções com toolbar de formatação rolável e blindagem contra teclado virtual. |
| `study-session` | `/estudo/sessao/:sessionId` | **1** | Modo de sessão concentrada (`cleanScreen` ativo, sem header ou footer). Totalmente imersivo e fluido. |
| `highlights` | `/highlights` (alias `/destaques`) | **1** | Biblioteca de passagens e notas. Filtros colapsáveis no mobile com botão de gatilho dedicado. |
| `review` | `/review` (alias `/revisao`) | **1** | Central de revisão com fichas de memorização e gatilho de sessão. |
| `inbox` | `/inbox` | **1** | Mesa de triagem e capturas rápidas. Lista fluida com processamento individual e em lote. |
| `friends` | `/amigos` | **1** | Gestão de conexões sociais e salão literário. Grids de amigos adaptados para `min(280px, 100%)`. |
| `user-profile` | `/@:username` | **1** | Perfil público de leitor e lista de estudos compartilhados com alvos táteis acessíveis. |
| `settings` | `/ajustes` | **2** | Central de ajustes com abas roláveis horizontalmente e botão flutuante (FAB) de preview posicionado acima da barra inferior. |
| `trash` | `/lixeira` | **1** | Lixeira com restauração e expurgo. Barra de lote fixa posicionada respeitando `--mobile-nav-offset`. |
| `connection` | `/conexao` | **5** | Tela de sincronização P2P e pareamento móvel com QR code centralizado. |
| `digitize-notebook` | `/digitalizar` (alias `/scan`) | **5** | Captura óptica de cadernos físicos e importação fotográfica. |
| `import` | `/importar` | **2** | Ateliê de importação e parsing. Em telas `<1024px`, os dois painéis alternam como abas de visualização. |
| `admin` | `/admin` | **3** | Painel de controle e governança. Tabela de 8 colunas convertida em cards no mobile para permitir moderação de contas por toque. |
| `shared-study` | `/compartilhado/:token` | **1** | Visualização pública isolada de estudo compartilhado sem dependência de autenticação. |

---

## 3. Estratégia Detalhada para as Visualizações Especializadas de Estudos

### 3.1 Map View (`StudyMapView.vue`) — Classificação 3 (Versão Móvel Simplificada)
1. **Diagnóstico**: Grafo conceitual radial calculado em torno de um estudo-núcleo em dois anéis. Palco fixo em 800×560px com interação via mouse.
2. **Limitações Móveis**: Inacessibilidade dos nós periféricos em viewports estreitas e badges SVG pequenos para dedos humanos.
3. **Alternativas Avaliadas**: Apenas lista (perda da noção de rede) vs Adaptar integralmente com gestos (ilegível em 375px).
4. **Recomendação Híbrida**:
   - Em `<768px`, a apresentação padrão é a **Lista de Conexões Semânticas**: o estudo-núcleo em destaque no topo, seguido pelos estudos agrupados por anel com seus graus e relações explícitas.
   - Alternador "Lista | Grafo" permite transitar para o panorama gráfico, com encaixe na largura, pan com um dedo e pinch com dois dedos sem prender a rolagem externa.
5. **Funções Mantidas no Celular**: Consultar rede de argumentos, abrir estudos, criar conexões táteis (toque na origem $\to$ "Conectar a..." $\to$ toque no destino), editar/excluir relações via lista, criar novos estudos.
6. **Funções Reorganizadas**: Popover de relação exibido como bottom sheet inferior; edição disparada a partir da linha da lista.
7. **Funções Restringidas no Celular**: Arrastar alça elástica pelo canvas e duplo-clique no vazio.
8. **Arquivos Afetados**: `StudyMapView.vue`, `map/MapConnectionsList.vue`, `MapRelationPopover.vue`, `MapQuickCreateCard.vue`.

### 3.2 Canvas View (`StudyCanvasView.vue`) — Classificação 4 (Desktop com Alternativa Móvel)
1. **Diagnóstico**: Quadro espacial livre de 20.000×20.000px com cartões de 280×200px, molduras temáticas e conexões vetoriais.
2. **Limitações Móveis**: Em 375px cabe apenas um cartão na largura. Manipular o arranjo de dezenas de cartões em tela de smartphone não traz valor ergonômico.
3. **Recomendação**:
   - Em `<768px`: A aba exibe aviso curto e claro acompanhado de **Lista Estruturada por Molduras** (estudos agrupados por moldura física e seção de avulsos), permitindo leitura imediata e envio à lixeira sem arrasto.
   - Em `768–1023px` (Tablet): Canvas completo com suporte tátil: pinch-zoom com 2 dedos, botão dedicado de "Seleção em Bloco" na toolbar (sem exigir tecla Shift), alças de redimensionamento ampliadas para 44px em `pointer: coarse`.
4. **Pertinência Estudo↔Moldura**: Calculada estritamente no cliente por intersecção retangular geométrica (`moveFrameSolidary`), dispensando novas chamadas ao backend.
5. **Arquivos Afetados**: `StudyCanvasView.vue`, `canvas/CanvasMobileOutline.vue`, `CanvasToolbar.vue`, `useCanvasViewport.ts`.

### 3.3 Tree View (`StudyTreeNodeItem.vue` / `StudyTreeView.vue`) — Classificação 2 (Reorganização Leve)
1. **Diagnóstico**: Lista hierárquica aninhada com até 5 níveis de profundidade, progressão por ramo e reordenação.
2. **Limitações Móveis**: Em níveis profundos, a indentação excessiva estrangula a largura útil do título; alça de arrasto visível em tablets com toque.
3. **Recomendação**:
   - Manter a árvore como estrutura nativa em todas as telas.
   - Reduzir a indentação por nível usando `clamp(0.4rem, 1.5vw, 1rem)`.
   - Mover botão de exclusão e leitura para o menu contextual da linha ("⋯") em telas estreitas, liberando espaço para o título.
   - Permitir até 2 linhas de texto no título antes de aplicar reticências.
   - Ocultar alça de arrasto estritamente via `@media (pointer: coarse)`.
4. **Arquivos Afetados**: `StudyTreeNodeItem.vue`, `StudyTreeView.vue`.

---

## 4. Shell e Overlays Globais

### 4.1 Shell Global (Header e Navegação) — Classificação 2
- Restaurar a barra inferior móvel fixa (`MobileTabBar` / `.navigation-tabs` adaptada) com 5 destinos (Início, Livros, Destaques, Revisão e menu "Mais").
- Limpar o cabeçalho superior móvel para exibir apenas o logo Leitorum, busca, captura rápida, notificações e avatar.
- Gaveta móvel "Mais" expandida para incluir todas as rotas secundárias (Inbox, Amigos com contagem, Ajustes, Lixeira, Importar).

### 4.2 Overlays Globais (Modais e Notificações) — Classificação 1
- `NotificationsDropdown`: em telas `<430px`, expandir para largura total da tela (`left: 0; right: 0; width: 100%`) com padding de segurança.
- Modais com formulários: transição de `vh` para `dvh` com `max-height: min(90dvh, 720px)`.
- `ShareModal.vue`: reescrito com tokens CSS nativos do projeto sem qualquer classe Tailwind.
