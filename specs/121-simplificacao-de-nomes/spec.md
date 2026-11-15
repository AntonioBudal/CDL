# Feature Specification: F0.12.08 — Simplificação de nomes

**Feature Branch**: `121-simplificacao-de-nomes`

**Created**: 2026-11-15

**Status**: Concluída

**Input**: Pedido do usuário em 2026-11-14 e a auditoria do `docs/contexto/ROADMAP-0.12.md` (seção F0.12.08). Oitava
feature do 0.12. **Sem migração.** Só textos visíveis; nomes internos do código (componentes, rotas, variáveis,
tabelas) não mudam.

---

## 1. Regra (da auditoria)

Nomes simples, descritivos e universais; **um nome por tela**, igual no menu (computador e celular), no título, no
rótulo acima do título, na aba do navegador (`meta.title`) e nos avisos; maiúscula só no começo; um subtítulo de uma
frase dizendo o que a tela faz. Saem metáforas ("Bancada", "Ateliê", "Salão", "Cockpit", "Mesa de Triagem",
"Despejo") e inglês na interface ("Dashboard", "Inbox", "Active Recall").

Levantamento de 2026-11-15 (só `src/`, ocorrências em texto e código): "Inbox" 164 em 19 arquivos (a maioria é nome
interno, que fica), "Dashboard" 33 em 8, "Mesa de Triagem" 10, "Central de Revisão" 10, "Léxico" 9, "Ateliê" 9,
"Caixa de Entrada" 8, "Minhas Imagens e Espaço" 7, "Active Recall" 6, demais 1 a 4.

---

## 2. Nomes finais

| Tela | Nome (menu, título e aba) | Rótulo acima do título · subtítulo |
|---|---|---|
| `/dashboard` | **Painel** | — · "Seus estudos recentes, suas conexões e seu ritmo de leitura." |
| `/revisao` | **Revisão** | — · "Pratique lembrando: responda às perguntas e complete os trechos escondidos." |
| `/inbox` | **Caixa de entrada** | — · "Anote ideias rápidas e decida depois o que vira estudo." |
| `/importar` | **Importar** (título "Importar fichamento") | "Importar" · — |
| `/digitalizar` | **Digitalizar caderno** | "Importar" · — |
| `/amigos` | **Amigos** | — · "Encontre leitores, veja leituras em comum e responda aos pedidos de amizade." |
| `/highlights` | **Destaques** | — · "Os trechos que você marcou e as notas que escreveu." |
| `/lixeira` | **Lixeira** | — · "Itens excluídos ficam aqui por 30 dias e depois são apagados de vez." |
| `/minhas-imagens` | **Minhas imagens** | — |
| `/ajustes` | **Ajustes** | — |
| perfil | **Meu perfil** | — |
| `/conceitos` | **Conceitos** | — |
| `/sinteses` | **Sínteses** | — |
| sair | **Sair** | — |

---

## 3. User Stories

### US1 — Uma tela, um nome (P1)

**Acceptance**:
1. Em cada tela da tabela, o nome é o mesmo no menu do computador, no menu do celular, na barra de baixo do celular,
   no título, na aba do navegador, nos atalhos e nos avisos ("Abrir na caixa de entrada", "Voltar à caixa de
   entrada", mensagens de vazio, painel de Ajustes, busca global, atalhos de teclado).
2. Nenhum texto visível usa os nomes antigos nem "Active Recall" (vira "lembrar sem olhar" onde precisar explicar).
3. Maiúscula só no começo nos nomes e títulos tocados ("Caixa de entrada", "Minhas imagens", "Meu perfil").

### US2 — Textos gravados (P2)

**Acceptance**:
1. Ao transformar uma captura em estudo, a nota gravada passa a dizer "Nota capturada da caixa de entrada" (em vez de
   "do Inbox"). **Estudos já existentes não mudam** (nada é reescrito no banco).

### Edge Cases

- A **linha do tempo das versões** (`/sobre/versoes`) é histórica: os itens já entregues mantêm o nome da época.
- Endereços (`/dashboard`, `/inbox`, `/highlights`…) e os apelidos existentes **não mudam** (links salvos continuam).
- Textos da documentação da API (resumos e etiquetas do FastAPI) ficam, por serem internos.

---

## 4. Requirements

- **FR-001**: Trocar os textos visíveis no frontend (menus, títulos, rótulos, subtítulos, `meta.title`, avisos, vazios,
  botões, Ajustes, busca, atalhos, página "Sobre", página inicial pública) conforme a tabela.
- **FR-002**: `services/inbox_service.py`: nova frase da nota capturada.
- **FR-003**: Teste-guarda novo que **procura os nomes antigos** nos textos visíveis do `src/` (templates, `meta.title`,
  textos de aviso) e falha se algum voltar; testes antigos que conferiam textos atualizados.
- **FR-004**: Versão `0.12.0-alpha.8` e F0.12.08 marcada na linha do tempo.

## 5. Success Criteria

- **SC-001**: Guarda dos nomes antigos verde; `npm test` e testes vizinhos do backend verdes; build.
- **SC-002**: Navegador (dados fictícios): passar pelas 14 telas no computador e a 375 px conferindo menu, título e aba;
  nada quebra linha de forma estranha nos menus.
- **SC-003**: Versão `alpha.8`; commit; levar ao `main`.

## 6. Fora do escopo

- Seletor de idioma (F0.12.09, só a fundação).
- Mudar endereços, nomes internos do código ou textos já gravados nos estudos.
- Reescrever textos longos de ajuda além do necessário para tirar os nomes antigos.
