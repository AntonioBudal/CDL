# Etapa 3 — Plano: estratégia, arquitetura-alvo, metas e crescimento do banco de páginas

**Data:** 2026-11-16 · **Status:** `RASCUNHO` para revisão do usuário · **Base:** [EXP-027](../../experiments/EXP-027-analise-50-paginas/report.md)
(Etapa 1), [pesquisa](./03-resultado-pesquisa.md) (Etapa 2), [diretriz de modelos próprios](../objetivo-modelos-proprios.md),
histórico EXP-008 a EXP-022.

**Como ler.** Cada afirmação carrega uma de três marcas: **[medido]** = número do próprio projeto;
**[pesquisa]** = afirmação do relatório da Etapa 2, com fonte citada lá, ainda não conferida aqui;
**[a medir]** = depende de experimento local antes de virar direção de trabalho (Constituição, Princípio 2).
O plano não decide nada que esteja só em [pesquisa]; ele diz o que medir primeiro.

---

## 1. O diagnóstico em três frases

O motor atual erra mais da metade dos caracteres nas suas páginas (CER 56 %, WER 90 %) **[medido]**. O erro
não vem das fórmulas (12–16 % dele) nem da cursiva (que lê igual ou melhor que a letra de forma); vem de
**texto comum mal lido** (54 % de CER) e de **texto que nem chega a ser lido** (28 % das palavras somem; 7 de 20
páginas saem com 30–67 % do tamanho) **[medido]**. Um modelo grande transcreveu as mesmas fotos quase sem erro
**[medido, declarado pelo usuário]**: o problema é resolvível; a questão é fazê-lo local, barato e, no fim, com
modelos nossos.

## 2. Estratégia em linguagem simples

> **Primeiro enxergar a página inteira, depois ler certo, depois polir.** Cada degrau usa um modelo aberto só
> até um modelo nosso igualar ou superar ele no mesmo teste congelado.

Três decisões de fundo:

1. **Manter o pipeline modular** (foto → linhas → leitura linha a linha → ordem) como motor do produto, em vez
   de trocar por um modelo multimodal de página inteira. Motivos: é o único que roda em menos de 1 GB e
   poucos segundos na máquina de referência **[medido: 7 s, ~800 MB]**; cada peça pode ser treinada em casa ou
   em poucas horas de GPU **[pesquisa]**; e é o caminho que leva a pesos nossos. Um VLM de 4 B em CPU precisa
   de 3–5 GB e dezenas de segundos por página **[pesquisa; a medir]**, e nunca seria nosso.
2. **Usar modelos multimodais abertos como professor e baseline**, não como motor: eles geram o rascunho que
   você corrige (dados de treino) e marcam o teto do que é possível localmente. A cópia exata fica guardada
   com hash e licença. O Qwen3-VL-4B já está guardado e verificado; GLM-OCR (0,9 B, MIT) e Gemma 4 E2B
   (Apache-2.0) são candidatos a medir **[pesquisa]**.
3. **Dados do próprio usuário são o ativo central.** Não há dataset público de manuscrito em português com
   licença limpa para produto (BRESSAY e LHTR.br sem licença comercial clara; PorTEXTO é não comercial)
   **[pesquisa; coerente com o que o projeto já sabia do BRESSAY]**. O banco de páginas transcritas do usuário,
   crescendo com as correções feitas no produto, é o que torna os modelos nossos possíveis.

## 3. Arquitetura-alvo

```
foto do celular
  │
  ▼
[A] preparação leve ............. OpenCV (perspectiva, iluminação); UVDoc só se medido   (c) → mantém (c)
  │
  ▼
[B] detecção de linhas .......... PP-OCRv6 DB small hoje (c) → ajustado com GNHK + páginas suas (b)
  │                                → próprio só se o layout de caderno exigir (a, longo prazo)
  ▼
[C] leitura de cada linha ....... PP-OCRv6 rec small hoje (c) → ajustado com 50–150 páginas suas (b)
  │                                → CTC próprio do zero com >150 páginas + sintético PT-BR (a)
  ▼
[D] decodificação com léxico .... desligada até CER < 20 % → KenLM + vocabulário seu, dentro do CTC (a, leve)
  │
  ▼
[E] ordem de leitura e zonas .... regras geométricas (a, já existe) → classes de zona (margem, lista) (b)
  │
  ▼
[F] fórmulas .................... por último: detector de fórmula + TexTeller (CC BY 4.0) ou VLM pontual (c→b)
  │
  ▼
LDF 2.0 → Leitorum (texto + confiança + caixas + correções humanas)

professor/baseline (fora do motor): Qwen3-VL-4B · GLM-OCR · Gemma 4 E2B — rascunhos para você corrigir e
teto local de qualidade; nunca componente do produto.
```

O contrato LDF 2.0 fica estável. Trechos de fórmula e classes de zona entram como **LDF 2.1** por change
request e ADR quando [E] e [F] forem implementados, não antes.

## 4. Três caminhos por etapa, com o veredito honesto

| Etapa | (a) próprio do zero | (b) ajuste fino, pesos nossos | (c) externo aberto | Veredito para esta máquina |
| :--- | :--- | :--- | :--- | :--- |
| [A] preparação | inviável (anotação de malha, GPU) | UVDoc em 50–200 fotos, GPU 1–3 h [pesquisa] | OpenCV / UVDoc 8 M MIT [pesquisa] | só (c); ganho em fotos de caderno **[a medir]** |
| [B] detecção | inviável (500+ páginas com caixas, dias) [pesquisa] | DB small com GNHK (CC-BY-4.0) + 50–100 páginas suas; CPU 4–12 h apertado ou GPU 0,5–2 h [pesquisa] | DB small hoje: F1 0,81 em fotos de manuscrito EN **[medido, EXP-008]** | (b) é o alvo; antes, **medir quanto dos 28 % é detecção [a medir]** |
| [C] leitura | só com >150 páginas suas + 100k–500k linhas sintéticas, 10–40 h de GPU [pesquisa] | PP-OCRv6 rec small/medium ou PyLaia; CTC em CPU **[medido: < 1 época em CPU, 29,7 → 13,6 % no BRESSAY]** | VLMs 1–4 B em CPU: 3–5 GB, 15–60 s/página [pesquisa; a medir] | **(b) é o maior ganho**; (a) só depois, quando o banco passar de 150 páginas |
| [D] decodificação | KenLM + léxico: minutos em CPU, LGPL [pesquisa] | ByT5/Monobyte: só entre 8 e 18 % de CER, GPU [pesquisa] | SymSpell/LLM: pioram [pesquisa; coerente com EXP-011 e EXP-024] | (a) leve, **só quando CER < 20 %** |
| [E] ordem/zonas | regras geométricas: já existe (EXP-003, ADR-003) **[medido]** | detector de zonas em 100–300 páginas, GPU [pesquisa] | VLM entende setas, mas caro em CPU [pesquisa] | (a) regras agora; (b) quando houver zonas anotadas |
| [F] fórmulas | inviável (100k+ pares, centenas de horas de GPU) [pesquisa] | TexTeller ajustado em 500+ recortes, GPU 2–6 h [pesquisa] | TexTeller 298 M CC BY 4.0, ~1 GB RAM [pesquisa] | (c) → (b), por último |

**O que cabe nesta máquina, sem GPU:** ajuste fino de leitores CTC pequenos (PP-OCRv6, PyLaia, Kraken) com
algumas centenas a 2 mil linhas **[medido no EXP-014/018 para o PP-OCRv6]**; KenLM; geração de dados sintéticos;
regras de ordem; inferência de tudo acima. **O que não cabe:** treinar qualquer coisa do zero, ajustar
transformers (TrOCR, TexTeller, VLMs) e o detector em muitas épocas **[pesquisa]**.

**Sobre GPU emprestada (Kaggle, Colab):** é grátis por poucas horas, mas significa **enviar as suas páginas (ou
os recortes de linha) para a nuvem de terceiros**. Isso não quebra a regra do produto (o motor continua local
e sem custo), mas é uma decisão sua de privacidade, a tomar por etapa. O plano prevê o caminho **sem** GPU
para [C] e [D] (CPU, como no EXP-014) e deixa [B], [F] e qualquer (a) como opcionais com GPU.

## 5. Metas mensuráveis, calibradas pela Etapa 1

Todas no **teste congelado v2** (20 páginas, hashes em `splits/test-manifest.json`), com a mesma referência e
o mesmo script de pontuação; em nível de página até as fotos entrarem, em nível de linha depois.

| Marco | Métrica no teste congelado | Hoje **[medido]** | Alvo | Como se mede |
| :--- | :--- | ---: | ---: | :--- |
| M0 | linha de base registrada | CER 56 %, WER 90 % | — | benchmark de 2026-11-16 |
| M1 cobertura | páginas com saída < 85 % do tamanho da referência | 7 de 20 | 0 de 20 | razão de caracteres; com fotos, recall de linhas |
| M1 cobertura | palavras da referência ausentes na saída | 28 % | ≤ 10 % | palavras omitidas no alinhamento |
| M2 leitura v1 | CER / WER com leitor ajustado em 30–50 páginas | 56 % / 90 % | ≤ 30 % / ≤ 65 % | mesmo script, mesmas páginas |
| M3 leitura v2 | CER / WER com 100–150 páginas + sintético + KenLM | — | ≤ 15–20 % / ≤ 45 % | idem |
| M4 fórmulas | CER só nos caracteres de fórmula | 73–77 % | ≤ 40 % sem piorar o texto | máscara `$…$` da referência |
| M5 próprio | leitor (a) do zero contra o ajustado (b) | — | igualar ou superar (b) | critério de troca |
| sempre | custo no produto | 7 s, ~800 MB | ≤ 10 s, ≤ 1,5 GB por página em CPU | medido no motor |
| teto local | baseline VLM aberto (CER, s/página, RAM) | — | medir | EXP de baseline com as fotos |

Por que esses números: o salto 29,7 → 13,6 % do BRESSAY **[medido]** foi em digitalizações; em fotos de caderno o
ponto de partida é 56 % e a chegada não será a mesma. M2 e M3 são **hipóteses a confirmar por experimento**,
não promessas; cada marco é um portão de saída de versão (Etapa 4). Se M2 não for atingido com 50 páginas, a
resposta é mais dados e cobertura antes de qualquer arquitetura nova.

## 6. Como o banco de páginas cresce sem contaminar o teste

1. **Teste congelado v2** (20 páginas) nunca entra em treino, prompt, limiar, léxico ou calibração. O script
   de treino recusa qualquer linha cuja página tenha hash no manifesto de teste (teste automatizado garante).
2. **Nada da mesma página em treino e teste.** Divisões são sempre por página inteira, nunca por linha.
3. **Conjunto de desenvolvimento** = as 31 páginas restantes + tudo que vier depois. Serve para treinar,
   ajustar e calibrar.
4. **Teste de deriva**: a cada ~3 meses (ou a cada 100 páginas novas), 10 páginas novas, sorteadas, viram um
   segundo teste congelado, para ver se caneta, caderno ou pressa mudaram a letra **[pesquisa; regra adotada]**.
   Elas nunca entram no treino.
5. **De onde vêm as páginas novas:** do próprio produto. Cada digitalização salva já guarda o texto bruto; a
   feature de produto (Etapa 4) passa a guardar, com consentimento explícito e opção de desligar, a foto
   recortada, as caixas das linhas e o texto corrigido pelo usuário, como `human_corrections` no LDF. Um
   exportador do Leitorum gera o pacote de treino (foto + caixas + linhas corrigidas), por página, com hash.
6. **Rascunho por professor, correção por você.** O rascunho que o usuário corrige pode vir do motor ou de um
   professor aberto local; o par (rascunho → correção) registra a origem. Rascunhos de professor **nunca** são
   usados sem correção humana, e nunca nas páginas de teste.
7. **Versões de dado e de modelo com manifesto**: cada treino registra os hashes das páginas usadas, o
   professor dos rascunhos, a semente e o commit; cada modelo é avaliado no teste v2 e no teste de deriva
   antes de entrar no produto (registry de modelos com licença e hash, como hoje).
8. **Fórmulas na referência**: marcadas entre `$…$` na correção, para a métrica M4 existir.

## 7. O que medir antes de decidir (ordem)

1. **Detecção × leitura nas 20 páginas** (fotos de teste no projeto; caixas do motor contra a referência):
   decide se M1 vem antes de M2. **[a medir]**
2. **Baseline VLM local** no teste (Qwen3-VL-4B já guardado; GLM-OCR e Gemma 4 E2B se a RAM permitir):
   CER, tempo e RAM na máquina de referência. Decide quem é o professor e qual o teto local. **[a medir]**
3. **Ajuste fino do leitor com 30 páginas de desenvolvimento em CPU** (repetir o EXP-014 com dados seus):
   primeiro número real de M2. **[a medir]**
4. **Preparação leve (OpenCV) e escala** nas páginas de pior cobertura: ganho isolado. **[a medir]**

## 8. Riscos

* A referência das 20 páginas é de um modelo externo sem conferência linha a linha; uma 2ª passada sua
  reduz o risco de "erro do professor virar erro do motor".
* Os números da pesquisa sobre VLMs em CPU (RAM, s/página) e sobre quantas páginas bastam para o detector
  são de terceiros; o projeto já viu uma direção da literatura não se confirmar em imagens reais (ADR-005).
* Um só autor: o modelo ajustado será **seu**, não de qualquer leitor do produto; para outros usuários, o
  mesmo caminho precisa das páginas deles (o produto já prevê isso no item 5 da §6).
* Licenças: GNHK (CC-BY-4.0) exige atribuição; TexTeller (CC BY 4.0) idem; Gemma tem termos próprios para
  as versões 3 (evitar) **[pesquisa]**; tudo passa pelo registry antes de uso.

## 9. O que vai para a Etapa 4

Com este plano aprovado, a Etapa 4 divide o trabalho em versões (0.13, 0.14, …) por marco (M1 → M2 → M3 →
M4), com features e experimentos pequenos, cada um uma spec, dependências, o que exige GPU e o que precisa
de dados que ainda não existem; e um roadmap separado para a trajetória de modelos próprios: coleta →
primeiro modelo próprio → comparação com o baseline → substituição.
