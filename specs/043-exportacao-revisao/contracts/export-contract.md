# API Contract: Exportação Estendida e Caderno de Revisão (Digest)

**Feature Branch**: `043-exportacao-revisao`  
**Date**: 2026-09-27  

Este contrato define a interface HTTP e os payloads de consulta para os endpoints de exportação de livros e estudos, cobrindo o modo integral com destaques e a nova modalidade **Caderno de Revisão (Digest)**.

---

## 1. Exportar Livro (Completo ou Caderno de Revisão)

Compila e faz download do arquivo consolidado de um livro, suportando tanto o texto integral com destaques quanto o Caderno de Revisão agrupado por capítulo e estudo.

### Endpoint
`GET /api/books/{book_id}/export`

### Parâmetros de Consulta (Query Params)

| Parâmetro | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `format` | `string` | `"markdown"` | Formato do documento: `"markdown"` ou `"text"`. |
| `export_type` | `string` | `"full"` | Modalidade: `"full"` (documento integral) ou `"digest"` (Caderno de Revisão). |
| `include_highlights` | `boolean` | `true` | Se `export_type=full`, indica se deve injetar destaques no texto. |
| `exercise_mode` | `boolean` | `false` | Se `export_type=digest`, ativa o Modo Exercício (respostas com `_______` e gabarito ao final). |
| `include_notes` | `boolean` | `true` | Se `export_type=full`, inclui anotações pessoais do leitor. |
| `include_sections` | `boolean` | `true` | Se `export_type=full`, inclui as 4 seções analíticas. |
| `include_source` | `boolean` | `false` | Se `export_type=full`, inclui a resposta original da importação. |
| `include_metadata` | `boolean` | `true` | Inclui bloco de metadados no início do documento. |

### Respostas

#### Sucesso: HTTP 200 OK — Documento Completo com Destaques (Markdown)
- **Headers**:
  - `Content-Type: text/markdown; charset=utf-8`
  - `Content-Disposition: attachment; filename="memorias-postumas-de-bras-cubas.md"`
- **Corpo (amostra)**:
  ```markdown
  ---
  title: "Memórias Póstumas de Brás Cubas"
  author: "Machado de Assis"
  date_exported: "2026-09-27T10:00:00Z"
  app: "Leitorum"
  ---

  # Memórias Póstumas de Brás Cubas

  ## Capítulo 1: O Óbito do Autor

  ### Estudo 1: A Dedicatória ao Verme

  #### Resumo
  Algum tempo hesitei se devia abrir estas memórias pelo princípio ou pelo fim, isto é, se poria em primeiro lugar o meu nascimento ou a minha ==morte==[^1].

  [^1]: **[Anotação]** Notável inversão temporal machadiana.
  ```

#### Sucesso: HTTP 200 OK — Caderno de Revisão no Modo Exercício (Markdown)
- **Headers**:
  - `Content-Type: text/markdown; charset=utf-8`
  - `Content-Disposition: attachment; filename="caderno-revisao-exercicio-memorias-postumas.md"`
- **Corpo (amostra)**:
  ```markdown
  # Caderno de Revisão — Memórias Póstumas de Brás Cubas

  > Modo: Exercício (Respostas no Gabarito Final)
  > Exportado em: 2026-09-27 10:00:00 UTC | Total de Perguntas: 4 | Oclusões: 2

  ## Sumário
  - [Capítulo 1: O Óbito do Autor](#capitulo-1-o-obito-do-autor)

  ---

  ## 1. Perguntas de Retenção (Active Recall)

  1. **[Capítulo 1 / Estudo 1]** Por que o autor decide começar suas memórias pelo óbito?
     *Resposta:* __________________________________________________

  ---

  ## 2. Termos Ocluídos (Cloze Deletion)

  1. **[Capítulo 1 / Estudo 1]** Ao verme que primeiro roeu as frias carnes do meu cadáver dedico como saudosa lembrança estas [ _______ ].

  ---

  ## 3. Gabarito de Revisão

  ### Perguntas de Retenção
  1. **[Capítulo 1 / Estudo 1]**
     - **Resposta:** Para estabelecer a perspectiva única de um defunto autor, liberto das convenções sociais dos vivos.

  ### Termos Ocluídos
  1. **[Capítulo 1 / Estudo 1]**
     - **Termo:** memórias póstumas
  ```

#### Erros Comuns
- `HTTP 401 Unauthorized`: Sessão expirada ou ausente (quando autenticação exigida).
- `HTTP 404 Not Found`: Livro inexistente, na lixeira ou sem permissão de leitura.
  ```json
  { "detail": "Livro não encontrado." }
  ```

---

## 2. Exportar Estudo Individual (Completo ou Caderno de Revisão)

Compila e faz download do arquivo correspondente a um único estudo individual.

### Endpoint
`GET /api/studies/{study_id}/export`

### Parâmetros de Consulta (Query Params)
Mesmos parâmetros descritos acima (`format`, `export_type`, `include_highlights`, `exercise_mode`, `include_notes`, `include_sections`, `include_source`, `include_metadata`).

### Respostas
- **Headers**:
  - `Content-Type: text/markdown; charset=utf-8` (ou `text/plain; charset=utf-8`)
  - `Content-Disposition: attachment; filename="memorias-postumas-cap-01-estudo-01.md"` (ou `caderno-revisao-estudo-01.md`)
- **Corpo**: Conteúdo textual UTF-8 contendo a formatação solicitada para o estudo.

---

## 3. Contrato de Comunicação Frontend (TypeScript / Fetch)

### Método Auxiliar: `buildExportQuery(config: ExportConfig): string`
Gera a string de query parameters com codificação URL:
```typescript
params.set('format', config.format)
params.set('export_type', config.exportType)
params.set('include_highlights', String(config.includeHighlights))
params.set('exercise_mode', String(config.exerciseMode))
params.set('include_notes', String(config.includeNotes))
params.set('include_sections', String(config.includeSections))
params.set('include_source', String(config.includeSource))
params.set('include_metadata', String(config.includeMetadata))
```
