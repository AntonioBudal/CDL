# Quickstart & Validation Guide: F01 — Sistema de Visualizações e Dashboard Responsivo

**Branch**: `019-sistema-visualizacoes` | **Data**: 2026-09-19

---

## 1. Preparação do Ambiente

Inicie o servidor de desenvolvimento do frontend:

```powershell
cd C:\Users\User\caderno\caderno-leitura-0.1\frontend
npm run dev
```

Abra a aplicação no navegador em `http://localhost:5173`.

---

## 2. Roteiro de Validação Manual

### Cenário 1: Alternância Fluida entre os 5 Modos de Visualização
1. Abra qualquer livro que possua estudos cadastrados (ex.: `http://localhost:5173/#/livros/1`).
2. Localize a barra seletora de visualização no topo da área de estudos.
3. Clique em **Grade**: os estudos aparecem em cartões com ênfase visual em título, resumo e data.
4. Clique em **Lista**: os estudos aparecem em linhas compactas de alta densidade informativa.
5. Clique em **Árvore**: os estudos aparecem organizados com hierarquia e ícones de expansão.
6. Clique em **Mapa**: os estudos são dispostos em nós conectados em uma rede conceitual.
7. Clique em **Canvas**: os estudos são dispostos em cartões flutuantes 2D no espaço bidimensional.
8. *Verificação*: A transição ocorre em menos de 100ms sem recarregar a página e sem quebras de layout.

### Cenário 2: Preservação do Estudo em Foco e Persistência Híbrida
1. Selecione um estudo específico em qualquer uma das visualizações.
2. Comute para outro modo: o mesmo estudo permanece visualmente destacado.
3. Altere o modo do livro para "Árvore".
4. Pressione `F5` para recarregar a página.
5. *Verificação*: O livro reabre automaticamente na visão "Árvore" selecionada anteriormente.
6. Abra um novo livro sem preferência prévia: constata-se a herança da preferência global do leitor.

### Cenário 3: Acessibilidade e Navegação por Teclado
1. Pressione `Tab` até colocar o foco no seletor de visualizações.
2. Pressione a tecla `Seta Direita` e `Seta Esquerda`.
3. *Verificação*: O foco e o modo comutam ordenadamente em conformidade com o padrão WAI-ARIA (`role="tablist"` e `role="tab"`).
4. Pressione as teclas `Home` e `End` para ir diretamente ao primeiro (Grade) e ao último modo (Canvas).

### Cenário 4: Validação do Dashboard no Celular (< 768px)
1. Abra as Ferramentas de Desenvolvedor (`F12`) e simule a visualização de um smartphone (ex.: 390x844px).
2. Acesse a rota de Dashboard (`/#/dashboard`).
3. *Verificação 1 (Métricas)*: Os indicadores organizam-se em uma grade de 2 colunas perfeitamente equilibrada, com o cartão de *Sequência Atual* ocupando as duas colunas inferiores com destaque visual.
4. *Verificação 2 (Mapa de Calor)*: O mapa de calor anual inicializa com o scroll posicionado na extrema direita, exibindo as semanas recentes e a data de hoje imediatamente, sem rolagem manual prévia.
5. *Verificação 3 (Linha do Tempo)*: Os cartões de atividade e links de ação ("Ler estudo", "Abrir livro") exibem botões confortáveis com dimensões táteis mínimas de 44x44px.

---

## 3. Validação Automatizada

```powershell
# 1. Testes unitários do frontend
cd C:\Users\User\caderno\caderno-leitura-0.1\frontend
npm test

# 2. Compilação estrita TypeScript/Vite
npm run build

# 3. Testes do backend (garantindo zero regressões)
cd C:\Users\User\caderno\caderno-leitura-0.1
.\backend\.venv\Scripts\python.exe -m pytest backend/tests
```
