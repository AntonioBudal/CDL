# Research & Architecture Decisions: Dashboard de Leitura com Calendário e Timeline

**Feature**: `013-dashboard-calendario-timeline`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Decisão 1: Estratégia de Agregação de Atividade (On-the-fly vs Tabela de Eventos)

### Contexto
O Roadmap 0.3 e o spec exigem computar dias ativos, frequência de leitura, sequências consecutivas (streaks) e uma timeline de atividades recentes, sem inventar estatísticas e mantendo consistência estrita com os itens ativos (excluindo a lixeira).

### Decisão
Utilizar agregação direta via consultas SQL/SQLAlchemy sobre os carimbos `created_at`, `updated_at` e `deleted_at` das tabelas existentes `books` e `studies`, sem criar novas tabelas de log ou migrações de banco.

### Justificativa
1. **Zero Impacto no Esquema do Banco**: As tabelas `books` e `studies` já possuem os carimbos temporais necessários (`created_at`, `updated_at`, `deleted_at`). Não são necessárias migrações Alembic no banco ativo `caderno.db`.
2. **Desempenho Instantâneo**: Em um caderno pessoal (centenas a poucos milhares de registros), consultas de agrupamento por data com índices em `deleted_at` executam em menos de 5ms no SQLite.
3. **Consistência Atômica**: Ao mover um livro ou estudo para a lixeira (ou restaurá-lo), as métricas e o mapa de calor são imediatamente refletidos sem risco de dessincronização entre tabelas de histórico e registros reais.

### Alternativas Rejeitadas
- *Tabela de log de auditoria/eventos (`activity_events`)*: Rejeitada pois exigiria migração de schema (Alembic), triggers ou interceptores de sessão, além de rotinas complexas de backfill e sincronização de soft-delete.
- *Processamento 100% no cliente carregando todos os livros e estudos*: Rejeitada pois transmitiria o conteúdo integral de todos os estudos para o navegador apenas para calcular totais, desperdiçando memória e largura de banda.

---

## 2. Decisão 2: Tratamento de Fuso Horário e Agrupamento por Dia Civil

### Contexto
Os instantes de criação e alteração são gravados em UTC canônico (`UTCDateTime`). Um estudo concluído às 22:30 no fuso de Brasília (UTC-3) corresponde a 01:30 do dia seguinte em UTC. O leitor espera ver a atividade computada no dia em que efetivamente leu.

### Decisão
1. O backend expõe o parâmetro opcional `?tz_offset=minutos` (ex.: `-180` para UTC-3, obtido no frontend via `new Date().getTimezoneOffset()`).
2. No SQLite, a conversão para a data local utiliza `date(datetime(column, printf('%+d minutes', -tz_offset)))`.
3. As datas agrupadas são retornadas no formato ISO `YYYY-MM-DD`.
4. Os itens da timeline mantêm o timestamp ISO 8601 UTC canônico, e o frontend formata a exibição relativa/absoluta utilizando `Intl.DateTimeFormat` no fuso local do navegador.

### Justificativa
- Garante exatidão cronológica rigorosa tanto em consultas de mesa quanto em acessos móveis via rede privada/Tailscale.
- Elimina discrepâncias entre o mapa de calor e a data real de estudo do usuário.

### Alternativas Rejeitadas
- *Agrupamento em UTC puro*: Rejeitada pois moveria artificialmente estudos noturnos para o dia civil seguinte, confundindo o usuário.
- *Fuso horário fixo configurado no servidor*: Rejeitada pois dispositivos com fusos diferentes ou em viagem veriam marcações incorretas.

---

## 3. Decisão 3: Arquitetura Visual do Mapa de Calor e Harmonia com Superclasses

### Contexto
O mapa de calor de semanas/dias precisa suportar 4 níveis de intensidade visual sem conflitar com os 10 temas de cor (Porcelana, Breu, Pergaminho, E-Ink, etc.) nem com as 5 Superclasses de Interface (Zero-G, Mecânica, Invisível, Dimensional, Monolítica).

### Decisão
Construir o heatmap em componente Vue nativo (`HeatmapCalendar.vue`) estilizado via CSS custom properties dinâmicas:
1. Níveis de intensidade definidos com `color-mix`:
   - `.level-0`: Fundo neutro do contêiner (`var(--color-surface-soft)`).
   - `.level-1`: `color-mix(in srgb, var(--color-accent) 25%, var(--color-surface))`
   - `.level-2`: `color-mix(in srgb, var(--color-accent) 60%, var(--color-surface))`
   - `.level-3`: `var(--color-accent)`
2. Para o tema `e-ink`, utilizar escala monocromática (tons de cinza e borda sólida).
3. Herdar as propriedades geométricas e físicas da Superclasse ativa (`border-radius: var(--sc-border-radius)`, microinterações nos botões e tooltips).

### Justificativa
- Zero dependências externas (sem D3.js ou Chart.js), preservando o bundle leve e rápido do Vite.
- Adaptação instantânea a qualquer troca de tema cromático ou superclasse em Ajustes sem recarregar a página.

### Alternativas Rejeitadas
- *Bibliotecas de gráficos externas (Chart.js / ApexCharts / ECharts)*: Rejeitadas pois aumentariam o bundle em mais de 200KB, complicariam a estilização com CSS custom properties e criariam conflito com o isolamento das superclasses.

---

## 4. Decisão 4: Adaptação Responsiva do Calendário (Desktop vs Mobile)

### Contexto
Um calendário de 52 semanas requer cerca de 750px a 900px de largura mínima para exibir células de 12px a 14px com espaçamento legível. Em smartphones (320px a 480px), tentar comprimir 52 colunas tornaria as células microscópicas e inacessíveis ao toque.

### Decisão
Implementar um corte temporal adaptativo inteligente:
1. **Desktop (> 768px)**: Exibe a janela anual completa dos últimos 12 meses (~52 semanas).
2. **Mobile (<= 768px)**: Exibe por padrão os últimos 4 meses (~17 semanas), garantindo células confortáveis ao toque (mínimo 18px x 18px com espaçamento de 3px).
3. **Controle de Alternância**: Botão "Ver ano completo" no cabeçalho do calendário que ativa rolagem horizontal fluida caso o usuário queira inspecionar o ano todo no celular.

### Justificativa
- Atende 100% à decisão de clarificação Q2 (Opção C).
- Proporciona excelente experiência de toque em telas móveis sem perder a riqueza de dados do desktop.
