# Research & Technical Decisions: Correções Visuais, de Cor e de Disposição

**Feature**: `075-correcoes-visuais-disposicao`  
**Date**: 2026-10-11  
**Status**: Concluído (Fase 0)

---

## 1. Mapeamento e Resolução da Causa Raiz de Cores (CSS Variables)

### Contexto
O levantamento estático realizado nos arquivos `.vue` do frontend detectou 115 variáveis CSS não declaradas em `tokens.css` nem `palettes.css`, totalizando 1.013 ocorrências em componentes. Como os navegadores não encontram essas variáveis no seletor `:root`, utilizam os valores de fallback estáticos presentes nos componentes (ex.: `#ffffff`, `#6b7280`), quebrando a adaptação visual em temas escuros (Noite Suave, Grafite, Fiorde, Voltagem) e em temas quentes (Pergaminho, Solário).

### Decisão
Criar em `tokens.css` um bloco canônico de **Camada de Compatibilidade de Tokens (F0.8.10)** que mapeia formalmente todos os 115 apelidos legados para as 127 variáveis canônicas oficiais do sistema de temas:
- **Cores de Texto**: `--color-text-muted`, `--text-muted` $\rightarrow$ `var(--color-muted)`; `--color-text-secondary`, `--text-secondary` $\rightarrow$ `var(--color-subtle)`; `--color-text-primary`, `--color-text-main`, `--text`, `--text-main` $\rightarrow$ `var(--color-text)`.
- **Cores de Superfície e Fundo**: `--color-bg`, `--color-background`, `--color-bg-base`, `--color-surface-ground` $\rightarrow$ `var(--color-page)`; `--color-surface-subtle`, `--color-surface-alt`, `--color-bg-subtle`, `--color-bg-alt`, `--color-bg-muted`, `--bg-muted` $\rightarrow$ `var(--color-surface-soft)`; `--color-surface-elevated`, `--card`, `--card-bg`, `--bg-surface`, `--color-card-bg` $\rightarrow$ `var(--color-surface)`.
- **Cores de Destaque e Ações**: `--color-primary`, `--primary`, `--accent`, `--accent-color` $\rightarrow$ `var(--color-accent)`; `--color-primary-hover`, `--accent-hover` $\rightarrow$ `var(--color-accent-hover)`; `--color-primary-light`, `--color-primary-subtle`, `--color-accent-subtle`, `--accent-subtle` $\rightarrow$ `var(--color-selected-bg)`.
- **Estados Semânticos (Erro, Aviso, Sucesso)**: `--color-danger`, `--danger`, `--color-danger-text`, `--color-error` $\rightarrow$ `var(--color-error-text)`; `--color-danger-subtle`, `--color-bg-danger-subtle` $\rightarrow$ `var(--color-error-bg)`; `--color-warning` $\rightarrow$ `var(--color-warning-text)`; `--color-bg-warning`, `--color-warning-subtle` $\rightarrow$ `var(--color-warning-bg)`; `--color-success` $\rightarrow$ `var(--color-success-text)`.
- **Raios e Sombras**: `--radius-sm` $\rightarrow$ `var(--radius-small)`; `--radius-md`, `--radius`, `--radius-surface`, `--border-radius`, `--sc-border-radius` $\rightarrow$ `var(--radius-card)`; `--radius-lg` $\rightarrow$ `var(--radius-panel)`; `--radius-full` $\rightarrow$ `9999px`; `--shadow-sm` $\rightarrow$ sombra suave; `--shadow-surface` $\rightarrow$ `var(--shadow-panel)`.

Adicionalmente, implementar teste automatizado em Node.js (`tests/feature-075-css-tokens-integrity.test.mjs`) que varre todos os componentes `.vue` e valida que 100% das variáveis CSS utilizadas estão presentes no conjunto consolidado de tokens declarados.

### Alternativas Consideradas
1. *Substituir pontualmente as variáveis apenas nos 14 componentes relatados*: Rejeitada. Deixaria centenas de outros modais, listas e telas secundárias vulneráveis a fundos brancos fixos em temas escuros. A camada de compatibilidade em `tokens.css` sana o problema em nível sistêmico para todo o repositório.
2. *Refatorar todos os 961 pontos de código substituindo por nomes canônicos*: Rejeitada para este ciclo. Introduziria um volume massivo de diff de código e risco de regressão desnecessário. A camada de alias CSS possui zero overhead em tempo de execução e resolve todos os cenários.

---

## 2. Correção de Alinhamento de Livros e Capas

### Contexto
- Em `BooksView.vue`, quando a estante possui 1 ou 2 livros, a classe `.book-grid` com `repeat(auto-fit, minmax(..., 1fr))` expande excessivamente as colunas ou centraliza, desalinhando o primeiro livro da margem esquerda da página.
- Em `BookCover.vue`, capas pequenas (`size="sm"`) sem imagem renderizam o texto truncado do título em um espaço de apenas 64px de largura.
- Em `CategoryBadge.vue`, o fundo possui cor fixa cinza clara (`--color-surface-muted, #f1f5f9`), destoando em temas escuros.
- Em `LibraryToolbar.vue`, o botão possui `+` duplo e o seletor Grade/Lista possui fundo branco e botões colados.

### Decisão
1. Em `appearance-advanced.css` / `style.css`, ajustar `.book-grid` no modo grid para utilizar `repeat(auto-fill, minmax(min(100%, 16rem), 1fr))` com `justify-content: start;`, garantindo alinhamento estrito à esquerda quando houver poucos itens.
2. Em `BookCover.vue`, ocultar o elemento `.placeholder-title` quando `size === 'sm'`, exibindo exclusivamente a lombada estilizada e o monograma ou cor base da capa.
3. Em `CategoryBadge.vue`, definir fundo transparente (`background-color: transparent; border: 1px solid var(--color-border); color: var(--color-text);`).
4. Em `BooksView.vue`, remover o `+` textual de `+ Adicionar Livro`, mantendo apenas o ícone `<Icon name="plus" />` e o texto `Adicionar Livro`.
5. Em `LibraryToolbar.vue`, transformar `.view-mode-toggle` em contêiner transparente com espaçamento visível (`gap: 0.35rem; border: none; background: transparent;`) e botões individuais estilizados com borda sutil e raio independente (`--radius-control`).

---

## 3. Visualização e Gestão de Estudos (`/livros/:id`)

### Contexto
- Em `StudyStatusBadge.vue`, as pílulas de status e o menu dropdown possuem fundos fixos claros em temas escuros.
- Em `StudyListView.vue`, cabeçalhos de tabela possuem alinhamentos divergentes e indicadores de ordenação com caracteres ASCII literais (`↑` / `↓`). O botão de desmarcar estudo carece de dimensão mínima tátil.
- Em `StudyTreeNodeItem.vue` e `StudyMapView.vue`, classes de botões e links utilizam `color: var(--color-inverse-bg)` sobre fundos claros ou invertidos, gerando invisibilidade em temas escuros.
- Em `StudyMapView.vue`, a barra móvel de resumo do estudo (`.mobile-map-toolbar`) não possui ocultação padrão para telas desktop.

### Decisão
1. Em `StudyStatusBadge.vue`, definir fundo transparente para selos e opções de status, utilizando borda e texto das variáveis do tema ativo, mais indicadores semânticos distintos (ícone ou forma) para cada estado (Rascunho, Em Estudo, Revisado, Concluído).
2. Em `StudyListView.vue`:
   - Padronizar cabeçalhos de tabela com alinhamento rigoroso à esquerda e hierarquia tipográfica idêntica entre colunas ordenáveis e não ordenáveis.
   - Substituir setas textuais pelo componente `<Icon :name="sortDirection === 'asc' ? 'arrow-up' : 'arrow-down'" :size="14" />`.
   - Garantir área tátil mínima de 44x44px no botão de desmarcar seleção.
3. Em `StudyTreeNodeItem.vue` e `StudyMapView.vue`, banir `color: var(--color-inverse-bg)` em textos e ícones, substituindo por `var(--color-text)` ou `var(--color-on-accent)` quando apropriado.
4. Em `StudyMapView.vue`, aplicar `display: none;` na classe base `.mobile-map-toolbar` e habilitar `display: flex;` exclusivamente dentro de `@media (max-width: 768px)`.

---

## 4. Cabeçalho, Rodapé e Estados Vazios

### Contexto
- Em `AppFooter.vue`, o rodapé possui `justify-content: center` com separadores literais `·` soltos que quebram de linha em telas móveis.
- Em `UserDropdown.vue`, o botão do usuário exibe o nome do usuário fora do avatar e uma seta decorativa redundante.
- Em `EmptyState.vue`, a caixa de ícone e o painel usam variáveis não mapeadas que recaem em `#ffffff`.
- Em `FriendsView.vue`, o estado vazio da aba de bloqueados utiliza markup customizado não centralizado em vez de `<EmptyState>`.

### Decisão
1. Em `AppFooter.vue`, estruturar em dois blocos flexíveis com `justify-content: space-between` em desktop: marca/licença à esquerda e links institucionais à direita. Em telas móveis, aplicar coluna centrada suave sem separadores órfãos.
2. Em `UserDropdown.vue`, simplificar o gatilho para conter unicamente o avatar circular (foto ou iniciais) com área de toque mínima de 44x44px, removendo o texto com o nome externo e a seta inferior.
3. Em `EmptyState.vue`, assegurar uso direto de `var(--color-surface)` para o cartão e `var(--color-surface-soft)` para a moldura do ícone.
4. Em `FriendsView.vue`, substituir a marcação manual da aba de bloqueados pelo componente `<EmptyState icon="ban" ... />`.

---

## 5. Páginas Públicas, Repositório e Persistência do Tema da Visita

### Contexto
- Em `PublicFooter.vue`, o link de código aberto aponta para `https://github.com/leitorum/caderno` em vez do repositório oficial do mantenedor.
- Em `SupportView.vue`, existem cartões com dados bancários vazios ou botões inoperantes caso os métodos PIX não estejam configurados.
- Em `useVisitorTheme.ts`, o hook executa `resetToOriginal()` no `onBeforeUnmount`, fazendo com que qualquer navegação entre `/`, `/sobre` e `/apoie` reverta o tema selecionado na vitrine.

### Decisão
1. Atualizar o link oficial de código aberto em `PublicFooter.vue` e onde mais aplicável para `https://github.com/AntonioBudal/CDL`.
2. Em `SupportView.vue`, reescrever o texto principal e a estrutura visual para destacar com transparência o apoio comunitário, reporte de falhas e contribuição de código no GitHub quando nenhum método de pagamento ativo estiver cadastrado, sem formulários vazios.
3. Em `useVisitorTheme.ts`, remover a reversão destrutiva no `onBeforeUnmount`. Persistir o tema anônimo ativo em `sessionStorage` (chave `caderno_visitor_theme`) para que persista durante a sessão de navegação pública.
4. Em `usePreferences.ts`, assegurar que caso o usuário faça login ou possua preferências salvas na conta, o tema do perfil registrado no banco local continue tendo precedência absoluta.
