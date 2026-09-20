# Convenção de Versionamento Git — Caderno de Leitura (CDL)

**Repositório Oficial:** [https://github.com/AntonioBudal/CDL](https://github.com/AntonioBudal/CDL)  
**Remote Esperado:** `https://github.com/AntonioBudal/CDL.git`  
**Data:** 19/09/2026  

---

## 1. Regra de Transição dos Roadmaps

O histórico Git do projeto Caderno de Leitura organiza-se em dois modelos temporais complementares:

### Marco Histórico (0.1 a 0.4)
Nos Roadmaps 0.1 a 0.4, o repositório consolida **1 commit por Roadmap**:
- **0.1:** `versão 0.1 — base inicial do acervo e estudos`
- **0.2:** `versão 0.2 — acesso em rede local e personalização`
- **0.3:** `versão 0.3 — gestão, visualização e produtividade`
- **0.4:** `versão 0.4 — navegação espacial, relações e movimento`

Cada um desses commits representa o estado consolidado do projeto ao término do respectivo Roadmap.

---

### Padrão Vigente (a partir da versão 0.5)
A partir do **Roadmap 0.5**, abandona-se o commit único por Roadmap e adota-se rigorosamente:

> **1 Commit = 1 Feature Implementada e Validada**

- **Roadmaps** são marcos de planejamento arquitetural de alto nível.
- **Features** são unidades de especificação e implementação atômica.
- Cada feature é concebida e desenvolvida através do fluxo completo do **GitHub Spec Kit** integrado ao Antigravity:
  ```
  Roadmap
    │
    ▼
  Escolher Feature
    │
    ├─► /speckit-specify
    ├─► /speckit-clarify
    ├─► /speckit-plan
    ├─► /speckit-checklist
    ├─► /speckit-tasks
    ├─► /speckit-analyze
    ├─► /speckit-implement
    ├─► /speckit-converge
    │
    ▼
  Validação das Suítes de Testes (npm test, pytest, npm run build)
    │
    ▼
  Commit Unitário da Feature
  ```

---

## 2. Padrão de Nomenclatura das Mensagens

As mensagens de commit das features devem seguir as seguintes regras:
- **Idioma:** Estritamente em língua portuguesa.
- **Estrutura:** `feature — <nome da feature>`
- **Estilo:** Curto, simples, direto e descritivo.
- **Evitar:** Mensagens vagas (`update`, `fix`, `changes`), jargões em inglês, termos excessivamente técnicos ou rótulos de marketing.

### Exemplos Válidos (Roadmap 0.5):
- `feature — base multiusuário`
- `feature — autenticação local`
- `feature — sincronização em nuvem`
- `feature — perfil do leitor`
- `feature — compartilhamento de anotações`
- `feature — painel de administração`
- `feature — notificações do sistema`

---

## 3. Segurança e Preservação de Dados
- O banco de dados ativo de produção (`backend/data/caderno.db`), backups (`.db`, `.zip`) e imagens de capa pessoais são estritamente privados e **NUNCA** devem ser adicionados ao versionamento Git.
- Antes de qualquer commit, certifique-se de que o `.gitignore` mantém a blindagem de dados e que `git status` não apresenta artefatos privados em staging.
- Para detalhes da auditoria histórica das versões anteriores, consulte [docs/HISTORICO-ROADMAPS.md](../HISTORICO-ROADMAPS.md).
