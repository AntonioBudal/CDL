# Data Model: F0.6.7 — Normalização de Categorias

Este documento define o modelo conceitual e relacional de dados para a taxonomia canônica do Leitorum.

---

## 1. Entidades e Mapeamento Relacional

```
┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
│              User               │                 │              Book               │
├─────────────────────────────────┤                 ├─────────────────────────────────┤
│ id: String(36) [PK]             │ 1             N │ id: Integer [PK]                │
│ username: String                │───────────────< │ user_id: String(36) [FK]        │
│ ...                             │                 │ title: String                   │
└─────────────────────────────────┘                 └─────────────────────────────────┘
                 │ 1                                                 │ 1
                 │                                                   │
                 │ N                                                 │ N
┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
│            Category             │ 1             N │         book_categories         │
├─────────────────────────────────┤───────────────< ├─────────────────────────────────┤
│ id: String(50) [PK] (slug)      │                 │ book_id: Integer [PK, FK]       │
│ user_id: String(36) [FK, NULL]  │                 │ category_id: Text [PK, FK]      │
│ name: Text (Canônico Singular)  │                 └─────────────────────────────────┘
│ normalized_name: Text           │
│ parent_id: Text [NULL]          │
│ path: Text                      │
│ is_canonical: Boolean (default) │
│ created_at: UTCDateTime         │
└─────────────────────────────────┘
```

---

## 2. Detalhes das Entidades

### Entidade `Category` (Tabela `categories`)
Representa uma categoria temática oficial no sistema.

* **`id`** (`String(50)`, Chave Primária): Identificador textual canônico baseado em slug limpo (ex.: `"filosofia"`, `"historia"`, `"ciencia"`).
* **`user_id`** (`String(36)`, Chave Estrangeira opcional para `users.id`): Nulo para categorias globais canônicas do sistema, ou associado a um usuário em categorias personalizadas.
* **`name`** (`Text`, Não Nulo): Nome oficial legível, sempre em **forma singular**, com grafia e acentuação corretas (ex.: `"Filosofia"`, `"História"`, `"Ficção"`).
* **`normalized_name`** (`Text`, Não Nulo, com índice): Versão para busca e unicidade (minúsculas, sem diacríticos e sem espaços extras, ex.: `"filosofia"`, `"historia"`).
* **`parent_id`** (`Text`, Nulo): Mantido como coluna no banco para compatibilidade, porém configurado estritamente como `NULL` para a taxonomia plana.
* **`path`** (`Text`, Não Nulo): Equivalente ao próprio identificador canônico `id`.
* **`is_canonical`** (`Boolean`, Padrão: `True`): Indica se o termo pertence ao catálogo canônico oficial.
* **`created_at`** (`UTCDateTime`, Não Nulo): Timestamp UTC de criação.

---

### Tabela de Junção `book_categories`
Mantém a associação Many-to-Many entre livros e categorias canônicas.

* **`book_id`** (`Integer`, Chave Estrangeira para `books.id`, `ondelete="CASCADE"`): Identificador da obra.
* **`category_id`** (`Text`, Chave Estrangeira para `categories.id`, `ondelete="RESTRICT"`): Identificador da categoria canônica.
* **Chave Primária Composta**: `(book_id, category_id)`.
* **Garantia de Unicidade**: Impede que o mesmo livro seja associado mais de uma vez à mesma categoria canônica, mesmo após convergência de categorias antigas.

---

## 3. Regras de Validação e Integridade

1. **Unicidade de Nome Normalizado**: Não pode existir mais de uma categoria com o mesmo `normalized_name` para o mesmo escopo (`user_id` ou global).
2. **Forma Singular e Termo Conciso**:
   - Comprimento mínimo de 2 caracteres, máximo de 30 caracteres.
   - Proibição de pontuações arbitrárias, delimitadores numéricos ou caracteres de controle.
   - Proibição de plurais terminados em sufixos evidentes quando a forma singular existir.
3. **Integridade Referencial na Exclusão**:
   - A exclusão de uma categoria que ainda possua livros associados é bloqueada com `RESTRICT` e gera mensagem informativa exigindo desassociação prévia.
   - A exclusão de um livro remove em cascata apenas os seus próprios registros em `book_categories`.

---

## 4. Dicionário Canônico Inicial de Referência (Amostra do Catálogo)

| Slug / ID | Nome Canônico (Singular) | Termos Legados Mapeados (Exemplos) |
| :--- | :--- | :--- |
| `filosofia` | Filosofia | Filosofias, Filosofia Antiga, Filosofia Moderna, Teoria Filosófica |
| `historia` | História | Histórias, Histórias do Brasil, Historiografia, Narrativas Históricas |
| `ciencia` | Ciência | Ciências, Ciências Sociais e Humanas, Ciências Naturais, Estudos Científicos |
| `literatura` | Literatura | Literaturas, Estudos Literários, Obras Literárias |
| `ficcao` | Ficção | Ficções, Ficção Científica, Histórias de Ficção, Contos de Ficção |
| `psicologia` | Psicologia | Psicologias, Estudos Psicológicos, Psicanálise e Teoria |
| `politica` | Política | Políticas, Teorias Políticas Modernas, Ciência Política |
| `direito` | Direito | Direitos, Legislação e Direito, Teoria do Direito |
| `economia` | Economia | Economias, Ciências Econômicas, Finanças e Economia |
| `sociologia` | Sociologia | Sociologias, Estudos Sociológicos |
| `arte` | Arte | Artes, Artes Visuais, História da Arte |
| `educacao` | Educação | Educações, Pedagogia e Educação, Práticas Educativas |
| `tecnologia` | Tecnologia | Tecnologias, Computação e Tecnologia |
