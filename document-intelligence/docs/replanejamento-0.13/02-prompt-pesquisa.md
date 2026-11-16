# Etapa 2 — Prompt de pesquisa técnica (executado pelo usuário fora do projeto)

Gerado em 2026-11-16 a partir do [EXP-027](../../experiments/EXP-027-analise-50-paginas/report.md) e da
diretriz de [modelos próprios](../objetivo-modelos-proprios.md). O resultado da pesquisa deve ser salvo em
`docs/replanejamento-0.13/03-resultado-pesquisa.md` (ou `.txt`) para a Etapa 3.

---

## Prompt (copiar a partir daqui)

Você é um pesquisador técnico sênior em reconhecimento de texto manuscrito (HTR), OCR de documentos e modelos
visão-linguagem (VLM). Faça uma pesquisa profunda e devolva um relatório em **português do Brasil**, com uma
parte em linguagem acessível (para quem decide sem formação na área) e um apêndice técnico. Exija de si mesmo
**fontes primárias** (papers, documentação oficial, cards de modelo, páginas de licença, leaderboards oficiais),
cite cada afirmação, e **separe explicitamente fato (com fonte) de inferência sua**. Onde não houver evidência,
diga "não encontrei evidência" em vez de supor. Data de referência: novembro de 2026; prefira resultados dos
últimos 24 meses e diga a data de cada fonte.

### 1. O problema

Um aplicativo local de cadernos de estudo lê **fotos de celular de páginas de caderno manuscritas em português
do Brasil** e devolve o texto para o usuário revisar. Características das páginas (medidas em 51 páginas reais de
um usuário): escrita cursiva em 55 %, mista (cursiva + forma na mesma página) em 35 %, letra de forma em 10 %;
fórmulas matemáticas em 59 % das páginas (12 % dos caracteres nas páginas de teste); listas, setas, notas de
margem, títulos, pequenos diagramas; papel de caderno; fotos consideradas boas pelo usuário. Cerca de 19 linhas
e 525 caracteres por página.

**Pipeline atual** (100 % local, CPU): detecção de linhas de texto PP-OCRv6 small (via rapidocr, ONNX) →
fusão de fragmentos → escala automática da página (linhas a ~80 px) → recorte desentortado de cada linha →
reconhecimento PP-OCRv6 small (modelo de reconhecimento de cena/impresso, latino, sem treino em manuscrito
português), inferência direta pelo ONNX Runtime com margem à direita → ordem de leitura de cima para baixo.
Sem correção lexical. ~7 s por página em CPU.

**Resultado medido em 20 páginas de teste congeladas** (referência transcrita por um modelo multimodal grande e
conferida pelo usuário; medida em nível de página):

- CER 56 % (mediana por página 53 %, de 32 % a 83 %); WER 90 %.
- CER só em texto comum: 54 %. CER só em fórmulas: 73–77 %. Fórmulas respondem por 12–16 % do erro total.
- Cursiva 50 %, letra de forma 55 %, mista 63 % — a cursiva **não** é pior.
- 28 % das palavras da referência não aparecem na saída; em 7 de 20 páginas a saída tem só 30–67 % do tamanho
  esperado (texto que não chega a ser lido: provável falha de detecção/cobertura, ainda não separada da
  falha de reconhecimento por falta das caixas).
- Das palavras erradas, 18 % estão a 1–2 letras da certa; um dicionário de 50 mil palavras corrigiria sem
  ambiguidade 4 % delas; 193 palavras erradas são palavras válidas do português.
- Um modelo multimodal grande de nuvem transcreveu as mesmas fotos de forma "praticamente perfeita" segundo o
  usuário (não medido numericamente). Ou seja: o problema é resolvido por modelos grandes; a pergunta é o que é
  possível **localmente** e, depois, com **modelos próprios**.

**Histórico medido no projeto (dados públicos, digitalizados, não fotos):** o mesmo reconhecedor PP-OCRv6
small tem CER de linha 29,7 % em redações manuscritas em português (BRESSAY, licença não comercial); um ajuste
fino (fine-tuning) com menos de uma época em CPU levou a 13,6 %; a curva de aprendizado mostrou que ~50 páginas
transcritas dão 88 % do ganho e ~150 páginas chegam ao mesmo resultado de 647 páginas; degradar artificialmente
digitalizações como "foto" não ensina o modelo a ler fotos. Detecção de linhas: o detector PP-OCRv6 deu F1
0,81 em fotos de manuscrito em inglês (GNHK) e 0,98 em digitalizações; Doc-UFCN ficou em 0,43/0,68.

### 2. Restrições não negociáveis

1. **Local e sem custo por uso**: nada de API paga ou serviço em nuvem no produto; tudo roda no computador do
   usuário. Pesos públicos são permitidos se a licença permitir uso local e redistribuição com o produto.
2. **Hardware de referência**: notebook com Intel i5-8265U (4 núcleos), 7,9 GB de RAM, GPU NVIDIA MX110 de
   2 GB (inútil para isso); Windows 11; Python 3.13. Considere também um cenário "GPU emprestada por algumas
   horas" (nuvem ou máquina de terceiros) **só para treino**, nunca para inferência, e diga o custo em horas.
3. **Objetivo final: modelos próprios** — arquitetura, pesos, dados e treino sob controle do usuário, sem
   depender de fornecedor. Modelos de pesos abertos (Qwen, Gemma etc.) servem como **baseline** e como
   **professores** (geram rascunhos que o usuário corrige e que viram dados de treino). Todo modelo externo
   usado deve poder ter cópia exata guardada (revisão, hash, texto da licença).
4. **Licenças**: para cada modelo, dataset ou ferramenta, informe a licença do código **e** a dos pesos/dados,
   separadamente, e se permite (a) uso local num produto, (b) ajuste fino com os pesos resultantes passando a
   ser do usuário, (c) uso das saídas como dados de treino de outro modelo. Sinalize termos de uso que proíbam
   destilar ou treinar modelos concorrentes.
5. **Português do Brasil**: acentos, cedilha, til; abreviações de estudante; termos técnicos.

### 3. O que responder, etapa por etapa

Para **cada etapa** abaixo, compare três caminhos e preencha uma tabela: **(a) modelo próprio treinado do
zero**, **(b) ajuste fino de modelo aberto** (pesos resultantes nossos), **(c) uso direto de modelo externo
aberto**. Colunas: candidatos concretos (nome, tamanho, licença do código, licença dos pesos), qualidade
esperada com números de benchmark e a fonte, dados necessários (quantas páginas/linhas, de que tipo, se
precisam de caixas de linha ou só texto), custo de treino (horas em CPU de 4 núcleos; horas em GPU emprestada;
RAM/VRAM), custo de inferência em CPU (RAM, segundos por página), risco. Termine cada etapa com uma frase que
diga **o que é viável treinar do zero em hardware doméstico e o que não é**, com honestidade.

1. **Pré-processamento da foto**: retificação de perspectiva/curvatura, remoção de sombra, binarização,
   detecção da página. Quanto isso melhora a leitura em fotos de celular, segundo evidência? Ferramentas locais.
2. **Detecção de linhas e regiões de texto em páginas de caderno fotografadas** (cobertura é o problema:
   28 % das palavras somem). Candidatos: detectores PP-OCR (DB/DB++) ajustados, Doc-UFCN, Kraken/segmentation,
   YOLO-based (atenção à AGPL), DocLayout-YOLO, Surya, abordagens que dispensam a detecção (VLM de página
   inteira). Quantas páginas anotadas com caixas são necessárias para ajustar um detector? Existe anotação
   automática confiável a partir de um VLM?
3. **Reconhecimento de texto manuscrito em português (o maior erro: 54 % em texto comum)**:
   - (b) ajuste fino de: PP-OCRv6/PP-OCRv5 rec (CTC, pequeno), TrOCR (base/small/large, handwritten), PyLaia,
     Kraken, Donut/Nougat-like, SmolDocling, Florence-2, outros que você encontrar; qualidade reportada em
     manuscrito (IAM, RIMES, READ, BRESSAY, LHTR-br, qualquer dataset PT) e o que se sabe sobre fotos.
   - (c) VLMs abertos para OCR/HTR, rodando em CPU quantizados: Qwen3-VL (2B/4B/8B), Qwen2.5-VL, Gemma 3/mais
     novos com visão, InternVL, MiniCPM-V, Pixtral, Florence-2, GOT-OCR 2.0, olmOCR, DeepSeek-OCR, PaddleOCR-VL,
     dots.ocr, Chandra, MinerU, Nanonets-OCR, outros. Para cada: evidência em **manuscrito** (não só impresso),
     evidência em português, tamanho quantizado, RAM necessária, velocidade em CPU, licença, se o projeto
     llama.cpp/mtmd ou ONNX os suporta.
   - (a) do zero: arquiteturas CTC (CRNN, VAN, PyLaia) e transformer pequenos; quantos dados e horas; o que a
     literatura diz sobre treinar HTR do zero com poucas centenas de páginas de um só autor (modelo
     personalizado) vs. muitos autores; geração sintética de manuscrito (fontes cursivas, GANs, difusão,
     renderização com variação) como suplemento, com evidência de ganho.
   - **Destilação**: um VLM aberto grande (ou de nuvem, respeitando termos) transcreve; o usuário corrige;
     treina-se um modelo pequeno. Evidência de que funciona para HTR e quantas páginas.
4. **Fórmulas e símbolos matemáticos manuscritos** (73–77 % de CER hoje; 12–16 % do erro): vale um módulo
   separado (pix2tex/LaTeX-OCR, UniMERNet, Nougat, TexTeller, modelos do CROHME/HME100K/MathWriting) ou o
   próprio reconhecedor/VLM deve tratar texto e fórmula misturados na mesma linha? Como detectar que um trecho
   é fórmula? Qualidade reportada em manuscrito. Responda explicitamente à hipótese "precisamos reconhecer
   fórmulas e converter para LaTeX": é prioridade dado que respondem por 12–16 % do erro?
5. **Ordem de leitura e layout de caderno** (listas, notas de margem, setas, duas colunas): métodos leves,
   VLM, ou regras; evidência.
6. **Correção depois da leitura** (dicionário, distância de edição, modelo de linguagem pequeno, LLM local):
   evidência de ganho em função do CER de entrada. Responda explicitamente à hipótese "uma IA secundária que
   corrige palavras com 1–2 letras erradas e aprende com os pares erro→correção": com 18 % das palavras erradas
   a 1–2 letras e 11 % de palavras certas, isso vale a pena agora, mais tarde, ou dentro do próprio reconhecedor
   (decodificação com modelo de linguagem, beam search com léxico)?
7. **Dados**: datasets públicos de manuscrito em português com licença compatível com produto (verifique
   BRESSAY, LHTR-br, PorTEXTO, qualquer outro; diga a licença exata); como coletar e anotar as páginas do
   próprio usuário com o menor esforço (ferramentas de transcrição linha a linha, anotação de caixas,
   uso de VLM como pré-anotador); como manter um conjunto de teste congelado válido enquanto o banco cresce
   com correções do usuário (contaminação, drift de letra do mesmo autor); quantas páginas por degrau.
8. **Treino em casa**: o que cabe em CPU de 4 núcleos com 8 GB (modelos, tamanhos de lote, horas); o que exige
   GPU; opções gratuitas ou baratas de GPU por horas (com restrições de termos); quantização e exportação
   para ONNX/GGUF para inferência em CPU; ferramentas (PaddleOCR, Transformers, llama.cpp, ONNX Runtime).
9. **Trajetória de substituição**: proponha, com base no que encontrou, a sequência mais plausível de
   "externo (c) → ajustado (b) → próprio (a)" para cada etapa, com o critério de troca (igualar ou superar o
   baseline no conjunto de teste congelado) e a ordem de prioridade pelo ganho esperado.

### 4. Formato da resposta

1. **Resumo executivo acessível** (1 página): onde está o maior ganho, em que ordem atacar, o que é viável em
   casa, o que não é, e respostas diretas às três hipóteses (fórmulas, cursiva/modelo, correção).
2. **Uma seção por etapa (1 a 9)** com a tabela (a)/(b)/(c) e o veredito de viabilidade doméstica.
3. **Tabela-mestra de candidatos**: modelo/ferramenta, tamanho, licença do código, licença dos pesos,
   roda em CPU 8 GB?, evidência em manuscrito, evidência em português, fonte com data.
4. **Riscos e incertezas**: o que depende de evidência que não existe; o que precisa ser medido localmente.
5. **Lista de fontes** com URL e data. Não invente fontes; se não tiver certeza de uma URL, diga.

Não recomende nada pago por uso. Não presuma GPU no computador do usuário. Quando um número de benchmark vier
de um dataset diferente do caso (fotos de caderno em português), diga isso e estime a distância com cautela.
