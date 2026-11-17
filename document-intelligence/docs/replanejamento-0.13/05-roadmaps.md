# Etapa 4 — Roadmaps a partir do 0.13: qualidade da digitalização e trajetória de modelos próprios

**Data:** 2026-11-16 · **Status:** `RASCUNHO` para revisão do usuário · **Base:** [plano aprovado](./04-plano.md)
(Etapa 3), [EXP-027](../../experiments/EXP-027-analise-50-paginas/report.md), [pesquisa](./03-resultado-pesquisa.md).

**Regras herdadas.** Cada item abaixo é uma spec própria do Spec Kit (experimento ou feature), um commit por
item quando aprovado; experimento ≠ feature, nada vira código de produto sem experimento medido e ADR; o
contrato LDF 2.0 só muda por versão MINOR com change request e ADR; o motor do produto fica local, em CPU, sem
custo por uso; modelos externos só com cópia exata guardada (revisão, hash, licença). Numeração: EXP-026 está
reservado (adaptador de referência); os experimentos aqui começam em EXP-028. **Itens fora de
`document-intelligence/` (motor, backend, frontend do Leitorum, arquivos da raiz) são change requests (CR) para o
usuário aprovar**, inclusive a criação de `ROADMAP-0.13.md` na raiz, que hoje é onde os roadmaps do Leitorum
vivem.

**Por que quatro versões mais um roadmap paralelo.** A divisão sai dos marcos do plano: cada versão fecha um
marco medido no teste congelado (M1 cobertura, M2 leitura v1, M3 leitura v2 + polimento, M4 fórmulas) e a
trajetória de modelos próprios corre ao lado, com portões próprios (M5), porque depende do banco de páginas
crescer e não deve atrasar as versões.

---

## Visão geral

| Versão | Tema | Métrica-alvo no teste congelado v2 | Critério de saída |
| :--- | :--- | :--- | :--- |
| **0.13** | Ver a página inteira, e ter dados | cobertura: 0 páginas com saída < 85 % do tamanho (hoje 7 de 20); palavras omitidas ≤ 10 % (hoje 28 %) | M1 atingido **e** banco com ≥ 50 páginas de desenvolvimento transcritas linha a linha, com caixas |
| **0.14** | Ler certo: leitor ajustado v1 (pesos nossos) | CER ≤ 30 %, WER ≤ 65 % (hoje 56 % / 90 %) | M2 atingido com o leitor no motor do produto, ≤ 10 s e ≤ 1,5 GB por página |
| **0.15** | Ler certo e polir: leitor v2, léxico, ordem | CER ≤ 15–20 %, WER ≤ 45 % | M3 atingido; decodificação com léxico só se melhorar o teste sem piorar fórmulas e siglas |
| **0.16** | Fórmulas e layout de caderno | CER em fórmulas ≤ 40 % (hoje 73–77 %) sem piorar o texto; ordem de leitura medida | M4 atingido; LDF 2.1 com trechos de fórmula e zonas |
| **MP** (paralelo) | Modelos próprios | leitor próprio ≥ leitor ajustado no teste v2 e no teste de deriva | M5: substituição quando igualar ou superar |

Depois do 0.16, o que sobrar (segundo autor, outros cadernos, diagramas) entra num roadmap novo com a mesma
regra: tema por marco medido.

---

## 0.13 — Ver a página inteira, e ter dados

**Por quê primeiro.** 28 % das palavras não chegam ao leitor; sem cobertura, qualquer ganho de leitura fica
limitado. E nenhum treino acontece sem páginas transcritas com caixas de linha: o 0.13 constrói o banco.

### Épico 0.13-A — Medir o que falta medir (fecha a Etapa 1 sem ressalvas)

| Item | O quê | Depende de | GPU? | Dados que ainda não existem |
| :--- | :--- | :--- | :---: | :--- |
| **EXP-028** | Quebra do erro por origem nas 20 páginas de teste com as fotos: motor com caixas, recall de linhas contra a referência, ordem, leitura; exemplos de falha em arquivo local; separa quanto dos 28 % é detecção, fusão, escala ou leitura | as 20 fotos de teste em `dataset/raw/exp-027/fotos/` | não | as fotos (o usuário tem) |
| **EXP-029** | Baseline VLM local no teste: Qwen3-VL-4B (guardado), GLM-OCR 0,9 B e Gemma 4 E2B se couberem na RAM; CER, WER, s/página, RAM de pico, com prompt fixo; registra o teto local e escolhe o **professor** | EXP-028 (fotos); cópia exata + licença de cada modelo no registry | não (CPU, em segundo plano, com espera de RAM) | — |
| **EXP-030** | Preparação leve e escala nas páginas de pior cobertura: OpenCV (perspectiva, iluminação) e variação da regra de escala; ganho isolado de cobertura e CER; UVDoc só se o ganho do OpenCV for pequeno | EXP-028 | não | — |

**Saída do épico:** ADR com a origem do erro (quanto é detecção, quanto é leitura) e a escolha do professor local.

### Épico 0.13-B — Banco de páginas (produto + ferramenta)

| Item | O quê | Depende de | GPU? | Dados que ainda não existem |
| :--- | :--- | :--- | :---: | :--- |
| **CR-F13.1** (Leitorum) | Pacote de treino na digitalização: guardar, com consentimento explícito e opção de desligar, a foto recortada, as caixas das linhas lidas e o texto corrigido pelo usuário (`human_corrections` do LDF 2.0), ligados por hash à página | spec de produto; feature 086/090 existentes | não | — |
| **CR-F13.2** (Leitorum) | Exportador do pacote de treino: por página, foto + caixas + linhas corrigidas + origem do rascunho (motor ou professor) + hashes, para uma pasta fora do Git; recusa páginas do teste congelado por hash | CR-F13.1; `splits/test-manifest.json` | não | — |
| **F-DI-13.3** | Ferramenta de transcrição linha a linha do DI (hoje em `EXP-027/harness`) promovida a utilitário do subprojeto: recortes por caixa, rascunho do professor nas páginas de desenvolvimento, 2ª passada, marcação `$…$`; exporta no mesmo formato do CR-F13.2 | EXP-029 (professor) | não | — |
| **EXP-031** | Revisão das 20 referências de teste (2ª passada do usuário contra o caderno) e medição do quanto a referência mudou; recongela o teste como v3 se mudar | F-DI-13.3 | não | tempo do usuário (~20 páginas) |
| **Dados-13.4** | 50 páginas de desenvolvimento transcritas linha a linha com caixas (professor local + correção do usuário); 31 já têm texto bruto; manifesto com hashes e origem do rascunho | F-DI-13.3, EXP-029 | não | **as transcrições** (5–15 min por página pré-transcrita, estimativa da pesquisa) |

### Épico 0.13-C — Cobertura

| Item | O quê | Depende de | GPU? | Dados que ainda não existem |
| :--- | :--- | :--- | :---: | :--- |
| **EXP-032** | Detector de linhas ajustado: PP-OCRv6 DB small com GNHK (CC-BY-4.0, atribuição) + as 50 páginas de desenvolvimento com caixas; medir recall de linhas e cobertura no teste; comparar com ajuste de fusão/escala sem treino | EXP-028, Dados-13.4 | **opcional**: CPU 4–12 h (apertado) ou GPU emprestada 0,5–2 h, que implica enviar as suas páginas à nuvem (decisão sua) | caixas de linha das 50 páginas (vêm do Dados-13.4) |
| **CR-F13.5** (motor) | Trocar o detector no motor do produto quando o EXP-032 atingir M1: `config.json`, hash, licença, pesos nossos registrados | EXP-032, ADR | não | — |

**Critério de saída do 0.13:** M1 no teste congelado (0 páginas < 85 %; omitidas ≤ 10 %) **e** Dados-13.4 pronto.
Se M1 vier só da regra de escala e fusão (EXP-030), o detector ajustado fica para o 0.14 e o 0.13 fecha antes.

---

## 0.14 — Ler certo: leitor ajustado v1

| Item | O quê | Depende de | GPU? | Dados que ainda não existem |
| :--- | :--- | :--- | :---: | :--- |
| **EXP-033** | Ajuste fino do leitor PP-OCRv6 rec small com 30 e com 50 páginas de desenvolvimento, em CPU (mesmo procedimento do EXP-014/018), avaliado no teste v2/v3: primeiro número real de M2; curva com 30 → 50 | Dados-13.4 | não (CPU, horas, retomável) | — |
| **EXP-034** | Mesmo treino com PyLaia (MIT) e PP-OCRv6 rec medium: qual arquitetura pequena rende mais por página sua; custo por página no motor | EXP-033 | não | — |
| **EXP-035** | Sintético PT-BR como suplemento: linhas renderizadas com fontes cursivas livres, pauta, sombra e perspectiva, misturadas às reais; ganho medido (o EXP-021 mostrou que degradar digitalizações não ajuda; aqui o sintético é texto novo, não degradação) | EXP-033 | não | corpus de texto PT-BR livre + fontes OFL |
| **CR-F14.1** (motor) | Trocar o leitor no motor pelo ajustado (pesos nossos, Apache-2.0 de origem): `config.json`, hash, licença, limiar de confiança recalibrado | EXP-033/034, ADR | não | — |
| **CR-F14.2** (Leitorum) | Indicador de versão do leitor na tela de digitalização e no estudo (qual modelo leu), para o teste de deriva e para o usuário saber o que mudou | CR-F14.1 | não | — |

**Critério de saída do 0.14:** M2 (CER ≤ 30 %, WER ≤ 65 %) com o leitor no produto, ≤ 10 s e ≤ 1,5 GB por
página. Se o EXP-033 ficar acima de 30 % com 50 páginas, a versão não fecha com arquitetura nova: fecha com
mais páginas (Dados-13.4 estendido a 100) e cobertura revista.

---

## 0.15 — Ler certo e polir: leitor v2, léxico e ordem

| Item | O quê | Depende de | GPU? | Dados que ainda não existem |
| :--- | :--- | :--- | :---: | :--- |
| **Dados-15.1** | Banco com 100–150 páginas de desenvolvimento (produto + ferramenta), primeiro **teste de deriva** congelado (10 páginas novas) | CR-F13.1/13.2 em uso | não | ~50–100 páginas a mais, transcritas |
| **EXP-036** | Leitor v2: ajuste com 100–150 páginas (+ sintético se o EXP-035 valeu); curva 50 → 100 → 150; avaliação no teste v2/v3 e no teste de deriva | Dados-15.1 | não (CPU; GPU opcional para reduzir horas) | — |
| **EXP-037** | Decodificação com léxico dentro do CTC: KenLM (LGPL) de corpus PT-BR + vocabulário dos seus estudos, em beam search; ligado só se CER < 20 %; mede ganho líquido e dano em fórmulas, siglas e abreviações | EXP-036 | não | corpus PT-BR livre; vocabulário do usuário (dos próprios estudos, local) |
| **EXP-038** | Ordem de leitura e zonas em caderno: regras geométricas sobre as caixas (colunas, margem, listas), medidas com a referência linha a linha; classes de zona só se as regras não bastarem | EXP-028 | não | anotação de ordem nas 20 páginas de teste (sai da referência linha a linha) |
| **CR-LDF-2.1** | Change request + ADR: campos para trechos de fórmula e zonas (margem, lista, figura) no LDF, versão MINOR | EXP-038, decisão do 0.16 | não | — |
| **CR-F15.1** (motor) | Leitor v2 + decodificação no motor; CR-F15.2 (Leitorum): mostrar a ordem/zonas no editor de revisão | EXP-036/037/038 | não | — |

**Critério de saída do 0.15:** M3 (CER ≤ 15–20 %, WER ≤ 45 %) no teste v2/v3 **e** sem queda no teste de
deriva maior que 5 pontos.

---

## 0.16 — Fórmulas e layout de caderno

| Item | O quê | Depende de | GPU? | Dados que ainda não existem |
| :--- | :--- | :--- | :---: | :--- |
| **EXP-039** | Fórmulas: (1) VLM pontual (professor local) nos trechos marcados; (2) detector de fórmula (Pix2Text MFD, MIT, ou PP-DocLayout, Apache-2.0) + TexTeller (CC BY 4.0, ~1 GB) em ONNX; medir CER em fórmulas (máscara `$…$`), falsos positivos em texto e custo | 0.15; cópias exatas no registry | não para inferência; **sim** para ajustar o TexTeller (2–6 h, opcional) | 500+ recortes de fórmulas manuscritas suas, se for ajustar |
| **EXP-040** | Detecção de "isto é fórmula" nas suas páginas (inline e em bloco), com as 20 páginas de teste marcadas | EXP-039 | não | marcação `$…$` já existe na referência |
| **CR-F16.1** (motor + Leitorum) | Fórmulas em LaTeX no LDF 2.1 e no editor (prévia renderizada, edição do LaTeX) | EXP-039/040, CR-LDF-2.1 | não | — |

**Critério de saída do 0.16:** M4 (CER em fórmulas ≤ 40 %) sem piorar o CER do texto comum em mais de 1 ponto.

---

## Roadmap MP — Modelos próprios (paralelo, com portões próprios)

**Princípio.** Nenhum item do MP atrasa 0.13–0.16; ele consome o banco de páginas que as versões criam e só
substitui um modelo do produto quando iguala ou supera no teste congelado e no teste de deriva.

| Degrau | O quê | Portão de entrada | GPU? | Dados que ainda não existem |
| :--- | :--- | :--- | :---: | :--- |
| **MP-1 Coleta** | Banco próprio: 150+ páginas suas transcritas com caixas (vem do 0.13–0.15); corpus sintético PT-BR; testes congelados v2/v3 + deriva; manifestos com hashes e origem dos rascunhos | — | não | as páginas (produto + ferramenta) |
| **MP-2 Primeiro modelo próprio** (EXP-041) | Leitor CTC próprio **do zero** (arquitetura pequena, CRNN/PyLaia-like, código nosso), treinado com o banco + sintético; variante "ajustado" como controle | MP-1 com ≥ 150 páginas reais (a pesquisa aponta colapso abaixo de ~110, **a confirmar**) | **sim** (10–40 h estimadas) ou CPU em muitos dias, retomável | 100k–500k linhas sintéticas (gerar localmente) |
| **MP-3 Comparação** (EXP-042) | Próprio × ajustado × baseline VLM no teste v2/v3 e no teste de deriva: CER, WER, cobertura, s/página, RAM | MP-2 | não | — |
| **MP-4 Substituição** (CR) | Entra no motor o que ganhar (critério M5); o modelo externo sai do produto; registro no registry com os hashes dos pesos nossos | MP-3 | não | — |
| **MP-5 Detector próprio** (opcional) | Só se o layout de caderno exigir zonas que o DB ajustado não dá; mesmo portão M5 | 0.15/0.16 | sim | 500+ páginas com caixas |
| **MP-6 Outros autores** | Repetir MP-1 → MP-4 com páginas de outros leitores do produto, com consentimento; teste congelado por autor | produto com CR-F13.1 em uso | — | páginas de outros autores |

**Honestidade sobre o degrau MP-2.** Treinar um leitor do zero competitivo não cabe na máquina de
referência; cabe em horas de GPU emprestada, o que significa enviar as suas páginas (ou linhas recortadas e
anonimizadas) para a nuvem de terceiros. A alternativa 100 % em casa é um treino de dias em CPU, retomável.
O plano deixa a escolha por degrau, e o portão M5 garante que nada entra no produto por ideologia: entra o
que ler melhor no teste. Fórmulas nunca entram no MP (inviável do zero); o detector só se precisar.

---

## Dependências entre tudo (resumo)

```
fotos de teste ─► EXP-028 ─► EXP-030 ─► EXP-032 ─► CR-F13.5 (detector)            } 0.13
             └─► EXP-029 (professor) ─► F-DI-13.3 ─► Dados-13.4 ─► EXP-033/034/035 ─► CR-F14.1 } 0.14
CR-F13.1/13.2 (produto) ─► Dados-15.1 ─► EXP-036 ─► EXP-037 ─► CR-F15.1                       } 0.15
EXP-028 ─► EXP-038 ─► CR-LDF-2.1 ─► EXP-039/040 ─► CR-F16.1                                   } 0.16
Dados-15.1 ─► MP-1 ─► MP-2 ─► MP-3 ─► MP-4                                                     } MP
```

## O que exige GPU ou treino, e o que precisa de dados que não existem

* **Sem GPU, só CPU:** EXP-028 a 031, 033, 034, 035, 036 (horas), 037, 038, 039 (inferência), 040; todas as
  CR do motor e do Leitorum.
* **GPU opcional (horas emprestadas; envia páginas à nuvem):** EXP-032 (detector), EXP-039 (ajustar TexTeller),
  MP-2 (do zero), MP-5.
* **Dados que ainda não existem:** fotos das 20 páginas de teste no projeto (o usuário tem); transcrições
  linha a linha com caixas de 50 → 150 páginas (o produto e a ferramenta produzem); 2ª passada das referências de
  teste; recortes de fórmulas (só para o 0.16); corpus e fontes livres para o sintético (gerar).

## Primeiro passo concreto

EXP-028 e EXP-029 (épico 0.13-A): dependem só das 20 fotos de teste e do que já está guardado. Spec de cada
um apresentada para aprovação antes de qualquer código, no ritmo fatiado do projeto.
