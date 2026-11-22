# Especificação: F-DI-13.03 — Catálogo de procedência (E2)

* **Feature:** `004-catalogo-de-procedencia` (item **F-DI-13.03** redefinido pela
  [estratégia de dados v2](../../docs/replanejamento-0.13/09-estrategia-de-aquisicao-de-dados.md), etapa **E2**;
  substitui a [spec 003](../003-kit-de-coleta/spec.md), que não foi executada)
* **Criada em:** 2026-11-22
* **Status:** `IMPLEMENTED` (aprovada pelo usuário em 2026-11-22; SC-001 a SC-003 conferidas)
* **Depende de:** EXP-043 (fontes medidas) · **Libera:** EXP-031P (E3) e os conectores (E4)

---

## 1. Por que

Antes de baixar centenas de milhares de linhas, cada arquivo precisa entrar com a sua procedência registrada:
de onde veio, sob que licença, em que situação de uso, sem duplicata, e com a certeza de que dá para tirá-lo
depois — inclusive dos modelos que aprenderam com ele. É o "mínimo" da estratégia: sem interface, sem conector
completo; só o registro e as regras.

## 2. O que o catálogo faz (em uma frase cada)

* **Registra fontes** com a licença padrão, a forma de acesso e uma cópia datada dos termos (com hash).
* **Registra itens** (uma linha de manuscrito, ou uma página) com fonte, endereço, licença, condições
  (atribuição, compartilha-igual, não comercial), situação de uso, idioma, época, escritor quando houver,
  divisão oficial da fonte (treino/validação/teste) e transcrição.
* **Guarda arquivos por conteúdo** (o nome é o SHA-256): duplicata exata não ocupa espaço duas vezes; quase
  duplicata de página é marcada por *hash* perceptivo.
* **Aplica as situações de uso** da estratégia: `APPROVED`, `EXPERIMENT_ONLY`, `PENDING_REVIEW` (só metadados,
  sem arquivo), `REJECTED` (apagado com derivados e bloqueado), `BLOCKED`.
* **Revisa** uma fonte inteira ou um item, com motivo e evidência; a lista de pendentes sai agrupada por fonte
  e motivo.
* **Apaga de verdade** o que for rejeitado (arquivos não usados por outro item, derivados) e põe o hash e o
  endereço numa **lista de bloqueio**, para nunca mais entrarem.
* **Registra cada ciclo de treino**: a lista exata de itens, com a licença e a situação naquele momento; marca
  como **contaminado** todo ciclo que usou um item rejeitado depois; recusa promover ao produto um ciclo que
  tenha algo diferente de `APPROVED`.
* **Gera o resumo do conteúdo de treino** de um ciclo (fontes, licenças, condições, contagens, atribuições).
* **Controla o espaço**: teto total de 100 GB e teto por pasta; recusa ingerir acima do teto.
* **Confere a integridade** (rehash dos arquivos) sob demanda.

## 3. Histórias de uso

### História 1 — Ingerir uma fonte aprovada (P1)

**Aceite:** importar as amostras aprovadas do EXP-043 cria as fontes, os itens e os arquivos; reimportar não
duplica nada; uma linha cujo hash está na lista de bloqueio é recusada; os arquivos de linha ficam no formato
padrão (cinza, 64 px de altura, PNG — ver plano, decisão 1), com as dimensões registradas.

### História 2 — Pendência e revisão (P1)

**Aceite:** um item de fonte `PENDING_REVIEW` entra só com metadados (nenhum arquivo); aprovar a fonte muda a
situação de todos os itens dela de uma vez e libera o download no próximo lote; rejeitar apaga os arquivos e
derivados, bloqueia os hashes e endereços e registra a revisão.

### História 3 — Ciclo de treino rastreável (P1)

**Aceite:** um ciclo de **experimento** aceita `APPROVED` e `EXPERIMENT_ONLY`; um ciclo de **produto** só
`APPROVED`; cada ciclo grava a lista de itens com hash, licença e situação; rejeitar depois um item usado marca
o ciclo como contaminado, e a conferência de promoção falha com o motivo.

### História 4 — Espaço e integridade (P2)

**Aceite:** o relatório de uso mostra cada pasta contra o seu teto; a ingestão para ao bater o teto; a
conferência de integridade acha um arquivo alterado de propósito num teste.

## 4. Requisitos

* **FR-001** SQLite local (biblioteca padrão), em `D:\Leitorum-DI\catalogo\catalogo.sqlite`; a raiz muda por
  `LEITORUM_DI_DATA` (testes usam pasta temporária).
* **FR-002** Armazenamento por conteúdo em `D:\Leitorum-DI\objetos\<2 primeiros>\<sha256>.<ext>`.
* **FR-003** Situações e regras da §3 e §5 da estratégia v2; condições de licença como lista (`by`, `sa`, `nc`).
* **FR-004** Lista de bloqueio por hash, endereço e id de item.
* **FR-005** Ciclos de treino com itens, situação e licença no momento; contaminação; conferência de promoção.
* **FR-006** Resumo do conteúdo de treino em Markdown/JSON, sem texto dos itens.
* **FR-007** Tetos: total 100 GB; por pasta conforme a estratégia (§7).
* **FR-008** Comando de linha (`python -m tools.catalogo …`) e uma API Python para os importadores.
* **FR-009** Nenhum texto de item, imagem ou dado privado vai para o Git; o repositório guarda só código,
  schema e testes.

## 5. Critérios de sucesso

* **SC-001** Testes com dados fictícios para as quatro histórias (inclusive: rejeição apaga e contamina;
  promoção recusa ciclo contaminado; reimportação idempotente; pendente sem arquivo).
* **SC-002** As amostras aprovadas do EXP-043 importadas de verdade: contagens por fonte iguais às do
  relatório; nenhuma duplicata; espaço medido.
* **SC-003** `uv run pytest` e `uv run ruff check .` verdes.

## 6. Fora do escopo

Conectores completos (E4), interface visual, deduplicação por semelhança de texto entre fontes, revisão
automática de licença (a revisão é humana, agrupada por fonte).
