# EXP-024 — Estado do experimento

Melhoria contínua autônoma do Organizador das 4 seções e da pós-correção da digitalização.

Este arquivo é o diário de bordo: é atualizado ao fim de cada fase, antes do commit da fase.

## Fases

| Fase | Conteúdo | Estado | Commit |
| :--- | :--- | :--- | :--- |
| F00 | Diagnóstico e linha de base (só leitura) | **concluída em 2026-10-28** | `F00` (este) |
| F01 | Pesquisa e especificação: `spec.md`, `plan.md`, `tasks.md` | pendente; **para para revisão do usuário** | — |
| F02 | Fluxos longitudinais sintéticos e simulador de feedback | pendente | — |
| F03 | Motor adaptativo em Python puro e travas anti-regressão | pendente | — |
| F04 | Calibração, curvas de aprendizado, ablações, estresse e D-usuário | pendente | — |
| F05 | `RESULTS.md`, ADR-011 (se houver adoção) e fechamento; **para para revisão do usuário** | pendente | — |

## F00 — Linha de base (2026-10-28)

### Verificações

| Comando (a partir de `document-intelligence/`) | Resultado |
| :--- | :--- |
| `uv run pytest` | 239 aprovados |
| `uv run ruff check .` | sem avisos |
| `uv run --frozen --project experiments/EXP-023/envs/organizer python -m pytest experiments/EXP-023/tests` | 14 aprovados |

- **Commit de partida:** `aaca5f8`, com a árvore de `document-intelligence/` limpa.
- **Disco:** 13,97 GB em `document-intelligence/`, abaixo do teto de 20 GB; 106 GB livres no C:.
- **RAM livre na medição:** 0,89 GB. Basta para os testes. Qualquer etapa que carregue o motor de leitura espera
  ≥ 1,5 GB livres, pela regra das rodadas longas.

### Artefatos herdados (conferidos)

| Artefato | SHA-256 |
| :--- | :--- |
| `experiments/EXP-023/artifacts/organizer-v1.json` | `60d6538de49495e4bfc01e00f048d5f4c0d1e55a7a84d6df33de9fee99c40d28` (igual ao `organizer-v1.sha256`) |
| `dataset/processed/exp-023/noise-model.json` (fora do Git, só contagens) | existe; CER 29,0 % sobre 495 864 caracteres do EXP-015 |

### Fatos de partida (EXP-023, ADR-010)

- Organizador `V4`, só semente: Macro-F1 0,934 no limpo e 0,825 com CER 25 %, nas páginas fictícias.
- **D-usuário:** só **3 estudos de 2 usuários**. Macro-F1 0,497; `references` 0,29.
- **`V6` com centróides do usuário:** 0,644 (κ = 25). A hipótese H4 ficou **inconclusiva** pelo N.
- **Montagem a frio dos centróides:** 1,2 s por 100 estudos, ~6 s estimados para 500 (meta: 2 s).
- **Parâmetros:** a validação zerou τ, ω e α. Ficaram λ = 8, σ_g = 0,75, η = 2 e β = 1,25.

### Divergências encontradas no diagnóstico (a tratar na F01)

1. **O LDF 2.0 não tem as 4 seções do Estudo.**
   - `semantics.sections.role` aceita só `title`, `summary`, `concept`, `question`, `quote`, `example`,
     `margin_note` e `other`. Não há `explanation` nem `references`.
   - Cada seção aponta para regiões (`region_ids`), não para trechos de texto.
   - O schema 2.0 está congelado (ADR-004).

   Conclusão: `human_corrections` serve direto para as correções de leitura (`recognition.lines`, `replace
   /text`). Os movimentos de seção do organizador não cabem nele sem perda. A decisão fica na spec (Categoria 2).
2. **O banco ativo mudou de lugar.**
   - Desde a feature 090-A do Leitorum (2026-10-28), o banco ativo é `D:\Leitorum\db\caderno.db`.
   - `caderno-leitura-0.1/backend/data/caderno.db` ficou como origem congelada da migração, guardada para
     rollback.
   - O `dusuario.py` do EXP-023 aponta para o caminho antigo.

   Qual cópia o D-usuário da F04 deve ler é decisão do usuário, na revisão da F01.
3. **O ruído do EXP-015 é global, não por escritor.** O `noise-model.json` tem taxas por caractere, sem
   identidade de escritor. Os "confundidores recorrentes por escritor" do simulador terão de ser sintéticos,
   declarados como tal.

## Próximo passo

F01: escrever `spec.md`, `plan.md` e `tasks.md` e parar para a revisão do usuário.
