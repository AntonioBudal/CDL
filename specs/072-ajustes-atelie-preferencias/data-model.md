# Data Model: Ajustes — Ateliê de Preferências e Leitura Viva

**Feature**: `072-ajustes-atelie-preferencias`
**Date**: 2026-10-11
**Status**: Concluído

## 1. Entidades e Tipos TypeScript

### 1.1 Temas Canônicos e Modelo de Pré-Visualização

```typescript
export type CanonicalThemeId =
  | 'papel-fosco'
  | 'noite-suave'
  | 'cinza-neutro'
  | 'grafite'
  | 'monocromatico'
  | 'pergaminho'
  | 'e-ink'
  | 'solario'
  | 'fiorde'
  | 'voltagem'

export interface ThemePaletteColors {
  page: string      // Fundo principal da página (--color-page)
  surface: string   // Superfície do card/painel (--color-surface)
  text: string      // Cor da tipografia principal (--color-text)
  accent: string    // Destaque cromático (--color-accent)
  border: string    // Borda e divisória (--color-border)
}

export interface ThemePreviewItem {
  id: CanonicalThemeId
  label: string
  scheme: 'light' | 'dark' | 'e-ink'
  colors: ThemePaletteColors
}
```

### 1.2 Navegação Vertical por Seções

```typescript
export type SettingsSectionId =
  | 'perfil'
  | 'aparencia'
  | 'leitura'
  | 'sistema'
  | 'conta'

export interface SettingsSectionItem {
  id: SettingsSectionId
  label: string
  subtitle: string
  icon: 'user' | 'palette' | 'book-open' | 'settings' | 'shield' // Nomes de Icon.vue
}
```

### 1.3 Estado do Simulador de Leitura e Amostra ao Vivo

```typescript
export interface ReadingWorkbenchState {
  isMobileDrawerOpen: boolean
  sampleTextKey: 'machado' | 'guimaraes'
  activeTabPreview: 'summary' | 'explanation' | 'concepts' | 'references'
}
```

### 1.4 Validação e Upload de Avatar

```typescript
export interface AvatarValidationRules {
  maxSizeBytes: number      // 2 * 1024 * 1024 (2MB)
  allowedMimeTypes: readonly string[] // ['image/png', 'image/jpeg', 'image/webp']
  targetDimensions: { width: 256; height: 256 }
}

export interface AvatarValidationResult {
  valid: boolean
  errorMessage?: string
}
```

## 2. Catálogo Oficial dos Temas para Pré-Visualização

Constante imutável no frontend contendo a paleta real dos 10 temas:

```typescript
export const CANONICAL_THEME_PREVIEWS: readonly ThemePreviewItem[] = [
  {
    id: 'papel-fosco',
    label: 'Papel Fosco',
    scheme: 'light',
    colors: {
      page: '#f5f5f5',
      surface: '#ffffff',
      text: '#333333',
      accent: '#475569',
      border: '#dcdcdc',
    },
  },
  {
    id: 'noite-suave',
    label: 'Noite Suave',
    scheme: 'dark',
    colors: {
      page: '#1e1e24',
      surface: '#26262e',
      text: '#d4d4d4',
      accent: '#64748b',
      border: '#383842',
    },
  },
  {
    id: 'cinza-neutro',
    label: 'Cinza Neutro',
    scheme: 'light',
    colors: {
      page: '#e8e8e8',
      surface: '#f0f0f0',
      text: '#2b2b2b',
      accent: '#52525b',
      border: '#cfcfcf',
    },
  },
  {
    id: 'grafite',
    label: 'Grafite',
    scheme: 'dark',
    colors: {
      page: '#222222',
      surface: '#2a2a2a',
      text: '#cccccc',
      accent: '#78716c',
      border: '#3d3d3d',
    },
  },
  {
    id: 'monocromatico',
    label: 'Monocromático',
    scheme: 'light',
    colors: {
      page: '#ffffff',
      surface: '#f8fafc',
      text: '#111111',
      accent: '#111111',
      border: '#d1d5db',
    },
  },
  {
    id: 'pergaminho',
    label: 'Sépia',
    scheme: 'light',
    colors: {
      page: '#E7CCA0',
      surface: '#F2DDB6',
      text: '#35200F',
      accent: '#873018',
      border: '#B58D58',
    },
  },
  {
    id: 'e-ink',
    label: 'E-Ink',
    scheme: 'e-ink',
    colors: {
      page: '#FFFFFF',
      surface: '#FFFFFF',
      text: '#000000',
      accent: '#000000',
      border: '#000000',
    },
  },
  {
    id: 'solario',
    label: 'Solarized',
    scheme: 'light',
    colors: {
      page: '#FDF6E3',
      surface: '#EEE8D5',
      text: '#3F5962',
      accent: '#00686D',
      border: '#B9B199',
    },
  },
  {
    id: 'fiorde',
    label: 'Nord',
    scheme: 'dark',
    colors: {
      page: '#2E3440',
      surface: '#3B4252',
      text: '#ECEFF4',
      accent: '#98D0E0',
      border: '#5A6A82',
    },
  },
  {
    id: 'voltagem',
    label: 'Cyber',
    scheme: 'dark',
    colors: {
      page: '#181820',
      surface: '#22222E',
      text: '#ECEAF4',
      accent: '#F6FF00',
      border: '#575067',
    },
  },
]
```

## 3. Integridade e Persistência de Dados

- **LocalStorage**: As preferências permanecem serializadas sob a chave canônica `caderno.aparencia.v2`.
- **Backend (SQLite)**: As configurações de perfil, senha e sessões usam a infraestrutura existente em `backend/app/routers/profile.py`, `backend/app/routers/auth.py` e `backend/app/routers/device.py` sem alteração de schema.
