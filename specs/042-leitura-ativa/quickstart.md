# Quickstart & Validation Guide: F0.6.3 — Leitura Ativa

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Date**: 2026-09-27

Este guia descreve os cenários de teste automatizados e manuais para validar a entrega da feature **F0.6.3 — Leitura Ativa**.

---

## 1. Pré-Requisitos e Ambiente

1. Aplicação em execução ou ambiente de teste:
   - Node.js $\ge 24$ para frontend (`caderno-leitura-0.1/frontend`).
   - Python 3.13 no Windows (`caderno-leitura-0.1/backend`).
2. Estudo com trechos ocluídos (`hidden`) e perguntas ativas (`question`) criados previamente através das ferramentas de seleção da F0.6.2.

---

## 2. Cenários de Validação Automatizada

### 2.1. Testes Unitários de Sessão e Utilitários de DOM
Executar no terminal dentro de `caderno-leitura-0.1/frontend`:

```bash
npm test
```

**Verificações Cobertas**:
- Cálculo e rastreamento reativo de progresso em `useActiveReadingSession.ts`.
- Métodos de manipulação em lote `setHighlightsRevealedState` (ocultar todos e revelar todos).
- Função de rolagem e foco sequencial `scrollAndFocusHighlight`.
- Conformidade editorial: zero emojis informais em `src/` conforme `visual_system.test.mjs`.

### 2.2. Compilação e Tipagem Estrita
Executar validação do TypeScript e Vite:

```bash
npm run build
```

**Critério de Aceite**: Saída com código 0 e zero erros de tipo (`vue-tsc -b`).

---

## 3. Roteiro de Validação Manual Ponta a Ponta

### Cenário 1: Ativação da Leitura Ativa e Oclusão Inicial em Lote
1. Abra um estudo contendo passagens marcadas como "Ocultar" e "Pergunta".
2. Na barra de ferramentas do leitor, clique no botão **"Leitura Ativa"**.
3. **Resultado Esperado**:
   - A barra `ActiveReadingBar` surge no topo da leitura exibindo o contador: `0 de N revisados (0%)`.
   - Todos os trechos interativos da seção ativa assumem o estado mascarado.
   - O Markdown e o texto original permanecem intactos.

---

### Cenário 2: Revelação Pontual e Atualização de Progresso
1. Com o modo ativo, localize um trecho ocluído no parágrafo e clique em `[Revelar]`.
2. **Resultado Esperado**:
   - Apenas aquele trecho se torna legível com fundo suave. O botão muda para `[Ocultar]`.
   - O contador na barra atualiza imediatamente para `1 de N revisados`.
3. Clique em `[Ocultar]`.
4. **Resultado Esperado**:
   - O trecho volta a ficar mascarado e o contador diminui de volta para `0 de N revisados`.

---

### Cenário 3: Ações em Massa (Revelar Todos e Ocultar Todos)
1. Na barra de Leitura Ativa, clique no botão **"Revelar todos"**.
2. **Resultado Esperado**:
   - Todas as oclusões e perguntas da aba tornam-se visíveis instantaneamente.
   - O contador exibe `N de N revisados (100%)`.
3. Clique em **"Ocultar todos"**.
4. **Resultado Esperado**:
   - Todos os trechos voltam a ficar mascarados e o contador zera.

---

### Cenário 4: Navegação Sequencial por Teclado e Foco
1. Pressione a tecla `J` ou o botão **"Próximo"** na barra.
2. **Resultado Esperado**:
   - O leitor rola suavemente até o próximo trecho interativo, aplicando anel de foco visível.
3. Pressione a barra de espaço ou Enter sobre o botão do trecho para revelá-lo.
4. Pressione `Escape`.
5. **Resultado Esperado**:
   - O modo de Leitura Ativa é encerrado e a barra se recolhe suavemente.

---

### Cenário 5: Estudo Compartilhado em Modo Somente Leitura
1. Acesse o estudo com uma conta convidada (`canEdit = false`).
2. Ative a Leitura Ativa e teste a revelação e navegação.
3. **Resultado Esperado**:
   - A experiência de treino opera com 100% de fluidez.
   - Nenhuma requisição de escrita é enviada ao servidor e os destaques originais do autor não são deletados nem corrompidos.
