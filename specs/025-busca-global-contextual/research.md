# Research: F08 — Busca Global Contextual

**Feature Branch**: `025-busca-global-contextual`  
**Date**: 2026-09-19  
**Specification**: [spec.md](./spec.md)  

---

## 1. Decisões Arquiteturais e Pesquisa Técnica

### Decisão 1: Mecanismo de Indexação e Busca Textual no SQLite

- **Problema**: O acervo do leitor contém estudos com termos técnicos, filosóficos e citações na língua portuguesa, com frequente uso de acentuação diacrítica (ex.: "concepção", "lógica", "análise"). O usuário pode digitar consultas com ou sem acentos (ex.: "analise" buscando "análise"). Além disso, o ambiente local é Windows (Python 3.13) e deve funcionar sem depender de bibliotecas externas compiladas em C ou binários proprietários.
- **Alternativas Avaliadas**:
  1. *SQLite FTS5 com tokenizer customizado*: O módulo FTS5 é poderoso, mas o suporte a remoção de acentos em português varia conforme as flags de compilação da biblioteca `sqlite3.dll` no Windows, além de exigir tabelas virtuais sincronizadas via triggers, o que complica migrações com Alembic em modo `render_as_batch=True`.
  2. *SQL LIKE com função Python UDF `unaccent` registrada na conexão (Escolhida)*: O SQLite permite registrar funções determinísticas em Python via `connection.create_function("unaccent", 1, unaccent_func)`. A normalização Unicode (`unicodedata.normalize('NFKD', text)`) remove marcas diacríticas de forma nativa e rápida.
- **Decisão**: Adotar a UDF `unaccent` registrada no evento `connect` do SQLAlchemy (`app/db/session.py`), permitindo consultas `unaccent(campo) LIKE '%termo%'`.
- **Racional**:
  - 100% de portabilidade no Windows sem dependência de módulos ou compilações externas.
  - Insensibilidade completa a acentuação e maiúsculas/minúsculas.
  - Para o porte de dados de um caderno de leitura pessoal (centenas a dezenas de milhares de estudos), a execução no SQLite em memória/WAL ocorre em menos de 15ms.
  - Compatibilidade nativa com o Alembic e todas as migrações existentes.

---

### Decisão 2: Estratégia de Combinação de Termos (AND vs OR)

- **Problema**: Ao pesquisar expressões com múltiplas palavras (ex.: "crítica razão pura"), o leitor espera precisão sem perder a capacidade de encontrar correspondências parciais quando a busca estrita não retornar nada.
- **Alternativas Avaliadas**:
  1. *Disjunção incondicional (OR)*: Retorna muitos resultados espúrios para palavras comuns.
  2. *Conjunção estrita (AND) com fallback assistido (Escolhida)*:
     - Por padrão, o filtro exige que todos os termos da consulta estejam presentes no estudo (mesmo que em campos diferentes, ex.: um termo no título e outro no resumo).
     - Se o resultado for vazio, a API e a UI indicam a sugestão de relaxamento para "qualquer um dos termos" (OR) em 1 clique.
- **Decisão**: Implementar o parâmetro `mode: "and" | "or"` (padrão `"and"`) na API `/api/search`.

---

### Decisão 3: Algoritmo de Extração de Snippets e Realce Seguro (`<mark>`)

- **Problema**: Textos de estudos podem ter milhares de caracteres. Exibir o texto integral polui a visualização. É necessário extrair um trecho conciso contendo a ocorrência do termo, sem risco de injeção HTML (*XSS*).
- **Alternativas Avaliadas**:
  1. *Corte no frontend*: Enviar o texto completo para o cliente consumir banda desnecessária e sobrecarregar o renderizador do Vue.
  2. *Extração e sanitização no backend (Escolhida)*:
     - O backend localiza o índice do primeiro match no texto normalizado.
     - Recorta uma janela de ~140 caracteres (aproximadamente 60 caracteres antes e 80 após o match), respeitando limites de palavras.
     - Higieniza caracteres especiais HTML (`html.escape`).
     - Insere tags `<mark class="search-highlight">...</mark>` ao redor dos termos coincidentes.
     - Retorna o snippet pronto e o nome do campo correspondente (`matched_field`: "Título", "Resumo", "Explicação", "Conceitos", "Referências", "Anotações").
- **Decisão**: Extração e sanitização estruturada no `search_service.py` do backend.

---

### Decisão 4: Persistência do Histórico de Buscas e Prontidão para Sincronização

- **Problema**: O leitor deseja que suas pesquisas recentes fiquem salvas para retomada rápida, funcionando tanto no PC quanto no smartphone (via rede local) e preparadas para sincronização futura em nuvem (ex.: conta Google).
- **Alternativas Avaliadas**:
  1. *Apenas `localStorage` no navegador*: Limita as buscas ao dispositivo específico; perde o histórico ao trocar do PC para o celular.
  2. *Tabela relacional no banco de dados com API REST (Escolhida)*:
     - Criação da tabela `search_history` no SQLite via migração Alembic.
     - Armazena `query`, `created_at` e `updated_at`.
     - Ao pesquisar, registra o termo; se já existir, atualiza o timestamp `updated_at` (evitando duplicatas na lista dos 10 recentes).
     - Endpoints para listagem e limpeza individual/total (`DELETE /api/search/history/{id}` e `DELETE /api/search/history`).
- **Decisão**: Tabela `search_history` persistida no SQLite via migração `0010_add_search_history.py`.

---

### Decisão 5: Interface do Usuário e Ergonomia Móvel

- **Componente**: `GlobalSearchModal.vue` acionado globalmente via botão no cabeçalho ou atalho de teclado (`Ctrl+K` / `/`).
- **Comportamento Desktop**:
  - Modal centralizado com backdrop escuro e foco imediato no campo de entrada.
  - Navegação vertical com teclas direcionais (↑/↓) e confirmação com Enter.
  - Fechamento com Esc ou clique fora.
- **Comportamento Mobile (<768px)**:
  - Overlay em tela cheia com alvos táteis mínimos de 44x44px.
  - Contenção estrita de rolagem lateral (`overflow-x: hidden`).
  - Botão visível "Fechar" no topo direito para descarte ágil.
- **Transição de 1 Clique**:
  - Ao clicar no resultado, navega para `/books/{book_id}?study={study_id}&highlight={term}`.
  - A tela do estudo abre com foco e breve animação de pulso visual no elemento.
