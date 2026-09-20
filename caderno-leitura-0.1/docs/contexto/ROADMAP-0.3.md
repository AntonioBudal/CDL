# Roadmap 0.3 — Gestão, Visualização e Produtividade

Data: 2026-09-15. **Nenhuma tarefa começou.** Os requisitos e recomendações abaixo são planejamento de transição. Código legado ou propostas anteriores não atribuem avanço.

## Quadro oficial

| ID | Entrega | Status |
| --- | --- | --- |
| T01 | Edição completa de livros e estudos | NÃO INICIADA |
| T02 | Lixeira e restauração de itens | NÃO INICIADA |
| T03 | Capas por upload e URL | NÃO INICIADA |
| T04 | Visualização, busca e ordenação do acervo | NÃO INICIADA |
| T05 | Categorias pesquisáveis e taxonomia | NÃO INICIADA |
| T06 | Dashboard com calendário e timeline | NÃO INICIADA |
| T07 | Exportação de anotações em TXT/Markdown | NÃO INICIADA |
| T08 | Central de ajustes com preview | NÃO INICIADA |
| T09 | Integridade do banco, migrações e concorrência | NÃO INICIADA |
| T10 | Backup completo, restauração e operação confiável | NÃO INICIADA |

As checklists de aceite também começam desmarcadas. Somente uma solicitação futura de execução pode iniciar uma tarefa. O relatório de auditoria não altera este quadro.

## T01 — Edição completa de livros e estudos

**Status: NÃO INICIADA.**

Permitir editar título, autor e metadados de livros e editar estudos/anotações anteriores. Reaproveitar a edição existente quando comprovada no código; não reconstruir um fluxo já funcional.

Implementar contratos de atualização coerentes com a API real, validação e telas/modais Vue. Definir explicitamente quais novos metadados são necessários. A edição de capítulos, caso incluída, deve cobrir nome e posição.

A ação “excluir” usa a lixeira de T02. Não entregar primeiro uma exclusão destrutiva provisória.

- [ ] Alterações persistem após recarregar e não alteram o texto original importado.
- [ ] Validações preservam o formulário e o texto digitado.
- [ ] Conflito de edição entre dispositivos não sobrescreve alterações silenciosamente.
- [ ] Fluxo utilizável em PC/celular e por teclado.
- [ ] IDs e vínculos permanecem válidos após editar.

Dependências: contratos de T09; exclusão alinhada com T02.

## T02 — Lixeira / soft delete

**Status: NÃO INICIADA.**

Usar timestamp anulável de exclusão, com convenção de fuso documentada, em vez de um booleano ambíguo. Cobrir livros e estudos; decidir o comportamento de capítulos antes da migração.

Itens excluídos e descendentes de ancestrais excluídos deixam o acervo ativo. Consultas diretas, edição, busca, importação, exportação e dashboard devem respeitar essa visibilidade.

Restaurar um livro não deve ressuscitar um estudo excluído separadamente antes dele. Definir a ordem de restauração de ancestrais e filhos e eventuais conflitos. Exclusão definitiva é uma operação distinta, deliberada e confirmada na interface.

- [ ] Enviar à lixeira e restaurar preserva conteúdo, IDs e relacionamentos.
- [ ] Acesso por URL direta não permite editar registros ocultos.
- [ ] Exclusão definitiva é transacional e não deixa registros órfãos.
- [ ] Identificadores antigos não passam a apontar para outros objetos.
- [ ] Backup inclui a lixeira; consultas normais a excluem.

Dependências: migração de T09 e edição de T01 coordenadas.

## T03 — Capas por upload e URL

**Status: NÃO INICIADA.**

Adicionar upload pelo PC/celular e importação de uma URL direta de imagem. Uma página de resultados do Google Imagens não é uma URL direta; mostrar orientação compreensível.

**Ajuste de arquitetura recomendado:** armazenar capas em diretório persistente, por exemplo `backend/data/covers` ou subdiretório do local de dados configurado. Não usar `frontend/public` ou `frontend/dist` para uploads, pois assets de build são substituíveis. Servir as imagens por rota controlada e guardar referência relativa no banco.

Validar tamanho, formato e dimensões; gerar nomes seguros e impedir caminhos arbitrários. Para baixar URLs no servidor, especificar proteção contra destinos locais/privados, redirecionamentos inseguros, arquivos excessivos e timeouts. Definir formatos aceitos; não aceitar SVG/HTML arbitrário como capa.

- [ ] Upload e URL válida geram capa local exibida em PC/celular.
- [ ] Link inválido ou imagem rejeitada mantém a capa anterior.
- [ ] Rebuild e atualização preservam os arquivos.
- [ ] Troca/exclusão não remove arquivo ainda referenciado ou necessário à lixeira.
- [ ] Backup e restauração de T10 preservam as capas e seus vínculos.

Dependências: diretório persistente de T09; contrato de pacote de T10.

## T04 — Acervo: visualização, busca e ordenação

**Status: NÃO INICIADA.**

Alternar entre capas grandes em grade e texto compacto/retrátil em lista. Reutilizar a preferência estrutural de acervo existente, com migração se precisar ampliar seus valores.

Adicionar pesquisa por título/autor e ordenação A–Z/mais recentes. Definir se “recente” significa inclusão ou edição, e criar o campo necessário de forma explícita; o modelo de livro de referência não possui data própria.

Filtro no frontend só é completo quando todos os dados relevantes estão carregados. Se houver paginação, a busca e a ordenação devem ser globais no servidor.

- [ ] Modos compartilham os mesmos registros e ações.
- [ ] Pesquisa/ordenação combinadas são previsíveis, inclusive com acentos.
- [ ] Sem capa há fallback legível; texto longo não rompe o layout.
- [ ] Escolha persiste e convive com densidade, tema e largura.
- [ ] Itens da lixeira não aparecem no acervo ativo.

Dependências: T02; capas de T03 para o modo visual completo. Não confundir esta busca com FTS global de todos os estudos.

## T05 — Categorias e taxonomia

**Status: NÃO INICIADA.**

Fornecer JSON com mais de 100 categorias úteis e nomes em português, incluindo hierarquia. Usar identificadores estáveis, rótulos e relação de categoria pai.

Criar seleção pesquisável com sugestão por digitação e caminho da categoria. A escolha entre uma ou várias categorias por livro precisa ser definida na especificação; recomendação: várias categorias, com relação muitos-para-muitos.

- [ ] Catálogo contém mais de 100 entradas válidas, sem ciclos nem duplicação de IDs.
- [ ] Importar/atualizar o catálogo é idempotente e preserva vínculos.
- [ ] Busca encontra nomes e apresenta a hierarquia sem ambiguidade.
- [ ] Livro preserva categorias ao editar outros campos.
- [ ] Exportações e backups conservam categorias e relações.

Dependências: migrações de T09 e edição de T01. Sem geração de categorias por IA em tempo de uso.

## T06 — Dashboard: calendário e timeline

**Status: NÃO INICIADA.**

Nova visão de produtividade com mapa de calor por dia e atividade recente. Especificar o que conta como atividade antes de implementar a consulta.

`created_at` de um estudo mede criação, não todas as sessões de estudo. Recomenda-se iniciar com eventos explícitos de criação/edição e comunicar essa métrica; leitura cronometrada só entra se for pedida. Guardar instantes em UTC e agrupar no fuso definido para a interface.

- [ ] Um mesmo evento não é contado duas vezes por retry ou recarga.
- [ ] Recarregar, trocar tema e navegar não geram atividade artificial.
- [ ] Calendário e timeline usam a mesma definição e fuso.
- [ ] Há estados vazios e visualização legível no celular.
- [ ] Regras para lixeira, restauração e exclusão definitiva são documentadas e testadas.

Dependências: T01/T02 para os eventos e T09 para persistência. Não apresentar estatística antiga inventada; se houver backfill, identificar sua origem.

## T07 — Exportação de anotações

**Status: NÃO INICIADA.**

Exportar o que o usuário escreveu sobre um livro em `.txt` e `.md`. Permitir exportação individual do estudo se encaixar no mesmo fluxo.

Organizar por livro, capítulo e estudo, com título e localização. Definir a inclusão das quatro seções e da resposta original; recomendação: anotações sempre incluídas, demais conteúdos com seleção explícita.

- [ ] Arquivo UTF-8 preserva acentos, quebras de linha e conteúdo original das notas.
- [ ] Ordem é estável e nomes de arquivo funcionam no Windows.
- [ ] Download funciona pelo PC e pelo celular.
- [ ] Itens da lixeira ficam de fora por padrão.
- [ ] Categorias/metadados incluídos são consistentes; nenhuma referência é inventada.

Dependências: T02; compatibilidade com T05. Exportar texto não substitui backup restaurável.

## T08 — Central de ajustes com preview

**Status: NÃO INICIADA.**

Organizar Ajustes em Aparência, Leitura e Sistema. Exibir amostra de cartão e texto que reflita imediatamente os mesmos tokens da aplicação.

Preservar as dez paletas, seletor pesquisável de fontes locais, dimensões estruturais, tamanho e foco. A preview da capa/lista usa a preferência real de T04.

- [ ] Cada controle tem rótulo e efeito visível na amostra e na interface.
- [ ] Preferências antigas e valores inválidos são tratados sem apagar escolhas válidas.
- [ ] Recarregar aplica preferências antes da montagem e evita flash de tema/layout incorreto.
- [ ] E-Ink e redução de movimento mantêm precedência.
- [ ] Teclado, foco e tamanho de toque são adequados.
- [ ] Sistema informa claramente o alcance de backup e de preferências por navegador.

Dependências: preferências existentes auditadas, T04 e controles de operação de T10.

## T09 — Infraestrutura: integridade, migrações e concorrência

**Status: NÃO INICIADA.**

Centralizar caminhos/configuração e tornar previsível a evolução do banco existente. Preservar `CADERNO_DATABASE_PATH` quando encontrado e definir diretório persistente para arquivos relacionados.

Rever Alembic, transações, chaves estrangeiras por conexão e tratamento de banco ocupado. Planejar controle de concorrência otimista para impedir perda de edição entre PC e celular, por versão do registro ou contrato equivalente.

- [ ] Atualização preserva IDs, vínculos, notas, resposta original e datas.
- [ ] Migração falha com diagnóstico claro, sem recriar a base nem deixar sucesso enganoso.
- [ ] Backup consistente anterior é criado/verificado antes de migração arriscada.
- [ ] Diretório inicial do terminal não muda qual banco é usado.
- [ ] Chaves estrangeiras são aplicadas em toda conexão relevante.
- [ ] Escritas concorrentes têm resultado definido; conflito preserva a edição local para recuperação.
- [ ] API, instalador, iniciador e manutenção compartilham a configuração.
- [ ] Testes cobrem banco anterior, restrições, transações e conflitos em base descartável.

T09 e T10 devem definir interfaces juntas. T09 precisa da **primitiva mínima de backup** de T10; não depende da conclusão de toda a UI de restauração.

## T10 — Infraestrutura: backup, restauração e operação

**Status: NÃO INICIADA.**

Definir backup consistente do SQLite, pacote completo com manifesto de versão e arquivos persistentes, restauração verificável e rotina operacional simples.

Reaproveitar a função de snapshot da 0.2 se validada. Não copiar apenas o `.db` ativo ignorando WAL. Definir checksums, limites de arquivo e validação de caminhos ao extrair pacotes. O snapshot de dados e a seleção das capas devem representar um estado coerente.

- [ ] Backup é restaurável e inclui banco, lixeira, categorias e capas quando existirem.
- [ ] Pacote corrompido, incompatível ou com caminhos inseguros é rejeitado antes de afetar o acervo.
- [ ] Restauração valida em área temporária e exige servidor sem acesso concorrente.
- [ ] Falha/interrupção mantém uma rota de recuperação para o estado anterior.
- [ ] Rotação de backups automáticos não remove os manuais; frequência e retenção são configuráveis e documentadas.
- [ ] Inicialização evita segunda instância acidental e diagnostica porta ocupada.
- [ ] Logs registram operação/erro sem textos do acervo ou segredos.
- [ ] Preferências locais têm alcance explicado; se exportadas, usam formato separado e validado.
- [ ] Teste de ida e volta comprova equivalência de conteúdo e relacionamentos.

Dependência coordenada com T09. A UI de backup pode ser refinada em T08 sem bloquear a fundação de recuperação.

## Ordem de execução proposta

1. Auditoria e integração do contexto; sem início de tarefa.
2. Especificar T09/T10 em conjunto: primeiro snapshot mínimo verificável, depois configuração/migrações/concorrência e pacote/restauração/operação. Evitar dependência circular entre tarefas inteiras.
3. T02 e T01 coordenadas: sem etapa intermediária com exclusão definitiva como comportamento padrão.
4. T03 e T05.
5. T04.
6. T06 e T07.
7. T08 e validação integrada da versão.

Esta é uma sequência recomendada, não um registro de execução. A numeração das features do Spec Kit deve ser escolhida depois de inspecionar o workspace; não precisa coincidir com T01–T10.

## Fechamento futuro da 0.3

- [ ] Todas as entregas têm critérios atendidos e evidências registradas.
- [ ] Upgrade ensaiado em cópia consistente da versão realmente instalada.
- [ ] Fluxo de importação, edição, lixeira/restauração, pesquisa e exportação validado.
- [ ] Temas, fontes e foco mantidos em PC/celular.
- [ ] Backup completo restaurado com sucesso em ambiente isolado.
- [ ] Alteração salva no celular aparece ao recarregar no PC.
- [ ] Acesso Tailscale pelo celular em 4G verificado pelo usuário ou por evidência real.
- [ ] Limitações restantes estão explícitas e não há perda silenciosa de dados.
