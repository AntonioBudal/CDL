# Especificações de Produto (Spec Kit) — Document Intelligence

Este diretório armazena as especificações técnicas, planos de implementação e decomposição de tarefas gerados através do **GitHub Spec Kit** para os componentes de produto do subsistema `document-intelligence/`.

---

## 1. Relação com os Experimentos (`experiments/`)

No Document Intelligence, **experimentos não são especificações de produto**:
- O diretório `experiments/` acolhe hipóteses exploratórias, benchmarks e provas de conceito (PoC).
- Quando um experimento demonstra viabilidade técnica, atende aos critérios de aceite e tem sua decisão arquitetural registrada via ADR em `docs/adr/`, cria-se uma especificação formal aqui em `specs/` usando o Spec Kit.

---

## 2. Estrutura Padrão de uma Feature

Cada entrega de funcionalidade em `specs/` segue a convenção canônica do Spec Kit:

```text
specs/
└── XXX-nome-da-feature/
    ├── spec.md             # Requisitos de usuário, user stories e critérios de aceite
    ├── plan.md             # Arquitetura técnica, data models e dependências
    ├── tasks.md            # Tarefas atômicas de implementação sequenciadas
    ├── research.md         # Pesquisa de suporte e consolidação técnica (opcional)
    ├── data-model.md       # Estruturas de dados e schemas envolvidos (opcional)
    ├── quickstart.md       # Guia executável de validação de aceitação
    └── contracts/          # Definições de interfaces e schemas (ex.: OpenAPI, JSON Schema)
```

---

## 3. Workflow de Execução com Spec Kit

O Claude Code deve utilizar os comandos do Spec Kit correspondentes à versão instalada (`specify 1.0.1`):

```text
speckit.specify   → Criação da especificação funcional (spec.md)
speckit.clarify   → Resolução de ambiguidades e edge cases
speckit.plan      → Planejamento técnico e arquitetural (plan.md)
speckit.tasks     → Geração da lista de tarefas orientada a dependências (tasks.md)
speckit.analyze   → Checagem de consistência contra a Constituição do projeto
speckit.implement → Execução atômica das tarefas descritas em tasks.md
```
