# Tarefas: EXP-044 — Fontes em português

**Entrada:** [spec.md](./spec.md) e [plan.md](./plan.md).

- [x] T001 Testes que falham primeiro: leitura de PAGE XML (arquivo fictício), recorte da linha, alinhamento forçado
  (carta fictícia com linhas lidas com erro, palavra pulada e linha extra), filtro de aceitação, cota por pessoa e
  invólucros de caminho do treino e da avaliação.
- [x] T002 Fontes no catálogo com a evidência de licença (TraPrInq `APPROVED`, BFL `EXPERIMENT_ONLY`).
- [x] T003 TraPrInq: baixar os critérios e o menor arquivo de treino, conferir o MD5, ler o formato e as datas,
  ingerir as linhas; mais um arquivo se faltar linha para 8 mil.
  *Feito:* `Training_Set_Model9.zip` (MD5 conferido), 500 páginas de 49 documentos, 12.717 linhas, 9.234
  ingeridas (3.416 fora do dicionário, 67 com dúvida ou riscado); um arquivo bastou.
- [x] T004 BFL: baixar, transcrever a carta, detectar e ler as linhas, alinhar, filtrar, conferir 50 linhas a olho e
  ingerir as aceitas.
  *Conferência:* na 1ª amostra, 5 de 50 rótulos errados, todos por palavra partida com hífen no fim da linha
  (o trecho levado ao limite de palavra ganha ou perde um pedaço). Regra nova (`align.align_detail`): descartar a
  linha cuja fronteira bruta do alinhamento cai a mais de 1 caractere de um espaço — pega os 5 e nenhum dos 45
  certos. Na 2ª amostra (nova, 50 linhas), 1 rótulo errado (palavra da linha de baixo numa página inclinada).
  *Feito:* 945 páginas, 18.215 linhas detectadas; 33 páginas fora de 8–25 linhas; 1.801 com palavra partida;
  11.923 ingeridas, de 309 pessoas (2 a 58 por pessoa, mediana 41).
- [x] T005 Montar as listas D1–D4 pelo catálogo, cada uma como ciclo `experimento`; medir o erro do leitor atual em
  200 linhas de cada fonte nova.
  *Feito:* ciclos run-0007 (D1), run-0008 (D2), run-0009 (D3), run-0010 (D4); disponíveis 9.234 TraPrInq e 11.923
  BFL. Leitor atual nas amostras: BFL CER 30,0 % (acentos 89 %), TraPrInq 55,0 % (acentos 99 %).
- [x] T006 Treinar D1, D2, D3 e D4, um por vez, retomável, com espera de RAM; avaliar cada um nas três medidas.
  *Feito:* ~1 h por condição e 4 h o D4, sem pausa por RAM; diferenças decisivas ≥ 1,9 ponto, sem repetição.
- [x] T007 `report.md` (H1–H4 e a decisão da E4'), `resultados.json` só com números, `CLAUDE.md`, estratégia v3 e
  roadmap; apagar os zips; commit `EXP-044(document-inteligence) …`.
  *Feito:* zips apagados; as páginas da BFL em PNG (~0,6 GB) ficam no D: para realinhar.
