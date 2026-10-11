# Data Model & Presentation Schemas: Tela Placeholder do Document Intelligence

**Feature**: F0.3.5 — Tela Placeholder do Document Intelligence  
**Branch**: `069-document-intelligence-placeholder`  
**Date**: 2026-10-11  

---

## 1. Visão Geral

Esta feature opera estritamente no frontend como uma tela informativa estática. Não existem tabelas de banco de dados, modelos SQLAlchemy, migrações Alembic ou endpoints de persistência no backend.

Os modelos de dados descritos abaixo são contratos de apresentação em TypeScript utilizados exclusivamente para renderização declarativa na interface.

---

## 2. Modelos de Apresentação (Frontend TypeScript)

### `MaturityStage`

Representa uma das 4 etapas de pesquisa técnica do Document Intelligence exibidas na matriz informativa.

```typescript
export type StageStatus = 'validating' | 'researching' | 'not_started'

export interface MaturityStage {
  id: string
  title: string
  status: StageStatus
  statusLabel: string
  description: string
  technicalNote?: string
}
```

### Constante Canônica: `DOCUMENT_INTELLIGENCE_STAGES`

Os 4 estágios fixos inegociáveis definidos pela especificação:

```typescript
export const DOCUMENT_INTELLIGENCE_STAGES: readonly MaturityStage[] = [
  {
    id: 'locate-lines-blocks',
    title: 'Localizar linhas e blocos na página',
    status: 'validating',
    statusLabel: 'Em validação',
    description: 'Segmentação visual para detecção de caixas de texto, títulos e notas laterais.',
    technicalNote: 'Funciona em páginas sintéticas; testes com fotografias reais em andamento.',
  },
  {
    id: 'reading-order',
    title: 'Ordem de leitura',
    status: 'validating',
    statusLabel: 'Em validação',
    description: 'Algoritmo de ordenação topológica para fluxo contínuo entre colunas e margens.',
    technicalNote: 'Validação preliminar de grafo de leitura em colunas duplas e notas soltas.',
  },
  {
    id: 'portuguese-htr',
    title: 'Transcrição do texto manuscrito em português',
    status: 'researching',
    statusLabel: 'Em pesquisa',
    description: 'Reconhecimento de texto caligráfico manuscrito (Handwritten Text Recognition).',
    technicalNote: 'Ainda não há modelo pré-treinado capaz de ler caligrafia corrente em português.',
  },
  {
    id: 'content-classification',
    title: 'Classificação do conteúdo e diagramas',
    status: 'not_started',
    statusLabel: 'Não iniciado',
    description: 'Distinção automática entre parágrafos conceituais, citações e croquis visuais.',
    technicalNote: 'Etapa futura dependente da estabilização da segmentação geométrica.',
  },
] as const
```

---

## 3. Estrutura de Navegação e Atalhos

### `ExitShortcut`

Representa as saídas úteis oferecidas ao leitor para não bloquear seu fluxo de trabalho:

```typescript
export interface ExitShortcut {
  title: string
  description: string
  routePath: string
  actionLabel: string
}

export const DIGITIZE_EXIT_SHORTCUTS: readonly ExitShortcut[] = [
  {
    title: 'Importar fichamento digitado',
    description: 'Cole trechos copiados do seu leitor de e-books ou digite anotações no Ateliê de Fichamento.',
    routePath: '/importar',
    actionLabel: 'Abrir Ateliê de Fichamento',
  },
  {
    title: 'Anotar na Caixa de Entrada',
    description: 'Despeje ideias rápidas, citações soltas ou pensamentos sem necessidade de classificação prévia.',
    routePath: '/inbox',
    actionLabel: 'Ir para Caixa de Entrada',
  },
] as const
```
