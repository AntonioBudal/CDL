# Quickstart: Validação da Feature F 0.7.4 (Redesenho da Grid View)

**Feature**: F 0.7.4 — Redesenho da Grid View: Reconhecimento Visual e Cartografia de Leitura  
**Artifact**: `quickstart.md`

---

## 1. Pré-requisitos
- Servidor backend em execução ou ambiente de teste automatizado ativo.
- Frontend em execução em `http://localhost:5173` ou suíte de testes unitários (`npm test`).

---

## 2. Cenários de Validação Fim a Fim

### Cenário 1: Reconhecimento Cromático de Status (P1 - MVP)
1. Acesse um capítulo contendo múltiplos estudos com diferentes status (`rascunho`, `em_andamento`, `revisado`, `concluido`).
2. **Resultado esperado**:
   - Cada cartão exibe um friso lateral esquerdo de 4px na cor canônica do status.
   - O cabeçalho do cartão exibe o `StudyStatusBadge.vue` com o rótulo textual e ponto colorido.
   - Clicar no badge permite alterar o status sem navegar para fora da página.

### Cenário 2: Mini-Indicadores de Densidade e Prévia do Resumo (P2)
1. Observe um estudo que possua destaques e notas vinculadas criadas via barra flutuante (F 0.7.3) e resumo preenchido.
2. **Resultado esperado**:
   - O cartão exibe entre 2 e 3 linhas da síntese analítica com corte suave (*line-clamp*).
   - O rodapé do cartão exibe um micro-badge com ícone de marcador e a contagem de destaques (ex.: `5 destaques`).
   - Se o estudo possuir relações com outros estudos, exibe micro-badge com ícone de elo e a contagem de conexões.

### Cenário 3: Navegação Direta de 1 Clique e Proteção da Lixeira (P1 / P2)
1. Clique em qualquer área do cartão do estudo (exceto o badge de status e o botão de lixeira).
2. **Resultado esperado**: O sistema navega instantaneamente para a tela de leitura do estudo (`StudyView.vue`).
3. Retorne à grade e clique no botão de lixeira no rodapé do cartão.
4. **Resultado esperado**: Abre o modal de confirmação de exclusão sem navegar para o estudo (`@click.stop` isolou o evento).

### Cenário 4: Responsividade e Ergonomia Mobile (P3)
1. Em tela desktop ampla (> 1024px), verifique que os cartões formam 3 colunas harmoniosas.
2. Reduza a janela para largura de tablet (800px): os cartões reorganizam-se em 2 colunas.
3. Alterne para visualização móvel (< 768px): os cartões organizam-se em 1 coluna confortável com alvos de toque mínimos de 44×44px.

### Cenário 5: Skeleton Screens durante o Carregamento (P3)
1. Alterne entre capítulos na navegação.
2. **Resultado esperado**: Enquanto os dados são carregados, a grade renderiza esqueletos pulsantes com a exata geometria dos cartões, evitando saltos bruscos de tela.
