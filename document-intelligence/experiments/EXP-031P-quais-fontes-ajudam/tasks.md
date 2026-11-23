# Tarefas: EXP-031P — Quais fontes abertas ajudam

**Entrada:** [spec.md](./spec.md) e [plan.md](./plan.md).

- [x] T001 Testes que falham primeiro: composição dos grupos (cotas, semente), descarte de caracteres fora do
  dicionário, registro do ciclo no catálogo, gerador sintético com aumentos (determinístico).
- [x] T002 Coletor de lote pequeno (Teklia Parquet/API, HTR-United zip) até 8 mil linhas por grupo, pelo catálogo.
- [x] T003 Gerador sintético com aumentos fortes; 8 mil linhas.
- [x] T004 Preparar os conjuntos de medida (BRESSAY teste, GNHK teste, 62 linhas do autor) e medir C0.
- [x] T005 Treinar C1–C5 (um por vez, retomável, com espera de RAM), cada um registrado como ciclo `experimento`.
- [x] T006 Avaliar os 5 modelos nos 3 conjuntos; CER, WER e acentos.
- [x] T007 `report.md` (H1–H4 e a decisão para a E4); benchmark só com números; `CLAUDE.md`, estratégia e
  roadmap; commit `EXP-031P(document-inteligence) …`.
