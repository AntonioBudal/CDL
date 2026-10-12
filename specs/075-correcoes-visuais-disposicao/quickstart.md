# Quickstart & Validation Guide: Correções Visuais, de Cor e de Disposição

**Feature**: `075-correcoes-visuais-disposicao`  
**Date**: 2026-10-11  
**Status**: Concluído (Fase 1)

---

## 1. Pré-Requisitos de Validação

- Node.js instalado (v18+)
- Repositório local atualizado no branch da feature
- Dependências de frontend instaladas (`npm --prefix caderno-leitura-0.1/frontend install` se necessário)

---

## 2. Cenários Automatizados de Teste

### Cenário A: Validação de Ausência de Variáveis CSS Indefinidas (P1)
Garante que nenhum componente Vue utilize variáveis CSS fora do conjunto canônico declarado.

**Comando**:
```powershell
node tests/feature-075-css-tokens-integrity.test.mjs
```

**Resultado Esperado**:
- 0 variáveis de cor, raio ou sombra indefinidas encontradas.
- Saída: `Sucesso: Todas as variáveis CSS utilizadas no frontend estão devidamente mapeadas.`
- Código de retorno: `0`.

---

### Cenário B: Suíte Completa de Testes de Frontend
Garante que nenhum componente sofreu regressão de montagem, testes de unidade ou composables.

**Comando**:
```powershell
npm --prefix caderno-leitura-0.1/frontend test
```

**Resultado Esperado**:
- 100% dos testes aprovados (GREEN).

---

### Cenário C: Compilação de Produção e Tipagem Estrita
Garante que o build de produção Vite é gerado sem erros de tipo TypeScript ou empacotamento CSS.

**Comando**:
```powershell
npm --prefix caderno-leitura-0.1/frontend run build
```

**Resultado Esperado**:
- Build concluído em `dist/` com `0` erros.

---

## 3. Roteiro de Inspeção Visual e Aceite Manual

1. **Troca de Temas Escuros**:
   - Ativar o tema **Grafite** ou **Noite Suave** em Configurações.
   - Navegar para as páginas de **Destaques**, **Hub de Revisão**, **Biblioteca** e **Lixeira**.
   - **Verificar**: Nenhum painel ou cartão apresenta caixa branca opaca ou texto escuro ilegível.
2. **Grade de Livros com Poucos Itens**:
   - Na tela `/livros`, com 1 a 3 livros cadastrados, verificar o alinhamento da grade.
   - **Verificar**: Os livros iniciam alinhados à esquerda da página, sem estiramento desproporcional.
3. **Miniatura de Capa em Lista**:
   - Alternar a visualização para Lista.
   - **Verificar**: Livros sem capa exibem miniatura sólida sem texto cortado ou ilegível.
4. **Visualizações de Estudos (`/livros/:id`)**:
   - Abrir um livro e inspecionar as abas Lista, Árvore e Mapa em tema escuro.
   - **Verificar**:
     - Lista: cabeçalhos alinhados com suas colunas e ordenação indicada com ícones SVG.
     - Árvore: ícones e chevrons visíveis em repouso e sob o cursor.
     - Mapa: controles de zoom nítidos e barra mobile restrita a dispositivos móveis.
5. **Cabeçalho e Rodapé**:
   - Inspecionar o botão de usuário no cabeçalho: apenas foto/iniciais, sem nome externo redundante nem setas soltas.
   - Inspecionar o rodapé interno: alinhamento distribuído em desktop e limpo em telas móveis.
6. **Persistência de Tema da Visita**:
   - Acessar a página inicial sem estar logado (`/`).
   - Escolher um tema diferente na vitrine (ex.: *Pergaminho* ou *Fiorde*).
   - Navegar para `/sobre` e `/apoie`.
   - **Verificar**: O tema escolhido permanece ativo em todas as páginas públicas durante a sessão.
