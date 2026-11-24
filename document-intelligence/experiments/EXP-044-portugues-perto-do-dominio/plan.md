# Plano: EXP-044 — Fontes em português

**Spec:** [spec.md](./spec.md) · **Data:** 2026-11-23 · **Status:** `DONE`

## Contexto técnico

* **Reaproveitado sem alteração:** `train.py` e `evaluate.py` do EXP-031P (ambiente `EXP-014/envs/ft`), chamados
  por invólucros do EXP-044 que trocam as constantes `WORK` e `MODELS` para `D:\Leitorum-DI\trabalho\exp-044` e
  `D:\Leitorum-DI\modelos\exp-044`. As medidas usam os mesmos arquivos de `trabalho\exp-031p\medida\`, copiados.
  Também são reaproveitados o `groups.py` (cotas por fonte, semente) e o sintético já gerado do EXP-031P.
* **Catálogo:** fontes novas `zenodo-traprinq` (`APPROVED`) e `ufpr-bfl` (`EXPERIMENT_ONLY`) com
  `Catalog.add_source` e a evidência de licença; linhas com `Catalog.ingest_line`; ciclos com `start_run`.

### TraPrInq

1. Baixar do Zenodo o `Transcription Criteria.pdf` e os arquivos de treino necessários, começando pelo menor
   (~0,45 GB), em `D:\Leitorum-DI\trabalho\exp-044\traprinq\`. Arquivos conferidos pelo MD5 do registro.
2. Ler o formato (PAGE XML, esperado do Transkribus): linhas com polígono e texto.
3. Datas: se os metadados trazem ano ou século, preferir séc. XVIII–XIX; se não, sorteio uniforme por documento.
4. Recorte da linha pela caixa do polígono, cinza, 64 px de altura (padrão do catálogo).
5. Ler os critérios de transcrição: abreviações expandidas ou mantidas, marcas editoriais. Marcas editoriais são
   removidas do texto de treino pela mesma regra em todas as linhas e registradas no relatório.
6. Os zips são apagados depois da ingestão; ficam só as linhas no catálogo.

### BFL e o alinhamento forçado

1. Baixar o `BFL_Database.zip` da UFPR (link direto da página do projeto) para
   `D:\Leitorum-DI\trabalho\exp-044\bfl\`.
2. **Texto da carta:** transcrito uma vez a partir da imagem de exemplo pública da página do BFL, conferido em 3
   páginas do conjunto. Fica em `D:/Leitorum-DI/trabalho/exp-044/bfl/carta.txt`, fora do Git (texto da BFL, `EXPERIMENT_ONLY`).
3. **Linhas:** o detector de linhas do produto (`leitorum_motor`, ambiente do motor), na escala automática do
   ADR-008, dá as caixas na ordem de leitura.
4. **Leitura:** o leitor atual lê cada linha (hipótese).
5. **Alinhamento:** programação dinâmica que divide a sequência de palavras da carta em tantos trechos quantas
   linhas detectadas, em ordem, minimizando a soma das distâncias de edição entre cada hipótese e o seu trecho.
   Cada linha recebe o trecho atribuído como texto.
6. **Filtro:** uma linha só entra se o CER da hipótese contra o trecho for ≤ 0,45 (o leitor atual erra ~30 % no
   BRESSAY), se o trecho tiver ≥ 3 palavras e se a página tiver detectado entre 8 e 25 linhas.
7. **Conferência:** 50 linhas sorteadas vistas a olho. Se mais de 10 % tiverem o texto errado, ajusto o limiar ou
   o filtro e repito antes de treinar.
8. Variações da pessoa (palavra pulada, erro de cópia) viram ruído de rótulo; o filtro de CER corta a maioria.

**Risco conhecido:** o filtro usa o próprio leitor e pode favorecer as linhas que ele já lê bem. Mitigação: o
limiar é largo, e o relatório traz a distribuição do CER das linhas aceitas e descartadas.

### Treino e medida

| Condição | Lista | Comando |
| :--- | :--- | :--- |
| D1 | 8 mil linhas da TraPrInq (`groups.select`, cota por documento) | `train.py --cond D1` |
| D2 | 8 mil linhas da BFL, cota igual por pessoa; se o filtro aceitar menos, todas as aceitas (o treino vê ~6,3 mil linhas de qualquer forma) | `train.py --cond D2` |
| D3 | 3 mil TraPrInq + 3 mil BFL + 2 mil sintéticas | `train.py --cond D3` |
| D4 | cópia da lista do C4 do EXP-031P | `train.py --cond D4 --steps 1568` |

Avaliação com `evaluate.py` nas três medidas, resultados em `trabalho\exp-044\resultados.json`, junto com o C0
copiado do EXP-031P para a tabela.

## Orçamento

| Item | Custo estimado |
| :--- | :--- |
| Downloads | TraPrInq ~1 GB + BFL (tamanho medido antes) |
| Alinhamento da BFL | ~945 páginas × ~7 s ≈ 2 h de CPU |
| Treino | D1–D3 ~1h30 cada; D4 ~6 h (checkpoint a cada 50 passos) |
| Avaliação | ~10 min por condição |
| Espaço final no D: | ~3 GB (linhas e modelos; zips apagados) |

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| Muitos caracteres fora do dicionário na TraPrInq (ſ, abreviações) | descartar e contar; > 20 % vira limitação registrada |
| A BFL decorada (mesmo texto) | nunca medir na BFL; cota por pessoa; mistura em D3 |
| Alinhamento errado | filtro de CER, conferência de 50 linhas, limiar ajustável antes do treino |
| Link da BFL fora do ar ou exigindo cadastro | não contornar; seguir só com D1 e D4 e registrar |
| D4 longo e a máquina compartilhada | retomável, espera de RAM; pode rodar à noite |
| Ruído entre condições | repetir com a semente 4321 se a diferença decisiva for < 1,5 ponto |
