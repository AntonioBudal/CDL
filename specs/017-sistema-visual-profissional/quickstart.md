# Quickstart & Validation Guide: F09 - Sistema Visual Profissional

**Branch**: `017-sistema-visual-profissional`  
**Feature**: F09 — Sistema Visual Profissional  
**Data**: 2026-09-19  

Este guia detalha o roteiro de execução e validação ponta a ponta para homologar a entrega da feature **F09 — Sistema Visual Profissional**.

---

## 1. Pré-Requisitos e Preparação do Ambiente

Certifique-se de estar na raiz do workspace ou da aplicação:

```powershell
cd C:\Users\User\caderno\caderno-leitura-0.1\frontend
```

Instalação da biblioteca de iconografia aprovada (executada no ciclo de implementação):
```powershell
npm install lucide-vue-next
```

---

## 2. Cenários de Validação

### Cenário 1: Erradicação Completa de Emojis
1. Execute o build ou servidor de desenvolvimento:
   ```powershell
   npm run dev
   ```
2. Navegue pelas seguintes telas:
   - **Acervo (`/`):** Verifique os botões de adicionar livro, exportar e alternar modo de exibição. Nenhum emoji deve estar presente.
   - **Visão do Livro (`/livro/:id`):** Verifique os botões de editar capítulo (substituindo o antigo `✎`) e excluir (substituindo o antigo `🗑`).
   - **Lixeira (`/lixeira`):** Quando a lixeira estiver vazia, certifique-se de que o ícone `🗑️` em emoji foi substituído pelo componente `EmptyState` com ícone vetorial Lucide `Trash2`.
   - **Dashboard (`/dashboard`):** Verifique o indicador de dias consecutivos (substituindo o antigo `🔥` por ícone vetorial `Flame`) e o botão de limpar data (substituindo o antigo `✕`).
   - **Modais:** Verifique os botões de fechar dos modais (`BookEditModal`, `TrashConfirmModal`, `ExportModal`, `RestoreModal`). Todos devem utilizar o ícone vetorial `X`.

### Cenário 2: Purificação Semântica e Nomenclatura Editorial
1. Abra a tela de **Importar Fichamento (`/importar`)**:
   - O título deve ser "Importar Fichamento" (em vez de "Importar resposta").
   - O campo principal deve ter o rótulo "Fichamento da Fonte" (em vez de "Resposta inteira do ChatGPT").
   - O texto de orientação deve orientar o leitor a colar o texto-base de apoio sem menções a IA.
2. Abra a tela de **Leitura de Estudo (`/estudo/:id`)**:
   - A seção retrátil inferior deve intitular-se "Consultar Fichamento da Fonte" (em vez de "Consultar resposta original").
3. Abra a tela de **Edição de Estudo (`/estudo/:id/editar`)**:
   - O campo de texto original preserva seu rótulo como "Fichamento da Fonte".

### Cenário 3: Esqueletos de Carregamento e Estados Vazios
1. Simule lentidão ou carregamento em uma lista de livros:
   - Os cartões de esqueleto devem surgir com proporção exata à dos livros reais.
   - O layout não deve sofrer saltos visuais (*layout shift*) quando os dados reais forem renderizados.
2. Ative a preferência do sistema operacional por redução de movimento (`prefers-reduced-motion: reduce`):
   - Os esqueletos de carregamento devem permanecer estáticos, com opacidade suave constante e sem oscilação de brilho.

---

## 3. Comandos de Validação Automatizada

Para validar que nenhuma regressão de tipos ou quebra de testes ocorreu:

```powershell
# 1. Validação de tipagem estrita TypeScript e Build de Produção
cd C:\Users\User\caderno\caderno-leitura-0.1\frontend
npm run build

# 2. Execução da suíte de testes unitários do frontend
npm test

# 3. Execução da suíte de testes unitários do backend
cd C:\Users\User\caderno\caderno-leitura-0.1\backend
.venv\Scripts\pytest
```

**Critério de Sucesso do Quickstart:**
- `npm run build` compila com **0 erros**.
- 100% dos testes do frontend e backend passam com **sucesso verde**.
- Nenhuma menção a emojis ou termos de IA é encontrada na varredura automatizada.
