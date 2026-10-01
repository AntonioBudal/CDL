# Regras para Agentes — Document Intelligence (Leitorum)

Este arquivo define o guia operacional, os limites de escopo e as diretrizes de governança para qualquer agente de inteligência artificial que atue no subprojeto **`document-intelligence/`**, com foco principal de atuação para o **Claude Code**.

---

## 1. Divisão Fundamental de Escopo e Responsabilidade

O repositório do **Leitorum** adota uma separação estrita de domínios técnicos entre agentes:

```text
leitorum/
├── frontend/                  # Interface do Usuário (Vue 3 / TypeScript) — Responsabilidade do Antigravity
├── backend/                   # Servidor de Aplicação & SQLite (FastAPI)   — Responsabilidade do Antigravity
└── document-intelligence/     # IA de Visão, OCR/HTR e Extração Estrutural — Responsabilidade do Claude Code
```

### 1.1 Responsabilidade do Claude Code
O **Claude Code** é o agente encarregado com exclusividade pelo domínio **`document-intelligence/`**. Seu escopo abrange:
- Algoritmos e pipelines de visão computacional e pré-processamento de imagens;
- Detecção de página, retificação geométrica, desinclinação e análise de layout;
- Segmentação em regiões, blocos e linhas textuais;
- Motores de OCR (texto impresso) e HTR (*Handwritten Text Recognition* - texto manuscrito em português);
- Reconstrução espacial da página e determinação da ordem natural de leitura;
- Classificação semântica de elementos (títulos, resumos, conceitos, citações, perguntas, observações, exemplos);
- Reconhecimento de diagramas, fluxogramas, caixas, nós, setas direcionais e relações espaciais;
- Definição, validação e serialização do **Leitorum Document Format (LDF)**;
- Especificação e disponibilização da API HTTP local do Document Intelligence;
- Curadoria de fixtures sintéticos, estratégias de particionamento de datasets e protocolos de avaliação (*benchmarks*);
- Treinamento, adaptação, *fine-tuning* e inferência local;
- Registro sistemático de experimentos (`experiments/`) e Decisões de Arquitetura (`docs/adr/`).

### 1.2 Fora do Escopo do Claude Code (Proibições Estritas)
- **NÃO altere** arquivos em `frontend/`, `backend/`, `caderno-leitura-0.1/` ou na raiz do repositório sem solicitação e autorização explícita do usuário.
- **NÃO modifique** schemas, modelos SQLAlchemy ou migrações Alembic do produto principal fora de `document-intelligence/`.
- **NÃO altere** a base de dados de produção do Leitorum (`backend/data/caderno.db`) nem dados privados do usuário.
- Qualquer integração entre o Leitorum e o Document Intelligence deve ocorrer **exclusivamente via contratos bem definidos** (o formato LDF e a API HTTP local).

---

## 2. Proteção da Fronteira Técnica em Múltiplas Camadas

A fronteira entre o produto principal e o Document Intelligence é defendida em seis níveis:

1. **Nível Normativo (`AGENTS.md` e `CLAUDE.md`)**:
   - Definição contratual explícita dos diretórios de atuação de cada agente.
2. **Nível de Regras do Antigravity (`.agents/rules/`)**:
   - O Antigravity está proibido de implementar modelos, OCR/HTR ou pipelines de visão computacional em `document-intelligence/`.
3. **Nível de Regras e Permissões do Claude Code (`CLAUDE.md`)**:
   - Configurações operacionais instruem o Claude Code a restringir suas escritas e execuções estritamente ao diretório `document-intelligence/`.
4. **Nível de Hooks Locais (quando aplicável)**:
   - Scripts e verificadores de pré-commit podem inspecionar caminhos alterados.
5. **Nível de Sandbox do Sistema**:
   - Comandos e testes devem rodar com o diretório de trabalho apontado para `document-intelligence/`.
6. **Nível de Validação Git / CI**:
   - Testes automatizados de fronteira (`tests/test_boundary.py`) garantem que nenhum arquivo de `document-intelligence/` dependa de imports relativos ou caminhos que vazem para o restante do repositório.

---

## 3. Princípios Operacionais Inegociáveis

1. **Local-first e Custo Zero**:
   - **NUNCA** utilize APIs pagas ou serviços em nuvem proprietários que cobrem por imagem, caractere, token, requisição ou tempo de processamento (ex.: OpenAI, Google Cloud Vision, Azure Cognitive Services, AWS Textract).
   - O pipeline deve ser 100% autônomo, executável localmente (*self-hosted* ou *on-premise*).
2. **Evidência Antes de Decisão**:
   - Nenhuma biblioteca ou modelo deve ser adotado apenas por popularidade ou preferência pessoal. Toda escolha deve ser sustentada por dados, experimentos documentados e métricas reproduzíveis.
3. **Medir Antes de Otimizar**:
   - Não introduza código em C/C++, kernels customizados de CUDA ou otimizações prematuras de baixo nível sem comprovação prévia de que existe um gargalo crítico de desempenho.
4. **Separação Rigorosa entre Reconhecimento e Interpretação**:
   - O texto bruto transcrito (OCR/HTR) jamais deve ser misturado silenciosamente com interpretações, inferências semânticas ou resumos gerados. Ambos devem ter campos e níveis de confiança explicitamente distintos no LDF.
5. **Human-in-the-Loop por Design**:
   - O sistema deve antecipar imperfeições e permitir que correções feitas por humanos sejam registradas (em formato RFC 6902 JSON Patch) para retroalimentar pipelines futuros de aprendizado contínuo.
6. **Experimentos Não São Features**:
   - Resultados de scripts de teste e experimentos (`experiments/`) não são código de produto. A migração de uma tecnologia experimental para o código-fonte principal (`src/leitorum_di/`) exige formalização via ADR (Decisão de Arquitetura) e ciclo de especificação via GitHub Spec Kit.

---

## 4. Fluxo de Trabalho com GitHub Spec Kit

O desenvolvimento de funcionalidades dentro de `document-intelligence/` segue obrigatoriamente o ciclo do **GitHub Spec Kit**:

```text
Constituição (.specify/memory/constitution.md)
       ↓
Especificação (speckit.specify)
       ↓
Clarificação (speckit.clarify)
       ↓
Plano Técnico (speckit.plan)
       ↓
Tarefas Atômicas (speckit.tasks)
       ↓
Implementação (speckit.implement)
       ↓
Testes Automatizados (pytest)
       ↓
Avaliação Quantitativa (Evaluation Benchmark)
       ↓
Registro de Decisão (ADR / MADR)
```

### Regras do Spec Kit para o Claude Code:
1. Verifique a versão do Spec Kit instalada (`specify --version`) e a sintaxe real de comandos disponíveis antes de executar chamadas de automação.
2. Nunca invente subcomandos inexistentes.
3. Cada entrega estruturante deve possuir sua pasta dedicada em `specs/` com `spec.md`, `plan.md` e `tasks.md`.

---

## 5. Roteiro Sequencial de Experimentos

O avanço tecnológico do domínio é estritamente incremental e delimitado. **Não avance para o experimento seguinte sem a aceitação formal e conclusão do anterior:**

1. **`EXP-000`** — *Environment, Reproducibility and Evaluation Foundation* (Ambiente, hardware, uv, pytest, reprodutibilidade e verificação de fronteira).
2. **`EXP-001`** — *HTR em Linhas Manuscritas* (Transcrição básica de imagem de linha em texto, baseline vs adaptação, métricas CER/WER).
3. **`EXP-002`** — *Detecção de Layout e Segmentação de Blocos/Regiões*.
4. **`EXP-003`** — *Reconstrução Espacial e Ordem de Leitura*.
5. **`EXP-004`** — *Classificação Semântica de Conteúdo do Caderno*.
6. **`EXP-005`** — *Reconhecimento de Diagramas, Nós e Fluxogramas*.
7. **`EXP-006`** — *Pipeline Integrado Ponta a Ponta*.

**Estado Atual:** O projeto encontra-se na fase de **Preparação de Contexto e Governança**. A primeira ação técnica a ser realizada pelo Claude Code é a execução e relatório do **`EXP-000`**.
