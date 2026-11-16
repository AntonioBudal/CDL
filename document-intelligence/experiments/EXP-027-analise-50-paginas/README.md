# EXP-027 — como rodar

Spec, hipóteses e tarefas em [spec.md](./spec.md). Resultado em `report.md` (quando concluído).
Tudo que toca dados reais fica fora do Git (`dataset/raw/exp-027`, `dataset/processed/exp-027`).

## Ambientes

- **Motor do produto** (`caderno-leitura-0.1/motor/.venv`): OpenCV, PIL, `rapidocr`, ONNX Runtime.
  Usado por `inventory.py`, `run_motor.py`, `prepare_tool.py`, `examples.py`, `synthetic_pages.py`.
- **Python puro** (qualquer Python ≥ 3.11): `transcribe_server.py`, `split.py`, `score.py`,
  `vlm_reference.py` (este último usa PIL).
- Variáveis: `EXP027_DATA_ROOT` (raiz `dataset/` com os dados; padrão: a do próprio checkout) e
  `EXP027_MOTOR_DIR` (pasta `motor/` com `.venv`; padrão: a do próprio checkout).

## Passos

```powershell
# a partir de document-intelligence/experiments/EXP-027-analise-50-paginas/harness
$motor = "..\..\..\..\caderno-leitura-0.1\motor\.venv\Scripts\python.exe"
& $motor -s inventory.py --expect 50        # T001a: pNN, SHA-256, manifesto
& $motor -s run_motor.py                     # T001b: leitura de cada foto pelo motor (retomável)
& $motor -s prepare_tool.py                  # T003a: imagens, recortes e medidas da foto
python -s transcribe_server.py               # T003b: http://127.0.0.1:8765/ para transcrever
python -s split.py --size 20                 # T002: congela o teste (uma vez; exige classificação)
python -s score.py --system motor --benchmark  # T004: métricas e quebra por origem
& $motor -s examples.py --per-kind 2         # T004b: exemplos de falha (fora do Git)
python -s vlm_reference.py --system qwen3-vl-4b  # T005: com um llama-server local no ar
python -s score.py --system qwen3-vl-4b --benchmark
```

Teste da cadeia sem dados reais: `synthetic_pages.py <pasta> --pages 2` gera páginas fictícias;
`uv run pytest experiments/EXP-027-analise-50-paginas/tests` cobre o alinhamento e a quebra do erro.

## Regras

- As páginas do `splits/test-manifest.json` nunca entram em treino, prompt, limiar ou dicionário.
- Nenhum texto, recorte ou foto do usuário vai para o Git, para o `report.md` ou para o chat.
