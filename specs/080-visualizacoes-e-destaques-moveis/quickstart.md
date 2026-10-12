# Guia Rápido de Validação (Quickstart): Feature 080

**Feature**: `080-visualizacoes-e-destaques-moveis`  
**Data**: 2026-10-12  

Este documento orienta a validação ponta a ponta das entregas da Feature 080 em ambiente local isolado.

---

## 1. Pré-Requisitos

- Node.js instalado na máquina local.
- Ambiente virtual Python (`.venv`) disponível em `backend/`.
- Banco de testes isolado (nunca utilizar `caderno.db` de produção).

---

## 2. Cenários de Validação

### Cenário 1: Biblioteca de Destaques sem Transbordamento e com Barra Inferior Íntegra
1. Executar a aplicação ou os testes automatizados com emulação de viewport de 320px, 375px e 767px.
2. Acessar a rota `/destaques`.
3. **Verificação de Largura**:
   - Confirmar que `scrollWidth <= clientWidth` no elemento raiz (`document.documentElement`), sem rolagem horizontal.
   - Constatar que o campo de busca ocupa 100% da primeira linha e que o seletor de modo quebra para a segunda linha.
4. **Verificação da Barra Inferior**:
   - Rolar até o fim da página.
   - Constatar que a barra de navegação inferior móvel (`MobileTabBar`) não cobre os botões de paginação.
   - Confirmar que o micro-toast flutuante de cópia aparece posicionado confortavelmente acima da barra móvel.

### Cenário 2: Gestos Táteis e Lista Semântica no Mapa de Estudos
1. Acessar um livro e selecionar a visualização Mapa (`StudyMapView`).
2. Reduzir a janela para viewport móvel ($\le 767\text{px}$) ou ativar emulação de toque.
3. **Verificação de Toque**:
   - Arrastar com um dedo: o grafo translada suavemente acompanhando o movimento (pan).
   - Fazer gesto de pinça com dois dedos: o zoom escala suavemente entre 0.5x e 2.5x.
4. **Verificação de Lista Alternativa**:
   - Alternar para a visualização em lista semântica.
   - Constatar listagem de estudos e relações com botões táteis de ação $\ge 44 \times 44\text{ px}$.

### Cenário 3: Rolagem Vertical Desbloqueada no Canvas
1. Acessar um capítulo no modo Canvas (`StudyCanvasView`) em viewport de 375px.
2. Tocar e deslizar verticalmente sobre a área do canvas.
3. Confirmar que a página do navegador rola verticalmente de forma suave, sem bloqueio por `touch-action: none`.
4. Verificar que a barra de ferramentas condensa opções secundárias em menu acessível.

### Cenário 4: Árvore de Estudos Acessível por Toque
1. Acessar o modo Árvore (`StudyTreeView`) com emulação de dispositivo de toque (`pointer: coarse`).
2. Constatar que as alças de arrasto invisíveis foram ocultadas.
3. Clicar no botão "⋯" de um card da árvore: verificar abertura do menu contextual com opções táteis de reordenação ("Mover para cima", "Mover para baixo") e alvos $\ge 44 \times 44\text{ px}$.

---

## 3. Comandos de Validação Automatizada

```powershell
# 1. Testes unitários focados da Feature 080
cd caderno-leitura-0.1/frontend
node --test tests/feature-080-mobile-views-highlights.test.mjs

# 2. Suíte completa de testes do frontend
npm test

# 3. Compilação de produção e checagem de tipos
npm run build

# 4. Testes do backend em ambiente virtual isolado
cd ../backend
.\.venv\Scripts\pytest.exe
```
