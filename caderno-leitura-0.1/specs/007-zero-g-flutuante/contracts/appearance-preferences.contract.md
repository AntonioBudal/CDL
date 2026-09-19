# Contract: Appearance Preferences & Superclasses

**Date**: 2026-09-19  
**Feature**: 007 — Zero-G: Superclasse Flutuante & Magnética  
**Status**: Ready  

---

## 1. Storage & Runtime Contract

### LocalStorage Schema
- **Key**: `caderno.aparencia.v2`
- **Format**: JSON serialized object conforming to `AppearancePreferences`.

```json
{
  "theme": "porcelana",
  "style": "rounded",
  "font": "inter",
  "accent": "theme",
  "density": "standard",
  "align": "left",
  "highlight": "background",
  "motion": "on",
  "surface": "raised",
  "button-style": "solid",
  "button-width": "auto",
  "tabs": "underline",
  "library": "grid",
  "container": "contained",
  "reader-size": "100",
  "superclass": "zero-g",
  "superclass-intensity": "standard"
}
```

### HTML Document Attributes
Ao chamar `cadernoAppearance.set(...)` ou no bootstrap inicial, o runtime aplica automaticamente os seguintes atributos no elemento `document.documentElement`:

| Atributo HTML | Valores Possíveis | Padrão | Descrição |
|---|---|---|---|
| `data-superclass` | `none`, `zero-g`, `mecanica`, `invisivel`, `dimensional`, `monolitica` | `none` | Arquétipo físico global ativo |
| `data-superclass-intensity` | `standard`, `subtle`, `high`, `off` | `standard` | Fator multiplicador de intensidade física |

---

## 2. API Contract: `window.cadernoAppearance`

### Types
```typescript
interface AppearancePreferences {
  // ... campos pré-existentes ...
  superclass: 'none' | 'zero-g' | 'mecanica' | 'invisivel' | 'dimensional' | 'monolitica';
  'superclass-intensity': 'standard' | 'subtle' | 'high' | 'off';
}

interface CadernoAppearance {
  readonly version: number;
  readonly fields: ReadonlyArray<AppearanceField>;
  get(): AppearancePreferences;
  set(value: Partial<AppearancePreferences>): boolean;
}
```

### Behaviors
1. `get()`: Retorna uma cópia do registro atual normalizado, garantindo que valores inválidos ou nulos recebam o fallback padrão (`none` e `standard`).
2. `set(patch)`: Mescla o objeto parcial, re-normaliza, atualiza os atributos `data-*` no DOM raiz e serializa no `localStorage`. Retorna `true` em caso de sucesso.
3. Se o armazenamento estiver bloqueado (ex.: modo anônimo restritivo), mantém o estado em memória para a sessão sem lançar exceções.
