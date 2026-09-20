# Research: F07 — Dashboard 2.0 (Cockpit de Estudos e Hub de Navegação)

**Feature Branch**: `024-dashboard-cockpit`  
**Date**: 2026-09-19  
**Spec**: [spec.md](./spec.md)  

---

## 1. Pesquisa Técnica e Decisões de Arquitetura

### R01: Ponto de Entrada da Aplicação e Rota Inicial Configurável
- **Decisão**: A rota raiz `/` passa a ser associada a `DashboardView.vue` como ponto de entrada padrão. Uma chave no `localStorage` (`caderno_home_view`: `'dashboard'` | `'books'`, padrão `'dashboard'`) e uma verificação no hook de navegação global do `vue-router` (`router.beforeEach`) permitem que o usuário escolha abrir direto no Acervo de Livros (`/books`), sem quebras ou redirecionamentos desnecessários.
- **Racional**: Transforma o Caderno de Leitura em um ambiente dinâmico focado em frentes ativas de estudo. Para o leitor que prefere o modelo clássico de prateleira, o toggle nas Configurações assegura autonomia e zero imposição de perspectiva (Princípio 2 do Roadmap 0.4).
- **Alternativas rejeitadas**:
  - *Redirecionamento fixo no backend*: Rejeitado porque o Caderno opera como SPA local única e a preferência de tela inicial deve responder instantaneamente sem requisição de rede.
  - *Substituir a rota `/books` por `/`*: Rejeitado porque quebra referências, links externos e coerência semântica de URLs.

---

### R02: Otimização de Consultas SQL para Estudos Órfãos e Relações Recentes no SQLite
- **Decisão**: Executar a identificação de estudos sem relações através de cláusula `NOT EXISTS` combinada sobre `study_relations`:
  ```sql
  SELECT s.id, s.title, s.reading_status, s.created_at, b.id AS book_id, b.title AS book_title, c.id AS chapter_id, c.name AS chapter_title
  FROM studies s
  JOIN chapters c ON s.chapter_id = c.id
  JOIN books b ON c.book_id = b.id
  WHERE s.deleted_at IS NULL AND b.deleted_at IS NULL
    AND NOT EXISTS (
      SELECT 1 FROM study_relations sr 
      WHERE sr.source_study_id = s.id OR sr.target_study_id = s.id
    )
  ORDER BY s.updated_at DESC
  LIMIT 5;
  ```
  E para a contagem total de órfãos:
  ```sql
  SELECT COUNT(s.id) FROM studies s
  JOIN chapters c ON s.chapter_id = c.id
  JOIN books b ON c.book_id = b.id
  WHERE s.deleted_at IS NULL AND b.deleted_at IS NULL
    AND NOT EXISTS (
      SELECT 1 FROM study_relations sr 
      WHERE sr.source_study_id = s.id OR sr.target_study_id = s.id
    );
  ```
- **Racional**: Os índices criados na migração 0008 (`ix_study_relations_source` e `ix_study_relations_target`) cobrem perfeitamente essas condições. O `NOT EXISTS` é altamente eficiente no planejador de consultas do SQLite, executando em menos de 10ms mesmo para acervos com milhares de estudos.
- **Alternativas rejeitadas**:
  - *Carregar todos os estudos e filtrar em memória no Python*: Ineficiente para acervos grandes; consome memória desnecessária.
  - *Adicionar coluna desnormalizada `has_relations` em `studies`*: Quebraria a separação de responsabilidades (Princípio 1 do Roadmap: Estrutura vs Relações) e exigiria triggers complexos.

---

### R03: Calibração de Contraste e Opacidade Multitema no Calendário de 12 Meses (Heatmap)
- **Decisão**: 
  1. Definir tokens CSS semânticos dedicados para as células do mapa de calor: `--heatmap-cell-empty-bg`, `--heatmap-cell-empty-border`, `--heatmap-cell-empty-opacity`.
  2. Para dias sem atividade (`.level-0`), aplicar:
     - No tema **Clássico**: Fundo suave `#f1f5f9`, borda `#e2e8f0` e opacidade `0.6`.
     - No tema **Escuro**: Fundo `rgba(255, 255, 255, 0.04)`, borda `rgba(255, 255, 255, 0.08)` e opacidade `0.5`.
     - No tema **Sépia**: Fundo `rgba(60, 40, 20, 0.06)`, borda `rgba(60, 40, 20, 0.12)` e opacidade `0.5`.
     - No tema **Solarized**: Fundo `rgba(0, 43, 54, 0.08)`, borda `rgba(0, 43, 54, 0.15)` e opacidade `0.55`.
     - No tema **E-Ink**: Fundo `#ffffff`, borda tracejada fina cinza claro `#9ca3af` e opacidade `0.5`.
  3. Para dias com atividade (`.level-1`, `.level-2`, `.level-3`):
     - Manter opacidade `1.0` inalterada e utilizar saturação e luminosidade elevadas da cor de destaque (`var(--color-accent)`), com borda sutilmente intensificada, assegurando que dias ativos saltem aos olhos instantaneamente em qualquer tema.
- **Racional**: Atende diretamente à dor apontada pelo usuário: em temas escuros e sépia, o fundo do `.level-0` anteriormente se fundia com o `.level-1` gerado via `color-mix`, tornando a visualização de frequência homogênea e difícil de distinguir.
- **Alternativas rejeitadas**:
  - *Usar apenas uma cor fixa para todos os temas*: Quebra a coerência estética dos temas e a imersão visual do usuário.

---

### R04: Arquitetura Responsiva Mobile-First com Abas/Acordeões e Prevenção de Overflow
- **Decisão**: 
  1. Em desktop (>=1024px), o Dashboard exibe uma grade modular articulada de 2 colunas principais (Coluna da Esquerda: Continuar Estudos e Estudos para Conectar; Coluna da Direita: Conexões Recentes e Métricas Topológicas) e Linha do Tempo/Heatmap ocupando a largura total na base.
  2. Em dispositivos móveis (<768px):
     - Barra métrica compacta no topo em formato 2x2.
     - Bloco "Continuar Estudos" prioritário com largura integral e alvos mínimos de toque de 44x44px.
     - Widgets "Estudos para Conectar" e "Conexões Recentes" agrupados sob um seletor visual em abas (*tabs*) acessíveis ou modo acordeão, diminuindo a altura total da página pela metade.
     - Heatmap com rolagem horizontal contida e visualização de período compacto ativada por padrão.
     - Contêiner raiz com `overflow-x: hidden; max-width: 100vw;` prevenindo qualquer rolagem lateral acidental no smartphone.
     - Barra de chips aderentes (*sticky navigation chips*) para navegação rápida entre blocos com 1 toque.
- **Racional**: Elimina a fadiga de rolagem (*scroll fatigue*) no celular e garante que a ação primordial (retomar estudo) esteja imediatamente acessível na área nobre do polegar (*thumb zone*).
- **Alternativas rejeitadas**:
  - *Ocultar completamente widgets secundários no celular*: Prejudicaria a utilidade do Caderno em dispositivos móveis, onde muitos usuários revisam suas notas.
