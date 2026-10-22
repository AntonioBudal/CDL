# Data Model & State Specifications: F0.9.02 — Ergonomia Mobile e Descongestionamento da Página do Livro

**Feature**: `specs/083-ergonomia-mobile-pagina-livro`  
**Date**: 2026-10-21  
**Status**: Completed  

---

## 1. Princípio de Isolamento de Dados

Em conformidade com a Constituição do projeto e com as regras invioláveis da versão **0.9 — Revisão Geral de UI/UX, Ergonomia e Estabilização**:
- **Zero alterações no banco de dados SQLite:** Nenhuma tabela, coluna ou índice novo é criado.
- **Zero alterações em modelos do backend:** Os schemas Pydantic e modelos SQLAlchemy permanecem 100% inalterados.
- Os modelos de dados abaixo representam as entidades de consumo existentes no frontend e as variáveis de estado reativo da interface da página do livro ([`BookView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/BookView.vue)).

---

## 2. Entidades de Dados do Frontend

### 2.1 Livro (`Book`)
Representa a obra cadastrada em exibição na rota `/livros/:bookId`.

```typescript
export interface Book {
  id: number
  title: string
  subtitle?: string | null
  author?: string | null
  year?: number | null
  cover_image?: string | null
  categories: CategorySummary[]
  created_at?: string
  updated_at?: string
}
```

### 2.2 Capítulo (`Chapter`)
Representa uma divisão estrutural do livro que agrupa estudos.

```typescript
export interface Chapter {
  id: number
  book_id: number
  name: string
  order_index: number
  created_at?: string
  updated_at?: string
}
```

### 2.3 Resumo de Estudo (`StudySummary`)
Representa a síntese de uma anotação vinculada a um capítulo específico.

```typescript
export interface StudySummary {
  id: number
  book_id: number
  chapter_id: number
  title: string
  location?: string | null
  char_count: number
  reading_status?: StudyReadingStatus
  template_id?: string | null
  updated_at?: string
}
```

---

## 3. Estado Reativo da Interface Móvel (`BookView.vue`)

A página do livro coordena os seguintes estados reativos no cliente:

| Variável reativa | Tipo | Valor Inicial | Finalidade no Mobile |
| :--- | :--- | :--- | :--- |
| `isInspectorExpandedMobile` | `Ref<boolean>` | `false` | Governa a exibição recolhível da barra inferior do inspetor no celular (`<= 767px`). Inicializa colapsada para poupar espaço vertical. |
| `isFocusMode` | `Ref<boolean>` | `false` | Quando ativado, recolhe tanto a faixa de capítulos quanto o inspetor analítico para máxima imersão. |
| `isCreatingChapterInline` | `Ref<boolean>` | `false` | Indica se o formulário inline de criação de novo capítulo está visível e focado. |
| `editingChapterId` | `Ref<number \| null>` | `null` | Armazena o identificador do capítulo atualmente em modo de edição de título. |
| `confirmTrashBookOpen` | `Ref<boolean>` | `false` | Controla a abertura do modal de confirmação para mover o livro para a lixeira. |
| `exportModalOpen` | `Ref<boolean>` | `false` | Controla a abertura do modal de exportação de notas do livro. |
| `isEditingBook` | `Ref<boolean>` | `false` | Controla a abertura do modal de edição de metadados e capa da obra. |

---

## 4. Matriz de Estados e Responsividade

| Estado do Dispositivo | Cabeçalho do Livro | Faixa de Capítulos | Inspetor Analítico |
| :--- | :--- | :--- | :--- |
| **Desktop (`>= 768px`)** | Capa média (160x240px), título expandido, autor, categorias e 4 botões de ação em pílula (`.header-actions`). | Título com contador, esteira rolável de pílulas horizontais (`.chapters-nav-strip`) e botão de novo capítulo. | Barra analítica horizontal completa aberta (`display: flex`). Botão de alternância oculto. |
| **Mobile (`<= 767px`)** | Linha 1: Miniatura da capa (48x72px), título (clamp 2 linhas) e autor.<br>Linha 2: Chips de categorias e menu agrupado (`DropdownMenu.vue` com as 4 ações). | Esteira de pílulas oculta (`display: none`). Exibição exclusiva do seletor único (`.chapters-mobile-select`) com botão de novo capítulo inline. | Barra do inspetor colapsada por padrão. Exibe botão acessível de alternância ("Ver detalhes do livro" / "Ocultar detalhes"). |
| **Modo Foco Ativo (qualquer viewport)** | Preserva cabeçalho da viewport correspondente. | Faixa de capítulos oculta (`v-if="!isFocusMode"`). | Faixa do inspetor oculta (`v-if="!isFocusMode"`). |
