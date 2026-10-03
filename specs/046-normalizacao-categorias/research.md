# Technical Research & Architectural Decisions: F0.6.7 — Normalização de Categorias

Este documento consolida as decisões de arquitetura e tecnologia para a implementação da **Feature 046 — Normalização e Simplificação de Categorias** do Roadmap 0.6.

---

## Decisão 1: Taxonomia Plana e Descontinuação de Hierarquia Aninhada

* **Decisão**: A taxonomia de categorias passa a operar como uma **estrutura estritamente plana (*flat*) de nível único**. Na tabela `categories`, a coluna `parent_id` permanece nula (`NULL`) para todas as categorias canônicas e a coluna `path` é mantida idêntica ao `name` (ou ao identificador slug), eliminando navegação de árvore aninhada arbitrária.
* **Justificativa**: A hierarquia com `parent_id` gerava ramificações desordenadas, dificultava filtros na biblioteca e multiplicava termos redundantes. Categorias planas de palavra única oferecem filtragem instantânea, indexação direta e consistência visual tanto no desktop quanto no mobile.
* **Alternativas Rejeitadas**:
  - *Manter árvore ilimitada*: Rejeitada por manter a complexidade cognitiva que motivou o Roadmap 0.6.
  - *Árvore de 1 nível opcional*: Rejeitada conforme decisão de alinhamento do usuário (Q1: Opção A), que determinou taxonomia totalmente plana.

---

## Decisão 2: Algoritmo de Normalização Canônica e Regras Gramaticais

* **Decisão**: Implementar um módulo de serviço (`category_normalizer.py`) com regras determinísticas para:
  1. **Remoção de Espaços e Pontuação**: `strip()` e substituição de múltiplos espaços por espaço único.
  2. **Colapso de Caixa e Diacríticos para Busca**: Campo derivado `normalized_name` em minúsculas e sem acentos para indexação única (evitando duplicatas como "historia" vs "História").
  3. **Grafia Oficial Canônica**: Nome exibido sempre com inicial maiúscula (Title Case) e acentuação gráfica correta em língua portuguesa (ex.: "História", "Ficção", "Filosofia").
  4. **Forma Singular**: Regras de lematização/singularização básica para sufixos comuns em português (`-s`, `-es`, `-ões` -> `-ão`, `-res` -> `-r`).
* **Justificativa**: Garante que buscas, autocompletar e validações reconheçam variações fonéticas ou de digitação sem poluir a base com termos duplicados.
* **Alternativas Rejeitadas**:
  - *Apenas validação case-sensitive*: Permitiria duplicatas graves no banco como "filosofia" e "Filosofia".

---

## Decisão 3: Atribuição Distributiva e Deduplicação em `book_categories`

* **Decisão**: No processo de migração, categorias legadas compostas mapeiam para uma lista de categorias canônicas (1 para N). Ao aplicar a atribuição distributiva aos livros da tabela `book_categories`:
  - A migração itera sobre os vínculos e insere os novos pares `(book_id, canonical_category_id)`.
  - Como a chave primária de `book_categories` é `(book_id, category_id)`, inserções concorrentes ou repetidas utilizam cláusula `ON CONFLICT DO NOTHING` (ou verificação prévia no SQLAlchemy) para garantir idempotência matemática e zero violações de chave primária.
* **Justificativa**: Atende rigorosamente à decisão Q3 (Opção A) do usuário, garantindo que nenhum livro perca seus temas constituintes e prevenindo erros de integridade relacional.
* **Alternativas Rejeitadas**:
  - *Atribuição arbitrária ao primeiro termo*: Rejeitada por perda de contexto semântico do segundo tema do livro.

---

## Decisão 4: Normalização Assistida no Frontend com Autocomplete

* **Decisão**: O componente de entrada de categorias no formulário de livros (`CategoryInput.vue`) oferece:
  - Dropdown com autocomplete em tempo real baseado no catálogo canônico aprovado.
  - Ao digitar um termo plural (ex.: "Sociologias"), o sistema sugere dinamicamente a conversão para a forma canônica singular ("Sociologia").
  - Badges visuais acessíveis com botão de remoção rápida.
* **Justificativa**: Atende à decisão Q2 (Opção A). Reduz o esforço do leitor, previne digitação incorreta e mantém a taxonomia limpa sem atrito ou mensagens punitivas de erro.
* **Alternativas Rejeitadas**:
  - *Bloqueio seco sem sugestão*: Rejeitada por piorar a experiência do leitor (UX punitiva).

---

## Decisão 5: Estratégia de Migração Alembic Segura e Não Destrutiva

* **Decisão**: A migração Alembic (`0023_normalize_categories.py`) seguirá as salvaguardas constitucionais:
  1. O hook pré-migração automático existente em `backend/migrations/env.py` dispara o snapshot de segurança atômico do SQLite antes de qualquer DDL/DML.
  2. Insere o catálogo de categorias canônicas padrão caso ainda não existam.
  3. Aplica a tabela declarativa de correspondência `MIGRATION_MAP` para reatribuir os livros em `book_categories`.
  4. Preserva os registros legados em tabela de mapeamento de auditoria ou marca as categorias antigas não canônicas com flag/remoção limpa somente após a confirmação de que zero livros apontam para elas.
* **Justificativa**: Cumpre o Princípio I e o Princípio V da Constituição (preservação do acervo e atomicidade).
