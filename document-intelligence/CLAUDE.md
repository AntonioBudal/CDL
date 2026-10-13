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
- **Tarefa Atual**: [`EXP-007`](./experiments/EXP-007/spec.md) (validação em imagens reais com datasets públicos: GNHK e BRESSAY, decisão do usuário em 2026-10-12). GNHK já baixado em `dataset/raw/exp-007/gnhk/` (autorizado pelo usuário). `spec.md`, `plan.md` e `tasks.md` aprovados; **em execução**. Fases 1 e 2 concluídas (verdade de chão: 172 fotos do GNHK, 185 páginas do BRESSAY); código de avaliação pronto. **Fase 3 (detecção com modelos) bloqueada por RAM livre abaixo de 1 GiB** — não relaxar o limite; retomar com `experiments/EXP-007/harness/detect.py --set <conjunto>` para `bressay-x3`, `bressay-native` e `gnhk`, depois `run.py`. O EXP-004 (semântica) fica para depois.
  - **Congelados:** `docs/schemas/ldf-1.0.schema.json` e os diretórios `experiments/EXP-001` a `EXP-003` não podem ser alterados (`tests/ldf/test_frozen.py` confere). Saídas novas usam `leitorum_di.contracts.ldf.build_document`. Ao rodar algo nos ambientes dos EXP-001/002, use `uv run --frozen --project …` (sem `--frozen` o `uv` reescreve o `uv.lock` do ambiente).
  - **Regra de workflow (usuário, 2026-09-30):** todo experimento segue o ciclo Spec Kit adaptado — Specify → Plan → Tasks — e a especificação/plano é apresentada **antes** de qualquer código de avaliação, script de inferência ou download de pesos.
  - **Ritmo fatiado (usuário, 2026-09-30):** nos próximos experimentos e features, produza **um artefato por vez** e aguarde a revisão antes do seguinte (Specify → aprovação → Plan → aprovação → Tasks → aprovação). Na execução, desde 2026-10-07 **não é preciso parar a cada checkpoint**: siga pelas fases com o próprio julgamento e pare só no aceite final ou em bloqueio real (licença em aberto, disco acima do teto, RAM insuficiente, decisão do usuário).
  - Commits: padrão `FNN(document-inteligence) <nome da fase>`, definido pelo usuário em 2026-09-30.
  - Exceções de licença em vigor (só uso experimental local, nunca produto): pesos do TrOCR small e dataset BRESSAY, ambos `LICENSE STATUS: NEEDS VALIDATION`. A exceção do BRESSAY foi estendida ao EXP-007 em 2026-10-12. Conteúdo do BRESSAY nunca vai para o Git.
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
