# Data Model & State Architecture: F09.5.2 — Contraste Dinâmico, Estudos Compartilhados e Responsividade Mobile

**Branch**: `038-contraste-compartilhados-mobile` | **Date**: 2026-09-26

---

## 1. Entidades do Motor de Contraste e Tipografia Acessível

### 1.1 `ContrastCalculationOptions`
Estrutura de entrada para o utilitário central de contraste `getAccessibleTextColor`:

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|:------|:-----|:------------|:-------|:----------|
| `targetRatio` | `number` | Não | `4.5` (AA) | Razão de contraste mínima desejada (`4.5` para texto regular, `3.0` para UI/texto grande, `7.0` para AAA). |
| `lightColor` | `string` | Não | `'#ffffff'` | Cor candidata para primeiro plano claro. |
| `darkColor` | `string` | Não | `'#18181b'` | Cor candidata para primeiro plano escuro. |
| `parentBackground` | `string` | Não | `'#ffffff'` | Cor do container pai para cálculo de transparência alfa quando o fundo for semi-transparente. |
| `highContrast` | `boolean` | Não | `false` | Se verdadeiro, força limiar estrito WCAG AAA (7.0:1 / 4.5:1). |

### 1.2 `ContrastResult`
Resultado retornado pelo cálculo de contraste para um par de cores:

```typescript
export interface ContrastResult {
  textColor: string        // Cor escolhida com maior legibilidade ('#ffffff' ou '#18181b' ou custom)
  contrastRatio: number    // Razão numérica de contraste calculada (ex.: 7.24)
  meetsAA: boolean         // Indica se atinge o limiar mínimo WCAG AA
  meetsAAA: boolean        // Indica se atinge o limiar rigoroso WCAG AAA
  luminance: number        // Luminância relativa do fundo normalizado (0.0 a 1.0)
  isDarkBackground: boolean// Booleano indicando se o fundo é considerado escuro
}
```

### 1.3 `DynamicThemeVariables`
Mapa de variáveis CSS locais geradas pelo composable `useAccessibleContrast` para injeção via `:style`:

```typescript
export interface DynamicThemeVariables {
  '--dynamic-fg': string           // Cor de texto e ícones no estado normal
  '--dynamic-hover-bg': string     // Cor de fundo ao passar o mouse
  '--dynamic-hover-fg': string     // Cor de texto e ícones no estado hover
  '--dynamic-active-bg': string    // Cor de fundo ao pressionar/selecionar
  '--dynamic-active-fg': string    // Cor de texto e ícones no estado ativo
  '--dynamic-border': string       // Cor de borda contrastante
}
```

---

## 2. Entidades da Arquitetura de Navegação Mobile

### 2.1 `MobileNavItem`
Definição dos itens apresentados na barra de rodapé do celular:

```typescript
export interface MobileNavItem {
  id: string              // Identificador único (ex.: 'home', 'import', 'friends', 'settings', 'more')
  to?: string             // Rota de destino no Vue Router (ausente se for ação)
  label: string           // Rótulo exibido no botão
  icon: IconName          // Nome do ícone oficial da biblioteca Lucide
  action?: () => void     // Função acionada ao tocar (ex.: abrir gaveta 'Mais')
  badgeCount?: number     // Contador de notificações ou solicitações pendentes
  isActive: boolean       // Indica se a rota atual corresponde a este item
}
```

### 2.2 `MobileMoreMenuItem`
Definição dos itens exibidos dentro da gaveta inferior (*Bottom Sheet*):

```typescript
export interface MobileMoreMenuItem {
  id: string
  to?: string
  label: string
  icon: IconName
  badgeCount?: number
  action?: () => void
  requiresAdmin?: boolean // Exibe apenas se o usuário for administrador
  danger?: boolean        // Estilo de perigo (ex.: Sair da aplicação)
}
```

---

## 3. Entidades da Tela de Estudos Compartilhados

### 3.1 `SharedStudyCardItem`
Entidade visual representativa do card de estudo compartilhado em `SharedStudiesList.vue`:

```typescript
export interface SharedStudyCardItem {
  id: string
  title: string
  book_id: string
  book_title: string
  chapter_name: string | null
  owner_username: string
  owner_display_name: string
  owner_avatar_url: string | null
  visibility: 'public' | 'friends' | 'custom'
  updated_at: string
}
```

### 3.2 `SharedStudiesFilterState`
Estado reativo dos filtros e da paginação da tela:

```typescript
export interface SharedStudiesFilterState {
  searchQuery: string     // Termo de busca textual no título ou tema
  authorFilter: string    // Filtro por username do autor (@username)
  loading: boolean        // Indicador de carregamento em curso
  errorMessage: string | null // Mensagem de erro de API
  items: SharedStudyCardItem[] // Lista de estudos filtrados
  total: number           // Total de estudos encontrados
}
```
