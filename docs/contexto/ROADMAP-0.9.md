# Roadmap 0.9 — Revisão Geral de UI/UX, Ergonomia e Estabilização

**Data oficial de emissão:** 2026-10-18  
**Status do Roadmap:** Planejado para desenvolvimento com o GitHub Spec Kit (`speckit`).  
**Regra Geral de Estado:** Todas as cinco features (**F01 a F05**) estão estritamente **NÃO INICIADAS**.  
Nenhum código preliminar, patch ou documento prévio altera o status de qualquer entrega deste roadmap. O avanço ocorre exclusivamente através de ciclos delimitados do fluxo Spec Kit (`speckit-specify` → `speckit-clarify` → `speckit-plan` → `speckit-tasks` → `speckit-analyze` → `speckit-implement`), resultando em **1 Commit Atômico por Feature Validada** com suítes de testes (`npm test`, `pytest`, `npm run build`) 100% aprovadas.

---

## 1. Visão Geral, Princípios de Engenharia e Escopo

O **Caderno de Leitura (Leitorum)** consolidou em suas versões anteriores (0.1 a 0.8) uma rica fundação técnica: multiusuário com Argon2id, autenticação híbrida (Google GIS e credenciais locais), sincronização em rede local/Tailscale, ACL granular de compartilhamento, repetição espaçada, oclusão de texto e 10 temas cromáticos.

A versão **0.9** é uma versão de **estabilização profunda e refinamento ergonômico**:
> **O objetivo não é adicionar novas funcionalidades, modelos de dados ou migrações de schema, mas aperfeiçoar rigorosamente a experiência, usabilidade, responsividade móvel, acessibilidade (WCAG AA) e consistência visual de todas as telas já existentes.**

### Princípios Fundamentais da Versão 0.9

1. **Delimitação Estrita de Escopo (Zero Novas Funcionalidades):**
   - É proibido criar novos endpoints de negócio, novas tabelas no SQLite ou alterar modelos conceituais.
   - Todo o esforço concentra-se na casca de aplicação (*App Shell*), componentes de visualização, alinhamentos de layout, alvos de toque, estados de interface e contraste.

2. **Ergonomia e Densidade Móvel em Primeiro Plano:**
   - Em dispositivos móveis, a área de leitura e o conteúdo central nunca devem ser espremidos por cabeçalhos inflados, rodapés analíticos estáticos ou sobreposição de barras fixas.
   - Alvos de toque (*touch targets*) em telas táteis devem possuir no mínimo 44x44px, respeitando as diretrizes WCAG 2.5.5.

3. **Imunidade Cromática e Respeito aos 10 Temas Oficiais:**
   - O Leitorum possui 10 temas canônicos (`sepia`, `classico`, `noturno`, `nordico`, `floresta`, `aurora`, `crepusculo`, `pergaminho`, `editorial`, `monocromatico`).
   - Nenhuma cor hexadecimal fixa (`#ffffff`, `#1e293b`, etc.) pode ser utilizada em classes de badges, tabelas ou avisos. Toda a estilização deve amarrar-se estritamente aos tokens CSS semânticos globais (`--color-text`, `--color-surface`, `--color-border`, `--color-accent`, etc.).

4. **Transparência e Resiliência de Estados da Interface:**
   - Nenhuma tela pode apresentar transições com texto estático cru ("Carregando…"). Todas devem utilizar telas esqueleto ([`LoadingSkeleton.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/ui/LoadingSkeleton.vue)) espelhando a geometria final.
   - Todos os estados vazios devem utilizar [`EmptyState.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/ui/EmptyState.vue) com título acolhedor, explicação pedagógica e pelo menos um botão de ação primária (CTA).

5. **Proteção Operacional contra Ações Destrutivas:**
   - Botões de descarte (como "Mover para a lixeira") nunca devem estar no mesmo grupo de clique rápido de ações frequentes (como "Editar estudo"), prevenindo toques acidentais em telas touch.

---

## 2. O que NÃO faz parte da Versão 0.9 (Fora de Escopo)

Para assegurar a entrega pontual e a estabilidade arquitetural, os seguintes pontos estão **expressamente fora de escopo**:

- **Novas Rotas de Navegação:** Nenhuma rota nova será registrada em `router/index.ts`. O trabalho aprimora as 25 rotas existentes.
- **Novas Migrações Alembic ou Alterações no Banco de Dados:** O schema ativo no SQLite permanece intacto. Nenhuma coluna ou tabela nova será introduzida.
- **Reintrodução de MapView, CanvasView ou TreeView:** As visualizações de grafos experimentais removidas no commit `7398da2` não serão restauradas. O acervo mantém seu foco funcional em `StudyGridView` e `StudyListView`.
- **Novas Paletas de Cores ou 11º Tema:** O sistema mantém exatamente os 10 temas canônicos estabelecidos, focando apenas em assegurar contraste perfeito entre eles.
- **Bibliotecas Externas de UI Pesadas:** Proibida a inclusão de frameworks utilitários volumosos que aumentem o bundle. Toda a estilização apoia-se em CSS moderno e componentes nativos Vue 3.

---

## 3. Quadro Oficial de Status das Features da Versão 0.9

| ID | Feature | Frente de Aperfeiçoamento | Escopo e Impacto | Status |
| :--- | :--- | :--- | :--- | :--- |
| **F01** | **Arquitetura de Navegação Global e Shell Responsivo** | Navegação Desktop e Mobile | Desacoplar "Dashboard" e "Livros" na barra superior; coordenar `--mobile-nav-offset` contra cortes no rodapé; criar componente universal `AppBreadcrumb.vue`. | **CONCLUÍDA** |
| **F02** | **Ergonomia Mobile e Descongestionamento da Página do Livro** | Página do Livro (`/livros/:bookId`) | Redesenhar cabeçalho compacto no mobile; unificar seletor de capítulos sem duplicidade; tornar o inspetor analítico recolhível. | **CONCLUÍDA** |
| **F03** | **Segurança Operacional e Refinamento do Leitor de Estudos** | Leitor de Estudo (`/livros/:bookId/estudos/:studyId`) | Isolar ação de lixeira em menu contextual suspenso; assegurar alvos de toque >= 44x44px; indicador persistente de rascunho salvo no editor. | **CONCLUÍDA** |
| **F04** | **Correções Estruturais nas Visualizações do Acervo** | Visualizações em Lista e Grade | Eliminar corte (*clipping*) do dropdown de status na tabela; corrigir visibilidade do ícone de ordenação com `stroke: currentColor`; alinhar colunas da lista. | **NÃO INICIADA** |
| **F05** | **Acessibilidade, Imunidade Cromática e Padronização de Estados** | Sistema Visual, Estados e WCAG | Erradicar cores hexadecimais em badges e avisos; converter mensagens de carregamento em skeletons fiéis; enriquecer estados vazios e página 404 com CTAs. | **NÃO INICIADA** |

---

## 4. Detalhamento Técnico das Features

---

### F01 — Arquitetura de Navegação Global e Shell Responsivo

**Status: CONCLUÍDA.**

Unificar e estabilizar a navegação principal da aplicação tanto no computador quanto em dispositivos móveis, eliminando restrições que escondem o acervo e corrigindo a sobreposição de elementos na casca do sistema.

#### Problemas Resolvidos
- Em [`NavigationTabs.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/layout/NavigationTabs.vue), quando o usuário define a preferência inicial como "Dashboard", a aba "Livros" desaparece da barra desktop, impedindo acesso direto ao acervo.
- A barra inferior fixa móvel ([`MobileTabBar.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/layout/MobileTabBar.vue)) sobrepõe o final dos conteúdos e o rodapé ([`.app-footer`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/App.vue)) em telas verticais longas.
- Múltiplas telas utilizam implementações ad-hoc de breadcrumbs que apontam para caminhos inconsistentes.

#### Escopo de Implementação
1. **Navegação Desktop Unificada:**
   - Atualizar `primaryNavItems` em `NavigationTabs.vue` para conter simultaneamente "Dashboard" (apontando para `/dashboard`) e "Livros" (apontando para `/livros`).
   - A preferência `caderno_home_view` passa a governar unicamente o destino do logotipo "Leitorum" e a rota de redirecionamento de login, sem nunca ocultar abas primárias da barra superior.
2. **Coordenação de Offset Móvel no App Shell:**
   - Centralizar no container `#conteudo` em [`App.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/App.vue) uma margem inferior calculada (`padding-bottom: calc(var(--mobile-nav-offset, 56px) + env(safe-area-inset-bottom, 0px) + 1.5rem)`) ativa apenas em resoluções `<= 767px` e quando o usuário estiver autenticado e fora do modo `cleanScreen`.
   - Assegurar que o rodapé `.app-footer` e formulários com botões fixos fiquem plenamente visíveis acima da barra de abas móvel.
3. **Componente Universal `AppBreadcrumb.vue`:**
   - Criar componente reutilizável em `components/ui/AppBreadcrumb.vue` com suporte a itens tipados `{ label: string, to?: string | RouteLocationRaw, current?: boolean }`.
   - Adotar atributos semânticos `aria-label="Trilha de navegação"` e `aria-current="page"`.
   - Substituir os breadcrumbs dispersos em `BookView.vue`, `StudyView.vue`, `StudyEditView.vue` e `UserProfileView.vue`.

#### Critérios de Aceitação
- [x] Usuário consegue navegar diretamente entre "Dashboard" e "Livros" na barra desktop com 1 clique a partir de qualquer página interna.
- [x] Em dispositivos móveis (360px a 767px de largura), todo o conteúdo final de qualquer página e o rodapé global terminam acima da barra inferior fixa, sem sobreposição nem corte visual.
- [x] O componente `AppBreadcrumb.vue` é utilizado de forma homogênea nas páginas de Livro, Estudo e Edição, exibindo hierarquia visual clara sem desvios incorretos para a raiz `/`.

---

### F02 — Ergonomia Mobile e Descongestionamento da Página do Livro

**Status: CONCLUÍDA.**

Redesenhar a composição espacial da página do livro ([`BookView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/BookView.vue)), reduzindo drasticamente o consumo vertical do cabeçalho em telas pequenas e otimizando a transição entre capítulos e estudos.

#### Problemas Resolvidos
- Em telas móveis, o cabeçalho do livro empilha capa grande, título, autor, categorias e 4 botões de ação em formato de pílula horizontal.
- Imediatamente abaixo, a faixa de capítulos renderiza simultaneamente um seletor dropdown nativo e uma esteira rolável de botões, consumindo mais de 600px de altura vertical antes do primeiro card de estudo.
- A faixa inferior do inspetor analítico repete dados já visíveis no topo, ocupando espaço sem agregar valor dinâmico.

#### Escopo de Implementação
1. **Cabeçalho Compacto do Livro no Mobile:**
   - No breakpoint `@media (max-width: 767px)`, reorganizar o cabeçalho do livro em formato condensado de linha dupla:
     - Linha 1: Miniatura da capa (48x72px), título do livro com truncamento inteligente e autor.
     - Linha 2: Chips de categoria compactos e botão de ações agrupadas ("Ações do Livro ▾" abrindo modal/drawer com Exportar, Editar e Lixeira).
2. **Unificação da Faixa de Capítulos:**
   - No mobile, exibir seletor elegante e aderente (*sticky*) com o nome do capítulo ativo, contador de estudos e botão discreto de novo capítulo inline.
   - Suprimir a duplicação entre `<select>` nativo e pílulas roláveis no celular, mantendo a experiência fluida sem saltos visuais.
3. **Inspetor Analítico Recolhível:**
   - Converter a faixa inferior ([`inspector-horizontal-bar`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/BookView.vue#L664-L720)) em uma barra de contexto colapsável por padrão no celular, com botão discreto "Ver detalhes do livro ▾", liberando 100% do foco para a grade ou lista de estudos.

#### Critérios de Aceitação
- [x] Em viewport de 390x844px (padrão móvel), o primeiro card de estudo cadastrado ou a mensagem orientadora é visível imediatamente na primeira dobra da tela (sem necessidade de rolagem vertical prévia).
- [x] O seletor de capítulos móvel permite alternar entre capítulos com no máximo 2 toques e sem quebras visuais.
- [x] Os botões de ação do livro (Editar, Exportar, Lixeira) permanecem acessíveis via menu contextual sem poluir a área superior.

---

### F03 — Segurança Operacional e Refinamento do Leitor de Estudos

**Status: CONCLUÍDA.**

Proteger o fluxo de estudo ativo contra descartes acidentais no leitor ([`StudyView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/StudyView.vue)), calibrar alvos de toque ergonômicos e aprimorar o feedback de persistência no editor ([`StudyEditView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/StudyEditView.vue)).

#### Problemas Resolvidos
- No cabeçalho do estudo, a ação destrutiva de exclusão ("Mover para a lixeira") fica posicionada ao lado dos botões de compartilhamento, exportação, histórico e edição, gerando alto risco de clique acidental em dispositivos móveis e touchscreens.
- O editor de estudos salva rascunhos localmente via localStorage e detecta conflitos, mas não exibe ao leitor uma indicação visual imediata e confiável do estado de salvamento.

#### Escopo de Implementação
1. **Menu Contextual de Ações Secundárias no Leitor:**
   - No cabeçalho de `StudyView.vue`, manter em destaque primário apenas o botão "Editar estudo" e a pílula de status de leitura.
   - Encapsular "Compartilhar", "Exportar", "Histórico de Versões" e a ação destrutiva "Mover para a Lixeira" em um menu suspenso contextual acionado por botão de ícone ("Mais opções ▾").
   - A ação de lixeira deve ter destaque visual diferenciado (texto com cor de alerta) e confirmação obrigatória via [`TrashConfirmModal.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/TrashConfirmModal.vue).
2. **Alvos de Toque Ergonômicos (WCAG 2.5.5):**
   - Garantir que todos os botões de ação do cabeçalho, da barra de leitura ativa ([`ActiveReadingBar.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/ActiveReadingBar.vue)) e das abas de estudo ([`StudyTabs.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/StudyTabs.vue)) possuam área de toque mínima de 44x44px em ponteiros táteis.
3. **Indicador Visual de Rascunho no Editor:**
   - Em `StudyEditView.vue`, adicionar pílula sutil de status ao lado do título:
     - "Rascunho salvo neste navegador" (quando houver alterações salvas localmente no localStorage).
     - "Alterações salvas" (quando o estudo for sincronizado com o servidor).
     - "Salvando…" (durante a requisição assíncrona).

#### Critérios de Aceitação
- [x] Ação de lixeira não é acionável por clique simples inadvertido no cabeçalho de leitura, residindo protegida dentro do menu contextual com confirmação por modal.
- [x] Todos os botões clicáveis da tela de leitura atendem ao critério de tamanho mínimo de 44x44px sob `@media (pointer: coarse)`.
- [x] O leitor visualiza feedback claro e em tempo real sobre a preservação de seu rascunho durante a edição de textos longos.

---

### F04 — Correções Estruturais nas Visualizações do Acervo

**Status: CONCLUÍDA.**

Corrigir problemas de layout, corte de menus e alinhamento responsivo nas duas visualizações ativas do acervo: [`StudyListView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue) e [`StudyGridView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/views/StudyGridView.vue).

#### Problemas Resolvidos
- Ao abrir o menu dropdown de status (`.status-dropdown-menu`) na tabela da lista de estudos, o menu é cortado pelas bordas da linha ou do contêiner pai devido a propriedades de `overflow: hidden`.
- O ícone SVG de ordenação (`.sort-indicator`) no cabeçalho da tabela perde contraste ou fica invisível dependendo do tema ativo.
- Em telas largas (acima de 1440px), as colunas do cabeçalho da lista sofrem desalinhamento visual em relação às células correspondentes do corpo da tabela.

#### Escopo de Implementação
1. **Eliminação de Corte (*Clipping*) do Dropdown de Status:**
   - Em `StudyListView.vue`, auditar a árvore de elementos da tabela removendo regras de `overflow: hidden` desnecessárias nas linhas e contêineres que restringem a sobreposição.
   - Implementar teletransporte com `<Teleport to="body">` para o menu suspenso ou ajustar coordenadas de posicionamento absoluto e `z-index: 1000`, garantindo flutuação livre sobre a tabela.
2. **Ícone de Ordenação e Herança de Cor:**
   - Definir `stroke: currentColor` e `fill: none` no SVG de ordenação do cabeçalho da lista, garantindo que o ícone herde com exatidão a cor do texto do rótulo da coluna.
3. **Alinhamento Geométrico Estrito do Grid da Tabela:**
   - Padronizar as regras de grid/flexbox entre `.list-header-row` e `.list-row` para utilizar as mesmas frações de largura em todas as resoluções (Título: 4fr, Localização: 2fr, Status: 2fr, Data: 1.5fr, Ações: 1fr).
   - Centralizar verticalmente os conteúdos de cabeçalho (`display: flex; align-items: center;`).

#### Critérios de Aceitação
- [x] O menu suspenso de status na visualização em lista abre livremente em qualquer linha (incluindo primeira e última linha) sem cortes na borda superior ou inferior.
- [x] O ícone de ordenação da coluna ativa é nitidamente legível e consistente com o texto do cabeçalho em todos os 10 temas do sistema.
- [x] As colunas do cabeçalho e do corpo da tabela mantêm alinhamento estrito e harmonioso em resoluções de 1024px até 2560px.

---

### F05 — Acessibilidade, Imunidade Cromática e Padronização de Estados

**Status: NÃO INICIADA.**

Garantir conformidade rigorosa de acessibilidade (WCAG AA), imunidade cromática nos 10 temas oficiais e experiência previsível em todos os estados de carregamento, erro e vazio.

#### Problemas Resolvidos
- Existência de valores de cores hexadecimais fixos em badges e avisos que quebram o contraste sobre fundos escuros (`noturno`, `crepusculo`, `nordico`) ou fundos texturizados (`pergaminho`, `sepia`).
- Mensagens de carregamento estáticas e toscas em certas páginas secundárias.
- Estados vazios sem direcionamento pedagógico e página 404 desprovida de identidade e atalhos.

#### Escopo de Implementação
1. **Erradicação de Cores Hexadecimais Fixas:**
   - Varrer todos os componentes de estilo e arquivos CSS eliminando cores fixas em `.status-pill-small`, `.badge-rascunho`, `.badge-em-estudo`, `.badge-revisado`, `.badge-concluido` e `.notice.error`.
   - Mapear todas as estilizações para variáveis semânticas dos temas:
     - Fundo de badge: `var(--color-surface-hover)` ou `var(--color-muted-bg)`.
     - Texto de badge: `var(--color-text)` ou `var(--color-text-emphasis)`.
     - Borda de badge: `var(--color-border)`.
2. **Padronização Universal com `LoadingSkeleton.vue`:**
   - Substituir mensagens em texto "Carregando…" em [`StudyEditView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/StudyEditView.vue#L123), [`UserProfileView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/UserProfileView.vue#L70) e [`AdminView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/AdminView.vue) por estruturas fiéis do componente `LoadingSkeleton.vue`.
3. **Qualificação de Estados Vazios e Redesenho da Página 404:**
   - Garantir que a biblioteca de destaques ([`HighlightsLibraryView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/HighlightsLibraryView.vue)) utilize `EmptyState.vue` com ação de "Limpar filtros" ou "Como criar anotações".
   - Refatorar [`NotFoundView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/NotFoundView.vue) integrando `EmptyState.vue` com ilustração/ícone de livro, mensagem amigável e botões direcionando para "Ir para o Acervo" e "Ir para o Dashboard".
4. **Regiões `aria-live` em Transições Assíncronas:**
   - Adicionar regiões de anúncio polido para leitores de tela em sessões de estudo ([`StudySessionView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/StudySessionView.vue)) e durante salvamentos automáticos de notas.

#### Critérios de Aceitação
- [ ] A relação de contraste entre texto e fundo em todos os badges, botões e alertas é igual ou superior a 4.5:1 em todos os 10 temas oficiais (verificado com analisador WCAG).
- [ ] Nenhuma tela exibe mensagem de texto desformatada durante carregamentos de dados assíncronos.
- [ ] A página 404 segue a identidade do sistema e oferece links de retorno funcionais com 1 clique.

---

## 5. Ordem de Execução e Convenção de Commits Git

Seguindo a política de governança do projeto, cada feature será implementada de maneira estritamente sequencial, isolada e atômica. 

Cada entrega conclui-se obrigatoriamente com a execução bem-sucedida das suítes de validação automatizada (`npm test`, `pytest`, `npm run build`), gerando exatamente **1 Commit por Feature**:

```
F01 └── feature — arquitetura de navegação global e shell responsivo
F02 └── feature — ergonomia mobile e descongestionamento da página do livro
F03 └── feature — segurança operacional e refinamento do leitor de estudos
F04 └── feature — correções estruturais nas visualizações do acervo
F05 └── feature — acessibilidade, imunidade cromática e padronização de estados
```

Ao término de F05, o marco da versão **0.9** estará formalmente consolidado.
