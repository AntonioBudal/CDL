# Quickstart: Validação da Feature F 0.7.5 (Redesenho da List View)

**Feature**: F 0.7.5 — Redesenho da List View: Busca Rápida, Filtragem e Comparação Analítica  
**Artifact**: `quickstart.md`

---

## 1. Pré-requisitos
- Servidor backend executando ou suite de testes de integração (`pytest`).
- Frontend rodando em `http://localhost:5173` ou suite de testes unitários (`npm test`).

---

## 2. Cenários de Validação Fim a Fim

### Cenário 1: Tabela Densa com Ordenação Multicritério Tripartite (P1 - MVP)
1. Navegue para um capítulo com estudos com títulos variados, datas e status distintos.
2. Alterne para o modo **List View**.
3. **Resultado esperado**:
   - A tabela exibe colunas alinhadas: Título, Status, Localização, Data, Conexões, Seções e Ações.
   - Clicar no cabeçalho "Título" reordena alfabeticamente A-Z com seta `↑`.
   - Clicar novamente reordena Z-A com seta `↓`.
   - Clicar pela terceira vez reseta para a ordem natural de leitura sem setas.
   - Recarregar a página mantém a preferência salva no `localStorage`.

### Cenário 2: Busca Textual Rápida e Insensível a Acentos (P2)
1. No campo de busca rápida da List View, digite um termo com ou sem acentos (ex.: "teoria" para "Teoria").
2. **Resultado esperado**:
   - A lista de estudos é filtrada instantaneamente (< 50ms) sem recarregar a tela.
   - O contador de resultados informa a quantidade exibida (ex.: `Exibindo 2 de 8 estudos`).
   - Apagar o campo de busca restaura imediatamente a lista completa.

### Cenário 3: Filtragem por Status e Estado Vazio Acolhedor (P2)
1. Selecione a pílula de status "Em Andamento".
2. **Resultado esperado**:
   - Apenas estudos com status `em_andamento` permanecem visíveis na tabela.
3. Digite um termo de busca inexistente para forçar zero resultados.
4. **Resultado esperado**:
   - É exibido o estado vazio de busca com mensagem informativa e o botão "Limpar filtros".
   - Clicar em "Limpar filtros" reseta tanto o texto da busca quanto o status para "Todos".

### Cenário 4: Micro-Chips de Seções Analíticas Preenchidas (P3)
1. Observe as linhas de estudos com diferentes graus de preenchimento.
2. **Resultado esperado**:
   - Cada linha exibe 4 micro-chips contíguos de largura fixa: `R`, `E`, `C`, `Ref`.
   - Seções preenchidas aparecem coloridas com contraste adequado.
   - Seções vazias aparecem esmaecidas em cinza neutro.

### Cenário 5: Ergonomia Mobile Compacta e Alvos Táteis de 44px (P3)
1. Reduza a janela para largura móvel (< 768px).
2. **Resultado esperado**:
   - A tabela transiciona para uma lista compacta de 2 linhas por estudo sem rolagem horizontal.
   - O filtro de status é acessado via botão expansível ("Filtrar por status ▾").
   - Todos os botões e áreas clicáveis possuem dimensões táteis mínimas de 44×44px.
