# Guia de Inicialização e Validação Rápida: F0.8.04 — Inbox: Mesa de Triagem e Despejo Intelectual

**Feature Branch**: `070-inbox-mesa-triagem`  
**Data**: 2026-10-11  
**Status**: Concluído (Fase 1 do Spec Kit)

---

## 1. Pré-Requisitos do Ambiente

- **Node.js**: v20+ e npm atualizado.
- **Python**: 3.13 de 64 bits no Windows.
- **Repositório**: Branch `main` ou `070-inbox-mesa-triagem`, com dependências instaladas.
- **Segurança**: Testes executados em diretórios isolados, sem tocar em `backend/data/caderno.db`.

---

## 2. Comandos de Validação Automatizada

Para verificar a integridade da aplicação e dos contratos:

### 2.1. Testes de Unidade e Contrato do Frontend
```powershell
cd caderno-leitura-0.1/frontend
npm test
```
*Critério de Sucesso*: 100% dos testes aprovados, incluindo testes de contratos de Inbox (`frontend/tests/inbox.test.mjs` e `feature-070-inbox-mesa-triagem.test.mjs`).

### 2.2. Build de Produção do Frontend (TypeScript + Vite)
```powershell
cd caderno-leitura-0.1/frontend
npm run build
```
*Critério de Sucesso*: Compilação concluída sem erros de tipagem TypeScript e sem advertências críticas.

### 2.3. Testes do Backend (FastAPI / Pytest)
```powershell
cd caderno-leitura-0.1
pytest backend/tests
```
*Critério de Sucesso*: Todas as suítes de teste de backend executadas em bancos efêmeros (`tmp_path`) sem regressões.

---

## 3. Roteiro de Validação Manual da Mesa de Triagem

Inicie a aplicação localmente:
```powershell
cd caderno-leitura-0.1
python iniciar.py
```
Acesse `http://localhost:8000/inbox` no navegador.

---

### Cenário 1: Despejo Rápido no Topo (*Quick Thought Drop*)
1. Ao carregar a página `/inbox`, observe o campo superior permanente de descarrego mental.
2. Clique no campo: verifique que a caixa de texto expande com suavidade de 1 linha para 4 linhas (~120px) em $\le 200$ms, revelando o campo de fonte opcional e a dica de atalho `Ctrl+Enter`.
3. Digite uma reflexão sintética (ex.: *"A persistência da memória na era digital"*).
4. Pressione `Ctrl+Enter` (ou `Cmd+Enter` no Mac):
   - A requisição é salva instantaneamente.
   - O campo é limpo e recolhido.
   - A nova nota surge no topo da lista com status "Pendente" sem recarregar a página.
   - O contador de pendências na barra é incrementado.

---

### Cenário 2: Barra Segmentada de Triagem e Filtros
1. Na barra segmentada, observe os 5 segmentos: `Pendentes`, `Promovidos`, `Vinculados`, `Arquivados` e `Todos`.
2. Clique em `Arquivados`: a lista exibe apenas notas previamente arquivadas, com acessibilidade `aria-selected="true"`.
3. Clique em `Pendentes`: retorna à lista de trabalho ativo com o contador destacado.
4. Digite um termo no campo de busca inline: confirme a filtragem em tempo real com debounce suave (250ms).

---

### Cenário 3: Triagem Contextual e Transição Cinética
1. Localize um cartão de captura na lista de pendentes.
2. Clique no botão de ação rápida "Arquivar":
   - O cartão desliza suavemente para a direita (`transform: translateX(30px)`) com desvanecimento (`opacity: 0`) em 180ms.
   - A lista reorganiza o espaço sem pulos bruscos.
   - O contador de pendências decrementa.
3. Alterne para o segmento `Arquivados`: constate que a nota arquivada agora está lá, exibindo a opção "Desarquivar".

---

### Cenário 4: Navegação e Triagem por Teclado (`J`, `K`, `E` e `Ctrl+Shift+C`)
1. Clique em uma área vazia da página (sem foco em inputs).
2. Pressione `J`: observe o anel de foco acessível selecionar o primeiro cartão.
3. Pressione `J` novamente: o foco se desloca para o segundo cartão.
4. Pressione `K`: o foco retorna para o primeiro cartão.
5. Com um cartão selecionado, pressione a tecla `E`:
   - A nota selecionada é arquivada com a animação suave.
   - O anel de foco passa automaticamente para a nota subsequente.
6. Pressione `Ctrl+Shift+C`:
   - O foco salta imediatamente para o campo de captura superior `QuickThoughtDrop`, pronto para digitação.

---

### Cenário 5: Estado Vazio "Mesa Limpa" e Tratamento de Falhas
1. Arquive todas as notas pendentes (ou use uma base nova sem pendências).
2. Na aba `Pendentes`, verifique a exibição da tela "Mesa Limpa":
   - Mensagem editorial calma e acolhedora.
   - Ilustração/ícone vetorial sereno, com zero emojis.
3. Simule queda de conexão (ou desative a rede temporariamente):
   - A tela apresenta o cartão editorial com `role="alert"` e botão "Tentar Novamente", sem expor mensagens técnicas cruas como "Not Found".

---

### Cenário 6: Imunidade Cromática e Layout Móvel
1. Alterne entre diferentes temas do Leitorum (Claro, Escuro, Sépia, E-Ink):
   - Constatar que todos os elementos, badges e botões se adaptam de forma homogênea, sem quebras de contraste ou cores hexadecimais saturadas fixas.
2. Redimensione a janela para largura móvel (< 768px):
   - A barra segmentada permite rolagem horizontal suave.
   - Todos os botões de ação e toques mantêm área mínima de $44 \times 44$px.
