# Experiment Specification: EXP-007 — Validação do Layout e da Ordem de Leitura em Imagens Reais

**Diretório do experimento**: `experiments/EXP-007/`

**Created**: 2026-10-12 · **Revisada**: 2026-10-12 (fonte dos dados trocada para datasets públicos, por decisão do
usuário)

**Status**: `DRAFT` — aguardando aprovação do usuário. Nenhum plano, tarefa, código ou download antes disso.

**Input**: ADR-002, ADR-003 e ADR-004 (aceitos); limitações declaradas nos EXP-002 e EXP-003 ("só páginas
sintéticas"); `dataset/README.md` (política de privacidade e de datasets públicos).

**Pré-requisito**: contrato LDF 2.0 aceito (2026-10-12).

**Numeração**: 007, porque 004 a 006 já estão reservados no roteiro. Ordem de execução: 003 → **007** → 004.

---

## 1. Pergunta e Hipóteses

**Pergunta central:** o que os EXP-002 e EXP-003 mediram em páginas **sintéticas** se mantém em imagens
**reais** — fotos de celular e caligrafia de verdade em português? Se não, onde quebra?

Toda a direção de trabalho (Doc-UFCN para linhas, Heron para blocos, retificação por contorno, ordem por
ancoragem) apoia-se em páginas renderizadas com fonte e degradadas por código. É a maior incerteza do que foi
decidido até aqui.

Nenhum dataset público encontrado reúne foto de celular, caderno, linhas, blocos e ordem de leitura. Por isso o
experimento usa **dois conjuntos complementares**, e cada hipótese é medida onde há verdade de chão para ela:

| Conjunto | O que tem de real | Verdade de chão disponível |
| :--- | :--- | :--- |
| **GNHK** — 687 fotos de anotações manuscritas tiradas com celular, em inglês | câmera, luz, perspectiva, fundo, papel | palavras com polígono agrupadas em linhas (a confirmar na abertura do arquivo) |
| **BRESSAY** — 1.000 páginas de redações manuscritas em português | caligrafia real de 1.000 pessoas, em português | recortes de linhas e de parágrafos de cada página, numerados; a posição na página precisa ser recuperada |

Hipóteses, com a referência sintética ao lado:

- **H1 (linhas em foto real — GNHK):** o F1 de linhas do Doc-UFCN `norhand` fica a no máximo 0,10 do sintético com
  degradação forte (0,784 sem retificação; 0,845 com).
- **H2 (retificação em foto real — GNHK):** a retificação por contorno encontra uma folha em ≥ 70 % das fotos e,
  onde encontra, não piora o F1 de linhas. (Muitas fotos do GNHK não mostram a folha inteira; por isso o limiar é
  mais baixo que no sintético.)
- **H3 (linhas em caligrafia portuguesa — BRESSAY):** F1 de linhas a no máximo 0,05 do sintético limpo (0,928).
- **H4 (blocos — BRESSAY):** os parágrafos são detectados pelo Heron com F1 ≥ 0,70 em IoU 0,5.
- **H5 (ordem — BRESSAY):** acurácia de ordem de blocos ≥ 0,90 com os parágrafos verdadeiros e ≥ 0,75 com os
  detectados.
- **H6 (custo):** tempo e memória por página ficam na mesma faixa dos experimentos anteriores.

Os limiares são critérios de avaliação. O experimento conclui com veredito explícito para cada hipótese, inclusive
"refutada" ou "não mensurável com estes dados".

---

## 2. Dados e licenças

| Item | GNHK | BRESSAY |
| :--- | :--- | :--- |
| Fonte | site oficial indicado em `github.com/GoodNotes/GNHK-dataset` | Zenodo, DOI 10.5281/zenodo.11637681 — **já está no disco** (`dataset/raw/exp-001/bressay.zip`, 1,4 GB) |
| Licença declarada | CC-BY-4.0 (repositório oficial) | conflitante: CC-BY-4.0 nos metadados, uso não comercial no README do arquivo |
| Estado | `LICENSE STATUS: VERIFIED` pelo que a fonte oficial declara (não é parecer jurídico) | `LICENSE STATUS: NEEDS VALIDATION` — exceção do usuário estendida ao EXP-007 em 2026-10-12: só experimento local, conteúdo fora do Git, não pode embasar produto |
| Download | **feito pelo usuário**: o site pede aceite de termos, e esse aceite não é do agente | nenhum |
| Destino | `dataset/raw/exp-007/gnhk/` (fora do Git) | reutilizado onde está, só leitura |

Cuidados que valem para os dois:

* As imagens são anotações e redações de pessoas reais. Nenhuma imagem, recorte ou **texto transcrito** vai para o
  Git, para relatórios versionados, para o chat ou para serviços externos. Relatórios trazem só números e
  identificadores de arquivo.
* O experimento não usa o texto das transcrições: mede só geometria.
* Atribuição (CC-BY) registrada em `docs/models-and-licensing.md` e no relatório.

`school_notebooks_RU` (cadernos pautados, MIT, 3 GB, cirílico) fica **fora** deste experimento, por decisão do
usuário; é candidato para depois, se a pauta do caderno se mostrar um problema.

---

## 3. Cenários Experimentais

### Cenário 1 — Abertura e auditoria dos dados (P1)

Conferir o que cada arquivo realmente contém antes de qualquer medição: formato da anotação do GNHK, tamanho,
hashes; no BRESSAY, se os recortes podem ser localizados na página.

**Critério de aceite:** relatório curto dizendo, para cada conjunto, qual verdade de chão existe de fato. Se a do
GNHK não permitir formar linhas, ou a do BRESSAY não puder ser localizada, a execução **para e pergunta**.

### Cenário 2 — Verdade de chão de linhas no GNHK (P1)

Formar a caixa e o contorno de cada linha a partir das palavras anotadas.

**Critério de aceite:** regra de agrupamento documentada e testada com casos fictícios; fotos sem anotação
utilizável são listadas, não descartadas em silêncio.

### Cenário 3 — Verdade de chão de linhas, blocos e ordem no BRESSAY (P1)

Recuperar a posição de cada recorte de linha e de parágrafo dentro da imagem da página; a ordem de leitura vem da
numeração dos parágrafos.

**Critério de aceite:** taxa de localização medida e reportada; páginas com localização incompleta ficam fora da
medição e são contadas. Uma amostra é conferida por sobreposição numérica (o recorte reaparece na posição
encontrada com erro abaixo de um limiar), sem inspeção de conteúdo.

### Cenário 4 — Medição com o pipeline dos ADR-002 e ADR-003 (P1)

Mesmos componentes, pesos, parâmetros e métricas dos experimentos aceitos. Nada é recalibrado nestes dados.

**Critério de aceite:** relatórios no formato dos anteriores; saídas em **LDF 2.0**, todas válidas.

### Cenário 5 — Comparação sintético × real e análise de falhas (P1)

Tabela lado a lado por métrica; no GNHK, com e sem retificação; análise de onde a perda acontece.

**Critério de aceite:** veredito para H1 a H6 e recomendação de próximo passo.

### Casos de borda

- Foto do GNHK sem folha visível inteira, com várias folhas, ou com texto impresso misturado.
- Palavras do GNHK sem índice de linha, ou marcadas como ilegíveis.
- Recorte do BRESSAY que aparece em mais de um lugar da página, ou em nenhum.
- Páginas muito grandes (memória) ou em orientação inesperada.
- Parágrafo de uma linha só; página com um único parágrafo (ordem trivial).

---

## 4. Requisitos

- **FR-001:** O pipeline medido é exatamente o dos ADR-002 e ADR-003: mesmos pesos (hashes conferidos), mesmos
  parâmetros e mesmo ponto de operação dos blocos. Nenhum ajuste nestes dados.
- **FR-002:** Subconjuntos fixos e reproduzíveis, escolhidos por sorteio com semente registrada antes de qualquer
  medição. Tamanho-alvo: 150 fotos do GNHK e 150 páginas do BRESSAY (o plano confirma pelo tempo disponível).
- **FR-003:** A lista de arquivos de cada subconjunto, com hash, é versionada; o conteúdo não.
- **FR-004:** As métricas são as dos experimentos anteriores (F1 de linhas, F1 e mAP de blocos, acurácia de
  ordem), mais a taxa de sucesso da retificação e a taxa de localização da verdade de chão.
- **FR-005:** O tipo de bloco não é avaliado no BRESSAY: só existe "parágrafo" na verdade de chão. A medição de
  blocos ignora a classe e diz isso no relatório.
- **FR-006:** Nenhuma imagem, recorte ou transcrição sai de `dataset/`; nada disso aparece em relatório, log
  versionado ou no chat. Metadados das fotos (EXIF) não são lidos nem reportados.
- **FR-007:** O `bressay.zip` do EXP-001 é lido onde está; os diretórios dos EXP-001 a EXP-003 não são
  modificados. O que for reaproveitado de código é copiado, como no EXP-003. Ambientes existentes são usados com
  `--frozen`.
- **FR-008:** Saídas em LDF 2.0, pelo conversor de referência (`leitorum_di.contracts.ldf.build_document`).
- **FR-009:** Sem modelo ou peso novo. Dependência nova só para ler os dados, se indispensável, e com parada para
  perguntar.
- **FR-010:** Critérios de parada dos experimentos anteriores (memória, tempo, RAM livre ≥ 1 GiB) continuam
  valendo; uso de disco medido antes e depois, dentro do teto de 20 GB.
- **FR-011:** Todos os relatórios e o ADR resultante trazem `LICENSE STATUS: NEEDS VALIDATION` na parte que
  depende do BRESSAY.

## 5. Critérios de Sucesso

- **SC-001:** Verdade de chão utilizável em ao menos 100 fotos do GNHK e 100 páginas do BRESSAY.
- **SC-002:** Veredito explícito para H1 a H6, com os números sintéticos de referência ao lado.
- **SC-003:** Análise de falhas que diga em qual etapa cada perda acontece.
- **SC-004:** 100 % das saídas válidas em LDF 2.0.
- **SC-005:** Nenhum conteúdo dos datasets no Git; nada fora de `document-intelligence/`; disco dentro do teto.
- **SC-006:** ADR novo, ou revisão dos ADR-002/003, conforme o que os dados mostrarem.

## 6. Fora do escopo

- Reconhecimento de texto (ADR-001) e qualquer uso das transcrições.
- Treinar, ajustar ou trocar modelos; recalibrar parâmetros.
- Fotos do acervo pessoal do usuário, em qualquer hipótese.
- Imprimir e fotografar páginas sintéticas (fica como experimento posterior, se necessário).
- Classificação semântica e diagramas (EXP-004 e EXP-005); integração com o site.

## 7. Limitações já conhecidas

- **Ordem de leitura com notas de margem em foto real continua sem medição.** Redações não têm margem anotada, e
  o GNHK não tem blocos. Só páginas próprias fotografadas cobririam isso.
- O GNHK é em inglês e não é caderno de estudo; o BRESSAY é em português, mas não é foto de celular nem caderno.
  Nenhum dos dois, sozinho, é o caso de uso do produto.
- A verdade de chão de linhas do GNHK é derivada (agrupamento de palavras), e a do BRESSAY é recuperada por
  localização de recortes: as duas têm erro próprio, que será medido e reportado.
- O BRESSAY tem licença em validação: os resultados que dependem dele não podem embasar decisão de produto.

## 8. O que preciso de você

1. **Aprovar esta especificação.**
2. **Baixar o GNHK**, quando for conveniente: pelo link no repositório oficial (`github.com/GoodNotes/GNHK-dataset`),
   aceitar os termos e salvar `train_data.zip` e `test_data.zip` em
   `document-intelligence/dataset/raw/exp-007/gnhk/`. Não precisa descompactar. Enquanto isso, plano e tarefas
   podem avançar, e a parte do BRESSAY pode ser executada primeiro.
