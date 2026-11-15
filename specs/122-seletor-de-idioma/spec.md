# Feature Specification: F0.12.09 — Seletor de idioma (só a fundação)

**Feature Branch**: `122-seletor-de-idioma`

**Created**: 2026-11-15

**Status**: Concluída

**Input**: Item F0.12.09 do `docs/contexto/ROADMAP-0.12.md`. **Decisão do usuário (2026-11-14): só a fundação.** Nona
feature do 0.12. **Com migração** (`0043`, uma coluna nova em `user_preferences`).

---

## 1. Contexto (auditoria de 2026-11-15)

| Ponto | Situação |
|---|---|
| Tradução | Nenhuma biblioteca; ~2.600 textos escritos direto no código, em português |
| Datas | 31 arquivos fixam `'pt-BR'`; 26 chamadas a `toLocale…`/`Intl` |
| Preferências | Tabela `user_preferences` (tema, fonte, modo de visão…), sincronizada pela API de preferências |
| Página | `<html lang="pt-BR">` fixo |
| Segurança | CSP `script-src 'self'` sem `unsafe-eval`: a biblioteca não pode compilar mensagens com `eval`/`new Function` |
| Nomes | F0.12.08 entregue: os nomes novos (Painel, Caixa de entrada…) já são os que serão traduzidos |

---

## 2. User Stories

### US1 — Escolher o idioma (P1)

**Acceptance**:
1. Em **Ajustes → Aparência**, um seletor **"Idioma da interface"**: **Português (Brasil)** e **English**. Trocar aplica na
   hora, sem recarregar.
2. O idioma fica **salvo na conta** (vale em outro aparelho) e **lembrado no navegador** (vale na tela de entrada,
   antes do login). Sem escolha salva, usa o idioma do navegador se for inglês; senão, português.
3. `<html lang>` acompanha o idioma (leitores de tela e corretores usam isso).

### US2 — O que já aparece em inglês (P1)

**Acceptance**:
1. Traduzidos para inglês os textos **de toda tela**: menus (computador, celular, barra de baixo, menu do usuário,
   "Mais"), cabeçalho (busca, captura rápida, notificações, sincronização), rodapé, títulos das abas do navegador
   (`meta.title` das telas), os avisos gerais (erro de rede, resposta inválida, erro genérico), a sincronização, o
   painel de notificações e o próprio seletor. *(Na execução: não existe diálogo global de atalhos; o item caiu.)*
2. **Datas e números** seguem o idioma em toda a interface (as 31 telas que fixavam `pt-BR` passam a usar a função
   comum de formato).
3. O resto da interface **continua em português** por enquanto e migra aos poucos (fora do escopo).

### Edge Cases

- Chave sem tradução em inglês: mostra o português (nunca a chave crua); um teste garante que as duas listas têm as
  mesmas chaves.
- Mensagens do servidor (erros de validação) continuam em português nesta fase.
- Partes presas ao português por natureza (citação ABNT, validador de paráfrase, leitura da seção Conceitos, organizador
  da digitalização, textos jurídicos e de apoio) não mudam com o idioma.
- Sem conexão ao salvar a preferência: o idioma fica no navegador e sincroniza depois (mesmo caminho das outras
  preferências).

---

## 3. Requirements

- **FR-001**: Biblioteca **`vue-i18n`** (padrão do ecossistema Vue), na montagem que **não usa `eval`** (compatível com
  a CSP), com `pt-BR` e `en` em `src/i18n/` (um arquivo por idioma, chaves agrupadas por área: `nav`, `header`,
  `footer`, `titles`, `common`, `settings`, `shortcuts`).
- **FR-002**: `src/i18n/format.ts`: `formatDate`, `formatDateTime`, `formatNumber`, `formatRelative` pelo idioma ativo;
  as 31 ocorrências de `'pt-BR'` passam a usá-las.
- **FR-003**: Migração `0043`: `user_preferences.locale` (`'pt-BR'` | `'en'`, padrão `'pt-BR'`); esquema e serviço de
  preferências aceitam o campo.
- **FR-004**: Seletor em Ajustes; `<html lang>`; `localStorage` (`leitorum_locale`) antes do login.
- **FR-005**: Versão `0.12.0-alpha.9` e F0.12.09 marcada na linha do tempo.

## 4. Success Criteria

- **SC-001**: Testes: as duas listas de mensagens têm as mesmas chaves; menus, cabeçalho, rodapé e `meta.title` usam
  chaves (nenhum texto fixo nesses arquivos); nenhum `'pt-BR'` fixo fora de `src/i18n/`; formatos de data nos dois
  idiomas; preferência salva e lida pela API; migração sobe e desce em banco descartável.
- **SC-002**: Navegador: trocar para English e ver menus, cabeçalho, rodapé, aba e datas em inglês sem recarregar;
  recarregar mantém; tela de entrada já em inglês; **nenhum erro de CSP no console**; 375 px (nomes em inglês cabem nos
  menus).
- **SC-003**: Testes novos e vizinhos; build; versão `alpha.9`; commit; levar ao `main`. A migração no banco ativo
  fica para o procedimento dos 4 comandos.

## 5. Fora do escopo

- Traduzir as telas por dentro (formulários, avisos específicos, textos de ajuda) e as mensagens do servidor.
- Outros idiomas além de português e inglês.
- Endereços em inglês (`/circulos` continua `/circulos`).
