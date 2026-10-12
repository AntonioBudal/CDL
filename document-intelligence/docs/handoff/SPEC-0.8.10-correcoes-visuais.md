# Especificação (rascunho) — Feature 0.8.10: correções visuais, de cor e de disposição

* **Preparado por:** Claude Code, em 2026-10-11, a partir da lista de bugs do usuário
* **Destino:** insumo para o Antigravity rodar `speckit.specify` (próxima pasta livre em `specs/`: a última vista foi
  `074-manifesto-leitor-reflexivo`). Não altera código.
* **Base:** leitura (sem alteração) dos componentes citados em cada bug, em `caderno-leitura-0.1/frontend/src/`.
* **Numeração:** mantive os números da lista original; não há bugs 08 e 09. No bug 02 o trecho de HTML colado era o
  mesmo do bug 01 (capa do livro); usei a descrição em texto.

---

## 1. Resumo e causa raiz

A lista tem 14 bugs. Dez deles são do mesmo tipo: **cores que não acompanham o tema** (fundo branco em tema escuro,
texto escuro sobre fundo escuro, ícone da cor do botão, borda branca).

Investigando o código, a causa é uma só. Os componentes usam variáveis de cor que **nunca foram definidas** em
`tokens.css`, `palettes.css` nem em lugar algum, sempre com uma cor fixa de reserva:

```css
color: var(--color-text-muted, #6b7280);   /* --color-text-muted não existe → sempre #6b7280 */
background: var(--color-bg, #ffffff);      /* --color-bg não existe → sempre branco */
```

Como a variável não existe, o navegador usa a cor de reserva em **todos** os temas. Medição no código atual:

| Medida | Valor |
| :--- | ---: |
| Variáveis usadas e nunca definidas | 104 nomes |
| Ocorrências em arquivos `.vue` | 961 |
| Mais frequentes | `--color-text-muted` (178), `--color-primary` (101), `--color-border-subtle` (95), `--color-text-secondary` (69), `--color-danger` (47), `--color-text-primary` (45), `--color-bg` (21) |
| Arquivos mais afetados | `LibraryToolbar.vue` (35), `SupportView.vue` (29), `DigitizeNotebookView.vue` (29), `LinkToStudyModal.vue` (28), `HighlightCard.vue` (25), `FriendsView.vue` (24), `HighlightsLibraryView.vue` (20), `ReviewHubView.vue` (20) |

O sistema de temas define 127 variáveis canônicas (`--color-text`, `--color-muted`, `--color-page`,
`--color-surface`, `--color-accent`, `--color-border`…), e os dez temas só redefinem essas.

**Consequência para a feature:** corrigir tela por tela resolveria os sintomas relatados e deixaria centenas de
outros iguais (modais, caixa de entrada, sessão de estudo, administração). A especificação propõe corrigir a causa
e depois os casos pontuais.

Um segundo padrão, menor: cor de fundo usada como cor de texto. Exemplo em `StudyTreeNodeItem.vue`: o botão de
ações usa `color: var(--color-inverse-bg)` sobre `--color-surface-hover`; em tema escuro, ícone e fundo ficam
quase iguais.

---

## 2. Cenários de uso e testes

### História 1 — Toda tela legível em qualquer um dos dez temas (P1)

Como leitor, escolho um tema e todas as telas o respeitam: nenhum painel branco em tema escuro, nenhum texto ou
ícone que suma no fundo.

**Por que P1:** é a causa de dez dos catorze bugs e afeta telas que não foram relatadas.

**Teste independente:** percorrer as telas da seção 4 nos dez temas e medir contraste; rodar o teste automático de
variáveis indefinidas (FR-002).

**Cenários de aceite:**
1. **Dado** um tema escuro (`noite-suave`, `grafite`, `fiorde`, `voltagem`), **quando** abro Destaques, Revisão,
   Lixeira vazia, Dashboard, Livros e Apoie, **então** nenhum contêiner tem fundo branco ou claro fixo.
2. **Dado** qualquer tema, **quando** olho textos e ícones de interface, **então** o contraste é ≥ 4,5:1 para texto
   e ≥ 3:1 para ícones e bordas de controles.
3. **Dado** o tema `pergaminho`, **quando** abro Destaques e Apoie, **então** os cartões não destoam do papel.

### História 2 — Livros: grade, lista, categorias e barra de ferramentas (P2)

Bugs 01, 03, 04 e 13.

**Cenários de aceite:**
1. **Dado** a grade de livros com poucos itens, **quando** a linha não está cheia, **então** os livros ficam
   alinhados à esquerda.
2. **Dado** a lista de livros, **quando** um livro não tem imagem de capa, **então** a miniatura mostra só a cor
   da capa, sem título cortado.
3. **Dado** qualquer tema, **quando** vejo o selo de categoria, **então** ele tem fundo transparente, e texto e
   borda vêm do tema.
4. **Dado** o botão de adicionar livro, **então** há um único sinal de mais (o ícone) e o texto é "Adicionar Livro".
5. **Dado** um tema escuro, **quando** vejo a busca e o seletor Grade/Lista, **então** a busca usa as cores do tema
   e o contêiner do seletor é transparente, com os dois botões separados por um espaço visível.

### História 3 — Estudos do livro: grade, lista, árvore e mapa (P2)

Bug 07, em `/livros/:id`.

**Cenários de aceite:**
1. **Dado** o menu de estado do estudo (Rascunho, Em Estudo, Revisado, Concluído), **então** as opções têm fundo
   transparente e a distinção vem de borda e texto do tema, mais um indicador que não dependa só de cor.
2. **Dado** a visão em lista, **então** os títulos das colunas ficam alinhados com o conteúdo de cada coluna e
   todos têm o mesmo estilo, ordenáveis ou não; a ordenação ativa é indicada por ícone.
3. **Dado** a lista com um estudo selecionado, **então** o botão de desmarcar tem área de toque ≥ 44 × 44 px.
4. **Dado** a visão em árvore e a visão em mapa, em qualquer tema, **então** todo ícone de ação é visível em
   repouso, ao passar o cursor e em foco.
5. **Dado** o mapa, **quando** seleciono um estudo, **então** a barra que aparece tem disposição correta e todos
   os botões executam a ação que anunciam — ou a barra não é exibida.

### História 4 — Cabeçalho, rodapé e estados vazios (P3)

Bugs 02, 10, 11 e 14.

**Cenários de aceite:**
1. **Dado** uma tela larga, **então** o rodapé distribui os itens pela largura (marca de um lado, links do outro);
   **dado** um celular, **então** os itens quebram em linhas sem ficar espremidos.
2. **Dado** o cabeçalho, **então** o gatilho do menu do usuário mostra só a foto ou as iniciais, sem nome, sem seta
   e sem fundo de botão, mantendo nome acessível e área de toque ≥ 44 × 44 px.
3. **Dado** a aba Bloqueados sem itens, **então** ícone, título e texto ficam centralizados.
4. **Dado** um tema escuro, **então** a caixa do ícone do estado vazio (Lixeira e demais) não tem fundo branco.

### História 5 — Páginas públicas: link, texto de apoio e tema da visita (P3)

Bugs 15 e 16.

**Cenários de aceite:**
1. **Dado** o rodapé público, **quando** clico em "Código Aberto", **então** vou para
   `https://github.com/AntonioBudal/CDL`.
2. **Dado** a página `/apoie`, **então** o texto diz que hoje a forma de apoiar é divulgar e colaborar, e que uma
   forma de contribuição financeira virá no futuro; não há botão ou link vazio.
3. **Dado** que escolhi um tema na vitrine da página inicial, **quando** navego para `/sobre` ou `/apoie`,
   **então** o tema escolhido continua aplicado.

### Casos de borda

- Tema `e-ink` (sem cor, sem animação): estados e seleção precisam de indicador que não seja cor.
- Tema `solario`: contraste de texto já é o mais baixo dos dez (6,9:1); nenhuma correção pode piorá-lo.
- Estilo de cantos "quadrado" (`data-style='square'`): contêineres transparentes não podem deixar "sobras".
- Nomes de categoria, livro e usuário muito longos; livro sem autor; usuário sem foto.
- Larguras de 320 px e de 1920 px; zoom de 200 %.
- Visitante que já tem conta e tema salvo: o tema da visita não pode sobrescrever a preferência salva.

---

## 3. Requisitos funcionais

### Causa raiz

- **FR-001**: Toda cor em estilo de componente DEVE vir de uma variável **definida** no sistema de temas. Para as
  104 variáveis hoje indefinidas, a correção DEVE seguir uma destas duas vias, a decidir no plano:
  (a) camada de compatibilidade em `tokens.css` que as define como apelidos das canônicas; (b) substituição direta
  pelas canônicas nos componentes. Recomendação: (a) agora, por corrigir as 961 ocorrências de uma vez com risco
  baixo, e (b) aos poucos.
- **FR-002**: DEVE existir um teste automático (`npm test`) que falha quando um arquivo de `src/` usa
  `var(--nome…)` com um nome que não está definido em nenhum arquivo de estilo.
- **FR-003**: Variáveis de raio e sombra indefinidas (`--radius-sm`, `--radius-md`, `--radius-lg`, `--shadow-sm`…)
  DEVEM apontar para as existentes (`--radius-control`, `--radius-card`, `--radius-panel`, `--shadow-control`…),
  para que o ajuste de cantos do usuário valha em toda a interface.
- **FR-004**: Nenhuma regra PODE usar uma variável de fundo como cor de texto ou de ícone (ex.:
  `color: var(--color-inverse-bg)`), salvo sobre o fundo correspondente (`--color-on-inverse` sobre
  `--color-inverse-bg`).
- **FR-005**: Contraste mínimo em todos os dez temas: 4,5:1 para texto de interface; 7:1 para texto de leitura
  contínua onde o tema já o atinge; 3:1 para ícones, bordas de controles e indicadores de foco.

Proposta inicial de correspondência (a confirmar no plano, caso a caso):

| Indefinida | Canônica sugerida |
| :--- | :--- |
| `--color-text-primary`, `--color-text-main`, `--text`, `--color-ink` | `--color-text` |
| `--color-text-muted`, `--text-muted`, `--muted` | `--color-muted` |
| `--color-text-secondary` | `--color-subtle` |
| `--color-bg`, `--color-background` | `--color-page` |
| `--color-surface-elevated`, `--color-surface-alt`, `--bg-surface` | `--color-surface` |
| `--color-surface-subtle`, `--color-surface-muted`, `--color-bg-subtle`, `--color-bg-alt`, `--bg-muted`, `--color-neutral-subtle` | `--color-surface-soft` |
| `--color-primary`, `--primary`, `--accent`, `--accent-color` | `--color-accent` |
| `--color-primary-hover` | `--color-accent-hover` |
| `--color-accent-subtle`, `--color-primary-light` | `--color-selected-bg` |
| `--color-border-subtle` | `--color-border-divider` |
| `--border` | `--color-border` |
| `--color-danger`, `--color-error`, `--color-danger-text` | `--color-error-marker` / `--color-error-text` |
| `--color-danger-subtle` | `--color-error-bg` |
| `--color-warning` | `--color-warning-marker` |
| `--color-bg-warning`, `--color-border-warning` | `--color-warning-bg`, `--color-warning-border` |
| `--color-success` | `--color-success-text` |

### Bugs pontuais

| Bug | Onde (arquivo) | Requisito |
| :--- | :--- | :--- |
| 01a | `views/BooksView.vue` (grade) | **FR-010**: a grade de livros alinha os itens à esquerda (`justify-content: start`), mantendo as colunas responsivas. |
| 01b | `components/BookCover.vue`, uso com `size="sm"` na lista | **FR-011**: na miniatura pequena, a capa sem imagem mostra só a cor e a lombada; título e autor não são renderizados. O nome do livro continua acessível pela linha da lista. |
| 02 | `components/layout/AppFooter.vue` | **FR-012**: em telas largas, marca e licença de um lado e links do outro (`space-between`), dentro da largura máxima do conteúdo; em telas estreitas, quebra em linhas centralizadas, sem os separadores "·" soltos no começo ou fim de linha. |
| 03 | `components/CategoryBadge.vue` | **FR-013**: selo de categoria com fundo transparente; texto em `--color-text` e borda em `--color-border`; ao passar o cursor ou focar, borda e texto em `--color-accent`. Hoje o fundo usa `--color-surface-muted`, que não existe. |
| 04 | `views/BooksView.vue` (linhas 208–212) | **FR-014**: texto do botão "Adicionar Livro" (sem "+"), mantendo o ícone; `aria-label` "Adicionar novo livro". |
| 05 | `components/highlights/HighlightCard.vue`, `views/HighlightsLibraryView.vue`, `components/highlights/HighlightFilterToolbar.vue` | **FR-015**: o cartão de destaque usa `--color-surface` e `--color-text`; a área abaixo do cabeçalho (corpo e rodapé do cartão) tem fundo transparente; selos semânticos (ex.: "Ideia Central") mantêm o ponto colorido, com texto e borda do tema; revisar todo o texto da tela contra FR-005. |
| 06 | `views/ReviewHubView.vue`, `components/review/*` | **FR-016**: barras de ferramentas, banners e cartões da Revisão usam `--color-border` / `--color-border-divider`; nenhuma borda branca fixa. |
| 07a | `components/StudyStatusBadge.vue` | **FR-017**: opções e selo de estado com fundo transparente; cor de borda e texto por variáveis do tema; um ponto ou ícone distingue os quatro estados sem depender só de cor; a opção atual mantém o `check`. |
| 07b | `components/views/StudyListView.vue` (cabeçalho, linha 532 em diante) | **FR-018**: títulos de coluna alinhados com as células (texto à esquerda; números e ações conforme a coluna); mesmo estilo para colunas ordenáveis e fixas; indicador de ordenação por `<Icon>` (hoje é o caractere "↑"); `aria-sort` preservado. |
| 07c | `components/views/StudyListView.vue` (seleção) | **FR-019**: botão de desmarcar com área de toque ≥ 44 × 44 px e espaçamento em relação aos vizinhos. |
| 07d | `components/views/StudyTreeNodeItem.vue` | **FR-020**: ícones de ação visíveis nos três estados (repouso, cursor, foco) em todos os temas; corrigir `color: var(--color-inverse-bg)`. |
| 07e | `components/views/StudyMapView.vue` e `components/views/map/*`, `canvas/*` | **FR-021**: auditar **todos** os botões e ícones do mapa (o usuário citou só o da lixeira) e aplicar FR-004 e FR-005. |
| 07f | `components/views/StudyMapView.vue` (`mobile-toolbar-header`) | **FR-022**: a barra exibida ao selecionar um estudo no mapa tem disposição definida (título truncado, ações, fechar) e cada controle funciona; se a barra só fizer sentido no celular, não aparece em telas largas. **[NEEDS CLARIFICATION: quais ações essa barra deve oferecer]** |
| 10 | `components/ui/EmptyState.vue` | **FR-023**: a caixa do ícone do estado vazio usa `--color-surface-soft` ou fica transparente; vale para todas as telas que usam o componente. |
| 11 | `components/layout/UserDropdown.vue` | **FR-024**: o gatilho mostra só a foto ou as iniciais, sem nome, sem seta e sem fundo; `aria-label` "Menu de {nome}"; foco visível; alvo ≥ 44 × 44 px. O nome continua dentro do menu aberto. |
| 12 | `views/DashboardView.vue`, `components/dashboard/*` | **FR-025**: nenhum texto do Dashboard usa cinza-azulado fixo; títulos em `--color-text`, apoio em `--color-muted`. |
| 13a | `components/LibraryToolbar.vue` (busca) | **FR-026**: campo de busca com fundo, texto, borda e texto de exemplo do tema. |
| 13b | `components/LibraryToolbar.vue` (seletor Grade/Lista) | **FR-027**: contêiner do seletor transparente e sem borda; botões separados por espaço; o ativo se distingue por borda ou fundo do tema, sem "sobra" branca nos cantos. |
| 14 | `views/FriendsView.vue` (linha 563) | **FR-028**: estado vazio de Bloqueados centralizado como os demais; preferir o componente `EmptyState` a um bloco próprio. |
| 15 | `components/landing/PublicFooter.vue` (linha 56) | **FR-029**: o link "Código Aberto" aponta para `https://github.com/AntonioBudal/CDL`; conferir se o endereço antigo aparece em outro lugar (JSON-LD, `/sobre`, README). |
| 16a | `views/SupportView.vue` | **FR-030**: página Apoie segue o tema (29 variáveis indefinidas hoje) e é legível em temas escuros e no `pergaminho`. |
| 16b | `views/SupportView.vue` | **FR-031**: texto reescrito conforme a seção 5; nenhum botão ou link de doação vazio. |
| 16c | `composables/useVisitorTheme.ts`, páginas públicas | **FR-032**: o tema escolhido na vitrine vale durante a visita em todas as rotas públicas (`/`, `/sobre`, `/apoie`). Hoje o composable restaura o tema ao sair da página inicial. **[NEEDS CLARIFICATION: ver seção 6, pergunta 3]** |

### Regras gerais

- **FR-040**: Somente frontend. Nenhuma mudança em backend, banco ou contratos de API.
- **FR-041**: Zero emojis; ícones só por `<Icon name="…" />`.
- **FR-042**: Nenhuma mudança de comportamento além das listadas; nenhum texto do acervo do usuário em testes ou
  capturas de tela.

---

## 4. Telas a verificar

Relatadas: Livros (`/livros`), Livro e suas quatro visões (`/livros/:id`), Destaques (`/highlights`), Revisão
(`/review`), Dashboard (`/dashboard`), Amigos (`/amigos`), Lixeira (`/lixeira`), Apoie (`/apoie`), Sobre (`/sobre`),
página inicial e rodapés.

Não relatadas, mas com o mesmo defeito no código (FR-001 as cobre): `DigitizeNotebookView`, Caixa de Entrada e
seus modais, sessão de estudo, seletor de modelos de estudo, histórico do estudo, leitura ativa, administração,
modais de confirmação e de lixeira, widgets do Dashboard.

Matriz de verificação: cada tela × dez temas × dois estilos de canto, em largura de celular e de desktop.

---

## 5. Texto proposto para `/apoie`

> **Apoie o Leitorum**
>
> O Leitorum é uma plataforma independente, gratuita e de código aberto, voltada à leitura atenta e aos estudos.
>
> **Como apoiar hoje**
>
> O projeto é mantido voluntariamente e, por enquanto, não recebe contribuições financeiras. Neste momento, a
> melhor ajuda é fazer o Leitorum chegar a quem lê:
>
> - Recomende o Leitorum a colegas, grupos de estudo e outros leitores.
> - Envie sugestões de recursos, relatos de problemas e ideias de melhoria.
> - Colabore com documentação e revisão no repositório de código aberto.
>
> **Apoio financeiro, no futuro**
>
> Quando o projeto crescer e os custos de servidores, domínio e tráfego aumentarem, abriremos uma forma de
> contribuição financeira, sempre facultativa. Quando isso acontecer, o caminho estará nesta página.

Com link para o repositório no terceiro item e, se houver, um canal para sugestões. O rótulo "Apoie o Leitorum" dos
rodapés permanece.

---

## 6. Perguntas em aberto

1. **Capa pequena na lista (bug 01b):** só a cor, como pedido, ou a cor com as iniciais (hoje "DD"), que cabem sem
   cortar? A especificação assume só a cor.
2. **Barra do mapa (bug 07f):** quais ações ela deve ter? Se não houver uso definido, a alternativa é removê-la até
   existir um.
3. **Tema da visita (bug 16c):** guardar só enquanto a aba estiver aberta (`sessionStorage`) ou também para a
   próxima visita (`localStorage`)? E vale nas telas de login e cadastro? A especificação assume: só durante a
   sessão, em todas as rotas públicas, sem tocar na preferência de quem já tem conta.
4. **Selos de estado (bug 07a):** manter uma cor por estado (em borda e ponto) ou deixar tudo neutro, distinguindo
   só por ícone e texto?
5. **Alcance da correção de causa raiz:** aceitar a camada de compatibilidade agora (corrige também as telas não
   relatadas) ou limitar esta feature às telas listadas?

---

## 7. Critérios de sucesso

- **SC-001**: Os 14 bugs da lista estão resolvidos e conferidos nos dez temas.
- **SC-002**: O teste de variáveis indefinidas passa com zero ocorrências (hoje: 961).
- **SC-003**: Nenhuma das telas da seção 4 tem contêiner de cor fixa que contrarie o tema.
- **SC-004**: Contraste conforme FR-005 nas telas da seção 4; nenhum tema fica pior do que está hoje.
- **SC-005**: Alvos de toque dos controles alterados ≥ 44 × 44 px.
- **SC-006**: `npm test` e `npm run build` passam; nenhuma mudança fora do frontend.

---

## 8. Premissas e fora de escopo

- O sistema de dez temas e as variáveis canônicas não mudam de nome.
- Ajustar os valores do tema `solario` para 7:1 não faz parte desta feature (já apontado no planejamento da
  página inicial).
- Redesenho de telas, novas funcionalidades e migração completa dos componentes para as variáveis canônicas ficam
  fora; esta feature corrige defeitos.
- A numeração 0.8.10 e o nome da pasta em `specs/` seguem a convenção do produto.
