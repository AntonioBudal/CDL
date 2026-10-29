# Modelo de Dados — Feature 091

Migração `0033_organizer_feedback` (`down_revision = 0032_media_completed_seen`). Cria as duas tabelas e não altera
nenhuma existente.

## `organizer_feedback` (fatia B)

Um registro `leitorum-feedback/1` por estudo salvo pela digitalização ou depois de organizar.

| Coluna | Tipo | Regra |
| :--- | :--- | :--- |
| `id` | Integer | PK |
| `user_id` | String(36) | FK `users.id`, `ON DELETE CASCADE` |
| `study_id` | Integer | FK `studies.id`, `ON DELETE CASCADE`; único (`uq_organizer_feedback_study`) |
| `schema` | String(32) | `leitorum-feedback/1` |
| `origin` | String(12) | CHECK `IN ('digitize', 'import')` |
| `reviewed` | Boolean | organização salva, não revertida; padrão `0` |
| `artifact_sha256` | String(64) | artefato que fez a sugestão; vazio sem organização |
| `payload` | Text | JSON do documento ([contrato](contracts/organizer-feedback.contract.md)) |
| `size_bytes` | Integer | tamanho do `payload` em UTF-8 (teto de 256 KB) |
| `created_at` | DateTime | `CURRENT_TIMESTAMP` |

**Índice:** `ix_organizer_feedback_user_reviewed (user_id, reviewed)`, para a fatia C contar os estudos revisados.

## `organizer_user_state` (criada na fatia B, usada na fatia C)

| Coluna | Tipo | Regra |
| :--- | :--- | :--- |
| `user_id` | String(36) | PK; FK `users.id`, `ON DELETE CASCADE` |
| `artifact_sha256` | String(64) | artefato sobre o qual o estado foi montado |
| `reviewed_count` | Integer | registros revisados já incorporados |
| `state` | Text | JSON com pesos, centróides e contadores |
| `updated_at` | DateTime | `CURRENT_TIMESTAMP` |

## Exclusão

- **Estudo, lixeira ou livro:** quando o estudo sai de vez (um a um, ao esvaziar a lixeira ou com o livro), o
  registro sai pela cascata (`PRAGMA foreign_keys=ON`).
- **Conta:** `delete_account_permanently` apaga as duas tabelas de forma explícita, além da cascata.
- **Exportação:** o ZIP de portabilidade não inclui nenhuma das duas tabelas.

## Formato do estado (`organizer_user_state.state`, fatia C)

JSON `leitorum-learning-state/1`, o mesmo do EXP-024, mais dois campos:
- `guard`: as listas `adapter` e `static` com até 20 medidas de acerto;
- `reviewed`: quantos registros revisados já entraram.

O resto do estado:
- `delta_W` (4 × 54) e `delta_b`;
- os centróides do leitor e de cada livro (hash → peso, podados);
- as formas de linha (`ref_shapes`);
- os contadores de comportamento.

**Sem texto.** Os números são gravados com 5 casas. Teto de 1 MB: acima disso, saem primeiro os livros de menor
peso. A reconstrução (`backend/scripts/rebuild_organizer_state.py`) aplica os registros em ordem e grava e relê a
cada um, como a atualização incremental.
