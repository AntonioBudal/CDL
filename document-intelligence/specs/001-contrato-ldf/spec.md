# Especificação: Fechamento do contrato LDF

* **Feature:** `001-contrato-ldf`
* **Criada em:** 2026-10-12
* **Status:** `APPROVED` (aprovada pelo usuário em 2026-10-12, com as decisões da §9)
* **Tipo:** feature de contrato (não é experimento; não baixa modelos nem mede candidatos)
* **Origem:** lacunas registradas no [EXP-002](../../experiments/EXP-002/RESULTS.md) (§5), no
  [EXP-003](../../experiments/EXP-003/RESULTS.md) (§5) e nos ADR-002 e ADR-003
* **Próximo artefato:** [`plan.md`](./plan.md)

---

## 1. Por que agora

O LDF é a única fronteira entre o Document Intelligence e o Leitorum (Princípio 8). Três experimentos já
escreveram documentos nesse formato e encontraram o mesmo problema: o contrato de hoje não consegue guardar o que o
pipeline produz, e existe em duas versões que se contradizem.

Enquanto isso não for resolvido:

* o EXP-004 (classificação semântica) e o EXP-005 (diagramas) mediriam saídas num formato que vai mudar;
* nenhum teste no site é possível, porque o Leitorum não tem um formato estável para ler;
* cada experimento novo repete um conversor com a mesma lista de "lacunas conhecidas".

## 2. Lacunas a fechar

Levantadas nos experimentos e na leitura de `docs/ldf.md`, `docs/schemas/ldf-1.0.schema.json` e
`src/leitorum_di/contracts/ldf.py`.

| # | Lacuna | Evidência |
| :--- | :--- | :--- |
| L1 | **Dois contratos divergentes.** O modelo Python e o JSON Schema discordam na raiz do documento, nos nomes dos campos, nos tipos de bloco e nas categorias semânticas. Um documento válido em um é inválido no outro. | EXP-002 §5 |
| L2 | **Região de diagrama sem lugar.** `structure.diagrams[]` só tem nós e arestas; a caixa do diagrama na página não pode ser gravada. | EXP-002: 100 % das caixas gráficas viraram diagramas vazios |
| L3 | **Ordem de leitura só aceita blocos.** Caixas gráficas ficam fora da ordem serializada. | EXP-003: 102 caixas no layout verdadeiro, 140 no detectado |
| L4 | **Etapa não executada é indistinguível de resultado vazio.** Sem reconhecimento de texto, a linha sai com `text: ""` e `confidence: 0`, igual a uma linha lida como vazia. O mesmo vale para `semantics`, que é obrigatória mesmo quando não rodou. | conversores do EXP-002 e EXP-003 |
| L5 | **Sistema de coordenadas indefinido após a retificação.** O ADR-002 adota retificação de perspectiva, mas o formato diz apenas "pixels da imagem original" e não guarda a transformação. | ADR-002 |
| L6 | **Geometria pobre para linhas inclinadas.** A caixa alinhada aos eixos é obrigatória e inteira; o polígono é opcional e sem regra de ordem dos vértices. | EXP-002 §5 |
| L7 | **Vocabulário de tipos inconsistente.** `title` × `heading`; `text_block`, `list_item` e `table` nunca foram produzidos; `diagram_region` só existe no modelo Python. | EXP-002 e EXP-003 |
| L8 | **Integridade referencial não verificada.** Nada garante identificadores únicos nem que `line_ids`, `block_ids` e `reading_order` apontem para elementos existentes. | leitura do schema |
| L9 | **Correções humanas frágeis.** Os caminhos de JSON Patch usam posição no vetor (`/recognition/lines/0/text`), que muda quando uma linha é inserida ou removida; não está dito se o documento guardado é o original ou o já corrigido. | leitura de `docs/ldf.md` §3.4 |
| L10 | **Metadados do pipeline livres.** `model_versions` aceita qualquer coisa; não há como rastrear revisão de pesos nem estado de licença de cada componente. | Princípio 3 |

## 3. Histórias de uso

### História 1 — Um contrato só (P1)

Quem escreve um experimento ou a integração com o Leitorum consulta uma única definição do LDF e obtém a mesma
resposta de validação, não importa a ferramenta.

**Teste independente:** validar o mesmo conjunto de documentos pelas duas vias e comparar os veredictos.

1. **Dado** um documento válido pelo JSON Schema, **quando** ele é carregado pelo modelo Python, **então** é aceito
   e, regravado, continua válido e equivalente.
2. **Dado** um documento com campo desconhecido ou tipo de bloco inexistente, **quando** validado por qualquer via,
   **então** é rejeitado pelas duas, com mensagem que aponta o campo.
3. **Dado** um documento com `line_ids` apontando para linha inexistente, **quando** validado, **então** é rejeitado
   com o identificador faltante na mensagem.

### História 2 — Guardar tudo o que o pipeline já produz (P1)

A saída de layout e ordem de leitura dos EXP-002 e EXP-003 é gravada sem perda e sem lista de lacunas à parte.

**Teste independente:** converter as páginas sintéticas dos dois experimentos e conferir que nenhuma região é
descartada.

1. **Dado** uma página com caixa gráfica, **quando** convertida, **então** a região da caixa está no documento e
   aparece na ordem de leitura na posição correta.
2. **Dado** uma página só com layout (sem texto reconhecido), **quando** convertida, **então** o documento declara
   que o reconhecimento de texto não foi executado, e nenhuma linha traz texto ou confiança inventados.
3. **Dado** uma página retificada, **quando** convertida, **então** o documento diz em qual imagem as coordenadas
   estão e permite levá-las de volta à fotografia original.
4. **Dado** uma linha inclinada, **quando** convertida, **então** seu contorno é preservado além da caixa.

### História 3 — Documento parcial honesto (P2)

O Leitorum recebe um documento em que só algumas etapas rodaram e sabe exatamente quais, sem inferir pelo conteúdo.

1. **Dado** um documento sem etapa semântica, **quando** lido, **então** o estado dessa etapa é "não executada", e
   não "executada sem achados".
2. **Dado** uma etapa que falhou, **quando** o documento é lido, **então** as demais etapas continuam utilizáveis e
   a falha está identificada.

### História 4 — Correção humana que sobrevive (P2)

Uma correção feita no Leitorum continua apontando para o elemento certo depois de outras correções.

1. **Dado** uma correção de texto na terceira linha, **quando** uma linha anterior é removida por outra correção,
   **então** a primeira correção ainda se aplica à mesma linha.
2. **Dado** um documento com correções, **quando** lido, **então** é possível obter tanto a saída original do
   pipeline quanto a versão corrigida, e saber quem corrigiu e quando.

### História 5 — Reprodutibilidade dos experimentos aceitos (P1)

Os EXP-002 e EXP-003 continuam reproduzíveis exatamente como foram aceitos.

1. **Dado** o repositório após esta feature, **quando** os testes e comandos de reprodução dos EXP-002 e EXP-003
   são executados, **então** passam sem nenhuma alteração nos diretórios desses experimentos.

### Casos de borda

* Página sem nenhuma linha ou bloco detectado.
* Linha que não pertence a nenhum bloco; bloco sem linhas.
* Região presente na página mas deliberadamente fora da ordem de leitura.
* Diagrama com região conhecida e sem nós nem arestas (o estado atual da pesquisa).
* Coordenadas fora dos limites da imagem ou caixa degenerada (largura ou altura zero).
* Documento de uma versão mais nova lido por um leitor mais antigo.

## 4. Requisitos funcionais

**Fonte única**

* **FR-001:** Deve existir uma única definição normativa do LDF; as demais representações devem derivar dela ou
  ser conferidas contra ela por teste automático que falha em qualquer divergência.
* **FR-002:** A documentação em prosa, o schema, o modelo Python e os exemplos devem descrever o mesmo formato;
  todo exemplo versionado deve ser validado nos testes.
* **FR-003:** A validação deve cobrir integridade referencial: identificadores únicos no documento e toda
  referência apontando para elemento existente.

**Capacidade de representação**

* **FR-004:** Toda região detectada na página, inclusive diagramas e caixas gráficas, deve ter sua localização
  gravada.
* **FR-005:** A ordem de leitura deve poder incluir qualquer região da página, não só blocos de texto.
* **FR-006:** Cada etapa do pipeline (layout, ordem de leitura, reconhecimento de texto, semântica, diagramas) deve
  ter estado explícito: executada, não executada ou falhou.
* **FR-007:** Linha sem reconhecimento de texto deve ser representável sem texto nem confiança fictícios.
* **FR-008:** O documento deve declarar o sistema de coordenadas usado e, havendo retificação, guardar o necessário
  para converter as coordenadas à imagem original.
* **FR-009:** O contorno de linhas e regiões inclinadas deve ser representável, com convenção definida para ordem
  dos vértices e relação entre contorno e caixa.
* **FR-010:** O vocabulário de tipos de região deve ser único e cobrir ao menos título, parágrafo, nota de margem e
  região gráfica; tipos nunca produzidos por experimento ficam fora ou marcados como reservados.

**Correções e rastreabilidade**

* **FR-011:** As correções humanas devem referir-se a elementos de forma estável, independente da posição no vetor,
  mantendo RFC 6902 como formato das operações (`CLAUDE.md` §4).
* **FR-012:** O formato deve definir se o documento carrega a saída original, a corrigida ou ambas, e a ordem de
  aplicação das correções.
* **FR-013:** Cada componente do pipeline registrado no documento deve trazer nome, versão ou revisão e estado de
  licença.

**Compatibilidade e limites**

* **FR-014:** O arquivo `docs/schemas/ldf-1.0.schema.json` atual deve permanecer inalterado, byte a byte, porque os
  conversores dos EXP-002 e EXP-003 o leem pelo caminho. O contrato fechado é publicado em arquivo novo.
* **FR-015:** A regra de versão deve dizer o que um leitor faz ao encontrar versão mais nova que a sua.
* **FR-016:** A camada semântica **não** é fechada nesta feature: fica marcada como provisória até o EXP-004, com
  apenas o mínimo necessário para o estado de etapa (FR-006).
* **FR-017:** O detalhamento de nós e arestas de diagramas **não** é alterado: fica como está até o EXP-005.
* **FR-018:** Deve existir um conversor de referência, fora dos diretórios dos experimentos aceitos, que grave a
  saída de layout e ordem no contrato fechado, para uso do EXP-004 em diante.
* **FR-019:** Nenhuma dependência pesada nova; nenhuma chamada de rede; exemplos e testes só com dados fictícios.
* **FR-020:** A decisão deve ser registrada em ADR próprio (ADR-004), com as alternativas consideradas.

## 5. Entidades principais

* **Documento:** uma página processada, com identidade, imagem de origem, estados das etapas e correções.
* **Imagem de origem e sistema de coordenadas:** a fotografia e, se houver, a imagem retificada e a transformação
  entre elas.
* **Linha:** unidade de reconhecimento, com geometria e, quando houver, texto e confiança.
* **Região:** área da página com tipo (título, parágrafo, nota de margem, gráfica), geometria e linhas contidas.
* **Ordem de leitura:** sequência de regiões.
* **Etapa do pipeline:** nome, estado, componente usado, revisão e licença.
* **Correção humana:** operação sobre um elemento identificado, com autoria e data.

## 6. Critérios de sucesso

* **SC-001:** 100 % dos exemplos versionados recebem o mesmo veredicto pelas duas vias de validação.
* **SC-002:** As 180 páginas de teste do EXP-003 são convertidas com **zero** lacunas registradas e zero regiões
  descartadas (hoje: 102 a 140 caixas gráficas fora da ordem).
* **SC-003:** Um conjunto de documentos inválidos de propósito, cobrindo L1 a L9, é rejeitado em 100 % dos casos
  com mensagem que identifica o problema.
* **SC-004:** Os testes dos EXP-002 e EXP-003 e a suíte principal (`uv run pytest`) passam; `git diff` sem nenhuma
  mudança em `experiments/EXP-001`, `EXP-002` e `EXP-003`.
* **SC-005:** As dez lacunas da §2 estão cada uma resolvida ou explicitamente adiada com justificativa no ADR-004.
* **SC-006:** Nada fora de `document-intelligence/` é modificado.

## 7. Fora do escopo

* API HTTP local (`docs/api-local.md` continua `DRAFT`) e qualquer serviço em execução.
* Integração com o backend ou o frontend do Leitorum; leitura do LDF pelo produto.
* Vocabulário semântico definitivo (EXP-004) e estrutura de diagramas (EXP-005).
* Documentos de várias páginas, cadernos inteiros e ligação entre páginas.
* Melhorar a detecção de blocos ou validar em fotos reais (passos seguintes, a decidir).
* Qualquer modelo, peso ou dataset novo.

## 8. Premissas

* Nenhum sistema lê LDF hoje: os únicos documentos gerados são saídas descartáveis dos experimentos. Mudanças
  incompatíveis não afetam ninguém além dos conversores dos experimentos, que ficam preservados (FR-014).
* Um documento LDF representa uma página.
* As coordenadas continuam em pixels.

## 9. Decisões do usuário (2026-10-12)

| # | Pergunta | Decisão |
| :--- | :--- | :--- |
| 1 | Número da versão do contrato fechado | **2.0.0**; o schema 1.0 fica congelado para os experimentos aceitos |
| 2 | Fonte normativa | **JSON Schema**; o modelo Python é conferido contra ele por teste |
| 3 | Sistema de coordenadas | **Fotografia original**; a transformação da retificação vai como metadado |
| 4 | Documento com correções | **Saída original intacta** mais a lista de correções; a versão corrigida é obtida por aplicação |
| 5 | Páginas por documento | **Uma**; cadernos de várias páginas ficam para depois |
