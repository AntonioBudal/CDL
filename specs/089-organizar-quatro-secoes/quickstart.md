# Quickstart: Validação da Feature 089

**Feature**: `089-organizar-quatro-secoes` | **Plan**: [plan.md](plan.md)

Só textos fictícios. Nenhum passo usa `backend/data/caderno.db`. O `pytest` roda com `CADERNO_DATABASE_PATH`
apontando para um banco descartável já migrado, como na validação da 086.

---

## 1. Suítes (SC-007)

```powershell
cd caderno-leitura-0.1\backend; $env:CADERNO_DATABASE_PATH = "<pasta temporária>\descartavel.db"; .\.venv\Scripts\python -m pytest
cd ..\frontend; npm test; npm run build
```

## 2. Paridade com o EXP-023 (SC-003)

O `test_organizer_parity.py` compara o organizador do produto com `backend/tests/fixtures/organizer-parity-v1.json`
em 144 de 144 casos (24 páginas × 6 condições). Trechos, seções, confiança e marcação de conferência precisam ser
iguais.

O fixture vem de `document-intelligence/experiments/EXP-023/harness/export_parity.py`, e o SHA-256 dele fica
registrado no teste.

## 3. Latência e carga (SC-001)

Num servidor de validação com banco temporário e porta própria, enviar as 144 páginas de paridade a
`POST /api/imports/organize` e medir:
- o p95 do tempo no servidor, com meta de até 200 ms;
- o tempo da primeira carga do artefato.

## 4. Fluxos manuais

1. **Digitalização** (com o motor instalado e uma página fictícia):
   - revisar e organizar: aparecem 4 editores, o aviso e "Seções para conferir";
   - mover um trecho;
   - editar e voltar: a confirmação aparece e o texto anterior volta exato;
   - organizar de novo e salvar: o estudo "rascunho" tem as 4 seções e o registro de origem intacto.
2. **Importação:**
   - colar um texto fictício sem cabeçalhos;
   - "Organizar automaticamente" distribui o texto e "Desfazer organização" restaura o estado anterior.
3. **Artefato ausente** (SC-005):
   - renomear `organizer-v1.json` e reiniciar;
   - o botão some ou aparece desativado com explicação, e digitalização e importação seguem funcionando;
   - desfazer a renomeação.
4. **Temas e celular** (SC-006): 320 px e desktop; temas claro, escuro e E-Ink; uso só pelo teclado. Os itens que
   dependem de olho humano ficam listados para o usuário.

## 5. Resultados da validação (2026-10-27)

Medidos pelo agente com textos fictícios. O `pytest` rodou com `CADERNO_DATABASE_PATH` num banco descartável e o
servidor de validação, com banco temporário e porta própria.

| Item | Resultado |
| :--- | :--- |
| Linha de base | backend 498 aprovados / 1 pulado; frontend 616 aprovados; build ok |
| Depois da feature (SC-007) | backend **513 aprovados / 1 pulado** (+15); frontend **633 aprovados** (+17); build ok |
| Paridade (SC-003) | **144/144** casos idênticos no teste e também pela API do servidor de validação |
| Latência (SC-001) | no servidor: mediana de 8 ms, **p95 de 17 ms**, máximo de 23 ms; ida e volta HTTP: p95 de 39 ms |
| Primeira carga do artefato | 0,049 s |
| Salvamento | estudo "rascunho" com as 4 seções idênticas às sugeridas |
| Artefato ausente (SC-005) | status `not_installed`; `organize` → `503 unavailable`; pré-visualização da importação e status da digitalização seguem `200`; artefato restaurado e conferido pelo SHA-256 |

**Pendente de execução manual pelo usuário** (não marcado como feito):
- SC-006: percorrer a tela em 320 px, em desktop, nos temas claro, escuro e E-Ink, e só com teclado (abas dos 4
  editores, "Mover para…", "Voltar para texto único");
- o fluxo de digitalização com uma foto real no celular.
