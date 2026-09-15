# Constituição do Projeto Caderno de Leitura

Este documento estabelece as regras fundacionais, restrições arquiteturais e diretrizes de governança técnica para a evolução contínua do **Caderno de Leitura**.

---

## Princípios Fundamentais

### I. Proteção Absoluta do Acervo e Privacidade de Dados
1. **Dados Pessoais e Acervo:** O acervo do usuário (livros cadastrados, capítulos, anotações pessoais, respostas importadas e metadados) é estritamente privado. É proibido ler, listar, resumir ou transmitir trechos do acervo real em prompts, chats de agentes, logs versionados ou repositórios públicos.
2. **Preservação de Registros:** Toda evolução técnica deve preservar chaves primárias (`id`), datas de criação/atualização, relacionamentos e o texto original importado (`source_response`).
3. **Proteção contra Sobrescrita Silenciosa:** Alterações concorrentes (ex.: PC e celular) não devem causar perda silenciosa de dados. Conflitos de escrita devem ser detectados e a edição local preservada para recuperação pelo usuário.

### II. Isolamento Estrito de Testes e Operações Locais
1. **Zero Impacto no Acervo Ativo:** Nenhuma suíte de testes (backend ou frontend) pode ler, gravar ou conectar-se ao arquivo de banco ativo (`backend/data/caderno.db`).
2. **Bancos Descartáveis:** Testes de banco ou de API devem instanciar bancos SQLite efêmeros em diretórios temporários (`tmp_path`), aplicando migrações e descartando os arquivos ao final.
3. **Servidores Efêmeros:** Testes de integração de servidor local devem utilizar portas de rede efêmeras (porta 0/aleatória) e variáveis de ambiente explícitas (`CADERNO_DATABASE_PATH`), sem disputar a porta 8000 do caderno ativo.

### III. Fidelidade Arquitetural e Tecnológica
1. **Backend:** Python 3.13 de 64 bits no Windows. Framework FastAPI, ORM SQLAlchemy 2.0 (mapeamento declarativo moderno), migrações gerenciadas via Alembic e servidor Uvicorn.
2. **Frontend:** Vue 3 (Composition API, `<script setup>`), TypeScript em modo estrito, Vite para build e empacotamento, biblioteca `markdown-it` para renderização segura e suporte a tipografia local (EB Garamond, Source Sans 3, OpenDyslexic).
3. **Persistência:** SQLite local em modo Write-Ahead Logging (WAL) quando apropriado. Chaves estrangeiras (`PRAGMA foreign_keys = ON`) ativadas em todas as conexões.
4. **Execução Local Única:** A aplicação funciona como um servidor local único orquestrado via `iniciar.py`, atendendo requisições da interface empacotada (`dist/`) e da API REST (`/api`), sem dependência de nuvem pública ou APIs pagas de terceiros.

### IV. Governança por Especificação Delimitada (Spec-Driven Development)
1. **Fatias Pequenas e Verificáveis:** O desenvolvimento é orientado a especificações formais utilizando o GitHub Spec Kit (`agy`). Nenhuma feature deve tentar "fazer tudo de uma vez".
2. **Ciclo Formal de SDD:** O fluxo obrigatório para cada entrega consiste em:
   - `speckit.specify`: Definição de escopo, comportamento e critérios de aceite mensuráveis.
   - `speckit.clarify`: Resolução prévia de ambiguidades funcionais ou de interface.
   - `speckit.plan`: Desenho técnico respeitando os caminhos auditados e contratos do sistema.
   - `speckit.tasks`: Decomposição em tarefas atômicas e sequenciadas.
   - `speckit.analyze`: Verificação de conformidade com esta Constituição.
   - `speckit.implement`: Execução das alterações sob demanda do usuário.
3. **Regra de Estado do Roadmap:** As dez tarefas do Roadmap 0.3 (T01 a T10) estão estritamente **NÃO INICIADAS**. A presença de rascunhos, patches ou código prévio não valida avanço de entrega.

### V. Resiliência Operacional, Transações e Migrações Seguras
1. **Backup Pré-Migração:** Antes de qualquer migração de schema arriscada, um backup consistente do acervo deve ser gerado e validado.
2. **SQLite Backup API:** O backup e snapshot do SQLite devem utilizar a API oficial de backup online (`sqlite3.Connection.backup`), garantindo consistência atômica mesmo sob conexões simultâneas ou arquivos WAL ativos.
3. **Atomicidade de Restauração:** A restauração de pacotes ou cópias de segurança deve ser executada em diretório intermediário, com validação de integridade (`PRAGMA quick_check`, `PRAGMA foreign_key_check`) e substituição segura, preservando o estado anterior caso a operação seja interrompida.
4. **Contratos de Configuração Unificados:** `iniciar.py`, `backend/app/core/config.py`, Alembic e scripts de manutenção devem respeitar rigidamente os mesmos contratos de resolução de caminhos e a variável `CADERNO_DATABASE_PATH`.

---

## Padrões de Desenvolvimento

### Backend (Python/FastAPI)
- Respeito às dependências fixadas em `requirements.txt` e `requirements-dev.txt`.
- Schemas Pydantic v2 para validação de entrada/saída de rotas.
- Tratamento de erros com mensagens claras em português e códigos HTTP semanticamente corretos.
- Sem vazamento de caminhos internos ou dados sensíveis em stack traces expostos na API.

### Frontend (Vue/TypeScript)
- Componentes organizados com responsabilidades claras (views, componentes reutilizáveis, composables para lógica de estado).
- Proteção contra perda de dados não salvos (`useUnsavedChanges`).
- Acessibilidade visual (contraste, tamanhos de toque para telas móveis, suporte a preferências de movimento reduzido e temas de alto contraste/E-Ink).
- Suporte a navegação por teclado e foco consistente.

---

## Governança

1. **Precedência:** Esta Constituição tem precedência sobre qualquer convenção implícita ou sugestão externa.
2. **Emendas:** Emendas a esta Constituição devem ser registradas em documento de histórico de decisões com a justificativa técnica.
3. **Auditoria:** Todo fechamento de ciclo ou entrega de feature deve validar o cumprimento dos artigos aqui dispostos antes do aceite final.

**Versão:** 1.0.0 | **Ratificado:** 2026-09-15 | **Autoridade:** Tech Lead Caderno de Leitura
