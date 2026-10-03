# ADR-001: Não adotar reconhecedores de manuscrito prontos sem treino em português

* **Status:** ACCEPTED (aceito pelo usuário em 2026-10-02)
* **Data:** 2026-10-02
* **Decisores:** Usuário (decisão); Claude Code (proposta)
* **Experimento de Suporte:** [EXP-001](../../experiments/EXP-001/RESULTS.md)
* **Status de Licença:** `LICENSE STATUS: NEEDS VALIDATION` para parte da evidência (pesos do TrOCR e dataset BRESSAY, usados por exceção experimental local); `LICENSE STATUS: VERIFIED` para PyLaia e pesos Teklia

---

## 1. Contexto e Declaração do Problema

O Leitorum precisa transformar linhas manuscritas de cadernos de estudo em português em texto. O EXP-001 mediu se
algum reconhecedor de linha já publicado, leve o bastante para rodar em CPU na máquina-alvo (i5-8265U, 7,9 GB de RAM),
poderia ser usado como está.

Não foi encontrado nenhum modelo leve de manuscrito treinado em português com pesos de licença utilizável. Os
candidatos avaliados foram treinados em francês (PyLaia/RIMES) ou inglês (PyLaia/IAM, TrOCR small).

---

## 2. Drivers de Decisão (Critérios de Avaliação)

* **Driver 1:** Local-first e custo zero.
* **Driver 2:** Acurácia empírica em português manuscrito (meta: CER ≤ 12 %, WER ≤ 25 %).
* **Driver 3:** Custo em CPU (meta: ≤ 150 ms/linha, ≤ 2 GB) e reprodutibilidade em Windows/`uv`.
* **Driver 4:** Licença permissiva de código **e** pesos.
* **Driver 5:** Preservação da fronteira com o produto principal.

---

## 3. Opções Consideradas

### Opção A: Adotar o TrOCR small como reconhecedor provisório
* **Descrição:** usar o candidato de menor erro medido.
* **Pontos Positivos (+):**
  * Menor CER entre os avaliados (17,0 % sintético; 69,4 % BRESSAY).
  * Cabe no orçamento de memória (585 MiB).
* **Pontos Negativos (-):**
  * 69 % de CER em manuscrito real: inutilizável.
  * 100 % de erro em vogais acentuadas e cedilha.
  * 705–798 ms/linha, cerca de 5× a meta.
  * Pesos sem licença declarada: barrado pelo Driver 4.

### Opção B: Adotar o PyLaia com pesos Teklia (RIMES ou IAM)
* **Descrição:** usar o candidato com licença verificada e menor latência.
* **Pontos Positivos (+):**
  * Código e pesos MIT declarados.
  * 179–186 ms/linha em linhas limpas; 474–503 MiB.
* **Pontos Negativos (-):**
  * 79–95 % de CER em manuscrito real; quase não emite texto.
  * Vocabulário de saída sem `á í ó ú ã õ` (RIMES) ou sem nenhum acento (IAM).
  * Depende de Python 3.10 e `torch` 1.13, sem correções recentes.

### Opção C: Não adotar nenhum; tratar a adaptação ao português como experimento próprio
* **Descrição:** nenhum reconhecedor entra em `src/leitorum_di/`. O harness de benchmark é mantido como
  infraestrutura de avaliação. A viabilidade de treinar ou ajustar um modelo com vocabulário PT-BR passa a ser a
  pergunta de um experimento futuro, condicionado a um dataset de treino com licença fechada.
* **Pontos Positivos (+):**
  * Coerente com a evidência: a lacuna é de ordem de grandeza, não de ajuste fino.
  * Não introduz dependências pesadas nem pesos de licença incerta no produto.
  * Preserva o harness, os manifestos e a análise de erros para comparar candidatos futuros.
* **Pontos Negativos (-):**
  * O Leitorum segue sem HTR.
  * O caminho de adaptação exige dados de treino que o projeto ainda não tem.

---

## 4. Decisão Escolhida

Aprovamos a **Opção C**. As Opções A e B falham no Driver 2 por larga margem (CER de 69–95 % contra a meta de
12 %), a Opção A falha também nos Drivers 3 e 4, e nenhuma das duas tem o alfabeto do português na saída — uma
limitação que não se corrige sem treino.

Diretrizes decorrentes:

1. Nenhum dos três modelos avaliados é promovido a produto. O TrOCR, em particular, não pode ser promovido enquanto
   os pesos estiverem em `LICENSE STATUS: NEEDS VALIDATION`.
2. Qualquer candidato futuro a HTR deve ter vocabulário de saída cobrindo `á é í ó ú â ê ô ã õ à ç` (e maiúsculas).
3. Todo candidato futuro é medido com o harness do EXP-001, nas mesmas camadas de dados e limites.
4. A família CNN-RNN-CTC é a referência de custo (cabe na memória e fica perto da meta de latência); arquiteturas
   Transformer só se justificam se a medição mostrar latência compatível em CPU.

**Fora do alcance deste ADR:** escolher o modelo ou o dataset de um experimento de adaptação. Isso exige
especificação própria no ciclo Spec Kit.

---

## 5. Evidência Empírica do Experimento

* **Experimento:** [EXP-001](../../experiments/EXP-001/RESULTS.md) e [análise de erros](../../experiments/EXP-001/error-analysis.md)
* **Métrica Aferida (BRESSAY, 398 linhas, 199 autores):**
  * `pylaia-rimes`: CER 94,7 %, WER 99,7 %, 407 ms/linha
  * `pylaia-iam`: CER 79,3 %, WER 99,4 %, 402–408 ms/linha
  * `trocr-small-handwritten`: CER 69,4 %, WER 102,9 %, 705–717 ms/linha
* **Métrica Aferida (200 linhas sintéticas limpas):** CER de 22,3 %, 24,6 % e 17,0 %; 83–100 % de erro em vogais
  acentuadas e cedilha.
* **Memória:** pico máximo de 585 MiB (teto de 2 GB).
* **Limitações Observadas:** o BRESSAY tem baixa resolução (altura mediana de 23 px) e não é foto de caderno;
  amostra única; modelos sem adaptação nem modelo de linguagem; sem baseline de texto impresso.

---

## 6. Consequências

### Consequências Positivas
* O produto não herda um reconhecedor que falha em português nem pesos de licença incerta.
* Fica disponível uma infraestrutura de avaliação reproduzível (harness, manifestos, análise de erros).
* O requisito de alfabeto passa a ser um filtro explícito para candidatos futuros.

### Consequências Negativas / Trade-offs
* A funcionalidade de HTR do Leitorum continua sem solução.
* O próximo passo (adaptação) depende de dados de treino em português com licença fechada; hoje o único dataset
  conhecido, o BRESSAY, tem termos conflitantes.
* EXP-002 em diante (layout, ordem de leitura) podem prosseguir de forma independente, mas o pipeline integrado
  (EXP-006) fica bloqueado até haver um reconhecedor viável.

### Conformidade com a Constituição
* [x] Princípio 1: Local-first garantido — nenhuma opção considerada usa serviço externo.
* [x] Princípio 2: Evidência antes de decisão — decisão apoiada nas medições do EXP-001.
* [x] Princípio 3: Reprodutibilidade — manifesto em `RESULTS.md` §6.
* [x] Princípio 6: Medição antes de otimização nativa — nenhuma otimização proposta.
* [x] Princípio 8: LDF como fronteira contratual preservado — nada muda no contrato.
