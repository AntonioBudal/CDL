# Modelo de Dados e Tipos: Página Inicial sem Login (SEO) — Manifesto do Leitor Reflexivo

**Feature**: `074-manifesto-leitor-reflexivo`  
**Data**: 2026-10-11  
**Status**: Concluído (Phase 1)  

---

## 1. Visão Geral

A landing page do Leitorum opera como uma interface pública editorial de apresentação do manifesto cognitivo e demonstração in-place do método em camadas. Não há persistência no banco de dados SQLite (`caderno.db`) para esta feature; os dados são estruturados em esquemas de tipagem TypeScript estritos e imutáveis no frontend.

---

## 2. Entidades do Simulador em 4 Dimensões

### 2.1 Dimensão Metodológica
```typescript
export type SimulatorDimensionId = 'resumo' | 'explicacao' | 'conceitos' | 'referencias'

export interface SimulatorDimension {
  id: SimulatorDimensionId
  title: string
  subtitle: string
  labelShort: string
  iconName: IconName
  content: string
  keyInsights: readonly string[]
}
```

### 2.2 Marcação Literária Anotada
```typescript
export interface TextHighlight {
  id: string
  dimensionId: SimulatorDimensionId
  text: string
  marginalNote?: string
}

export interface LiteraryWorkSnippet {
  author: string
  title: string
  year: number
  sectionTitle: string
  paragraphs: readonly string[]
  highlights: readonly TextHighlight[]
  marginalia: {
    label: string
    text: string
  }
}
```

### 2.3 Estrutura Consolidada do Simulador
```typescript
export interface LandingSimulatorModel {
  work: LiteraryWorkSnippet
  dimensions: readonly SimulatorDimension[]
}
```

---

## 3. Entidades de Soberania e Tradição Histórica

### 3.1 Princípio de Soberania
```typescript
export interface SovereigntyPrinciple {
  id: string
  icon: IconName
  title: string
  description: string
  bulletPoints?: readonly string[]
}
```

### 3.2 Marco da Linhagem Histórica
```typescript
export interface HistoricalMilestone {
  era: string
  title: string
  subtitle: string
  description: string
  methodLink: string
}
```

---

## 4. Estado Efêmero de Tema e Acessibilidade

### 4.1 Estado da Sessão do Visitante (`useVisitorTheme`)
```typescript
export interface VisitorThemeState {
  currentTheme: Ref<CanonicalThemeId>
  originalTheme: string
  announcementText: Ref<string>
  setTheme: (themeId: CanonicalThemeId) => void
  resetTheme: () => void
}
```

---

## 5. Schema.org e Metadados Canônicos de SEO

```typescript
export interface WebApplicationLdJson {
  '@context': 'https://schema.org'
  '@type': 'WebApplication'
  name: 'Leitorum'
  url: string
  description: string
  applicationCategory: 'EducationalApplication'
  operatingSystem: 'All'
  offers: {
    '@type': 'Offer'
    price: '0'
    priceCurrency: 'BRL'
  }
  author: {
    '@type': 'Organization'
    name: 'Leitorum'
    url: string
  }
}
```

---

## 6. Regras de Integridade e Validação

1. **Imutabilidade**: Todas as constantes de texto de Machado de Assis, dimensões, princípios e marcos históricos são declaradas como `readonly` ou encapsuladas em `Object.freeze()`.
2. **Conformidade Constitucional Zero Emojis**: O campo `iconName` aceita exclusivamente chaves tipadas válidas do catálogo `IconName` (Lucide Icons), sendo terminantemente proibido qualquer caractere emoji nos dados.
3. **Idempotência de Tema**: A alteração do tema via `setTheme` atualiza unicamente a árvore do DOM em memória (`document.documentElement.dataset.theme`) sem invocar `localStorage.setItem('caderno_theme', ...)` para visitantes anônimos.
