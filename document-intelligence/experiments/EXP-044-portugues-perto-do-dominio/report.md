# EXP-044 — Relatório: fontes em português

* **Data:** 2026-11-23 a 2026-11-24 · **Status:** `DONE`
* **Spec:** [spec.md](./spec.md) · **Plano:** [plan.md](./plan.md) · **Tarefas:** [tasks.md](./tasks.md) ·
  **Números:** [resultados.json](./resultados.json) (só medidas, sem texto)
* **Dados e modelos:** `D:\Leitorum-DI\` (catálogo, listas, modelos de experimento), fora do Git. Nenhum modelo
  deste experimento vai ao produto.

## 1. Resumo

1. **A BFL é a primeira fonte da internet que ensina o domínio.** Com 8 mil linhas alinhadas de 309 pessoas
   copiando a mesma carta, o CER no BRESSAY teste cai de 29,9 % para **23,0 %** (−6,9 pontos). O erro nos acentos
   cai de 76 % para 32 %, e as 62 linhas do autor vão de 65,8 % para 53,1 %. Para comparar: o próprio BRESSAY
   de treino, com o mesmo orçamento, leva a 13,6 %.
2. **O GNHK (fotos em inglês) piora 5,4 pontos com a BFL**, acima do limite de 2 da regra. Pela regra da spec,
   nenhuma condição passa, e a escala não é automática (§6).
3. **O português histórico não serve.** A TraPrInq leva o BRESSAY a 32,8 %: piora o leitor atual, mas bem menos
   que o histórico latino do EXP-031P (46,9 %).
4. **A mistura não soma.** TraPrInq + BFL + sintético dá 26,6 %, entre o D1 e o D2. É a condição que menos piora
   o GNHK (+3,4).
5. **O EXP-031P não falhou por treino curto.** O latino moderno + sintético, com 4× os passos, termina em
   29,4 %, o mesmo do C4. Nas linhas do autor, piora para 71,7 %. As fontes latinas modernas saem.

## 2. Resultados

CER de linha (WER e acentos no BRESSAY). Receita do EXP-031P: ajuste fino do PP-OCRv6 small, lotes de 16, taxa
5e-5, margem 640 px, semente 1234, modelo final. BRESSAY = 2.000 linhas sorteadas do teste; GNHK = teste completo
(1.918 linhas); autor = 62 linhas de 4 páginas, imagens de 512 px.

| Condição | Dados | Passos | BRESSAY | WER | Acentos | GNHK | Autor |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| C0 | nenhum (leitor atual, EXP-031P) | — | 29,9 % | 73,1 % | 76,0 % | **15,1 %** | 65,8 % |
| C2 | histórico latino (EXP-031P) | 392 | 46,9 % | 90,1 % | 94,4 % | 31,7 % | 87,8 % |
| C4 | latino moderno + sintético (EXP-031P) | 392 | 29,4 % | 71,6 % | 59,2 % | 18,3 % | 65,5 % |
| **D1** | TraPrInq, 8 mil | 392 | 32,8 % | 76,7 % | 62,5 % | 23,1 % | 64,5 % |
| **D2** | BFL alinhada, 8 mil | 392 | **23,0 %** | **63,5 %** | **32,1 %** | 20,5 % | **53,1 %** |
| **D3** | TraPrInq 3 mil + BFL 3 mil + sintético 2 mil | 392 | 26,6 % | 67,0 % | 42,5 % | 18,5 % | 59,4 % |
| **D4** | a lista do C4 | 1.568 | 29,4 % | 72,4 % | 59,5 % | 20,5 % | 71,7 % |
| *Referência (EXP-014)* | *BRESSAY treino* | *392* | *13,6 %* | | | | |

**Ruído.** No EXP-031P, duas sementes da mesma lista diferiram 1,4 ponto no BRESSAY e 2,0 no autor. Todas as
diferenças decisivas aqui passam de 1,5 ponto (a menor é D1 contra C0 + 1, com 1,9 ponto), então nenhuma
condição foi repetida.

**Treino.** Cerca de 1 h por condição de 392 passos e 4 h para o D4, em CPU, sem nenhuma pausa por falta de
memória. A perda final do D4 (0,20, contra ~1 nas outras) indica que o modelo decorou a lista. Cada lista é um
ciclo `experimento` no catálogo: run-0007 (D1), run-0008 (D2), run-0009 (D3) e run-0010 (D4).

**O leitor atual nas fontes novas** (amostras de 200 linhas): BFL 30,0 % de CER, com 89 % de erro nos acentos;
TraPrInq 55,0 %, com 99 % de erro nos acentos. A BFL tem dificuldade parecida com a do BRESSAY. A TraPrInq é
bem mais difícil.

## 3. Hipóteses

| # | Hipótese | Resultado |
| :--- | :--- | :--- |
| **H1** | o português histórico ajuda mais que o histórico latino: CER(D1) < 46,9 % **e** ≤ C0 + 1 | **refutada em parte**: 32,8 % é bem menor que 46,9 %, mas passa 1,9 ponto do limite de 30,9 % |
| **H2** | a BFL ensina o domínio: o BRESSAY cai ≥ 3 pontos | **confirmada**: −6,9 pontos (29,9 → 23,0 %) |
| **H3** | a mistura em português é a melhor | **refutada**: D3 (26,6 %) fica 3,6 pontos atrás do D2 |
| **H4** | o EXP-031P falhou por treino curto: CER(D4) ≤ 26,4 % | **refutada**: 29,4 %, o mesmo do C4 |

## 4. As fontes

### TraPrInq (`APPROVED`, CC BY 4.0)

* Um arquivo de treino bastou: `Training_Set_Model9.zip`, com MD5 conferido. São 500 páginas de 49 documentos e
  12.717 linhas.
* Linhas por século: XVIII e XIX primeiro, depois XVII; o resto completa a lista.
* Foram descartadas 3.416 linhas (27 %) por caractere fora do dicionário do leitor: as abreviaturas com macron
  combinante, ꝯ, ꝑ e ¶. Outras 67 foram descartadas por dúvida ou riscado. Ficaram 9.234.
* O descarte passa dos 20 % previstos na spec e fica registrado como limitação. As linhas que sobram são as com
  menos abreviatura, o que favorece a fonte.
* A transcrição é diplomática: conserva a grafia antiga e as maiúsculas do manuscrito.

### BFL (`EXPERIMENT_ONLY`, licença conflitante)

* São 945 páginas de 315 pessoas. A detecção e a leitura foram feitas com o motor do produto (~4,4 s por
  página). O texto da carta foi distribuído entre as linhas detectadas por **alinhamento forçado**, caractere a
  caractere e sem caixa.
* Filtros:
  * página com 8 a 25 linhas: 33 páginas ficaram de fora;
  * CER da leitura contra o trecho ≤ 0,45, sem caixa;
  * ≥ 3 palavras;
  * **linha que parte uma palavra**: 1.801 linhas descartadas.
* Resultado: **11.923 linhas de 309 pessoas** (2 a 58 por pessoa, mediana 41).
* Quando a leitura sai quase toda em maiúsculas (≥ 70 % das letras), o rótulo também vai para maiúsculas. Isso
  aconteceu em 1.015 das linhas aceitas.
* **Conferência a olho.** Na primeira amostra de 50 recortes, 5 rótulos estavam errados, todos pelo mesmo
  motivo: palavra partida com hífen no fim da linha. O trecho, levado ao limite de palavra, ganha ou perde um
  pedaço que não está na imagem.
  * A regra nova (`align.align_detail`) descarta a linha quando a fronteira bruta do alinhamento cai a mais de
    1 caractere de um espaço.
  * Ela pega os 5 erros e nenhum dos 45 certos.
  * Numa segunda amostra, também de 50, sobrou 1 erro: uma palavra da linha de baixo, numa página inclinada.

## 5. O que isso quer dizer

* **A letra pesa mais que o texto.** A BFL repete um único texto de 128 palavras, e ainda assim ensina mais que
  8 mil linhas variadas de qualquer outra fonte. O que falta ao leitor é ver muitas mãos brasileiras modernas e
  os acentos escritos à mão. Vocabulário vem depois.
* **O ganho é transferência, não memória.** O BRESSAY e as páginas do autor não têm o texto da carta. Mesmo
  assim, as duas medidas melhoram.
* **O histórico, até em português, ensina convenções que atrapalham.** Grafia antiga, maiúsculas de época e
  traçado de escrivão afastam o leitor da letra escolar.
* **Treinar mais com a fonte errada não adianta.** O D4 decora a lista e fica igual no BRESSAY.
* **O GNHK continua piorando com qualquer treino** (+3,4 a +8,0 pontos aqui). O leitor geral precisa de inglês e
  de foto na mistura. Nenhuma fonte testada até agora protege isso.

## 6. Decisão para a E4'

Pela regra da spec, a fonte vencedora só escala se ganhar ≥ 3 pontos no BRESSAY **sem piorar > 2 no GNHK**.

* O D2 ganha 6,9 pontos, mas piora o GNHK em 5,4.
* O D3 ganha 3,3 e piora 3,4.

**Nenhuma condição passa na regra completa, então a E4' não é disparada.** Além disso:

* **TraPrInq inteira (6,7 GB):** não vale o download. O D1 piora o leitor.
* **BFL:** não há o que escalar. As 945 páginas já estão no catálogo (11.923 linhas, das quais o D2 usou 8 mil).
  A fonte continua `EXPERIMENT_ONLY` até a resposta dos autores, e nenhum modelo com ela vai ao produto.
* **Latino moderno:** sai de vez (H4 refutada). As linhas já coletadas ficam só como reserva de mistura.

**Proposta para o próximo passo** (decisão do usuário; nada foi iniciado): um experimento curto que tente manter
o ganho do D2 sem perder o GNHK. A ideia é misturar a BFL com linhas que tenham inglês e foto e medir com a mesma
régua. Se a mistura passar na regra, a BFL vira a primeira fonte da E4', ainda como experimento até a licença ser
esclarecida.

## 7. Limites

* **Licença da BFL.** O selo diz CC BY 4.0, mas o texto da página diz "non-commercial research". O resultado
  vale como experimento. Para o produto, depende da resposta dos autores (Apêndice A da
  [estratégia v3](../../docs/replanejamento-0.13/10-revisao-da-estrategia-de-dados.md)).
* **Ruído de rótulo na BFL.** Cerca de 2 % de erro na conferência. Além disso, há variações que o alinhamento
  não vê: acento posto ou tirado num nome, trema, ordinal trocado, número diferente, palavras puladas por quem
  escreveu. A regra de caixa é uma heurística (≥ 70 % de maiúsculas na leitura).
* **Um texto só.** A BFL pode ensinar o vocabulário da carta. As medidas usam textos diferentes, mas o ganho
  pode encolher com textos muito distantes dela.
* **Descarte alto na TraPrInq** (27 % por dicionário), o que pode favorecer a fonte.
* **Uma semente por condição** e a mesma régua pequena do EXP-031P. As páginas do autor são poucas e de 512 px.
