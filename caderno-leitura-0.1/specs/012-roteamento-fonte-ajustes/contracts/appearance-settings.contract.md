# Interface Contract: Catálogo e Bootstrap de Aparência Higienizado

**Feature**: `012-roteamento-fonte-ajustes`  
**Contract Type**: Frontend In-Memory State & Storage Interface  
**Status**: Final  

---

## 1. Contrato da Interface `AppearancePreferences`

```typescript
export interface AppearancePreferences {
  theme: ThemeName;
  accent: AccentName;
  density: DensityName;
  align: AlignName;
  font: FontName;
  'reader-size': ReaderSize;
  highlight: HighlightName;
  library: LibraryLayout;
  container: ContainerWidth;
  superclass: SuperclassName;
  'superclass-intensity': SuperclassIntensity;
}
```

*Removidos do contrato:*
```typescript
// PROIBIDOS / REMOVIDOS:
// motion: MotionPreference;
// 'button-width': ButtonWidth;
// tabs: TabsStyle;
```

---

## 2. Contrato de Normalização e Purga no `localStorage`

```typescript
function normalize(value: unknown): AppearancePreferences {
  // 1. Converte e valida valores aceitos para as 7 seções
  // 2. Remove as propriedades legadas 'motion', 'button-width', 'tabs'
  // 3. Regrava o objeto no localStorage sob a chave 'caderno.aparencia.v2'
  // 4. Remove atributos obsoletos do documentElement:
  //    - documentElement.removeAttribute('data-motion');
  //    - documentElement.removeAttribute('data-button-width');
  //    - documentElement.removeAttribute('data-tabs');
}
```

---

## 3. Contrato de Propagação Tipográfica Global

```css
/* Em tokens.css */
:root {
  --font-ui: var(--font-reading);
}

/* Em style.css */
:root,
body,
#app,
button,
input,
select,
textarea,
code,
pre {
  font-family: var(--font-reading);
}
```

---

## 4. Contrato de Roteamento Reativo e Enraizamento

```vue
<!-- Em App.vue -->
<main id="conteudo" class="workspace" tabindex="-1">
  <RouterView v-slot="{ Component }">
    <Transition name="page" mode="out-in">
      <component :is="Component" :key="$route.fullPath" />
    </Transition>
  </RouterView>
</main>
```

Todas as views devem conter um único elemento envoltório no `<template>` para preservar a estabilidade da transição.
