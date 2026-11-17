# Etapa 4 — Roadmaps v2: 0.13 a 0.16 e trajetória de modelos próprios

**Data:** 2026-11-16 (v1 entregue; **v2** incorpora a [revisão crítica externa](./07-plano-revisado.md) conforme o
[plano v2](./04-plano.md) §0) · **Status:** `APROVADO` pelo usuário em 2026-11-16 (v2).

**Regras herdadas.** Cada item é uma spec própria do Spec Kit, um commit por item quando aprovado; experimento
≠ feature; nada vira produto sem medição no `frozen-test-v3` e ADR; LDF 2.0 só muda por versão MINOR com CR e
ADR; motor local, em CPU, sem custo por uso; modelo externo só com cópia exata guardada. Numeração: EXP-026
reservado; aqui a partir de EXP-028. Itens fora de `document-intelligence/` são **change requests (CR)** para o
usuário, inclusive `ROADMAP-0.13.md` na raiz. **Toda calibração, limiar, época e escolha de modelo se decide no
`dev-val`; o `frozen-test-v3` é lido uma vez, no fechamento de cada versão.**

**Convenção dos critérios.** Alvos numéricos são hipóteses a confirmar (**[revisão]** quando vieram da revisão
externa). Cada item tem critério de aceite e de abandono; cada versão tem plano B.

---

## Visão geral

| Versão | Tema | Métrica-alvo principal (`frozen-test-v3`) | Critério de saída |
| :--- | :--- | :--- | :--- |
| **0.13** | Régua limpa (épico 0, bloqueante) + enxergar a página inteira + Degrau 1 de dados | recall de linhas IoU ≥ 0,5 ≥ 92 % [revisão]; caixas falsas ≤ 5 %; palavras omitidas ≤ 10 %; 0 páginas < 85 % | M1 no teste v3, calibrado só no `dev-val`; 21 `dev-train` + 10 `dev-val` prontos com caixas |
| **0.14** | Ler certo v1: primeiro leitor nosso em CPU | CER ≤ 30 %, WER ≤ 65 %; CER com caixas perfeitas ≤ 22 % [revisão] | M2 com o leitor no motor, ≤ 10 s e ≤ 1,5 GB; banco em 50 `dev-train` |
| **0.14.5** | Consolidação I: coleta vinculada pelo produto, treino em 1 comando, dívida técnica | zero regressão de CER e custo; pacote exportado sem vazamento (teste automatizado) | pipeline de coleta → treino → ONNX → relatório sem intervenção manual |
| **0.15** | Ler certo v2 + léxico seguro + ordem de leitura | CER ≤ 15–20 %, WER ≤ 45 %; dano léxico ≤ 1 %; teste × deriva ≤ 5 p.p. | M3 no teste v3 e estável no `drift-test-1` (100–150 `dev-train`) |
| **0.16** | Fórmulas 2D e zonas de caderno; LDF 2.1 | CER em fórmulas ≤ 35–40 %; LaTeX válido ≥ 85 %; texto comum piora ≤ 1 p.p. | M4; LDF 2.1 por CR e ADR |
| **MP** (paralelo) | Modelos próprios do zero: leitor e decodificador | CER(a) ≤ CER(b) + 0,5 p.p. no teste **e** ≤ CER(b) na deriva | M5: substituição dos pesos herdados |

Por que esta divisão: cada versão fecha um marco medido; a 0.14.5 existe porque, sem coleta vinculada e treino
reprodutível, o 0.15 exigiria esforço manual insustentável; o MP corre ao lado porque depende do banco crescer.

---

## 0.13 — Régua limpa, página inteira e Degrau 1 de dados

### Épico 0.13-0 — Régua limpa (bloqueante: nada roda antes)

| Item | O quê e hipótese | Aceite | Abandono | Depende de | GPU | Dados novos |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **F-DI-13.01** | Ferramenta de anotação (evolução do harness do EXP-027): caixas de linha ajustáveis/criáveis sobre a foto, texto por `line_id`, marcação `$…$`, 2ª passada, exportação JSON com hash | 1 página completa exportada em ≤ 10 min [revisão], schema validado | — | 20 fotos de teste + 31 de dev em `dataset/raw/exp-027/fotos/` | não | as fotos (o usuário tem) |
| **EXP-028A** | Caixas reais + 2ª passada humana nas 20 páginas de teste e nas 10 `dev-val` (sorteio único, estratificado); mede o piso de ruído humano (1ª × 2ª passada). *Hipótese:* a referência v2 tinha ≥ 2 % de divergência e perda de quebras que distorciam o CER | `splits/test-manifest-v3.json` (20) e `splits/dev-val-manifest.json` (10) com 100 % das linhas com caixa e texto conferido duas vezes | — | F-DI-13.01 | não | ~3–4 h do autor [revisão] |
| **F-DI-13.02** | Harness gatekeeper: os 8 indicadores do plano §3.2, trava por hash entre treino e teste/val/deriva, relatório reproduzível | relatório das 20 + 10 páginas em < 3 min com semente fixa; teste automatizado do bloqueio de hashes | — | EXP-028A | não | — |
| **EXP-028B** | Decomposição exata do erro nas 20 (v3) e 10 (`dev-val`): motor com caixas vs caixas perfeitas. *Hipótese:* ≥ 10 p.p. do CER de página vêm de caixas perdidas/cortadas e ordem, não do leitor | tabela: % detecção, % corte de caixa, % ordem, % leitor puro; exemplos de falha em arquivo local | — | F-DI-13.02 | não | — |
| **EXP-029** | Professores locais no `dev-val`: Qwen3-VL-4B (guardado), GLM-OCR 0,9 B e Gemma 4 E2B se licença e cópia exata conferirem; dois modos: página inteira × recortes de 1–3 linhas (absorve o micro-experimento A4). *Hipótese:* recortes reduzem omissões/alucinações ≥ 30 % e RAM de pico | escolher o professor com menor CER no `dev-val` cabendo em ≤ 5,0 GB de RAM | descartar o que passar de 5,2 GB, > 120 s/página ou degenerar em > 5 % das linhas | F-DI-13.02; registry | não (CPU, noite, espera de RAM) | — |

**Saída do épico 0 / portão DG-1:** ADR com a decomposição real dos 56 %, teste v3 trancado, `dev-val` pronto,
professor escolhido. **Plano B:** se nenhum VLM local servir, o rascunho das páginas de treino vem do próprio
motor e, a partir do 0.14, do leitor v1 em ciclo iterativo (a cada 5 páginas corrigidas, retreina).

### Épico 0.13-1 — Cobertura sem treino (calibração no `dev-val`)

| Item | O quê e hipótese | Aceite | Abandono | Depende de | GPU | Dados novos |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **EXP-030A** | Ablação dos limiares e da resolução do detector DB sem treino (absorve A3): resolução máxima, `thresh`, `box_thresh`, `unclip_ratio`, fusão de fragmentos. *Hipótese:* metade das linhas perdidas está no mapa de probabilidade e é descartada por limiar de impresso | recall de linhas ≥ 90 % no `dev-val` com caixas falsas ≤ 5 % e detecção ≤ 2,5 s/página | caixas falsas > 10 % ou CER final piora | EXP-028B | não | — |
| **EXP-030B** | Preparação leve e escala (absorve A1, reformulado): iluminação suave por divisão morfológica; escala de **detecção** (alvo 64/80/96 px, EXP-013 mediu 80) e resolução do recorte de origem; padding vertical que preserva acentos e descendentes; filtro de rejeição de pautas vazias. *Hipótese:* ≥ 3 p.p. de CER de linha pareada. UVDoc só se a curvatura for causa provada no EXP-028B | ≥ 3 p.p. no `dev-val` com custo ≤ 0,3 s/página | qualquer filtro que apague traço fraco em ≥ 1 página | EXP-028B | não | — |
| **Dados-13.1** | Degrau 1: caixas + revisão linha a linha das **21 páginas restantes** de desenvolvimento, com rascunho do professor | 21 `dev-train` completas (51 páginas 100 % estruturadas) | — | EXP-029, F-DI-13.01 | não | ~2,5–3,5 h do autor [revisão], sem páginas novas |
| **DG-2** | Portão: a calibração fechou M1 no `dev-val`? | se recall ≥ 92 %: segue para CR-F13.5; senão: EXP-032 (GPU com GNHK, sem dado pessoal) ou plano B em CPU | — | EXP-030A/B | — | — |
| **EXP-032** (condicional) | Detector DB small ajustado com GNHK (CC-BY-4.0, atribuição) + 21 `dev-train`, validado no `dev-val`; fase com GNHK pode ir à GPU sem dado pessoal; fase com suas páginas em casa se couber | recall ≥ 92 % e omissões ≤ 10 % no `dev-val` | > 2 h de GPU ou ganho < 3 p.p. sobre o EXP-030A | DG-2, Dados-13.1 | **opcional** | — |
| **CR-F13.5** (motor) | Parâmetros (e pesos, se houver) vencedores no `config.json`, hash, licença; uma leitura do teste v3 | M1 no teste v3 em ≤ 8 s e ≤ 1 GB | — | EXP-030A/B (032), ADR | não | — |

**Plano B do 0.13** (se a calibração não bastar e você recusar GPU): detecção em duas escalas (fatiamento
horizontal com sobreposição) + resgate por perfil de tinta (caixa candidata onde há tinta num vão maior que 1,6×
a altura mediana), 100 % em CPU [revisão; a medir].

**Critério de saída do 0.13:** M1 no teste v3 (recall ≥ 92 %, omissões ≤ 10 %, 0 páginas < 85 %, caixas falsas
≤ 5 %) **e** Degrau 1 pronto.

---

## 0.14 — Ler certo v1: primeiro leitor nosso em CPU

| Item | O quê e hipótese | Aceite | Abandono | Depende de | GPU | Dados novos |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **EXP-A2** (micro) | Auditoria do dicionário de caracteres do leitor (metadados do ONNX) e da normalização NFC contra os caracteres do `dev-val`. *Hipótese:* 2–5 % do CER vêm de caracteres ausentes ou mal mapeados [revisão] | cobertura de caracteres 100 % ou plano de expansão da camada de saída | — | EXP-028A | não | — |
| **EXP-033A** | Ajuste fino imediato do PP-OCRv6 rec small com as 21 páginas (~400 linhas) em CPU, procedimento do EXP-014/018, melhor checkpoint pelo `dev-val`. *Hipótese:* ≥ 15 p.p. de queda no CER com caixas perfeitas [revisão] | CER no `dev-val` ≤ 35 % em ≤ 4 h de CPU [revisão] | queda < 10 p.p. (indica bug de dicionário, normalização ou camadas congeladas erradas) | Dados-13.1, 0.13 | não (CPU 1–4 h) | **nenhum** |
| **EXP-A6** (micro) | Variância entre 3 sementes e congelamento dos 2 primeiros estágios convolucionais. *Hipótese:* variância < 0,8 p.p. e treino ~35 % mais rápido [revisão] | receita estável fixada para EXP-033B e EXP-036 | — | EXP-033A | não (2–3 h CPU) | — |
| **Dados-14.1** | Degrau 2: +29 páginas novas, pré-preenchidas pelo leitor do EXP-033A ou pelo professor | 50 `dev-train` (~950 linhas) com manifesto | — | EXP-033A | não | +29 páginas do autor |
| **EXP-033B** | Curva 21 → 35 → 50 páginas; vencedor lido uma vez no teste v3. *Hipótese:* 50 páginas atingem M2 | M2 (CER ≤ 30 %, WER ≤ 65 %) no teste v3 | — | Dados-14.1 | não (CPU 2–6 h) | — |
| **EXP-034** | Disputa de arquitetura leve: PP-OCRv6 small × Kraken × PyLaia (timebox de 4 h para build no Windows/WSL2); `rec medium` **fora** do caminho em CPU | só troca se o desafiante reduzir ≥ 2,5 p.p. no `dev-val` com ONNX ≤ 5 s/página | build ou exportação frágil | EXP-033B | não | — |
| **EXP-035** | Sintético PT-BR sobre papel real do caderno (20 mil linhas, fontes OFL): pré-ajuste → real, ou 80/20 por época. *Hipótese:* ≥ 1,5 p.p. de CER e ≥ 3 p.p. em diacríticos | ganho líquido no `dev-val` contra EXP-033B | empate ou piora: desligar para o ajustado, guardar para o MP-2 | EXP-033B | não (1 h geração; 3–8 h treino) | corpus PT-BR livre + fontes OFL |
| **EXP-A7** (micro) | Sensibilidade à quantização INT8 no ONNX. *Hipótese:* FP32 já basta (< 3 s/página) e INT8 degrada 1–3 p.p. [pesquisa] | decisão de exportação | — | EXP-033B | não (30 min) | — |
| **DG-3 / CR-F14.1, 14.2** | Promoção do leitor v1 ao motor (hash, licença, limiar recalibrado no `dev-val`) + indicador de versão do leitor na tela e no estudo | M2 no teste v3, ≤ 10 s, ≤ 1,5 GB; regra: promover se ganho ≥ 20 p.p. mesmo em 31–33 % | — | EXP-033B/034/035, ADR | não | — |

**Plano B do 0.14:** com CER entre 30 e 35 %, promover mesmo assim (ganho real > 20 p.p.) e abrir **EXP-033C**:
análise das 100 linhas de maior erro no `dev-val` (letra miúda, contraste, vocabulário, linhas mistas com
fórmula) para dirigir o 0.15.

---

## 0.14.5 — Consolidação I: coleta vinculada, reprodutibilidade, dívida técnica

| Item | O quê | Aceite | Depende de | GPU |
| :--- | :--- | :--- | :--- | :---: |
| **CR-F13.1** (Leitorum) | Modo "conferência linha a linha" na revisão da digitalização, com `line_id` e caixa por linha, antes do texto livre; `human_corrections` vinculadas; consentimento e opção de desligar | 100 % das linhas corrigidas nesse modo preservam o par caixa ↔ texto | 0.14 | não |
| **CR-F13.2** (Leitorum) | Exportador seguro: pacote por página (foto recortada, caixas, linhas corrigidas, origem do rascunho, hashes) para pasta fora do Git; recusa hashes de teste, `dev-val` e deriva; alinhador para texto livre (só linhas ≥ 90 %) | teste automatizado: 0 linhas de teste/val e 0 linhas desalinhadas no pacote | CR-F13.1 | não |
| **F-DI-14.5** | Pipeline de 1 comando: pacote → treino retomável (checkpoint a cada 15 min) → ONNX → relatório gatekeeper, com semente determinística | duas execuções com a mesma semente: variância 0,0 % | 0.14 | não |
| **F-DI-14.6** | Dívida técnica: consolidar os harness dos EXP-027 a 035 num utilitário do subprojeto, testes, lint, registry de modelos com `NOTICE` de atribuições | suíte verde; registry com lista negra de licenças | 0.14 | não |

---

## 0.15 — Ler certo v2, léxico seguro e ordem de leitura

| Item | O quê e hipótese | Aceite | Abandono | Depende de | GPU | Dados novos |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **Dados-15.1** | Degrau 3: 100–150 `dev-train` pelo produto e pela ferramenta; **antes** de usar, sortear 10 páginas novas como `drift-test-1` | manifestos com hashes | — | 0.14.5 | não | +60 a 110 páginas do uso normal |
| **EXP-036** | Leitor v2: curva 50 → 100 → 150 no `dev-val`, teste v3 e deriva. *Hipótese:* CER com caixas perfeitas ≤ 15 % | queda contínua sem distância > 5 p.p. entre teste e deriva | — | Dados-15.1 | não (CPU 4–10 h; GPU opcional) | — |
| **EXP-037** | Decodificação com léxico dentro do CTC: ARPA (KenLM fora do produto; decodificação `pyctcdecode` Apache-2.0 ou própria) de corpus PT-BR livre + notas dos seus estudos (sem páginas de teste) + gate de proteção (confiança > 0,92, dígitos, símbolos, siglas, abreviações do glossário não são tocados). *Hipótese:* WER −8 p.p., CER −1,5 p.p., dano léxico ≤ 1 % [revisão] | ganho líquido no `dev-val` **e** dano léxico ≤ 1 % | dano > 2 % ou ganho < 0,5 p.p.: desligar | EXP-036, só se CER óptico < 22 % | não (5 min; +0,3 s/página) | notas de estudo (já existem, locais) |
| **EXP-038** | Ordem de leitura e zonas por regras geométricas sobre caixas (colunas, indentação de listas, notas curtas nas bordas), medidas pela diferença WER de página × WER de saco de palavras. *Hipótese:* −50 % da penalidade de ordem | ≥ 50 % no `dev-val` sem piorar páginas de coluna única | regras falham em margem: manter top-down, adiar zonas | EXP-028B | não | — |
| **CR-F15.1, 15.2** | Leitor v2 + decodificador + ordenador no motor; ordem e zonas visíveis no editor | M3 no teste v3 e deriva ≤ 5 p.p. | — | EXP-036/037/038, ADR | não | — |

**Plano B do 0.15:** deriva > 5 p.p. → aumento fotométrico forte (contraste, espessura morfológica, inclinação),
20 % sintético, 20 páginas recentes no `dev-train`.

---

## 0.16 — Fórmulas 2D, zonas e LDF 2.1

| Item | O quê e hipótese | Aceite | Abandono | Depende de | GPU | Dados novos |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **EXP-040** (antes do 039) | Roteador "fórmula 2D × texto (incl. matemática linear simples)": detector MFD pronto (Pix2Text MFD MIT / PP-DocLayout Apache-2.0) × gatilho pós-CTC por densidade de símbolos e entropia. *Hipótese:* gatilho + layout ≤ 2 % de texto comum enviado por engano | precisão ≥ 90 %, recall ≥ 80 % nos trechos `$…$` do `dev-val`, ≤ 2 % de falso envio | > 5 % de texto comum enviado ao módulo de LaTeX | 0.15 | não | marcações `$…$` já existentes |
| **EXP-039** | Motores de fórmula em CPU nos recortes 2D do `dev-val`: TexTeller ONNX INT8 × UniMERNet × professor VLM pontual; métricas: CER em fórmulas, acerto exato, **LaTeX válido** (compila no KaTeX). Ajuste fino opcional com HME100K (Apache-2.0) + seus ~150–250 recortes (a conta da revisão: 1,5–2,5 fórmulas por página) | CER ≤ 35–40 % **e** LaTeX válido ≥ 85 %, ≤ +2,5 s nas páginas com fórmula, ≤ 700 MB extras carregados sob demanda | estourar 1,5 GB ou piorar texto comum > 1 p.p.: fórmulas só sob demanda no editor | EXP-040; registry | inferência não; ajuste opcional sim (2–4 h) | recortes de fórmulas das páginas de treino |
| **CR-LDF-2.1** | Change request + ADR: `math_spans` (latex, compile_valid, bbox) e `zone_type` (body, margin_note, list_item), opcionais e retrocompatíveis | só depois de EXP-038/040/039 provarem ganho | — | EXP-038/039/040 | não | — |
| **DG-4 / CR-F16.1** | Integração no motor (carga sob demanda) + renderização KaTeX no editor; automático na digitalização ou botão sob demanda | M4 no teste v3 | — | CR-LDF-2.1 | não | — |

---

## Roadmap MP — Modelos próprios (paralelo, portões próprios)

**Escopo após os cortes:** o MP concentra-se no **leitor óptico de linha [D1]** e no **decodificador [D2]**, onde
estão a sua letra e a sua língua. Detector próprio (MP-5) e modelos para outros autores (MP-6) saem do roadmap
até existir motivo medido; fórmulas nunca entram no caminho do zero.

| Degrau | O quê | Portão de entrada | GPU | Dados novos |
| :--- | :--- | :--- | :---: | :--- |
| **MP-1 Coleta** | 150+ páginas com caixas (vem do 0.13–0.15), corpus sintético PT-BR, testes v3 e deriva, manifestos | — | não | as páginas |
| **MP-0 Léxico próprio** (já no 0.15) | ARPA + léxico do autor + gate: primeiro componente 100 % nosso | EXP-037 | não | — |
| **MP-2 Leitor próprio do zero** (EXP-041) | CRNN/CTC compacto (~3–6 M parâmetros) em PyTorch puro, no repositório, em **duas fases**: (1) pré-treino em ~200 mil linhas sintéticas PT-BR + GNHK/READ (CC-BY-4.0), **sem dado pessoal** — GPU emprestada 4–10 h [revisão] ou CPU 80–150 h retomável; (2) ajuste fino nas suas 150 páginas **em casa**, CPU 3–8 h [revisão]; congelar primeiras camadas; 20 % sintético | Degrau 4 (150 `dev-train`); DG-5 | fase 1 opcional | sintético (gerar) |
| **MP-3 Comparação** (EXP-042) | próprio × ajustado × baseline VLM no teste v3 e na deriva: CER, WER, cobertura, s/página, RAM, 3 sementes | MP-2 | não | — |
| **MP-4 Substituição** (CR) | entra no motor o que vencer pelo critério M5; registry com hashes dos pesos nossos; o peso herdado sai do produto | MP-3 | não | — |

---

## Micro-experimentos de baixo custo (30 min a 3 h de CPU, sem dados novos)

| ID | Pergunta | Onde entra | Custo | O que decide |
| :--- | :--- | :--- | :--- | :--- |
| A1 | escala de detecção (64/80/96 px) e resolução do recorte; padding vertical | EXP-030B | 20 min | escala e recorte padrão antes de exportar pacotes de treino |
| A2 | dicionário de caracteres e NFC cobrem o português do `dev-val`? | 0.14 (antes do EXP-033A) | 30 min | expansão da camada de saída |
| A3 | `box_thresh`/`unclip_ratio` recuperam ≥ 50 % das linhas omitidas? | EXP-030A | 30 min | pode dispensar o EXP-032 e a GPU |
| A4 | professor em página inteira × tiras de 1–3 linhas | EXP-029 | 1,5 h | modo de pré-anotação |
| A5 | piso de ruído humano: 1 × 2 passadas | EXP-028A | 1 h | regime de passadas no `dev-train` |
| A6 | variância entre sementes; congelar estágios | 0.14 | 2–3 h | receita estável de ajuste |
| A7 | INT8 × FP32 no ONNX | 0.14 | 30 min | exportação |

## O que foi cortado ou adiado

1. **MP-5** detector próprio do zero e **leitor de fórmulas do zero**: fora de escopo (geometria sem viés de
   fornecedor; fórmulas exigem centenas de milhares de pares).
2. **MP-6** outros autores: adiado até existir um segundo usuário real com 50 páginas; o exportador limpo é o
   único pré-requisito.
3. **`rec medium` em CPU** e insistência em **PyLaia** além de 4 h de build.
4. **Esperar 50 páginas** para o primeiro ajuste: o Degrau 1 usa as 21 que existem.
5. **Classificador neural de zonas**: regras geométricas primeiro.
6. **Fórmulas lineares simples** não vão ao módulo de LaTeX: ficam no leitor de texto, com o dicionário auditado.

## Ordem de execução (sem datas; condições de passagem)

```
FASE 1 (bloqueante)      F-DI-13.01 → EXP-028A (+A5) → F-DI-13.02 → { EXP-028B ‖ EXP-029 (+A4) } → DG-1 (ADR)
FASE 2 (51 páginas)      { EXP-030A (+A3) + EXP-030B (+A1) ‖ Dados-13.1 } → DG-2 → [EXP-032?] → CR-F13.5 (M1)
                         → EXP-A2 → EXP-033A → EXP-A6 → { Dados-14.1 ‖ CR-F13.1 + CR-F13.2 + F-DI-14.5 + 14.6 }
                         → EXP-033B + 034 + 035 + A7 → DG-3 → CR-F14.1/14.2 (M2) → 0.14.5 fecha
FASE 3 (escala orgânica) Dados-15.1 (+drift-test-1) → { EXP-036 + 037 ‖ EXP-038 } → CR-F15.1/15.2 (M3)
                         → trilhas independentes: { MP: DG-5 → EXP-041 → EXP-042 → MP-4 } ‖ { 0.16: EXP-040 → 039 → DG-4 → CR-LDF-2.1 → CR-F16.1 (M4) }
```

## Contagem

| Tipo | Quantidade | Quais |
| :--- | ---: | :--- |
| Experimentos | 19 | EXP-028A, 028B, 029, 030A, 030B, 032, 033A, 033B, 033C (plano B), 034, 035, 036, 037, 038, 039, 040, 041, 042 + micro A1–A7 dentro das specs dos pais |
| Features do DI | 5 | F-DI-13.01, 13.02, 14.5, 14.6 e a promoção dos harness |
| Change requests do Leitorum, motor e LDF | 10 | CR-F13.1, 13.2, 13.5, 14.1, 14.2, 15.1, 15.2, LDF-2.1, 16.1, MP-4 |
| Itens de dados | 4 | Dados-13.1, 14.1, 15.1, MP-1 |
| Portões de decisão | 5 | DG-1 a DG-5 |

## Primeiro passo concreto

F-DI-13.01 e EXP-028A: precisam das 20 fotos de teste e das 31 de desenvolvimento em
`dataset/raw/exp-027/fotos/`, processadas por script (nenhuma imagem passa pelo chat), e de ~3–4 h suas para
caixas e 2ª passada. Spec apresentada para aprovação antes de qualquer código, no ritmo fatiado do projeto.
