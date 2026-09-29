# API Contracts: F0.6.5 — Histórico Automático de Versões

Este documento especifica os contratos de rota REST para consulta, inspeção, diff e restauração de versões de estudo.

---

## 1. Listar Versões de um Estudo

Retorna a linha do tempo cronológica decrescente de todas as versões arquivadas do estudo.

- **Método**: `GET`
- **Rota**: `/api/studies/{study_id}/versions`
- **Autenticação**: Obrigatória (`CurrentUser`)
- **Permissão**: Leitura permitida para quem tem acesso ao estudo (`can_read_study`).

### Resposta de Sucesso (`200 OK`)

```json
[
  {
    "id": 14,
    "study_id": 42,
    "version_number": 3,
    "user_id": "usr-123",
    "author_name": "Antônio Budal",
    "change_summary": "Edição",
    "char_count": 4820,
    "highlights_count": 5,
    "is_current": true,
    "created_at": "2026-09-28T22:15:00Z",
    "updated_at": "2026-09-28T22:18:30Z"
  },
  {
    "id": 12,
    "study_id": 42,
    "version_number": 2,
    "user_id": "usr-123",
    "author_name": "Antônio Budal",
    "change_summary": "Edição",
    "char_count": 4150,
    "highlights_count": 3,
    "is_current": false,
    "created_at": "2026-09-27T18:00:00Z",
    "updated_at": "2026-09-27T18:00:00Z"
  },
  {
    "id": 10,
    "study_id": 42,
    "version_number": 1,
    "user_id": "usr-123",
    "author_name": "Antônio Budal",
    "change_summary": "Versão inicial",
    "char_count": 3800,
    "highlights_count": 0,
    "is_current": false,
    "created_at": "2026-09-20T10:00:00Z",
    "updated_at": "2026-09-20T10:00:00Z"
  }
]
```

---

## 2. Inspecionar Conteúdo Integral de uma Versão

Recupera os dados completos de uma versão passada específica em modo somente leitura.

- **Método**: `GET`
- **Rota**: `/api/studies/{study_id}/versions/{version_id}`
- **Autenticação**: Obrigatória (`CurrentUser`)
- **Permissão**: Leitura permitida para quem tem acesso ao estudo.

### Resposta de Sucesso (`200 OK`)

```json
{
  "id": 12,
  "study_id": 42,
  "version_number": 2,
  "user_id": "usr-123",
  "author_name": "Antônio Budal",
  "title": "A Dialética do Esclarecimento — Análise Crítica",
  "summary": "Texto integral da seção resumo...",
  "explanation": "Texto integral da seção argumentos...",
  "concepts": "Texto integral da seção conceitos...",
  "references": "Texto integral da seção referências...",
  "notes": "Anotações marginais...",
  "highlights": [
    {
      "section": "summary",
      "start_offset": 45,
      "end_offset": 82,
      "selected_text": "conceito central",
      "prefix": "o ",
      "suffix": " de razão",
      "color": "yellow",
      "kind": "highlight",
      "note": ""
    }
  ],
  "change_summary": "Edição",
  "created_at": "2026-09-27T18:00:00Z",
  "updated_at": "2026-09-27T18:00:00Z"
}
```

---

## 3. Calcular Diferenças Visuais (Diff)

Compara a versão especificada contra a versão atual (ou contra outra versão indicada via query parameter).

- **Método**: `GET`
- **Rota**: `/api/studies/{study_id}/versions/{version_id}/diff?target_version_id={optional_id}`
- **Autenticação**: Obrigatória (`CurrentUser`)
- **Permissão**: Leitura permitida para quem tem acesso ao estudo.

### Resposta de Sucesso (`200 OK`)

```json
{
  "version_number": 2,
  "target_version_number": 3,
  "is_target_current": true,
  "sections": {
    "title": {
      "status": "modified",
      "chunks": [
        { "type": "equal", "text": "A Dialética do Esclarecimento — " },
        { "type": "delete", "text": "Análise" },
        { "type": "insert", "text": "Revisão Crítica" }
      ]
    },
    "summary": {
      "status": "modified",
      "chunks": [
        { "type": "equal", "text": "O esclarecimento visava libertar o homem do medo. " },
        { "type": "insert", "text": "No entanto, transformou-se em nova mitologia." }
      ]
    },
    "explanation": {
      "status": "unchanged",
      "chunks": [
        { "type": "equal", "text": "Texto dos argumentos inalterado..." }
      ]
    },
    "concepts": {
      "status": "unchanged",
      "chunks": []
    },
    "references": {
      "status": "unchanged",
      "chunks": []
    },
    "notes": {
      "status": "unchanged",
      "chunks": []
    }
  }
}
```

---

## 4. Restaurar Versão Anterior

Restaura o conteúdo e os destaques da versão anterior para o estado ativo do estudo, criando atomicamente uma nova versão no histórico que registra a restauração.

- **Método**: `POST`
- **Rota**: `/api/studies/{study_id}/versions/{version_id}/restore`
- **Autenticação**: Obrigatória (`CurrentUser`)
- **Permissão**: Requer permissão de edição (`check_study_mutation_permission`).

### Resposta de Sucesso (`200 OK`)

Retorna a entidade `StudyRead` atualizada do estudo:

```json
{
  "id": 42,
  "title": "A Dialética do Esclarecimento — Análise Crítica",
  "chapter_id": 10,
  "reading_status": "em_andamento",
  "visibility": "inherit",
  "location": "Capítulo 1",
  "summary": "Texto restaurado...",
  "explanation": "Texto restaurado...",
  "concepts": "Texto restaurado...",
  "references": "Texto restaurado...",
  "notes": "Notas restauradas...",
  "version": 4,
  "created_at": "2026-09-20T10:00:00Z",
  "updated_at": "2026-09-28T22:20:00Z",
  "can_edit": true
}
```

### Respostas de Erro

- `401 Unauthorized`: Usuário não autenticado.
- `403 Forbidden`: Usuário sem permissão de escrita no estudo.
- `404 Not Found`: Estudo ou versão inexistente, ou estudo na lixeira.
