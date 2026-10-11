# Quickstart & Verification Guide: Tela Placeholder do Document Intelligence

**Feature**: F0.3.5 — Tela Placeholder do Document Intelligence  
**Branch**: `069-document-intelligence-placeholder`  
**Date**: 2026-10-11  

---

## 1. Pré-Requisitos

- Servidor local do Caderno de Leitura em execução (`python iniciar.py` ou serviço ativo).
- Usuário autenticado na interface web (`http://localhost:8000`).

---

## 2. Cenários Manuais de Validação

### Cenário 1: Descoberta a partir do Hub de Importação
1. Acesse o sistema e navegue até `/importar`.
2. Localize o card **"Caderno Manuscrito (Em Pesquisa)"**.
3. Verifique o ícone editorial em SVG, o badge sutil e o texto sobre soberania de dados.
4. Clique no botão **"Conhecer a proposta"**.
5. **Resultado Esperado**: O navegador é redirecionado instantaneamente para `/digitalizar` sem recarregar a aplicação e sem erros no console.

### Cenário 2: Consulta à Tela Placeholder e Matriz de Maturidade
1. Na rota `/digitalizar`, confira o título da aba do navegador: `"Digitalizar Caderno — Caderno de Leitura"`.
2. Leia a seção de compromisso com a privacidade: confira a garantia expressa de que todo o processamento computacional ocorre localmente no computador, sem envio de imagens para serviços externos.
3. Inspecione a **Matriz de Maturidade**:
   - Etapa 1: *Localizar linhas e blocos na página* — Status: `Em validação`.
   - Etapa 2: *Ordem de leitura* — Status: `Em validação`.
   - Etapa 3: *Transcrição do texto manuscrito em português* — Status: `Em pesquisa`.
   - Etapa 4: *Classificação do conteúdo e diagramas* — Status: `Não iniciado`.
4. Observe a ilustração conceitual: certifique-se de que está claramente rotulada como `"Ilustração Conceitual"` e utiliza texto fictício.
5. **Resultado Esperado**: Informações claras, honestas, sem promessa de prazos e com fidelidade editorial.

### Cenário 3: Transição para Fluxos Produtivos Existentes
1. Na seção inferior de caminhos disponíveis, clique em **"Abrir Ateliê de Fichamento"**.
   - Confirme redirecionamento para `/importar`.
2. Volte para `/digitalizar` e clique em **"Ir para Caixa de Entrada"**.
   - Confirme redirecionamento para `/inbox`.
3. **Resultado Esperado**: Navegação fluida em 1 clique sem bloqueios ou telas mortas.

### Cenário 4: Inspeção de Rede e Resiliência Offline
1. Abra as Ferramentas do Desenvolvedor (F12) na aba **Rede (Network)**.
2. Navegue para `/digitalizar`.
3. Verifique que nenhuma chamada de rede relacionada a OCR, IA ou Document Intelligence é disparada.
4. Desative a rede (modo Offline nas DevTools) e navegue pela tela.
5. **Resultado Esperado**: A página permanece íntegra e navegável, pois opera exclusivamente com ativos estáticos do bundle.

---

## 3. Validação Automatizada

Executar na raiz do frontend (`caderno-leitura-0.1/frontend`):

```powershell
# Execução da suíte de testes unitários da feature
node --test tests/feature-069-document-intelligence-placeholder.test.mjs

# Execução global da suíte de frontend
npm test

# Verificação estrita de tipagem TypeScript e build Vite
npm run build
```
