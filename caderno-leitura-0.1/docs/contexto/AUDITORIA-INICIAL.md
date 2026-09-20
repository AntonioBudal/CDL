# Relatório de Auditoria Inicial — Transição Caderno de Leitura 0.3

**Data da Auditoria:** 15 de setembro de 2026  
**Responsável:** Tech Lead (Antigravity + GitHub Spec Kit)  
**Status Oficial das Tarefas 0.3 (T01–T10):** **TODAS NÃO INICIADAS**

---

## 1. Resumo Executivo

Nesta rodada inicial, foi assumida a liderança técnica da transição do projeto **Caderno de Leitura** para o ambiente Antigravity integrado ao GitHub Spec Kit (`agy`).

**Principais Conclusões:**
1. A **raiz real da aplicação** foi identificada em `C:\Users\User\caderno\caderno-leitura-0.1`, onde residem `iniciar.py`, `backend/`, `frontend/` e `backend/data/caderno.db`.
2. A **raiz do Git** está em `C:\Users\User` (diretório pessoal do usuário no Windows), o que exige atenção rigorosa para não expor arquivos externos ou dados pessoais.
3. O histórico do erro `corrupt patch …infra-0.3.patch:1957` foi **investigado e solucionado por leitura**: o patch possui truncamento no caractere final (ausência de newline no EOF e falta da marcação `\ No newline at end of file`), confirmando que **o patch nunca foi aplicado** e a base permanece limpa na versão Alpha 0.1/0.2.
4. O **acervo do usuário** em `backend/data/caderno.db` (32 KB) está íntegro e em repouso (sem arquivos WAL/SHM pendentes). Nenhum dado do acervo foi lido, alterado ou transmitido.
5. A infraestrutura do **Spec Kit** foi integrada com sucesso através da integração nativa `agy`, tendo sido criada a Constituição oficial do projeto (`.specify/memory/constitution.md`) e as regras de agentes (`AGENTS.md` e `.agents/rules/caderno-leitura.md`).
6. Nenhuma linha de código da aplicação foi modificada nesta rodada. Todas as dez tarefas da 0.3 permanecem **NÃO INICIADAS**.

---

## 2. Mapeamento de Caminhos e Estrutura Real

| Escopo | Caminho Absoluto | Detalhes / Observações |
|---|---|---|
| **Raiz Real da Aplicação** | `C:\Users\User\caderno\caderno-leitura-0.1` | Contém `iniciar.py`, `backend/`, `frontend/`, scripts e banco ativo. |
| **Workspace Aberto no Antigravity** | `C:\Users\User\caderno` | Pasta pai que abriga a raiz real e os arquivos de transição. |
| **Raiz do Repositório Git** | `C:\Users\User` | Inicialização ampla do Git cobrindo a pasta de usuário do Windows. |
| **Banco de Dados Ativo** | `C:\Users\User\caderno\caderno-leitura-0.1\backend\data\caderno.db` | Tamanho: 32.768 bytes. Data: 10/09/2026 06:48:26. |
| **Frontend Compilado (Dist)** | `C:\Users\User\caderno\caderno-leitura-0.1\frontend\dist` | Assets HTML/JS/CSS prontos para consumo pelo FastAPI. |
| **Ambiente Virtual Backend** | `C:\Users\User\caderno\caderno-leitura-0.1\backend\.venv` | Python 3.13.15 configurado e com pacotes instalados. |

---

## 3. Diagnóstico de Runtimes e Ferramental

- **Python:** Python 3.13.15 detectado (`py -3.13` e venv local). Suporte pleno às anotações tipadas e aos requisitos do backend.
- **Node.js e npm:** Node v24.14.1 e npm 11.11.0 instalados. Atendem perfeitamente ao requisito `engines: ">=24.0.0 <25"` do `frontend/package.json`.
- **uv:** Versão 0.11.21 instalada e funcional.
- **GitHub Spec Kit CLI:** Versão 1.0.1 instalada. O comando `specify check` confirmou a disponibilidade de `Antigravity (available)`.
- **Integração Spec Kit:** O comando `specify integration status` reportou conformidade total (`Integration status: OK`, `Default integration: agy`).

---

## 4. Diferenças em Relação à Base Esperada

1. **Pacote de Contexto:** O usuário havia baixado individualmente `LEIA-ME-TRANSICAO.md`, `FLUXO-SPECKIT.md`, `ROADMAP-0.3.md` e `PRIMEIRO-PROMPT-ANTIGRAVITY.md`. Os arquivos complementares (`AGENTS.md`, `.specify/memory/constitution.md`, `docs/contexto/PROJETO.md`, `ESTADO-E-DIAGNOSTICO.md`, `AMBIENTE-E-VALIDACAO.md`, `RETOMADA.md`) foram gerados e integrados diretamente nos destinos especificados, unificando a documentação nas duas pastas (`caderno` e `caderno-leitura-0.1`).
2. **Capacidades 0.2 Já Existentes:** Foi constatado que a base atual já possui o endpoint `GET /api/backup` (`backend/app/routers/backups.py` e `backend/app/services/backups.py`), que utiliza com precisão a SQLite Online Backup API (`original.backup(snapshot)`), além de `iniciar.py` já contar com rotinas de inicialização em rede e impressão de QR Code.
3. **Versão do Frontend:** `frontend/package.json` declara a versão `0.2.0-alpha.1`.

---

## 5. Investigação do Erro do Patch (`infra-0.3.patch`)

- **Contexto:** Ao tentar rodar `git apply --check infra-0.3.patch`, o Git retornou:
  `fatal: corrupt patch at line 1957`
- **Análise Técnica:**
  - O arquivo possui exatamente 1957 linhas.
  - A inspeção binária dos bytes finais revelou:
    `b'ile=sys.stderr)\r\n+        return 1\r\n+\r\n+\r\n+if __name__ == "__main__":\r\n+    raise SystemExit(main())'`
  - A última linha (1957) termina abruptamente no fim do arquivo sem caractere de quebra de linha (`\n`) e sem a marcação canônica do diff unificado `\ No newline at end of file`.
  - Pelas regras da especificação de diff do Git, a ausência dessa marcação quando um hunk termina sem newline faz o parser considerar que o arquivo foi truncado ou corrompido durante a transferência/cópia.
- **Conclusão:** O patch foi interrompido no momento da sua geração ou cópia. Como a verificação parou no `--check`, **nenhuma modificação do patch foi aplicada ao código-fonte**. O repositório está limpo e não contaminado.

---

## 6. Auditoria de Testes, Scripts e Isolamento de Dados

- **Backend (`backend/tests/`):**
  - Todas as fixtures de banco (`test_database.py`, `test_api.py`, `test_import_api.py`) utilizam `tmp_path` para criar bancos SQLite descartáveis com nomes isolados.
  - O teste de servidor local (`test_local_server.py`) aloca uma porta efêmera via socket e define `CADERNO_DATABASE_PATH` para uma base temporária, sem concorrer com a porta 8000 nem acessar `backend/data/caderno.db`.
- **Frontend (`frontend/tests/`):**
  - Testes unitários executados via `node:test`. Todos os módulos de gateway e serviços são mockados em memória (`makeDraft`), sem tráfego de rede ou dependência de banco.
- **Scripts de Ciclo de Vida:**
  - `package.json` não possui ganchos automáticos maliciosos ou destrutivos (`preinstall`/`postinstall`).
  - Nenhum teste ou comando `npm install` foi executado nesta rodada, mantendo o isolamento exigido.

---

## 7. Riscos Concretos Identificados

1. **Risco de Escopo do Git (CRÍTICO):** O fato de `C:\Users\User` ser a raiz do Git implica que qualquer comando como `git add .` ou `git commit -a` executado sem o devido cuidado poderia rastrear acidentalmente diretórios pessoais, documentos ou credenciais da máquina do usuário.
   - *Mitigação:* Nunca executar comandos globais de Git na raiz do perfil. Operar sempre com caminhos específicos ou, futuramente, isolar um repositório Git dedicado exclusivamente dentro de `caderno-leitura-0.1`.
2. **Ambiguidade de Raiz do Workspace:** O Antigravity foi aberto em `C:\Users\User\caderno`, enquanto a aplicação executável está em `C:\Users\User\caderno\caderno-leitura-0.1`.
   - *Mitigação:* Os arquivos de contexto, regras de agentes e Spec Kit foram sincronizados em ambos os locais para garantir que ferramentas e comandos funcionem independentemente de o terminal estar em `caderno` ou em `caderno-leitura-0.1`.
3. **Dependência Circular T09 x T10:** Querer entregar toda a infraestrutura de migrações e concorrência (T09) antes de ter backup, ou querer entregar toda a interface e pacote de backup (T10) antes das definições de banco.
   - *Mitigação:* Seguir a recomendação coordenada abaixo.

---

## 8. Recomendação de Especificação Coordenada: T09 e T10

Para iniciar com máxima segurança a versão 0.3 após esta auditoria, recomenda-se a seguinte estratégia de fatiamento:

```
[Etapa 1: Snapshot Consistente Mínimo] 
  │  (Reaproveita e consolida a SQLite Backup API já presente em backups.py)
  │  (Garante cópia atômica consistente do banco ativo antes de qualquer operação)
  ▼
[Etapa 2: Fatias de T09 — Integridade e Migrações]
  │  (Contratos unificados de caminho: CADERNO_DATABASE_PATH)
  │  (Validação pré-migração obrigatória: PRAGMA quick_check + snapshot prévio)
  │  (Controle de concorrência otimista para edição PC/celular)
  ▼
[Etapa 3: Fatias de T10 — Pacote, Restauração e Operação]
  │  (Empacotamento completo com manifesto: banco + capas persistentes)
  │  (Procedimento de restauração transacional com rollback em caso de falha)
  │  (Bloqueio de instâncias duplicadas e diagnóstico de porta)
```

**Benefício:** T09 ganha imediatamente a proteção de backup necessária para evoluir o esquema sem risco ao acervo, enquanto T10 pode amadurecer suas rotinas operacionais sem a pressão de entregar tudo em um único bloco monolítico.

---

## 9. Quadro Oficial de Estado das Tarefas 0.3

| ID | Tarefa | Status Auditado |
|---|---|---|
| **T01** | Edição completa de livros e estudos | **NÃO INICIADA** |
| **T02** | Lixeira e restauração de itens | **NÃO INICIADA** |
| **T03** | Capas por upload e URL | **NÃO INICIADA** |
| **T04** | Visualização, busca e ordenação do acervo | **NÃO INICIADA** |
| **T05** | Categorias pesquisáveis e taxonomia | **NÃO INICIADA** |
| **T06** | Dashboard com calendário e timeline | **NÃO INICIADA** |
| **T07** | Exportação de anotações em TXT/Markdown | **NÃO INICIADA** |
| **T08** | Central de ajustes com preview | **NÃO INICIADA** |
| **T09** | Integridade do banco, migrações e concorrência | **NÃO INICIADA** |
| **T10** | Backup completo, restauração e operação confiável | **NÃO INICIADA** |

---

## 10. Próximos Passos Imediatos

1. Concluir esta rodada informando o diagnóstico ao usuário.
2. Aguardar a autorização explícita do usuário para dar início à primeira feature.
3. Quando autorizado, invocar a skill/comando **`speckit.specify`** para a primeira fatia delimitada de infraestrutura (Snapshot Consistente Mínimo e Proteção de Migrações de T09/T10).
