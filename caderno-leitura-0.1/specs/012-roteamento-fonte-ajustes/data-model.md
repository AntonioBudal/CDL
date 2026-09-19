# Data Model: Correção de Roteamento, Fonte Global e Limpeza de Ajustes

**Feature**: `012-roteamento-fonte-ajustes`  
**Date**: 2026-09-19  
**Status**: Ready  

---

## 1. Entidades de Frontend e Estado de Aparência

### 1.1 `AppearancePreferences` (Estado Limpo no `localStorage`)

Representa o conjunto estrito de preferências persistido sob a chave `caderno.aparencia.v2`:

| Propriedade | Tipo | Valores Válidos | Padrão | Grupo Numerado |
|---|---|---|---|---|
| `theme` | `ThemeName` | `'porcelana'`, `'breu'`, `'pergaminho'`, `'e-ink'`, `'vespera'`, `'solario'`, `'fiorde'`, `'vinil'`, `'sequoia'`, `'voltagem'` | `'porcelana'` | Aparência básica |
| `accent` | `AccentName` | `'theme'`, `'blue'`, `'green'`, `'purple'`, `'orange'` | `'theme'` | 1. Cor de destaque |
| `density` | `DensityName` | `'standard'`, `'compact'`, `'comfortable'` | `'standard'` | 2. Densidade |
| `align` | `AlignName` | `'left'`, `'justify'` | `'left'` | 3. Leitura |
| `font` | `FontName` | 24 famílias tipográficas do catálogo local | `'inter'` | 3. Leitura |
| `reader-size` | `ReaderSize` | `'100'` a `'200'` (passo 10%) | `'100'` | 3. Leitura |
| `highlight` | `HighlightName` | `'background'`, `'underline'`, `'bold'` | `'background'` | 4. Marcação |
| `library` | `LibraryLayout` | `'grid'`, `'list'` | `'grid'` | 5. Acervo *(antigo 9)* |
| `container` | `ContainerWidth`| `'contained'`, `'fluid'` | `'contained'` | 6. Largura da interface *(antigo 10)* |
| `superclass` | `SuperclassName`| `'none'`, `'zero-g'`, `'mecanica'`, `'invisivel'`, `'dimensional'`, `'monolitica'` | `'none'` | 7. Superclasse de Interface *(antigo 11)* |
| `superclass-intensity` | `SuperclassIntensity` | `'standard'`, `'subtle'`, `'high'`, `'off'` | `'standard'` | 7. Superclasse de Interface *(antigo 11)* |

> [!IMPORTANT]
> **Campos Removidos Definitivamente:**
> - `motion` (absorvido por `superclass-intensity`)
> - `button-width` (absorvido pela geometria da superclasse)
> - `tabs` (absorvido pelo estilo da superclasse)
> 
> A função de normalização purga essas chaves caso existam no `localStorage`.

---

### 1.2 `AppearanceField` (Estrutura do Catálogo)

Define os metadados de cada campo exibido no painel de configurações:

```typescript
export interface AppearanceField {
  readonly key: keyof AppearancePreferences;
  readonly group: string;
  readonly label: string;
  readonly options: readonly (readonly [string, string])[];
}
```

**Mapeamento Sequencial dos Grupos:**
1. `"Aparência básica"` → `theme`
2. `"1. Cor de destaque"` → `accent`
3. `"2. Densidade"` → `density`
4. `"3. Leitura"` → `align`, `font`, `reader-size`
5. `"4. Marcação"` → `highlight`
6. `"5. Acervo"` → `library`
7. `"6. Largura da interface"` → `container`
8. `"7. Superclasse de Interface"` → `superclass`, `superclass-intensity`

---

### 1.3 `RouteViewRootEnclosure` (Conformidade de Roteamento)

Mapeamento do invólucro único de cada componente de rota:

| Componente | Arquivo | Invólucro Único Raiz | Classe Raiz |
|---|---|---|---|
| `BooksView` | `frontend/src/views/BooksView.vue` | `<div class="books-view">` | `.books-view` |
| `BookView` | `frontend/src/views/BookView.vue` | `<div class="book-view">` | `.book-view` |
| `StudyView` | `frontend/src/views/StudyView.vue` | `<div class="study-view">` | `.study-view` |
| `StudyEditView` | `frontend/src/views/StudyEditView.vue` | `<div class="study-edit-view">` | `.study-edit-view` |
| `ImportView` | `frontend/src/views/ImportView.vue` | `<div class="import-view">` | `.import-view` |
| `SettingsView` | `frontend/src/views/SettingsView.vue` | `<section class="settings-page">` | *(já é raiz única)* |
| `TrashView` | `frontend/src/views/TrashView.vue` | `<div class="trash-container wrap">` | *(já é raiz única)* |
| `ConnectionView` | `frontend/src/views/ConnectionView.vue` | `<section class="connection-page">` | *(já é raiz única)* |
