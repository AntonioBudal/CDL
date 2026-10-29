# Contrato: Registro Silencioso do Feedback do Organizador

**Feature**: `091-organizer-v2-feedback`, fatia B | Router: `backend/app/routers/organizer_feedback.py` | Prefixo:
`/api/studies`

A rota:
- exige usuário autenticado (`CurrentUser`);
- só aceita estudo do próprio usuário, fora da lixeira;
- nunca registra texto em log.

---

## `POST /api/studies/{study_id}/organizer-feedback`

Chamada pelo navegador **depois** de `POST /api/studies` bem-sucedido, sem esperar resposta. Corpo:

```json
{
  "origin": "digitize",
  "organizer": {
    "engine": { "version": "2", "sha256": "9f6530a3…", "adapter": null },
    "outcome": "saved",
    "text": "texto que foi enviado ao organizador",
    "segments": [{ "index": 0, "start": 0, "end": 37, "section": "summary", "confidence": 0.81, "review": false }]
  }
}
```

**Regras do corpo:**
- `origin` ∈ `digitize`, `import`.
- `organizer` pode ser `null` (digitalização sem organizar).
- `outcome` ∈ `saved`, `reverted`.
- `text` com até 50 000 caracteres.
- Até 400 `segments`, com `0 ≤ start < end ≤ len(text)`.
- `lines` (fatia C, opcional): até 400 linhas `{text, bbox, confidence}`, as mesmas enviadas ao organizador. A
  digitalização envia; a importação não. Sem elas, o adaptador não realinha uma página analisada com layout.
- Campos extras são recusados.

| Resposta | Quando |
| :--- | :--- |
| **204** | todo pedido válido, gravando ou não, e também numa falha interna |
| **404** | estudo inexistente, de outro usuário ou na lixeira |
| **422** | corpo inválido |

**Códigos no log** (`organizer-feedback: <código> (<origem>, <trechos>, <correções>, <bytes>)`):

| Código | Significado |
| :--- | :--- |
| `recorded` | gravado |
| `exists` | o estudo já tem registro; o primeiro fica |
| `stale` | estudo criado há mais de 10 minutos |
| `no_source` | `digitize` sem `source_response` |
| `no_organizer` | `import` sem organização |
| `too_large` | passou de 256 KB mesmo sem a parte de leitura |
| `error` | falha interna; nada gravado e o estudo intacto |

## Documento `leitorum-feedback/1` (coluna `organizer_feedback.payload`)

Montado pelo servidor a partir do **estudo salvo**. As seções e o texto lido vêm do banco, nunca do cliente.

```json
{
  "schema": "leitorum-feedback/1",
  "created_at": "2026-10-28T20:30:00Z",
  "origin": "digitize",
  "organizer": {
    "engine": { "version": "2", "sha256": "9f6530a3…", "adapter": null },
    "outcome": "saved",
    "text": "…",
    "segments": [{ "index": 0, "start": 0, "end": 37, "section": "summary", "confidence": 0.81, "review": false }],
    "lines": [{ "text": "…", "bbox": [0, 0, 900, 60], "confidence": 0.9 }],
    "saved_sections": { "summary": "…", "explanation": "…", "concepts": "…", "references": "…" },
    "units": [{ "index": 0, "outcome": "kept", "final": "summary", "ratio": 1.0 }],
    "patch": [{ "op": "replace", "path": "/segments/1/section", "value": "concepts" }]
  },
  "reading": {
    "lines": 4,
    "kinds": { "same": 2, "ocr": 2, "rewrite": 0, "ambiguous": 0 },
    "human_corrections": [{
      "id": "corr-line-0", "author": "leitor", "timestamp": "2026-10-28T20:30:00Z", "reason": "ocr-fix",
      "target": { "collection": "recognition.lines", "id": "line-0" },
      "ops": [{ "op": "replace", "path": "/text", "value": "linha revisada" }]
    }]
  }
}
```

**Parte `organizer`:**
- Só existe se houve organização.
- Com `outcome: "reverted"`, não tem `saved_sections`, `units` nem `patch`.
- `units[].outcome` ∈ `kept`, `moved`, `edited`, `deleted`.
- `patch` é RFC 6902 sobre o resultado do organizador e lista só os movimentos.

**Parte `reading`:**
- Só existe na digitalização com até 80 linhas lidas.
- `line-{k}` é a posição da linha em `source_response`.
- Só as correções de leitura (`ocr`) viram `human_corrections`. Reescritas e ambíguas entram só nas contagens, sem
  texto.

**Coluna `reviewed`:** `true` só com `organizer.outcome = "saved"`.

**Teto:** acima de 256 KB, o documento sai sem `reading`. Se ainda passar, não é gravado (`too_large`).

**Leitura:** nada aqui altera o texto lido. A pós-correção automática continua desligada (FR-016).

## Adaptador (fatia C)

Depois de um `recorded`, a mesma requisição atualiza o estado do adaptador do usuário (`organizer_user_state`).
A atualização acontece **sempre**, mesmo com o adaptador desligado. O log ganha
`adaptador: <código>, <ms> ms`. Códigos:

| Código | Significado |
| :--- | :--- |
| `learned` | aprendeu |
| `gated` | não aprendeu: revertido, ou pouca retenção sem correções |
| `misaligned` | a análise de hoje não bate com os trechos sugeridos |
| `no_organizer` | o registro não teve organização |
| `skipped_artifact` | o estado é de outro artefato; só a reconstrução o remonta |
| `unavailable` | o organizador está indisponível |
| `error` | falha; o registro continua gravado |

Os códigos que aprendem podem ganhar o sufixo `+pruned_books`.
