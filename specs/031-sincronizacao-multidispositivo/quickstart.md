# Quickstart: Sincronização Multidispositivo (F04)

**Feature**: `031-sincronizacao-multidispositivo`  
**Date**: 2026-09-22  

Este guia detalha os procedimentos para testar e validar o controle otimista de concorrência (`HTTP 409 Conflict`), a reconciliação incremental de dados (`/api/sync/changes`), a sincronização de preferências do leitor e o comportamento no frontend.

---

## 1. Pré-Requisitos e Ambiente

- Python 3.13 / 3.14 (64 bits) no Windows com dependências instaladas.
- Node.js 24 com dependências do frontend instaladas.
- Diretório de trabalho: `caderno-leitura-0.1`.
- Para testes automatizados: bancos SQLite efêmeros (`tmp_path`) sem impacto no banco ativo.

---

## 2. Cenário 1: Atualização Sequencial com Avanço de Versão

**Objetivo**: Confirmar que requisições de atualização avançam o contador monotônico `version`.

### Procedimento
1. Obter o estudo atual:
   ```http
   GET /api/studies/1
   ```
   **Resultado Esperado**: `HTTP 200 OK` contendo `"version": 1`.
2. Enviar atualização informando `expected_version = 1`:
   ```http
   PATCH /api/studies/1
   Content-Type: application/json

   {
     "title": "Título Atualizado Sequencialmente",
     "expected_version": 1
   }
   ```
   **Resultado Esperado**: `HTTP 200 OK` contendo `"version": 2` e `updated_at` atualizado.

---

## 3. Cenário 2: Detecção de Conflito de Concorrência (HTTP 409)

**Objetivo**: Garantir que requisições enviando versão obsoleta sejam barradas sem alterar os dados no servidor.

### Procedimento
1. Estudo no servidor está na versão `2`.
2. Cliente defasado tenta atualizar enviando `expected_version = 1`:
   ```http
   PATCH /api/studies/1
   Content-Type: application/json

   {
     "title": "Tentativa Conflitante do Cliente Defasado",
     "expected_version": 1
   }
   ```
   **Resultado Esperado**:
   - `HTTP 409 Conflict`
   - Payload:
     ```json
     {
       "detail": "Conflito de concorrência: o registro foi modificado em outro dispositivo.",
       "entity_id": 1,
       "entity_type": "study",
       "server_version": 2,
       "server_updated_at": "...",
       "server_data": {
         "title": "Título Atualizado Sequencialmente",
         ...
       }
     }
     ```
   - O título no banco permanece inalterado.

---

## 4. Cenário 3: Resolução de Conflito com Sobrescrita Local

**Objetivo**: Validar a mecânica de "Sobrescrever com rascunho local" após um conflito 409.

### Procedimento
1. Após receber o 409 com `server_version = 2`, o cliente reenvia o salvamento ajustando a expectativa:
   ```http
   PATCH /api/studies/1
   Content-Type: application/json

   {
     "title": "Texto Local Vencedor",
     "expected_version": 2
   }
   ```
   **Resultado Esperado**:
   - `HTTP 200 OK`
   - Objeto gravado com `"title": "Texto Local Vencedor"` e `"version": 3`.

---

## 5. Cenário 4: Feed de Alterações Incrementais e Exclusões (Tombstones)

**Objetivo**: Verificar a entrega de entidades criadas/modificadas e identificadores de itens excluídos desde um timestamp.

### Procedimento
1. Registrar o timestamp atual `T0`.
2. Modificar o Estudo 1 (`updated_at` > `T0`) e mover o Estudo 2 para a lixeira (`deleted_at` > `T0`).
3. Consultar o feed incremental:
   ```http
   GET /api/sync/changes?since=<T0>
   ```
   **Resultado Esperado**:
   - `HTTP 200 OK`
   - `updated.studies` contém o Estudo 1 com seus campos e versão.
   - `deleted.study_ids` contém `[2]`.
   - `server_time` presente com timestamp UTC.

---

## 6. Cenário 5: Sincronização de Preferências do Leitor

**Objetivo**: Validar a leitura e atualização de preferências de visualização (Superclasse, modo de exibição, etc.).

### Procedimento
1. Consultar preferências:
   ```http
   GET /api/preferences
   ```
   **Resultado Esperado**: `HTTP 200 OK` com valores padrão (`active_superclass: "mecanica"`, `preferred_view_mode: "grid"`).
2. Atualizar preferência para superclasse `monolitica`:
   ```http
   PUT /api/preferences
   Content-Type: application/json

   {
     "active_superclass": "monolitica",
     "superclass_intensity": 1.5,
     "preferred_view_mode": "tree"
   }
   ```
   **Resultado Esperado**: `HTTP 200 OK` persistido com versão incrementada.

---

## 7. Cenário 6: Isolamento Estrito por Usuário

**Objetivo**: Garantir que o feed de alterações e as preferências nunca exponham dados de outro leitor.

### Procedimento
1. Usuário B consulta `GET /api/sync/changes`.
2. **Resultado Esperado**: Recebe exclusivamente livros e estudos criados pelo Usuário B; nenhum dado do Usuário A é incluído no payload.

---

## 8. Comandos de Validação Automatizada

```powershell
# Testes do backend para concorrência e sincronização
python -m pytest backend/tests/test_sync_and_concurrency.py -v

# Suíte completa de testes e verificação de tipos do frontend
npm test
npm run build
```
