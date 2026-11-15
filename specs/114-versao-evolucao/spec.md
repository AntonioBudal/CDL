# Feature Specification: F0.12.01 — Versão no Rodapé e "Evolução das Versões"

**Feature Branch**: `114-versao-evolucao`

**Created**: 2026-11-14

**Status**: Concluída em 2026-11-14

**Input**: Pedido do usuário em 2026-11-14 (`docs/contexto/ROADMAP-0.12.md`): mostrar no rodapé em que versão estamos,
"seguindo uma norma estabelecida", e uma tela **bem escondida** com a evolução de cada roadmap, acessível por um botão
em "Sobre o Leitorum". Primeira feature do Roadmap 0.12. **Sem migração.**

---

## 1. Contexto (auditoria de 2026-11-14, só código e documentos do projeto)

| Ponto | Situação | Onde |
|---|---|---|
| Versão declarada | **Parada em `0.2.0-alpha.1`** em dois lugares, sem ligação entre eles | `frontend/package.json`, `backend/app/__init__.py` |
| Onde a versão aparece | `/api/health` e o Painel de Sistema (F0.10.03), com o commit do servidor e o da interface | `routers/health.py`, `routers/system.py`, `SystemSovereigntyCard.vue` |
| Commit da interface | Embutido no build (`__BUILD_COMMIT__`) | `vite.config.ts` |
| Rodapé | Marca, "Código-fonte público", Sobre e Apoie; sem versão | `components/layout/AppFooter.vue` |
| Sobre | Página pública (sem login), sem nada sobre versões | `views/AboutView.vue` |
| Histórico | 0.1 a 0.4 auditados em `docs/HISTORICO-ROADMAPS.md`; 0.3 a 0.9 em `docs/contexto/ROADMAP-0.x.md`; 0.10 e 0.11 no HANDOFF; commits de marco "versão 0.1 — …" a "versão 0.4 — …"; nenhuma *tag* git | `docs/` |

---

## 2. User Stories

### US1 — Versão no rodapé, pela norma (P1)

**Acceptance**:
1. O rodapé mostra, discreto, **`v0.12.0-alpha.1`** (com esta feature concluída), no padrão **Versionamento Semântico
   2.0.0** descrito no `ROADMAP-0.12.md`: roadmap fechado `0.MINOR.0`; em andamento `0.MINOR.0-alpha.N` (N = features
   do roadmap entregues); correção depois de fechado `0.MINOR.PATCH`.
2. Ao passar o mouse (ou focar), a dica mostra a versão completa com o commit da compilação: `0.12.0-alpha.1+a1b2c3d`.
   A versão no rodapé **não é um link** e não leva a lugar nenhum (a tela fica escondida no Sobre).
3. **Fonte única:** o arquivo `caderno-leitura-0.1/VERSION` (uma linha, SemVer). O backend (`app.__version__`) e o build
   do frontend leem dele; o `package.json` acompanha (um teste confere que os três batem e que o texto é SemVer válido).
4. `/api/health` e o Painel de Sistema passam a mostrar a mesma versão.

### US2 — "Evolução das versões", escondida (P1)

**Acceptance**:
1. **Sem entrada em nenhum menu.** No fim da página **Sobre o Leitorum**, um botão discreto `.quiet`:
   **"Evolução das versões"** → rota `/sobre/versoes` (pública como o Sobre, com `noindex`, fora do sitemap).
2. A tela mostra uma **linha do tempo** de cada roadmap, do mais recente ao mais antigo: versão (`0.11.0`, …), período,
   tema, situação (**em andamento** / **fechado**), quantas features e de 3 a 6 avanços principais, em linguagem de
   quem usa (não de código).
3. O 0.12 em andamento mostra as features entregues e as que faltam (lidas da mesma fonte de dados).
4. No topo, a versão atual e um texto curto explicando a numeração (o que significam `0.12`, `alpha.1` e por que ainda
   não é 1.0).
5. Conteúdo **escrito à mão** num arquivo de dados do frontend (`data/versionHistory.ts`), a partir dos documentos do
   projeto; nada do acervo do usuário. Um teste confere que a versão atual do arquivo `VERSION` aparece no histórico como
   "em andamento" e que as versões estão em ordem.

### Edge Cases

- Build sem git: a dica mostra só a versão (sem `+commit`), como o Painel já faz com "desconhecido".
- Celular: a versão cabe no rodapé sem rolagem lateral (quebra de linha se preciso); a linha do tempo em uma coluna.
- Leitor de tela: a versão no rodapé tem rótulo "Versão 0.12.0-alpha.1"; cada roadmap da linha do tempo é um
  `article` com título.
- Achado na execução: o rodapé que aparece na tela é o do `App.vue`; `components/layout/AppFooter.vue` não é usado
  em lugar nenhum e ficou como estava.

---

## 3. Requirements

- **FR-001**: `caderno-leitura-0.1/VERSION` = `0.12.0-alpha.1`; `backend/app/__init__.py` lê o arquivo (com reserva se
  faltar); `frontend/vite.config.ts` define `__APP_VERSION__`; `package.json` = mesma versão.
- **FR-002**: `frontend/src/utils/appVersion.ts`: `appVersion()`, `fullVersion(commit)`, `parseSemver`, `isValidSemver`.
- **FR-003**: `frontend/src/data/versionHistory.ts`: lista de roadmaps (versão, período, tema, situação, features,
  avanços) de 0.1 a 0.12.
- **FR-004**: `components/layout/AppFooter.vue` com a versão; `views/AboutView.vue` com o botão; `views/VersionsView.vue`
  (`/sobre/versoes`, rota `versions`, `public: true`), registrada nos contratos 076/081.
- **FR-005**: `docs/contexto/HANDOFF.md` §2 ganha a regra: ao concluir cada feature do 0.12, subir o `alpha.N` em
  `VERSION` e `package.json` e marcar a feature no `versionHistory.ts`, no mesmo commit; ao fechar o roadmap,
  `0.12.0`.
- **FR-006**: Só tokens, `.quiet`, 44 px no botão, contraste ≥ 4,5:1 nos 10 temas.

## 4. Success Criteria

- **SC-001**: Testes: `VERSION`, `package.json` e o backend com a mesma versão SemVer válida; `/api/health` devolve a
  versão; utilitário (`parseSemver`, `fullVersion` com e sem commit); histórico ordenado e com a versão atual em
  andamento; rodapé sem link na versão; botão só no Sobre (nenhum menu aponta para `/sobre/versoes`); rota nos
  contratos.
- **SC-002**: Navegador: versão no rodapé (dica com commit), botão no Sobre, tela de versões, sem login e com login;
  375 e 1366 px; contraste nos 10 temas.
- **SC-003**: Build e testes novos e vizinhos; commit; levar ao `main`.

## 5. Fora do escopo

- *Tags* git `v0.1.0` … `v0.11.0` nos commits de marco (sugestão para depois; só com o pedido do usuário, porque o
  push das *tags* é público).
- Changelog automático a partir dos commits; aviso "novidades desta versão" ao entrar.
