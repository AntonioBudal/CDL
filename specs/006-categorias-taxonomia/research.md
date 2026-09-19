# Research & Technical Decisions: Categorias e Taxonomia de Livros (T05)

**Feature**: `006-categorias-taxonomia`  
**Date**: 2026-09-18  
**Status**: Completed

---

## 1. Modelagem Hierárquica da Taxonomia (Árvore de Categorias)

### Contexto
O Roadmap 0.3 (T05) exige mais de 100 categorias úteis em português, com hierarquia estável, identificadores canônicos, rótulos legíveis e relação de categoria pai (`parent_id`), sem ciclos e com importação idempotente.

### Decisão
Utilizar o padrão **Adjacency List** com `parent_id` (auto-relacionamento na tabela `categories`) combinado com um campo de caminho desnormalizado `path` calculado automaticamente durante a carga/validação.

### Justificativa
- **Simplicidade e robustez**: O catálogo taxonômico é estático/canônico na v0.3, sendo lido frequentemente e alterado apenas em atualizações de versão.
- **Eficiência de leitura**: O campo `path` (ex.: `"Ciências Humanas / Filosofia / Ética"`) evita queries N+1 ou joins recursivos para exibição na interface e facilita buscas preditivas locais instantâneas (< 5ms).
- **Consultas hierárquicas recursivas no SQLite**: Quando o usuário filtra o acervo por uma categoria pai no backend (`GET /api/books?category=filosofia`), o SQLite resolve todas as subcategorias descendentes de forma nativa e extremamente rápida através de uma Common Table Expression (`WITH RECURSIVE`):
  ```sql
  WITH RECURSIVE subcategories AS (
      SELECT id FROM categories WHERE id = :category_id
      UNION ALL
      SELECT c.id FROM categories c
      JOIN subcategories s ON c.parent_id = s.id
  )
  SELECT book_id FROM book_categories WHERE category_id IN (SELECT id FROM subcategories);
  ```

### Alternativas Consideradas
- *Nested Sets (Conjuntos Aninhados)*: Requer recomputação de `lft` e `rgt` em inserções; complexidade desnecessária para uma taxonomia predominantemente estável.
- *Closure Table (Tabela de Fechamento)*: Tabela adicional `category_paths (ancestor, descendant, depth)`; útil em taxonomias dinâmicas com mutação frequente por múltiplos usuários, mas excessiva para SQLite local com CTEs nativas.

---

## 2. Associação Livros-Categorias (Muitos-para-Muitos)

### Contexto
Conforme esclarecido com o usuário e recomendado pelo Roadmap, cada livro pode pertencer a múltiplas categorias (N:N), permitindo associar, por exemplo, "Filosofia" e "Ciência Política" à mesma obra.

### Decisão
Criar a tabela de junção `book_categories`:
- `book_id`: Chave estrangeira referenciando `books.id` com `ON DELETE CASCADE`.
- `category_id`: Chave estrangeira referenciando `categories.id` com `ON DELETE RESTRICT`.
- Chave primária composta `(book_id, category_id)`.
- Índice secundário em `(category_id, book_id)` para aceleração de filtros por categoria.

### Preservação de Categorias em Atualizações Parciais (`PATCH /api/books/{id}`)
- O schema Pydantic `BookPatch` recebe `category_ids: list[str] | None = None`.
- Verificação via `self.model_fields_set`:
  - Se `category_ids` **não constar** no payload JSON enviado, os vínculos de categorias do livro permanecem intocados.
  - Se `category_ids` constar explicitamente (inclusive como lista vazia `[]`), o serviço sincroniza os vínculos, removendo desassociações e inserindo novas associações de forma atômica dentro da transação.

---

## 3. Catálogo Canônico (>100 Categorias) e Idempotência

### Contexto
T05 exige mais de 100 categorias em português com identificadores estáveis (slugs sem acento, ex.: `literatura-brasileira`), sem ciclos e sem duplicações.

### Decisão
- Armazenar o catálogo padronizado em um arquivo JSON canônico versionado no backend: `backend/app/data/canonical_categories.json`.
- O catálogo cobrirá 10 grandes áreas do conhecimento com subcategorias em 2 a 3 níveis de profundidade, totalizando ~120 categorias cuidadosamente selecionadas para um caderno de leitura e estudos:
  1. Literatura e Linguística
  2. Filosofia
  3. História
  4. Ciências Sociais e Humanas
  5. Psicologia e Psicanálise
  6. Ciências Exatas e da Natureza
  7. Computação e Tecnologia
  8. Artes, Arquitetura e Música
  9. Religião, Mitologia e Teologia
  10. Desenvolvimento Pessoal e Prática de Estudos
- Validador algorítmico de catálogo (`validate_catalogue`):
  - Verifica se há mais de 100 entradas.
  - Verifica unicidade estrita de `id`.
  - Verifica que todo `parent_id` aponta para um `id` existente.
  - Detecta ciclos na árvore via busca em profundidade (DFS com detecção de nós em visitação / coloração).
- Sincronizador idempotente (`sync_canonical_categories`):
  - Executa na inicialização do servidor e/ou em migração Alembic.
  - Insere novas categorias que não existiam no banco.
  - Atualiza nomes e caminhos de categorias existentes caso o JSON tenha sido refinado.
  - **Nunca remove** categorias do banco silenciosamente, evitando registros órfãos ou quebra de vínculos com livros existentes.

---

## 4. Busca Preditiva com Digitação (Autocomplete) e Caminho Hierárquico

### Contexto
O usuário precisa encontrar facilmente categorias digitando fragmentos de texto (ex.: "ética", "brasil", "ficcao"), vendo imediatamente o caminho hierárquico formatado.

### Decisão
- No backend: `GET /api/categories` retorna a lista completa de categorias com `id`, `name`, `parent_id` e `path`. O payload total de ~120 categorias tem menos de 15 KB (descomprimido), tornando viável o cache em memória no cliente.
- No frontend: Componente reutilizável de seleção preditiva (`CategorySelector.vue` ou campo integrado no `BookEditModal.vue`):
  - Normalização Unicode NFD (reutilizando a lógica estabelecida em T04): termos digitados sem acento como "etica" coincidem perfeitamente com "Ética".
  - Apresentação em dropdown com destaque da trilha (`path`) e do nome da categoria.
  - Navegação fluida por teclado (setas Cima/Baixo, Enter para selecionar, Esc para fechar).
  - Exibição de categorias selecionadas como badges (`CategoryBadge.vue`) com botão `✕` para desassociação rápida.

---

## 5. Filtragem Hierárquica Inclusiva no Acervo

### Contexto
Conforme aprovado no esclarecimento Q3 (Opção A), ao selecionar uma categoria pai (ex.: "Filosofia"), todos os livros de subcategorias filhas (ex.: "Filosofia / Ética", "Filosofia / Epistemologia") devem ser automaticamente incluídos no filtro da estante.

### Decisão
- O composable `useLibraryFilter` no frontend mantém `selectedCategory: string | null` (armazenando o `id` da categoria).
- O mapa hierárquico de descendentes é construído em memória no frontend a partir do catálogo carregado: para qualquer categoria selecionada, obtém-se o conjunto `Set<string>` contendo o próprio `id` e todos os `ids` de seus descendentes recursivos.
- Um livro passa no filtro de categoria se pelo menos uma de suas categorias associadas estiver contida nesse conjunto.
- O filtro é perfeitamente combinável com o campo de busca textual e a ordenação existente.
- Na barra de ferramentas (`LibraryToolbar.vue`), um seletor de categorias com opção "Todas as categorias" e contagem dinâmica é integrado sem poluir o layout existente.
