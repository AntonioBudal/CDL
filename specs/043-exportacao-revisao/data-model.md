# Data Model: F0.6.4 — Exportação com Destaques e Caderno de Revisão

**Feature**: F0.6.4 — Exportação com Destaques e Caderno de Revisão  
**Branch**: `043-exportacao-revisao`  
**Date**: 2026-09-27  

Este documento descreve os modelos de dados, schemas Pydantic e estruturas em memória que sustentam a exportação estendida e a geração do Caderno de Revisão (Digest).

---

## 1. Schemas de Entrada e Configuração (Backend & API)

### 1.1 `ExportFormat` (Enum)
Formato de saída gerado pelo serviço:
- `MARKDOWN = "markdown"` (Arquivo `.md` com Frontmatter YAML e markdown formatado).
- `TEXT = "text"` (Arquivo `.txt` com divisores e caixas tipográficas ASCII).

### 1.2 `ExportType` (Enum)
Modalidade da exportação:
- `FULL = "full"`: Documento integral contendo o texto das seções e fichamentos do livro ou estudo, com destaques embutidos.
- `DIGEST = "digest"`: Caderno de Revisão compilando exclusivamente perguntas ativas, termos ocluídos, notas e citações.

### 1.3 `ExportOptions` (Pydantic Model)
Localização: `backend/app/schemas/export.py`

| Campo | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `format` | `ExportFormat` | `ExportFormat.MARKDOWN` | Formato do documento (`markdown` ou `text`). |
| `include_notes` | `bool` | `True` | Inclui reflexões pessoais manuscritas do estudo. |
| `include_sections` | `bool` | `True` | Inclui seções formais (resumo, explicação, conceitos, referências). |
| `include_source` | `bool` | `False` | Inclui resposta textual original da importação (`source_response`). |
| `include_metadata` | `bool` | `True` | Inclui metadados no topo (YAML Frontmatter ou cabeçalho ASCII). |
| `include_highlights` | `bool` | `True` | **(Novo)** Injeta destaques e anotações visuais no fluxo textual. |
| `export_type` | `ExportType` | `ExportType.FULL` | **(Novo)** Modalidade de exportação (`full` ou `digest`). |
| `exercise_mode` | `bool` | `False` | **(Novo)** No modo digest, oculta respostas com linhas de preenchimento e gera gabarito final. |

---

## 2. Estrutura de Compilação em Memória do Caderno de Revisão

Durante a geração do Caderno de Revisão (tanto em nível de estudo quanto de livro completo), o serviço agrega as marcações da tabela `study_highlights` nas seguintes estruturas tipadas intermediárias:

### 2.1 `ReviewQuestionItem`
Representa uma pergunta de retenção ativa cadastrada sobre um trecho do estudo.

- `study_id: int`: Identificador do estudo.
- `study_title: str`: Título do estudo.
- `chapter_name: str`: Nome do capítulo pai.
- `section: str`: Seção de origem (`summary`, `explanation`, etc.).
- `question: str`: Texto da pergunta cadastrada (armazenado em `StudyHighlight.note`).
- `answer: str`: Texto alvo correspondente à resposta (armazenado em `StudyHighlight.selected_text`).
- `location: str | None`: Localização da citação na obra original.

### 2.2 `ReviewOcclusionItem`
Representa um termo ou conceito ocluído (Cloze Deletion) para memorização.

- `study_id: int`: Identificador do estudo.
- `study_title: str`: Título do estudo.
- `chapter_name: str`: Nome do capítulo pai.
- `prefix: str`: Trecho textual anterior imediato (contexto).
- `occluded_text: str`: Termo ocluído ocultado no exercício (`selected_text`).
- `suffix: str`: Trecho textual posterior imediato (contexto).
- `note: str | None`: Anotação mnemônica ou dica opcional (`StudyHighlight.note`).

### 2.3 `ReviewNoteItem`
Representa anotações marginais, grifos de ênfase e citações destacadas.

- `study_id: int`: Identificador do estudo.
- `study_title: str`: Título do estudo.
- `chapter_name: str`: Nome do capítulo pai.
- `kind: str`: Tipo do grifo (`highlight`, `note`, `quote`).
- `selected_text: str`: Trecho grifado.
- `note: str`: Comentário ou reflexão associada.
- `color: str`: Cor atribuída ao realce (`yellow`, `green`, `blue`, etc.).

### 2.4 `ReviewDigestData`
Contêiner consolidado contendo os dados prontos para formatação:

- `title: str`: Título principal do caderno (Livro ou Estudo).
- `subtitle: str | None`: Subtítulo da obra.
- `author: str | None`: Autor da obra.
- `scope: str`: `'book'` ou `'study'`.
- `exercise_mode: bool`: Indica se deve suprimir respostas e adicionar apêndice de gabarito.
- `questions: list[ReviewQuestionItem]`: Lista ordenada de perguntas ativas.
- `occlusions: list[ReviewOcclusionItem]`: Lista ordenada de oclusões.
- `notes: list[ReviewNoteItem]`: Lista ordenada de notas marginais e citações.
- `total_items: int`: Soma total de elementos interativos compilados.

---

## 3. Schemas do Frontend (TypeScript)

Localização: `frontend/src/types.ts`

```typescript
export type ExportFormat = 'markdown' | 'text'
export type ExportType = 'full' | 'digest'

export interface ExportConfig {
  format: ExportFormat
  exportType: ExportType
  includeNotes: boolean
  includeSections: boolean
  includeSource: boolean
  includeMetadata: boolean
  includeHighlights: boolean
  exerciseMode: boolean
}
```

---

## 4. Regras de Validação e Integridade

1. **Imutabilidade do Banco**: Todas as transformações são realizadas estritamente em memória durante a montagem do arquivo. Nenhuma coluna de banco ou linha relacional sofre `UPDATE`, `INSERT` ou `DELETE`.
2. **Consistência de Respostas Suprimidas**: No modo exercício (`exercise_mode = True`), as linhas de preenchimento `_______` devem ter comprimento padronizado (mínimo de 30 caracteres ou proporcional ao termo) e o gabarito final deve referenciar com exatidão o número do exercício correspondente.
3. **Mapeamento de Notas de Rodapé**: Na exportação integral com destaques, os identificadores de rodapé `[^1]`, `[^2]`, ... devem ser reiniciados por seção ou sequenciais por estudo, garantindo que não haja referências quebradas.
4. **Isolamento de Acesso**: A geração só processa estudos e livros aos quais o usuário autenticado tenha permissão de leitura explícita (`can_read_study` ou propriedade do livro).
