# Experiment Specification: EXP-001 — HTR em Linhas Manuscritas Isoladas (PT-BR)

**Diretório do experimento**: `experiments/EXP-001/`

**Created**: 2026-09-30

**Status**: `APPROVED` — spec, plano e tarefas aprovados pelo usuário em 2026-09-30; decisões registradas em §6. Execução concluída em 2026-10-02; resultados em [RESULTS.md](./RESULTS.md).

**Input**: `experiments/EXP-001-context.md` + instrução do usuário de 2026-09-30 (ciclo Spec Kit adaptado a
experimentos: Specify → Plan → Tasks, apresentados antes de qualquer execução).

**Pré-requisito**: EXP-000 `ACCEPTED` em 2026-09-30 (`experiments/EXP-000/RESULTS.md`).

> **Nota de adaptação do Spec Kit.** `specs/` é reservado a features de produto (`specs/README.md` §1) e
> experimentos não são features (Constituição, Princípio 7). Por isso os artefatos do ciclo ficam em
> `experiments/EXP-001/` (`spec.md`, `plan.md`, `tasks.md`), no formato dos templates do `specify 1.0.1`,
> com "user stories" lidas como **perguntas experimentais**. Nada daqui entra em `src/leitorum_di/` sem ADR.

---

## 1. Pergunta e Hipóteses

**Pergunta central:** existe hoje algum reconhecedor de linha manuscrita, com código e pesos de licença
verificada, que rode na máquina-alvo em CPU (i5-8265U, 7,9 GB RAM) dentro de 2 GB de memória e que leia
português manuscrito com qualidade útil?

- **H1 (qualidade):** ao menos um candidato atinge CER ≤ 12 % e WER ≤ 25 % em linhas manuscritas PT-BR limpas, *sem adaptação*.
- **H2 (custo):** ao menos um candidato fica em ≤ 150 ms/linha (mediana, CPU) e ≤ 2,0 GB de pico de memória.
- **H0 esperada (a refutar):** modelos prontos treinados em inglês/francês (IAM, RIMES) erram sistematicamente
  diacríticos do português (`ã õ ç á é ê ô à`) e **não** atingem H1. Confirmar H0 também é um resultado válido:
  ele quantifica a lacuna e fundamenta um experimento posterior de adaptação.

Os limiares são os de `EXP-001-context.md` §4 e são **hipóteses iniciais**, não critérios de aprovação do experimento.

---

## 2. Cenários Experimentais *(equivalente a User Stories)*

### Cenário 1 — Harness de benchmark validado com dados sintéticos (P1)

O benchmark roda de ponta a ponta sobre linhas **sintéticas** (texto fictício em PT-BR renderizado em imagem),
com um reconhecedor "eco" de referência, e produz o log no schema `leitorum-di-benchmark`.

**Por que P1**: sem harness auditável, nenhum número de modelo é confiável (Princípios 2 e 3).

**Teste independente**: `uv run pytest` verde + execução do harness com o reconhecedor de referência, sem
nenhum modelo de IA instalado.

**Aceite**:
1. **Dado** o manifesto de linhas sintéticas, **quando** o harness roda com o reconhecedor de referência, **então** CER = WER = 0 e o log registra tempo por linha, pico de memória, seeds e hashes.
2. **Dado** um reconhecedor que excede o teto de memória ou de tempo, **quando** o harness o executa, **então** o candidato é interrompido e registrado como `ABORTED` com o motivo, sem derrubar os demais.

### Cenário 2 — Comparação zero-shot de pelo menos dois candidatos (P2)

Cada candidato com `LICENSE STATUS: VERIFIED` é executado em subprocesso isolado sobre o conjunto de avaliação.

**Teste independente**: relatório com uma linha por candidato (CER, WER, ms/linha mediana e p95, pico de RSS, status).

**Aceite**:
1. **Dado** dois ou mais candidatos verificados, **quando** o benchmark conclui, **então** `RESULTS.md` traz a tabela comparativa e o manifesto de reprodutibilidade completo (Princípio 3).
2. **Dado** um candidato com `NEEDS VALIDATION`, **quando** o benchmark é lançado, **então** ele é recusado antes de qualquer download.

### Cenário 3 — Análise de erros em português (P3)

Matriz de confusão por caractere com foco em diacríticos, cedilha, dígitos e pares ambíguos (`l`/`1`, `O`/`0`).

**Aceite**: `RESULTS.md` lista as 20 confusões mais frequentes por candidato e a taxa de erro por classe
(vogais acentuadas, `ç`, dígitos, pontuação).

### Casos de borda

- Linha vazia ou só com pontuação (CER com N = 0).
- Imagem muito larga (> 1 500 px) ou muito baixa (< 32 px).
- Saída do modelo com caracteres fora do alfabeto PT-BR ou com normalização Unicode diferente (NFC × NFD).
- Candidato sem wheel para Python 3.14 no Windows.
- Falha de rede no download de pesos (única etapa com rede; ver FR-009).

---

## 3. Requisitos

### Funcionais

- **FR-001**: O benchmark DEVE receber linhas já recortadas (uma imagem = uma linha) e uma transcrição de referência por linha.
- **FR-002**: O benchmark DEVE calcular CER e WER com `leitorum_di.metrics` (WER com a normalização aprovada em 2026-09-30: remove pontuação de borda, preserva acentos e caixa). Textos comparados em Unicode NFC.
- **FR-003**: O benchmark DEVE medir, por candidato: tempo por linha (mediana, p95), tempo de carga do modelo, pico de memória do processo.
- **FR-004**: Cada candidato DEVE rodar em subprocesso próprio, em CPU, com teto de **2,0 GB** de memória e critérios de parada definidos em `plan.md` §5.
- **FR-005**: Só entram no benchmark candidatos com `LICENSE STATUS: VERIFIED` para **código e pesos**, registrados em `docs/models-and-licensing.md` com identificador, revisão e SHA-256 dos pesos.
- **FR-006**: O resultado bruto do modelo DEVE ser preservado sem correção por dicionário ou modelo de linguagem externo (Princípio 4); a confiança, quando o modelo a expõe, é registrada à parte.
- **FR-007**: O experimento DEVE gerar manifesto com hash Git, `uv.lock` do ambiente do experimento, versão/hash dos pesos, parâmetros, identificação do dataset e hardware (Princípio 3).
- **FR-008**: Dependências pesadas (Torch, ONNX Runtime, wrappers de OCR) NÃO DEVEM entrar no `pyproject.toml` principal; ficam em ambiente isolado do experimento.
- **FR-009**: Rede só é permitida para instalar pacotes e baixar pesos verificados de repositório oficial; a inferência DEVE rodar offline. Nenhuma imagem ou texto sai da máquina.
- **FR-010**: Nenhuma imagem real de caderno, texto do acervo ou conteúdo de `backend/data/` pode ser lido ou usado sem consentimento explícito do usuário para aquela amostra.
- **FR-011**: A caligrafia real é avaliada com um dataset público de licença verificada e download reproduzível (BRESSAY, CC-BY-4.0, Zenodo, checksum conferido). Nenhuma amostra pessoal do usuário é usada. Se o dataset público não puder ser usado, a rodada conclui só com a camada sintética, medindo custo e lacuna.
- **FR-012**: Nenhum binário é instalado no sistema fora de `document-intelligence/`; todo candidato precisa ser instalável por wheels em ambiente `uv` isolado.
- **FR-013**: Candidato executado sob exceção do usuário mantém `LICENSE STATUS: NEEDS VALIDATION` em todos os relatórios e não pode ser promovido a feature de produto.

### Entidades

- **Linha**: `id`, caminho da imagem, SHA-256, transcrição de referência (NFC), origem (`synthetic` | `real`), autor/caderno (para split), licença/consentimento.
- **Candidato**: identificador, versão/revisão, licença do código, licença dos pesos, SHA-256 dos pesos, status de licença.
- **Execução**: candidato × dataset → predições por linha, métricas, tempos, pico de memória, status (`OK` | `ABORTED` | `REFUSED`), manifesto.

---

## 4. Candidatos e Situação de Licença

Verificação feita em 2026-09-30 por leitura das páginas/metadados oficiais (API de licenças do GitHub e API de
modelos do Hugging Face). Nada foi baixado. "Declarada" = o que o repositório oficial publica; não é parecer jurídico.

| # | Candidato | Família | Licença do código | Licença dos pesos | Português? | Status |
| :- | :--- | :--- | :--- | :--- | :--- | :--- |
| A | Tesseract 5 + `por.traineddata` (`tessdata_best`) | LSTM, impresso | Apache-2.0 (verificada) | Apache-2.0 (verificada) | sim, treinado para impresso | `LICENSE STATUS: VERIFIED` |
| B | PyLaia + modelos Teklia (`pylaia-rimes`, `pylaia-iam`) | CNN-RNN-CTC, manuscrito | MIT (a reconfirmar no repositório do PyLaia) | MIT (declarada nos cards) | não — francês / inglês | `LICENSE STATUS: NEEDS VALIDATION` até reconfirmar o código |
| C | TrOCR `microsoft/trocr-small-handwritten` | Transformer, manuscrito | MIT (`microsoft/unilm`, verificada) | **nenhuma licença declarada no card** | não — inglês | `LICENSE STATUS: NEEDS VALIDATION` |
| D | EasyOCR (`pt`) | CRNN, impresso | Apache-2.0 (verificada) | não verificada separadamente | sim, impresso | `LICENSE STATUS: NEEDS VALIDATION` |
| E | `mazafard/trocr-finetuned_20250422_125947` | TrOCR ajustado (en/pt, base impressa) | — | MIT (declarada); procedência fraca (41 downloads) | sim, impresso | `LICENSE STATUS: NEEDS VALIDATION` |

### 4.1 Lista final (T002/T003, 2026-09-30)

Fonte de verdade: [`candidates.json`](./candidates.json) (revisões e SHA-256) e `docs/models-and-licensing.md`.

| Candidato | Decisão | Status de licença |
| :--- | :--- | :--- |
| `pylaia-rimes` (PyLaia 1.1.2 + pesos Teklia, francês) | **executar** | `LICENSE STATUS: VERIFIED` (código MIT, pesos MIT declarados) |
| `pylaia-iam` (idem, inglês) | executar se o tempo permitir | `LICENSE STATUS: VERIFIED` |
| `trocr-small-handwritten` | **executar sob exceção do usuário**, só experimental/local | `LICENSE STATUS: NEEDS VALIDATION` — não promovível a produto |
| Tesseract + `por` | excluído: exige binário no sistema (não autorizado) | licença verificada, mas fora da rodada |
| EasyOCR (`pt`) | excluído: pesos sem licença declarada e sem exceção; a documentação oficial informa que manuscrito não é suportado | `LICENSE STATUS: NEEDS VALIDATION` |
| `mazafard/trocr-finetuned…` | excluído: procedência fraca | `LICENSE STATUS: NEEDS VALIDATION` |

Consequência: **não há baseline de texto impresso nesta rodada**; a comparação é entre duas famílias de manuscrito
(CNN-RNN-CTC × Transformer), ambas sem treino em português.

**Dataset real:** BRESSAY (DOI 10.5281/zenodo.11637681, `bressay.zip`, 1,5 GB, MD5 conferido em 2026-09-30).
**Correção da Fase 3:** os metadados do Zenodo declaram CC-BY-4.0, mas o `README.md` dentro do arquivo restringe o
uso a "non-commercial research and teaching purposes only". Com termos conflitantes, o status passa a
`LICENSE STATUS: NEEDS VALIDATION` e, pela regra do usuário (§6.1), a rodada conclui só com a camada sintética,
salvo autorização expressa.
**Exceção do usuário (2026-10-01):** uso experimental e local autorizado, mantendo `LICENSE STATUS: NEEDS VALIDATION`
em todos os relatórios. Imagens e transcrições ficam fora do Git; os relatórios versionados trazem só agregados.

### 4.2 Achados da pesquisa inicial

1. **Não encontrei nenhum modelo leve de manuscrito em português com pesos de licença verificada.** Os modelos
   PT de manuscrito localizados (Transkribus) rodam em plataforma de terceiros e ficam **excluídos** pelo Princípio 1.
2. Hoje só o candidato **A** está `VERIFIED`, e ele é um baseline de texto impresso. O requisito de "pelo menos
   duas abordagens" depende de fechar a licença de B (provável) e/ou C.
3. Os conjuntos de treino de B e C (IAM, RIMES) têm termos próprios de uso em pesquisa; isso afeta a
   interpretação da licença dos pesos e será registrado, não resolvido, pelo agente.
4. Compatibilidade com Python 3.14 no Windows para Torch/ONNX Runtime **não ficou confirmada** na consulta de
   hoje; o plano prevê fixar outra versão de Python só no ambiente do experimento.

---

## 5. Critérios de Sucesso do Experimento

- **SC-001**: Tabela comparativa com ≥ 2 candidatos `VERIFIED` executados, ou registro explícito de por que só um pôde ser executado.
- **SC-002**: Para cada candidato executado: CER, WER, ms/linha (mediana e p95), pico de memória — com veredito contra H1 e H2.
- **SC-003**: Análise de erros por classe de caractere PT-BR (Cenário 3).
- **SC-004**: `docs/models-and-licensing.md` preenchido para todos os candidatos considerados, inclusive os recusados.
- **SC-005**: ADR em `docs/adr/` com a decisão (adotar, adaptar em experimento futuro, ou descartar).
- **SC-006**: Zero arquivos alterados fora de `document-intelligence/`; `uv run pytest` e `uv run ruff check .` verdes.

O experimento é bem-sucedido se responder à pergunta com evidência reproduzível — **mesmo que nenhum candidato atinja H1**.

---

## 6. Decisões do Usuário *(Clarify — respondido em 2026-09-30)*

1. **Dados:** sem amostras pessoais. Camada sintética expandida + dataset público em português com licença
   verificada e download reproduzível (BRESSAY ou similar). Sem dataset fechado a tempo → concluir com o sintético.
2. **Tesseract:** não autorizado; nada de binários no sistema fora de `document-intelligence/`. Só wheels em ambiente `uv` isolado; baseline impresso pode ser dispensado.
3. **TrOCR:** autorizado para uso estritamente experimental e comparativo local, mantendo `LICENSE STATUS: NEEDS VALIDATION` em todos os relatórios e sem promoção a produto.
4. **Git:** commit inicial autorizado e criado — `33c293f doc-intelligence — estrutura inicial e fundação (EXP-000)`.

### Perguntas originais (histórico)

1. **Dados reais de avaliação.** O projeto não tem dataset real (`docs/dataset-and-evaluation.md` §3) e linhas
   sintéticas renderizadas com fonte não medem HTR de verdade. Opções:
   - **(a) Recomendada:** você fornece um conjunto pequeno e congelado (~100–150 linhas) da sua própria letra,
     com texto **não sensível** escrito para esse fim, recortado e transcrito por você, dentro de
     `document-intelligence/dataset/` e fora do Git. Um único autor não permite *writer split*; isso fica declarado como limitação.
   - **(b)** Dataset público de manuscrito em português (ex.: BRESSAY). Acesso e licença: `LICENSE STATUS: NEEDS VALIDATION`.
   - **(c)** Só sintético nesta rodada: valida o harness e o custo (H2), mas **não** responde H1.
2. **Tesseract** exige instalar um binário no sistema, fora de `document-intelligence/`. Autoriza, ou o baseline impresso deve ser outro?
3. **TrOCR sem licença declarada nos pesos (C):** excluir, ou você aceita o risco para uso estritamente experimental local?
4. **Versionamento:** `document-intelligence/` ainda não está no Git, e o Princípio 3 exige hash de commit no manifesto. O commit inicial é decisão sua (convenção da raiz).

---

## 7. Fora de Escopo

- Treino, *fine-tuning* ou adaptação de modelos (candidato a experimento posterior, conforme o resultado).
- Detecção de layout, segmentação de linhas, recorte automático (EXP-002).
- Uso de GPU (MX110 2 GB): baseline é CPU-only, conforme `environment.md`.
- Qualquer código em `src/leitorum_di/` além de utilitários genéricos de medição já existentes; integração LDF/API.
- Leitura de cadernos reais do acervo ou do banco do Leitorum.

## 8. Premissas

- Máquina-alvo: a de `experiments/EXP-000/environment.md`.
- Métricas e normalização: as homologadas no EXP-000.
- Pesos e caches ficam em `document-intelligence/models/` (ignorado pelo Git), nunca no perfil global do usuário.
