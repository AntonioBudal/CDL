# Data Model: Fundação Multiusuário e CRUD Geral (F01)

**Feature**: `028-fundacao-multiusuario`  
**Date**: 2026-09-20  
**Status**: Completed  

---

## 1. Diagrama de Relacionamento de Entidades (ERD)

```
┌─────────────────────────────────────────────────────────────┐
│                            User                             │
├─────────────────────────────────────────────────────────────┤
│ id: String(36) [PK, UUID]                                   │
│ username: String(50) [Unique, Indexed]                      │
│ display_name: Text                                          │
│ status: String(20) [ativo | suspenso | inativo]             │
│ created_at: UTCDateTime                                     │
│ updated_at: UTCDateTime                                     │
└──────────────┬───────────────────────────────┬──────────────┘
               │ 1                             │ 1
               │                               │
               ▼ *                             ▼ *
┌──────────────────────────────┐ ┌──────────────────────────────┐
│             Book             │ │      Category (Híbrida)      │
├──────────────────────────────┤ ├──────────────────────────────┤
│ id: Integer [PK]             │ │ id: Text [PK]                │
│ user_id: String(36) [FK]     │ │ user_id: String(36) [FK, opt]│
│ title: Text                  │ │ name: Text                   │
│ author: Text [opt]           │ │ parent_id: Text [FK, opt]    │
│ subtitle: Text               │ │ path: Text                   │
│ year: Integer [opt]          │ │ created_at: UTCDateTime      │
│ cover_image: Text [opt]      │ └──────────────────────────────┘
│ created_at: UTCDateTime      │
│ updated_at: UTCDateTime      │
│ deleted_at: UTCDateTime [opt]│
└──────────────┬───────────────┘
               │ 1
               ▼ *
┌──────────────────────────────┐
│           Chapter            │
├──────────────────────────────┤
│ id: Integer [PK]             │
│ book_id: Integer [FK]        │
│ name: Text                   │
│ position: Integer            │
│ created_at: UTCDateTime      │
└──────────────┬───────────────┘
               │ 1
               ▼ *
┌──────────────────────────────┐
│            Study             │
├──────────────────────────────┤
│ id: Integer [PK]             │
│ user_id: String(36) [FK]     │
│ chapter_id: Integer [FK]     │
│ parent_study_id: Int [FK,opt]│
│ position: Integer            │
│ reading_status: String(20)   │
│ title: Text                  │
│ location: Text               │
│ source_response: Text        │
│ summary: Text                │
│ explanation: Text            │
│ concepts: Text               │
│ references: Text             │
│ notes: Text                  │
│ created_at: UTCDateTime      │
│ updated_at: UTCDateTime      │
│ deleted_at: UTCDateTime [opt]│
└──────────────────────────────┘
```

---

## 2. Especificação das Entidades e Atributos

### 2.1. Entidade `User` (Nova)

| Atributo | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | `String(36)` | Primary Key, UUID | Identificador único estável da identidade soberana. |
| `username` | `String(50)` | Not Null, Unique, Index | Nome de usuário único (`a-z`, `0-9`, `_`, `-`). |
| `display_name` | `Text` | Not Null | Nome legível para exibição ("Proprietário do Caderno"). |
| `status` | `String(20)` | Not Null, Default: `'ativo'` | Estado operacional da conta (`'ativo'`, `'suspenso'`). |
| `created_at` | `UTCDateTime` | Not Null, Default: UTC Now | Carimbo de criação no servidor. |
| `updated_at` | `UTCDateTime` | Not Null, OnUpdate: UTC Now | Carimbo de última modificação de perfil. |

### 2.2. Atualizações em Entidades Existentes

#### Tabela `books`
- **Nova Coluna**: `user_id` (`String(36)`, Not Null, FK `users.id`, ondelete='CASCADE').
- **Novo Índice**: `ix_books_user_id` (`user_id`).
- **Novo Índice Composto**: `ix_books_user_deleted` (`user_id`, `deleted_at`).

#### Tabela `studies`
- **Nova Coluna**: `user_id` (`String(36)`, Not Null, FK `users.id`, ondelete='CASCADE').
- **Novo Índice**: `ix_studies_user_id` (`user_id`).
- **Novo Índice Composto**: `ix_studies_user_deleted` (`user_id`, `deleted_at`).
- **Novo Índice Composto**: `ix_studies_user_chapter` (`user_id`, `chapter_id`).

#### Tabela `categories` (Modelo Híbrido)
- **Nova Coluna**: `user_id` (`String(36)`, Nullable, FK `users.id`, ondelete='CASCADE').
  - Se `user_id IS NULL`: Categoria global/padrão da plataforma (somente-leitura para usuários regulares).
  - Se `user_id IS NOT NULL`: Categoria exclusiva criada pelo usuário proprietário.
- **Novo Índice**: `ix_categories_user_id` (`user_id`).

#### Tabela `study_relations`
- **Nova Coluna**: `user_id` (`String(36)`, Not Null, FK `users.id`, ondelete='CASCADE').
- **Novo Índice**: `ix_study_relations_user_id` (`user_id`).

#### Tabela `study_canvas_nodes`
- **Nova Coluna**: `user_id` (`String(36)`, Not Null, FK `users.id`, ondelete='CASCADE').
- **Novo Índice**: `ix_study_canvas_nodes_user_id` (`user_id`).

#### Tabela `canvas_frames`
- **Nova Coluna**: `user_id` (`String(36)`, Not Null, FK `users.id`, ondelete='CASCADE').
- **Novo Índice**: `ix_canvas_frames_user_id` (`user_id`).

#### Tabela `search_history`
- **Nova Coluna**: `user_id` (`String(36)`, Not Null, FK `users.id`, ondelete='CASCADE').
- **Atualização de Índice**: O índice `ix_search_history_query` passa a ser composto `("user_id", "query")` para permitir que diferentes usuários façam a mesma busca sem conflito de unicidade.

---

## 3. Regras de Integridade e Validação

1. **Atribuição Automática de Propriedade**:
   - Todo registro criado (`Book`, `Study`, `StudyRelation`, etc.) recebe obrigatoriamente `user_id = current_user.id`. O cliente nunca envia o `user_id` no corpo da requisição; ele é injetado pelo servidor com base no contexto de autenticação.
2. **Consistência de Pertencimento Hierárquico**:
   - Ao criar um `Study` para um determinado `chapter_id`, o servidor valida se o capítulo e seu respectivo livro pertencem ao mesmo `current_user.id`.
   - Ao criar uma `StudyRelation` entre `source_study_id` e `target_study_id`, ambos os estudos devem pertencer ao `current_user.id`.
3. **Exclusão Lógica e Restauração Hermética**:
   - Ao enviar para a lixeira (`deleted_at`), o recurso permanece vinculado ao `user_id`.
   - A listagem da lixeira e o comando de restauração filtram exclusivamente `user_id == current_user.id`.
4. **Resolução de Anti-Enumeração (IDOR)**:
   - Tentativa de consulta, alteração ou exclusão de recurso com `user_id != current_user.id` emite `HTTP 404 Not Found` idêntico a ID inexistente.
