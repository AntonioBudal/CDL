# Experiment Specification: EXP-008 — Detecção de Linhas em Manuscrito Real

**Diretório do experimento**: `experiments/EXP-008/`

**Created**: 2026-10-13

**Status**: `DRAFT` — **proposta condicionada** ao aceite do EXP-007 e do ADR-005 e à escolha deste passo pelo
usuário. Nenhum plano, tarefa, código ou download antes da aprovação.

**Input**: [EXP-007](../EXP-007/RESULTS.md), [failure-analysis](../EXP-007/failure-analysis.md) e ADR-005
(`PROPOSED`); ADR-002.

**Pré-requisito**: EXP-007 `ACCEPTED`.

---

## 1. Pergunta e Hipóteses

**Pergunta central:** existe um detector de linhas local, com licença verificada, que funcione em manuscrito real?
E quanto do problema medido no EXP-007 é do modelo, e quanto é de como a saída dele é usada?

O EXP-007 mostrou que o Doc-UFCN `norhand` acha o texto (só 3 % a 7 % das linhas perdidas não são vistas), mas
parte cada linha em fragmentos: F1 de 0,345 (fotos) e 0,372 (português), com teto de 0,54 e 0,71 se os fragmentos
fossem unidos de forma ideal.

- **H1 (fusão de fragmentos):** um pós-processamento que une fragmentos colineares, calibrado fora do teste, leva
  o Doc-UFCN `norhand` a pelo menos 80 % do teto medido (F1 ≥ 0,43 no GNHK e ≥ 0,57 no BRESSAY).
- **H2 (alternativa):** algum outro candidato atinge F1 ≥ 0,70 no BRESSAY e ≥ 0,60 no GNHK.
- **H3 (baseline clássico — hipótese, não premissa):** o método clássico do EXP-002 fica abaixo dos modelos em
  manuscrito real, como ficou no sintético degradado.
- **H4 (custo):** o melhor candidato fica em ≤ 3 s por página e ≤ 2 GiB.
- **H5 (medida):** o veredito não muda quando o acerto é medido por cobertura de tinta em vez de IoU com a linha
  inteira.

Os limiares são critérios de avaliação; o experimento conclui com veredito explícito para cada um, inclusive
"nenhum candidato serve".

---

## 2. Cenários Experimentais

### Cenário 1 — Benchmark real fixo (P1)

Reaproveitar a verdade de chão do EXP-007 e acrescentar um conjunto de calibração que não se mistura com o teste.

| Papel | Conjunto | Tamanho |
| :--- | :--- | ---: |
| Calibração | GNHK, divisão oficial de **treino** (já baixada) | 515 fotos; usar uma amostra fixa |
| Calibração | BRESSAY, divisão oficial de **validação** | 154 páginas |
| Teste | GNHK, divisão oficial de teste (a do EXP-007) | 172 fotos |
| Teste | BRESSAY, divisão oficial de teste (a do EXP-007) | 185 páginas utilizáveis |

**Critério de aceite:** nenhum parâmetro é escolhido olhando o teste; os números do EXP-007 são reproduzidos antes
de qualquer mudança.

### Cenário 2 — Pós-processamento do Doc-UFCN (P1)

Fusão de fragmentos colineares e demais ajustes de saída (limiar de componente, dilatação), sem trocar o modelo.

**Critério de aceite:** veredito de H1; quanto do teto foi alcançado; o que sobra de erro e de que tipo.

### Cenário 3 — Candidatos alternativos (P1)

Levantamento, com auditoria de licença, de detectores de linha que rodem em CPU por wheels no Windows. Já
conhecidos: Doc-UFCN `generic-historical-line` (pesos já no disco) e o baseline clássico do EXP-002. O
levantamento de outros é a primeira tarefa do plano; nenhum nome é assumido aqui. Continuam excluídos: Kraken (sem
wheels no Windows), docTR (pesos sem licença) e qualquer dependência AGPL.

**Critério de aceite:** tabela de candidatos com licença de código e de pesos verificada na fonte, e a razão de
cada exclusão. Download só depois da sua aprovação da lista.

### Cenário 4 — Medida complementar (P2)

Além do F1 por IoU com a linha inteira, uma medida por cobertura: que fração da área de cada linha verdadeira fica
dentro de detecções atribuídas a ela, e que fração das detecções cai fora de qualquer linha.

**Critério de aceite:** veredito de H5.

### Cenário 5 — Recomendação (P1)

**Critério de aceite:** relatório com veredito de H1 a H5 e ADR que diga qual componente de linhas passa a ser a
direção de trabalho, ou que nenhum serve e por quê.

### Casos de borda

- Linha muito inclinada ou curva; linhas que se tocam.
- Texto impresso misturado ao manuscrito.
- Página quase vazia; página muito densa.
- Candidato que exige mais memória que o limite ou que não instala.

---

## 3. Requisitos

- **FR-001:** Conjuntos de calibração e de teste disjuntos, fixados por lista com hash antes de qualquer medição.
- **FR-002:** Os números do EXP-007 são reproduzidos como primeira medição.
- **FR-003:** Mesmo harness, limites de memória e tempo e gate de licença dos experimentos anteriores; RAM livre
  ≥ 1 GiB para rodar modelos.
- **FR-004:** Todo candidato novo passa por auditoria de licença (código e pesos) registrada em
  `docs/models-and-licensing.md` antes do download; pesos com SHA-256 conferido.
- **FR-005:** Nenhuma imagem, recorte ou transcrição dos datasets vai para o Git, para relatórios ou para o chat.
  O texto das transcrições não é usado.
- **FR-006:** Sem retificação por contorno (suspensa pelo ADR-005).
- **FR-007:** Saídas em LDF 2.0.
- **FR-008:** Diretórios dos EXP-001 a EXP-003 e do EXP-007 só lidos; o que for reaproveitado é copiado; ambientes
  existentes com `--frozen`.
- **FR-009:** Relatórios e ADR com `LICENSE STATUS: NEEDS VALIDATION` na parte que depende do BRESSAY; a conclusão
  principal tem de se sustentar só com o GNHK.
- **FR-010:** Disco medido antes de cada download; teto de 20 GB.

## 4. Critérios de Sucesso

- **SC-001:** Benchmark fixo com calibração e teste separados, e os números do EXP-007 reproduzidos.
- **SC-002:** Ao menos três candidatos medidos (o Doc-UFCN com pós-processamento, o clássico e um alternativo), ou
  registro de que não há alternativo que cumpra as restrições.
- **SC-003:** Veredito explícito de H1 a H5.
- **SC-004:** 100 % das saídas válidas em LDF 2.0.
- **SC-005:** Nenhum conteúdo de dataset no Git; nada fora de `document-intelligence/`; disco dentro do teto.
- **SC-006:** ADR sobre o componente de linhas.

## 5. Fora do escopo

- Treinar ou ajustar pesos de modelos (se nenhum candidato servir, isso vira a recomendação, não a execução).
- Blocos, ordem de leitura, reconhecimento de texto, semântica e diagramas.
- Fotos do acervo do usuário; imprimir e fotografar páginas.
- Integração com o site.

## 6. Limitações já conhecidas

- O GNHK é em inglês e não é caderno; o BRESSAY não é foto e tem licença em validação.
- A verdade de chão de linha do GNHK é derivada das palavras; a medida por cobertura (Cenário 4) reduz, mas não
  elimina, esse efeito.
- Calibrar no treino do GNHK e testar no teste do GNHK mede generalização dentro do mesmo dataset, não para
  cadernos.

## 7. Perguntas para o usuário

1. **Este é o próximo passo?** A alternativa é atacar primeiro os blocos, ou voltar à opção de imprimir e
   fotografar páginas próprias para ter o caso de uso real.
2. **Fine-tuning:** fica fora, como proposto, ou você quer que entre como cenário se nenhum candidato pronto servir?
3. **Meta de H2** (F1 ≥ 0,70 no BRESSAY e ≥ 0,60 no GNHK): está adequada como "serve para seguir adiante"?
