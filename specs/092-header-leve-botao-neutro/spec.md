# Feature Specification: F0.10.01 — Header Leve e Variante Neutra de Botão

**Feature Branch**: `092-header-leve-botao-neutro`

**Created**: 2026-11-01

**Status**: Concluída em 2026-11-01, aceita pelo usuário.

**Input**: Feature 01 do plano mestre enviado pelo usuário em 2026-11-01 ("Header Global, Estante `/livros` e
Visualização Interna do Livro"), com o escopo reduzido aprovado depois da auditoria do repositório. O plano foi
renumerado para **0.10, 0.11 e 1.0**, porque os números 0.8 e 0.9 já pertencem a roadmaps entregues
(`docs/contexto/ROADMAP-0.8.md` e `ROADMAP-0.9.md`).

---

## 1. Contexto

A auditoria de 2026-11-01 mostrou que quase tudo o que a Feature 01 pedia já está no código:

| Pedido | Situação | Onde |
|---|---|---|
| Estante com "Em andamento" e cadastro em drawer | Feito | `views/BooksView.vue` (`BookHeroCard`, botão "Adicionar Livro", `Drawer` "Novo livro") |
| Página do livro em 3 faixas horizontais | Feito | `views/BookView.vue` (faixa de capítulos l. 486, estudos em largura total, inspetor l. 731) |
| Botões de ação que expandem no hover | Feito | `.icon-action-btn` / `.btn-pill-label` em `views/BookView.vue` (l. 899–957) |
| "Sair" dentro do menu do perfil | Feito | `components/layout/UserDropdown.vue` |
| Header sem "efeito blocos de Lego" | **Não** | ver abaixo |

**Causa do "efeito blocos de Lego".** A regra global de botões em `src/appearance-advanced.css:261`

```css
:root :is(button, .button):not([role='tab']):not(.group-toggle-btn) { background: var(--button-bg); … }
```

tem especificidade (0,4,0) e pinta todo `<button>` com `--color-accent`. Os estilos dos componentes, com (0,2,0),
perdem. As abas primárias escapam porque são `<a>`; os controles da direita do header são `<button>`. No
servidor de validação (tema Voltagem, superclasse mecânica), os 6 controles do header saíram com o fundo do
destaque: "Mais", sincronização, busca, captura, notificações e perfil. O mesmo acontece com as ferramentas da
pílula do capítulo ativo em `/livros/:id` e com os botões auxiliares da barra da estante.

O código já tem o padrão para corrigir isso: a variante `.secondary` (`appearance-advanced.css:276`) troca só as
variáveis `--button-*`, com especificidade suficiente para vencer a regra base.

**Relação com os roadmaps:** primeira feature do Roadmap 0.10. Não altera o estado de nenhuma feature da 0.5, 0.8
ou 0.9.

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 — Header leve (Priority: P1)

Como leitor, quero que a barra superior tenha uma só linguagem visual, com só a ação de captura em destaque, para
que a navegação não pareça uma fileira de blocos pesados.

**Independent Test**: com qualquer um dos 10 temas e qualquer superclasse, o fundo calculado de "Mais",
sincronização, busca, notificações e perfil não é a cor de destaque; o de "Capturar" é.

**Acceptance Scenarios**:

1. **Given** um leitor autenticado em `/livros`, **When** a página carrega, **Then** "Mais", busca, notificações e
   perfil usam a superfície neutra das abas primárias (fundo transparente ou `--color-surface`, texto do tema).
2. **Given** o mesmo leitor, **When** olha a sincronização, **Then** vê um indicador leve (ícone e ponto colorido do
   estado), sem caixa de botão, com dica ao passar o mouse ou focar pelo teclado.
3. **Given** um header com espaço (container query de 1400 px no `.header-inner`), **When** olha a busca, **Then**
   vê uma pílula sutil com "Buscar" e o atalho "Ctrl K"; sem espaço, vê só o ícone, com o mesmo `aria-label`.
   *(Revisado na execução: a versão original dizia "≥ 1024 px de tela", mas com a grade `1fr auto 1fr` e o
   contêiner padrão de 74rem a pílula invadia o "Mais".)*
4. **Given** qualquer largura, **When** olha "Capturar", **Then** é o único controle do header com a cor de
   destaque.
5. **Given** um controle neutro, **When** passa o mouse ou foca pelo teclado, **Then** o fundo vira
   `--color-surface-hover`, o texto vira `--color-hover-text` e o anel de foco continua visível.

### User Story 2 — Controles secundários neutros nas páginas de livros (Priority: P2)

Como leitor, quero que os botões auxiliares da estante e da página do livro não disputem atenção com as ações
principais.

**Independent Test**: em `/livros/:id`, as ferramentas da pílula do capítulo ativo (mover para trás, mover para
frente, editar) têm fundo neutro; em `/livros`, os botões de limpar busca, limpar filtros e limpar categoria e o
modo de visualização **não selecionado** têm fundo neutro, e o selecionado mantém o destaque.

**Acceptance Scenarios**:

1. **Given** um capítulo selecionado, **When** a faixa de capítulos aparece, **Then** os 3 botões `.pill-tool-btn`
   são neutros, mantêm a área de toque de 44 px no celular e o `aria-label` atual.
2. **Given** a estante com busca ou filtro ativo, **When** aparecem os botões de limpar, **Then** são neutros.
3. **Given** a alternância Grade/Lista da estante, **When** um modo está ativo, **Then** só o botão ativo usa o
   destaque (`aria-pressed="true"`).

### User Story 3 — Nada do que já funciona regride (Priority: P1)

Como leitor, quero que o drawer de cadastro, as 3 faixas da página do livro e os botões que expandem no hover
continuem iguais.

**Independent Test**: as suítes atuais passam sem mudança de comportamento; em 1366, 768 e 375 px não há rolagem
horizontal em `/livros` e `/livros/:id`.

**Acceptance Scenarios**:

1. **Given** `/livros/:id` em 375 px, **When** a página carrega, **Then** o inspetor continua em grade 2×2 e os
   botões de ação continuam com 44×44 px.
2. **Given** `prefers-reduced-motion: reduce`, **When** o leitor passa o mouse num botão expansível, **Then** o
   rótulo aparece sem animação.
3. **Given** o seletor de visualização dos estudos (`ViewSwitcher`, `role="tab"`), **When** a página carrega,
   **Then** ele continua como está; a regra global já o exclui.

### Edge Cases

- **Superclasses** (mecânica, dimensional e as demais em `styles/superclasses/`): algumas aplicam `box-shadow`,
  `border-radius` e `transform: none !important` a todo `<button>`. A variante neutra não pode reintroduzir o
  destaque por elas; diferenças de raio e sombra herdadas da superclasse são aceitáveis.
- **Estilos de botão `outline` e `ghost`** (`:root[data-button-style]`): também pintam com o destaque e precisam
  ceder à variante neutra.
- **Notificações não lidas**: o badge numérico continua com a cor semântica atual; só o botão fica neutro.
- **Sincronização com erro ou offline**: o ponto colorido usa os tokens semânticos (`--color-danger`,
  `--color-warning` etc.), nunca hex.
- **Visitante não autenticado**: o header público (Entrar, Criar Conta) não muda; "Criar Conta" segue como ação
  principal.
- **Landing**: os controles que receberam ajustes caso a caso em `HeroShowcase.vue` e `ThemeShowcase.vue` passam a
  usar a variante, sem mudança visual.

---

## 3. Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Deve existir uma variante de botão neutra, `.quiet`, em `src/appearance-advanced.css`, no mesmo
  padrão da `.secondary`: só redefine `--button-bg`, `--button-fg`, `--button-border`, `--button-hover-bg` e
  `--button-hover-fg`, com especificidade igual ou maior que a regra base e que os modos `outline` e `ghost`.
- **FR-002**: Na variante, o fundo é transparente, o texto é `--color-text`, a borda é transparente, o hover usa
  `--color-surface-hover` e o texto no hover usa `--color-hover-text`.
- **FR-003**: Usam `.quiet`:
  - o gatilho "Mais" (`NavigationTabs.vue`);
  - a sincronização (`SyncStatusBadge.vue`);
  - a busca e as notificações (`GlobalHeader.vue`);
  - o gatilho do perfil (`UserDropdown.vue`);
  - as `.pill-tool-btn` (`BookView.vue`);
  - os botões de limpar e o modo não selecionado em `LibraryToolbar.vue`.
- **FR-004**: "Capturar" (`.quick-capture-trigger-btn`) mantém o destaque e é o único controle do header com ele.
- **FR-005**: A busca mostra a pílula "Buscar · Ctrl K" quando o header tem espaço (container query de 1400 px) e
  só o ícone fora disso, sem mudar o `aria-label` nem o atalho. *(Revisado na execução; ver US1, cenário 3.)*
- **FR-006**: A sincronização vira indicador (ícone e ponto de estado), sem borda nem fundo, com `title` e
  `aria-label` descrevendo o estado.
- **FR-007**: Nenhuma cor hexadecimal nova nos arquivos tocados; só tokens existentes.
- **FR-008**: Zero falhas de contraste (WCAG 4,5:1 para texto) nos 10 temas, estáticas e com hover simulado, nos
  controles tocados.
- **FR-009**: Nenhuma mudança de rota, de API, de banco ou de comportamento dos controles.
- **FR-010**: Os ajustes caso a caso da landing (`HeroShowcase.vue`, `ThemeShowcase.vue`) passam a usar `.quiet`.
  Isso depende de a reformulação da landing estar commitada antes ou junto desta feature.

### Key Entities

Nenhuma. A feature é só de apresentação.

---

## 4. Success Criteria *(mandatory)*

- **SC-001**: No navegador, nos 10 temas × superclasses disponíveis, o fundo calculado dos 5 controles neutros do
  header é diferente de `--color-accent`, e o de "Capturar" é igual.
- **SC-002**: Em `/livros/:id`, as 3 `.pill-tool-btn` têm fundo diferente de `--color-accent`.
- **SC-003**: Sem rolagem horizontal em 1366, 768 e 375 px em `/livros` e `/livros/:id`.
- **SC-004**: `npm test`, `npm run build` e `pytest` (com banco descartável) passam; os testes de contraste incluem
  os novos pares.
- **SC-005**: Um teste novo falha se algum dos controles da FR-003 perder a classe `.quiet` ou se "Capturar" a
  ganhar.

---

## 5. Fora do escopo

- O resto do Roadmap 0.10 (endurecimento de segurança, painel de Sistema, Revisão, Destaques, Importar, Amigos,
  landing de confiança e correções reservadas).
- Trocar a regra global de botões por opt-in. Mexeria em todos os botões do sistema; a variante resolve o problema
  sem esse risco.
- Status de leitura do livro (Lendo, Quero Ler, Consulta, DNF): entra no Roadmap 0.11, com migração e backup.
- Criar `ROADMAP-0.10.md`, `ROADMAP-0.11.md` e `ROADMAP-1.0.md`: documentação à parte, a ser escrita quando você
  aprovar o texto dos roadmaps.

## 6. Assumptions

- A auditoria visual usou o servidor de validação (banco temporário e dados fictícios, porta 8010). Os temas e as
  superclasses do ambiente real seguem as mesmas regras de CSS.
- "Capturar" continua como a única ação primária do header, como pede o plano mestre.
