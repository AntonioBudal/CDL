# Data Model: F09.5 — Refatoração de Temas, Persistência e Correções Visuais

## 1. Entidades Principais

### `ThemeDefinition`
Representa um tema visual do sistema Leitorum no catálogo canônico de aparência.

| Campo | Tipo | Descrição | Exemplo |
|---|---|---|---|
| `id` | `string` | Identificador único do tema (usado no atributo `data-theme`) | `"papel-fosco"`, `"noite-suave"`, `"nord"` |
| `name` | `string` | Nome de exibição simplificado | `"Papel Fosco"`, `"Noite Suave"`, `"Nord"` |
| `scheme` | `'light' \| 'dark'` | Esquema base de iluminação | `'light'` ou `'dark'` |
| `is_default` | `boolean` | Indica se é o tema padrão inicial do sistema | `true` (apenas para `papel-fosco`) |
| `is_new` | `boolean` | Indica se é um dos novos temas minimalistas adicionados | `true` ou `false` |

### Catálogo Canônico de Temas (10 Temas)

```typescript
export interface ThemeOption {
  id: string
  name: string
  scheme: 'light' | 'dark'
}

export const CANONICAL_THEMES: readonly ThemeOption[] = Object.freeze([
  // 5 Novos Temas Minimalistas de Baixo Contraste
  { id: 'papel-fosco', name: 'Papel Fosco', scheme: 'light' },    // Padrão do Sistema
  { id: 'noite-suave', name: 'Noite Suave', scheme: 'dark' },
  { id: 'cinza-neutro', name: 'Cinza Neutro', scheme: 'light' },
  { id: 'grafite', name: 'Grafite', scheme: 'dark' },
  { id: 'monocromatico', name: 'Monocromático', scheme: 'light' },

  // 5 Temas Clássicos Preservados (Nomes Simplificados)
  { id: 'pergaminho', name: 'Sépia', scheme: 'light' },
  { id: 'e-ink', name: 'E-Ink', scheme: 'light' },
  { id: 'solario', name: 'Solarized', scheme: 'light' },
  { id: 'fiorde', name: 'Nord', scheme: 'dark' },
  { id: 'voltagem', name: 'Cyber', scheme: 'dark' },
])
```

---

## 2. Mapa de Migração de Temas Legados

Para garantir que leitores com temas anteriores não sofram telas quebradas ou redefinições indesejadas, a rotina de inicialização mapeia temas obsoletos:

| Tema Legado | Ação | Tema Substituto |
|---|---|---|
| `porcelana` | Migrar automaticamente | `papel-fosco` |
| `breu` | Migrar automaticamente | `noite-suave` |
| `vinil` | Migrar automaticamente | `grafite` |
| `sequoia` | Migrar automaticamente | `noite-suave` |
| `vespera` | Migrar automaticamente | `noite-suave` |

```javascript
const LEGACY_THEME_MIGRATIONS = {
  porcelana: 'papel-fosco',
  breu: 'noite-suave',
  vinil: 'grafite',
  sequoia: 'noite-suave',
  vespera: 'noite-suave',
  light: 'papel-fosco',
  dark: 'noite-suave',
  sepia: 'pergaminho',
}
```

---

## 3. Estado de Persistência no Cliente

### `localStorage` Keys
1. `caderno.aparencia.v2`: Objeto JSON com as configurações visuais do leitor:
   ```json
   {
     "theme": "papel-fosco",
     "accent": "theme",
     "density": "standard",
     "font": "garamond",
     "reader-size": "100",
     "superclass": "none",
     "superclass-intensity": "standard"
   }
   ```
2. `caderno_user_preferences`: Objeto JSON sincronizado com o backend, onde `theme_mode` passa a refletir diretamente o ID do tema ativo (ex.: `"papel-fosco"`).

---

## 4. Variáveis CSS por Tema (Tokens)

Cada tema define o conjunto completo de variáveis no `:root[data-theme="<id>"]`:
- `--color-page`: Fundo principal da página.
- `--color-surface`: Fundo de cartões, painéis e modais.
- `--color-surface-soft`: Fundo secundário suave (hover, itens selecionados).
- `--color-text`: Cor do texto primário (títulos, corpo principal).
- `--color-muted`: Cor do texto secundário e metadados.
- `--color-border`: Cor de divisores e bordas sutis.
- `--color-border-strong`: Cor de bordas com maior ênfase visual.
- `--color-accent`: Cor de destaque do tema.
- `--color-on-accent`: Cor do texto sobre a cor de destaque (garante contraste 4.5:1).
