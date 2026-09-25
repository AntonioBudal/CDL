# Guia de Arquitetura: Sincronização Multidispositivo e Concorrência Otimista (F04)

Este documento descreve as decisões arquiteturais, o protocolo de rede e a dinâmica de concorrência e reconciliação multidispositivo implementados na Feature 04 do **Caderno de Leitura**.

---

## 1. Princípios Arquiteturais Centrais

1. **Fonte Única da Verdade (*Single Source of Truth*)**: O backend central (FastAPI + SQLite WAL) é a autoridade máxima e definitiva de estado para todas as operações de escrita, leitura e reconciliação. Nenhum cliente impõe seu estado sem validação prévia.
2. **Controle Otimista de Concorrência (OCC)**: As entidades do acervo (`Study`, `Book`, `StudyCanvasNode` e `UserPreference`) utilizam contadores inteiros monotônicos de versão (`version: int`) iniciados em 1 e incrementados atômica e sucessivamente a cada modificação.
3. **Isolamento Estrito Multiusuário**: Todas as consultas de feed incremental, busca de preferências e mutações espaciais são obrigatoriamente filtradas por `user_id == current_user.id`, impedindo vazamento de dados ou alteração indevida entre contas distintas.
4. **Preservação Sagrada de Rascunhos**: Em nenhuma circunstância o cliente descarta o texto digitado pelo leitor caso ocorra um conflito de concorrência (`HTTP 409 Conflict`) ou perda de conexão.
5. **Ergonomia e Adaptação Espacial Diferenciada**: As coordenadas absolutas dos cartões no Canvas 2D (`x, y`) são centralizadas e sincronizadas entre dispositivos, enquanto a câmera de visualização (zoom e deslocamento pan) permanece estritamente local em cada dispositivo, respeitando telas ultrawide vs. celulares.

---

## 2. Controle Otimista de Concorrência (OCC)

### 2.1 Fluxo de Validação no Backend

Ao emitir uma requisição `PATCH /api/studies/{id}` ou `PATCH /api/books/{id}`:
1. O cliente informa `expected_version: int`.
2. O servidor compara `expected_version == entity.version`.
3. Se os números coincidirem:
   - Os campos modificados são aplicados.
   - O contador é incrementado: `entity.version += 1`.
   - A transação é comitada e o servidor responde `HTTP 200 OK` com o registro atualizado.
4. Se os números divergirem:
   - A transação é abortada imediatamente.
   - O servidor responde com `HTTP 409 Conflict` e um payload estruturado `ConflictErrorResponse`.

### 2.2 Estrutura do Payload de Conflito (`ConflictErrorResponse`)

```json
{
  "detail": "Conflito de concorrência: este estudo foi modificado em outro dispositivo. Seus dados foram preservados no formulário.",
  "entity_id": 42,
  "entity_type": "study",
  "server_version": 3,
  "server_updated_at": "2026-09-24T21:00:00Z",
  "server_data": {
    "id": 42,
    "title": "Título vigente no servidor",
    "location": "p. 10",
    "summary": "Resumo gravado por outro terminal",
    "explanation": "...",
    "version": 3
  }
}
```

### 2.3 Resolução de Conflitos no Frontend

O componente acessível `ConflictResolutionModal.vue` intercepta o erro 409 e apresenta três caminhos:
1. **Sobrescrever com rascunho local**: Reenvia a requisição com `expected_version = server_version`, gravando com sucesso na versão `server_version + 1`.
2. **Adotar versão do servidor**: Descarta as alterações locais e recarrega os dados vigentes no servidor.
3. **Comparar lado a lado**: Expande uma tabela de diferenças destacando os campos divergentes entre o formulário local e o servidor.

---

## 3. Feed Incremental de Alterações (`GET /api/sync/changes`)

### 3.1 Parâmetros e Funcionamento

- `GET /api/sync/changes`: Retorna o estado completo do acervo do usuário autenticado.
- `GET /api/sync/changes?since=<ISO-8601-UTC>`: Retorna apenas entidades criadas ou modificadas após o instante informado, além dos IDs de registros que foram excluídos (tombstones baseados em `deleted_at > since`).

### 3.2 Resposta Particionada (`SyncChangesResponse`)

```json
{
  "server_time": "2026-09-24T21:30:00Z",
  "updated": {
    "books": [...],
    "studies": [...],
    "canvas_nodes": [...],
    "preferences": {...}
  },
  "deleted": {
    "book_ids": [15],
    "study_ids": [108, 109]
  }
}
```

---

## 4. Sincronização de Preferências e Metadados Visuais

- **Rotas**: `GET /api/preferences` e `PUT /api/preferences`.
- **Campos Sincronizados**:
  - `active_superclass`: Superclasse cinemática ativa (`zero-g`, `mecanica`, `invisivel`, `dimensional`, `monolitica`).
  - `superclass_intensity`: Intensidade física entre 0.0 e 2.0.
  - `preferred_view_mode`: Modo de visualização (`grid`, `list`, `tree`, `canvas`, `cockpit`).
  - `tree_collapsed_state`: Lista de IDs com nós colapsados na árvore.
  - `font_family`, `font_scale`, `theme_mode`: Configurações de tipografia e tema.
  - `version`: Controle OCC com `expected_version`.

---

## 5. Orquestração Reativa no Cliente (`useSync.ts`)

O composable reativo `useSync.ts` monitora os seguintes eventos:
- `online`: Dispara sincronização imediata assim que a rede é restabelecida.
- `visibilitychange`: Dispara sincronização quando a aba do navegador volta ao primeiro plano (despertar de suspensão/standby móvel).
- `focus`: Dispara sincronização debounced quando a janela ganha foco.
- Dispara evento DOM customizado `caderno:sync-applied` para notificar views ativas de novas atualizações.

---

## 6. Indicador de Conexão (`SyncStatusBadge.vue`)

Localizado no cabeçalho da aplicação, reflete os estados:
- **Sincronizado**: Verde suave/neutro com ícone `Check`.
- **Sincronizando…**: Azul suave com ícone `RefreshCw` rotativo.
- **Offline — dados retidos no dispositivo**: Âmbar discreto com ícone `CloudOff`.
- **Conflito de concorrência**: Vermelho/alerta com ícone `AlertTriangle`.

Em conformidade com a Constituição do projeto, **nenhum emoji informal é utilizado**.
