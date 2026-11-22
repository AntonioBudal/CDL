# Especificação: F-DI-13.03 — Kit de coleta de páginas de várias pessoas

* **Feature:** `003-kit-de-coleta` (item **F-DI-13.03** do [roadmap v3](../../docs/replanejamento-0.13/08-roadmaps-v3-leitor-geral.md))
* **Criada em:** 2026-11-20
* **Status:** `SUPERSEDED` (aprovada em 2026-11-20 e não executada; substituída pela [estratégia de dados v2](../../docs/replanejamento-0.13/09-estrategia-de-aquisicao-de-dados.md):
  sem coleta com amigos; a F-DI-13.03 passa a ser o catálogo de procedência, com spec própria)
* **Tipo:** feature de dados e governança do Document Intelligence (não é experimento; não treina nem baixa nada)
* **Próximos que dependem dela:** F-DI-13.04 (transcrição pela própria pessoa), F-DI-13.02 (trava por pessoa),
  Dados-13.G (primeira coleta)

---

## 1. Por que

O leitor geral precisa de fotos e transcrições de várias pessoas. São dados pessoais de terceiros: antes de pedir
qualquer página a um amigo, o projeto precisa de um termo claro, de instruções que garantam fotos úteis, de um
registro que identifique cada pessoa sem expor o nome, e de um jeito comprovado de **retirar** alguém.

## 2. O que o kit entrega

1. **Termo de consentimento** (`docs/coleta/termo-de-consentimento.md`), em português simples, para imprimir ou
   preencher: o que é coletado, para quê, onde fica, quem acessa, o direito de retirar, o que acontece com um
   modelo já treinado, e a idade mínima (18 anos).
2. **Guia de foto e de transcrição** (`docs/coleta/guia-para-quem-participa.md`), uma página: como fotografar
   (luz, página inteira, sem flash, arquivo original), como enviar (cabo, e-mail ou nuvem; **não** por
   WhatsApp/Telegram, que comprimem), que páginas escolher (anotações de estudo sem dados pessoais) e como
   transcrever (um `.txt` por foto, uma linha do papel por linha, `$…$`, `[?]`, riscado ignorado).
3. **Registro de pessoas** pelo comando `tools.anotar.pessoas`:
   * `adicionar` — cria `w01`, `w02`… (o autor do projeto é `w00`), guarda nome e termo **fora do Git** e grava no
     registro versionado só o id, a data do termo e o SHA-256 do arquivo do termo;
   * `registrar-fotos` — confere e registra as fotos da pasta da pessoa (`wNN-p01`, `wNN-p02`…, hash e tamanho),
     recusando foto repetida (mesmo hash em outra pessoa ou página) e foto pequena demais (lado maior < 2000 px,
     sinal de compressão);
   * `retirar` — a pessoa sai: apaga as pastas dela (fotos, transcrições, anotações, imagens de trabalho), marca
     `retirada` no registro versionado com a data e tira as páginas dela de qualquer conjunto. Só roda com
     `--confirmar wNN` digitado de novo;
   * `listar` — situação de cada pessoa (só ids, datas e contagens).
4. **Pastas por pessoa** fora do Git: `dataset/raw/pessoas/wNN/{termo,fotos,transcricoes}/`.

## 3. Histórias de uso

### História 1 — Chamar um amigo (P1)

O autor manda o guia e o termo; o amigo devolve o termo assinado, as fotos e as transcrições. O autor roda
`adicionar` e `registrar-fotos`.

**Aceite:** a pessoa ganha um `wNN`; nome e termo ficam só em `dataset/raw/pessoas/` (fora do Git); o registro
versionado não tem nome; as fotos ficam registradas por hash; uma foto comprimida demais é recusada com o motivo.

### História 2 — Alguém desiste (P1)

**Aceite:** `retirar wNN --confirmar wNN` apaga todos os arquivos daquela pessoa no projeto e deixa no registro
só `wNN: retirada em <data>`; um teste confere que nada com o id sobra em `dataset/` e que as páginas saem dos
manifestos.

### História 3 — Ninguém aparece em dois conjuntos (P1)

**Aceite:** o registro guarda, por pessoa, o conjunto (`treino`, `validacao`, `teste` ou vazio); a função de
conferência recusa uma página cuja pessoa está em outro conjunto. (O sorteio por pessoa é do Dados-13.G; aqui
só a estrutura e a conferência.)

## 4. Requisitos

* **FR-001** Nenhum dado que identifique a pessoa no Git: nome, contato e termo ficam em `dataset/raw/pessoas/`
  (já coberto pelo `.gitignore` de `dataset/raw/*`); um teste confere que o registro versionado só tem campos
  permitidos.
* **FR-002** Registro versionado em `document-intelligence/splits/pessoas.json` e `splits/paginas.json`
  (ids, datas, hashes, tamanhos, conjunto, situação), com histórico de emendas.
* **FR-003** O autor do projeto entra como `w00`, com as 20 páginas de 512 px marcadas `low_resolution` (as
  mesmas do EXP-027; continuam também no teste do autor).
* **FR-004** `retirar` apaga de verdade (não move para lixeira) e é idempotente.
* **FR-005** Termo e guia em linguagem simples, revisáveis pelo usuário; o termo diz que **não é um documento
  jurídico revisado por advogado**.

## 5. Critérios de sucesso

* **SC-001** Termo e guia aprovados pelo usuário.
* **SC-002** Testes com pessoas fictícias: adicionar → registrar fotos → recusar repetida e pequena → listar →
  retirar sem deixar rastro; nenhum nome no registro versionado; conferência de conjunto.
* **SC-003** `uv run pytest` e `uv run ruff check .` verdes.

## 6. Fora do escopo

* Importar a transcrição e o `writer_id` na ferramenta de anotação (F-DI-13.04).
* Sortear pessoas para teste e validação (Dados-13.G).
* Coleta pelo Leitorum (0.14.5).
* Revisão jurídica do termo (fica com o usuário, se quiser).

## 7. O que depende do usuário

Ler e aprovar o texto do termo e do guia (vêm junto com a implementação, para revisão).
