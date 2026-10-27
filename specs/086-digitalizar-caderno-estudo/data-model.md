# Data Model: Digitalizar Caderno — Foto de Página Manuscrita para Estudo

**Feature**: `086-digitalizar-caderno-estudo` | **Date**: 2026-10-27 | **Plan**: [plan.md](plan.md)

**Nenhuma tabela, coluna ou migração nova (NR-001).** As entidades abaixo são transitórias. Só existem durante um
pedido ou na memória da tela, exceto o Estudo, que já existe.

---

## 1. Saída do motor (`leitorum-motor/1`)

Arquivo JSON gravado pelo motor na pasta temporária e lido pelo backend. Nunca persistido.

| Campo | Tipo | Regra |
| :--- | :--- | :--- |
| `schema` | `"leitorum-motor/1"` | obrigatório; outro valor → erro `engine_failed` |
| `image` | `{width, height}` | dimensões da imagem recebida |
| `lines[]` | lista | **já em ordem de leitura** |
| `lines[].text` | string | texto lido, sem correção |
| `lines[].confidence` | número 0–1 | média das probabilidades CTC dos caracteres mantidos |
| `lines[].bbox` | `[x0, y0, x1, y1]` inteiros | coordenadas na imagem recebida |
| `page_scale` | inteiro 1–4 | fator de ampliação usado |
| `engine` | `{name, version, detector, reader, reader_sha256, license_status}` | identificação para auditoria |
| `elapsed_ms` | número | tempo de leitura dentro do motor |

## 2. Pré-visualização da leitura (resposta da API)

`DigitizePreviewRead` (Pydantic, backend) e `DigitizePreview` (TypeScript, frontend).

| Campo | Tipo | Origem |
| :--- | :--- | :--- |
| `text` | string | `lines[].text` unidos por `\n` (vira `source_response` ao salvar) |
| `lines[]` | `{index, text, confidence, low_confidence}` | `low_confidence = confidence < config.low_confidence` |
| `low_confidence_count` | inteiro | contagem de linhas marcadas |
| `warnings[]` | `{code, message}` | ver tabela de avisos |
| `engine` | `{name, version, reader, license_status}` | da saída do motor, sem caminhos |
| `elapsed_ms` | inteiro | tempo total do pedido no backend |

**Avisos** (não são erros, a resposta é `200`):

| `code` | Quando |
| :--- | :--- |
| `no_text` | nenhuma linha detectada (US1, cenário 4) |
| `many_uncertain` | mais da metade das linhas marcadas como incertas |
| `draft` | sempre presente: o texto foi lido automaticamente e deve ser revisado |

As caixas (`bbox`) não chegam ao frontend nesta fatia. Exibir as caixas sobre a foto está fora de escopo.

## 3. Estado do motor

`DigitizeStatusRead`: `{available: bool, reason: null | "not_installed" | "integrity_failed"}`.
Fica em cache no processo do backend.

## 4. Rascunho da digitalização (frontend, `useDigitizeDraft`)

| Campo | Tipo | Regra |
| :--- | :--- | :--- |
| `phase` | `'checking' \| 'idle' \| 'unavailable' \| 'reading' \| 'review' \| 'saving' \| 'saved' \| 'error'` | máquina de estados abaixo (`checking` enquanto consulta o status) |
| `file` / `previewUrl` | `File` / `blob:` URL | só na memória; URL revogada em `reset` e ao desmontar |
| `preview` | `DigitizePreview \| null` | resposta da API |
| `text` | string | começa igual a `preview.text`; editável |
| `section` | `'summary' \| 'explanation' \| 'concepts' \| 'references'` | padrão `'summary'` |
| `bookId`, `chapterId`, `title` | strings | validados contra as listas carregadas |
| `error` | `{code, message} \| null` | mensagem em português |
| `dirty` | computado | `phase === 'review' && text.trim() !== ''` (alimenta `useUnsavedChanges`) |
| `canSave` | computado | capítulo válido, título não vazio, `text.trim()` não vazio, fora de `saving` |

**Transições**:

```text
idle ──escolher foto──▶ reading ──200──▶ review ──salvar──▶ saving ──201──▶ saved
  ▲                       │  └─erro──▶ error ─tentar outra─┘   │  └─erro──▶ review (erro exibido)
  │                       └─cancelar (abort)──▶ idle            │
  └──────────── "Digitalizar outra página" ◀────────────────────┘
status indisponível ──▶ unavailable (atalhos /importar e /inbox)
```

## 5. Estudo (existente, sem mudança)

Payload de `POST /api/studies` montado pela tela:

| Campo do `StudyCreate` | Valor |
| :--- | :--- |
| `chapter_id` | capítulo escolhido |
| `title` | título digitado (padrão: "Página digitalizada em DD/MM/AAAA") |
| `summary` / `explanation` / `concepts` / `references` | **só a seção escolhida** recebe `text` revisado; as outras vão vazias |
| `source_response` | `preview.text` (leitura automática, sem correções) |
| `location`, `notes` | `""` |
| `template_id` | padrão do backend (`classico`) |

`reading_status` não é enviado. O modelo já nasce com `'rascunho'`. O estudo pertence ao usuário autenticado,
como qualquer estudo (FR-010).
