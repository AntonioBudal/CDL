# Feature Specification: F0.11.03 — Importar Destaques do Kindle e do Kobo

**Feature Branch**: `105-importar-kindle-kobo`

**Created**: 2026-11-09

**Status**: Concluída em 2026-11-09

**Input**: Item "parsers Kindle/Kobo" do Roadmap 0.11 no HANDOFF. Terceira feature do lote 1 do 0.11. **Sem migração.**

---

## 1. Contexto (auditoria de 2026-11-09, só código)

| Ponto | Situação | Onde |
|---|---|---|
| Kindle / Kobo | **Nada** no código (só uma menção a "posição Kindle" na documentação) | — |
| Destino natural | A **Mesa de Triagem** (capturas com livro e, desde a F0.11.02, capítulo) e a **bandeja do capítulo**: um destaque importado é uma ideia a triar, não um estudo pronto | `models/inbox_capture.py`, `components/books/ChapterTray.vue` |
| Casar livros | `normalize_title_key` e `first_author_surname_key` (F0.10.07) já casam títulos e autores entre grafias | `services/in_common_service.py` |
| Formatos | Kindle: `My Clippings.txt` (texto, blocos separados por `==========`, cabeçalho em inglês ou português). Kobo: `KoboReader.sqlite` do aparelho (tabelas `Bookmark` e `content`) | — |

**Decisão de dados:** sem migração. Cada destaque vira uma captura `status = inbox` com o livro escolhido, sem
capítulo (a triagem para capítulos fica na bandeja). A duplicata é evitada comparando livro + texto + localização das
capturas que já existem.

---

## 2. User Stories

### US1 — Enviar o arquivo e ver o que tem nele (P1)

**Acceptance**:
1. Na Mesa de Triagem, o botão **"Importar do Kindle ou Kobo"** abre a tela de importação (`/inbox/importar-leitor`)
   com instruções curtas de onde achar cada arquivo (Kindle: `documents/My Clippings.txt` pelo cabo USB; Kobo:
   `.kobo/KoboReader.sqlite`).
2. Ao enviar o arquivo, o servidor **só lê** (nada é gravado) e devolve a prévia: por livro, título, autor e quantos
   destaques e notas; quantos já estão na Mesa (duplicatas) e quantos são novos; marcadores (sem texto) são ignorados.
3. Formato reconhecido pelo conteúdo, não pela extensão. Arquivo inválido → mensagem clara ("Não reconheci este
   arquivo como My Clippings.txt do Kindle nem como KoboReader.sqlite").
4. Limites: Kindle até 20 MB; Kobo até 200 MB. O arquivo do Kobo é aberto **somente leitura** a partir de uma cópia
   temporária, apagada ao terminar.

### US2 — Escolher o livro de destino e importar (P1)

**Acceptance**:
1. Para cada livro do arquivo, a prévia sugere um livro do acervo quando título (e sobrenome do primeiro autor, se
   houver nos dois) casam; senão sugere **criar o livro** com título e autor do arquivo. O leitor pode trocar para
   outro livro, criar, ou **não importar** aquele livro.
2. "Importar" cria as capturas novas (`status = inbox`, `book_id` do destino) com:
   - `content` = texto do destaque; se houver nota no mesmo lugar, ela vai junto, abaixo, como "Nota: …";
   - `source_hint` = origem e localização, ex.: `Kindle · p. 32 · pos. 488–489 · 03/03/2025` ou
     `Kobo · 42% · 03/03/2025`.
3. O resultado mostra quantas capturas foram criadas e quantas duplicatas foram puladas, com links para a Mesa
   filtrada por livro e para a página do livro (onde a bandeja mostra "N capturas do livro sem capítulo").
4. Reenviar o mesmo arquivo não duplica nada.

### Edge Cases

- `My Clippings.txt` com BOM, CRLF, título com parênteses no meio ("Livro (Edição) (Autor)"), autor ausente,
  cabeçalho em português ("Seu destaque na página 32 | posição 488-489 | Adicionado: …") ou inglês.
- Nota sem destaque correspondente → captura própria só com a nota.
- Kindle repete o mesmo destaque quando o leitor ajusta a seleção: entradas com o mesmo livro e localização
  inicial, uma contendo a outra, viram uma só (fica a mais longa).
- Kobo: destaque sem texto (só anotação) vira captura com a nota; livro sem título no banco do aparelho usa
  "Livro sem título (Kobo)".
- Arquivo enorme com milhares de destaques: a prévia agrega por livro; a importação grava em lote numa transação.

---

## 3. Requirements

- **FR-001**: `services/ereader_import/kindle.py` e `kobo.py` (puros, testáveis): devolvem
  `[{title, author, entries: [{kind: highlight|note, text, note, location, page, percent, created_at}]}]`.
- **FR-002**: `POST /api/inbox/ereader/preview` (multipart) → prévia por livro, com a sugestão de destino e as
  contagens de novos e duplicatas; `POST /api/inbox/ereader/import` (multipart + escolhas por livro: `book_id`,
  `create` ou `skip`) → contagens criadas/puladas e livros criados. O arquivo é reenviado na importação (o servidor
  não guarda nada entre as duas chamadas).
- **FR-003**: Duplicata = mesma `user_id` + `book_id` + `content` normalizado (espaços) + mesma origem/localização no
  `source_hint`.
- **FR-004**: Frontend `views/EreaderImportView.vue` (envio, prévia com escolha por livro, resultado) e botão na
  `InboxView`. Só tokens, `.quiet`, 44 px, contraste ≥ 4,5:1 nos 10 temas, `aria-live` nos estados.
- **FR-005**: Sem migração; nenhum arquivo enviado fica no disco.

## 4. Success Criteria

- **SC-001**: Testes dos parsers com arquivos sintéticos (Kindle em inglês e português, BOM, CRLF, notas, marcadores,
  duplicatas por ajuste; Kobo com um `KoboReader.sqlite` sintético criado no teste) e dos endpoints (prévia não grava,
  importação cria e reenviar não duplica, livro criado, `skip`, arquivo inválido, limite de tamanho, livro de outro
  leitor recusado).
- **SC-002**: Teste de frontend da tela (envio, escolhas, resultado, `aria-live`).
- **SC-003**: Navegador (banco temporário, arquivos sintéticos): Kindle e Kobo de ponta a ponta até a bandeja;
  1366 e 375 px; contraste nos 10 temas.
- **SC-004**: Build, testes novos e vizinhos; commit; levar ao `main`.

## 5. Fora do escopo

- Importar direto do aparelho conectado (sem enviar o arquivo), da nuvem da Amazon ou do Kobo.
- Distribuir os destaques nos capítulos automaticamente (o Kobo tem o arquivo do capítulo, mas o título nem sempre
  corresponde aos capítulos do Leitorum; fica para depois da triagem manual).
- Readwise, Goodreads, KOReader/Readest (outros itens do 0.11 e do 1.0).
