# Feature Specification: F0.11.11 — Cadernos de Síntese com Transclusão

**Feature Branch**: `113-cadernos-sintese`

**Created**: 2026-11-14

**Status**: Concluída em 2026-11-14

**Input**: Item "cadernos de síntese com transclusão" do Roadmap 0.11 no HANDOFF. Primeira feature do lote 3 do 0.11
(último item do roadmap). **Com migração (`0039`).**

---

## 1. Contexto (auditoria de 2026-11-14, só código)

| Ponto | Situação | Onde |
|---|---|---|
| Unidade de escrita | O **estudo**, sempre preso a um capítulo de um livro (4 seções + notas) | `models/study.py` |
| Ligações | `[[Título|id]]` cria link e *backlink* entre estudos; `[[conceito:Termo]]` liga ao léxico | `services/markdown.ts`, `study_mention_service.py` |
| Texto que atravesse livros | **Não existe.** Não há onde escrever uma síntese de vários livros/estudos | — |
| Transclusão | **Não existe.** Copiar o texto de um estudo para outro lugar cria duas versões que se desencontram | — |
| Portabilidade | O pacote da conta (LGPD) leva livros, estudos, destaques e imagens | `services/export_service.py` (`generate_account_export_zip`) |

**Decisão:** uma entidade nova, **caderno de síntese**, do próprio leitor e fora de qualquer livro, com texto
Markdown próprio e **trechos transcluídos**: marcas no texto que, na leitura, mostram o conteúdo **atual** do estudo,
da seção ou do destaque de origem (nada é copiado).

---

## 2. User Stories

### US1 — Criar e escrever um caderno (P1)

**Acceptance**:
1. Página **"Sínteses"** (`/sinteses`, na barra secundária, no menu "Mais" e no menu do usuário): lista dos cadernos
   (título, atualizado em, quantos trechos), botão **"Novo caderno"**.
2. Caderno (`/sinteses/:id`): título e texto em Markdown, com **Ler** e **Editar**; salvar com aviso de alterações
   não salvas; controle de versão otimista (dois aparelhos não se sobrescrevem: 409 com mensagem).
3. Excluir manda para **"Excluídos"** na própria página Sínteses (restaurar ou excluir de vez, com confirmação); some
   em 30 dias como a Lixeira.

### US2 — Transcluir trechos (P1)

**Acceptance**:
1. Marcas aceitas no texto, cada uma sozinha na linha:
   - `![[Título|id]]` → o estudo inteiro (título e as seções preenchidas);
   - `![[Título|id#resumo]]` (também `#explicacao`, `#conceitos`, `#referencias`) → só a seção;
   - `![[destaque:123]]` → o destaque (texto, nota e origem).
2. Na leitura, cada marca vira um **bloco** com o conteúdo atual da origem, a origem ("Livro · Capítulo · Estudo") e o
   link **"Abrir no estudo"**. Editar o estudo muda o caderno na hora.
3. Origem na lixeira, apagada ou de outro leitor → bloco "Trecho indisponível (o estudo foi excluído ou não é seu)",
   sem vazar nada.
4. No editor, **"Inserir trecho"** abre a busca de estudos (a mesma das menções); escolhido o estudo, oferece "Estudo
   inteiro", as seções preenchidas e os destaques dele; a marca entra numa linha própria na posição do cursor.

### US3 — Exportar e levar junto (P2)

**Acceptance**:
1. **"Exportar Markdown"** no caderno: arquivo `.md` com os trechos **resolvidos** (como citação, com a origem), para
   usar fora do Leitorum.
2. O pacote da conta (Ajustes → exportar tudo) passa a incluir `sinteses/<título>.md`, também resolvido.

### Edge Cases

- Marca no meio de um parágrafo, id inexistente ou seção desconhecida: fica como texto e aparece a dica "Marca de
  trecho não reconhecida".
- Transclusão não é recursiva (estudos não transcluem); limite de 200 trechos por caderno na leitura.
- Texto do caderno até 500 mil caracteres; título até 300.
- Celular: blocos em uma coluna, sem rolagem lateral; alvos de 44 px.
- Exportação: cada trecho sai cercado de linhas em branco (sem elas, a linha seguinte entraria na citação do
  Markdown; achado na execução).

---

## 3. Requirements

- **FR-001**: Migração `0039_synthesis_notebooks`: tabela `synthesis_notebooks` (`id`, `user_id` → `users.id` `ON
  DELETE CASCADE`, `title`, `body`, `version`, `created_at`, `updated_at`, `deleted_at`), índice por `user_id`,
  nomes pela convenção.
- **FR-002**: `services/synthesis_service.py`: CRUD com versão, lixeira própria (30 dias), `parse_embeds(body)`
  (puro), `resolve_embeds(session, user_id, embeds)` (só do próprio leitor, fora da lixeira), `export_markdown`.
- **FR-003**: `routers/syntheses.py`: `GET/POST /api/syntheses`, `GET/PATCH/DELETE /api/syntheses/{id}`,
  `POST /{id}/restore`, `DELETE /{id}/permanent`, `GET /{id}/resolved`, `GET /{id}/export`; `GET
  /api/syntheses/trash`.
- **FR-004**: Frontend: `views/SynthesesView.vue`, `views/SynthesisView.vue`, `components/synthesis/EmbedBlock.vue`,
  `components/synthesis/InsertEmbedDialog.vue`, `utils/synthesisEmbeds.ts` (mesmo analisador no navegador para
  dividir o texto); rotas `syntheses` e `synthesis` registradas nos contratos 076/081; menus.
- **FR-005**: Só tokens, `.quiet`, 44 px, contraste ≥ 4,5:1 nos 10 temas.

## 4. Success Criteria

- **SC-001**: Testes puros do analisador (três formas, seções, marcas inválidas, no meio do parágrafo, limite) no
  backend e no frontend (mesmos casos).
- **SC-002**: Testes de API: CRUD, versão (409), isolamento, lixeira e restauração, resolução (estudo, seção,
  destaque; origem na lixeira, de outro leitor, inexistente), exportação resolvida, pacote da conta com `sinteses/`.
- **SC-003**: Migração: `test_migration_matches_models` e upgrade/downgrade em banco descartável.
- **SC-004**: Navegador (dados fictícios): criar, inserir trecho pelo diálogo, ver o bloco atualizar depois de editar
  o estudo, origem excluída, exportar; 1366 e 375 px; contraste nos 10 temas.
- **SC-005**: Build e testes novos e vizinhos; commit; levar ao `main`. Migração **não** aplicada ao banco ativo.

## 5. Fora do escopo

- Transcluir em estudos; *backlinks* "usado nas sínteses" na página do estudo.
- Caderno compartilhado com amigos ou público; colaboração em tempo real.
- Transcluir trechos de outros cadernos ou de páginas do livro.
