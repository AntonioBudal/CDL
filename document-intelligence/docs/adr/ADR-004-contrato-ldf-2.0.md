# ADR-004: Contrato LDF 2.0 — JSON Schema como fonte única, coordenadas na foto original, correções por identificador

* **Status:** ACCEPTED (aceito pelo usuário em 2026-10-12)
* **Data:** 2026-10-12
* **Decisores:** Usuário (decisão); Claude Code (proposta)
* **Experimento de Suporte:** não é um experimento. Evidência: lacunas do [EXP-002](../../experiments/EXP-002/RESULTS.md) (§5) e do [EXP-003](../../experiments/EXP-003/RESULTS.md) (§5); feature [`specs/001-contrato-ldf`](../../specs/001-contrato-ldf/spec.md)
* **Status de Licença:** `jsonschema` 4.26.0, MIT (metadados do pacote instalado) — `LICENSE STATUS: VERIFIED`. Nenhum modelo, peso ou dataset.

---

## 1. Contexto e Declaração do Problema

O LDF é a única fronteira entre o Document Intelligence e o Leitorum. Na versão 1.0 ele existia em duas definições
que se contradiziam (JSON Schema e modelo Pydantic) e não conseguia guardar o que o pipeline já produz: a região de
um diagrama não tinha campo, a ordem de leitura só aceitava blocos de texto, e uma etapa não executada era
indistinguível de um resultado vazio. Três experimentos escreveram conversores com a mesma lista de "lacunas
conhecidas". Sem um contrato estável não há como medir os próximos experimentos no formato final nem como o
Leitorum começar a ler a saída.

Nenhum sistema lê LDF hoje; os únicos documentos gerados eram saídas descartáveis dos experimentos.

---

## 2. Drivers de Decisão (Critérios de Avaliação)

* **Driver 1:** Uma definição só, verificável por máquina, utilizável fora do Python.
* **Driver 2:** Representar sem perda a saída de layout e ordem de leitura dos EXP-002 e EXP-003.
* **Driver 3:** Não desenhar o que nenhum experimento exercitou.
* **Driver 4:** Preservar a reprodução dos experimentos aceitos.
* **Driver 5:** Correções humanas rastreáveis e reversíveis (RFC 6902).
* **Driver 6:** Local-first, sem dependência pesada.

---

## 3. Opções Consideradas

### Opção A: LDF 1.1 — só acréscimos opcionais ao 1.0

Mantém leitores de 1.0 funcionando. Mas não há leitores de 1.0, e o texto obrigatório da linha e o vocabulário de
tipos inconsistente continuariam como estavam.

### Opção B: LDF 2.0 com o modelo Python como fonte e o schema gerado

Uma fonte só, confortável para quem escreve Python. O backend do Leitorum passaria a depender deste pacote, ou de
um arquivo gerado, para validar.

### Opção C: LDF 2.0 com o JSON Schema como fonte e o modelo Python conferido por teste

O schema é lido por qualquer linguagem. O modelo Pydantic é um espelho tipado; um teste compara os dois campo a
campo e por veredicto. O que o schema não expressa vira regra numerada, com casos de conformidade.

---

## 4. Decisão Escolhida

**Opção C**, com as decisões do usuário de 2026-10-12:

1. **Versão 2.0.0.** O schema 1.0 fica congelado em `docs/schemas/`, porque os conversores dos EXP-002 e EXP-003 o
   leem pelo caminho.
2. **JSON Schema como fonte normativa**, em cópia única dentro do pacote. `jsonschema` entra como dependência.
3. **Coordenadas na fotografia original.** A retificação vai como metadado (`source_quad`, `output_size`,
   `homography`).
4. **Saída original intacta mais lista de correções.** A versão corrigida é calculada.
5. **Uma página por documento.**

E as decisões de desenho que decorrem delas:

6. `blocks` vira `regions`, com quatro tipos: `title`, `paragraph`, `margin_note`, `graphic`. A ordem de leitura
   aceita qualquer região. Todo diagrama aponta para uma região `graphic`.
7. Cada etapa do pipeline tem estado (`completed`, `not_run`, `failed`), componente e estado de licença. `text` e
   `confidence` da linha e a camada `semantics` deixam de ser obrigatórios.
8. Correções apontam para o elemento pelo `id`; as operações RFC 6902 têm caminho relativo a ele.
9. Regras R1–R9 fora do schema, com códigos estáveis e casos de conformidade versionados.
10. Um leitor recusa versão mais nova que a sua.

Como os ADRs anteriores, este não promove modelo nenhum a produto.

### Situação de cada lacuna

| # | Lacuna | Situação |
| :--- | :--- | :--- |
| L1 | Dois contratos divergentes | **Resolvida.** Paridade de estrutura e de veredicto testada; cópia única do schema |
| L2 | Região de diagrama sem lugar | **Resolvida.** A região `graphic` guarda a caixa; o diagrama a referencia |
| L3 | Ordem de leitura só com blocos | **Resolvida.** As 102 caixas gráficas do conjunto de teste do EXP-003 entram na ordem |
| L4 | Etapa não executada indistinguível | **Resolvida.** `pipeline.stages`, R7 e R8 |
| L5 | Coordenadas após a retificação | **Resolvida.** Tudo na foto original; `rectification` como metadado |
| L6 | Geometria pobre para linhas inclinadas | **Resolvida.** Decimais; polígono em sentido horário; caixa = envelope (R6) |
| L7 | Vocabulário de tipos inconsistente | **Resolvida para regiões.** Quatro tipos com produtor conhecido |
| L8 | Integridade referencial | **Resolvida.** R1–R4 |
| L9 | Correções frágeis | **Resolvida** para o alvo da correção. **Limitação:** dentro de um elemento, um caminho como `/line_ids/2` ainda depende de posição; a forma recomendada é substituir a lista inteira |
| L10 | Metadados do pipeline livres | **Resolvida.** `component` com versão, revisão e estado de licença |
| — | Vocabulário semântico | **Adiado** para depois do EXP-004; camada marcada provisória |
| — | Estrutura de nós e arestas | **Adiado** para depois do EXP-005; mantida como no 1.0 |

---

## 5. Evidência

Medido em 2026-10-12, no ambiente do EXP-000 (CPU, Python 3.14.3):

| Verificação | Resultado |
| :--- | :--- |
| Casos de conformidade | 12 válidos aceitos; 47 inválidos rejeitados, cada um só com o código declarado; ao menos dois por código |
| Paridade schema × modelo Pydantic | estrutura idêntica; mesmo veredicto de forma nos 59 casos; ida e volta sem perda |
| Páginas de teste do EXP-003, layout verdadeiro (no Git) | 180 de 180 convertidas; zero regiões descartadas; 102 caixas gráficas, todas na ordem de leitura |
| Páginas de teste do EXP-003, layout detectado (no disco, fora do Git) | 180 de 180 convertidas; 3 777 linhas e 3 561 regiões brutas (antes do filtro de blocos), nenhuma descartada; zero problemas de validação |
| Schema 1.0 e diretórios dos EXP-001 a EXP-003 | inalterados (hash e árvores Git conferidos por teste) |

---

## 6. Consequências

### Consequências Positivas

* O EXP-004 em diante mede saídas no formato final, com um conversor de referência (`build_document`).
* O Leitorum pode validar com o schema e os casos de conformidade, sem depender deste pacote.
* Documentos parciais são honestos: quem lê sabe quais etapas rodaram e com qual componente e licença.

### Consequências Negativas / Trade-offs

* **Duas implementações para manter em sincronia** (schema e modelo); o teste de paridade reduz o risco, não o trabalho.
* **Regras fora do schema.** Um leitor que só valide o schema aceita documentos com referências quebradas. As
  regras estão documentadas e têm casos de teste, mas precisam ser implementadas por quem lê.
* **Validação lenta com contornos densos.** Com os polígonos que o Doc-UFCN devolve (em média 174 vértices por
  linha), validar uma página custa cerca de 0,13 s em Python, quase tudo na checagem de forma; com os contornos do
  manifesto (4 a 9 vértices), cerca de 8 ms.
  Simplificar o contorno antes de gravar é assunto do pipeline, não do contrato, e não foi medido aqui.
* **Lockfiles dos experimentos aceitos.** Seis ambientes dos EXP-001 e EXP-002 instalam o pacote principal em modo
  editável. Com `jsonschema` nas dependências dele, `uv run --project <ambiente>` passa a querer reescrever o
  `uv.lock` do ambiente (só o trecho que descreve o `leitorum-di`). Para reproduzir os experimentos sem tocar neles,
  use `uv run --frozen --project <ambiente> …`. Verificado: com `--frozen`, os testes dos harness passam (33 e 46) e
  os diretórios ficam inalterados. Nenhum código de experimento importa `leitorum_di.contracts`. Decisão do usuário
  (2026-10-12): manter os experimentos intocados e usar `--frozen`.
* **`semantics` e diagramas mudarão.** Quem construir sobre eles agora terá retrabalho.
* **Sem validação em fotos reais.** O formato foi exercitado só com páginas sintéticas, como os experimentos.
* O modelo Pydantic compara tipos em modo estrito: recusa `1.0` onde o schema pede inteiro, embora o JSON Schema
  aceite. Não afeta documentos gerados pelo conversor.

### Conformidade com a Constituição

* [x] Local-first: sem rede, sem serviço.
* [x] Sem modelos prematuros: nenhuma biblioteca de OCR/HTR; só `jsonschema`.
* [x] Experimentos antes de features: o contrato cobre apenas o que os EXP-002/003 produzem.
* [x] LDF como contrato soberano: é o objeto desta decisão; 1.0 preservado, 2.0 versionado.
* [x] Human-in-the-loop: correções em RFC 6902.
* [x] Escopo: nada fora de `document-intelligence/`.
