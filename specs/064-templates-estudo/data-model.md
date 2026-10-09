# Data Model: F0.7.15 — Templates Estruturados de Estudo

## 1. Modificações na Entidade `Study`

### Tabela: `studies` (SQLite)

| Coluna | Tipo | Nullable | Default | Descrição |
|---|---|---|---|---|
| `template_id` | `VARCHAR(30)` | `NOT NULL` | `'classico'` | Identificador canônico do template estrutural de estudo. |

### Índices
- `ix_studies_template_id` em `(template_id)` para consultas filtradas por modelo mental caso necessário no futuro.

### Mapeamento SQLAlchemy 2.0 (`backend/app/models/study.py`)
```python
template_id: Mapped[str] = mapped_column(
    String(30),
    default="classico",
    server_default=text("'classico'"),
    nullable=False,
)
```

---

## 2. Catálogo Estático no Frontend (`frontend/src/constants/studyTemplates.ts`)

```typescript
export type StudyTemplateId =
  | 'classico'
  | 'conceito'
  | 'argumento'
  | 'comparativo'
  | 'resenha'

export interface StudyTemplateSectionGuide {
  key: 'summary' | 'explanation' | 'concepts' | 'references'
  label: string
  hint: string
  skeleton: string
}

export interface StudyTemplateDefinition {
  id: StudyTemplateId
  name: string
  badgeLabel: string
  shortDescription: string
  detailedPurpose: string
  sections: Record<'summary' | 'explanation' | 'concepts' | 'references', StudyTemplateSectionGuide>
}
```

### Definição dos 5 Templates Canônicos

1. **`classico` — Fichamento Clássico**
   - **Propósito**: Síntese geral, desenvolvimento argumentativo e extração de citações.
   - `summary`: Síntese analítica e tese central do capítulo ou trecho.
   - `explanation`: Articulação e detalhamento dos passos do autor.
   - `concepts`: Termos técnicos, definições e vocabulário essencial.
   - `references`: Citações literais, notas de apoio e diálogos bibliográficos.

2. **`conceito` — Estudo de Conceito**
   - **Propósito**: Dissecação semântica, histórica e prática de uma ideia ou termo filosófico/técnico.
   - `summary`: **Definição Essencial** (`### Definição Essencial\n- O que é:\n- O que não é:`)
   - `explanation`: **Etimologia e Contexto Histórico** (`### Origem e Contexto\n- Raiz etimológica:\n- Contexto de surgimento:`)
   - `concepts`: **Aplicações e Manifestações** (`### Aplicações Práticas\n- Exemplos concretos:\n- Casos de uso:`)
   - `references`: **Contrapontos e Limitações** (`### Limites e Objeções\n- Críticas teóricas:\n- Fronteiras de validade:`)

3. **`argumento` — Reconstrução de Argumento**
   - **Propósito**: Análise lógica da validade, premissas e conclusões de um raciocínio.
   - `summary`: **Tese Central** (`### Tese\n- Proposição fundamental defendida:`)
   - `explanation`: **Premissas e Justificativas** (`### Premissas\n1. Premissa 1:\n2. Premissa 2:\n- Relação de sustentação:`)
   - `concepts`: **Objeções Antecipadas** (`### Objeções e Contra-exemplos\n- Fragilidades apontadas:\n- Resposta do autor:`)
   - `references`: **Conclusão Dialética** (`### Desfecho Argumentativo\n- Solidez da inferência:\n- Implicações conceituais:`)

4. **`comparativo` — Análise Comparativa**
   - **Propósito**: Confronto analítico entre duas obras, perspectivas ou pensadores.
   - `summary`: **Objeto de Comparação** (`### Confronto Analítico\n- Obra/Autor A:\n- Obra/Autor B:\n- Ponto comum de partida:`)
   - `explanation`: **Convergências e Afinidades** (`### Pontos de Convergência\n- Concordâncias fundamentais:`)
   - `concepts`: **Divergências e Disputas** (`### Pontos de Divergência\n- Linhas de atrito e distinções:`)
   - `references`: **Síntese Avaliativa** (`### Veredito do Leitor\n- Conclusão comparativa:\n- Qual tese se sustenta melhor:`)

5. **`resenha` — Resenha Crítica**
   - **Propósito**: Julgamento fundamentado do valor, alcance e limitações de um texto.
   - `summary`: **Contexto e Autor** (`### Apresentação da Obra\n- Autor e época:\n- Propósito da publicação:`)
   - `explanation`: **Avaliação da Tese** (`### Julgamento do Argumento\n- Relevância e mérito das propostas:`)
   - `concepts`: **Pontos Cegos e Fragilidades** (`### Limitações\n- O que foi desconsiderado:\n- Vieses evidentes:`)
   - `references`: **Posicionamento Crítico** (`### Posicionamento Pessoal\n- Diálogo com minha experiência:\n- Recomendação e legado:`)

---

## 3. Schemas Pydantic (`backend/app/schemas/study.py`)

- `StudyCreate`: inclui `template_id: str = "classico"`
- `StudyPatch`: inclui `template_id: str | None = None`
- `StudySummary`: inclui `template_id: str = "classico"`
- `StudyRead`: herda de `StudySummary` (inclui `template_id: str = "classico"`)

---

## 4. Validação e Fallback
- Caso a API receba um `template_id` não previsto no catálogo canônico (ex.: valor inválido ou corrompido), o backend normaliza para `'classico'`.
- Estudos antigos que possuam valor `null` no banco (se criados antes da migração em instâncias descartáveis) retornam `'classico'` no Pydantic.
