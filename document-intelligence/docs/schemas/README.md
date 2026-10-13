# Schemas do LDF

| Versão | Arquivo | Situação |
| :--- | :--- | :--- |
| **2.0** | [`src/leitorum_di/contracts/ldf/schemas/ldf-2.0.schema.json`](../../src/leitorum_di/contracts/ldf/schemas/ldf-2.0.schema.json) | **Fonte normativa atual.** Fica dentro do pacote para ser distribuída com o código; é a única cópia (um teste falha se aparecer outra). Descrição em [`docs/ldf.md`](../ldf.md). |
| 1.0 | [`ldf-1.0.schema.json`](./ldf-1.0.schema.json) | **Congelado.** Não é mais o contrato. Permanece aqui, byte a byte, porque os conversores dos EXP-002 e EXP-003 o leem por este caminho; alterá-lo quebraria a reprodução de experimentos aceitos. `tests/ldf/test_frozen.py` confere o hash. |

Não edite um schema publicado. Mudanças entram como arquivo novo (`ldf-2.1.schema.json`, e assim por diante),
conforme a regra de versões em [`docs/ldf.md`](../ldf.md) §6.
