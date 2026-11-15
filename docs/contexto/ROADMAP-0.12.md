# Roadmap 0.12 — Comunidade, ecossistema e versões

**Criado em:** 2026-11-14, por decisão do usuário: o antigo "Roadmap 1.0" passou a ser o **0.12**, porque a 1.0 ainda
está longe. Os itens de comunidade e ecossistema do plano mestre de 2026-11-01 continuam aqui, na mesma ordem,
depois de uma feature nova de versionamento, que vem primeiro porque as seguintes passam a se registrar nela.

**Fluxo:** o de sempre (HANDOFF §2): spec, plano e tarefas juntos em `specs/NNN-*/`, uma aprovação por feature,
suítes completas a cada 5 features, commit em português, push só quando o usuário pedir.

---

## Convenção de versão (adotada na F0.12.01)

[Versionamento Semântico 2.0.0](https://semver.org/lang/pt-BR/) (`MAJOR.MINOR.PATCH`, com pré-lançamento):

| Situação | Versão | Exemplo |
|---|---|---|
| Roadmap fechado (todas as features + suítes completas) | `0.MINOR.0` | `0.11.0` |
| Roadmap em andamento, N features entregues | `0.MINOR.0-alpha.N` | `0.12.0-alpha.2` |
| Correção depois de fechado | `0.MINOR.PATCH` | `0.11.1` |
| Compilação (só no Painel de Sistema e na dica do rodapé, não no texto) | `+<commit curto>` | `0.12.0-alpha.2+a1b2c3d` |

- `MAJOR` fica em `0` até a 1.0. Fonte única: **`caderno-leitura-0.1/VERSION`**, lida pelo backend (`app.__version__`,
  `/api/health`, Painel de Sistema) e pelo build (`__APP_VERSION__`); o `package.json`/`package-lock.json` acompanham.
- Cada feature do 0.12, ao ser concluída, sobe o `alpha.N` em `VERSION`, `package.json` e `package-lock.json` e marca
  `done: true` em `frontend/src/data/versionHistory.ts`, no mesmo commit (um teste confere que `alpha.N` = features
  entregues). Ao fechar o roadmap: `0.12.0`, `status: 'closed'` e `closed` com a data.

---

## Features

| # | Feature | Notas |
|---|---|---|
| F0.12.01 | **Versão no rodapé e "Evolução das versões"** | **Concluída em 2026-11-14** (versão `0.12.0-alpha.1`). Spec **114**. |
| F0.12.02 | **Estudos publicados na web** (`/compartilhado/:id`, indexável) | O antigo item "cadernos públicos indexáveis". Rascunho de spec já escrito (spec **115**, ainda não aprovado); fecha a pendência do HANDOFF §5 sobre `/compartilhado/{id}`. |
| F0.12.03 | **Importadores:** Readwise, Goodreads, StoryGraph, Omnivore, BookWyrm | Pode virar mais de uma feature (um formato por fatia), decidido na spec. |
| F0.12.04 | **Feeds RSS, Atom e JSON** | Depende da F0.12.02 (só o que está publicado entra em feed). |
| F0.12.05 | **Quadro espacial com exportação JSON Canvas** | O backend do canvas já existe. |
| F0.12.06 | **Oclusão de imagem em SVG** | Cartões de revisão sobre imagens. |
| F0.12.07 | **Círculos de leitura com trava anti-spoiler** | Depende de ISBN (F0.11.04) e estados de leitura (F0.11.01), já entregues. |

### F0.12.01 — Versão no rodapé e "Evolução das versões" (pedido do usuário em 2026-11-14)

1. **Rodapé:** mostra a versão atual no padrão acima, discreta (ex.: `v0.12.0-alpha.1`), com o commit da compilação
   na dica (`title`) e no Painel de Sistema; nunca dados do usuário.
2. **Tela "Evolução das versões"**, bem escondida: sem entrada nos menus; só um botão discreto no fim da página
   **Sobre o Leitorum**. Rota própria, com `noindex`.
   - Linha do tempo de **cada roadmap** (0.1 até o 0.12 em andamento): versão, período, tema e principais avanços,
     quantas features, e a situação (fechado / em andamento).
   - Fonte: um arquivo de dados escrito à mão a partir de `docs/HISTORICO-ROADMAPS.md`, dos `ROADMAP-0.x.md` e do
     HANDOFF (texto do projeto, nada do acervo do usuário).
3. A versão do backend (`/api/health`, Painel de Sistema) passa a ser a mesma do rodapé.

---

## Fora deste roadmap (a decidir)

- Ideias adiadas nas specs do 0.11 (backlinks "usado nas sínteses", transclusão em estudos, bordas/perspectiva na
  digitalização, SM-2/FSRS, KOReader pela rede, editar o léxico à parte).
- Planos do usuário ainda não registrados.
- Critérios da 1.0.
