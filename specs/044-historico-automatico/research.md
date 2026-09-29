# Research: F0.6.5 — Histórico Automático de Versões de Estudo

## Objetivo da Pesquisa

Definir a estratégia técnica, modelos de dados, algoritmos de cálculo de diff e padrões de UX para o registro automático de versões, consulta de histórico, visualização comparativa e restauração segura de estudos no Caderno de Leitura.

---

## 1. Registro Automático e Coalescência de Versões (Debounce / Coalesce)

### Decisão
Implementar a captura de snapshots no momento da persistência das alterações do estudo no backend (`PATCH /api/studies/{id}`), com uma janela de coalescência de 5 minutos baseada no autor da edição.

### Racional
- **Garantia de consistência**: Capturar a versão no backend garante que qualquer interface (web desktop, web mobile, requisições diretas de API) registre versões uniformemente, sem depender de temporizadores voláteis do navegador.
- **Transação atômica**: A criação da versão ocorre dentro da mesma transação do banco (`commit_changes(session)`), garantindo que nunca ocorra salvamento do estudo sem a versão correspondente.
- **Regra dos 5 minutos**:
  - Se a versão mais recente deste estudo foi criada/atualizada há menos de 5 minutos pelo mesmo usuário (`user_id`), atualiza-se o snapshot existente (`updated_at = utc_now()`) e atualiza-se o conteúdo.
  - Se o intervalo for superior a 5 minutos, ou se o autor for diferente, um novo número de versão sequencial (`version_number = max + 1`) é gerado.
  - Caso o estudo nunca tenha tido versões anteriores (ex.: estudos antigos já existentes no banco), cria-se primeiro um snapshot de versão base ("Versão inicial") com os dados prévios e, em seguida, a nova versão modificada.
- **Detecção de alteração real**: Se o payload de alteração não modificar nenhum campo textual relevante (`title`, `summary`, `explanation`, `concepts`, `references`, `notes`), nenhuma versão é gerada ou atualizada.

### Alternativas Consideradas
- *Autosave contínuo a cada digitação (client-side)*: Descartado por gerar tráfego excessivo de rede, sobrecarregar o SQLite local com transações microscópicas e aumentar o risco de conflitos concorrentes em dispositivos móveis.
- *Histórico via log de comandos (Event Sourcing/CRDT)*: Complexidade desnecessária para a escala de caderno pessoal de estudos; o snapshot integral é mais simples, imutável e transparente.

---

## 2. Abrangência e Persistência do Snapshot (Texto + Destaques)

### Decisão
O modelo `StudyVersion` persistirá o snapshot completo do estudo:
1. Campos textuais: `title`, `summary`, `explanation`, `concepts`, `references`, `notes`.
2. Metadados do autor e carimbos de tempo: `user_id`, `created_at`, `updated_at`, `change_summary`.
3. Snapshot de Leitura Ativa (`highlights_data`): Serialização em JSON estruturado de todos os `study_highlights` ativos no momento da versão (`section`, `selected_text`, `start_offset`, `end_offset`, `prefix`, `suffix`, `color`, `kind`, `note`).

### Racional
- Conforme decidido na clarificação (Q2: A), os estudos no Leitorum combinam texto e marcações ativas (perguntas, termos ocluídos, notas e citações).
- Se uma versão anterior for restaurada, os destaques correspondentes àquele texto devem ser recuperados em sincronia; caso contrário, os offsets dos destaques apontariam para posições textuais inválidas do texto atual.
- O campo `highlights_data` como JSON em coluna `Text` do SQLite permite armazenamento compacto e leitura rápida sem criar tabelas secundárias com chaves estrangeiras complexas para snapshots imutáveis.

### Alternativas Consideradas
- *Tabela relacional separada `study_version_highlights`*: Aumentaria a sobrecarga de queries e joins para entidades que nunca são consultadas isoladamente (apenas acompanham a versão pai). O campo JSON em coluna de texto é padrão no SQLAlchemy 2 e no ecossistema SQLite.

---

## 3. Algoritmo e Apresentação de Diff Comparativo

### Decisão
Fornecer endpoint dedicado `GET /api/studies/{study_id}/versions/{version_id}/diff` utilizando a biblioteca padrão do Python (`difflib.SequenceMatcher`), entregando uma estrutura serializada de diferenças por seção para o frontend. Além disso, disponibilizar o endpoint de leitura integral da versão `GET /api/studies/{study_id}/versions/{version_id}` para visualização completa em modo somente leitura.

### Racional
- `difflib` faz parte da biblioteca padrão do Python (zero novas dependências).
- O backend compara o texto da versão selecionada com a versão de referência (por padrão, a versão atual ativa do estudo, ou outra versão informada no query param `target_version_id`).
- O retorno divide as diferenças por seção (`title`, `summary`, `explanation`, `concepts`, `references`, `notes`):
  - `status`: `"modified"` | `"unchanged"` | `"added"` | `"removed"`.
  - `chunks`: lista de blocos com `{ "type": "equal" | "insert" | "delete", "text": "..." }` ou linhas com diferenças.
- No frontend, o componente renderiza os blocos com classes CSS semânticas (`diff-ins`, `diff-del`, `diff-unchanged`), garantindo contraste acessível, suporte a temas claro/escuro e alta performance (< 50ms de renderização).

### Alternativas Consideradas
- *Cálculo de diff exclusivo no frontend via biblioteca NPM pesada*: Requereria adicionar novas dependências como `diff` ou `diff-match-patch` ao `package.json`, aumentando o bundle. A solução híbrida mantém o bundle leve e utiliza o poder do Python no backend.

---

## 4. Fluxo e Segurança de Restauração

### Decisão
Implementar a restauração via endpoint `POST /api/studies/{study_id}/versions/{version_id}/restore`:
1. Verifica se o usuário atual possui permissão de escrita no estudo.
2. Recupera o snapshot da versão alvo.
3. Se o estado presente do estudo divergir da última versão arquivada, salva preventivamente um snapshot do estado presente antes de sobrescrever.
4. Aplica os campos textuais no registro `Study` ativo.
5. Limpa os destaques atuais do estudo e insere os destaques presentes no snapshot da versão restaurada.
6. Cria um novo registro em `study_versions` com `change_summary = "Restauração da versão X"`.
7. Incrementa o contador de concorrência `study.version += 1` e atualiza `study.updated_at = utc_now()`.
8. Retorna o `StudyRead` atualizado para o frontend, que emite notificação e recarrega os dados.

### Racional
- Preserva a rastreabilidade total: restaurar nunca apaga o histórico; a restauração simplesmente adiciona um novo marco cronológico que reflete o estado recuperado.
- Previne perda de dados por clique acidental com diálogo de confirmação claro no frontend.

---

## 5. Diretrizes de Interface e Acessibilidade (UI / UX)

### Decisão
Criar o componente `StudyHistoryModal.vue` e integrá-lo tanto no `StudyView.vue` (visualização) quanto no `StudyEditView.vue` (edição).
- Layout em painel dividido:
  - Esquerda: Linha do tempo cronológica com cartões de versão (número, data/hora formatada, autor, etiqueta de versão atual/restauração, tamanho do texto).
  - Direita: Área de conteúdo com alternador de abas ("Inspeção Completa" vs "Comparar Alterações").
- Barra superior de ações com botão proeminente "Restaurar esta versão" (visível apenas para quem tem permissão de escrita).
- Zero emojis em botões, títulos ou indicadores.
- Totalmente navegável por teclado (`Esc` para fechar, setas para navegar entre versões).
- Responsivo: Em telas menores que 768px, o painel se reorganiza em visualização com seletor de versões no topo.
