# Feature Specification: F0.10.08 — Landing: Seção de Confiança, "Desafio F12" e Custo com Fontes e Datas

**Feature Branch**: `101-landing-confianca-f12`

**Created**: 2026-11-07

**Status**: Concluída em 2026-11-07 (com o Notion incluído)

**Input**: Feature 08 do Roadmap 0.10 ("Landing: seção de confiança e 'Desafio F12' (TCO só com fontes e datas)").
Quarta feature do lote 2.

---

## 1. Contexto (auditoria de 2026-11-07, só código)

| Ponto | Situação | Onde |
|---|---|---|
| Seção "Seus dados" | **Existe**: 4 fatos conferidos no código (onde ficam, exportação, sem análise de uso nem IA, conexões externas só no login com Google e na capa por endereço) e o link do repositório | `components/landing/SovereigntySection.vue` |
| Prova verificável | **Não existe**. Os fatos são afirmações; o visitante não tem como conferir na própria página | — |
| Recursos externos na landing | Nenhum: `index.html` não carrega fontes, scripts ou imagens de outros domínios; a CSP da F0.10.02 vale para todas as respostas | `index.html`, `core/security_headers.py` |
| Custo (TCO) | **Não existe** nenhuma comparação de custo | — |

**Regra do roadmap:** número de custo só com **fonte e data de consulta** na própria página. Nada de estimativa
sem fonte (energia, hardware) apresentada como fato.

---

## 2. User Stories

### US1 — "Desafio F12": não acredite, confira (P1)

Como visitante desconfiado, quero conferir sozinho que a página não fala com terceiros.

**Acceptance**:
1. Nova seção "Desafio F12" depois de "Seus dados", com 3 passos curtos: abrir as ferramentas do navegador (F12 ou
   Ctrl+Shift+I; no Mac, Cmd+Option+I), ir à aba **Rede** e recarregar; conferir que todos os pedidos vão para o
   mesmo endereço da barra.
2. Um painel "Conferir nesta página" lista, a partir da API de desempenho do próprio navegador
   (`performance.getEntriesByType('navigation' | 'resource')`), **os endereços contatados desde que a página abriu**,
   agrupados por origem e marcados "este servidor" ou "outro endereço", com a contagem de pedidos.
3. Botão "Conferir de novo" refaz a lista (inclui pedidos feitos depois). Resultado anunciado em `aria-live`.
4. O painel também mostra a **política de segurança (CSP)** que o servidor enviou, lida do cabeçalho
   `Content-Security-Policy` de um `HEAD` à própria página, com uma linha explicando `connect-src` e `script-src`.
   Se o cabeçalho não vier (ex.: rodando no Vite), diz isso em vez de inventar.
5. Texto honesto: o painel mostra o que **este navegador** registrou; extensões do navegador podem fazer pedidos
   próprios, e o login com Google, se ativado, fala com o Google só na tela de entrada.

### US2 — Custo com fontes e datas (P1)

**Acceptance**:
1. Bloco "Quanto custa" com uma tabela curta:
   - **Leitorum**: licença US$ 0; código público (link do repositório); roda no computador ou servidor que você já
     tem; o custo de energia e de máquina **não é estimado** (depende do seu caso).
   - **Readwise** (serviço comparável: importa destaques, revisão diária, exporta): Full US$ 9,99/mês no plano anual
     (US$ 119,88/ano) ou US$ 12,99 no mensal; Highlights US$ 7,99 (anual) ou US$ 8,99 (mensal); Highlights Lite
     US$ 5,59 (anual) ou US$ 6,99 (mensal). Fonte: `readwise.io/pricing`, consultada em 07/11/2026.
   - **Notion** (caderno geral, não específico de leitura; incluído a pedido do usuário): Free US$ 0; Plus US$ 10 por
     vaga/mês no plano anual (US$ 120/ano) ou US$ 12 no mensal. Fonte: `notion.com/pricing`, consultada em
     07/11/2026.
2. Cada linha com preço mostra a **fonte (link) e a data de consulta**; preços em dólar, como a fonte, sem converter.
3. Nota: "Preços de terceiros mudam; confira na fonte. Comparamos custo, não recursos."
4. Os dados ficam num arquivo próprio (`landing/costSources.ts`) e um teste recusa linha de preço sem `sourceUrl`
   https e `checkedAt` em data ISO.

### US3 — Navegação (P2)

**Acceptance**: o rodapé/índice da landing ganha a âncora `#desafio-f12` se houver um índice de seções; a seção usa o
mesmo `v-reveal`, tokens e larguras das vizinhas; alvos de 44 px; contraste ≥ 4,5:1 nos 10 temas.

### Edge Cases

- Navegador sem `performance.getEntriesByType` → mensagem "Seu navegador não expõe esta lista; use o F12".
- `HEAD` falhando (rede desligada) → "Não foi possível ler a política agora."
- Pedidos para `data:` ou `blob:` não contam como endereço externo.
- Landing aberta com login exigido: a landing é pública; o `HEAD` à raiz não exige sessão.

---

## 3. Requirements

- **FR-001**: `utils/networkAudit.ts` (puro): `groupEntriesByOrigin(entries, pageOrigin)` → `[{ origin, sameOrigin,
  count }]`, ignorando `data:`/`blob:`; `summarizeCsp(header)` → diretivas `connect-src`, `script-src`, `img-src`.
- **FR-002**: `components/landing/TrustChallengeSection.vue` (passos, painel ao vivo, CSP) e
  `components/landing/CostComparison.vue` com `landing/costSources.ts`.
- **FR-003**: `LandingView.vue` inclui as duas, depois de `SovereigntySection`.
- **FR-004**: Sem backend novo; sem pedido a terceiros (nem para buscar preços: os dados são estáticos e datados).
- **FR-005**: Só tokens, `.quiet` nos botões secundários, `prefers-reduced-motion` respeitado.

## 4. Success Criteria

- **SC-001**: Testes do `networkAudit` (agrupamento, mesma origem, `data:`/`blob:`, CSP ausente e presente).
- **SC-002**: Teste de dados: toda linha com preço tem `sourceUrl` https e `checkedAt` ISO; texto mostra a data.
- **SC-003**: Teste da landing: seções presentes, âncora, `aria-live`, nenhum `http(s)://` de terceiros carregado
  pelos componentes (só links `<a>`).
- **SC-004**: Navegador (servidor de validação): painel lista só a origem local; CSP lida do cabeçalho; 1366 e
  375 px; contraste nos 10 temas. `npm run build`; commit; levar ao `main`.

## 5. Fora do escopo

- Estimar energia, hardware ou hospedagem (sem fonte confiável para o caso de cada um).
- Comparar com Obsidian e outros (sem pedido; o Notion entrou a pedido do usuário em 07/11/2026).
- Atualizar preços automaticamente.
