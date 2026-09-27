# Quickstart & Validation Guide: F0.6.1 — Importação Inteligente

**Feature**: `040-importacao-inteligente`  
**Date**: 2026-09-27  

Este guia descreve os passos e cenários para validação de ponta a ponta da **Importação Inteligente**.

---

## 1. Pré-Requisitos do Ambiente

- **Python**: 3.13 (64-bit) com ambiente virtual ativo (`.venv`).
- **Node.js**: v20+ com dependências instaladas em `frontend/node_modules`.
- **Banco de Dados**: Para validações manuais, a aplicação local pode ser iniciada via `python iniciar.py`. Para testes automatizados, o pytest utiliza bancos descartáveis em `tmp_path`.

---

## 2. Validação Automatizada (Suíte de Testes)

### Backend (Testes Unitários do Parser Tolerante)
Executa testes de reconhecimento de variações de títulos, prefixos, marcações de negrito, isolamento de cercas de código (` ``` `) e geração de avisos:

```powershell
cd caderno-leitura-0.1/backend
pytest tests/unit/test_import_parser.py -v
```

**Resultado Esperado**:
- Todos os testes de sinônimos (`visao geral`, `sintese`, `aprofundamento`, `termos-chave`, `fontes`) passam com 100% de sucesso.
- Nenhuma quebra de isolamento em blocos com cercas de código Markdown.

### Frontend (Testes de Componente e Composable)
Valida a geração da prévia no evento de colagem (`paste`), sincronização com o botão "Atualizar prévia", movimentação de texto não atribuído com 1 clique e preservação do accordion recolhido:

```powershell
cd caderno-leitura-0.1/frontend
npm test
npm run build
```

**Resultado Esperado**:
- Testes unitários do composable `useImportDraft` e views passam sem erros.
- Build do Vite concluído sem warnings de tipo TypeScript (`vue-tsc --noEmit`).

---

## 3. Validação Manual de Ponta a Ponta (Fluxo do Usuário)

### Cenário 1: Importação com Sinônimos e Colagem Instantânea
1. Inicie a aplicação local:
   ```powershell
   python iniciar.py
   ```
2. Acesse `http://localhost:8000/import` (ou pelo menu "Novo estudo").
3. Selecione um Livro e um Capítulo disponíveis.
4. Cole no campo principal um texto contendo títulos variados:
   ```markdown
   # 1. Visão Geral
   Esta obra analisa as transformações do pensamento moderno.

   **Aprofundamento:**
   O autor descreve em três momentos principais...

   ## Glossário e Termos
   - Hermenêutica: arte da interpretação.

   ### Fontes Consultadas
   - SILVA, 2023.
   ```
5. **Verificação**:
   - A prévia deve carregar imediatamente (sem necessidade de rolagem nem de clique prévio).
   - As 4 seções devem aparecer populadas respectivamente com seus conteúdos.
   - O botão "Salvar Estudo" fica disponível imediatamente.
6. Clique em "Salvar Estudo".
7. Acesse o estudo salvo e verifique se as 4 seções foram persistidas e se o texto colado original está íntegro na aba/visualização do fichamento da fonte.

### Cenário 2: Tratamento de Texto Não Classificado
1. Na tela de importação, cole um texto com saudação inicial do chatbot:
   ```markdown
   Olá! Aqui está o fichamento detalhado que você pediu:

   ## Resumo
   Conteúdo do resumo...

   ## Explicação
   Conteúdo da explicação...
   ```
2. **Verificação**:
   - Um card de aviso "Conteúdo Não Classificado" deve ser exibido com o texto "Olá! Aqui está o fichamento...".
   - Botões "Mover para Resumo", "Mover para Explicação", etc., estão visíveis.
3. Teste o clique em "Mover para Resumo":
   - O texto da introdução é imediatamente transferido para a seção Resumo e o aviso de não classificado desaparece.
4. Caso decida salvar sem clicar em nenhum botão:
   - O conteúdo residual é anexado automaticamente ao final da Explicação com divisor visual suave, sem gerar perda de dados.

### Cenário 3: Painel de Ajuste Manual Detalhado (Accordion)
1. Na mesma tela de prévia, localize o bloco colapsável "Ajuste manual detalhado (opcional)".
2. **Verificação**:
   - Por padrão, o painel deve estar fechado/recolhido para não poluir visualmente a tela.
   - Ao clicar no título, os 4 campos `<textarea>` se abrem, permitindo ajustes finos se o leitor desejar.
   - Ao alterar uma palavra em qualquer textarea, a alteração é sincronizada e salva corretamente.
