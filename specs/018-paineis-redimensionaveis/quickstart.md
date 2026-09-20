# Quickstart & Validation Guide: F06 — Painéis Redimensionáveis

**Branch**: `018-paineis-redimensionaveis` | **Feature**: F06 — Painéis Redimensionáveis | **Data**: 2026-09-19

Este guia fornece os passos práticos para homologar as capacidades de redimensionamento, colapso e responsividade dos painéis.

---

## 1. Preparação do Ambiente

Navegue até a pasta do frontend e inicie o ambiente de desenvolvimento:

```powershell
cd C:\Users\User\caderno\caderno-leitura-0.1\frontend
npm run dev
```

Abra a aplicação em um navegador moderno (Chrome, Edge ou Firefox) em `http://localhost:5173`.

---

## 2. Roteiro de Validação Manual

### Cenário 1: Redimensionamento por Arrasto com Limites Seguros
1. Abra um livro com capítulos cadastrados (ex.: `http://localhost:5173/#/livro/1`).
2. Posicione o cursor do mouse sobre a linha divisora entre o painel esquerdo (navegador de capítulos) e o centro da tela.
   - *Verificação:* O cursor deve se transformar no indicador de redimensionamento horizontal (`col-resize`).
3. Clique e arraste para a direita até atingir ~450px de largura.
   - *Verificação:* O painel expande suavemente e o texto central reorganiza suas quebras de linha sem seleção azul acidental.
4. Tente arrastar o divisor além do limite máximo (ex.: mais de 600px).
   - *Verificação:* O arrasto trava rigidamente no limite máximo, garantindo no mínimo 360px de palco central útil.
5. Dê um duplo clique na barra divisora.
   - *Verificação:* A largura da coluna esquerda retorna imediatamente para 300px (padrão de fábrica).

### Cenário 2: Colapso e Restauração com Persistência
1. Clique no botão de alternância rápida na divisória esquerda (ou no topo do painel).
   - *Verificação:* O painel de navegação se recolhe com transição suave; um botão compacto de reabertura permanece disponível.
2. Clique no botão de expansão do painel direito (Inspetor/Contexto).
   - *Verificação:* O painel direito se abre com metadados/contexto.
3. Pressione `F5` para recarregar a página.
   - *Verificação:* O estado do layout é idêntico: painel esquerdo recolhido, painel direito aberto e dimensões preservadas.

### Cenário 3: Acessibilidade por Teclado
1. Pressione `Tab` até colocar o foco na barra divisora (`role="separator"`).
   - *Verificação:* Uma moldura de foco acessível de alto contraste destaca o separador.
2. Pressione a tecla `Seta Direita` 5 vezes seguidas.
   - *Verificação:* O painel cresce 50 pixels (10px por clique), sem exigir uso do mouse.
3. Pressione `Enter`.
   - *Verificação:* O painel correspondente é colapsado. Pressione `Enter` novamente para reabri-lo.

### Cenário 4: Responsividade Mobile (< 768px)
1. Abra as Ferramentas de Desenvolvedor (`F12`) e simule a resolução de um smartphone (ex.: 390x844px).
   - *Verificação:* As divisórias de arrasto desaparecem. A tela de leitura ocupa 100% da largura útil sem transbordamento horizontal.
2. Toque no botão de índice/navegação.
   - *Verificação:* A lista de capítulos abre-se como uma gaveta (*drawer*) sobreposta com backdrop. Tocar fora fecha a gaveta.

---

## 3. Validação Automatizada

Para garantir zero regressões de tipagem e integridade dos testes:

```powershell
# 1. Testes unitários do frontend (incluindo composable useSplitPanes e componentes)
cd C:\Users\User\caderno\caderno-leitura-0.1\frontend
npm test

# 2. Compilação estrita de produção
npm run build

# 3. Testes do backend
cd C:\Users\User\caderno\caderno-leitura-0.1\backend
.venv\Scripts\pytest
```
