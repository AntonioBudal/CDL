# Quickstart: Validação da Hierarquia e Ergonomia de Header Actions no Leitor

**Feature**: `050-ergonomia-header-actions`  
**Data**: 2026-10-03  
**Status**: Pronto para Execução

Este guia descreve os passos de validação ponta a ponta para verificar o funcionamento da reorganização do cabeçalho de `StudyView.vue` e do componente `DropdownMenu.vue`.

---

## 1. Pré-Requisitos e Ambiente

Certifique-se de estar na raiz do projeto frontend:
```bash
cd caderno-leitura-0.1/frontend
```

---

## 2. Cenários de Validação Manual

### Cenário 1: Hierarquia de Ações no Desktop (≥ 768px)
1. Inicie a aplicação localmente (`py -3.13 iniciar.py` na raiz).
2. Abra o navegador em janela maximizada (largura > 1024px) e navegue para qualquer estudo existente.
3. **Verificação**:
   - O botão "Editar estudo" possui destaque visual nítido como ação primária (`button primary`).
   - O botão "Compartilhar" está visível ao lado do botão primário com estilo secundário.
   - O botão `•••` está presente logo após "Compartilhar".
   - Os botões "Exportar estudo", "Histórico" e "Mover para a lixeira" NÃO poluem a barra principal.
4. Clique no botão `•••`.
5. **Verificação**:
   - O menu se abre exibindo "Histórico de versões", "Exportar estudo" e "Mover para a lixeira" (em vermelho/danger).
   - Ao clicar fora do menu ou teclar `Escape`, o menu fecha suavemente.

---

### Cenário 2: Cabeçalho Condensado no Mobile (< 768px e < 640px)
1. Ative a emulação de dispositivos móveis do DevTools (ex.: iPhone 14, 390x844px).
2. Abra qualquer estudo.
3. **Verificação**:
   - O breadcrumb não quebra em várias linhas; exibe um botão compacto de retorno `← Voltar ao capítulo`.
   - O bloco de ações possui exatamente 2 botões na linha: o botão primário "Editar" (compacto) e o menu `•••`.
   - As ações ocupam estritamente 1 linha horizontal, sem qualquer quebra de linha.
   - O tamanho de toque de ambos os botões respeita no mínimo 44x44px.
4. Abra o menu `•••` no mobile.
5. **Verificação**:
   - A opção "Compartilhar" está presente dentro do menu, junto a "Histórico", "Exportar" e "Mover para a lixeira".
   - O menu não provoca rolagem horizontal na tela.

---

### Cenário 3: Acessibilidade e Navegação por Teclado
1. Navegue pelo cabeçalho utilizando a tecla `Tab`.
2. Quando o foco atingir o botão `•••`, pressione `Enter` ou `Space`.
3. **Verificação**:
   - O menu abre e o primeiro item recebe foco imediatamente.
   - Pressione `ArrowDown` e `ArrowUp`: o foco transita de forma circular entre os itens.
   - Pressione `Escape`: o menu fecha e o foco retorna para o botão `•••`.

---

### Cenário 4: Modo Somente Leitura (Convidado)
1. Abra um estudo compartilhado onde o usuário não é proprietário (`canEdit === false`).
2. **Verificação**:
   - O botão "Editar estudo" não é renderizado.
   - A opção "Mover para a lixeira" não aparece no menu `•••`.
   - Apenas a opção de leitura/consumo "Exportar estudo" permanece disponível.

---

## 3. Validação Automatizada de Testes

Execute as suítes de validação automatizada:

```bash
# 1. Testes unitários do frontend
npm test

# 2. Verificação de tipagem estrita e build de produção
npm run build
```

**Critério de Sucesso**: 100% dos testes passando sem nenhuma quebra de regressão e build sem erros de compilação TypeScript.
