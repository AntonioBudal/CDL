# Data Model & State Transitions: F0.8.02 — Destaques: Códice e Margens Vivas

**Feature**: `067-destaques-codice-margens` | **Date**: 2026-10-11 | **Status**: Complete

---

## 1. Entidades de Domínio e Contratos de Dados

A Feature 02 preserva integralmente as estruturas de persistência do SQLite e os schemas da API, atuando sobre a modelagem de apresentação e enriquecimento semântico no cliente.

### 1.1 Entidade: `StudyHighlight` (Modelo Backend e Persistência)
Representa a marcação ou citação persistida no banco de dados SQLite.

| Campo | Tipo | Nulo | Descrição |
|---|---|---|---|
| `id` | `INTEGER` | Não | Chave primária única do destaque. |
| `study_id` | `INTEGER` | Não | Chave estrangeira para o estudo (`studies.id`). |
| `selected_text` | `TEXT` | Não | Texto exato citado/grifado da obra original. |
| `note` | `TEXT` | Sim | Anotação pessoal ou reflexão elaborada pelo leitor. |
| `color` | `VARCHAR(20)` | Não | Código de cor do grifo (`yellow`, `green`, `blue`, `pink`, `purple`). |
| `kind` | `VARCHAR(20)` | Não | Tipo de marcação (`highlight`, `note`, `quote`, `question`, `hidden`). |
| `start_offset` | `INTEGER` | Sim | Posição inicial no texto da fonte. |
| `end_offset` | `INTEGER` | Sim | Posição final no texto da fonte. |
| `created_at` | `DATETIME` | Não | Data/hora de criação do grifo. |
| `updated_at` | `DATETIME` | Não | Data/hora da última alteração. |

---

### 1.2 Entidade de Apresentação: `HighlightLibraryItem` (Frontend)
Estrutura enriquecida retornada pelo endpoint `/api/highlights/library` para consumo na biblioteca.

```typescript
export interface HighlightLibraryItem {
  id: number
  study_id: number
  study_title: string
  book_id: number
  book_title: string
  book_author?: string | null
  chapter_id?: number | null
  chapter_title?: string | null
  chapter_order?: number | null
  selected_text: string
  note?: string | null
  color: HighlightColor // 'yellow' | 'green' | 'blue' | 'pink' | 'purple'
  kind: HighlightKind   // 'highlight' | 'note' | 'quote' | 'question' | 'hidden'
  created_at: string
  updated_at: string
}
```

---

### 1.3 Mapeamento Semântico: `HighlightSemanticCategory`
Mapeamento intelectual que confere significado às cores no catálogo de estudo.

```typescript
export interface HighlightSemanticCategory {
  key: HighlightColor
  label: string         // Nome da cor em português (ex: "Amarelo")
  semanticName: string  // Categoria intelectual (ex: "Ideia Central")
  description: string   // Significado de estudo
}

export const HIGHLIGHT_SEMANTIC_CATEGORIES: Record<HighlightColor, HighlightSemanticCategory> = {
  yellow: {
    key: 'yellow',
    label: 'Amarelo',
    semanticName: 'Ideia Central',
    description: 'Destaque fundamental da tese ou argumento principal da obra',
  },
  green: {
    key: 'green',
    label: 'Verde',
    semanticName: 'Citação-chave',
    description: 'Passagem memorável, aforismo ou referência direta para citação',
  },
  blue: {
    key: 'blue',
    label: 'Azul',
    semanticName: 'Dúvida',
    description: 'Ponto obscuro, conceito desafiador ou questão para aprofundamento',
  },
  pink: {
    key: 'pink',
    label: 'Rosa',
    semanticName: 'Refutação',
    description: 'Contraposição, argumento divergente ou crítica ao texto',
  },
  purple: {
    key: 'purple',
    label: 'Roxo',
    semanticName: 'Síntese',
    description: 'Conclusão conceitual, fechamento de raciocínio ou resumo',
  },
}
```

---

### 1.4 Modelo de Citação Formatada: `CitationExport`
Formato estruturado para cópia em múltiplos padrões textuais.

```typescript
export type CitationFormat = 'abnt' | 'markdown' | 'plain'

export interface CitationPayload {
  format: CitationFormat
  text: string
  author?: string
  bookTitle: string
  chapterTitle?: string
  pageOrLocation?: string
}
```

---

## 2. Máquina de Estados e Transições no Cliente

### 2.1 Ciclo de Estados da Ficha Literária (`HighlightCard.vue`)

```
                  ┌─────────────────┐
                  │   Leitura Base   │ ◄──────────────────┐
                  └────────┬────────┘                     │
                           │                              │
         ┌─────────────────┼──────────────────┐           │
         │                 │                  │           │
         ▼                 ▼                  ▼           │
 ┌───────────────┐ ┌───────────────┐  ┌───────────────┐   │
 │   Expandido   │ │ Edição de     │  │ Confirmação   │   │
 │   (Contexto)  │ │ Nota Pessoal  │  │ de Exclusão   │   │
 └───────┬───────┘ └───────┬───────┘  └───────┬───────┘   │
         │                 │                  │           │
    "Ver menos"       "Salvar"          "Cancelar"        │
         │                 │                  │           │
         └─────────────────┴──────────────────┴───────────┘
```

1. **Estado `Leitura Base` (Padrão):** Citação tipográfica serifada, aspas editoriais, nota pessoal (se existente), rodapé com dados bibliográficos e botão discreto de cópia.
2. **Estado `Expandido`:** Se `selected_text.length > 260`, alterna suavemente para visualização integral do trecho sem quebras de layout.
3. **Estado `Edição de Nota Pessoal`:** Abre textarea in-card com preenchimento da nota atual, botões "Salvar" e "Cancelar". Ao salvar, emite evento assíncrono para persistência no backend.
4. **Estado `Confirmação de Exclusão`:** Exibe aviso de confirmação na própria ficha ("Excluir este destaque?") prevenindo exclusões acidentais. Ao confirmar, executa exclusão atômica na API.

---

### 2.2 Ciclo de Feedback de Cópia de Citação

```
[Clique em Copiar]
       │
       ▼
[Clipboard API writeText] ──(Falha)──► [Fallback de Seleção Manual]
       │ (Sucesso)
       ▼
[Microfeedback no Botão (Check animado: 150ms)]
       │
       ▼
[Toast Flutuante ("Copiado para a área de transferência")]
       │
       ▼
[Dissolução Automática após 1500ms]
       │
       ▼
[Retorno ao Ícone de Cópia]
```

---

### 2.3 Estados de Consulta da Biblioteca (`HighlightsLibraryView.vue`)

1. **`Carregando` (`loading === true`):** Exibe 4 cartões de esqueleto (*loading skeletons*) com animação de pulso sutil nos tokens do tema.
2. **`Erro de Rede` (`errorMessage !== ''`):** Exibe cartão acolhedor sem bordas vermelhas, com mensagem clara e botão acessível "Tentar novamente" (`fetchHighlights`).
3. **`Vazio com Filtros` (`items.length === 0 && hasFiltersActive`):** Mensagem informando ausência de resultados para a combinação de filtros, com botão para redefinir filtros.
4. **`Vazio Sem Destaques` (`items.length === 0 && !hasFiltersActive`):** Mensagem convidativa orientando como grifar textos durante a leitura ativa.
5. **`Sucesso com Resultados` (`items.length > 0`):** Renderização das fichas literárias ordenadas por data ou agrupadas sob cabeçalhos por livro.
