# Data Model & Type Definitions: F09 - Sistema Visual Profissional

**Branch**: `017-sistema-visual-profissional`  
**Feature**: F09 — Sistema Visual Profissional  
**Data**: 2026-09-19  

Este documento descreve as estruturas de dados, interfaces TypeScript e dicionários de tipografia e iconografia introduzidos para suportar o Sistema Visual Profissional.

---

## 1. Integridade e Modelo de Dados do Backend (SQLite)

Em estrita consonância com a Constituição do Projeto e os princípios de estabilidade da versão 0.4:
- **Zero alterações no schema do banco de dados**: Nenhuma coluna ou tabela é renomeada ou modificada no SQLite.
- A coluna `studies.source_response` permanece idêntica em tipos, constraints e serialização JSON da API.
- Apenas a documentação e os textos de validação de `backend/app/schemas/imports.py` são atualizados para adotar linguagem editorial clássica.

---

## 2. Tipos de Apresentação e Componentes Frontend (`frontend/src/types.ts`)

### 2.1 Catálogo de Ícones Suportados (`IconName`)

```typescript
export type IconName =
  | 'book-open'
  | 'book'
  | 'layout-dashboard'
  | 'plus'
  | 'sliders'
  | 'trash'
  | 'trash-restore'
  | 'pencil'
  | 'x'
  | 'search'
  | 'alert-triangle'
  | 'check-circle'
  | 'check'
  | 'flame'
  | 'folder'
  | 'calendar'
  | 'download'
  | 'upload'
  | 'external-link'
  | 'chevron-right'
  | 'chevron-down'
  | 'grid'
  | 'list'
  | 'network'
  | 'canvas'
```

### 2.2 Propriedades do Componente Envelope de Ícone (`IconProps`)

```typescript
export interface IconProps {
  /** Nome do ícone registrado no catálogo Lucide do sistema */
  name: IconName
  /** Dimensão em pixels (largura e altura proporcionais). Padrão: 20 */
  size?: number | string
  /** Espessura do traço vetorial (stroke-width). Padrão: 2 */
  strokeWidth?: number | string
  /** Rótulo para leitores de tela quando o ícone for interativo ou informativo */
  ariaLabel?: string
  /** Classes CSS adicionais para estilização */
  class?: string
}
```

### 2.3 Propriedades do Estado Vazio (`EmptyStateProps`)

```typescript
export interface EmptyStateProps {
  /** Ícone ilustrativo vetorial exibido no topo */
  icon: IconName
  /** Título principal da mensagem (nível semântico h2 ou h3) */
  title: string
  /** Descrição orientadora ou explicativa para o leitor */
  description?: string
  /** Nível hierárquico do cabeçalho HTML. Padrão: 'h2' */
  headingLevel?: 'h2' | 'h3' | 'h4'
}
```

### 2.4 Propriedades do Esqueleto de Carregamento (`LoadingSkeletonProps`)

```typescript
export interface LoadingSkeletonProps {
  /** Formato geométrico do bloco: 'rect' (padrão), 'circle' (avatares/ícones), 'text' (linhas) */
  shape?: 'rect' | 'circle' | 'text'
  /** Largura customizada em CSS (ex.: '100%', '240px', '4rem') */
  width?: string
  /** Altura customizada em CSS (ex.: '1.25rem', '48px', '120px') */
  height?: string
  /** Número de linhas de texto simuladas quando shape === 'text'. Padrão: 1 */
  lines?: number
  /** Espaçamento vertical entre linhas múltiplas. Padrão: '0.5rem' */
  gap?: string
}
```

### 2.5 Propriedades de Badges e Indicadores de Status (`StatusBadgeProps`)

```typescript
export type BadgeVariant = 'neutral' | 'accent' | 'warning' | 'danger' | 'success'

export interface StatusBadgeProps {
  /** Variante cromática harmonizada com tokens de cor */
  variant?: BadgeVariant
  /** Ícone opcional exibido à esquerda do texto */
  icon?: IconName
  /** Texto visível do indicador */
  label: string
}
```

---

## 3. Dicionário de Vocabulário Editorial Canônico

Constante de referência para rotulagem de formulários e exibições na interface do usuário:

```typescript
export const EDITORIAL_TERMS = {
  SOURCE_STUDY_LABEL: 'Fichamento da Fonte',
  SOURCE_STUDY_HINT: 'Texto-base de apoio, extraído e preservado para consulta e aprofundamento analítico.',
  SOURCE_STUDY_PLACEHOLDER: 'Cole o texto-base ou fichamento analítico aqui…',
  IMPORT_TITLE: 'Importar Fichamento',
  EMPTY_TRASH_TITLE: 'Lixeira vazia',
  EMPTY_TRASH_DESC: 'Nenhum livro ou estudo excluído no momento.',
  EMPTY_LIBRARY_TITLE: 'Nenhum livro cadastrado',
  EMPTY_LIBRARY_DESC: 'Inicie adicionando seu primeiro livro ou importando anotações de leitura.',
} as const
```
