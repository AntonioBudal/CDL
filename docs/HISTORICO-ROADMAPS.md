# Histórico de Roadmaps e Convenção de Versionamento Git

**Projeto:** Caderno de Leitura (CDL)  
**Repositório Oficial:** [https://github.com/AntonioBudal/CDL](https://github.com/AntonioBudal/CDL)  
**Remote:** `https://github.com/AntonioBudal/CDL.git`  
**Data:** 19 de setembro de 2026  

---

## 1. Auditoria e Análise Histórica dos Roadmaps

Esta seção documenta com rigor e transparência as evidências materiais encontradas no workspace local e em backups do ambiente Windows para a reconstituição da evolução histórica do projeto Caderno de Leitura.

### Versão 0.1 — Base Inicial
- **Evidências encontradas:**
  - Pacote original arquivado e preservado em `C:\Users\User\Downloads\caderno-leitura-tarefa8-completo.zip` e diretório extraído `caderno-leitura-tarefa8-completo/caderno-leitura-0.1` (carimbo: 10/09/2026 06:41).
  - Documentos de entrega da versão: `LEIA-ME-0.1.md`, `ACEITE-0.1.md`, `VALIDACAO-0.1.md`, `PROMPT-PADRAO.md` e `MANIFESTO-SHA256.txt`.
  - Hashes criptográficos SHA-256 de cada arquivo individual registrados no manifesto oficial.
  - Declaração explícita de escopo: Tarefas 1 a 8 consolidadas; suporte exclusivo a PC local (`127.0.0.1`); sem rede móvel, sem QR Code, sem backup API, sem lixeira, sem customização visual.
- **Componentes identificados:**
  - `iniciar.py` e `instalar.py` originais de processo único local em porta 8000.
  - Backend FastAPI com models iniciais (`Book`, `Chapter`, `Study`) e migração única `0001_initial_schema.py`.
  - Frontend Vue 3 com leitura em 4 abas (Resumo, Explicação, Conceitos, Referências) e versão declarada `0.1.0-alpha.1`.
- **Grau de confiança:** **100% (Verificação Criptográfica Absoluta)**. O snapshot da 0.1 existe intacto no disco.

---

### Versão 0.2 — Acesso em Rede e Aparência
- **Evidências encontradas:**
  - Relatório de auditoria inicial de 15/09/2026 em `docs/contexto/AUDITORIA-INICIAL.md`.
  - Registro de retomada em `docs/contexto/RETOMADA.md` (sessão de 15/09/2026).
  - Cabeçalho `a/` do patch de transição `infra-0.3.patch` (criado em 13/09/2026) que atesta a versão `0.2.0-alpha.1`.
  - Documento de transição `LEIA-ME-TRANSICAO.md` confirmando a base estável pré-0.3.
- **Componentes identificados:**
  - Inicializador `iniciar.py` ampliado com flags `--host`, `--port`, `--ip` e impressão de QR Code ASCII no terminal para pareamento de celulares e tablets na rede local/Tailscale.
  - Script executável `INICIAR-REDE.cmd`.
  - Endpoint `GET /api/backup` com implementação da SQLite Online Backup API (`original.backup(snapshot)`).
  - Primeira camada do motor de aparência (`appearance-bootstrap.js`, `window.cadernoAppearance`, seletores de densidade, tamanho tipográfico e temas claro/escuro/sépia/e-ink).
- **Grau de confiança:** **Alto com Inferência Estrutural Documentada**. Não havia um zip congelado com o rótulo "0.2", mas o estado base 0.2 está documentado com precisão nos relatórios de auditoria e no cabeçalho pré-patch de 13–15/09/2026.

---

### Versão 0.3 — Gestão, Visualização e Produtividade
- **Evidências encontradas:**
  - `ROADMAP-0.3.md` (10 tarefas: T01 a T10).
  - Especificações Spec Kit completas: `specs/001` a `specs/016` (tarefas atômicas e planos).
  - Migrações Alembic incrementais correspondentes:
    - `0002_add_book_metadata_and_concurrency.py` (T01: Edição de livros, capítulos e concorrência HTTP 409)
    - `0003_add_trash_soft_delete.py` (T02: Lixeira transacional, `deleted_at` e purga de 30 dias)
    - `0004_add_book_cover_image.py` (T03: Capas persistentes por upload e URL via Pillow)
    - `0005_add_categories_and_taxonomy.py` (T05: Taxonomia de categorias hierárquicas)
  - Módulos de infraestrutura e produto:
    - `backend/app/services/maintenance.py` (T09: Snapshots atômicos pré-upgrade e rotação de 5 cópias)
    - `backend/app/services/backup_bundle.py` (T10: Backup universal ZIP com restauração e rollback)
    - `backend/app/services/dashboard_service.py` (T06: Dashboard com mapa de calor e timeline)
    - `frontend/src/styles/superclasses/` (T07: 5 Superclasses de interface — Zero-G, Mecânica, Invisível, Dimensional, Monolítica)
    - `frontend/src/views/SettingsView.vue` (T08: Central de ajustes unificada com preview)
  - Emissão do `ROADMAP-0.4.md` em 19/09/2026 marcando a conclusão formal da 0.3.
- **Componentes identificados:**
  - Todas as funcionalidades das tarefas T01 a T10 implementadas, com 102 testes de backend e 74 testes de frontend homologados.
- **Grau de confiança:** **Alto**. A fronteira exata entre 0.3 e 0.4 é demarcada de forma inequívoca pelas migrações do Alembic (0002–0005 pertencem a 0.3; 0006–0010 pertencem a 0.4) e pelas especificações Spec Kit.

---

### Versão 0.4 — Navegação Espacial, Relações e Movimento
- **Evidências encontradas:**
  - `ROADMAP-0.4.md` (10 features: F01 a F10).
  - Especificações Spec Kit completas: `specs/017` a `specs/026`.
  - Migrações Alembic incrementais da 0.4:
    - `0006_add_study_hierarchy_and_position.py` (F02: Hierarquia interativa e ordenação de estudos)
    - `0007_add_study_canvas_nodes.py` (F03: Coordenadas 2D e dimensões de cards no Canvas)
    - `0008_add_study_relations.py` (F04: Grafo semântico transversal com 6 tipos de relação)
    - `0009_add_reading_status_and_canvas_frames.py` (F05: Status de leitura e molduras manuais do Canvas)
    - `0010_add_search_history.py` (F08: Histórico recente de busca global)
  - Módulos e visualizações de produto:
    - `StudyCanvasView.vue`, `CanvasToolbar.vue`, `CanvasMinimap.vue`, `CanvasFrameNode.vue` (F03)
    - `CanvasAcceleratedLayer.vue` (F10: Camada acelerada Canvas 2D a 60fps para ≥ 60 nós)
    - `StudyTreeView.vue`, `StudyTreeNodeItem.vue` (F02)
    - `StudyMapView.vue` (F01 / F04)
    - `DashboardView.vue` 2.0 (F07)
    - `GlobalSearchModal.vue` (F08: Busca global multi-termo com snippets destacados)
    - `SplitPanes.vue` (F06: Painéis redimensionáveis)
    - `useSuperclassPhysics.ts`, `physics.css` (F10: Cinemática, inércia, micro-respostas táteis de 80ms)
    - Iconografia vetorial Lucide integrada e erradicação de emojis / alusões a IA (F09)
  - Cobertura de testes: 223 testes de frontend aprovados (`npm test`), 199 testes de backend aprovados (`pytest`), compilação de produção Vite limpa em 3.26s.
- **Grau de confiança:** **100% (Código Atual Íntegro e Validado)**.

---

## 2. Regra e Convenção de Versionamento Git

Para garantir que o histórico do Git represente com clareza a evolução arquitetural do projeto, adota-se a seguinte convenção oficial:

### Histórico Retrospectivo (0.1 a 0.4)
Nos Roadmaps 0.1 a 0.4, o versionamento é consolidado no padrão **1 commit por Roadmap**:

```
0.1 └── versão 0.1 — base inicial do acervo e estudos
0.2 └── versão 0.2 — acesso em rede local e personalização
0.3 └── versão 0.3 — gestão, visualização e produtividade
0.4 └── versão 0.4 — navegação espacial, relações e movimento
```

Cada commit representa o marco final acumulado daquele Roadmap.

---

### Novo Padrão a partir da Versão 0.5: 1 Commit por Feature
A partir do **Roadmap 0.5**, abandona-se o modelo de commits acumulados por Roadmap. Adota-se estritamente:

> **1 Commit = 1 Feature Implementada e Validada**

```
Roadmap 0.5
  ├── Feature — Base multiusuário       (1 commit)
  ├── Feature — Autenticação            (1 commit)
  ├── Feature — Conta Google            (1 commit)
  ├── Feature — Sincronização           (1 commit)
  ├── Feature — Perfil                  (1 commit)
  └── ...
```

#### Ciclo Obrigatório de Cada Feature (Spec Kit):
Nenhuma feature é commitada diretamente. O fluxo segue o ciclo completo:
1. `speckit-specify` → Especificar a necessidade em linguagem natural
2. `speckit-clarify` → Clarificar dúvidas e regras de negócio com o usuário
3. `speckit-plan` → Elaborar plano técnico e verificar a constituição
4. `speckit-checklist` → Gerar critérios de aceite
5. `speckit-tasks` → Decompor em tarefas atômicas e ordenadas
6. `speckit-analyze` → Análise de consistência entre spec, plano e tarefas
7. `speckit-implement` → Executar tarefas faseadas
8. `speckit-converge` → Verificar conformidade
9. **Validação**: Executar suítes de testes (`npm test`, `pytest`, `npm run build`)
10. **Commit da Feature**: Realizar o commit unitário da feature concluída

#### Padrão de Mensagens de Commit:
- Idioma: Português.
- Formato: Curto, simples e descritivo.
- Sem nomes artificiais, sem jargões de marketing, sem mensagens vagas.
- Exemplos:
  - `feature — base multiusuário`
  - `feature — autenticação local`
  - `feature — sincronização em nuvem`
  - `feature — perfil do leitor`
