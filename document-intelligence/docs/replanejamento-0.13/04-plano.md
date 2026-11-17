# Etapa 3 — Plano v2: estratégia, arquitetura-alvo, régua de medição, dados e metas

**Data:** 2026-11-16 (v1 aprovada pelo usuário; **v2** incorpora a [revisão crítica externa](./07-plano-revisado.md))
· **Status:** `RASCUNHO v2` para revisão do usuário · **Base:** [EXP-027](../../experiments/EXP-027-analise-50-paginas/report.md),
[pesquisa](./03-resultado-pesquisa.md), [diretriz de modelos próprios](../objetivo-modelos-proprios.md), histórico EXP-008 a EXP-024.

**Marcas.** **[medido]** = número do projeto; **[pesquisa]** / **[revisão]** = afirmação do relatório da Etapa 2 ou
da revisão externa, com fonte lá, não conferida aqui; **[a medir]** = vira direção só depois de experimento
local (Constituição, Princípio 2).

---

## 0. O que mudou da v1 para a v2, e por quê

A revisão externa foi tratada como dado a pesar. Resultado, item a item:

| Crítica da revisão | Veredito | O que muda no plano |
| :--- | :--- | :--- |
| A referência de teste está sem quebras de linha e sem 2ª passada; medir antes de consertá-la obrigaria a refazer tudo | **Aceita** — coerente com o EXP-027 §2 **[medido]** | Régua limpa vira o **primeiro épico, bloqueante**: caixas de linha e 2ª passada nas 20 páginas de teste antes de qualquer experimento; `frozen-test-v3` |
| M1 (razão de tamanho, palavras omitidas) pode ser batida com lixo (caixas fantasmas, letras repetidas) | **Aceita** | M1 passa a exigir **recall de linhas (IoU ≥ 0,5)** e **teto de caixas falsas**; razão de tamanho fica como sinal auxiliar |
| O EXP-030 calibrava escala e OpenCV olhando as páginas de teste: contaminação | **Aceita** — era uma falha da v1 | Nasce o **`dev-val`** (10 das 31 páginas de desenvolvimento, sorteio único e estratificado): toda calibração, limiar, época e peso do léxico se decidem nele; o teste é usado uma vez, no fechamento |
| Faltavam 19 páginas para "50 de desenvolvimento"; anotar caixas não custa 5–15 min/página quando o detector perde metade | **Aceita** | **Degrau 1** usa só o que existe: 21 `dev-train` + 10 `dev-val` + 20 teste; anotação de caixas separada da transcrição; estimativas de tempo marcadas como **[revisão]** |
| Treinar detector denso e `rec medium` em CPU de 4 núcleos é proibitivo; VLM 4B exige fechar tudo | **Aceita como inferência plausível** **[revisão]** | Detector ajustado vira **condicional** (só se a calibração sem treino não bastar); `medium` sai do caminho em CPU; EXP-029 ganha teto de RAM (5 GB) e tempo (120 s/página) |
| A correção feita no produto perde o vínculo caixa ↔ linha (o usuário reorganiza o texto) | **Aceita** — o EXP-027 mostrou 96 % de reordenação **[medido]** | A coleta do produto passa a ter **modo de conferência linha a linha com `line_id`** antes do texto livre, e o exportador só aceita linhas alinhadas (≥ 90 % de similaridade de borda) |
| Modelo próprio do zero com 1 autor colapsa ou decora as matérias atuais | **Aceita como risco** **[pesquisa]** | MP-2 em **duas fases**: pré-treino pesado só com sintético + datasets CC-BY-4.0 (sem dado pessoal; pode ir à GPU emprestada), ajuste fino das páginas do usuário **em casa** |
| Infraestrutura de avaliação com 8 métricas ortogonais | **Aceita** | Seção 3 deste plano; harness do EXP-027 evolui para o "gatekeeper" |
| Versão intermediária de consolidação (reprodutibilidade, coleta pelo produto, treino em 1 comando) | **Aceita** | **0.14.5** nos roadmaps |
| Numerar a fase zero como `0.12.9` | **Recusada** | O 0.12 do Leitorum está fechado; a fase zero é o **épico 0 do 0.13**, bloqueante. Numeração de produto não muda por conveniência do laboratório |
| "O pipeline escala as linhas para 80 px antes de um modelo cuja entrada nativa é 48 px" (EXP-A1) | **Recusada na premissa, aceita na pergunta** | O motor já entrega 48 px ao leitor; os 80 px são a escala de **detecção** da página (EXP-013 **[medido]**). O experimento vira: variar a escala de detecção e a resolução do recorte de origem, e medir o *padding* vertical que corta acentos e descendentes |
| KenLM é LGPL | **Aceita com nota** | O produto consome um arquivo ARPA gerado fora dele; decodificador por `pyctcdecode` (Apache-2.0) ou implementação própria; nada de ligação estática |
| Métrica de fórmulas em CER engana (40 % de CER = LaTeX que não compila) | **Aceita** | M4 passa a exigir **taxa de LaTeX válido** e acerto exato de expressão, além do CER em fórmulas |
| Fórmulas lineares simples ficam no leitor de texto; só matemática 2D vai ao módulo de fórmulas | **Aceita** | Entra como hipótese do EXP-040 (roteador) |
| Cortar MP-5 (detector próprio), MP-6 (outros autores), `rec medium` em CPU; timebox de 4 h para PyLaia no Windows | **Aceita** | MP-5 e MP-6 saem do roadmap (ficam registrados como "fora de escopo até existir motivo medido"); PyLaia com timebox |
| Estimativas numéricas da revisão (recall ≥ 92 %, CER ≤ 35 % com 21 páginas, −15 p.p., tempos humanos) | **Mantidas como hipóteses** **[revisão; a medir]** | Entram como critérios de aceite de experimentos, nunca como fatos |
| Gemma 4 E2B Apache-2.0, GLM-OCR MIT, números de benchmarks | **Não conferidos** **[pesquisa]** | Só entram depois de cópia exata, licença lida e registro no registry, como o Qwen3-VL já tem |

---

## 1. Diagnóstico em três frases

O motor atual erra mais da metade dos caracteres nas suas páginas (CER 56 %, WER 90 %) **[medido]**. O erro não
vem das fórmulas (12–16 % dele) nem da cursiva (lê igual ou melhor que a letra de forma); vem de **texto comum
mal lido** (54 % de CER) e de **texto que nem chega a ser lido** (28 % das palavras somem; 7 de 20 páginas saem
com 30–67 % do tamanho) **[medido]**. Parte desses 56 % é penalidade de **ordem de leitura** contada como erro
de letra, e essa parte ainda não foi separada **[a medir, épico 0]**. Um modelo grande transcreveu as mesmas
fotos quase sem erro **[medido, declarado pelo usuário]**: o problema é resolvível; a questão é fazê-lo local,
barato e, no fim, com modelos nossos.

## 2. Estratégia em linguagem simples

> **Primeiro a régua, depois enxergar a página inteira, depois ler certo, depois polir.** Cada degrau usa um
> modelo aberto só até um modelo nosso igualar ou superar ele no mesmo teste congelado.

Quatro decisões de fundo:

1. **Régua antes de qualquer mudança.** Nenhuma hipótese de pré-processamento, detector ou leitor é julgada
   enquanto a referência misturar origens de erro. A primeira entrega é a referência auditada e o harness
   que decompõe o erro (seção 3).
2. **Pipeline modular como motor do produto** (foto → linhas → leitura linha a linha → ordem), em vez de um
   modelo multimodal de página inteira: roda em menos de 1 GB e poucos segundos **[medido: 7 s, ~800 MB]**,
   cada peça é treinável em casa ou em poucas horas de GPU **[pesquisa]**, e é o caminho que leva a pesos
   nossos. Um VLM de 4 B em CPU precisa de 3–5 GB e dezenas de segundos por página **[pesquisa; a medir]**.
3. **Modelos multimodais abertos como professor e baseline, fora do produto:** geram o rascunho que você
   corrige (dados de treino) e marcam o teto local. Cópia exata guardada com hash e licença (Qwen3-VL-4B já
   está; GLM-OCR e Gemma 4 E2B são candidatos **[pesquisa]**).
4. **Dados do próprio usuário são o ativo central.** Não há dataset público de manuscrito em português com
   licença limpa para produto **[pesquisa; coerente com o BRESSAY]**. O banco cresce com correções feitas no
   produto, **vinculadas linha a linha**.

## 3. Régua de medição (infraestrutura de avaliação, primeira entrega)

### 3.1 Quatro conjuntos, papéis estritos

| Conjunto | Composição | Para que serve | O que é proibido |
| :--- | :--- | :--- | :--- |
| **`frozen-test-v3`** | as 20 páginas de teste atuais, com caixas de linha e 2ª passada humana; hashes em `splits/test-manifest.json` | juiz final de cada versão (portão de ADR) | treino, prompt, léxico, limiares, épocas, escolha de arquitetura, "dar uma olhada" |
| **`dev-val`** | 10 das 31 páginas de desenvolvimento, sorteio único com semente, estratificado por escrita × fórmulas; com caixas e 2ª passada | calibrar tudo: escala, limiares do detector, época de parada, peso do léxico, escolha do professor | treino |
| **`dev-train`** | as 21 restantes + toda página nova corrigida + sintético | único conjunto que entra no otimizador e no vocabulário | nada |
| **`drift-test-N`** | 10 páginas novas sorteadas a cada ~100 páginas novas ou ~3 meses, congeladas **antes** de entrar no `dev-train` | medir deriva de caneta, caderno, matéria **[pesquisa: queda 5,7 → 11,1 % de CER no mesmo autor]** | treino, calibração |

Regras mecânicas: divisão sempre por **página inteira**; scripts de calibração e treino **recusam por código**
qualquer hash do teste e dos testes de deriva (teste automatizado garante); o teste só é lido pelo script de
fechamento de versão.

### 3.2 Oito indicadores, todos no relatório automático

| # | Indicador | O que diagnostica |
| :--- | :--- | :--- |
| 1 | **Recall de linhas (IoU ≥ 0,5)** e fragmentação (caixas por linha real) | linha não detectada × linha partida |
| 2 | **Caixas falsas** (sem interseção com linha real) | impede bater cobertura com lixo |
| 3 | **CER de linha com caixas perfeitas** (recorte pelas caixas da referência) | evolução do leitor isolada do detector e da ordem |
| 4 | **CER de linha pareada** (caixas do detector casadas por IoU) | caixas apertadas cortando acentos e descendentes |
| 5 | **WER de página × WER de saco de palavras** (ignora ordem) | a diferença é o custo da ordem de leitura |
| 6 | **Erro em diacríticos e sinais do português** (á é í ó ú â ê ô ã õ à ç, setas, pontuação) | "alisamento" para ASCII |
| 7 | **Dano léxico** (siglas, abreviações do autor, trechos `$…$` certos na saída óptica e estragados depois) | o léxico não pode destruir anotação técnica |
| 8 | **Custo**: mediana e p95 de segundos por página, RAM de pico, em processo isolado | páginas densas que estouram tempo ou memória |

Além desses, continuam CER e WER de página (comparáveis ao M0) e a razão de tamanho como sinal auxiliar.

### 3.3 Piso de ruído humano

A diferença entre a 1ª e a 2ª passada nas 30 páginas (teste + `dev-val`) é medida e registrada
(**[revisão]** estima 0,5–1,5 % de CER). Nenhum modelo é cobrado abaixo desse piso.

## 4. Arquitetura-alvo

```
PRODUTO (100 % local, CPU, ≤ 10 s e ≤ 1,5 GB por página)
foto do celular
  ▼
[A] preparação leve ............. OpenCV: margens, iluminação suave (nunca binarização dura)       (c) mantém
  ▼
[B] detecção de linhas .......... PP-OCRv6 DB small (c) com limiares/fusão calibrados no dev-val →
  │                               ajustado com GNHK + páginas suas (b) só se preciso →
  │                               + filtro de rejeição (pauta vazia, rabisco) + resgate por perfil de tinta
  ▼
[C] recorte + escala canônica ... altura e padding calibrados no dev-val; roteador texto/fórmula (0.16)
  ├─ texto ─► [D1] leitor CTC de linha ... PP-OCRv6 rec small (c) → ajustado (b) → próprio (a, MP)
  │                 ▼
  │           [D2] decodificador + léxico ... só com CER < 20 %; ARPA (KenLM) fora do produto,
  │                 decodificação Apache-2.0; gate protege dígitos, símbolos, siglas, abreviações
  └─ fórmula 2D ─► [F] leitor de expressões ... TexTeller ONNX (c→b) + validador de LaTeX
  ▼
[E] ordem e zonas ............... grafo geométrico sobre caixas (colunas, listas, notas de margem)
  ▼
LDF 2.0 (→ 2.1: math_spans, zone_type) ─► Leitorum: conferência linha a linha vinculada por line_id

FÁBRICA (fora do produto)
exportador seguro (bloqueia hashes de teste/val/deriva) ─► professor local em lote (noite) ─►
banco versionado por página (manifestos SHA-256) ─► treino reprodutível (CPU; GPU opcional sem dado pessoal)
─► gatekeeper (3.2) ─► relatório assinado ─► ADR
```

Dois componentes que a v1 não tinha: o **filtro de rejeição** entre [B] e [C] e o **validador de alinhamento
linha ↔ caixa** no exportador. O contrato LDF 2.0 fica estável; `math_spans` e `zone_type` entram como LDF 2.1
por change request e ADR só depois que os experimentos de ordem e fórmulas provarem ganho.

## 5. Três caminhos por etapa, veredito honesto para esta máquina

| Etapa | (a) próprio do zero | (b) ajuste fino, pesos nossos | (c) externo aberto | Veredito |
| :--- | :--- | :--- | :--- | :--- |
| [A] preparação | inviável | UVDoc só se curvatura for causa provada | OpenCV; UVDoc 8 M MIT **[pesquisa]** | (c); ganho **[a medir]** |
| [B] detecção | **cortado** (MP-5 fora de escopo) | DB small com GNHK + páginas suas; GPU 0,5–2 h **[revisão]**; CPU proibitivo **[revisão]** | DB small calibrado: F1 0,81 em fotos EN **[medido]** | calibração (c) primeiro; (b) condicional |
| [C]/[D1] leitura | só em duas fases (pré-treino público/sintético + ajuste em casa) com > 150 páginas | PP-OCRv6 rec small em CPU **[medido: < 1 época, 29,7 → 13,6 % no BRESSAY]**; PyLaia com timebox | VLMs 1–4 B: 3–5 GB, 15–60 s/página **[pesquisa; a medir]** | **(b) é o maior ganho**; (a) é o coração do MP |
| [D2] decodificação | ARPA + léxico do autor: minutos em CPU | ByT5/Monobyte só entre 8 e 18 % de CER **[pesquisa]** | pós-correção por LLM piora **[pesquisa; EXP-011/024]** | (a) leve, só com CER < 20 %, com gate |
| [E] ordem/zonas | regras geométricas: já existe (ADR-003) | classificador de zonas: **cortado** até haver motivo medido | VLM caro em CPU | (a) regras, medidas pelo indicador 5 |
| [F] fórmulas 2D | inviável | TexTeller + HME100K (Apache-2.0) + recortes seus, GPU 2–6 h **[pesquisa]** | TexTeller CC BY 4.0 ONNX ~1 GB **[pesquisa]** | (c) → (b), por último; fórmulas lineares ficam em [D1] |

**Privacidade e GPU emprestada.** Treinar com GPU de terceiros só é aceitável, por decisão sua, quando o
lote **não contém dado pessoal** (sintético + datasets CC-BY-4.0): é o caso do pré-treino do MP-2 e do
pré-treino do detector com GNHK. O ajuste fino com as suas páginas roda em casa, em CPU, como no EXP-014.

## 6. Metas, calibradas pela Etapa 1 (sempre no `frozen-test-v3`, uma leitura por versão)

| Marco | Indicadores | Hoje **[medido]** | Alvo (hipótese) | Observação |
| :--- | :--- | ---: | ---: | :--- |
| M0 | linha de base com a régua v3 | CER 56 %, WER 90 % (v2) | registrar na v3 | pode mudar com a referência corrigida |
| M1 cobertura | recall de linhas IoU ≥ 0,5; caixas falsas; palavras omitidas; páginas < 85 % | — ; — ; 28 %; 7/20 | ≥ 92 % **[revisão]**; ≤ 5 %; ≤ 10 %; 0/20 | calibrado só no `dev-val` |
| M2 leitura v1 | CER / WER de página; CER com caixas perfeitas | 56 % / 90 % | ≤ 30 % / ≤ 65 %; ≤ 22 % **[revisão]** | 21 → 50 páginas |
| M3 leitura v2 | CER / WER; dano léxico; deriva | — | ≤ 15–20 % / ≤ 45 %; ≤ 1 %; diferença teste × deriva ≤ 5 p.p. | 100–150 páginas |
| M4 fórmulas | CER em fórmulas; LaTeX válido; texto comum | 73–77 % | ≤ 35–40 %; ≥ 85 % compila; piora ≤ 1 p.p. | só matemática 2D vai ao módulo |
| M5 próprio | CER(a) × CER(b) no teste e na deriva | — | CER(a) ≤ CER(b) + 0,5 p.p. no teste **e** ≤ CER(b) na deriva; ≤ 5 s, ≤ 500 MB | critério de troca |
| sempre | custo no produto | 7 s, ~800 MB | ≤ 10 s, ≤ 1,5 GB | p95, não média |

Todos os alvos são hipóteses a confirmar; cada um é portão de saída de versão com plano B (roadmaps).

## 7. Como o banco cresce sem contaminar o teste

1. Divisões por página inteira; hashes nos manifestos; bloqueio por código (seção 3.1).
2. **No produto:** modo "conferência linha a linha" na revisão da digitalização, com `line_id` e caixa por
   linha, **antes** da edição livre do estudo; consentimento explícito e opção de desligar; cada linha
   corrigida ali recebe `alignment: exact_human_line`.
3. **Exportador seguro:** recusa hashes de teste, `dev-val` e deriva; para páginas editadas em texto livre,
   alinha por programação dinâmica e só exporta linhas com similaridade de borda ≥ 90 %; teste automatizado
   prova que nada vaza.
4. **Rascunho por professor, correção por você:** rascunhos nunca treinam sem correção humana; cada linha
   registra a origem do rascunho (motor, leitor vN, professor X).
5. **Qualidade da referência:** teste e `dev-val` com duas passadas em dias diferentes; `dev-train` com uma
   passada e auditoria de 10 % das linhas por lote de 25 páginas (lote acima de 2 % de CER volta).
6. **Deriva:** a cada ~100 páginas novas, 10 viram `drift-test-N` antes de qualquer uso.
7. **Degraus de dados:** 1 = 21 `dev-train` + 10 `dev-val` + 20 teste (só com o que existe); 2 = 50
   `dev-train`; 3 = 100 `dev-train` + `drift-test-1`; 4 = 150 `dev-train` (portão do MP-2).
8. **Sintético PT-BR** (fontes OFL sobre faixas de papel real das suas fotos): ensina ortografia, acentos e
   vocabulário, não a sua letra; entra como pré-ajuste ou como ≤ 20 % do lote, nunca em massa misturado com
   400 linhas reais (lição do EXP-021 **[medido]**); desligado quando o treino 100 % real igualar.

## 8. Portões de decisão (decisões suas, com os números na mesa)

| Portão | Quando | Decisão | Você terá em mãos |
| :--- | :--- | :--- | :--- |
| DG-1 | fim do épico 0 do 0.13 | qual professor local e em que modo (linha recortada × página inteira × motor iterativo) | CER no `dev-val`, RAM de pico, s/página, taxa de "correção silenciosa" de abreviações |
| DG-2 | meio do 0.13 | fechar M1 só com calibração, ou treinar o detector (GPU com GNHK sem dado pessoal) | recall de linhas e omissões no `dev-val` após calibração |
| DG-3 | fim do 0.14 | promover o leitor v1 ao produto; congelar arquitetura | relatório completo no teste v3 (21 e 50 páginas); regra: promover se ganho ≥ 20 p.p. mesmo raspando a meta |
| DG-4 | meio do 0.16 | fórmulas automáticas na digitalização ou botão sob demanda | precisão do roteador, LaTeX válido, RAM e segundos extras |
| DG-5 | entrada do MP-2 | pré-treino do modelo próprio: GPU emprestada só com dados públicos/sintéticos (recomendado) ou tudo em CPU | banco de 150 páginas, sintético, resultado do leitor (b) |

## 9. Riscos (sinal mensurável → resposta)

| Risco | Sinal | Resposta |
| :--- | :--- | :--- |
| Contaminação silenciosa do teste | qualquer script de calibração lendo o manifesto de teste | bloqueio por código; teste só no fechamento |
| Desalinhamento caixa ↔ texto nas correções do produto | linhas exportadas com comprimento incoerente com a caixa; CER sobe ao treinar com mais páginas | modo linha a linha com `line_id`; filtro de alinhamento no exportador |
| RAM estourando com VLM no Windows | processo > 5,2 GB ou > 120 s/página | modelos menores, recortes de 1–3 linhas, ou motor iterativo como professor |
| Ruído visual do Qwen3-VL no llama.cpp **[pesquisa: issue #29251]** | erros em palavras legíveis | projetor em F16 (já é), recortes em vez de página espremida, outro professor |
| Alucinação do professor virando verdade | auditoria de 10 % achando > 2 % de abreviações "corrigidas" | destaque de divergência motor × professor na ferramenta; regra "escreva o que está no papel" |
| Colapso ou memorização no treino do zero | loss CTC parada; saída vazia; deriva > 5 p.p. | duas fases; congelar primeiras camadas; aumento fotométrico; 20 % sintético |
| Build de PyLaia/Kraken no Windows | > 4 h de tentativa | timebox: fica PP-OCRv6 small ou CRNN próprio em PyTorch |
| Dano do léxico em siglas e fórmulas | dano léxico > 1 % | gate de proteção; desligar se > 2 % |
| Licença incompatível ou contaminação de destilação | tentativa de usar Qwen2.5-VL-3B, Gemma 3, DocLayout-YOLO, Nougat, PorTEXTO | lista negra no registry; só Apache-2.0, MIT, BSD, CC-BY-4.0 no produto, com `NOTICE` |

## 10. O que medir antes de decidir, na ordem

1. Caixas + 2ª passada nas 30 páginas (teste e `dev-val`) e a decomposição exata do erro por origem.
2. Benchmark de professores locais no `dev-val`, em página inteira e em recortes de linha.
3. Micro-experimentos baratos (roadmaps, seção "A1–A7"): limiares do detector, escala de detecção e padding,
   dicionário de caracteres, variância entre sementes, quantização.
4. Primeiro ajuste fino do leitor com as 21 páginas que já existem.

## 11. O que a Etapa 4 faz com isto

Os roadmaps (v2) dividem o trabalho em 0.13 (com o épico 0 bloqueante), 0.14, 0.14.5 (consolidação), 0.15,
0.16 e o roadmap MP, cada item com hipótese, critério de aceite, critério de abandono, dependências, GPU e
dados inexistentes, mais a lista de micro-experimentos e a de cortes.
