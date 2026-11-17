# Revisão Crítica Sênior e Plano Ampliado: Qualidade de Digitalização (HTR/OCR) e Trajetória de Modelos Próprios (Etapas 3 e 4 — v2)

**Data da revisão:** 16 de novembro de 2026  
**Escopo:** Auditoria técnica cética e reescrita integral do Plano (Etapa 3) e dos Roadmaps 0.13+ e MP (Etapa 4), confrontados contra o Diagnóstico Medido (EXP-027 / Etapa 1) e a Pesquisa de Literatura (Etapa 2).  
**Restrições invioláveis:** Produto 100% local em CPU (Intel i5-8265U 4 núcleos, 7,9 GB RAM, Windows 11, Python 3.13, sem GPU útil), sem custo por uso; modelos de pesos abertos apenas como baseline/professor (com hash e licença registrados); objetivo final de modelos próprios; 20 páginas do teste congelado jamais entram em treino, prompt, léxico ou escolha de limiar; adaptação ao autor (nunca pedir que o autor mude a caligrafia).  
**Convenção epistemológica:** **[Fato — Projeto]** = medido no EXP-027 ou histórico EXP-008..024; **[Fato — Literatura]** = evidência primária com fonte e data; **[Inferência]** = dedução técnica do revisor; **[A medir]** = hipótese dependente de experimento local.

---

## Parte I — Visão Executiva em Linguagem Acessível (Para Tomada de Decisão)

O plano original (Etapas 3 e 4) acerta na escolha estrutural mais importante: **manter um motor modular leve em CPU** (detecção de linhas → leitura linha a linha → ordenação) em vez de colocar um modelo multimodal gigante dentro do produto, e **usar modelos abertos maiores apenas fora do produto, como professores** que geram rascunhos para você corrigir. Acerta também ao tratar suas próprias páginas corrigidas como o verdadeiro patrimônio do projeto, já que não existe banco público de manuscrito em português com licença comercial limpa ([Repo BRESSAY/pySarah](https://github.com/arthurflor23/handwritten-text-recognition), 2024–2026; [PorTEXTO CC-BY-NC-4.0](https://huggingface.co/datasets/amalia-llm/PorTEXTO), jun/2026).

Porém, quando olhamos com lupa de engenharia para um projeto que precisa durar meses sem travar nem enganar você com números falsos, o plano original tem **sete fragilidades graves** que precisam ser corrigidas agora:

1. **A régua de medição atual está quebrada (e o plano deixa o conserto para tarde demais):** Hoje, as 20 páginas do teste congelado têm uma transcrição feita por um modelo externo sem quebras de linha em 6 dos 20 blocos e sem uma segunda conferência humana linha a linha **[Fato — Projeto, EXP-027]**. Além disso, quando o detector erra a ordem de uma nota de margem ou de duas colunas, a comparação de página inteira conta tudo como "erro de leitura". Se você não consertar a referência e o script de avaliação **antes** de qualquer experimento (numa versão `0.12.9` / `0.13-Zero`), vai passar meses achando que o leitor não melhora quando, na verdade, a régua está misturando erro de ordem, erro de caixa e erro de letra.
2. **A métrica de cobertura do Marco 1 (M1) pode ser batida "no papel" com lixo:** O plano define M1 como "nenhuma página com saída menor que 85% do tamanho da referência e ≤10% de palavras omitidas". Em reconhecimento CTC, basta baixar o limiar de detecção (aceitar pautas vazias, rabiscos e sombras como linhas) ou afrouxar a fusão de caixas para o motor cuspir caracteres fantasmas: o tamanho da saída passa de 85% no papel, mas o texto continua ilegível. Cobertura só vale se for medida como **recall de caixas reais de linha (IoU ≥ 0,5)** e acompanhada de um teto de inserções falsas.
3. **Proibição de calibrar limiares no teste congelado:** O plano diz que o teste congelado nunca entra em calibração, mas no Épico `0.13-A` (`EXP-030`) manda testar variações de escala e preparação diretamente nas 20 páginas de teste e escolher a melhor regra. **Isso é contaminação direta do conjunto de teste.** Toda escolha de escala, margem, fusão de caixas e limiar de confiança tem de ser feita nas **31 páginas de desenvolvimento** (ou num subconjunto fixo de validação de 10 páginas dentro delas), usando as 20 páginas congeladas apenas uma vez no fim para confirmar se funcionou.
4. **O gargalo oculto de anotar caixas em 50 páginas:** O plano assume que você vai anotar caixas e transcrever 50 páginas em "5 a 15 minutos por página" no `0.13-B`. **Fato da literatura:** 5–15 minutos por página só é verdade quando as caixas já vêm quase certas e o texto já vem pré-transcrito ([PPOCRLabel](https://pypi.org/project/PPOCRLabel/), Apache 2.0; [eScriptorium](https://ub-mannheim.github.io/eScriptorium_Dokumentation/Training-with-eScriptorium-EN.html)). Mas hoje você só tem 31 páginas de desenvolvimento no projeto, e nas páginas ruins o detector atual perde até metade das caixas **[Fato — Projeto]**. De onde vêm as outras 19 páginas para chegar a 50 no `0.13` se a feature do produto só fica pronta junto? E quem desenha as caixas que o detector perdeu? O plano precisa separar **anotação de caixas** de **transcrição de linhas**.
5. **Treinar em CPU de 8 GB sem estourar memória ou travar o notebook:** O plano afirma que o `EXP-034` vai treinar `PP-OCRv6 rec medium` (19M parâmetros) e `PyLaia` (~9,5M) na sua CPU de 4 núcleos, e que o `EXP-032` pode ajustar o detector `DB small` em CPU em 4–12 h. **[Inferência técnica]:** O detector DB opera em imagens de página inteira (ex.: 960×960 ou 1280×1280); o *backpropagation* de mapas de características densos nessa resolução consome 4 a 8 GB só de ativações e leva dezenas de horas em 4 núcleos AVX2 sem GPU. E no `EXP-029`, rodar `Qwen3-VL-4B` no Windows 11 com 7,9 GB de RAM exige fechar navegador e IDE, porque o Windows sozinho ocupa ~2,5 GB e o modelo + projetor visual (`mmproj`) + cache de imagem consomem ~4,2–4,8 GB ([unsloth/Qwen3-VL-4B-Instruct-GGUF](https://huggingface.co/unsloth/Qwen3-VL-4B-Instruct-GGUF), 2025).
6. **Dependência oculta no alinhamento entre correção do usuário e caixas de linha (`CR-F13.1`):** No Leitorum, quando você edita o texto transcrito na tela, você apaga linhas, junta parágrafos e reordena blocos (tanto que no `EXP-027` 96% da diferença entre bruto e revisado era reordenação **[Fato — Projeto]**). Se a feature `CR-F13.1` apenas salvar o "texto final da página" junto com as "caixas originais do motor", **não haverá mais correspondência 1-para-1 entre cada caixa recortada e sua linha corrigida**, inutilizando o pacote para treinar o leitor CTC! A correção precisa ser vinculada por `line_id` antes de o usuário reorganizar o estudo, ou alinhada automaticamente com filtro estrito de confiança.
7. **Treinar leitor próprio do zero (`MP-2`) com um único autor tem risco altíssimo de memorização cega:** A literatura de 2026 mostra que abaixo de 110 páginas cerca de dois terços dos treinos do zero colapsam para CER > 70% ([Oxford DSH](https://academic.oup.com/dsh/article/41/3/1365/8666109), mai/2026). Mesmo com 150 páginas suas + linhas sintéticas, um modelo treinado do zero só na sua mão corre o risco de decorar as palavras dos seus assuntos atuais e colapsar quando você começar uma disciplina nova no semestre seguinte ([arXiv:2411.17332](https://arxiv.org/html/2411.17332v1), nov/2024; [CEUR-WS Cavalcaselle](https://ceur-ws.org/Vol-4240/short31.pdf), ago/2026).

---

## Parte II — Auditoria Crítica Detalhada do Plano (Etapa 3) e dos Roadmaps (Etapa 4)

### 1. Auditoria Seção a Seção do Plano (Etapa 3)

| Seção da Etapa 3 | O que está bem fundamentado | O que é afirmação sem evidência ou frágil | O que falta / Ordem errada | Onde o marco pode ser batido "no papel" (Métrica falha) |
| :--- | :--- | :--- | :--- | :--- |
| **§1 Diagnóstico** | Números exatos do `EXP-027` (CER 56%, WER 90%, 28% omissão, fórmulas 12–16%, cursiva 50% vs mista 63%) **[Fato — Projeto]**. | Assume que o professor externo foi "praticamente perfeito" sem medir CER dele contra revisão humana rigorosa. | Falta explicitar que os 56% de CER página-inteira incluem penalidade de permutação (erros de ordem de leitura contados como substituições/deleções). | Se a ordem de leitura mudar 2 blocos de lugar, o CER de página sobe ~10–15 pontos mesmo que o leitor acerte 100% das letras. |
| **§2 Estratégia** | Manter pipeline modular em CPU (<1 GB, ~7 s) e usar VLMs abertos apenas como professor/baseline com cópia e hash guardados. | Assume que um VLM 4B local em CPU conseguirá servir confortavelmente como gerador de rascunhos em lote na máquina de 7,9 GB sem travar o uso diário. | Falta distinguir **professor de linha recortada** vs **professor de página inteira** (no `llama.cpp`, Qwen3-VL tem ruído visual em baixa resolução: [issue #29251](https://github.com/ggml-org/llama.cpp/issues/29251), set/2026). | Escolher um professor pelo CER de página inteira sem notar que ele "corrige silenciosamente" abreviações do autor (*Prior-Driven Errors*: 63–79% dos erros no [WildHandBench](https://arxiv.org/html/2608.22959v1), ago/2026). |
| **§3 Arquitetura-alvo** | Separação clara entre `[A..F]` no motor e professor fora do motor; estabilidade do contrato `LDF 2.0`. | Trata `[B] detecção` e `[E] ordem/zonas` como etapas distantes no tempo (`0.13` vs `0.15`), quando na prática páginas de escrita "mista" (62,7% CER **[Fato — Projeto]**) sofrem justamente de listas, setas e notas de margem. | Falta um componente explícito de **Filtro de Qualidade / Rejeição de Ruído** entre `[B]` e `[C]` (para não ler pautas vazias, setas ou rabiscos como texto) e um **Validador de Alinhamento Linha↔Caixa** no exportador. | — |
| **§4 Três caminhos por etapa** | Descarte honesto de treino do zero para `[A]` e `[F]`; priorização de `(b)` ajuste fino em `[C]` e `(a)` KenLM leve em `[D]`. | Afirma que ajustar `DB small` em CPU leva "4–12 h apertado" e que `PP-OCRv6 rec medium` roda treino fácil em CPU. **[Inferência]:** treino de detector denso em imagem alta em 4 núcleos CPU sem GPU é proibitivo na prática. | Falta separar o custo de **inferência em lote do professor** (50 páginas × 45 s = ~40 min de CPU 100% ocupada) e falta alertar sobre a licença do `Qwen3-VL` vs `Qwen2.5-VL-3B` (proibido comercialmente: [LICENSE](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct/blob/main/LICENSE)) e `Gemma 3` (contamina destilação: [Gemma Terms](https://ai.google.dev/gemma/terms)). | — |
| **§5 Metas mensuráveis (M0..M5)** | Uso do mesmo conjunto congelado e recusa de promessas mágicas. | **M1** exige "0 de 20 páginas com saída <85% do tamanho da referência". Em páginas com listas curtas, diagramas ou muita fórmula simplificada, a razão de caracteres é instável. | Falta uma métrica de **CER pareado por linha (Line-matched CER)** e **Normalized Edit Distance (NED) invariante à ordem** (como *Bag-of-Words Recall* + *Line IoU Recall*). | **Alto risco de "gaming" em M1:** se o detector dividir linhas ao meio ou detectar pautas em branco e o reconhecedor repetir letras, o número de caracteres passa de 85% do esperado com texto inútil. |
| **§6 Crescimento do banco e higiene** | Proibição de dividir a mesma página entre treino e teste; guarda de hashes e manifesto; marcação `$...$`. | Não cria uma **divisão fixa de Validação (`dev-val`) separada do Treino (`dev-train`)** dentro das 31+ páginas de desenvolvimento! Se você usar todas as páginas de dev para treinar e olhar o Teste Congelado para decidir época, *learning rate* e escala, você vazou o Teste Congelado. | Falta resolver matematicamente o **problema das 19 páginas faltantes**: o projeto tem 51 páginas (20 teste + 31 dev). Para ter 50 páginas de dev no `0.13`, faltam 19 páginas novas antes mesmo de o `0.14` começar. | Achar que o teste congelado está "puro" quando, na verdade, ele foi usado 15 vezes seguidas para escolher hiperparâmetros e regras de OpenCV (seleção indireta / *adaptive overfitting*). |
| **§7 O que medir antes de decidir** | Colocar a quebra detecção × leitura (`EXP-028`) como passo 1. | Coloca a revisão humana da referência (`EXP-031`) **depois** de `EXP-028`, `EXP-029` e `EXP-030`! | **Ordem invertida:** você não pode medir `EXP-028` (recall de linhas), `EXP-029` (teto do VLM) e `EXP-030` (escala) contra uma referência v2 que não tem quebras de linha em 6 blocos e não teve 2ª passada, e só depois no `EXP-031` mudar a referência para v3! Isso obrigaria a invalidar e re-rodar `EXP-028`, `029` e `030`. | Medir o professor VLM (`EXP-029`) contra uma referência gerada por outro VLM sem revisão humana linha a linha premia alucinações compartilhadas entre VLMs. |

---

### 2. Auditoria por Versão dos Roadmaps (Etapa 4)

#### Versão `0.13` — "Ver a página inteira, e ter dados"
* **O que está na ordem errada:**
  1. `EXP-031` (Revisão das 20 referências de teste e recongelamento para v3) está no Épico `0.13-B`, **depois** do Épico `0.13-A` (`EXP-028`, `EXP-029`, `EXP-030`). Se `EXP-028` precisa comparar as caixas e linhas do motor contra a referência linha a linha, e a referência v2 atual *não tem quebras de linha em 6 blocos* **[Fato — Projeto, EXP-027]**, `EXP-028` é impossível de ser executado corretamente antes de `EXP-031`!
  2. `EXP-030` ajusta regras de OpenCV e escala olhando as páginas de pior cobertura do teste. Isso viola a governança do teste congelado.
* **Passos que exigem dados que ninguém vai produzir no prazo da versão:**
  * `Dados-13.4` exige **50 páginas de desenvolvimento** transcritas linha a linha com caixas. Hoje existem apenas **31 páginas de desenvolvimento** **[Fato — Projeto]**. Para chegar a 50, você precisa digitalizar e revisar mais 19 páginas reais suas antes de fechar a `0.13`. Além disso, anotar *bounding boxes* / polígonos em 50 páginas onde o detector falha leva muito mais que 5–15 min/página se a ferramenta `F-DI-13.3` só mostrar as caixas que o motor achou (e não tiver editor de caixas faltantes).
* **Onde falta Plano B:**
  * Se `EXP-030` (escala/OpenCV) não atingir M1 e o dono **não quiser enviar suas páginas para GPU na nuvem** no `EXP-032` (treino do detector DB), o que acontece? Treinar DBNet em página inteira na CPU i5-8265U pode travar por dias. O plano não traz o Plano B 100% local sem treino pesado de detector (ex.: *tiling* / fatiamento horizontal com sobreposição + ajuste de limiares `box_thresh`/`unclip_ratio` do DB no ONNX Runtime + projeção horizontal de perfil de tinta nas zonas onde faltam caixas).

#### Versão `0.14` — "Ler certo: leitor ajustado v1"
* **O que está bem fundamentado:** Replicar o sucesso do `EXP-014/018` (ajuste fino CTC em CPU) nas páginas reais do autor **[Fato — Projeto]**.
* **O que é afirmação sem evidência / risco de máquina:**
  * `EXP-034` propõe treinar `PyLaia` e `PP-OCRv6 rec medium` em CPU no Windows 11 com Python 3.13. **Fato técnico:** `PyLaia` tem dependências históricas complexas em C++/PyTorch/warp-ctc que frequentemente falham ao compilar no Windows nativo (exigindo WSL2) e Python 3.13 ainda sofre incompatibilidades de *wheels* pré-compilados em pacotes legados de HTR. Tratar isso como um experimento simples sem antes validar o ambiente de build vai travar a `0.14`.
  * `EXP-035` (Sintético PT-BR): o plano diz que vai renderizar fontes cursivas com pauta, sombra e perspectiva. Mas **fontes tipográficas cursivas têm glifos idênticos toda vez que a mesma letra se repete**, enquanto a escrita humana varia a ligação entre letras. Se você misturar 50.000 linhas sintéticas de fonte estática com apenas 900 linhas reais suas (50 páginas), o modelo vai decorar as fontes sintéticas e piorar na sua letra real (exatamente como o `EXP-021` fracassou com degradação artificial **[Fato — Projeto]**), a menos que a proporção de mistura (*mixing ratio*) seja rigidamente controlada (ex.: pré-treino no sintético → ajuste fino só no real, ou ≤30% sintético por batch).
* **Meta sem critério de parada claro:** "Se o EXP-033 ficar acima de 30% com 50 páginas, fecha com Dados-13.4 estendido a 100". Mas se com 50 páginas o CER cair de 56% para 31,5%, vale a pena travar a versão inteira por meses esperando mais 50 páginas, ou entregar o ganho de 24,5 pontos no produto e continuar a coleta em produção?

#### Versão `0.15` — "Ler certo e polir: leitor v2, léxico e ordem"
* **Dependência oculta:** `CR-F13.1/13.2` (coleta pelo produto) precisa preservar o vínculo exato `caixa_da_linha ↔ texto_corrigido_da_linha`. Se no uso real do Leitorum você corrigir o texto livremente num bloco Markdown único, `Dados-15.1` terá 100 páginas de texto corrigido **sem alinhamento linha a linha**, que não servem para treinar CTC!
* **Risco de licença:** `KenLM` é **LGPL**; usado via binário externo ou bindings Python sem modificar código-fonte do KenLM é seguro, mas se embutido estaticamente num executável fechado exige cuidado. Alternativa ainda mais simples e 100% sob controle (MIT/Apache): decodificador CTC com *prefix beam search* em Python/Cython/Numba ou `pyctcdecode` (Apache 2.0) consumindo um arquivo ARPA gerado pelo KenLM fora do produto.
* **Ordem errada:** `EXP-038` (Ordem de leitura e zonas) aparece só na `0.15`, mas páginas de escrita "mista" (62,7% de CER no `EXP-027`) têm listas, setas e notas de margem que bagunçam a medição de página inteira desde a `0.13`. A métrica de ordem precisa nascer no `0.13`, mesmo que a feature visual no editor fique para a `0.15`.

#### Versão `0.16` — "Fórmulas e layout de caderno"
* **Passo que exige dado que ninguém vai produzir:** `EXP-039` fala em "500+ recortes de fórmulas manuscritas suas, se for ajustar". **Faça a conta:** nas suas 51 páginas, fórmulas são 12% dos caracteres (~310 caracteres por página nas páginas que têm fórmula, ou ~2 a 4 expressões por página em 59% das páginas) **[Fato — Projeto, EXP-027]**. Isso dá cerca de **1,5 a 2,5 fórmulas por página na média geral**. Para juntar **500 recortes de fórmulas suas**, você precisaria digitalizar e anotar **200 a 330 páginas de caderno**! Em 100–150 páginas você terá apenas ~150–250 recortes de fórmula.
* **Onde um marco pode ser batido no papel sem resolver o produto:** Medir `CER ≤ 40%` em fórmulas. Em LaTeX, **40% de erro de caractere significa 100% de falha de compilação/renderização** (basta errar uma chave `{` ou um comando `\frac` para o KaTeX/MathJax quebrar ou renderizar outra equação). Em matemática, as métricas corretas são **Taxa de Compilação Sintática Válida (1 - Failure Rate)**, **ExpRate (acerto exato da expressão)** ou **EPMR / CDM** ([TexTeller, arXiv:2508.09220](https://arxiv.org/html/2508.09220v1), ago/2025).

#### Roadmap `MP` — Modelos Próprios
* **Risco subestimado de colapso e deriva:** `MP-2` propõe treinar um leitor CTC do zero assim que houver 150 páginas reais + 100k–500k linhas sintéticas. Embora 150 páginas superem o limiar de 110 páginas de [Oxford DSH](https://academic.oup.com/dsh/article/41/3/1365/8666109) (mai/2026), 150 páginas suas têm apenas ~2.850 linhas reais e um vocabulário restrito às matérias que você estudou naqueles meses. Um modelo treinado **do zero** (sem o pré-treino visual de milhões de imagens variadas que o `PP-OCRv6` teve) pode empatar no teste v3 da mesma época e **desabar no Teste de Deriva** quando você trocar de caneta ou de matéria.

---

## Parte III — Plano Ampliado e Reescrito (Etapas 3 e 4 Unificadas e Robustecidas)

### A. Estratégia e Arquitetura-Alvo em Linguagem Simples

A filosofia central do projeto é **Autonomia Progressiva com Régua Imutável**:
1. **No produto (tempo de uso):** Tudo roda em menos de 1,5 GB de RAM e até 10 segundos por página na CPU do seu notebook, usando modelos pequenos em ONNX Runtime. Nenhum modelo grande (VLM) entra no fluxo obrigatório do usuário.
2. **Fora do produto (fábrica de dados e treino):** Modelos multimodais abertos (guardados com hash SHA-256 e licença auditada) trabalham em segundo plano como **professores** para pré-transcrever suas páginas novas de desenvolvimento. Você apenas corrige os erros do rascunho linha a linha. Essas correções alimentam o treino dos modelos pequenos — primeiro ajustando pesos abertos permissivos (Apache 2.0 / MIT) que passam a ser seus, e depois treinando arquiteturas próprias do zero quando o banco tiver volume e diversidade suficientes.
3. **Separação estrita entre motor e laboratório:** O motor só conhece arquivos `.onnx`, um dicionário/ARPA estático e um `config.json` assinado por hash. Qualquer mudança exige passar pelo **Relatório Automático de Avaliação** sem regredir nem no Teste Congelado nem no Teste de Deriva.

#### Diagrama em Texto da Arquitetura-Alvo Completa (Produto vs. Fábrica Offline)

```text
================================================================================
A. AMBIENTE DO PRODUTO (100% Local, CPU i5-8265U, ≤ 10 s/pág, ≤ 1,5 GB RAM)
================================================================================

[Foto de Celular da Página do Caderno]
   │
   ▼
[A. Preparação Geométrica e Fotométrica Leve] (OpenCV Apache-2.0)
   │  • Detecção de margens/folha, correção de iluminação suave (divisão morfológica
   │    em tons de cinza/RGB, NUNCA binarização rígida que apaga lápis/traço fino)
   ▼
[B. Detecção de Linhas e Regiões + Resgate de Cobertura]
   │  • Detector PP-OCRv6 DB small (ONNX, Apache-2.0 → ajustado com pesos nossos)
   │  • Pós-processamento geométrico calibrado em dev-val: unclip_ratio adaptativo,
   │    fusão horizontal consciente de espaçamento e resgate por perfil de tinta
   │  • Filtro de rejeição de pautas vazias / rabiscos sem tinta suficiente
   ▼
[C. Recorte Desentortado + Escala Canônica + Classificador Leve de Trecho]
   │  • Normalização de altura (testada em dev-val: 48px / 64px / 80px) + margem direita
   │  • Roteamento (a partir da v0.16): [Texto Comum] vs [Bloco/Trecho de Fórmula]
   ├───► (Se Texto Comum) ──► [D1. Leitor Óptico CTC de Linha]
   │                           • Fase b: PP-OCRv6 rec small / PyLaia ajustado (ONNX)
   │                           • Fase a (MP): CRNN/CTC próprio treinado do zero (ONNX)
   │                                │
   │                                ▼
   │                          [D2. Decodificador CTC + Léxico Adaptativo] (só c/ CER < 20%)
   │                           • Prefix Beam Search + KenLM ARPA (PT-BR + glossário do autor)
   │                           • Gate de proteção: desativa correção em tokens com dígitos,
   │                             símbolos matemáticos, CAIXA ALTA (siglas) ou abreviações
   │
   └───► (Se Fórmula, v0.16) ► [F. Leitor de Expressões Matemáticas]
                               • Fase c/b: TexTeller ONNX INT8 (CC BY 4.0) ou fallback
                               • Validador sintático de LaTeX (se falhar parse → mantém texto cru)
   │
   ▼
[E. Ordenador Geométrico de Layout de Caderno]
   │  • Grafo topológico leve sobre caixas: detecta 1 vs 2 colunas, indentação de listas
   │    e vincula notas de margem ao parágrafo mais próximo sem cruzar blocos
   ▼
[Contrato LDF 2.0 / 2.1] ──► [Interface Leitorum: Revisão Linha a Linha Vinculada]
   • Guarda por line_id: bbox, texto_bruto, confiança, texto_corrigido_pelo_usuário


================================================================================
B. FÁBRICA OFFLINE DE DADOS, AVALIAÇÃO E TREINO (Fora do Produto)
================================================================================

[Exportador Seguro do Leitorum] (bloqueia hashes de test-manifest.json e drift-manifest.json)
   │
   ├──► [Pré-Anotador / Professor Local em Batch] (CPU ociosa / madrugada)
   │     • Qwen3-VL-4B / Gemma 4 E2B / GLM-OCR (GGUF Q4_K_M + mmproj F16/Q8_0)
   │     • Gera rascunho APENAS para páginas novas de dev; sempre revisado pelo autor
   │
   ├──► [Banco Versionado de Dados do Autor (DVC / Manifestos SHA-256)]
   │     • Split estrito por PÁGINA INTEIRA:
   │       1. frozen-test-v3 (20 págs fixas — intocável)
   │       2. temporal-drift-test (10 págs a cada 100 novas — intocável)
   │       3. dev-val (10 págs fixas das 31 de dev — escolha de limiares/early stopping)
   │       4. dev-train (21 págs iniciais + todas as novas páginas corrigidas + sintético)
   │
   ├──► [Motor de Treino Reprodutível] (CPU local noturna ou GPU emprestada opcional)
   │     • Treina [B], [D1], [D2], [F] com semente fixa → Exporta e valida ONNX
   │
   └──► [Harness de Avaliação Automática (Gatekeeper)]
         • Roda em frozen-test-v3 + temporal-drift-test + dev-val
         • Emite Relatório JSON/Markdown assinado (CER/WER decompostos, RAM, s/pág)
```

---

### B. Infraestrutura de Avaliação como Primeira Entrega (`v0.12.9` / Épico Zero)

Nenhuma hipótese de pré-processamento, detector ou leitor pode ser julgada enquanto a régua misturar origens de erro ou tiver referências sem quebras de linha. A **primeira entrega obrigatória** do projeto é o **Harness de Avaliação Decomposta**.

#### 1. Os Quatro Conjuntos de Avaliação e Seus Papéis Estritos
1. **`frozen-test-v3` (20 páginas congeladas atuais, revisadas linha a linha pelo autor):** Nunca entra em treino, nunca entra em prompt, nunca entra no léxico e **nunca é usado para escolher hiperparâmetros, altura de linha ou limiares de OpenCV/DB**. Serve exclusivamente como juiz final de aprovação de versão (Portão de ADR).
2. **`dev-val` (10 páginas sorteadas uma única vez entre as 31 páginas de desenvolvimento, estratificadas por cursiva/mista/forma e fórmulas):** **Este é o conjunto que faltava no plano.** É no `dev-val` que você testa se escala de 64 px é melhor que 80 px (`EXP-030`), escolhe o `box_thresh` do detector, decide em qual época parar o treino (*early stopping*) e calibra o peso do KenLM.
3. **`dev-train` (as 21 páginas restantes das 31 iniciais + todas as novas páginas que vierem do produto/ferramenta):** Único conjunto cujas imagens e textos entram no otimizador de treino e na construção do vocabulário do autor.
4. **`temporal-drift-test` (Teste de Deriva Longitudinal):** A cada 100 páginas novas coletadas (ou a cada 3 meses), 10 páginas novas são sorteadas antes de entrar no `dev-train` e congeladas num lote datado (`drift-2027Q1`, `drift-2027Q2`). Mede se o modelo ficou viciado nas matérias/canetas antigas (**[Fato — Literatura]:** queda de 5,71% para 11,07% CER no mesmo autor por deriva de sessão em [CEUR-WS Cavalcaselle](https://ceur-ws.org/Vol-4240/short31.pdf), ago/2026).

#### 2. O Que Medir Que o Plano Atual Não Mede (Métricas Decompostas por Origem)
O plano atual mede apenas CER/WER de página inteira e razão de tamanho. O novo relatório automático medirá obrigatoriamente **8 indicadores ortogonais**:

| Métrica | Como é calculada | O que ela diagnostica (e evita "bater meta no papel") |
| :--- | :--- | :--- |
| **1. Line Recall (`IoU ≥ 0,5`) e Fragmentação** | Fração das linhas reais da página que têm pelo menos 1 caixa detectada cobrindo ≥80% da sua largura; e número médio de caixas por linha real. | Separa "linha não detectada" de "linha cortada pela metade" ou "linha partida em 3 pedaços". |
| **2. Taxa de Caixas Fantasmas (False Positive Boxes)** | Caixas detectadas pelo motor que não têm interseção com nenhuma linha real da referência (ex.: pauta vazia, espiral do caderno, margem). | Impede que você bata M1 apenas baixando o limiar do detector e gerando lixo. |
| **3. Oracle-Box Line CER (CER puro do leitor)** | CER medido recortando a página com as **caixas perfeitas da referência** (sem erro do detector nem erro de ordem). | Mede a evolução real do reconhecedor `[C]` isolada de falhas de `[B]` e `[E]`. |
| **4. Matched-Box Line CER (CER fim a fim por linha)** | CER apenas das linhas que o detector encontrou (pareadas por IoU com a referência). | Mostra se as caixas do detector estão apertadas demais (cortando acentos/descendentes como `g, j, p, ç, ã`). |
| **5. Bag-of-Words WER (Invariante à Ordem)** | Taxa de erro de palavras tratando a página como multiconjunto (ignorando a ordem das linhas). | A diferença entre o **WER padrão de página** e o **Bag-of-Words WER** mede exatamente quantos pontos de erro vêm só da **Ordem de Leitura `[E]`**! |
| **6. CER de Diacríticos e Caracteres Especiais PT-BR** | Taxa de acerto específica em `{á, é, í, ó, ú, â, ê, ô, ã, õ, à, ç}` e pontuação/setas. | Detecta se o ajuste fino ou léxico está "alisando" o português para ASCII ou errando acentuação. |
| **7. Taxa de Preservação de Siglas, Abreviações e Fórmulas (Lexical Damage Rate)** | Percentual de tokens fora do dicionário comum (siglas em maiúsculas, abreviações do autor como `p/`, `c/`, `qdo`, `tb`, e máscaras `$...$`) que eram certos na saída óptica e foram **estragados** pelo decodificador/léxico. | Garante que o KenLM (`[D]`) não destrua anotações técnicas de estudo ([EditVeto, arXiv:2611.05539](https://arxiv.org/html/2611.05539v1), nov/2026). |
| **8. Custo Operacional de Pico e P95** | Tempo mediano e P95 por página (s) + RSS de RAM de pico (MB) medidos em processo isolado na CPU i5-8265U (4 threads). | Evita que uma página densa (30 linhas) demore 25 s ou estoure a memória mesmo com média de 9 s. |

---

### C. Estratégia de Dados em Profundidade

#### 1. Como Coletar, Anotar Caixas e Transcrever com o Menor Esforço Humano
O plano original subestimou o trabalho de anotar caixas. O fluxo de menor esforço validado pela literatura ([RefLAM, 2026](https://huggingface.co/papers?q=manual%20annotation); [PPOCRLabel](https://pypi.org/project/PPOCRLabel/); [PorTEXTO](https://arxiv.org/html/2606.19096v1), jun/2026) separa o processo em **3 passos rápidos por página** dentro da ferramenta local `F-DI-13.3`:

1. **Passo 1 — Pré-segmentação assistida de caixas (~1–2 min/página):** O motor atual (`PP-OCRv6 DB small`) gera as caixas iniciais. A interface mostra a foto da página com as caixas sobrepostas; onde o detector perdeu uma linha (os 28% atuais), você apenas arrasta um retângulo (ou clica no início e fim da linha com altura padrão de 80 px). **Regra:** não avance para a transcrição sem que 100% das linhas visíveis tenham caixa.
2. **Passo 2 — Pré-transcrição linha a linha pelo Professor Local (0 min humano; roda em lote na CPU ociosa):** Em vez de pedir ao VLM (`Qwen3-VL-4B` ou `Gemma 4 E2B`) para ler a foto da página inteira de uma vez — onde VLMs se perdem em colunas, pulam linhas e alucinam contexto ([WildHandBench](https://arxiv.org/html/2608.22959v1), ago/2026) —, o script passa **recortes de 1 a 3 linhas por vez** (ou a página com numeração visual das caixas) para o professor local em lote durante a noite.
3. **Passo 3 — Revisão humana focada por linha (~4–8 min/página):** A ferramenta `F-DI-13.3` exibe a imagem da linha recortada logo acima da caixa de texto pré-preenchida pelo professor, destacando em amarelo palavras onde o professor e o motor discordam. Você corrige apenas os erros, envolve fórmulas entre `$...$` e aperta `Enter` para ir à próxima linha.

#### 2. Como o Produto (`CR-F13.1`) Coleta Sem Perder o Alinhamento Linha↔Caixa
Para evitar a falha crítica de alinhamento quando você edita o estudo no Leitorum:
* A interface de revisão pós-digitalização no Leitorum terá um modo **"Conferência Rápida das Linhas"** (onde cada linha lida ainda está ligada ao seu `line_id` e `bbox`).
* Quando você corrige uma linha ali, ela recebe a flag `alignment_confidence: exact_human_line`.
* Se você preferir editar o texto livremente como documento corrido depois, o exportador `CR-F13.2` roda um alinhamento de programação dinâmica (Needleman-Wunsch por linha) entre o texto editado e as linhas originais: **só exporta para treino as linhas cujo alinhamento tiver similaridade de borda ≥ 90%**, descartando trechos reescritos ou reordenados pelo usuário para nunca ensinar rótulo trocado ao CTC.

#### 3. Protocolo de Qualidade da Referência (Duas Passadas e Auditoria)
* **Para `frozen-test-v3` (20 páginas) e `dev-val` (10 páginas):** Obrigatórias **duas passadas humanas independentes** em dias diferentes (Passada 1: ajuste de caixas + correção do rascunho do professor linha a linha; Passada 2: conferência cega lendo a foto do caderno contra o texto final, verificando acentos, pontuação, maiúsculas/minúsculas e tags `$...$`). Mede-se o **CER entre Passada 1 e Passada 2**: esse número (tipicamente ~0,5% a 1,5%) é o **Piso de Ruído Humano (Human Noise Floor)** do projeto — nenhum modelo poderá ser cobrado além disso.
* **Para `dev-train` (páginas de treino):** Uma única passada humana corrigindo o rascunho do professor, com **auditoria por amostragem de 10% das linhas** a cada lote de 25 páginas (se o erro de anotação na amostra passar de 2% de CER, o lote é revisado).

#### 4. Curva Planejada de Dados e Degraus de Ganho Esperados

| Degrau do Banco | Composição Exata de Páginas | Linhas Reais Estimadas (~19/pág) | O que desbloqueia | Ganho esperado (Baseado em EXP-018 e Literatura) |
| :--- | :--- | :--- | :--- | :--- |
| **Degrau 0 (Hoje)** | 20 `frozen-test` (v2 sem caixas) + 31 `dev` (só texto bruto do motor) | 0 linhas com caixa+verdade | Nada de treino; apenas diagnóstico | CER 56% / WER 90% **[Fato — Projeto]** |
| **Degrau 1 (Mínimo Viável)** | 20 `frozen-test-v3` (com caixas + 2 passadas) + 10 `dev-val` (com caixas + 2 passadas) + **21 `dev-train`** (as restantes das 31 atuais, com caixas + 1 passada) | ~400 linhas de treino + ~190 de validação | Calibração limpa de escala/detector (`EXP-030`) + 1º *fine-tuning* CTC sem precisar digitalizar páginas novas! | Queda inicial forte (estimado 56% → ~30–35% CER **[A medir]**; literatura aponta ganho já com 40–80 linhas em [arXiv:2609.20064](https://arxiv.org/pdf/2609.20064), set/2026) |
| **Degrau 2 (Meta v0.14)** | +29 páginas novas do produto/ferramenta → **50 `dev-train`** + 10 `dev-val` + 20 `frozen-test-v3` | ~950 linhas de treino | Ajuste fino sólido do leitor (`EXP-033/034`) e do detector (`EXP-032`) | ~88% do ganho assintótico de *fine-tuning* (**[Fato — Projeto, EXP-018]**); meta CER ≤ 25–30% |
| **Degrau 3 (Meta v0.15)** | +60 páginas novas → **100 `dev-train`** + 10 `dev-val` + 20 `frozen-test-v3` + **10 `drift-test-1`** | ~1.900 linhas de treino | Leitor v2 + KenLM calibrado + 1ª medição de deriva temporal | Estabilização de vocabulário e acentuação; meta CER ≤ 15–20% |
| **Degrau 4 (Portão MP)** | +50 páginas novas → **150 `dev-train`** + 10 `dev-val` + 20 `frozen-test-v3` + 10 `drift-test-1` | ~2.850 linhas de treino | Ultrapassa o limiar de colapso de 110 páginas ([Oxford DSH](https://academic.oup.com/dsh/article/41/3/1365/8666109), mai/2026); habilita treino do zero (`MP-2`) | Permite testar CRNN/CTC próprio do zero sem colapso em 66% das runs |

*(Nota crítica sobre o Degrau 1: Ao dividir as 31 páginas já existentes em `10 dev-val + 21 dev-train`, você consegue rodar o primeiro ciclo completo de melhoria sem bloquear o projeto esperando digitalizar 19 páginas novas!)*

#### 5. Dados Sintéticos em Português: Como Gerar, Como Validar e Quando Parar
O `EXP-021` provou que degradar digitalizações não ensina o modelo a ler fotos **[Fato — Projeto]**. A literatura recente ([UniLipi, arXiv:2608.28195](https://arxiv.org/html/2608.28195v1), ago/2026; [DiffLine, jul/2026](https://www.researchgate.net/publication/410838313_Handwritten_Text_Recognition_for_Historical_Latin_Manuscripts_via_Model_Adaptation_and_Synthetic_Data_Augmentation_Handwritten_Text_Recognition_for_Historical_LatinM_M_Trusca_et_al)) mostra por que e como fazer certo:
* **Para que serve o sintético:** Não serve para ensinar a caligrafia do autor (fontes não imitam suas ligações cursivas); serve para **ensinar ortografia, encontros consonantais, acentuação (`ç, ã, õ, ê, í`) e vocabulário técnico do português** ao decodificador CTC antes ou junto das páginas reais.
* **Como gerar localmente em CPU:**
  1. Extrair frases reais de cadernos/textos de estudo do autor (sem usar textos das páginas de teste!) + corpus público PT-BR (Wikipédia/livros em domínio público), garantindo cobertura de todas as letras acentuadas, números e abreviações (`p/`, `q/`, `obs:`, `=>`, `->`).
  2. Selecionar 15 a 25 fontes manuscritas/cursivas sob licença **SIL Open Font License (OFL)** que suportem glifos latinos acentuados completos.
  3. **Fundo real, não fundo sintético artificial:** Recortar faixas de **papel pautado vazio real** das próprias fotos de desenvolvimento do caderno (com a iluminação, sombra e textura reais da câmera do seu celular) e renderizar o texto sobre elas com leve transformação afim (*shear* de inclinação ±8°, variação de espessura de traço por erosão/dilatação e *alpha blending* da tinta).
* **Protocolo de mistura (evita *catastrophic forgetting* da letra real):**
  * **Nunca** misturar 100.000 linhas sintéticas direto num batch simples com 400 linhas reais (o gradiente seria 99,6% dominado pelas fontes tipográficas).
  * **Regra de duas fases ou amostragem balanceada:** Fase 1 = pré-ajuste no sintético (ensina PT-BR); Fase 2 = ajuste fino em **80% linhas reais do autor + 20% linhas sintéticas** por época (o sintético entra apenas como regularizador de vocabulário).
* **Quando parar de usar sintético:** Quando o *Oracle-Box Line CER* no `dev-val` com `100% real` igualar ou superar o treino com `80% real + 20% sintético` (tipicamente acima de 100–150 páginas reais para um único autor).

---

### D. Roadmap por Versões Mais Granular (Incluindo Versões de Consolidação)

Em vez de 4 blocos monolíticos onde falhas de referência ou de ambiente travam tudo, o roadmap passa a ter **6 versões sequenciais curtas + 2 marcos de consolidação embutidos**, seguidos pelo **Roadmap Paralelo MP**.

#### Visão Geral das Versões

| Versão | Tema Central | Métrica-Alvo Principal (`frozen-test-v3`) | Critério de Saída |
| :--- | :--- | :--- | :--- |
| **`0.12.9` (Zero)** | **Régua Limpa e Diagnóstico com Fotos** | Referência `v3` auditada (2 passadas + caixas); 8 métricas ativas no harness | Relatório decomposto gerado nas 20 págs `v3` e nas 10 `dev-val`; zero vazamento validado por teste automatizado |
| **`0.13`** | **Enxergar a Página Inteira (Cobertura + Banco Base)** | `Line Recall (IoU ≥ 0,5) ≥ 92%`; palavras omitidas ≤ 10%; `False Positive Boxes ≤ 5%`; 0 págs < 85% | M1 atingido no `frozen-test-v3` (calibrado apenas no `dev-val`) + Degrau 1 de dados pronto (21 `dev-train` + 10 `dev-val`) |
| **`0.14`** | **Ler Certo v1 (Primeiro Leitor Nosso em CPU)** | `CER de página ≤ 30%`, `WER ≤ 65%`, `Oracle-Box Line CER ≤ 22%` | M2 atingido com pesos nossos no motor (≤ 10 s/pág, ≤ 1,5 GB RAM) + Banco expandido para Degrau 2 (50 `dev-train`) |
| **`0.14.5`** | **Consolidação I (Reprodutibilidade, Exportador e Dívida Técnica)** | Tempo de build/treino automatizado em 1 comando; cobertura de testes do pipeline ≥ 90%; zero regressão de CER/latência | Pipeline de treino, exportação ONNX e coleta pelo Leitorum (`CR-F13.1/13.2`) rodando sem intervenção manual |
| **`0.15`** | **Ler Certo v2 + Decodificação Léxica Segura + Ordem** | `CER de página ≤ 15–20%`, `WER ≤ 45%`, `Lexical Damage Rate ≤ 1%` | M3 atingido no `frozen-test-v3` e diferença ≤ 5 p.p. no `drift-test-1` (100–150 `dev-train`) |
| **`0.16`** | **Fórmulas Matemáticas e Zonas de Caderno** | `CER em fórmulas ≤ 35%`, `Valid LaTeX Compile Rate ≥ 85%`, sem piorar texto comum em > 1 p.p. | M4 atingido; contrato `LDF 2.1` homologado por CR e ADR |
| **`MP` (Paralelo)** | **Modelos Próprios do Zero (Independência Total)** | Modelo `(a)` próprio ≤ CER do modelo `(b)` ajustado no `frozen-test-v3` e no `drift-test` | M5 atingido: substituição definitiva de pesos herdados de terceiros |

---

#### Detalhamento Granular por Versão

##### Versão `0.12.9` (Épico Zero) — Régua Limpa, Divisão `dev-val` e Origem do Erro
* **Hipótese central:** Separar o erro atual (56% CER) entre falha de detecção, erro de escala, erro de ordem de leitura e erro óptico do reconhecedor revelará exatamente quanto podemos ganhar sem trocar de arquitetura.

| ID | Tipo | Descrição e Hipótese Falseável | Métrica e Critério de Aceite | Critério de Abandono | Depende de | GPU? | Dados novos exigidos |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **F-DI-12.1** | Utilitário | **Ferramenta de Anotação de Caixas e Linhas (evolução do harness EXP-027):** permite ajustar/criar *bounding boxes* de linha na foto, alinhar texto por `line_id`, marcar `$...$` e exportar JSON com hash SHA-256. | Exportar 1 página completa em ≤ 10 min com validação de schema. | — | Fotos locais | Não | — |
| **EXP-028A** | Experimento / Dados | **Auditoria de 2ª Passada e Recongelamento (`frozen-test-v3` + `dev-val`):** Anotar caixas reais e fazer 2ª passada humana linha a linha nas **20 páginas de teste** e em **10 páginas sorteadas de dev (`dev-val`)**. *Hipótese:* a referência v2 do Gemini tinha ≥ 2% de divergência ou falta de quebras de linha que distorciam o CER. | Gerar `splits/test-manifest-v3.json` (20 págs) e `splits/dev-val-manifest.json` (10 págs) com 100% das linhas com caixa e texto conferido em 2 passadas. | — | `F-DI-12.1` + 30 fotos locais | Não | ~3 a 4 horas do autor (único esforço manual imediato) |
| **F-DI-12.2** | Infra de Avaliação | **Harness Gatekeeper v2:** implementa as 8 métricas ortogonais (Line Recall IoU, False Positive Boxes, Oracle-Box CER, Matched-Box CER, Bag-of-Words WER, Diacríticos, Lexical Damage, RAM/s) e trava execução se houver interseção de hashes entre treino e teste/val. | Relatório reproduzível com semente fixa em < 3 min para as 20 páginas. | — | `EXP-028A` | Não | — |
| **EXP-028B** | Experimento | **Decomposição Exata do Erro nas 20 páginas (`v3`) e 10 (`dev-val`):** roda o motor atual gravando caixas e compara com `Oracle-Box CER` (usando as caixas perfeitas humanas). *Hipótese:* pelo menos 10 pontos percentuais do CER de página (56%) vêm de caixas perdidas/cortadas e ordem, não do reconhecedor. | Produzir tabela exata: `% erro detecção`, `% erro corte de caixa`, `% erro ordem`, `% erro reconhecedor puro`. | — | `F-DI-12.2` | Não | — |
| **EXP-029** | Experimento | **Benchmark de Professores VLMs Locais em CPU (Página Inteira vs. Linha Recortada):** testar `Qwen3-VL-4B` (Q4_K_M), `GLM-OCR` (0,9B, MIT) e `Gemma 4 E2B` (Apache 2.0) no `dev-val` (10 págs) em dois modos: (1) página inteira e (2) linhas recortadas (lotes de 1–3 linhas). *Hipótese:* rodar o VLM em linhas recortadas reduz alucinações/omissões em ≥ 30% e usa menos RAM de pico do que página inteira. | Escolher o Professor Oficial que tiver menor CER no `dev-val` cabendo em **≤ 5,0 GB de RAM** na CPU i5-8265U sem swap. | Abandonar qualquer VLM que passe de 5,2 GB de RAM, degenere em > 5% das linhas ou demore > 120 s/página. | `F-DI-12.2`; cópias e hashes no registry | Não | — |

* **Critério de saída da `0.12.9`:** ADR registrando a decomposição real dos 56% de CER, o `frozen-test-v3` trancado por hash, o `dev-val` pronto e o Professor Local escolhido.
* **Plano B da `0.12.9`:** Se todos os VLMs locais (até 0,9B–2B) forem lentos demais ou ruins em CPU no `EXP-029`, o pré-rascunho das páginas de treino passa a usar o próprio motor atual (e, a partir da `0.14`, o leitor v1 ajustado em loop iterativo ao estilo *eScriptorium*, onde cada 5 páginas corrigidas retreinam o leitor para ajudar nas próximas 10).

---

##### Versão `0.13` — Enxergar a Página Inteira (Cobertura M1) e Fechar o Degrau 1 de Dados
* **Hipótese central:** A maior parte das 7 páginas com 30–67% de cobertura sofre de limiares conservadores do detector `PP-OCRv6 DB small` (`box_thresh`, `unclip_ratio`), resolução de entrada do detector ou iluminação desigual, podendo atingir `Line Recall ≥ 92%` com calibração no `dev-val` ou ajuste fino leve.

| ID | Tipo | Descrição e Hipótese Falseável | Métrica e Critério de Aceite | Critério de Abandono | Depende de | GPU? | Dados novos exigidos |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-030A** | Experimento (Novo) | **Ablação de Hiperparâmetros do Detector DB e Resolução de Entrada (Sem Treino):** variar no `dev-val` a resolução máxima do detector (`960`, `1280`, `1536`), `det_db_thresh` (`0.2` a `0.4`), `det_db_box_thresh` (`0.3` a `0.6`), `det_db_unclip_ratio` (`1.5` a `2.5`) e regras de fusão de fragmentos. *Hipótese:* metade das linhas perdidas já tem resposta no mapa de probabilidade do DB, mas é descartada pelo limiar padrão de texto impresso. | Subir `Line Recall (IoU ≥ 0,5)` no `dev-val` para **≥ 90%** mantendo `False Positive Boxes ≤ 5%` e tempo de detecção ≤ 2,5 s/pág. | Se aumentar falsos positivos para > 10% ou degradar o CER final. | `EXP-028B` | Não | — |
| **EXP-030B** | Experimento | **Preparação Fotométrica/Geométrica Leve e Escala da Linha:** testar no `dev-val` (1) normalização de iluminação por divisão morfológica (OpenCV), (2) altura do recorte da linha (`48 px` nativo do PP-OCR vs `64 px` vs `80 px` atual) e `padding` vertical/horizontal. *Hipótese:* o reconhecedor `PP-OCRv6` foi treinado com altura 48 px; redimensionar linhas para 80 px (ou cortar descendentes sem margem vertical) está degradando o CER óptico. | Reduzir `Matched-Box Line CER` em **≥ 3 p.p.** no `dev-val` com custo ≤ 0,3 s/pág. `UVDoc` (8M, MIT) só é testado se a curvatura da folha for causa comprovada no `EXP-028B`. | Abandonar qualquer filtro (especialmente binarização) que apague traços fracos em ≥ 1 página do `dev-val`. | `EXP-028B` | Não | — |
| **Dados-13.1** | Dados | **Fechamento do Degrau 1 (21 páginas `dev-train`):** usar `F-DI-12.1` + Professor escolhido no `EXP-029` para anotar caixas e revisar linha a linha as **21 páginas restantes** das 31 páginas de desenvolvimento já existentes no projeto. | 21 páginas `dev-train` completas com caixas e texto revisado (totalizando 31 págs de dev + 20 de teste = 51 págs 100% estruturadas). | — | `EXP-029`, `F-DI-12.1` | Não | ~2,5 a 3,5 h do autor sobre páginas que já existem! |
| **EXP-032** | Experimento (Condicional) | **Ajuste Fino do Detector `PP-OCRv6 DB small`:** executado **somente se** `EXP-030A + 030B` não atingirem M1 no `dev-val`. Treinar com **GNHK** (CC-BY-4.0) + **21 páginas `dev-train`**, validando no `dev-val`. | `Line Recall ≥ 92%` no `dev-val` e palavras omitidas ≤ 10%. | Se exigir mais de 2 h de GPU ou não superar `EXP-030A` em ≥ 3 p.p. de recall. | `EXP-030A`, `Dados-13.1` | **Sim (0,5–2 h GPU)** ou **Plano B CPU** abaixo | — |
| **CR-F13.5** | Produto (Motor) | **Atualização do Pipeline de Detecção e Escala no Motor:** aplica no `config.json` os parâmetros (e pesos, se `EXP-032` rodar) vencedores após validação única no `frozen-test-v3`. | Atingir **M1** no `frozen-test-v3` em ≤ 8 s/pág e ≤ 1 GB RAM. | — | `EXP-030A/B` (e `032` se usado), ADR | Não | — |

* **Critério de saída da `0.13`:** M1 atingido no `frozen-test-v3` (`Line Recall ≥ 92%`, palavras omitidas ≤ 10%, 0 páginas < 85% do tamanho sem inflar `False Positive Boxes > 5%`) + Degrau 1 de dados concluído (21 `dev-train` + 10 `dev-val` prontas).
* **Plano B da `0.13` (se `EXP-030A/B` não atingir M1 e o dono recusar GPU na nuvem para `EXP-032`):** Implementar **Detecção em Duas Escalas (Multi-scale Tiling CPU)** + **Resgate por Projeção Horizontal de Tinta (Ink Profile Fallback)**: nas faixas horizontais da página onde o detector DB deixou um buraco maior que $1,6 \times \text{altura mediana da linha}$ mas há densidade de pixels escuros de caneta/lápis, o algoritmo gera uma caixa candidata suplementar. Roda 100% em CPU (< 0,2 s) sem precisar de treino em GPU.

---

##### Versão `0.14` — Ler Certo v1: Primeiro Leitor Ajustado (Pesos Nossos em CPU)
* **Hipótese central:** Ajustar o reconhecedor CTC (`PP-OCRv6 rec small`) nas linhas reais do autor (começando já com as 21 páginas do `Dados-13.1` e subindo para 50 páginas no `Dados-14.1`) reduzirá o CER de página de 56% para ≤ 30% rodando treino 100% na CPU doméstica.

| ID | Tipo | Descrição e Hipótese Falseável | Métrica e Critério de Aceite | Critério de Abandono | Depende de | GPU? | Dados novos exigidos |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-033A** | Experimento | **Ajuste Fino Imediato do `PP-OCRv6 rec small` com 21 páginas (`Dados-13.1`) em CPU:** rodar o procedimento do `EXP-014/018` nas ~400 linhas reais de `dev-train`, selecionando o melhor checkpoint pelo `dev-val` (10 págs). *Hipótese:* 21 páginas reais do próprio autor já derrubam o `Oracle-Box Line CER` em ≥ 15 p.p. | Reduzir CER no `dev-val` de ~54% para **≤ 35%** em ≤ 4 h de treino em CPU. | Se não houver queda de pelo menos 10 p.p. (indica bug no dicionário de caracteres PT-BR, normalização ou *learning rate* congelando camadas erradas). | `Dados-13.1`, `0.13` | **Não (CPU 1–4 h)** | **Zero páginas novas!** (Usa as 21 já prontas) |
| **Dados-14.1** | Dados | **Expansão para o Degrau 2 (de 21 para 50 páginas `dev-train`):** digitalizar e revisar **+29 páginas novas** de caderno usando o leitor do `EXP-033A` ou o Professor Local para pré-preencher. | Banco `dev-train` com **50 páginas** (~950 linhas) + manifesto SHA-256. | — | `EXP-033A` | Não | +29 páginas novas do autor (~3 a 5 h distribuídas) |
| **EXP-033B** | Experimento | **Curva de Aprendizado `21 → 35 → 50` páginas no `PP-OCRv6 rec small` (CPU):** medir ganho marginal por lote de páginas no `dev-val` e avaliar o vencedor no `frozen-test-v3`. *Hipótese:* 50 páginas atingem **M2** (`CER ≤ 30%`, `WER ≤ 65%`). | Atingir **M2** (`CER ≤ 30%`, `WER ≤ 65%`) no `frozen-test-v3`. | — | `Dados-14.1` | **Não (CPU 2–6 h)** | — |
| **EXP-034** | Experimento | **Disputa de Arquitetura Leve (`PP-OCRv6 small` 5,2M vs `Kraken` 2M vs `PyLaia` 9,5M):** testar se uma arquitetura CTC clássica (`PyLaia`/`Kraken`, via WSL2 se o build Windows falhar) supera a rede móvel do `PP-OCRv6 small` nas mesmas 50 páginas. *Nota:* `PP-OCRv6 medium` (19M) fica restrito a teste de 1 época em CPU ou GPU opcional. | Só trocar `PP-OCRv6 small` se o desafiante reduzir o CER no `dev-val` em **≥ 2,5 p.p.** mantendo inferência ONNX ≤ 5 s/pág em CPU. | Abandonar imediatamente se o build ou a exportação para ONNX no Windows 11 exigir gambiarra frágil. | `EXP-033B` | Não | — |
| **EXP-035** | Experimento | **Suplemento Sintético PT-BR em Papel Real do Caderno:** gerar 20.000 linhas sintéticas renderizadas com 20 fontes cursivas OFL sobre recortes de pauta vazia das fotos de `dev-train`. Testar (1) pré-treino no sintético → fine-tune nas 50 págs reais vs (2) mistura 80% real + 20% sintético. *Hipótese:* reduz erros em palavras raras e diacríticos (`ç, ã, õ, ê`) em ≥ 2 p.p. de CER. | Ganho líquido **≥ 1,5 p.p. de CER** e **≥ 3 p.p. no CER de Diacríticos** no `dev-val` contra `EXP-033B` puro. | Se empatar ou piorar o CER nas linhas reais, **desligar o sintético** para o modelo ajustado e guardá-lo apenas para o treino do zero (`MP-2`). | `EXP-033B` | Não (geração 1 h CPU; treino 3–8 h CPU) | Corpus PT-BR livre + 20 fontes OFL |
| **CR-F14.1 / 14.2** | Produto | **Promoção do Leitor v1 ao Motor + Indicador de Modelo no Leitorum:** registra os pesos nossos no registry com hash, calibra limiar de confiança no `dev-val` e exibe na UI qual versão do leitor transcreveu a página. | Motor rodando em produção local com `CER ≤ 30%`, ≤ 10 s/pág e ≤ 1,5 GB RAM. | — | `EXP-033B/034/035`, ADR | Não | — |

* **Critério de saída da `0.14`:** M2 atingido no `frozen-test-v3` (`CER ≤ 30%`, `WER ≤ 65%`).
* **Plano B da `0.14`:** Se com 50 páginas o CER cair para a faixa de **30,1% a 35%** (ganho real > 20 pontos sobre os 56% iniciais, mas raspando na meta), **não bloqueie a promoção do modelo para o produto!** Promova o leitor v1 para você já se beneficiar de um rascunho muito melhor no uso diário, e abra um experimento de diagnóstico (`EXP-033C`: análise das 100 linhas de maior erro no `dev-val` para checar se o gargalo residual é letra miúda, contraste, vocabulário ou linhas mistas com fórmula).

---

##### Versão `0.14.5` — Consolidação I: Coleta pelo Produto, Reprodutibilidade e Dívida Técnica
* **Por que esta versão existe (ausente no plano original):** Depois de mexer em pré-processamento, detector, escala e leitor nas versões `0.12.9` a `0.14`, o código experimental acumula scripts avulsos, e você precisará coletar mais 50 a 100 páginas para a `0.15`. Fazer isso sem automatizar a coleta linha a linha dentro do Leitorum e sem um pipeline de treino de 1 clique causará exaustão manual.

| ID | Tipo | Descrição | Critério de Aceite | Depende de | GPU? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CR-F13.1 (Revisado)** | Produto (Leitorum) | **Modo "Conferência Linha a Linha" + Persistência Vinculada (`line_id`):** na tela de revisão da digitalização, permite corrigir cada linha vendo o recorte da caixa acima dela antes de converter para texto livre do fichamento, salvando `human_corrections` com vínculo exato `line_id ↔ bbox`. | 100% das linhas corrigidas nesse modo preservam pareamento 1-para-1 com sua caixa original; opção clara de *opt-in / opt-out* de coleta. | `0.14` | Não |
| **CR-F13.2 (Revisado)** | Produto (Leitorum) | **Exportador Seguro com Alinhador e Bloqueio de Teste:** exporta pacotes de treino para pasta fora do Git; recusa hashes de `test-manifest-v3.json`, `dev-val-manifest.json` e `drift-manifest.json`; para páginas editadas em texto livre, só exporta linhas com alinhamento ≥ 90%. | Teste automatizado provando que 0 linhas de teste/validação ou linhas desalinhadas vazam no pacote exportado. | `CR-F13.1` | Não |
| **F-DI-14.5** | Engenharia / Consolidação | **Pipeline Reprodutível de 1 Comando (`train_and_eval.py`):** unifica preparação do pacote, treino retomável por época (checkpoint automático a cada 15 min para suportar interrupção em CPU), exportação ONNX e geração do Relatório Gatekeeper. | Rodar fim a fim em um único comando com semente determinística (variância entre 2 runs com mesma semente = 0,0%). | `0.14` | Não |

---

##### Versão `0.15` — Ler Certo v2, Decodificação com Léxico Seguro e Ordem de Leitura
* **Hipótese central:** Dobrar o banco de treino para 100–150 páginas reais + acoplar decodificação CTC em *beam search* com modelo de linguagem `KenLM` (protegido contra dano em siglas/fórmulas) e ordenação geométrica de colunas/margens levará o CER para a faixa de **15–20%**.

| ID | Tipo | Descrição e Hipótese Falseável | Métrica e Critério de Aceite | Critério de Abandono | Depende de | GPU? | Dados novos exigidos |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dados-15.1** | Dados | **Degrau 3 (100 a 150 páginas `dev-train`) + 1º Teste de Deriva (`drift-test-1`):** coletar pelo produto (`CR-F13.1`) e pela ferramenta. **Antes** de usar as novas páginas no treino, sortear 10 páginas novas para congelar como `drift-test-1`. | 100–150 páginas `dev-train` + 10 `drift-test-1` com hashes registrados. | — | `0.14.5` | Não | +60 a 110 páginas do uso normal do produto |
| **EXP-036** | Experimento | **Leitor v2 (`50 → 100 → 150` páginas):** treinar o reconhecedor vencedor da `0.14` na curva de 100 e 150 páginas, medindo no `dev-val`, `frozen-test-v3` e `drift-test-1`. *Hipótese:* reduz o `Oracle-Box Line CER` para **≤ 15%**. | Redução contínua de CER sem abrir distância > 5 p.p. entre `frozen-test-v3` e `drift-test-1`. | — | `Dados-15.1` | Não (CPU 4–10 h, ou GPU opcional 30 min) | — |
| **EXP-037** | Experimento | **Decodificação CTC com `KenLM` + Glossário do Autor + Gate de Proteção:** construir modelo *n-gram* ARPA (usando corpus PT-BR livre + notas Markdown dos estudos anteriores do autor no Leitorum, excluindo páginas de teste!) e decodificar via *prefix beam search* (`pyctcdecode` Apache 2.0 / C++). **Regra do Gate:** se o caminho guloso (greedy) do CTC tiver confiança > 0,92 ou contiver dígitos, símbolos matemáticos, siglas em maiúsculas ou abreviações do glossário pessoal (`p/`, `c/`, `tb`, `qdo`), o léxico não altera o token. *Hipótese:* reduz WER em ≥ 8 p.p. e CER em ≥ 1,5 p.p. com `Lexical Damage Rate ≤ 1%`. | Ganho líquido de CER/WER no `dev-val` **E** `Lexical Damage Rate ≤ 1%` em siglas, abreviações e fórmulas. | **Abandonar/desligar** se `Lexical Damage Rate > 2%` ou se o ganho de CER for < 0,5 p.p. | `EXP-036` (só roda se CER óptico < 22%) | Não (treino KenLM: 5 min CPU; inferência +0,3 s/pág) | Corpus de notas de estudo do autor (já existe no Leitorum) |
| **EXP-038** | Experimento | **Ordem de Leitura e Zonas Geométricas em Caderno:** implementar ordenador por grafo topológico sobre as caixas (detectando separadores verticais de 2 colunas, indentação de listas e notas de margem curtas nas bordas laterais) e medir pela queda na diferença entre `WER de página` e `Bag-of-Words WER` no `dev-val`. | Reduzir a penalidade de ordem de leitura em **≥ 50%** no `dev-val` sem piorar páginas de coluna única. | Se regras geométricas falharem em notas de margem, manter ordenação simples de cima para baixo e adiar zonas para classificador supervisionado. | `EXP-028B` | Não | — |
| **CR-F15.1 / 15.2** | Produto | **Promoção do Leitor v2 + Decodificador + Ordenador ao Motor e Editor.** | **M3** atingido (`CER ≤ 15–20%`, `WER ≤ 45%`) no `frozen-test-v3` e deriva ≤ 5 p.p. no `drift-test-1`. | — | `EXP-036/037/038`, ADR | Não | — |

* **Critério de saída da `0.15`:** M3 atingido no `frozen-test-v3` e estabilidade comprovada no `drift-test-1`.
* **Plano B da `0.15`:** Se o `drift-test-1` mostrar queda > 5 p.p. em relação ao `frozen-test-v3` (sinal de que o modelo decorou o estilo/caneta das primeiras páginas), aplicar **aumento de dados fotométrico forte** (variação de contraste, espessura morfológica de caneta e inclinação) e **regularização por dropout / mistura de 20% sintético**, além de incluir 20 páginas da época recente no `dev-train`.

---

##### Versão `0.16` — Fórmulas Matemáticas e Evolução do Contrato `LDF 2.1`
* **Hipótese central:** Como 150 páginas do autor terão apenas ~150 a 250 fórmulas (insuficiente para ajustar um transformer de 298M sozinho), a combinação de um **classificador leve de trecho matemático** + **TexTeller pré-treinado em ONNX INT8** (ou ajuste fino misturando `HME100K` Apache 2.0 com os ~200 recortes do autor) converterá blocos matemáticos para LaTeX compilável sem degradar o texto comum.

| ID | Tipo | Descrição e Hipótese Falseável | Métrica e Critério de Aceite | Critério de Abandono | Depende de | GPU? | Dados novos exigidos |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-040 (Reordenado: vem ANTES do 039!)** | Experimento | **Roteador "Isto é Fórmula vs. Texto Comum" nas Linhas/Blocos:** testar no `dev-val` (1) detecção por `Pix2Text MFD 1.5` (MIT) / `PP-DocLayout` (Apache 2.0) na página vs (2) gatilho pós-CTC (quando a linha lida pelo CTC tiver alta densidade de símbolos `=, +, -, /, ^, (, )` ou entropia de caracteres alta, envia o recorte para o leitor de fórmulas). *Hipótese:* o gatilho pós-CTC + layout tem < 2% de falso positivo em texto comum, enquanto detectores MFD prontos erram em manuscrito. | `Precision ≥ 90%` e `Recall ≥ 80%` na identificação de trechos com fórmula no `dev-val`, com **≤ 2% de texto comum enviado por engano ao leitor de fórmula**. | Se o detector enviar > 5% de texto comum para o motor de LaTeX (o que destruiria frases em português). | `0.15` | Não | Marcações `$...$` já existentes em `dev-val` e `dev-train` |
| **EXP-039** | Experimento | **Avaliação de Motores de Fórmula em CPU (`TexTeller` ONNX INT8 vs `UniMERNet` ONNX vs Professor VLM pontual):** medir nos recortes de fórmula de `dev-val` o `CER de Fórmula`, `ExpRate` e **`Valid LaTeX Compile Rate` (taxa de equações que compilam sem erro no KaTeX)**. Se necessário e autorizado pelo dono, testar *fine-tuning* LoRA do `TexTeller` usando `HME100K` (Apache 2.0) + os ~150–250 recortes de fórmula de `dev-train`. | `CER em fórmulas ≤ 40%` **E** `Valid LaTeX Compile Rate ≥ 85%`, adicionando no máximo **+2,5 s** nas páginas que tiverem fórmula e **≤ 700 MB RAM** extras (carregado sob demanda / *lazy load*). | Se estourar o teto de 1,5 GB de RAM do motor ou piorar o CER do texto comum em > 1,0 p.p., manter fórmulas apenas no modo "Revisão Assistida Offline" (fora do motor de tempo real). | `EXP-040` | Inferência: Não.<br>Ajuste fino opcional: **Sim (2–4 h GPU)** | ~150–250 recortes de fórmulas extraídos automaticamente das 150 págs de `dev-train` |
| **CR-LDF-2.1** | Governança | **Change Request + ADR para o Contrato `LDF 2.1` (versão MINOR):** adiciona campos opcionais retrocompatíveis `math_spans` (com `latex`, `compile_valid`, `bbox`) e `zone_type` (`body`, `margin_note`, `list_item`). | Aprovado apenas **depois** que `EXP-038`, `EXP-040` e `EXP-039` provarem ganho real. | — | `EXP-038`, `EXP-039`, `EXP-040` | Não | — |
| **CR-F16.1** | Produto | **Integração no Motor (Lazy-load ONNX) + Renderização KaTeX no Editor do Leitorum.** | **M4** atingido no `frozen-test-v3`. | — | `CR-LDF-2.1` | Não | — |

*(Observação de auditoria: Note que na tabela acima **invertemos a ordem entre `EXP-040` e `EXP-039`** em relação ao plano original — primeiro você descobre se consegue detectar onde está a fórmula sem estragar o texto comum (`EXP-040`), e só depois integra o modelo de LaTeX (`EXP-039`), além de exigir que o `CR-LDF-2.1` só mude o contrato após o experimento dar certo!)*

---

### E. Trajetória de Modelos Próprios em Degraus (Por Componente, Custo Honesto e Riscos)

O objetivo de longo prazo é ter **arquitetura, código de treino, dados e pesos 100% sob controle do dono**, sem herdar pesos pré-treinados de terceiros no produto final. Porém, cada componente tem uma física de dados diferente:

#### Tabela de Degraus por Componente (`(c) Externo → (b) Ajustado → (a) Próprio do Zero`)

| Componente | Degrau 1: Externo `(c)` (Baseline / Professor) | Degrau 2: Ajustado `(b)` (Pesos nossos sobre base aberta) | Degrau 3: Próprio do Zero `(a)` (Código + Pesos 100% nossos) | Custo Honesto de `(a)` (CPU 4c vs GPU Emprestada) | Risco de Colapso em `(a)` e Como Mitigar | Critério Objetivo de Troca `(b) → (a)` (Portão M5) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Decodificador Léxico `[D2]`** | Desligado | N/A | **1º componente 100% próprio (já na `v0.15`):** `KenLM` ARPA + dicionário + regras de proteção treinados do zero nos seus textos. | **CPU:** 5–15 min.<br>**GPU:** 0 h. | Baixo (risco é apenas corrigir siglas por engano, mitigado pelo Gate de Proteção). | Reduzir CER/WER no `frozen-test-v3` e `drift-test` com `Lexical Damage ≤ 1%`. |
| **2. Ordenador de Layout `[E]`** | Ordenação top-down simples | N/A | **2º componente 100% próprio (já na `v0.15`):** algoritmo de grafo geométrico sobre caixas escrito no projeto. | **CPU:** 0 h de treino (algoritmo determinístico). | Nenhum colapso de treino; risco é falhar em setas curvas (mitigado por edição rápida na UI). | Reduzir erro de ordem (`WER - BoW WER`) em ≥ 50% sem regredir páginas simples. |
| **3. Leitor Óptico de Linha `[D1]`** *(Coração do MP)* | `PP-OCRv6 rec small` original + Professor VLM (`Qwen3-VL-4B` / `Gemma 4 E2B`) fora do motor | `PP-OCRv6 rec small` (Apache 2.0) ou `PyLaia` (MIT) ajustado em 50 → 150 páginas (`v0.14`–`v0.15`) | **`MP-2` (`EXP-041`):** Arquitetura **CRNN/CTC compacta própria** (~3M–6M params: Backbone ConvNeXt-Tiny/VGG + BiLSTM 2 camadas + Linear CTC) escrita em PyTorch puro no repositório do projeto. | **Fase 1 (Pré-treino em 200k linhas sintéticas PT-BR + GNHK/READ CC-BY-4.0):**<br>• GPU T4/P100: **4–10 h**<br>• CPU 4c: **~80–150 h** (5–7 dias em background)<br>**Fase 2 (Fine-tune em 150+ págs reais suas):**<br>• GPU: **20–40 min**<br>• CPU 4c: **3–8 h** | **Altíssimo se treinado só nas 150 págs reais** (CTC colapsa para caractere vazio ou decora frases). **Mitigação obrigatória:** Curriculum Learning em 2 fases (Fase 1 sintético + datasets CC-BY-4.0 públicos que não têm dado privado do dono → pode rodar em GPU grátis sem expor cadernos pessoais!; Fase 2 com as 150 páginas privadas do dono → **roda 100% na CPU de casa em 3–8 h!**). | `CER(a) ≤ CER(b) + 0,5 p.p.` no `frozen-test-v3` **E** `CER(a) ≤ CER(b)` no `drift-test-1`, com latência ≤ 5 s/pág e RAM ≤ 500 MB. |
| **4. Detector de Linhas `[B]`** | `PP-OCRv6 DB small` original (Apache 2.0) | `PP-OCRv6 DB small` ajustado em GNHK + 50 págs (`EXP-032`, se necessário) | **`MP-5` (Opcional de longo prazo):** U-Net/DBNet leve (~1,5M params) escrito em PyTorch puro. | **Fase 1 (GNHK CC-BY-4.0 + sintético de páginas):** GPU **4–8 h** (sem dados privados!).<br>**Fase 2 (150–300 págs suas):** GPU 1 h ou CPU ~12–24 h (em resolução reduzida 640×640). | Médio (perder linhas curtas de margem). Mitigado mantendo o Resgate por Perfil de Tinta. | `Line Recall(a) ≥ Line Recall(b)` e `False Positives(a) ≤ False Positives(b)` no teste v3 e deriva. |
| **5. Fórmulas `[F]`** | `TexTeller` (CC BY 4.0) em ONNX | `TexTeller` ajustado com `HME100K` (Apache 2.0) + recortes do autor | **Fora de escopo para 1 autor** (exige >100k–1M pares e centenas de horas de GPU; caso deseje no futuro, pré-treinar encoder-decoder leve apenas em `HME100K` + sintético LaTeX na nuvem sem dados privados). | Inviável em CPU (>500 h). Em GPU: ~20–60 h só em dados públicos (`HME100K` + sintético). | Alto em matrizes/frações aninhadas. | Só substituir `TexTeller` se atingir `Valid LaTeX Compile Rate ≥ 85%` e mesmo `ExpRate`. |

> **Insight Estratégico Decisivo para Privacidade + GPU no `MP-2` (que o plano original não percebeu):**  
> O plano original assumia que usar GPU emprestada (Kaggle/Colab) para treinar o modelo próprio do zero (`MP-2`) obrigaria você a **enviar suas páginas pessoais de caderno para a nuvem**. **Isso não é verdade se você separar o treino em duas fases!**  
> 1. **Fase Pesada (95% do custo computacional = 200.000 linhas sintéticas PT-BR + GNHK/READ sob CC-BY-4.0):** Contém **zero páginas pessoais suas** — apenas texto público renderizado com fontes livres e datasets abertos. Você pode rodar essa fase gratuitamente numa GPU P100/T4 do Kaggle em **4 a 8 horas com risco zero de privacidade**, baixando para o seu computador o checkpoint base `leitorum-crnn-base-ptbr.pt` (100% seu, código seu, dados públicos/sintéticos).  
> 2. **Fase Leve de Personalização (5% do custo computacional = suas 150 páginas reais de caderno):** Partindo do seu `leitorum-crnn-base-ptbr.pt`, o ajuste final nas suas ~2.850 linhas reais leva apenas **3 a 6 horas na sua própria CPU Intel i5-8265U em casa**!  
> **Resultado:** Você conquista um modelo 100% próprio, treinado do zero sob seu controle, sem esperar semanas de CPU e **sem nunca enviar uma única foto ou linha do seu caderno para fora do seu notebook**.

---

### F. Gestão de Risco (Tabela Completa com Sinais de Alerta e Respostas)

| ID | Risco | Probabilidade | Impacto | Sinal de Alerta Mensurável (Gatilho) | Resposta / Plano de Contingência |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R1** | **Contaminação silenciosa do Teste Congelado por escolhas iterativas** | Alta (se usar o fluxo original) | Crítico (invalida meses de decisões) | Qualquer script de experimento (`EXP-030`, `032`, `033`, `037`) lendo `test-manifest-v3.json` durante busca de hiperparâmetros. | **Bloqueio por código no `F-DI-12.2`:** scripts de calibração/treino só aceitam `dev-val-manifest.json`; o `frozen-test-v3` só pode ser chamado pelo script de fechamento de ADR. |
| **R2** | **Desalinhamento `Caixa ↔ Texto` nas correções salvas pelo Leitorum (`CR-F13.1`)** | Alta | Crítico (corrompe o treino CTC e faz o CER subir com mais páginas) | Taxa de linhas exportadas com diferença de comprimento > 35% em relação à largura da caixa, ou aumento do CER ao treinar com `Dados-15.1`. | **Modo "Conferência Linha a Linha" vinculado por `line_id`** na UI + filtro automático no exportador (`CR-F13.2`) que descarta linhas editadas livremente com similaridade de borda < 90%. |
| **R3** | **Estouro de RAM (> 7,9 GB) ou travamento por swap ao rodar Professor VLM no Windows 11** | Média/Alta | Médio | Uso de RAM do processo `llama-mtmd-cli` / Python passando de **5,2 GB** ou tempo por página > 120 s no `EXP-029`. | Usar modelos menores (`GLM-OCR` 0,9B MIT ou `Gemma 4 E2B` Apache 2.0), rodar inferência sob recortes de 1–3 linhas (menor KV cache e resolução de visão) ou usar o próprio leitor ajustado v1 em loop (*human-in-the-loop*). |
| **R4** | **Ruído numérico visual do `Qwen3-VL` no `llama.cpp` (`mtmd`)** | Média (**[Fato — Literatura]:** [issue #29251](https://github.com/ggml-org/llama.cpp/issues/29251), set/2026) | Médio | `Qwen3-VL-4B` errando palavras legíveis ou exigindo resolução muito alta no `EXP-029`. | Manter `mmproj` em `F16` (nunca quantizar o projetor visual para Q4), passar recortes de blocos/linhas em vez da página inteira espremida, ou escolher `Gemma 4 E2B` / `GLM-OCR` no `EXP-029`. |
| **R5** | **Alucinação semântica do Professor VLM virando "verdade" no banco de treino** | Média (**[Fato — Literatura]:** 63–79% dos erros de VLMs são *Prior-Driven* no [WildHandBench](https://arxiv.org/html/2608.22959v1)) | Alto (ensina o modelo óptico a ler o que não está escrito) | Auditoria de amostragem (10% das linhas de `dev-train`) encontrando > 2% de abreviações do autor trocadas por palavras inteiras pelo VLM e não percebidas na revisão. | Na ferramenta `F-DI-12.1`, destacar em cor forte toda palavra onde o VLM divergir do tamanho esperado da caixa ou onde o motor CTC e o VLM discordarem. |
| **R6** | **Colapso do treino CTC do zero (`MP-2`) ou memorização das matérias atuais (Deriva)** | Alta (se treinar direto em 150 págs de 1 autor) | Alto | Loss CTC estacionada perto de $\ln(V)$ nas primeiras 5 épocas, saída vazia/repetida, ou `CER(drift-test-1) - CER(frozen-test-v3) > 5 p.p.` | **Treino em 2 fases obrigatório:** pré-treino pesado em 200k linhas sintéticas PT-BR + GNHK/READ (CC-BY-4.0) seguido de ajuste fino com *learning rate* baixo nas 150 páginas reais + congelamento das primeiras camadas convolucionais. |
| **R7** | **Incompatibilidade de build de `PyLaia` / `Kraken` no Windows 11 + Python 3.13** | Alta | Baixo/Médio | Mais de 4 horas gastas tentando compilar pacotes C++/PyTorch legados no `EXP-034`. | **Timebox estrito de 4 horas:** se não rodar nativo ou via WSL2 com exportação limpa para `.onnx`, descartar `PyLaia` e manter `PP-OCRv6 rec` (ou PyTorch CRNN puro próprio) como arquitetura padrão. |
| **R8** | **Dano do decodificador léxico (`KenLM`) em siglas, variáveis e fórmulas** | Média | Alto (irrita o usuário em cadernos técnicos de TADS/matemática) | `Lexical Damage Rate > 1%` no `EXP-037`. | Gate de proteção léxica: `beam search` só atua em palavras 100% alfabéticas minúsculas/capitalizadas com confiança óptica moderada (< 0,92), ignorando tokens com números, símbolos ou maiúsculas internas. |
| **R9** | **Incompatibilidade de Licença ou Contaminação de Destilação** | Baixa (com registry ativo) | Crítico (jurídico) | Tentativa de usar `Qwen2.5-VL-3B` (NC), `Gemma 3` (contamina destilação), `DocLayout-YOLO` (AGPL-3.0), `Nougat` (CC-BY-NC) ou `PorTEXTO` (CC-BY-NC). | Lista Negra automatizada no `model-registry.json`: só entram no produto pesos **Apache 2.0, MIT, BSD ou CC-BY-4.0** (com atribuição gerada no `NOTICE.md`). |

---

### G. Portões de Decisão do Dono do Projeto (Decision Gates)

Em cinco momentos exatos ao longo do projeto, o avanço exige uma decisão explícita sua, com todos os números na mesa:

| Portão | Quando ocorre | O que você precisa decidir | Que informação exata você terá em mãos para decidir | Opções e Consequências |
| :--- | :--- | :--- | :--- | :--- |
| **DG-1: Escolha do Professor e Modo de Pré-Anotação** | Fim da `v0.12.9` (após `EXP-028B` e `EXP-029`) | Qual modelo gerará os rascunhos das páginas de desenvolvimento (VLM local em linha, VLM em página, ou o próprio motor iterativo). | Tabela com CER no `dev-val`, RAM de pico (MB), segundos/página no seu i5-8265U e taxa de alucinação de abreviações de `Qwen3-VL-4B`, `Gemma 4 E2B` e `GLM-OCR`. | **(A)** Usar VLM local em lote noturno (melhor rascunho inicial, gasta CPU ociosa); **(B)** Usar ciclo iterativo do próprio leitor CTC a cada 5–10 páginas (instantâneo, zero peso extra). |
| **DG-2: Caminho de Cobertura (`EXP-030` vs `EXP-032` com GPU)** | Meio da `v0.13` (após `EXP-030A/B`) | Se a calibração sem treino (`EXP-030A/B` + Resgate de Tinta) já basta para fechar M1, ou se vale treinar o detector `DB small` (`EXP-032`). | `Line Recall` e `% palavras omitidas` alcançados no `dev-val` apenas com ajuste de limiares/escala/OpenCV. | **(A)** Se Recall ≥ 92%, fechar `0.13` sem treino de detector; **(B)** Se ficar abaixo, decidir entre pré-treinar detector em GNHK na GPU Kaggle + ajuste curto local vs enviar recortes anonimizados das 21 págs de dev para GPU. |
| **DG-3: Promoção do Leitor v1 na `v0.14`** | Fim da `v0.14` (após `EXP-033B/034/035`) | Colocar o primeiro leitor com pesos seus em produção no Leitorum e definir se congela a arquitetura em `PP-OCRv6 rec` ou `PyLaia`. | Relatório Gatekeeper completo no `frozen-test-v3` (CER, WER, Oracle-Box CER, s/pág, RAM) para 21 e 50 páginas. | **(A)** Promover ao motor se CER ≤ 30% (ou se o ganho for ≥ 20 p.p. mesmo ficando em ~31–33%, continuando coleta em produção); **(B)** Segurar promoção se houver regressão em alguma classe. |
| **DG-4: Escopo de Fórmulas no Tempo Real vs. Sob Demanda** | Meio da `v0.16` (após `EXP-040` e `EXP-039`) | Se a conversão para LaTeX roda automaticamente em toda página durante a digitalização ou apenas quando você clicar em "Converter fórmula para LaTeX" no editor. | Precisão do roteador (`EXP-040`), `Valid LaTeX Compile Rate` do `TexTeller` (`EXP-039`), RAM extra (+400–700 MB) e segundos adicionais por página. | **(A)** Automático na digitalização (se falsos positivos ≤ 2% e tempo total ≤ 10 s); **(B)** Botão sob demanda no editor do Leitorum (zero impacto na velocidade e RAM da leitura de texto comum). |
| **DG-5: Estratégia de Treino do Modelo Próprio do Zero (`MP-2`)** | Entrada do `MP-2` (quando o banco atingir 150 págs `dev-train`) | Como executar o pré-treino base do seu modelo próprio (`CRNN/CTC` do zero). | Banco com 150 páginas reais suas + 200k linhas sintéticas PT-BR + resultado do leitor ajustado `(b)` da `v0.15`. | **(A) Híbrido Privacidade Total (Recomendado):** pré-treinar a base em GPU gratuita (Kaggle 4–8 h) usando **apenas dados sintéticos + GNHK/READ públicos**, e fazer o ajuste fino nas suas 150 páginas **100% na sua CPU em casa (3–6 h)**; **(B)** 100% em CPU em casa (5–7 dias em background). |

---

### H. Ordem de Execução Sugerida (Sequência Lógica e Paralelismo, Sem Datas)

```text
FASE 1: FUNDAÇÃO E RÉGUA LIMPA (Bloqueante — nada roda antes disto)
  [1] F-DI-12.1 (Utilitário de caixas + linha a linha)
       │
       ▼
  [2] EXP-028A (Caixas + 2ª passada nas 20 págs frozen-test-v3 e 10 págs dev-val)
       │
       ▼
  [3] F-DI-12.2 (Harness Gatekeeper com as 8 métricas e trava de hashes)
       │
       ├───────────────────────────────────────────┐ (Em paralelo!)
       ▼                                           ▼
  [4A] EXP-028B (Decomposição do erro nas 20+10)  [4B] EXP-029 (Benchmark VLMs no dev-val)
       │                                           │
       └───────────────────┬───────────────────────┘
                           ▼
                  [PORTÃO DG-1: ADR-0.12.9]

FASE 2: COBERTURA E PRIMEIRO SALTO DE LEITURA (Com as 51 páginas que já existem!)
       ┌───────────────────────────────────────────┐ (Em paralelo: código vs anotação!)
       ▼                                           ▼
  [5A] EXP-030A + EXP-030B                        [5B] Dados-13.1 (Anotar caixas + revisar
       (Calibrar limiares DB, escala 48/64/80px        as 21 págs dev-train restantes com
        e iluminação no dev-val)                       ajuda do Professor escolhido em 4B)
       │                                           │
       ▼                                           │
  [PORTÃO DG-2: Precisa de EXP-032?]               │
   (Se não → CR-F13.5 fecha M1 no motor!)          │
       │                                           │
       └───────────────────┬───────────────────────┘
                           ▼
  [6] EXP-033A (1º Fine-tuning do leitor PP-OCRv6 rec small em CPU com as 21 págs!)
       │  (Já entrega o 1º salto real de qualidade sem esperar páginas novas!)
       │
       ├───────────────────────────────────────────┐ (Em paralelo: coleta vs código!)
       ▼                                           ▼
  [7A] Dados-14.1 (+29 págs novas → 50 dev-train, [7B] CR-F13.1 + CR-F13.2 + F-DI-14.5
       já auxiliadas pelo leitor do EXP-033A!)         (Coleta vinculada por line_id no
       │                                                Leitorum + script 1-clique)
       ▼                                           │
  [8] EXP-033B (Treino 50 págs) + EXP-034 + EXP-035│
       │                                           │
       ▼                                           │
  [PORTÃO DG-3: CR-F14.1/14.2 fecha v0.14 e M2] ◄──┘

FASE 3: ESCALA ORGÂNICA, POLIMENTO E MODELO PRÓPRIO
  [9] Coleta contínua pelo uso normal do Leitorum até 100–150 págs (Dados-15.1 + drift-test-1)
       │
       ├───────────────────────────────────────────┐ (Em paralelo!)
       ▼                                           ▼
  [10A] EXP-036 (Leitor v2 150 págs)              [10B] EXP-038 (Ordem geométrica de
        + EXP-037 (KenLM c/ Gate de Proteção)           colunas/margens) + Gerador Sintético
       │                                           │
       └───────────────────┬───────────────────────┘
                           ▼
              [CR-F15.1/15.2 fecha v0.15 e M3]
       │
       ├───────────────────────────────────────────┐ (Trilhas independentes!)
       ▼                                           ▼
  [11A] Trilha MP (Modelos Próprios):             [11B] Trilha v0.16 (Fórmulas):
        • PORTÃO DG-5 → Pré-treino base CRNN            • EXP-040 (Roteador fórmula vs texto)
          no sintético + CC-BY-4.0                      • EXP-039 (TexTeller ONNX / LoRA)
        • Ajuste fino CPU nas 150 págs (EXP-041)        • PORTÃO DG-4 → CR-LDF-2.1 + CR-F16.1
        • Comparação M5 (EXP-042) → Substituição
```

---

## Parte IV — Lista de Experimentos Adicionais de Baixo Custo (Redução de Incerteza)

Estes **7 micro-experimentos** não estavam no plano original, custam de **30 minutos a 3 horas em CPU** cada um (sem GPU e sem dados novos além das 31+20 páginas atuais) e evitam que você gaste semanas na direção errada:

| ID | Pergunta que responde | Hipótese Falseável | Custo em CPU (i5-8265U) | O que o resultado decide |
| :--- | :--- | :--- | :--- | :--- |
| **EXP-A1** *(Altura canônica da linha: 48 px vs 64 px vs 80 px)* | Quanto dos 54% de CER em texto comum vem do fato de o pipeline atual escalar as linhas para `~80 px` antes de passar para um modelo (`PP-OCRv6 rec`) cuja entrada nativa é `48 px` de altura? | Passar recortes na altura nativa de treino do modelo (`48 px` mantendo proporção de aspecto e *padding* vertical de 4–6 px para não cortar acentos/cedilha) reduz o `Oracle-Box Line CER` no `dev-val` em **≥ 4 p.p.** sem nenhum treino. | **20 minutos** (apenas re-inferência nas 10 páginas do `dev-val`). | Decide a altura padrão dos recortes em `[C]` antes de exportar os pacotes de treino `Dados-13.1` e `Dados-14.1`. |
| **EXP-A2** *(Auditoria do Dicionário de Caracteres do `PP-OCRv6`)* | O arquivo de dicionário de caracteres (`dict.txt`) usado hoje na inferência ONNX do `PP-OCRv6 small` contém **todos** os caracteres acentuados minúsculos/maiúsculos do português (`á..ú, â..ô, ã, õ, à, ç`) e símbolos comuns de caderno, e nas mesmas posições do modelo original? | Pelo menos **2% a 5% do CER atual** decorre de caracteres ausentes ou mapeados de forma subótima no dicionário/normalizador Unicode (`NFC` vs `NFD`). | **30 minutos** (script de cobertura do `dict.txt` contra os caracteres de `dev-val`). | Decide se é necessário expandir a camada linear final de saída CTC antes do `EXP-033A`. |
| **EXP-A3** *(Limiar de `box_thresh` e `unclip_ratio` do Detector DB)* | As linhas que somem nas 7 páginas críticas foram ignoradas pela rede neural do detector, ou foram detectadas com probabilidade 0,30–0,50 e descartadas pelo pós-processamento padrão (`box_thresh=0.6`, `unclip_ratio=1.5`)? | Baixar `box_thresh` para `0.35–0.45` e subir `unclip_ratio` para `1.8–2.2` no `dev-val` recupera **≥ 50% das linhas omitidas** sem precisar treinar o detector (`EXP-032`). | **30 minutos** (grid search 3×3 no `dev-val`). | Pode **eliminar a necessidade de GPU e do `EXP-032`** na versão `0.13`, fechando M1 em um único dia! |
| **EXP-A4** *(VLM em Página Inteira vs. VLM em Tiras de 1–3 Linhas)* | O professor VLM (`Qwen3-VL-4B` / `Gemma 4 E2B`) erra menos e usa menos RAM quando lê recortes de 1–3 linhas do que quando tenta ler a foto inteira da página de caderno? | Alimentar tiras de 1–3 linhas reduz o CER do professor no `dev-val` em **≥ 5 p.p.**, elimina pulos de linha e reduz o pico de RAM do encoder visual em **≥ 800 MB**. | **1,5 hora** em CPU nas 10 páginas do `dev-val`. | Define como a ferramenta `F-DI-12.1` chamará o professor para pré-anotar `Dados-13.1` e `Dados-14.1`. |
| **EXP-A5** *(Piso de Ruído Humano: 1 Passada vs. 2 Passadas)* | Qual é a diferença real entre uma transcrição revisada pelo autor em 1 passada rápida vs. 2 passadas cuidadosas? | A 1ª passada deixa passar **1,5% a 3,0% de CER** (especialmente acentos omitidos no próprio caderno vs. corrigidos mentalmente pelo autor). | **1 hora** (medido automaticamente durante o `EXP-028A` salvando o estado da Passada 1 antes da Passada 2). | Define se `dev-train` precisa de 2 passadas ou se 1 passada + auditoria de 10% basta, e fixa a regra de "escrever exatamente a abreviação que está no papel". |
| **EXP-A6** *(Variância entre Sementes e Congelamento de Backbone no Fine-tuning CTC)* | Com apenas 21 a 50 páginas de um único autor, o ajuste fino completo de todas as camadas do `PP-OCRv6 rec small` varia muito entre sementes ou sofre *overfitting* visual rápido? | Congelar os primeiros 2 estágios convolucionais (mantendo os filtros básicos de borda/traço) e treinar apenas o restante + cabeça CTC com 3 sementes (`42, 1337, 2026`) reduz a variância do CER no `dev-val` para **< 0,8 p.p.** e acelera o treino em CPU em **~35%**. | **2 a 3 horas** em CPU com as 21 páginas do `Dados-13.1`. | Fixa a receita estável de *fine-tuning* para `EXP-033B` e `EXP-036`. |
| **EXP-A7** *(Sensibilidade à Quantização INT8 no ONNX Runtime)* | Exportar o leitor CTC ajustado para `ONNX INT8` (dinâmico ou estático calibrado no `dev-val`) melhora a velocidade em CPU sem degradar o CER em relação ao `ONNX FP32`? | Para modelos pequenos (5M params), `ONNX FP32` já roda em < 3 s/pág em AVX2, enquanto `INT8` dinâmico pode degradar o CER em **1 a 3 p.p.** sem ganho relevante de memória (**[Fato — Literatura]:** degradação não-linear reportada em [AfriPlaybook](https://afriplaybook.waraka.org/deployment/edge-devices), jul/2026). | **30 minutos** no `dev-val`. | Evita quantizar cegamente modelos pequenos onde FP32 já cabe em 25 MB de RAM. |

---

## Parte V — O Que Cortar, Simplificar ou Adiar Sem Rodeios

Para um único autor e uma máquina de 4 núcleos / 7,9 GB de RAM, tentar abraçar tudo ao mesmo tempo é o caminho mais curto para a paralisia. Aqui está o que deve ser **cortado ou adiado imediatamente**:

1. **CORTAR do curto/médio prazo: Treinar Detector de Linhas do Zero (`MP-5`) e Treinar Leitor de Fórmulas do Zero.**
   * *Por quê:* Um detector de linhas (`PP-OCRv6 DB small`, Apache 2.0, 2,48M params) pré-treinado ou ajustado não carrega viés ideológico nem dependência de fornecedor: é uma operação puramente geométrica de achar tinta sobre papel, cujos pesos cabem em < 10 MB com licença Apache 2.0 perpétua. E treinar um leitor de fórmulas LaTeX do zero exigiria centenas de milhares de expressões e milhares de horas de GPU ([TexTeller usou 2.688 h de GPU A800 em 80M de pares](https://arxiv.org/html/2508.09220v1), ago/2025). Concentre 100% da energia de "modelo próprio do zero" (`MP-2`) no **Leitor Óptico de Linha `[D1]`** e no **Decodificador Léxico `[D2]`**, que são onde estão a sua caligrafia e a sua língua.
2. **ADIAR INDEFINIDAMENTE: `MP-6` (Modelos para outros autores).**
   * *Por quê:* Você é o único usuário real hoje e tem 51 páginas. Projetar arquitetura multi-autor agora vai poluir suas decisões com problemas que você não tem. A única coisa que o produto precisa ter hoje é o exportador limpo (`CR-F13.1/13.2`); quando um segundo usuário real existir e tiver 50 páginas, o mesmo pipeline roda para ele.
3. **CORTAR da `v0.14`: Treinar `PP-OCRv6 rec medium` (19M) em CPU e perder tempo compilando `PyLaia` se falhar no Windows.**
   * *Por quê:* Em CPU de 4 núcleos sem GPU, sair de `small` (5,2M) para `medium` (19M) quadruplica o tempo de treino e dobra a latência de inferência para um ganho marginal de ~1–2% reportado em literatura ([arXiv:2609.20064](https://arxiv.org/pdf/2609.20064), set/2026). E `PyLaia` é excelente em Linux, mas notório por quebrar *builds* no Windows. Se não rodar limpo em 4 horas via WSL2/ONNX, corte sem remorso e fique com `PP-OCRv6 small` (no degrau `b`) e seu `CRNN PyTorch puro` (no degrau `a`).
4. **CORTAR da `v0.13`: Espera pelas "50 páginas de desenvolvimento" antes de treinar o primeiro leitor.**
   * *Por quê:* Você já tem 31 páginas de desenvolvimento no projeto! Separando 10 para `dev-val` e usando as 21 restantes para `dev-train` (`Dados-13.1`), você já tem ~400 linhas reais — volume suficiente para o primeiro ajuste fino (`EXP-033A`) derrubar o CER drasticamente. Não trave o primeiro treino esperando digitalizar mais 29 páginas; use o modelo treinado nas 21 páginas para tornar a transcrição das 29 seguintes muito mais rápida!
5. **SIMPLIFICAR na `v0.15`: Classificador neural de zonas (`margem`, `lista`, `figura`).**
   * *Por quê:* Com 100 páginas de um único autor, treinar um detector de objetos para classificar tipos de zona em página inteira exigiria GPU e anotação manual de polígonos de zona. Em cadernos de um único autor, **regras geométricas simples sobre as caixas de linha** (ex.: caixa curta isolada nos 20% extremos da esquerda/direita = nota de margem; linha começando com `-`, `•`, `1.` ou indentada = item de lista) resolvem 90% do layout com custo zero de RAM e zero GPU.
6. **SIMPLIFICAR na `v0.16`: Fórmulas *inline* curtas vs. Fórmulas em bloco.**
   * *Por quê:* Quando você escreve $x = 2$ ou $a + b = c$ no meio de uma linha em português, o próprio leitor CTC de texto (desde que os símbolos `+, -, =, /, ^, (, )` estejam no dicionário `dict.txt` auditado no `EXP-A2`) consegue ler isso perfeitamente como texto normal! Você só precisa acionar um modelo pesado de LaTeX (`TexTeller`) quando houver **fórmulas estruturais bidimensionais** (frações com barra horizontal, raízes, somatórios, matrizes ou blocos isolados). Distinguir "matemática linear simples" (fica no CTC) de "matemática 2D" (vai para o TexTeller/editor) reduz pela metade o risco de falsos positivos e economiza segundos preciosos na sua CPU.

---

## Lista de Fontes Primárias Verificadas

1. **Diagnóstico Interno e Histórico do Projeto Leitorum (Nov/2026):** `EXP-027` (análise das 51 páginas reais e 20 congeladas v2), `EXP-008` (detecção GNHK/BRESSAY), `EXP-014/018` (curva de aprendizado CTC em CPU no BRESSAY), `EXP-021` (falha de degradação sintética artificial) e `EXP-024` (limites de pós-correção).
2. **PP-OCRv6 (Jun/2026) & Adaptação Histórica Few-Shot (Set/2026):** [arXiv:2606.13108v1](https://arxiv.org/html/2606.13108v1) | [arXiv:2609.20064](https://arxiv.org/pdf/2609.20064) | [GitHub PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
3. **Limiar de Colapso em Treino HTR do Zero (Mai/2026) & Curvas de Complexidade Amostral (Set/2026):** *Defeating the Haystack* ([Oxford Digital Scholarship in the Humanities](https://academic.oup.com/dsh/article/41/3/1365/8666109)) | [arXiv:2609.16859](https://arxiv.org/pdf/2609.16859)
4. **Deriva Temporal de Autor Único e Generalização OOD em HTR (2024–2026):** Estudo Cavalcaselle ([CEUR-WS Vol-4240](https://ceur-ws.org/Vol-4240/short31.pdf), ago/2026) | [arXiv:2411.17332v1](https://arxiv.org/html/2411.17332v1) (nov/2024) | [CVPR 2025 MetaWriter](https://openaccess.thecvf.com/content/CVPR2025/papers/Gu_MetaWriter_Personalized_Handwritten_Text_Recognition_Using_Meta-Learned_Prompt_Tuning_CVPR_2025_paper.pdf)
5. **VLMs em Manuscrito, Erros Guiados por Prior e Execução em CPU (`llama.cpp`):** *WildHandBench* ([arXiv:2608.22959v1](https://arxiv.org/html/2608.22959v1), ago/2026) | *Using OCR models with llama.cpp* ([Blog ggml-org](https://huggingface.co/blog/ggml-org/using-ocr-models-with-llama-cpp), abr/2026) | Ruído visual `mtmd` Qwen3-VL ([llama.cpp issue #29251](https://github.com/ggml-org/llama.cpp/issues/29251), set/2026) | Quantização de projetor visual ([arXiv:2609.28757v1](https://arxiv.org/html/2609.28757v1), set/2026)
6. **Benchmarks e Licenças em Português (2023–2026):** *DharmaOCR-Benchmark* ([Hugging Face](https://huggingface.co/Dharma-AI/Dharma-OCR-LITE) / [arXiv:2604.14314v1](https://arxiv.org/html/2604.14314v1), abr/2026) | *PorTEXTO* ([Hugging Face CC-BY-NC-4.0](https://huggingface.co/datasets/amalia-llm/PorTEXTO) / [arXiv:2606.19096v4](https://arxiv.org/html/2606.19096v4), set/2026) | *BRESSAY* ([Repo pySarah](https://github.com/arthurflor23/handwritten-text-recognition), 2024–2026) | *LHTR.br* ([SBC OpenLib](https://sol.sbc.org.br/index.php/dsw/article/view/25501), set/2023) | *GNHK* ([GitHub GoodNotes CC-BY-4.0](https://github.com/GoodNotes/GNHK-dataset)) | *READ Bozen* ([Zenodo CC-BY-4.0](https://zenodo.org/records/218236))
7. **Licenças de VLMs Abertos:** [Qwen3-VL-4B Apache 2.0](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct) | [Qwen2.5-VL-3B Research License (NC)](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct/blob/main/LICENSE) | [Gemma Terms of Use](https://ai.google.dev/gemma/terms) | [Gemma 4 E2B Apache 2.0](https://huggingface.co/google/gemma-4-E2B-it) (jul/2026) | [GLM-OCR MIT](https://huggingface.co/zai-org/GLM-OCR) (fev/2026)
8. **Decodificação Léxica, Pós-Correção em PT-BR e Dano de Edição:** *PyLaia + KenLM* ([arXiv:2404.18722v1](https://arxiv.org/html/2404.18722v1), abr/2024) | *Post-OCR PT-BR no BRESSAY* ([ptbr-post-ocr-sc-llm](https://huggingface.co/savi8sant8s/ptbr-post-ocr-sc-llm) e [Monobyte](https://huggingface.co/savi8sant8s/monobyte-spelling-corrector), 2024–2025) | *EditVeto* ([arXiv:2611.05539v1](https://arxiv.org/html/2611.05539v1), nov/2026) | Degradação pós-OCR em CER alto ([ACL CAWL](https://aclanthology.org/2026.cawl-1.8.pdf), mai/2026)
9. **Geração Sintética para HTR:** *UniLipi* ([arXiv:2608.28195v1](https://arxiv.org/html/2608.28195v1), ago/2026) | *DiffLine* ([ResearchGate](https://www.researchgate.net/publication/410838313_Handwritten_Text_Recognition_for_Historical_Latin_Manuscripts_via_Model_Adaptation_and_Synthetic_Data_Augmentation_Handwritten_Text_Recognition_for_Historical_LatinM_M_Trusca_et_al), jul/2026)
10. **Fórmulas Matemáticas (HMER) e Detectores de Layout:** *TexTeller* ([arXiv:2508.09220v1](https://arxiv.org/html/2508.09220v1), ago/2025) | *UniMERNet* ([arXiv:2404.15254v2](https://arxiv.org/html/2404.15254v2), set/2024) | *HME100K Apache 2.0* ([Hugging Face](https://huggingface.co/datasets/SoyVitou/Latex-Math-HME100K)) | *Pix2Text MFD 1.5 MIT* ([Hugging Face](https://huggingface.co/breezedeus/pix2text-mfd-1.5), dez/2025) | *DocLayout-YOLO AGPL-3.0* ([GitHub](https://github.com/opendatalab/DocLayout-YOLO)) | *FocalOrder* ([ACL](https://aclanthology.org/2026.acl-long.868.pdf), jul/2026) | *Orli* ([arXiv:2606.04166v1](https://arxiv.org/html/2606.04166v1), jun/2026)
11. **Pré-processamento, Ferramentas de Anotação e Quantização Edge:** *UVDoc* ([arXiv:2302.02887v2](https://arxiv.org/html/2302.02887v2), fev/2024) | *PPOCRLabel* ([PyPI](https://pypi.org/project/PPOCRLabel/)) | *eScriptorium* ([GitLab](https://gitlab.com/scripta/escriptorium)) | Quantização INT8 em Edge ([AfriPlaybook](https://afriplaybook.waraka.org/deployment/edge-devices), jul/2026) | Cotas de GPU Kaggle/Colab ([Fastero](https://fastero.com/blog/kaggle-vs-colab), nov/2026)
