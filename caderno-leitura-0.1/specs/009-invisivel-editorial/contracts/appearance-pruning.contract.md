# Contract: Appearance Settings Pruning & Migration

**Date**: 2026-09-19  
**Feature**: 009 — Invisível: Superclasse Silenciosa & Editorial e Limpeza de Ajustes  
**Status**: Ready  

---

## 1. Campos Removidos do Frontend

Os seguintes 3 campos são removidos formalmente da interface de Ajustes e do catálogo de campos:

| Campo Removido | Grupo Anterior | Razão da Remoção | Absorvido Por |
|---|---|---|---|
| `style` | Aparência básica ("Formato das caixas") | Redundante com o controle físico de bordas das Superclasses | Variável `--sc-border-radius` de cada Superclasse |
| `surface` | 6. Contraste da interface ("Cartões") | Redundante com a elevação, profundidade e sombras dinâmicas | Variáveis `--sc-shadow-idle` e `--sc-shadow-hover` de cada Superclasse |
| `button-style` | 7. Botões ("Preenchimento") | Redundante com a física tátil, elevação e estilo de botões | Estilização nominal de botões de cada Superclasse |

---

## 2. Contrato de Migração e Normalização (`normalize`)

Em `frontend/src/appearance-bootstrap.js`:
- Ao carregar dados salvos no `localStorage` sob a chave `caderno.aparencia.v2` ou `caderno.aparencia.v1`, as propriedades `style`, `surface` e `button-style` são simplesmente ignoradas pelo `normalize`.
- Nenhuma exceção é lançada.
- O objeto retornado por `window.cadernoAppearance.get()` conterá apenas as chaves válidas remanescentes.
- Nenhuma redefinição indesejada das outras preferências (como `theme` e `font`) ocorrerá.

---

## 3. Contrato de Tipagem (`appearance.d.ts`)

A interface `AppearancePreferences` é estritamente definida sem as propriedades removidas:
```typescript
export type AppearancePreferences = {
  theme: 'porcelana' | 'breu' | 'pergaminho' | 'e-ink' | 'vespera'
       | 'solario' | 'fiorde' | 'vinil' | 'sequoia' | 'voltagem'
  accent: 'theme' | 'blue' | 'green' | 'purple' | 'orange'
  density: 'standard' | 'compact' | 'comfortable'
  align: 'left' | 'justify'
  font: string
  highlight: 'background' | 'underline' | 'bold'
  'reader-size': string
  motion: 'off' | 'on'
  'button-width': 'auto' | 'block'
  tabs: 'underline' | 'segmented' | 'folders'
  library: 'grid' | 'list'
  container: 'contained' | 'fluid'
  superclass: 'none' | 'zero-g' | 'mecanica' | 'invisivel' | 'dimensional' | 'monolitica'
  'superclass-intensity': 'standard' | 'subtle' | 'high' | 'off'
}
```

---

## 4. Contrato da Interface de Ajustes (`AppearanceControls.vue`)

- Nenhum `<fieldset>` ou `<select>` para `style`, `surface` ou `button-style` será renderizado.
- O grupo órfão "6. Contraste da interface" deixa de existir na tela.
- O grupo "7. Botões" passa a conter apenas "Largura" (`button-width`), renomeado para maior clareza.
