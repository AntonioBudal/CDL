# Briefing Executivo — Feature 0.8.10: Correções Visuais, de Cor e de Disposição

**Preparado por**: Claude Code, em 2026-10-11, a partir da lista de bugs do usuário  
**Destino**: Insumo para Antigravity (Spec Kit: `075-correcoes-visuais-disposicao`)  
**Base**: Leitura direta dos componentes em `caderno-leitura-0.1/frontend/src/`  

---

## 1. Resumo e Causa Raiz

A lista de pendências do usuário compreende 14 apontamentos visuais. Destes, 10 decorrem da mesma causa sistêmica: componentes Vue utilizam variáveis CSS que nunca foram declaradas em `tokens.css` nem em `palettes.css`, caindo sempre em fallbacks fixos (como `#ffffff` para fundo ou `#6b7280` para texto):

```css
color: var(--color-text-muted, #6b7280);   /* --color-text-muted não existe -> sempre #6b7280 */
background: var(--color-bg, #ffffff);      /* --color-bg não existe -> sempre branco */
```

### Medições no Código Atual:
- **Variáveis usadas e nunca definidas**: 104 nomes distintos
- **Ocorrências em arquivos `.vue`**: 961 ocorrências
- **Mais frequentes**: `--color-text-muted` (178), `--color-primary` (101), `--color-border-subtle` (95), `--color-text-secondary` (69), `--color-danger` (47), `--color-text-primary` (45), `--color-bg` (21).
- **Arquivos mais impactados**: `LibraryToolbar.vue`, `SupportView.vue`, `DigitizeNotebookView.vue`, `LinkToStudyModal.vue`, `HighlightCard.vue`, `FriendsView.vue`, `HighlightsLibraryView.vue`, `ReviewHubView.vue`.

O sistema oficial de temas define 127 variáveis canônicas (`--color-text`, `--color-muted`, `--color-page`, `--color-surface`, `--color-accent`, `--color-border`...). A solução estrutural consiste em introduzir em `tokens.css` uma camada de compatibilidade mapeando os apelidos obsoletos para as variáveis canônicas correspondentes, complementada por um teste automatizado de integridade CSS e correções pontuais nos componentes específicos.

---

## 2. Cenários de Uso e Histórias Priorizadas

### História 1 — Toda tela legível em qualquer um dos dez temas (P1)
- **Objetivo**: O leitor navega em qualquer tema sem deparar com painéis brancos em paletas escuras ou textos/ícones ilegíveis por falta de contraste.
- **Critérios**: Contraste $\ge 4,5:1$ para textos de interface e $\ge 3:1$ para ícones/bordas de controle; teste automatizado de variáveis indefinidas.

### História 2 — Livros: grade, lista, categorias e barra de ferramentas (P2)
- **Bugs 01, 03, 04, 13**:
  - Grade de livros com poucos itens alinhada à esquerda (`justify-content: start`).
  - Miniatura de capa pequena (`size="sm"`) na lista sem texto cortado (apenas cor da capa e lombada).
  - Selo de categoria com fundo transparente e borda/texto do tema.
  - Botão "Adicionar Livro" com um único sinal de mais (o ícone oficial) e texto limpo.
  - Seletor Grade/Lista com contêiner transparente, botões com espaçamento visível e campo de busca nas cores do tema.

### História 3 — Estudos do livro: grade, lista, árvore e mapa (P2)
- **Bug 07 em `/livros/:id`**:
  - Menu e selo de status (`StudyStatusBadge.vue`) com fundo transparente e diferenciação semântica por ícone/borda.
  - Visão em lista (`StudyListView.vue`): cabeçalhos alinhados com as células, mesmo estilo entre colunas, indicador de ordenação com `<Icon>` sem caracteres ASCII e botão de desmarcar com alvo $\ge 44 \times 44$px.
  - Visão em árvore (`StudyTreeNodeItem.vue`): ícones de ação visíveis nos 3 estados (repouso, hover, foco), corrigindo `color: var(--color-inverse-bg)`.
  - Visão em mapa (`StudyMapView.vue`): ícones do mapa com alto contraste; barra mobile de estudo selecionado ajustada e oculta em desktop.

### História 4 — Cabeçalho, rodapé e estados vazios (P3)
- **Bugs 02, 10, 11, 14**:
  - Rodapé da aplicação (`AppFooter.vue`): `space-between` em desktop, quebra fluida em mobile sem pontuações isoladas.
  - Cabeçalho (`UserDropdown.vue`): gatilho exibe apenas a foto ou iniciais, sem nome duplicado, sem seta e sem fundo cinza fixo, mantendo alvo $\ge 44 \times 44$px e rótulo acessível.
  - Estado vazio de Bloqueados em `FriendsView.vue` centralizado via `EmptyState.vue`.
  - Caixa de ícone em `EmptyState.vue` transparente ou em `--color-surface-soft`, sem caixa branca em temas escuros.

### História 5 — Páginas públicas: link, texto de apoio e tema da visita (P3)
- **Bugs 15, 16**:
  - Link "Código Aberto" em `PublicFooter.vue` e rodapés atualizado para `https://github.com/AntonioBudal/CDL`.
  - Página `/apoie`: texto reescrito com clareza informando que o apoio atual é divulgação e colaboração técnica, sem formulários ou botões de pagamento vazios.
  - Tema da visita: mantido durante toda a sessão de navegação pública nas rotas `/`, `/sobre`, `/apoie`.

---

## 3. Requisitos Funcionais e Diretrizes Técnicas

- **FR-001**: Toda cor em estilo de componente deve provir do sistema de temas. Criação de camada de compatibilidade em `tokens.css` mapeando os 104 apelidos não declarados para as variáveis canônicas correspondentes.
- **FR-002**: Teste automatizado (`npm test`) validando que nenhum arquivo em `src/` utiliza variáveis indefinidas.
- **FR-003**: Mapeamento de variáveis de raio (`--radius-sm`, `--radius-md`, `--radius-lg`) e sombra para as canônicas (`--radius-control`, `--radius-card`, `--radius-panel`).
- **FR-004**: Proibição de uso de variáveis de fundo como cor de texto (ex.: `color: var(--color-inverse-bg)`).
- **FR-005**: Contraste mínimo de 4,5:1 para texto de interface e 3:1 para controles em todos os 10 temas.
- **FR-010 a FR-032**: Correções pontuais dos bugs 01 a 16 conforme especificado.
- **FR-040**: Escopo estritamente restrito ao frontend (zero alterações de schema ou endpoints backend).
- **FR-041**: Zero emojis em 100% dos textos e componentes.
- **FR-042**: Preservação absoluta do acervo privado do usuário.
