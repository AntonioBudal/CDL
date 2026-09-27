# Data Model: F0.6.1 — Importação Inteligente

**Feature**: `040-importacao-inteligente`  
**Date**: 2026-09-27  

---

## 1. Entidades Persistidas

### `Study` (Tabela `studies`)
Representa o estudo/fichamento vinculado a um capítulo de livro no acervo. Nenhuma alteração destrutiva ou migration de quebra de schema é necessária nesta feature, preservando a retrocompatibilidade com a base existente.

| Campo | Tipo SQLite / ORM | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK, AutoIncrement | Identificador primário do estudo |
| `chapter_id` | INTEGER | FK (`chapters.id`), NOT NULL | Vínculo com o capítulo do livro |
| `title` | VARCHAR(255) | NULLABLE | Título do estudo (se vazio, assume nome do capítulo) |
| `location` | VARCHAR(100) | NULLABLE | Página ou localização de leitura |
| `source_response` | TEXT | NULLABLE | **Texto bruto colado na importação (preservação integral)** |
| `summary` | TEXT | NOT NULL, DEFAULT '' | Conteúdo da seção Resumo |
| `explanation` | TEXT | NOT NULL, DEFAULT '' | Conteúdo da seção Explicação |
| `concepts` | TEXT | NOT NULL, DEFAULT '' | Conteúdo da seção Conceitos |
| `references` | TEXT | NOT NULL, DEFAULT '' | Conteúdo da seção Referências |
| `notes` | TEXT | NULLABLE | Anotações adicionais e reflexões do leitor |
| `user_id` | INTEGER | FK (`users.id`), NOT NULL | Titular/autor do estudo |
| `created_at` | DATETIME | NOT NULL, DEFAULT UTC | Carimbo de data/hora de criação |
| `updated_at` | DATETIME | NOT NULL, DEFAULT UTC | Carimbo de data/hora da última alteração |

---

## 2. Estruturas em Memória e DTOs de Análise (Stateless)

### `ImportWarning` (Value Object / Pydantic Schema)
Emite alertas informativos gerados durante a análise sintática do texto bruto.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `code` | `str` | Código legível do aviso (`unassigned_text`, `repeated_section`, `missing_section`, `empty_section`, `unclosed_code_block`, `no_sections_found`) |
| `message` | `str` | Descrição amigável em português para o leitor |
| `section` | `str | None` | Chave da seção canônica afetada (`summary`, `explanation`, `concepts`, `references` ou `None`) |
| `line` | `int | None` | Número da linha no texto bruto onde a ocorrência foi detectada |

### `ImportPreviewRead` (DTO da API `/api/imports/preview`)
Retornado para a interface no momento da geração da prévia.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `source_response` | `str` | O texto de entrada íntegro que originou a prévia |
| `summary` | `str` | Texto extraído e associado ao Resumo |
| `explanation` | `str` | Texto extraído e associado à Explicação |
| `concepts` | `str` | Texto extraído e associado aos Conceitos |
| `references` | `str` | Texto extraído e associado às Referências |
| `unassigned_text` | `str` | Trechos não associados (preâmbulos, saudações, cabeçalhos atípicos) |
| `warnings` | `list[ImportWarning]` | Lista de advertências e orientações de conferência |

---

## 3. Regras de Validação e Integridade

1. **Preservação de Conteúdo**:
   - `source_response` nunca é truncado, sanitizado de tags nem reformatado pelo parser.
   - Qualquer texto em `unassigned_text` não descartado explicitamente pelo usuário é preservado via anexo à seção `explanation` ao salvar.
2. **Proteção contra Sobrescrita no Frontend**:
   - Se o usuário editar a caixa do texto de entrada original após gerar uma prévia, a interface sinaliza `stale = true` e solicita reanálise via botão "Atualizar prévia" para manter consistência antes de salvar.
3. **Seção Obrigatória**:
   - Ao menos uma das 4 seções (`summary`, `explanation`, `concepts`, `references`) deve conter texto não vazio para que o botão "Salvar Estudo" seja habilitado.
