# Instruções Operacionais para o Claude Code — Leitorum Document Intelligence

Bem-vindo ao subprojeto **`document-intelligence/`** do ecossistema **Leitorum**.

---

## 1. Regra Absoluta de Escopo

Você está atuando com **responsabilidade exclusiva dentro do diretório `document-intelligence/`**.
- **NUNCA** modifique arquivos fora de `document-intelligence/` (especialmente `frontend/`, `backend/`, `caderno-leitura-0.1/` ou o banco de dados `caderno.db`).
- Toda a sua inteligência, código, testes, modelos e dados devem residir dentro desta pasta.
- Leia o arquivo [`AGENTS.md`](./AGENTS.md) na íntegra para compreender a constituição e os princípios inegociáveis.

---

## 2. Gerenciamento do Ambiente com `uv`

Este é um projeto Python independente gerenciado com **`uv`**. O namespace do pacote é **`leitorum_di`**.

Comandos fundamentais a partir de `document-intelligence/`:

```powershell
# Sincronizar o ambiente virtual e dependências
uv sync

# Executar a suíte de testes automatizados
uv run pytest

# Executar com verbosidade
uv run pytest -v

# Verificar formatação e linter
uv run ruff check .

# Executar comandos do módulo
uv run python -m leitorum_di
```

---

## 3. Estado Atual do Projeto e Próxima Tarefa

- **Status**: **`EXP-000` aceito pelo usuário em 2026-09-30** (ver [`experiments/EXP-000/RESULTS.md`](./experiments/EXP-000/RESULTS.md)).
- **EXP-001 aceito em 2026-10-02**, com o [ADR-001](./docs/adr/ADR-001-nao-adotar-htr-pronto-sem-portugues.md) aceito: nenhum HTR pronto sem treino em português é adotado.
- **EXP-002 aceito em 2026-10-05**, com o [ADR-002](./docs/adr/ADR-002-segmentacao-de-layout-doc-ufcn-heron.md) aceito: Doc-UFCN `norhand` (linhas), Docling Heron (blocos) e retificação por contorno são a direção de trabalho; nada entra em `src/` sem validação em fotos reais e spec de produto. A exceção de licença do docTR (`NEEDS VALIDATION`) valeu só para o EXP-002.
- **EXP-003 aceito em 2026-10-12**, com o [ADR-003](./docs/adr/ADR-003-ordem-de-leitura-por-ancoragem.md) aceito: ordem de leitura por ancoragem de regiões laterais; a detecção de blocos é o gargalo de ponta a ponta.
- **Contrato LDF 2.0 aceito em 2026-10-12**, com o [ADR-004](./docs/adr/ADR-004-contrato-ldf-2.0.md) aceito (feature [`specs/001-contrato-ldf/`](./specs/001-contrato-ldf/)): fonte normativa em `src/leitorum_di/contracts/ldf/schemas/ldf-2.0.schema.json`, descrição em [`docs/ldf.md`](./docs/ldf.md). O schema 2.0 não é mais editado; mudança entra como versão nova.
- **EXP-007 aceito em 2026-10-13**, com o [ADR-005](./docs/adr/ADR-005-layout-nao-confirmado-em-imagens-reais.md) aceito: a direção de layout do ADR-002 **não se confirma** em imagens reais (F1 de linhas 0,35–0,37 contra 0,78–0,93 no sintético); retificação por contorno suspensa; Heron só como detector da região de texto. **Regra nova:** nenhum componente de layout vira direção de trabalho sem medição em imagens reais; as divisões de teste do GNHK e do BRESSAY são o benchmark de referência para linhas.
- **EXP-008 executado em 2026-10-14** ([RESULTS](./experiments/EXP-008/RESULTS.md), [ADR-006](./docs/adr/ADR-006-deteccao-de-linhas-pp-ocr.md) `ACCEPTED` por delegação em 2026-10-18): o detector de texto do PP-OCRv6 (via `rapidocr`, ambiente `experiments/EXP-008/envs/ppocr`) + fusão de fragmentos dá F1 de linhas 0,812 (GNHK) e 0,982 (BRESSAY); Doc-UFCN fica em 0,428 e 0,675.
- **EXP-009 executado em 2026-10-14 por delegação** ([RESULTS](./experiments/EXP-009/RESULTS.md), [ADR-007](./docs/adr/ADR-007-leitura-pp-ocr-sem-portugues-suficiente.md) `ACCEPTED` por delegação em 2026-10-18): o reconhecedor PP-OCRv6 small lê as linhas do EXP-001 com CER 38,5 % (antes 69,4 %) e inglês fotografado com 14,8 %; acentos com 80 % de erro; ADR-001 mantido.
- **EXP-010 executado em 2026-10-14 por delegação** ([RESULTS](./experiments/EXP-010/RESULTS.md); evidência acrescentada ao ADR-007): melhor leitura em português é o PP-OCRv6 small com recorte ampliado 2× (CER 34,4 %); medium (58,7 %) e latino (42,8 %) não superam. Modelos novos em `models/exp-010/` (fora do Git).
- **Autonomia (usuário, 2026-10-18):** "não precisa me pedir para tomar decisões mais, sempre aceitarei o seu plano e suas permissões". Planos, instalações e aceites passam a ser feitos **por delegação**, registrados como tal; as regras do projeto (escopo, privacidade, licenças, disco, RAM, nada em `src/` sem validação em caderno) continuam valendo.
- **EXP-011 concluído em 2026-10-18 por delegação** ([RESULTS](./experiments/EXP-011/RESULTS.md)): correção lexical depois do small 2× dá WER 67,0 % e CER 33,8 % (antes 74,1 % e 34,4 %); ajuda pouco.
- **Tarefa Atual**: [`EXP-012`](./experiments/EXP-012/spec.md) — pipeline integrado de ponta a ponta (detecção + fusão + leitura 2× + correção lexical → LDF 2.0), por delegação.
  - **Dados do EXP-007:** GNHK em `dataset/raw/exp-007/gnhk/` e imagens de trabalho em `dataset/processed/exp-007/`, fora do Git. Nenhuma imagem, recorte ou transcrição desses datasets vai para o Git, para relatórios ou para o chat.
  - **Congelados:** `docs/schemas/ldf-1.0.schema.json` e os diretórios `experiments/EXP-001` a `EXP-003` não podem ser alterados (`tests/ldf/test_frozen.py` confere). Saídas novas usam `leitorum_di.contracts.ldf.build_document`. Ao rodar algo nos ambientes dos EXP-001/002, use `uv run --frozen --project …` (sem `--frozen` o `uv` reescreve o `uv.lock` do ambiente).
  - **Regra de workflow (usuário, 2026-09-30):** todo experimento segue o ciclo Spec Kit adaptado — Specify → Plan → Tasks — e a especificação/plano é apresentada **antes** de qualquer código de avaliação, script de inferência ou download de pesos.
  - **Ritmo fatiado (usuário, 2026-09-30):** nos próximos experimentos e features, produza **um artefato por vez** e aguarde a revisão antes do seguinte (Specify → aprovação → Plan → aprovação → Tasks → aprovação). Na execução, desde 2026-10-07 **não é preciso parar a cada checkpoint**: siga pelas fases com o próprio julgamento e pare só no aceite final ou em bloqueio real (licença em aberto, disco acima do teto, RAM insuficiente, decisão do usuário).
  - Commits: padrão `FNN(document-inteligence) <nome da fase>`, definido pelo usuário em 2026-09-30.
  - Exceções de licença em vigor (só uso experimental local, nunca produto): pesos do TrOCR small e dataset BRESSAY, ambos `LICENSE STATUS: NEEDS VALIDATION`. A exceção do BRESSAY foi estendida ao EXP-007 em 2026-10-12 e ao EXP-008 e seguintes (por delegação do usuário) em 2026-10-13. Conteúdo do BRESSAY nunca vai para o Git.
  - **Armazenamento local (usuário, 2026-10-02):** ambientes, pesos e datasets de experimentos podem ocupar no
    máximo **20 GB** em `document-intelligence/` (unidade C:). Antes de ultrapassar, **pergunte ao usuário**; o plano é
    passar a armazenar no HD (unidade D:, ~880 GB livres). Meça o uso antes de cada download grande. Uso em
    2026-10-07: 8,2 GB.
  - Normalização do WER (pontuação de borda removida; acentos e caixa preservados) foi **aprovada** e deve ser mantida.

---

## 4. Princípios Técnicos Imediatos

1. **Local-first**: Proibido o uso de APIs externas proprietárias ou pagas (nem por imagem, caractere ou token).
2. **Sem modelos prematuros**: Nenhuma biblioteca pesada de OCR/HTR (ex.: Tesseract, EasyOCR, TrOCR, PaddleOCR, Surya, Florence-2) deve ser adicionada a `pyproject.toml` sem experimento prévio documentado.
3. **LDF como Contrato**: A interface com o Leitorum ocorre estritamente através do Leitorum Document Format (consulte [`docs/ldf.md`](./docs/ldf.md)).
4. **Human-in-the-loop**: Antecipe correções humanas como RFC 6902 JSON Patch.
