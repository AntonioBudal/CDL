# Feature Specification: F0.10.02.5 — Correções Visuais e Gerenciamento de Capítulos (emergência)

**Feature Branch**: `094-correcoes-capa-capitulos`

**Created**: 2026-11-02

**Status**: Concluída em 2026-11-02 (feature de emergência; planejamento, tarefas, implementação e verificação
num só ciclo). Na execução, três defeitos antigos da mesma tela entraram: seleção que pulava ao mover sem
`?chapter=`, foco do campo de renomear (ref em `v-for`) e rótulo `.sr-only` visível. Ver `RETOMADA.md`.

**Input**: "Feature 2.5° — Correções visuais e gerenciamento de capítulos", entre a F0.10.02 e a F0.10.03.

---

## 1. Diagnóstico (servidor de validação, banco fictício)

| # | Problema | Causa |
|---|---|---|
| 1.1 | No celular (≤ 767 px), o container da capa em `/livros/:id` ocupa 140×210 px e cobre o título, embora a imagem esteja em 48×72 px | A regra móvel de `views/BookView.vue` (l. 1425) força a largura em `:deep(.book-cover)`, classe que não existe mais; o componente `BookCover.vue` usa `.book-cover-container` (largura fixa de 140 px no tamanho `md`). Só o `:deep(img)` casa, e a imagem encolhe dentro de um container grande |
| 1.2 | Ícones das ferramentas do capítulo selecionado quase invisíveis nos temas claros: 1,0 a 2,0:1 em Papel Fosco, Cinza Neutro, Pergaminho, Monocromático, E-Ink e Solário | As `.pill-tool-btn` usam a variante `.quiet` (texto `--color-text`), mas ficam sobre o fundo da pílula selecionada (`--color-selected-bg`), que nesses temas é escuro |
| 2 | Gerenciamento de capítulos incompleto | Não existe exclusão de capítulo (nem na API); no celular, a faixa de pílulas fica oculta e só sobra o seletor, sem mover, renomear ou excluir |

## 2. User Stories

### US1 — Capa no tamanho certo no celular (P1)

**Acceptance**: em 375 px, o container da capa mede 48×72 px, igual ao wrapper; o título não fica coberto; no
desktop, a capa segue com 140×210 px.

### US2 — Ícones do capítulo selecionado legíveis (P1)

**Acceptance**: nos 10 temas, os ícones habilitados das ferramentas do capítulo selecionado têm pelo menos 4,5:1
contra o fundo da pílula (os desabilitados continuam visíveis, mais apagados); hover e foco seguem neutros.

### US3 — Gerenciar capítulos no computador e no celular (P1)

**Acceptance**:
1. **Desktop:** o capítulo selecionado mostra mover para trás, mover para frente, renomear (já existiam) e
   excluir (novo).
2. **Celular:** ao lado do seletor de capítulo, um menu "Gerenciar capítulo" oferece as mesmas quatro ações;
   renomear abre um campo logo abaixo do seletor; mover troca a ordem e o seletor reflete a nova numeração.
3. **Exclusão:** pede confirmação (`role="alertdialog"`); capítulo sem estudos é excluído e as posições dos
   demais são renumeradas; o leitor vai para o capítulo vizinho.
4. **Capítulo com estudos (inclusive na lixeira):** não é excluído. A interface avisa antes, quando sabe que há
   estudos, e a API recusa com 409 e mensagem clara. Os estudos nunca são apagados junto.
5. Tudo persiste (recarregar a página mantém nome, ordem e exclusão).

### Edge Cases

- **Um só capítulo:** pode ser excluído se estiver vazio; a página volta ao estado "adicione o primeiro capítulo".
- **Mover nas pontas:** a ação fica desabilitada (como já é no desktop).
- **Livro compartilhado com o leitor:** as ações não aparecem para quem não é dono; a API já responde 404.
- **Edição simultânea:** a renomeação mantém a trava otimista existente (`expected_updated_at`).

## 3. Requirements

- **FR-001**: Regra móvel da capa passa a mirar `.book-cover-container` (largura, altura e bordas), sem `!important`
  novo além dos já existentes na mesma regra.
- **FR-002**: A variante `.quiet` ganha os ganchos `--quiet-fg` (texto) e `--quiet-fg-disabled` (texto desabilitado);
  a `.chapter-pill.selected` os define com `--color-selected-text`.
- **FR-003**: `DELETE /api/books/{book_id}/chapters/{chapter_id}`: só o dono; 409 se houver estudos (ativos ou na
  lixeira); senão exclui, renumera as posições e devolve a lista restante.
- **FR-004**: Desktop: botão "Excluir capítulo" (ícone de lixeira) nas ferramentas do capítulo selecionado.
- **FR-005**: Celular: menu "Gerenciar capítulo" (`DropdownMenu`) com mover para trás, mover para frente,
  renomear e excluir; renomear em campo abaixo do seletor; alvos de 44 px.
- **FR-006**: Confirmação de exclusão com o `TrashConfirmModal` existente (`danger`).
- **FR-007**: Nenhuma mudança na identidade visual além das cores das ferramentas; sem migração.

## 4. Success Criteria

- **SC-001**: Testes de backend da exclusão (vazio, com estudo ativo, com estudo na lixeira, livro de outro
  usuário, renumeração).
- **SC-002**: Teste de frontend: botão de excluir no desktop, menu de gerenciamento no celular, chamada à API, regra
  da capa e ganchos da variante.
- **SC-003**: No navegador, em 1366 e 375 px: capa correta; contraste das ferramentas ≥ 4,5:1 nos 10 temas;
  criar, renomear, mover e excluir capítulos fictícios funcionando e persistindo após recarregar.
- **SC-004**: `npm run build` passa (3ª feature do lote de 5).
