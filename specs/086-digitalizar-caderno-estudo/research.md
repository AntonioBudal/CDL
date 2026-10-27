# Research: Digitalizar Caderno — Foto de Página Manuscrita para Estudo

**Feature**: `086-digitalizar-caderno-estudo` | **Date**: 2026-10-27 | **Plan**: [plan.md](plan.md)

Cada decisão abaixo responde a um ponto deixado para o plano pela especificação. Formato: decisão, motivo,
alternativas descartadas.

---

## R1. Como o backend chama o motor de leitura

**Decisão**: o motor roda num **processo separado, um por pedido**, num ambiente Python próprio
(`caderno-leitura-0.1/motor/.venv`). O backend grava a imagem normalizada numa pasta temporária, executa
`<python do motor> -I -m leitorum_motor read --image <png> --out <json>` e lê o JSON de saída. O processo termina
ao fim de cada pedido.

**Motivo**:
- **NR-004**: OpenCV, ONNX Runtime e RapidOCR ficam fora do `backend/.venv`. Se o motor não estiver instalado,
  nada no backend importa essas bibliotecas e o Leitorum inicia normalmente.
- **Memória**: o pico do pipeline é de ~800 MiB (EXP-019/022). Com um processo por pedido, a memória volta ao
  sistema ao terminar, em vez de ficar presa no servidor. Isso importa numa máquina de 7,9 GB compartilhada.
- **Falha contida**: um travamento ou estouro de memória do motor derruba só o processo filho. O backend o mata
  por tempo limite ou quando o navegador desiste (cancelamento).
- **Mesmo desenho já validado**: o supervisor do `document-intelligence/` usa processo filho com limites há 20
  experimentos.

**Custo**: carregar os modelos a cada pedido. O `load_ms` medido no EXP-022 fica na casa de poucos segundos. Somado
a ~7 s de leitura, o total cabe no SC-001 (≤ 20 s); a medição real fica na validação (quickstart §3).

**Alternativas descartadas**:
- *Na mesma memória do backend*: põe dependências pesadas no `requirements.txt` (viola NR-004) e deixa ~800 MiB
  residentes no servidor.
- *Serviço HTTP local permanente* (rascunho `document-intelligence/docs/api-local.md`): segundo processo para o
  `iniciar.py` cuidar, porta extra, segredo compartilhado e memória sempre ocupada. Demais para um pedido por vez.

## R2. Onde fica o código do motor

**Decisão**: novo pacote **`caderno-leitura-0.1/motor/leitorum_motor/`**, promovido do pipeline do EXP-019
(`pipeline.py`, `merge.py`, `crop.py`, ordem de leitura). Tem `pyproject.toml` próprio e `requirements.txt`
fixado. É instalado no `motor/.venv` com `pip install ./motor`.

**Motivo**: o Leitorum é distribuído como pasta ou ZIP próprio, então o motor precisa estar dentro dela. Os
harnesses do `document-intelligence/` são código de experimento e não um pacote instalável. A promoção fica
registrada no lado do `document-intelligence/` (nota no ADR-008 e no roadmap), que continua sendo onde a pesquisa
acontece.

**O que entra e o que fica de fora**:
- **Entra**:
  - detecção PP-OCRv6 small;
  - fusão de fragmentos com os parâmetros do EXP-008 (`v_overlap 0.7`, `max_gap 1.0`, `max_angle 20`);
  - escala automática de página (alvo 80 px);
  - recorte desentortado;
  - leitura ONNX com margem de 640 px;
  - decodificação CTC com confiança por linha;
  - ordem de leitura.
- **Fica de fora**:
  - a correção lexical (R6);
  - o supervisor e o worker de benchmark;
  - a montagem de LDF 2.0 (R7).

**Alternativa descartada**: importar o harness do EXP-019 por caminho. O experimento depende do repositório de
pesquisa e de dados fora do Git, o que acopla o produto ao laboratório.

## R3. Versão do Python e dependências do motor

**Decisão**: `motor/.venv` com **Python 3.13 de 64 bits**, o mesmo interpretador do backend (Constituição III.1).
As dependências são fixadas nas versões que o `document-intelligence/` usou nos experimentos:
- `rapidocr==3.10.0`
- `onnxruntime==1.31.0`
- `opencv-python-headless==5.0.0.93`
- `numpy==2.5.4`

As transitivas também são fixadas no `motor/requirements.txt`.

**Confirmado na implementação (2026-10-27):** Python 3.13.15 instalou as mesmas versões do `uv.lock` dos
experimentos e leu o mesmo texto em 458/458 linhas (quickstart §6). Não foi preciso usar 3.12.

**Risco**: o ambiente dos experimentos (`EXP-008/envs/ppocr`) usou Python 3.12. A primeira tarefa da
implementação confirma que essas versões instalam e leem igual em 3.13, com a checagem de paridade do
quickstart §4. Se 3.13 falhar, o motor usa 3.12 via `py -3.12`, e isso é registrado. É uma decisão de ambiente,
sem efeito na API.

**Instalação**: opcional, por `py -3.13 instalar.py --motor`. Sem a flag, o `instalar.py` atual segue idêntico.
Com a flag:
1. cria o `motor/.venv`;
2. instala o motor;
3. roda `python -I -m leitorum_motor check`.

Uma falha nessa etapa é informada e **não** interrompe a instalação do Leitorum. Nenhum binário global é instalado.

## R4. Modelos, integridade e troca de leitor (FR-013, NR-003)

**Decisão**: os modelos PP-OCRv6 small de detecção e leitura **já vêm dentro do wheel do `rapidocr`** (Apache-2.0).
Não há download. O SHA-256 de cada um é conferido antes de carregar, com os mesmos valores dos experimentos:
- detecção: `090f04ab…f94f`
- leitura: `6f327246…4884`

O arquivo **`motor/config.json`** define:
- o leitor: `null` para o embutido, ou caminho e SHA-256 de outro ONNX;
- `license_status`;
- alvo de escala;
- parâmetros de fusão;
- limiar de baixa confiança.

O motor **recusa** carregar um leitor cujo `license_status` não seja `VERIFIED`. Isso barra por construção o leitor
ajustado no BRESSAY (`NEEDS VALIDATION`).

Trocar o leitor por um treinado com dados licenciados significa trocar o arquivo e atualizar `config.json`.
Frontend e API não mudam (FR-013).

**Sem rede** (FR-004, SC-003):
- O motor confere que os arquivos de modelo existem **antes** de iniciar o RapidOCR, para que a biblioteca nunca
  tente baixá-los.
- O backend não faz chamada externa.
- A validação inclui rodar o motor com a rede desligada (quickstart §3).

## R5. Imagem: formatos, orientação e limites (FR-002)

**Decisão**: o backend valida e normaliza com o **Pillow**, que já é dependência do backend. Os passos:
1. Lê o upload em blocos e recusa acima de **20 MB** com `413`.
2. Abre com o Pillow:
   - aceita só os formatos `JPEG`, `PNG` e `WEBP`;
   - qualquer outro formato recebe `415`;
   - arquivo corrompido ou truncado recebe `422`.
3. Recusa imagens acima de **40 megapixels** (`413`), o que também protege contra bombas de descompressão.
4. Aplica `ImageOps.exif_transpose`, no mesmo padrão do `avatar_service.py`.
5. Converte para RGB e grava como PNG sem perda na pasta temporária.

Não reduz a imagem: o pipeline só amplia. Uma foto de 12 MP de uma página tem linhas na faixa em que o alvo de
80 px funciona.

**HEIC**: fora do escopo. No iPhone, o seletor de arquivo do navegador entrega JPEG. Se chegar HEIC, a resposta é
`415` com orientação.

## R6. Correção lexical: fica de fora desta fatia

**Decisão**: o motor do produto **não** aplica a correção lexical do EXP-011.

**Motivo**:
- **Ganho pequeno**: no EXP-011 e no EXP-012, a correção tirou quase nada de CER e 5 a 7 pontos de WER.
- **Licença**: o léxico deriva do `wordfreq`, cujos dados são CC-BY-SA 4.0. Levar uma lista derivada ao produto
  pede uma decisão de licença própria.
- **Texto mais fiel**: sem a correção, o texto devolvido é o lido de fato, o que ajuda a revisar com a foto ao lado.

**Consequência**: o CER esperado do produto é o do leitor original sem correção, praticamente igual aos 24–27 %
medidos com correção. A paridade do quickstart §4 compara contra a leitura bruta do EXP-022, que é anterior à
correção.

## R7. LDF 2.0: não é produzido nesta fatia

**Decisão**: a resposta é uma **pré-visualização simples**, com texto, confiança e caixa por linha, além de avisos e
identificação do motor. Ela não é um documento LDF 2.0.

**Motivo**: nada é persistido além do Estudo (NR-001), e o validador LDF mora no pacote `leitorum_di`, que tem
dependências próprias. Os campos por linha (`bbox`, `text`, `confidence`) são o subconjunto de
`recognition.lines` do LDF 2.0. Assim, uma fatia futura que guarde o LDF pode montá-lo a partir da mesma saída do
motor, sem mudar o contrato.

## R8. Um pedido por vez, memória e cancelamento (FR-005, FR-011)

**Decisão**:
- **Fila**: há um `asyncio.Lock` global do serviço. Se o lock estiver ocupado, a resposta é imediatamente
  **`503` com código `busy`** e `Retry-After: 15`, sem fila. A tela mostra "outro pedido está sendo lido, tente em
  instantes".
- **Memória**: antes de iniciar, o serviço mede a memória livre do sistema:
  - no Windows, pela função `GlobalMemoryStatusEx` via `ctypes`;
  - no Linux, por `/proc/meminfo`;
  - sem medida possível, o pedido segue.

  Abaixo de **2 GiB** livres (pico de ~800 MiB mais 1 GiB de reserva, a regra da máquina), a resposta é **`503` com
  código `low_memory`**. O limite pode ser mudado por `LEITORUM_DIGITIZE_MIN_FREE_MB`.
- **Tempo**: o processo do motor é morto após **120 s** e a resposta é `504` com código `timeout`.
- **Cancelamento**: enquanto o motor roda, o endpoint assíncrono verifica a cada 250 ms se o processo terminou e
  se o cliente desconectou (`request.is_disconnected()`). Em caso de desconexão, mata o processo.
- **O processo é iniciado com `subprocess.Popen`**, sem o `asyncio` de subprocessos, para não depender do tipo de
  event loop do Uvicorn no Windows.
- **A saída vai para um arquivo**, não para `stdout`, para evitar travamento por buffer cheio.
- **Limpeza** (FR-005, SC-002): a pasta temporária vem de `tempfile.TemporaryDirectory`. O diretório de
  temporários do sistema é usado, e nunca a pasta de dados do Leitorum. A pasta é removida num `finally` que cobre
  sucesso, erro, tempo esgotado e cancelamento. A remoção tenta de novo por até 2 s, porque o Windows pode segurar
  o arquivo por instantes depois que o processo morre.

## R9. Disponibilidade do motor (FR-012, SC-004)

**Decisão**: o endpoint `GET /api/digitize/status` responde `{available, reason}`.

A primeira consulta roda `python -I -m leitorum_motor check`, que confere o interpretador, o pacote e o SHA-256
dos modelos. O resultado fica em memória até o servidor reiniciar ou até um pedido de leitura falhar por
integridade.

O caminho do interpretador vem de `LEITORUM_MOTOR_PYTHON`. Se a variável não estiver definida, vale
`motor/.venv/Scripts/python.exe` no Windows ou `motor/.venv/bin/python` nos demais sistemas. O motivo devolvido em
`reason` não expõe caminhos internos (Constituição, padrões de backend).

## R10. Linhas de baixa confiança (FR-006)

**Decisão**: a confiança da linha é a média das probabilidades dos caracteres mantidos na decodificação CTC, já
calculada pelo pipeline. Uma linha é marcada `low_confidence` quando a confiança fica abaixo de
`config.json → low_confidence`.

**Valor final: 0,75** (calibrado; ver quickstart §6). **Valor inicial do plano: 0,80.** Uma tarefa de calibração usa as leituras já existentes do `document-intelligence/`. Ela
mede, só com números, quanto o CER das linhas marcadas supera o das não marcadas e qual fração das linhas é
marcada. A meta é marcar no máximo cerca de 1 em cada 4 linhas. O valor final fica registrado no `config.json`.

**Na tela**:
- um textarea comum para editar;
- acima dele, a lista "Linhas para conferir", com o número e o início de cada linha incerta;
- cada item é um botão que seleciona aquele trecho no editor.

A marcação usa texto e ícone, não só cor. Se a linha já foi editada e não é mais encontrada, o item diz "já
revisada" e fica desativado.

**Alternativa descartada**: um campo por linha. Atrapalha juntar ou dividir linhas, que é a correção mais comum
de um texto lido automaticamente.

## R11. Tela: câmera e arquivo

**Decisão**: dois botões, os dois com `<input type="file" accept="image/jpeg,image/png,image/webp">`:
- **"Tirar foto"** usa `capture="environment"`, que abre direto a câmera traseira no celular;
- **"Escolher imagem"** não usa `capture`, para permitir escolher da galeria ou dos arquivos.

Não usa `getUserMedia`. O seletor do sistema é mais simples, funciona em HTTP na rede local e não pede permissão
de câmera ao navegador.

A foto aparece ao lado do texto na revisão, por URL `blob:`, que a CSP já permite em `img-src`. Ela fica só na
memória do navegador e a URL é revogada ao sair da tela ou começar outra página.

## R12. Salvar como Estudo (FR-007, FR-008, SC-006)

**Decisão**: o salvamento usa `api.createStudy` (`POST /api/studies`), como o `useImportDraft`. O payload é:
- `chapter_id`, `title`;
- `[seção escolhida]`: o texto revisado;
- `source_response`: o texto lido automaticamente, sem correções, com as linhas unidas por quebra de linha.

O status "rascunho" não vai no payload: o `StudyCreate` do backend não aceita `reading_status`, e o modelo de
Estudo já nasce com `reading_status = 'rascunho'`. Um teste de backend confirma esse valor no estudo criado.

A seção inicial é **Resumo**. Livro e capítulo vêm pré-selecionados com a última escolha da sessão, se ainda
existir.

Ações até salvar: destino (livro e capítulo), título, seção opcional e "Salvar como estudo". São 4, o que atende
o SC-006.

A regra `analysis_not_blank` do Estudo já impede salvar texto vazio. A tela desabilita o botão antes disso.

## R13. O que acontece com a tela da feature 069

**Decisão**: o `DigitizeNotebookView.vue` é **reescrito**. Do original ficam:
- a rota (`/digitalizar`, alias `/scan`, nome `digitize-notebook`);
- o título;
- a mensagem de processamento local;
- os atalhos de saída (`DIGITIZE_EXIT_SHORTCUTS`).

Saem a matriz de maturidade (`DOCUMENT_INTELLIGENCE_STAGES`) e a promessa "sem data de lançamento".

O teste `feature-069-document-intelligence-placeholder.test.mjs` é **substituído** por
`feature-086-digitalizar-caderno-estudo.test.mjs`. As proibições da 069 (sem input de arquivo, sem rede) deixam
de valer, conforme a spec. As garantias que continuam valendo (rota, zero emojis, mensagem local, atalhos de
saída) passam para o teste novo.

No Ateliê de Importação, o card troca o selo "Em Pesquisa" por "Rascunho a revisar".
