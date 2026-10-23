# EXP-016: Relatório de Resultados — Leitura em Lote no Pipeline

* **Status:** `ACCEPTED` / `CONCLUÍDO` (executado e aceito por delegação permanente do usuário, 2026-10-22)
* **Executor:** Claude Code
* **Decisão:** a leitura em lote **não** entra no pipeline do [ADR-008](../../docs/adr/ADR-008-pipeline-de-referencia.md)
* **Artefato do ciclo:** [spec.md](./spec.md)

> **Dados.** As sondas usam linhas fictícias ("Livro de Teste", "Capítulo N") e as 20 primeiras páginas do conjunto
> de **calibração** do BRESSAY (`NEEDS VALIDATION`, só experimento), registrando **só tempos**. Os conjuntos de
> teste não foram usados: continuam sem uso para a próxima mudança real.

---

## 1. Resposta

**Não.** Ler as linhas em lotes de 8 dá o mesmo texto, mas não fica mais rápido; fica um pouco mais lento. Com 640 px
de margem, o custo de ler é proporcional à largura total, e o ONNX Runtime já usa todos os núcleos em cada chamada.
No lote, cada linha é preenchida até a largura da maior, o que só acrescenta conta. Como a sonda na calibração já
refuta H1, os conjuntos de teste não foram rodados (T002 cancelada).

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — redações ≤ 6 s por página | **Refutada** (na calibração) | leitura 4,6 s individual → 5,0 s em lote (mediana por página) |
| H2 — CER não piora mais de 0,5 ponto | Não medida no teste | 40 / 40 textos idênticos nas linhas fictícias; confiança difere até 0,02 |
| H3 — 100 % LDF válido | Não medida | sem mudança na montagem do LDF |

## 2. Onde vai o tempo

Sonda [`probe_cost.py`](./harness/probe_cost.py), ambiente `EXP-008/envs/ppocr`, 20 páginas de calibração do
BRESSAY, alvo de 80 px (escalas 2×, 3× e 4×), mediana de 30 linhas por página. Modos de leitura rodados em
sequência na mesma página.

| Etapa | Mediana por página |
| :--- | ---: |
| Primeira detecção (escala original) | 0,74 s |
| Detecção na página ampliada | 4,17 s |
| Recorte | 0,03 s |
| **Leitura individual, margem 640 px (EXP-015)** | **4,56 s** |
| Leitura em lotes de 8, margem 640 px | 5,00 s |
| Leitura individual, sem margem | 2,90 s |

Sonda [`probe_batch.py`](./harness/probe_batch.py), 40 linhas fictícias: individual 2,9–3,6 s, em lote 3,2–3,8 s
(duas execuções), 40 / 40 textos iguais.

O custo se divide quase meio a meio entre a **detecção na página ampliada** (escala automática do EXP-013) e a
**margem de leitura** (EXP-014). Os tempos absolutos aqui saíram mais altos que os 7,4 s do EXP-015 (o EXP-015 rodou
pelo supervisor, em outro momento da máquina); a proporção entre as etapas é o que importa.

## 3. Consequências

* O pipeline do ADR-008 fica como está (leitura individual).
* Para chegar a 6 s, as alavancas são as duas medidas acima, e as duas mexem na qualidade: margem menor (320 px
  custou 0,8 ponto de CER de linha na validação do EXP-014) ou detecção numa escala menor que a da leitura. Ganhar
  1 a 2 s por página vale menos que pontos de CER enquanto o texto em português é rascunho. Por isso, o custo fica
  como limitação registrada, não como próximo experimento.

## 4. Reprodução

```powershell
$py = "experiments/EXP-008/envs/ppocr/.venv/Scripts/python.exe"
& $py -I experiments/EXP-016/harness/probe_batch.py
& $py -I experiments/EXP-016/harness/probe_cost.py
uv run --frozen --project experiments/EXP-002/envs/harness pytest -q experiments/EXP-016/tests
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-22`
