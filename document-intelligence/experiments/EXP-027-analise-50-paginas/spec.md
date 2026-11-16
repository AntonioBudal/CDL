# EXP-027 — Análise das 50 páginas reais do caderno (especificação, plano e tarefas)

**Created**: 2026-11-16 · **Status**: `DRAFT` — aguarda (1) a autorização escrita do usuário para usar o
livro de teste e seus 50 estudos e (2) a exportação do material para fora do banco do Leitorum. Nada foi lido,
copiado nem executado sobre dados reais.

**Numeração**: o EXP-026 está reservado pelo [STATE do EXP-024](../EXP-024/STATE.md) (decisão de ligar o
adaptador de referência, à espera de 30 registros de feedback); por isso este é o EXP-027. O nome da pasta e o
`report.md` seguem o pedido do usuário de 2026-11-16.

**Input**: o usuário digitalizou 50 páginas reais do caderno como 50 estudos pela tela `/digitalizar` do
Leitorum (feature 086, motor `caderno-leitura-0.1/motor`, pipeline do ADR-008 com o leitor original PP-OCRv6
small, sem correção lexical). "Nenhum resultado ficou minimamente aceitável." Muitas páginas têm cursiva e
fórmulas. Objetivo de longo prazo: qualidade próxima à dos grandes modelos multimodais, 100 % local, sem custo
por uso. Este experimento é a **Etapa 1** do replanejamento a partir do Roadmap 0.13: medir onde está o erro
antes de decidir o que construir.

## Pergunta

Nas 50 páginas, de onde vem o erro de leitura (foto, detecção de linhas, reconhecimento de caracteres,
fórmulas, ordem de leitura) e quanto cada origem pesa? Qual é o maior ganho possível e o que os dados dizem
sobre as três hipóteses do usuário?

## Hipóteses (todas a confirmar, refutar ou substituir pelos dados)

- **H1 — fórmulas.** Pelo menos 25 % dos caracteres errados estão dentro de trechos de fórmula marcados na
  referência. Se ficar abaixo de 10 %, fórmulas não são a prioridade do próximo roadmap.
- **H2 — cursiva.** Nas linhas bem detectadas, o CER das páginas cursivas é pelo menos 1,5× o das páginas em
  letra de forma. Mede se o problema principal é o reconhecedor diante da caligrafia.
- **H3 — correção de palavras.** Pelo menos 30 % das palavras erradas estão a distância de edição 1 ou 2 de
  uma palavra da referência (teto de ganho de uma etapa de correção). Mede-se também quantas dessas correções um
  dicionário de português resolveria sozinho e quantas precisariam de contexto.
- **H4 — alternativa: a perda é antes da leitura.** Linhas não detectadas, fragmentadas ou unidas respondem
  por mais erro de página do que a leitura dentro das linhas bem detectadas. Se H4 se confirmar, a prioridade
  é detecção/foto, mesmo contradizendo H1 e H2.
- **H5 — referência local.** Um modelo visão-linguagem (VLM) local quantizado, em CPU, lê as mesmas páginas
  com CER de página pelo menos 10 pontos menor que o motor. Só referência do que já é possível localmente; não
  é adoção.

## Material, privacidade e conjunto congelado

- **Origem:** fotos e textos do livro de teste do usuário, exportados por ele para
  `dataset/raw/exp-027/` (coberto pelo `.gitignore`: `dataset/raw/*`). Nada desse material vai para o Git, para
  relatórios ou para o chat; os relatórios trazem só números, categorias e nomes neutros (`p01`…`p50`).
- **Exemplos de falha (5 a 10):** recorte + saída + esperado gravados em `dataset/processed/exp-027/exemplos/`
  (fora do Git), para o usuário abrir localmente; o `report.md` descreve cada um só por categoria e número.
- **Conjunto de teste congelado:** ~20 páginas, estratificadas por tipo de escrita (cursiva / forma / misto),
  presença de fórmulas e qualidade da foto, sorteadas com semente fixa depois da classificação manual. Manifesto
  com o SHA-256 de cada foto em `splits/test-manifest.json` (dentro da pasta do experimento, versionado: só
  hashes e categorias). Essas páginas nunca entram em treino, ajuste de prompt, limiares, dicionários ou
  correções, neste ou nos próximos experimentos. As ~30 restantes são o conjunto de desenvolvimento.

## Referência (ground truth)

Não há transcrição de referência conhecida. O texto revisado pelo usuário no estudo, quando existir, não serve
como referência linha a linha (vai para seções e pode ter sido reorganizado), mas serve de apoio.

- **Formato:** um arquivo `pNN.txt` (UTF-8) por página, **uma linha por linha física do caderno**, na ordem de
  leitura; acentos e pontuação fiéis; fórmulas entre `$…$` em LaTeX simples (`$x^2 + 1$`); `[figura]` para
  desenho ou diagrama; `[?]` para trecho ilegível. A marcação `$…$` é o que permite medir H1.
- **Quantidade:** as 20 páginas de teste são obrigatórias para toda métrica (~600 linhas, estimativa de 30
  linhas por página). As outras 30 (~900 linhas) são opcionais para a Etapa 1, mas necessárias depois para
  qualquer ajuste do leitor (EXP-018: ~50 páginas dão 88 % do ganho medido).
- **Ferramenta mais rápida:** uma página HTML local, sem rede, gerada pelo experimento, que mostra a foto e os
  recortes de linha do motor com o texto lido já preenchido para corrigir, e salva os `pNN.txt`. Regra: ler a
  foto antes de aceitar o texto preenchido, porque o preenchimento tende a preservar erros do motor; as 20
  páginas de teste recebem uma segunda passada de conferência. Estimativa: 3 a 5 min por página preenchida.

## Método

1. **Inventário:** versão do motor, configuração (`config.json`), SHA-256 dos modelos, hardware (i5-8265U,
   7,9 GB de RAM, CPU-only), formato e resolução das fotos exportadas, se chegaram cruas da câmera ou já
   recortadas pelo navegador (feature 112).
2. **Reprodução:** rodar o motor do produto (`leitorum_motor read`) sobre cada foto exportada, para ter saídas
   reproduzíveis e as caixas das linhas; conferir contra o `source_response` dos estudos quando a imagem for a
   mesma.
3. **Classificação manual por página:** escrita (cursiva / forma / misto), fórmulas (nenhuma / poucas / muitas),
   foto (iluminação, ângulo, desfoque: boa / média / ruim), papel (branco / pautado / quadriculado) e layout
   (uma coluna / notas laterais / diagramas). Registrada no manifesto.
4. **Métricas:** CER e WER por página e no total (normalização aprovada: pontuação de borda removida, acentos e
   caixa preservados), com a referência congelada.
5. **Quebra do erro por origem**, nesta ordem, cada etapa medida com a anterior já contabilizada:
   - linhas da referência sem correspondência (não detectadas), detectadas em pedaços ou unidas → erro de
     **detecção**;
   - ordem das linhas correspondidas diferente da referência → erro de **ordem de leitura**;
   - CER dentro das linhas bem correspondidas → erro de **reconhecimento**, separado em trechos de fórmula e
     texto comum (H1, H2);
   - correlação do CER com a qualidade da foto (classes de 3) → **foto**.
6. **Palavras quase certas (H3):** entre as palavras erradas das linhas correspondidas, fração a distância 1 e
   2 da palavra de referência; quantas dessas um dicionário de português resolve sem ambiguidade; ganho máximo
   de WER se todas fossem corrigidas.
7. **Referência VLM local (H5):** `llama.cpp` (MIT) com um Qwen3-VL quantizado (Apache-2.0), em CPU, nas
   mesmas páginas, com um só prompt fixo definido **antes** de ver as páginas de teste; CER/WER de página e
   tempo por página. Gemma só se houver tempo e RAM. Registro no registry de modelos com licença.
8. **Exemplos:** 5 a 10 falhas representativas (uma por origem de erro pelo menos), fora do Git.
9. **Relatório:** `report.md` com tabelas, veredito de H1 a H5 e a conclusão: onde está o maior ganho possível.

## Hardware, RAM e disco

- Máquina CPU-only (MX110 2 GB não serve). RAM física livre em uso normal: ~0,9 a 1,5 GB; o VLM de 4B
  quantizado precisa de ~4–5 GB livres (o de 2B, ~2,5 GB). A corrida do VLM fica para um momento com os
  outros programas fechados, em segundo plano, com espera de RAM e retomável página a página.
- Disco: `document-intelligence/` usa hoje ≥ 8,5 GB em dados e modelos mais os ambientes dos experimentos;
  o VLM acrescenta ~3 GB. Medir antes do download; se passar de 20 GB, perguntar e migrar para D:.

## Tarefas

- [ ] **T000** (usuário) Autorização escrita e exportação do material para `dataset/raw/exp-027/`.
- [ ] **T001** Inventário, reprodução das leituras com o motor e manifesto das páginas (sem referência ainda).
- [ ] **T002** Classificação manual das páginas e sorteio estratificado do conjunto de teste congelado; hashes.
- [ ] **T003** Ferramenta local de transcrição; (usuário) transcrever ao menos as 20 páginas de teste.
- [ ] **T004** Métricas, quebra por origem, palavras quase certas, exemplos.
- [ ] **T005** Referência VLM local.
- [ ] **T006** `report.md` e benchmark JSON em `evaluation/benchmarks/`.
