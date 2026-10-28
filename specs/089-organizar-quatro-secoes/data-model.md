# Data Model: Organizar nas 4 Seções

**Feature**: `089-organizar-quatro-secoes` | **Plan**: [plan.md](plan.md)

**Nenhuma tabela, coluna ou migração (NR-001).** Tudo abaixo é transitório.

---

## 1. Backend (Pydantic, `app/schemas/organize.py`)

| Schema | Campos |
| :--- | :--- |
| `OrganizeLineInput` | `text: str`, `bbox: list[float] \| None` (4 itens), `confidence: float \| None` (0–1) |
| `OrganizeRequest` | `text: str` (≤ 50 000), `lines: list[OrganizeLineInput] \| None` (≤ 2 000) |
| `OrganizeSegmentRead` | `index`, `start`, `end`, `text` (= `text[start:end]`), `section` (`summary` \| `explanation` \| `concepts` \| `references`), `confidence`, `review` |
| `OrganizeRead` | `sections: {summary, explanation, concepts, references}`, `segments`, `explicit_headings`, `review_count`, `engine: {name, version, sha256}`, `elapsed_ms`, `warnings` |
| `OrganizeStatusRead` | `available`, `reason`, `version` |
| `DigitizeLineRead` (086) | **+ `bbox: list[int] \| None`** |

## 2. Estado do organizador no backend (`services/organizer/loader.py`)

| Item | Regra |
| :--- | :--- |
| artefato | `app/data/organizer/organizer-v1.json` mais o `.sha256` ao lado |
| carga | preguiçosa, uma vez por processo, sob `threading.Lock` |
| cache | modelo carregado ou motivo da falha; nunca guarda texto de pedidos |

## 3. Frontend: `useSectionOrganizer` (compartilhado)

| Campo | Tipo | Regra |
| :--- | :--- | :--- |
| `active` | boolean | modo organizado ligado |
| `loading` | boolean | pedido em andamento |
| `snapshot` | string | texto único exato antes de organizar |
| `segments` | `{index, text, section, review}[]` | `text` vem da resposta (nunca recortado por posição no cliente) |
| `assignment` | seção por trecho | começa igual à resposta; muda com "Mover para…" |
| `sections` | `AnalysisSections` | os 4 editores (editáveis) |
| `built` | `AnalysisSections` | o que o organizador montou por último para cada seção |
| `edited` | computado | algum `sections[s] !== built[s]` |
| `reviewItems` | computado | trechos com `review`, cada um com `movable` (texto ainda no editor de origem) |
| `error` | `{code, message} \| null` | mensagens em português |

**Montagem de uma seção:** a junção por `\n` dos textos dos trechos com aquela seção em `assignment`, na ordem
dos índices. É a mesma regra do backend, então a primeira montagem reproduz `sections` da resposta.

## 4. Digitalização (`useDigitizeDraft`, extensão)

- `preview.lines[].bbox` guardado como veio da API.
- `organizer`: instância de `useSectionOrganizer`.
- **`save()`:**
  - no modo organizado: `summary`, `explanation`, `concepts` e `references` vêm de `organizer.sections`;
  - no modo texto único: como hoje;
  - `source_response` é sempre `preview.text`.
- **`canSave`:** no modo organizado, exige ao menos uma das 4 seções com texto.
- **`dirty`:** inclui o modo organizado com texto.

## 5. Importação (`useImportDraft`, extensão)

| Campo | Regra |
| :--- | :--- |
| `organizeSnapshot` | `{sections, unassigned_text} \| null`, criado por `organizeUnassigned()` |
| `organizeUnassigned()` | acrescenta cada seção sugerida ao fim da seção atual (com `\n\n` se não vazia) e esvazia `unassigned_text` |
| `undoOrganize()` | restaura o snapshot exato e o descarta |
| nova prévia | descarta o snapshot |
