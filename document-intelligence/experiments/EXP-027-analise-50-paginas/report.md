# EXP-027: Relatório — Análise das 50 páginas reais do caderno (Etapa 1)

* **Status:** `CONCLUÍDO COM RESSALVAS` — modo só texto, 2026-11-16 (executor: Claude Code; decisões de
  material pelo usuário)
* **Artefatos:** [spec.md](./spec.md), [splits/test-manifest.json](./splits/test-manifest.json) (v2),
  benchmark `evaluation/benchmarks/BENCHMARK-20261116-exp-027-motor.json`
* **Privacidade:** nenhum texto, foto ou recorte do caderno aparece aqui; só números e categorias.

---

## 1. Resposta

Nas 20 páginas de teste, o motor do produto **erra 56 % dos caracteres e 90 % das palavras**. O erro não
está nas fórmulas nem é maior na letra cursiva: está no **texto comum**, em todas as classes de escrita, e
uma parte grande dele é **texto que o motor nem chega a escrever** (28 % das palavras da referência não
aparecem na saída; em 7 das 20 páginas a saída tem só 30 a 67 % do tamanho esperado). Uma etapa de
correção de palavras depois da leitura teria teto de 18 % das palavras erradas e um dicionário sozinho
resolveria 4 %. O maior ganho possível está no **leitor e na cobertura da página em fotos reais**, e o
caminho já medido no projeto para isso é o ajuste fino com páginas do próprio usuário.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| **H1** fórmulas ≥ 25 % do erro | **Refutada** | 12 % dos caracteres de referência são fórmula; 12–16 % dos erros estão neles |
| **H2** cursiva ≥ 1,5× pior que forma | **Refutada** | CER cursiva 50 %, forma 55 %, mista 63 % |
| **H3** ≥ 30 % das palavras erradas a 1–2 letras | **Refutada** | 18 %; dicionário corrige 4 % sem contexto |
| **H4** perda antes da leitura domina | **Apoio parcial** | 28 % das palavras omitidas; sem caixas não dá para separar de leitura |
| **H5** VLM local ≥ 10 pontos melhor | **Não medida** | exige as fotos; o professor externo foi "praticamente perfeito" segundo o usuário |

## 2. Material e como foi medido

* **Páginas:** 51 estudos exportados do Leitorum em Markdown com a opção "Fichamento da Fonte", que traz o
  texto bruto do motor (feature 086, pipeline do ADR-008, leitor PP-OCRv6 small, sem correção lexical);
  969 linhas lidas, mediana de 525 caracteres por página. O texto "revisado" nas seções era o bruto
  reorganizado (96 % da diferença era ordem de linhas; 1,4 % das palavras mudavam): **não servia de referência**.
* **Classificação manual (usuário, 51 páginas):** escrita cursiva 28, mista 18, forma 5; fórmulas
  nenhuma 21, poucas 26, muitas 4; foto "boa" em 49 de 50 classificadas.
* **Teste congelado (v2):** 20 páginas sorteadas (semente `exp-027`) estratificadas por escrita × fórmulas,
  com duas trocas registradas antes de qualquer medição (p20→p16, p44→p43: fotos não existiam mais).
  Estratos no teste: cursiva/nenhuma 6, cursiva/poucas 3, mista/poucas 6, forma/poucas 2, mista/nenhuma 2,
  mista/muitas 1. 31 páginas de desenvolvimento, sem referência.
* **Referência:** transcrição das 20 fotos por um modelo multimodal externo (Gemini), feita pelo usuário
  fora do projeto, por decisão dele, e **declarada por ele "praticamente perfeita"**; sem 2ª passada linha a
  linha. Registrada como `draft_source: teacher:gemini`. Fórmulas em LaTeX entre `$…$`.
* **Limitação decisiva:** a transcrição chegou sem as quebras de linha (6 dos 20 blocos têm mais de uma
  linha). Por isso toda medida é **em nível de página**: CER e WER com espaços colapsados, acentos e caixa
  preservados; a quebra do erro por origem (detecção × ordem × leitura), os exemplos com recorte e o
  baseline VLM local **não foram medidos** por falta das fotos no projeto.
* **Fórmulas, duas leituras:** (a) LaTeX da referência tal qual; (b) "simplificada": `\frac{a}{b}` → `a/b`,
  `\cdot` → `.`, chaves, `^` e `_` removidos, porque um leitor de texto nunca escreveria LaTeX e o CER cru
  creditaria a marcação como erro. A (b) é aproximada e declarada como tal.

## 3. Resultados (20 páginas de teste, 15 594 caracteres de referência)

| Medida | Referência em LaTeX | Fórmulas simplificadas |
| :--- | ---: | ---: |
| CER (micro, todos os caracteres) | **56,3 %** | 55,5 % |
| CER por página: mediana / p25 / p75 / mín / máx | 52,8 % / 45,3 % / 76,3 % / 32,5 % / 83,4 % | — |
| WER médio por página | **90,5 %** | 90,3 % |
| CER só no texto comum | 53,5 % | 53,7 % |
| CER só nas fórmulas | 77,1 % | 72,9 % |
| Parte dos erros que está em fórmulas | 16,3 % | 12,0 % |
| Caracteres de fórmula na referência | 1 857 de 15 594 (12 %) | — |

**Por classe (CER micro, LaTeX):** escrita cursiva 49,7 % (9 páginas), forma 55,1 % (2), mista 62,7 % (9);
fórmulas nenhuma 48,2 % (8), poucas 63,9 % (11), muitas 50,1 % (1); foto boa 56,2 % (19), média 62,2 % (1).
Com 2 páginas de forma e 1 de "muitas", esses dois grupos são indicativos; a comparação cursiva × mista
(9 × 9) é a que tem peso, e vai no sentido contrário da hipótese.

**Palavras (fórmulas simplificadas; 2 511 palavras de referência):**

| | Quantidade | Parte das erradas |
| :--- | ---: | ---: |
| Certas | 279 (11 %) | — |
| Trocadas por outra a 1 letra | 211 | 9,4 % |
| Trocadas a 2 letras | 194 | 8,6 % |
| Trocadas a 3 letras ou mais | 1 124 | 50,0 % |
| **Omitidas** (não aparecem na saída) | **703** | **31,3 %** |
| Inseridas (saída sem par na referência) | 16 | 0,7 % |

Das 405 palavras a 1–2 letras da certa: 193 saídas do motor **são palavras válidas** do português (um
dicionário não as veria), 85 seriam corrigidas sem ambiguidade pelo léxico de 50 mil palavras (73 a 1
letra, 12 a 2), 107 têm a certa entre os candidatos mas não como a mais provável (exigem contexto) e 20
têm a certa fora do léxico. Teto de uma correção perfeita de 1–2 letras: WER 90 % → ~74 %. Ganho de um
dicionário sozinho: ~3,8 % das palavras erradas.

**Cobertura da página** (caracteres na saída do motor ÷ caracteres na referência): mediana 0,84; 7 páginas
entre 0,30 e 0,67 (p10, p11, p14, p15, p21, p37, p45); nenhuma acima de 1,06. O motor produz menos texto
do que existe, e não lixo a mais.

## 4. O que isso diz, em linguagem simples

* **Onde o motor está hoje.** Nas redações digitalizadas do BRESSAY ele errava 1 em 4 caracteres; nas suas
  fotos de caderno erra mais de 1 em 2, e em 5 páginas erra 3 em 4. É um salto de dificuldade real:
  letra de caderno brasileira, fotografada, com fórmulas, listas e notas de margem. O leitor nunca viu
  nada parecido no treino.
* **Fórmulas não são o problema principal.** Elas são 12 % do texto e respondem por 12 a 16 % do erro,
  quase proporcional. São lidas pior (73–77 % contra 54 %), mas mesmo acertando todas o CER cairia de
  56 % para cerca de 47 %. Converter para LaTeX é uma necessidade de **produto** (como o usuário escreve
  matemática), não a maior fonte de erro.
* **Cursiva não é pior que letra de forma** nos dados. A classe "mista" é a pior, o que sugere que o
  problema é a **variação dentro da página** (tamanhos, inclinações, listas, setas) mais do que o traço.
* **Corrigir palavras depois não resolve.** Metade das palavras erradas estão longe demais da certa e
  quase um terço nem aparece. Com 11 % de palavras certas, não há contexto para uma "IA secundária" se
  apoiar. Isso confirma o EXP-024 (pós-correção tira 6–7 % do erro a 25 % de CER) num regime bem pior.
* **Parte grande do texto some antes de ser lida.** Palavras omitidas (28 % da referência) e páginas com
  metade do tamanho esperado apontam para a detecção de linhas e para a escala (linhas pequenas,
  margens, listas) tanto quanto para o reconhecimento. Separar os dois exige as caixas das linhas, que só
  saem com as fotos.
* **O que um modelo grande faz.** O professor externo transcreveu as mesmas fotos de forma que o usuário
  considerou praticamente perfeita. A meta de longo prazo (qualidade de grande modelo, local) é portanto
  um problema resolvido em algum lugar; a pergunta da Etapa 2 é **quanto disso um modelo local e,
  depois, um modelo próprio** consegue, e a que custo.

## 5. Onde está o maior ganho possível

1. **Leitor adaptado às páginas do usuário** (fine-tuning; pesos passam a ser nossos). É o único caminho
   já medido no projeto: no EXP-018, 50 páginas transcritas deram 88 % do ganho (32 % → 15,8 % de CER de
   validação). O ponto de partida aqui é 56 %, mais difícil, e a chegada não será a mesma; mas é a
   alavanca com evidência. Exige: as fotos e as transcrições das 31 páginas de desenvolvimento (as 20 de
   teste ficam de fora), em linhas fiéis.
2. **Cobertura: detecção de linhas e escala em fotos de caderno.** Hipótese forte, não confirmada; medir
   custa pouco assim que as fotos entrarem (caixas do motor + referência).
3. **Baseline VLM local (Qwen3-VL 4B quantizado, já guardado com hash e licença)**: define se um modelo
   local de pesos abertos chega perto do professor externo. Se chegar, vira o professor local e o
   primeiro degrau da trajetória de modelos próprios; se não, o degrau é o item 1.
4. **Fórmulas → LaTeX** e **correção pós-leitura**: depois, como requisitos de produto e polimento, não
   como fonte de ganho.

## 6. Limitações

* Referência de um modelo externo, declarada correta pelo usuário, sem conferência linha a linha; erros
  do professor viram "erro do motor". Pela qualidade declarada, o efeito sobre os totais deve ser pequeno.
* Nível de página: ordem de leitura e correspondência de linhas não medidas; a quebra por origem do
  método da spec (§5) fica pendente.
* 20 páginas, um autor, um caderno; estratos pequenos (forma 2, muitas fórmulas 1).
* Classificação "foto boa" é do usuário; a foto crua não foi vista nem medida no projeto.
* A variante "fórmulas simplificadas" é uma aproximação textual, não uma equivalência matemática.

## 7. Reprodução

```powershell
# document-intelligence/experiments/EXP-027-analise-50-paginas/harness, com os dados em dataset/raw/exp-027
python -s parse_export.py --expect 50
python -s import_teacher.py --system gemini
python -s score.py --system motor --page-level --benchmark
```

Referências em `dataset/raw/exp-027/referencia/pNN.txt` (20 páginas de teste), classificação em
`dataset/raw/exp-027/classificacao/`, tudo fora do Git.

## 8. Para fechar a Etapa 1 sem ressalvas

Colocar as **20 fotos de teste** (as mesmas enviadas ao professor externo) em
`dataset/raw/exp-027/fotos/`, com o nome `pNN.jpg`. Os scripts as processam sem que nenhuma imagem passe
pelo chat. Com elas: motor com caixas → quebra do erro por origem; exemplos de falha em arquivo local;
baseline Qwen3-VL local (T005). As 31 páginas de desenvolvimento, com fotos e transcrições, são o que o
item 1 da §5 pede.
