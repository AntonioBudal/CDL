# EXP-044 — Fontes em português ajudam o leitor onde as fontes latinas não ajudaram?

* **Criado em:** 2026-11-23
* **Status:** `DONE` (aprovado pelo usuário em 2026-11-23; [relatório](./report.md))
* **Etapa:** E3.1 da [estratégia de dados v3](../../docs/replanejamento-0.13/10-revisao-da-estrategia-de-dados.md)
* **Depende de:** EXP-031P (régua e condições de referência), F-DI-13.03 (catálogo) · **Decide:** a E4' (o que
  escalar)

---

## 1. Pergunta

O EXP-031P mostrou que 8 mil linhas de francês, norueguês e latim não melhoram a leitura de letra moderna em
português (29,9 % → 28,9–30,3 % no BRESSAY teste), enquanto 6 mil linhas de redações em português levam a 13,6 %.
**Fontes em português que achamos na internet chegam perto desse ganho?** E o fracasso do EXP-031P foi falta de
domínio ou falta de treino?

## 2. Fontes novas

| Fonte | O que é | Situação no catálogo |
| :--- | :--- | :--- |
| **TraPrInq** | processos da Inquisição portuguesa, séc. XVI–XIX, transcritos por linha (6.417 páginas) | `APPROVED` (CC BY 4.0, Zenodo) |
| **BFL** | 315 pessoas copiando à mão a mesma carta de 131 palavras, 3 vezes cada (945 páginas, 300 dpi) | `EXPERIMENT_ONLY` (licença conflitante: selo CC BY 4.0 e "non-commercial research") |

A BFL não tem transcrição por linha. Como o texto é fixo, ele é distribuído entre as linhas detectadas por
**alinhamento forçado**, e linhas de baixa confiança são descartadas (plano, §BFL).

## 3. Condições

Receita e medidas do EXP-031P: ajuste fino do PP-OCRv6 small, lotes de 16, taxa 5e-5, margem de 640 px, semente
1234, modelo final.

| Condição | Dados de treino | Passos | Pergunta |
| :--- | :--- | ---: | :--- |
| **C0** | nenhum (do EXP-031P: 29,9 %) | — | referência |
| **D1** | TraPrInq, 8 mil linhas, preferindo os documentos mais recentes | 392 | o português histórico ajuda onde o latim e o francês antigo atrapalharam? |
| **D2** | BFL alinhada, 8 mil linhas | 392 | letra moderna brasileira com texto fixo ensina o domínio? |
| **D3** | TraPrInq 3 mil + BFL 3 mil + sintético 2 mil | 392 | a mistura soma? |
| **D4** | a lista do C4 do EXP-031P (latino moderno 4 mil + sintético 4 mil) | **1.568** (4×) | o EXP-031P falhou por treino curto? |

## 4. Onde se mede

As mesmas listas do EXP-031P, sem mudança: **BRESSAY teste** (2.000 linhas sorteadas, medida principal), **GNHK
teste** (1.918 linhas, foto e inglês) e as **62 linhas do autor** (4 páginas, 512 px). Medidas: CER, WER e erro nas
letras acentuadas. A BFL e a TraPrInq **nunca** são usadas para medir.

## 5. Hipóteses

| # | Hipótese | Critério |
| :--- | :--- | :--- |
| **H1** | o português histórico ajuda mais que o histórico latino | CER(D1) < CER(C2 do EXP-031P, 46,9 %) **e** CER(D1) ≤ C0 + 1 |
| **H2** | a BFL ensina o domínio | CER no BRESSAY cai ≥ 3 pontos de C0 para D2 |
| **H3** | a mistura em português é a melhor condição | D3 tem o menor CER no BRESSAY entre D1–D4 |
| **H4** | o EXP-031P falhou por treino curto | CER(D4) ≤ CER(C4, 29,4 %) − 3 |

**Regra de decisão para a E4'** (a mesma do EXP-031P): escalar a fonte da condição vencedora se ela melhorar
≥ 3 pontos sobre C0 no BRESSAY sem piorar > 2 no GNHK.

* Se a vencedora usa **só `APPROVED`** (D1, D4): escalar já.
* Se usa a **BFL** (D2, D3): escalar só como experimento e esperar a resposta dos autores antes de qualquer
  modelo do produto.
* Se nenhuma melhorar ≥ 3 pontos: a única via medida que funciona é o BRESSAY, e a decisão volta ao usuário.

**Ruído:** como no EXP-031P, se a diferença decisiva ficar abaixo de 1,5 ponto, a condição é repetida com a
semente 4321.

## 6. Regras

* Dados de treino **só pelo catálogo**; cada condição é um ciclo `experimento` com a lista exata.
* Evidência de licença guardada no catálogo: a resposta da API do Zenodo (TraPrInq) e cópia da página da UFPR
  (BFL).
* Baixar **só o necessário** para 8 mil linhas (1 ou 2 dos 10 arquivos da TraPrInq, ~1 GB; a BFL inteira, que é
  um arquivo só). A TraPrInq inteira (6,7 GB) só entra na E4', se ganhar.
* Linhas com caracteres fora do dicionário do leitor são descartadas e contadas. Se passar de 20 % numa fonte,
  isso é registrado como limitação.
* Tudo local, em CPU, retomável e com espera de RAM livre. Espaço extra estimado: ~3 GB no D:.
* Nenhum modelo deste experimento vai ao produto.
