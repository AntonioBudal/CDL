# Catálogo de procedência (F-DI-13.03)

Registro local de **de onde veio** cada linha de manuscrito usada pelo Document Intelligence, **sob que
licença**, **em que situação de uso** e **em que ciclos de treino entrou**. Spec:
[`specs/004-catalogo-de-procedencia`](../../specs/004-catalogo-de-procedencia/spec.md). Regras:
[estratégia de dados v2](../../docs/replanejamento-0.13/09-estrategia-de-aquisicao-de-dados.md).

* Dados em `D:\Leitorum-DI\` (ou `LEITORUM_DI_DATA`): `catalogo\catalogo.sqlite` e `objetos\` (arquivos com o
  nome do próprio SHA-256). Nada disso vai para o Git.
* Linha padrão: PNG em cinza, 64 px de altura.
* Situações: `APPROVED`, `EXPERIMENT_ONLY`, `PENDING_REVIEW` (só metadados), `REJECTED` (apagado e bloqueado),
  `BLOCKED`.

## Comandos (a partir de `document-intelligence/`)

| Comando | Faz |
| :--- | :--- |
| `uv run python -m tools.catalogo fontes` | lista as fontes, licença, condições e situação |
| `uv run python -m tools.catalogo uso` | espaço por tipo contra o teto (100 GB no total) |
| `uv run python -m tools.catalogo pendentes` | `PENDING_REVIEW` agrupado por fonte e motivo (revisão mensal) |
| `uv run python -m tools.catalogo revisar --fonte F --para APPROVED --motivo "..." [--evidencia URL]` | muda a situação de uma fonte inteira |
| `uv run python -m tools.catalogo revisar --item F:ID --para REJECTED --motivo "..."` | rejeita um item: apaga, bloqueia e marca os ciclos que o usaram como contaminados |
| `uv run python -m tools.catalogo ciclo --finalidade experimento --fontes a,b --receita R --commit C --semente 0` | registra um ciclo de treino com a lista exata de itens |
| `uv run python -m tools.catalogo promover-conferir RUN` | só passa se todos os itens do ciclo forem `APPROVED` e o ciclo não estiver contaminado |
| `uv run python -m tools.catalogo resumo-treino RUN` | resumo do conteúdo de treino (fontes, licenças, atribuições), sem texto |
| `uv run python -m tools.catalogo verificar` | confere os hashes dos arquivos |
| `uv run python -m tools.catalogo importar-exp043` | importa as amostras aprovadas do EXP-043 |

Os conectores (E4) usam a API Python: `Catalog().ingest_line(fonte, id, image=..., text=..., url=..., ...)`,
com `flush()` ou `close()` no fim (as gravações são agrupadas em lotes de 500).
