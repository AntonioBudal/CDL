# Leitorum Document Intelligence

> Subsistema autônomo de inteligência documental e visão computacional para o ecossistema **Leitorum**.

---

## 1. O que é o Leitorum Document Intelligence?

O **Leitorum Document Intelligence** (`leitorum_di`) é um subsistema dedicado à transformação de fotografias e digitalizações de páginas de cadernos de estudo (manuscritas, impressas ou mistas) em **conteúdo estruturado, semanticamente enriquecido e navegável**.

O objetivo não é um OCR genérico ou superficial que apenas extrai um fluxo linear de texto bruto. Cadernos de anotações possuem hierarquia espacial bidimensional complexa, incluindo:
* Títulos, tópicos e parágrafos cursivos.
* Conceitos, explicações, resumos e citações.
* Diagramas, fluxogramas, setas direcionais e relações entre blocos.
* Notas marginais e correções manuscritas.

---

## 2. Pipeline Conceitual de Ponta a Ponta

```text
Foto da Página
      ↓
Pré-processamento (deskew, normalização, iluminação)
      ↓
Detecção da Página / Layout Analysis
      ↓
Segmentação em Linhas, Blocos e Regiões
      ↓
OCR / HTR (Handwritten Text Recognition)
      ↓
Reconstrução Espacial e Ordem de Leitura
      ↓
Análise Estrutural e Agrupamento
      ↓
Classificação Semântica (conceito, pergunta, citação, etc.)
      ↓
Reconhecimento de Diagramas / Fluxogramas (nós e arestas)
      ↓
Leitorum Document Format (LDF 1.0)
      ↓
Consumo pelo Produto Leitorum
```

---

## 3. Separação de Responsabilidades e Fronteira entre Agentes

O repositório é governado por uma separação estrita de escopo entre agentes autônomos:

```text
leitorum/
├── frontend/                  # Exclusivo do Antigravity (Vue 3 / TypeScript)
├── backend/                   # Exclusivo do Antigravity (FastAPI / SQLite)
└── document-intelligence/     # Exclusivo do Claude Code (Python / uv / HTR / CV)
```

* **Claude Code:** Responsável exclusivo por todo o ciclo técnico dentro de `document-intelligence/` (modelos, inferência, visão computacional, experimentos, LDF e testes do domínio).
* **Antigravity:** Responsável pelo produto principal (`frontend/` e `backend/`). O Antigravity não implementa algoritmos de visão ou HTR.
* **Fronteira Inviolável:** Nenhuma dependência direta de código é permitida entre `document-intelligence/` e o backend/frontend do Leitorum. A integração ocorre exclusivamente através do contrato **LDF (Leitorum Document Format)** e da API HTTP local.

---

## 4. Quickstart para Desenvolvimento

O projeto utiliza **`uv`** como gerenciador de dependências e ambiente Python:

### 4.1. Sincronizar Dependências e Criar Ambiente Virtual
```powershell
cd document-intelligence
uv sync
```

### 4.2. Executar a Suíte de Testes
```powershell
uv run pytest
```

### 4.3. Executar Linter e Checagem de Estilo
```powershell
uv run ruff check .
```

---

## 5. Estrutura de Diretórios

```text
document-intelligence/
├── AGENTS.md                  # Manual de operações e governança do Claude Code
├── CLAUDE.md                  # Instruções de sessão e comandos rápidos para o Claude
├── README.md                  # Este documento (visão geral do subsistema)
├── pyproject.toml             # Gerenciamento de projeto e dependências (uv/hatchling)
├── .gitignore                 # Isolamento de .venv, pesos binários e dados privados
│
├── .specify/                  # Configuração do GitHub Spec Kit
│   └── memory/
│       └── constitution.md    # Os 8 Princípios Inegociáveis da Constituição
│
├── specs/                     # Especificações funcionais e técnicas de features
├── docs/                      # Documentação técnica e contratos de arquitetura
│   ├── adr/                   # Architecture Decision Records (padrão MADR)
│   ├── ldf.md                 # Especificação do Leitorum Document Format 1.0
│   ├── api-local.md           # Contrato HTTP de integração Leitorum ↔ DI (Draft)
│   ├── dataset-and-evaluation.md # Diretrizes de dados, writer-split e LGPD
│   ├── metrics.md             # Definições matemáticas de CER, WER, IoU, F1
│   ├── models-and-licensing.md # Matriz de modelos e auditoria de licenças de pesos
│   ├── roadmap-experiments.md # Roteiro sequencial de experimentos (EXP-000 a EXP-006)
│   ├── ldf-examples/          # Payloads de exemplo válidos do LDF
│   └── schemas/               # JSON Schema oficial do LDF 1.0
│
├── experiments/               # Rastreamento de pesquisa e experimentos
│   ├── EXP-000/               # Fundação de ambiente e reprodutibilidade (ACEITO em 2026-09-30)
│   ├── EXP-001/               # HTR de linhas isoladas: spec, plano, harness, RESULTS.md (ACEITO em 2026-10-02)
│   ├── EXP-002/               # Layout e segmentação: spec, plano, harness, RESULTS.md (AGUARDANDO ACEITE)
│   └── EXP-001-context.md     # Contexto original do EXP-001
│
├── dataset/                   # Gestão de dados sintéticos (dados reais NUNCA versionados)
│   └── fixtures/              # Casos de teste puramente sintéticos para CI/testes
│
├── models/                    # Diretório local para checkpoints de modelos (.gitkeep)
├── evaluation/                # Relatórios de benchmark e suítes congeladas (.gitkeep)
├── tests/                     # Testes automatizados de estrutura, fronteira e métricas
└── src/
    └── leitorum_di/           # Pacote Python principal (namespace do subsistema)
        ├── contracts/         # Modelos Pydantic formais do LDF 1.0
        └── metrics/           # Utilitários puros de CER, WER e IoU
```

---

## 6. Governança e Ciclo de Trabalho

1. **Constituição Obrigatória:** Todo trabalho técnico deve respeitar os 8 princípios definidos em [.specify/memory/constitution.md](file:///c:/Users/User/caderno/document-intelligence/.specify/memory/constitution.md) (Local-first, Custo zero, Evidência antes de decisão, Reprodutibilidade, Human-in-the-loop).
2. **Experimentos Antes de Features:** Nenhum modelo é promovido a feature de produto sem um experimento homologado em `experiments/` e um registro arquitetural em `docs/adr/`.
3. **Spec Kit:** Uma vez aprovado o ADR, o desenvolvimento segue o fluxo canônico de Spec-Driven Development: `Specify → Plan → Tasks → Implement → Test`.
