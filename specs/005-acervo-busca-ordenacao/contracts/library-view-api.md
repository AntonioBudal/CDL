# Contrato de API e Interface: Acervo — Visualização, Busca e Ordenação

**Feature**: Acervo: Visualização, Busca e Ordenação  
**Branch**: `005-acervo-busca-ordenacao`  
**Data**: 2026-09-18  

---

## 1. Contrato da API REST (Backend)

### `GET /api/books`

Recupera livros do acervo ativo, com suporte opcional a busca e ordenação no servidor.

#### Parâmetros de Consulta (Query String) — Todos Opcionais
| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `q` | `string` | `None` | Termo de pesquisa a ser buscado (case-insensitive) em título, autor e subtítulo. |
| `sort` | `string` | `id` | Campo base para ordenação: `title`, `author`, `created_at`, `updated_at`, `year`, `id`. |
| `order` | `string` | `asc` | Sentido da ordenação: `asc` (crescente) ou `desc` (decrescente). |

#### Respostas

**200 OK** — Lista de livros retornada com sucesso
```json
[
  {
    "id": 1,
    "title": "A Arte da Guerra",
    "author": "Sun Tzu",
    "subtitle": "Edição comentada",
    "year": 2021,
    "cover_image": "a1b2c3d4e5f6.webp",
    "created_at": "2026-09-18T18:30:00Z",
    "updated_at": "2026-09-18T19:15:00Z",
    "deleted_at": null
  }
]
```

#### Regras de Segurança e Isolamento
- Livros com `deleted_at IS NOT NULL` (lixeira) **nunca** são retornados, independentemente dos parâmetros `q`, `sort` ou `order`.
- Se `q` for informado, o servidor aplica busca com `LIKE` insensível a maiúsculas:
  `title LIKE :q OR author LIKE :q OR subtitle LIKE :q`.
- Se nenhum livro for encontrado, retorna lista vazia `[]` com status `200 OK`.

---

## 2. Contrato de Componentes e Interface (Frontend)

### 2.1 Barra de Ferramentas do Acervo (`.library-toolbar`)

Posicionada acima da listagem de livros em `BooksView.vue`:

```text
+-----------------------------------------------------------------------------------------+
| [🔍 Buscar por título, autor...  (✕)]   [⇅ Ordenar por: Recentemente modif. ▾]   [⊞] [☰] |
+-----------------------------------------------------------------------------------------+
```

1. **Campo de Busca (`<input type="search">`)**:
   - `placeholder="Buscar por título, autor ou subtítulo…"`
   - `aria-label="Filtrar livros do acervo"`
   - Botão para limpar a busca quando houver texto digitado.
   - Tecla `Escape` limpa a busca.

2. **Seletor de Ordenação (`<select>`)**:
   - `aria-label="Critério de ordenação"`
   - Opções:
     - `recent-updated`: Recentemente modificados
     - `recent-created`: Recentemente adicionados
     - `title-asc`: Título (A–Z)
     - `title-desc`: Título (Z–A)
     - `author-asc`: Autor (A–Z)
     - `year-desc`: Ano de publicação
     - `oldest-created`: Mais antigos primeiro

3. **Alternador de Visualização (Segmented Control)**:
   - Botão "Grade de Capas": `aria-label="Exibir em grade de capas"`, `aria-pressed="true|false"`.
   - Botão "Lista Compacta": `aria-label="Exibir em lista compacta"`, `aria-pressed="true|false"`.

---

### 2.2 Estrutura do Modo "Lista Compacta" (`.book-list-compact`)

Cada linha da lista compacta renderiza:
- Miniatura pequena da capa (`size="sm"` com proporção 2:3 ou 36x54px).
- Título principal do livro com link direto (`<RouterLink :to="{ name: 'book', params: { bookId: book.id } }">`).
- Autor e ano de publicação alinhados.
- Data amigável da última atividade ou inclusão.
- Indicador visual e acessível de navegação.
