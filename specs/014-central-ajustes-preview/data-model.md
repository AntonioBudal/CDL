# Phase 1: Data Model — Central de Ajustes com Preview ao Vivo

**Feature Branch**: `014-central-ajustes-preview`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Entidades do Cliente (Frontend)

### `AppearancePreferences`
Estrutura reativa de estado persistida no `localStorage` sob a chave `caderno.aparencia.v2`.

```typescript
export type AppearancePreferences = {
  // Seção Aparência
  theme: 'porcelana' | 'breu' | 'pergaminho' | 'e-ink' | 'vespera'
       | 'solario' | 'fiorde' | 'vinil' | 'sequoia' | 'voltagem'
  accent: 'theme' | 'blue' | 'green' | 'purple' | 'orange'
  container: 'contained' | 'fluid'
  superclass: 'none' | 'zero-g' | 'mecanica' | 'invisivel' | 'dimensional' | 'monolitica'
  'superclass-intensity': 'standard' | 'subtle' | 'high' | 'off'

  // Seção Leitura
  font: string // Chave canônica catalogada em font-catalog.json (ex: 'eb-garamond')
  'reader-size': '100' | '110' | '120' | '130' | '140' | '150' | '160' | '170' | '180' | '190' | '200'
  density: 'standard' | 'compact' | 'comfortable'
  align: 'left' | 'justify'
  highlight: 'background' | 'underline' | 'bold'
  library: 'grid' | 'list'
}
```

#### Regras de Validação e Normalização
1. Valores ausentes, não reconhecidos ou corrompidos revertem para a primeira opção válida (default de fábrica) definida em `appearance-bootstrap.js`.
2. Quando `theme === 'e-ink'`, `accent` e `superclass-intensity` são ignorados e forçados semanticamente para apresentação monocromática e neutra.
3. Migração automática e transparente de chaves da versão legada `caderno.aparencia.v1` para `caderno.aparencia.v2`.

---

### `SettingsTab`
Representação das abas de navegação estruturada da tela de Ajustes.

```typescript
export type SettingsTabId = 'aparencia' | 'leitura' | 'sistema'

export interface SettingsTab {
  id: SettingsTabId
  label: string
  description: string
  icon?: string
}
```

#### Definição das Abas Canônicas
| ID | Rótulo | Descrição |
|----|--------|-----------|
| `aparencia` | Aparência | Paletas de cores, Superclasses de interface, intensidade física e largura |
| `leitura` | Leitura | Tipografia literária, escala do texto, densidade e destaque de notas |
| `sistema` | Sistema | Escopo de persistência, diagnóstico de armazenamento, status e backup |

---

### `StorageDiagnostic`
Diagnóstico local de consumo e chaves do armazenamento do navegador.

```typescript
export interface StorageDiagnostic {
  isAvailable: boolean
  keyCount: number
  totalBytes: number
  formattedSize: string // ex: "14.2 KB" ou "N/D"
  cadernoKeysCount: number
}
```

---

### `HealthCheckResult`
Status de conectividade em tempo real com o backend local.

```typescript
export interface HealthCheckResult {
  status: 'loading' | 'ok' | 'error'
  version: string | null
  latencyMs: number | null
  message: string
}
```

---

### `ResetPreferencesModalState`
Estado de controle do diálogo modal acessível de confirmação para restauração dos padrões de fábrica.

```typescript
export interface ResetPreferencesModalState {
  isOpen: boolean
  isBusy: boolean
  feedback: string | null
}
```
