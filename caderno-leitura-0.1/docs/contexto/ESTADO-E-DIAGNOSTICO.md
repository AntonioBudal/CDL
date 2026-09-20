# Estado e Diagnóstico da Base

## 1. Mapeamento de Caminhos e Raízes
A auditoria revelou três níveis distintos de diretórios no ambiente:
1. **Raiz do Repositório Git:** `C:\Users\User` (o Git foi inicializado no diretório de usuário do Windows, abrangendo pastas pessoais). Não há `.git` isolado dentro de `caderno` ou `caderno-leitura-0.1`.
2. **Raiz do Workspace Antigravity:** `C:\Users\User\caderno` (pasta aberta na IDE Antigravity).
3. **Raiz Real da Aplicação:** `C:\Users\User\caderno\caderno-leitura-0.1` (contém `iniciar.py`, `backend`, `frontend`, `scripts`, `exemplos`, dependências e banco).

## 2. Estado do Código e Histórico de Patches
- **Estado Atual da Base:** O código em `caderno-leitura-0.1` corresponde à consolidação estável das Tarefas 1 a 8 (Alpha 0.1) com acréscimos operacionais da 0.2:
  - Inicialização de rede com detecção de IP e QR Code (`iniciar.py`).
  - Endpoint de snapshot via SQLite Online Backup API (`backend/app/services/backups.py` e `backend/app/routers/backups.py`).
  - Frontend Vue compilado em `frontend/dist`.
- **Investigação do Patch `infra-0.3.patch`:**
  - O arquivo possui 1957 linhas e 91.852 bytes.
  - Ao ser verificado anteriormente pelo comando `git apply --check`, falhou com a mensagem: `corrupt patch at line 1957`.
  - **Diagnóstico Técnico do Erro:** A linha 1957 (`+    raise SystemExit(main())`) termina exatamente no EOF sem caractere de nova linha (`\r\n` ou `\n`) e sem a marcação canônica do diff unificado `\ No newline at end of file`. O parser do Git interpreta a ausência como truncamento do arquivo.
  - **Conclusão:** O patch **nunca foi aplicado** à base. O código em `caderno-leitura-0.1` permanece limpo e consistente com o esquema 0001.

## 3. Estado do Banco de Dados
- **Banco de Produção Ativo:** `backend/data/caderno.db`.
- **Tamanho:** 32.768 bytes (32 KB).
- **Data de Modificação:** 10/09/2026 06:48:26.
- **Arquivos WAL/SHM:** Nenhum arquivo temporário pendente (`caderno.db-wal` ou `caderno.db-shm` ausentes). O banco está em repouso e íntegro.
- **Histórico de Backups:** Foram identificados dois snapshots prévios baixados em `Downloads`:
  - `caderno-20260912-011948-844507Z.db` (32 KB)
  - `caderno-20260912-185023-785402Z.db` (32 KB)

## 4. Migrações e Esquema Atual
- Diretório de migrações: `backend/migrations/versions/`.
- Única versão registrada: `0001_initial_schema.py` (cria tabelas `books`, `chapters` e `studies`).
- Nenhuma migração da versão 0.3 (como a proposta `0002_integrity.py` presente no patch corrompido) foi aplicada ou registrada na tabela `alembic_version`.

## 5. Status do Roadmap 0.3
- **REGRA DE ESTADO INVIOLÁVEL:** Todas as dez tarefas (T01 a T10) estão estritamente **NÃO INICIADAS**.
- Rascunhos de código ou o patch não aplicado não concedem progresso.
- Nenhum trabalho de implementação de banco ou infraestrutura 0.3 foi iniciado nesta rodada.

## 6. Superclasses de Interface (Frontend)
- **Superclasse Zero-G (`.superclass-zero-g`)**: Físicas de levitação suave, sombra difusa e atração magnética implementadas em `zero-g.css`.
- **Superclasse Mecânica (`.superclass-mecanica`)**: Física tátil de resposta imediata, cantos secos, push-down e corte seco de rota implementadas em `mecanica.css`.
- **Superclasse Invisível (`.superclass-invisivel`) & Poda de Ajustes**: Estética editorial limpa, desmaterialização de caixas/sombras, microinterações de leitura (`translateX(4px)` e sublinhado progressivo) e transição de rota em cascata temporal (*staggered fade-up*) implementadas em `invisivel.css`. Controles legados de formato de caixas (`style`), contraste de cartões (`surface`) e preenchimento de botões (`button-style`) podados da tela de Ajustes e catalogo com normalização tolerante e retrocompatível no cliente.
- **Superclasse Dimensional (`.superclass-dimensional`)**: Física cinemática e profunda, perspectiva óptica de 1000px, tilt 3D microcontrolado delimitado nos cartões (rotateX: ±1.5°, rotateY: ±2.0°), sombras dinâmicas projetadas opostas ao cursor, relevo multicamada interno escalonado (capa 1px, título 2px, marcadores/badges 3px), botões dimensionais com elevação Z e transição de rota cinemática em aproximação Z (`scale(0.985) → scale(1.0)` em ~300ms) implementadas em `dimensional.css` com blindagem absoluta de leitura e neutralização universal por acessibilidade.
- **Superclasse Monolítica (`.superclass-monolitica`)**: Estética de arquitetura brutalista em pedra e arquivo perpétuo, cantos estritamente retos (`border-radius: 0px !important`), supressão total de sombras difusas (`box-shadow: none !important`), relevo demarcado por bordas estruturais sólidas (`calc(var(--border-width, 1px) + 1px)`), microinterações solenes (~380ms), inversão brutalista de alto contraste no clique (`:active`), transição de rotas por dissolução lapidar em opacidade (~380ms) e blindagem estrita de leitura implementadas em `monolitica.css`.

## 7. Roteamento, Fonte Global e Limpeza de Ajustes (Feature 012)
- **Roteamento Estável sem Telas Vazias**: Corrigida a montagem do `<RouterView>` via `:key="$route.fullPath"` sob `<Transition mode="out-in">` em `App.vue` e garantido invólucro de elemento raiz único nas 5 visualizações (`BooksView`, `BookView`, `StudyView`, `StudyEditView`, `ImportView`), eliminando falhas silenciosas de montagem client-side.
- **Aplicação Global da Fonte**: Elevada a variável `--font-reading` para `--font-ui` em `tokens.css` e aplicada regra global irrestrita `font-family: var(--font-reading)` a `:root, body, #app, button, input, select, textarea, code, pre` em `style.css`, proporcionando preview fidedigno e instantâneo em toda a casca da aplicação.
- **Poda de Ajustes e Renumeração Sequencial**: Purgadas as opções obsoletas `motion`, `button-width` e `tabs` absorvidas pelas Superclasses. Catálogo reestruturado para exatos 7 grupos numerados (1 a 7). Bootstrap versionado em 72 com purga atômica no `localStorage` (`caderno.aparencia.v2`) e remoção dos atributos do DOM `<html>`.

## 8. Dashboard de Leitura com Calendário e Timeline (Feature 013 - T06 do Roadmap 0.3)
- **Métricas Consolidadas e Agregação Segura**: Indicadores em tempo real de total de livros ativos, total de estudos, total de dias de leitura, média ponderada por livro e sequência de dias ativos (streak) calculados via agregação direta sobre `books` e `studies` sem necessidade de novas tabelas ou migrações no SQLite.
- **Mapa de Calor em Calendário**: Componente `HeatmapCalendar.vue` com grade cronológica de semanas/dias, 4 níveis de intensidade harmonizados com as Superclasses via `color-mix`, modo monocromático para o tema E-Ink, tooltips contextuais e recorte responsivo adaptativo (12 meses desktop vs 3 a 4 meses mobile com alternância).
- **Linha do Tempo e Filtro Integrado**: Linha do tempo cronológica reversa de atividades recentes (criação de livros, criação de estudos e edição de anotações) com atalhos diretos de leitura e filtragem instantânea por data ao clicar na célula do mapa de calor.
- **Isolamento da Lixeira**: Exclusão estrita e imediata de itens descartados (soft delete), com restauração atômica dos pontos históricos.

