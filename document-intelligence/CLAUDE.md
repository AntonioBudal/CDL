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
- **Tarefa Atual**: **`EXP-001`** em fase de especificação, aguardando revisão do usuário.
  - Artefatos: [`spec.md`](./experiments/EXP-001/spec.md), [`plan.md`](./experiments/EXP-001/plan.md), [`tasks.md`](./experiments/EXP-001/tasks.md).
  - **Regra de workflow (usuário, 2026-09-30):** todo experimento segue o ciclo Spec Kit adaptado — Specify → Plan → Tasks — e a especificação/plano é apresentada **antes** de qualquer código de avaliação, script de inferência ou download de pesos.
  - **Ritmo fatiado (usuário, 2026-09-30):** nos próximos experimentos e features, produza **um artefato por vez** e aguarde a revisão antes do seguinte (Specify → aprovação → Plan → aprovação → Tasks → aprovação). Na execução, pare em cada checkpoint de fase e reporte.
  - EXP-001: spec, plano e tarefas aprovados; Fases 0 e 1 concluídas; Fase 2 autorizada. **Não** inicie a Fase 3 (download de pesos/dataset) sem autorização.
  - Normalização do WER (pontuação de borda removida; acentos e caixa preservados) foi **aprovada** e deve ser mantida.

---

## 4. Princípios Técnicos Imediatos

1. **Local-first**: Proibido o uso de APIs externas proprietárias ou pagas (nem por imagem, caractere ou token).
2. **Sem modelos prematuros**: Nenhuma biblioteca pesada de OCR/HTR (ex.: Tesseract, EasyOCR, TrOCR, PaddleOCR, Surya, Florence-2) deve ser adicionada a `pyproject.toml` sem experimento prévio documentado.
3. **LDF como Contrato**: A interface com o Leitorum ocorre estritamente através do Leitorum Document Format (consulte [`docs/ldf.md`](./docs/ldf.md)).
4. **Human-in-the-loop**: Antecipe correções humanas como RFC 6902 JSON Patch.
