# Data Model: Correções Visuais, de Cor e de Disposição

**Feature**: `075-correcoes-visuais-disposicao`  
**Date**: 2026-10-11  
**Status**: Concluído (Fase 1)

---

## 1. Entidades de Frontend e Estado

### 1.1 CompatibilityTokenMapping (Tokens de Compatibilidade)
Representa o mapeamento estático entre as variáveis CSS legadas e as variáveis canônicas oficiais do Caderno de Leitura.

- **legacy_name**: `string` — Nome da variável CSS legada (ex.: `--color-text-muted`, `--color-primary`, `--color-bg`, `--radius-md`).
- **canonical_target**: `string` — Nome da variável canônica correspondente (ex.: `--color-muted`, `--color-accent`, `--color-page`, `--radius-card`).
- **domain**: `'color' | 'radius' | 'shadow' | 'typography'` — Categoria do token no design system.
- **fallback_behavior**: `'alias-chain'` — O token legado resolve diretamente via `var(--canonical-target)`.

### 1.2 VisitorThemeSession (Sessão de Tema da Visita)
Representa o estado transitório de preferência visual para navegação anônima entre rotas públicas (`/`, `/sobre`, `/apoie`).

- **theme_id**: `CanonicalThemeId` — Identificador do tema ativo selecionado (um dos 10 temas canônicos).
- **storage_key**: `'caderno_visitor_theme'` — Chave de armazenamento persistida em `sessionStorage`.
- **active_mode**: `'anonymous-session'` — O tema perdura enquanto a aba do navegador estiver aberta, sem poluir preferências salvas de contas cadastradas.
- **precedence**: Inferior a `UserPreferences.theme_mode`. Se o usuário estiver autenticado, o tema do perfil local é imperativo.

### 1.3 StudyStatusPresentation (Apresentação Semântica do Status de Leitura)
Modelo que estrutura as propriedades visuais de cada estado na visualização e badges.

- **id**: `'rascunho' | 'em_estudo' | 'revisado' | 'concluido'`
- **label**: `'Rascunho' | 'Em Estudo' | 'Revisado' | 'Concluído'`
- **icon_name**: `'circle' | 'book-open' | 'feather' | 'check'`
- **background**: `'transparent'`
- **border_token**: `--color-muted` (rascunho), `--color-accent` (em estudo), `--color-warning-text` (revisado), `--color-success-text` (concluído)
- **text_token**: `--color-text` / `--color-muted`

### 1.4 StudyListColumnConfig (Configuração de Coluna da Lista de Estudos)
Estrutura de apresentação e acessibilidade para o cabeçalho da tabela de estudos.

- **key**: `'title' | 'status' | 'location' | 'date' | 'sections' | 'actions'`
- **label**: `string` — Texto legível da coluna.
- **sortable**: `boolean` — Se a coluna permite ordenação por clique.
- **align**: `'left' | 'center' | 'right'` — Alinhamento visual das células correspondentes.
- **aria_sort**: `'ascending' | 'descending' | 'none'` — Rótulo ARIA para tecnologias assistivas.
