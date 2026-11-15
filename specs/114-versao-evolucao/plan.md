# Implementation Plan: F0.12.01 — Versão no Rodapé e "Evolução das Versões"

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-14 | **Status**: Executado em 2026-11-14

## Technical Context

FastAPI (só a leitura da versão), Vue 3 + TS + Vite. **Sem migração.** Testes `pytest` (`tmp_path`) e `node:test`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: histórico escrito a partir de documentos do projeto |
| Banco ativo | Não é tocado |
| Privacidade | Rodapé e tela não mostram nada do acervo; a tela é pública como o Sobre, com `noindex` |
| Lote | 1ª feature do lote 1 do 0.12 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `caderno-leitura-0.1/VERSION` (novo) | `0.12.0-alpha.1` |
| `backend/app/__init__.py` | `__version__` lido de `VERSION` |
| `frontend/vite.config.ts`, `src/build-info.d.ts`, `package.json` | `__APP_VERSION__`; versão do pacote |
| `frontend/src/utils/appVersion.ts` (novo) | versão, versão completa, SemVer |
| `frontend/src/data/versionHistory.ts` (novo) | roadmaps 0.1 a 0.12 |
| `frontend/src/App.vue` (o rodapé real; `AppFooter.vue` não é usado) | versão discreta com dica |
| `frontend/src/views/AboutView.vue` | botão "Evolução das versões" no fim |
| `frontend/src/views/VersionsView.vue` (novo), `router/index.ts` | tela e rota `versions` |
| `frontend/src/components/settings/SystemSovereigntyCard.vue` | versão da interface ao lado da do servidor |
| `specs/076-…`, `specs/081-…` | rota `versions` |
| testes | `backend/tests/test_app_version.py`, `frontend/tests/feature-114-versoes.test.mjs` |
| docs | `HANDOFF.md` (regra de subir a versão), `ROADMAP-0.12.md` (F0.12.01 entregue), `RETOMADA.md` |

## Decisões

1. **SemVer 2.0.0 com `alpha.N`**: norma mais usada; `0.x` diz "antes da 1.0", `alpha.N` conta as features do roadmap
   em andamento sem inventar números.
2. **Arquivo `VERSION` como fonte única**: lido pelo backend e pelo build; o `package.json` só acompanha (o npm exige o
   campo) e um teste impede divergência.
3. **Histórico escrito à mão**: os commits antigos não têm padrão uniforme; um texto curado por roadmap explica melhor
   os avanços e não depende de git na máquina.
4. **Escondida, mas não secreta**: sem menu, só o botão no Sobre; pública como o Sobre (não há nada sensível) e fora
   dos buscadores.

## Riscos

| Risco | Mitigação |
|---|---|
| Esquecer de subir a versão a cada feature | Regra no HANDOFF §2 e teste que liga `VERSION` ao histórico |
| Datas e números de features antigas imprecisos | Fontes citadas em comentário no arquivo de dados; "cerca de" quando o documento não for exato |
| Versão quebrar o rodapé no celular | Teste de largura no navegador em 375 px |
