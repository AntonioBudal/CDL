# Quickstart: Validação da Responsividade Mobile, Toque Nativo e Micro-Toast

**Feature**: `051-mobile-toque-microtoast`  
**Data**: 2026-10-03  
**Status**: Pronto para Execução

Este guia descreve os passos práticos para validar as melhorias de seleção por toque, botões em ícones puros e o micro-toast no topo da aba de estudos.

---

## 1. Cenários de Validação Manual

### Cenário 1: Seleção de Palavra por Duplo Toque no Mobile
1. Abra o navegador com emulação móvel ativada (ex: iPhone 14, 390x844px).
2. Acesse qualquer estudo em `StudyView.vue`.
3. Toque duas vezes rapidamente sobre qualquer palavra de um parágrafo.
4. **Verificação**:
   - A palavra é selecionada imediatamente.
   - A barra flutuante de ações se abre na base da tela.

---

### Cenário 2: Barra Móvel com Ícones Puros de 44x44px
1. Com a barra de ações aberta no mobile, inspecione seus botões.
2. **Verificação**:
   - Nenhum texto de legenda ("Destacar", "Anotar", etc.) é exibido; apenas os ícones canônicos.
   - Cada botão possui dimensões de toque de pelo menos 44x44px.
   - Os ícones estão perfeitamente centralizados e confortáveis ao toque do polegar.

---

### Cenário 3: Exibição do Micro-Toast no Topo da Aba de Leitura
1. Toque no botão de Marca-texto (ou Ocluir, ou Citação) na barra de ferramentas.
2. **Verificação**:
   - Uma pequena notificação elegante surge no topo do leitor (`top: 1rem`), centralizada horizontalmente.
   - Exibe a mensagem correspondente (ex: `"Destaque aplicado"` ou `"Trecho ocultado para revisão"`).
   - O micro-toast possui `pointer-events: none` (não bloqueia toques na leitura).
   - Após 1.8 segundos, ele desaparece suavemente com fade-out.

---

## 2. Validação Automatizada de Testes

```bash
# Execução dos testes unitários e de integração do frontend
npm test

# Validação de tipagem e empacotamento de produção
npm run build
```
