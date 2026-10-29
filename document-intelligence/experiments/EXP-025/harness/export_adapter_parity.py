"""EXP-025, F05: casos de paridade do adaptador para a feature 091-C do Leitorum (dados fictícios).

Fluxo de 40 páginas de adaptação dos fluxos de VALIDAÇÃO do EXP-024: 20 do perfil P1 (usuário A) e
20 do P4 (usuário B), intercaladas, cada perfil com os seus livros, no regime R1. Em cada passo:

- o registro ``leitorum-feedback/1`` que o Leitorum gravaria e o livro;
- a sugestão esperada **antes** de aprender (trechos, seção, confiança e "conferir");
- o código do ``learn``, a norma de ΔW, ``reviewed`` e o SHA-256 do estado serializado depois.

O Leitorum copia ``artifacts/adapter-parity-v2.json`` e exige o mesmo em cada passo.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter

import adapter_deps  # noqa: F401  (caminhos)
import adapter_v2 as av
import feedback_doc
import organizer_v2 as v2
import safety_gate  # EXP-024
import simulator as sim  # EXP-024
import state as st  # EXP-024
import streams  # EXP-024
from evaluate_adapter import ART


def flow() -> list[tuple[str, dict]]:
    a = streams.stream("P1", "val")["adapt"][:20]
    b = streams.stream("P4", "val")["adapt"][:20]
    out = []
    for pa, pb in zip(a, b, strict=True):
        out += [("u-a", pa), ("u-b", pb)]
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    artifact_sha = (ART / "organizer-v2.sha256").read_text(encoding="utf-8").strip()
    adapter = av.AdapterV2(v2.load(), artifact_sha)
    states = {user: adapter.new_state(user) for user in ("u-a", "u-b")}
    steps = []
    for user, page in flow():
        state = states[user]
        seen = {}

        def organize(text, layout, book, seen=seen, state=state):
            seen["result"] = adapter.organize(state, text, layout, book)
            return seen["result"]

        feedback, _truth = sim.session(page, "R1", organize)
        result = seen["result"]
        document = feedback_doc.to_document(feedback, result["segments"])
        code = adapter.learn(state, document, page["book_id"])
        o = state["organizer"]
        steps.append(
            {
                "user": user,
                "book_id": page["book_id"],
                "document": document,
                "expected_segments": [
                    {k: s[k] for k in ("start", "end", "section", "confidence", "review")}
                    for s in result["segments"]
                ],
                "code": code,
                "delta_norm": round(safety_gate.frobenius(o["delta_W"], o["delta_b"]), 6),
                "reviewed": state["reviewed"],
                "guard_allows": adapter.guard_allows(state),
                "state_sha256": hashlib.sha256(st.dumps(state).encode("utf-8")).hexdigest(),
            }
        )
    body = json.dumps(
        {
            "license": "MIT — páginas fictícias do EXP-024",
            "artifact_sha256": artifact_sha,
            "params": av.PARAMS,
            "steps": steps,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    (ART / "adapter-parity-v2.json").write_text(body, encoding="utf-8", newline="\n")
    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    (ART / "adapter-parity-v2.sha256").write_text(sha + "\n", encoding="utf-8", newline="\n")
    codes = Counter(s["code"] for s in steps)
    print(f"{len(steps)} passos; códigos {dict(codes)}")
    print(f"{len(body) / 1e6:.2f} MB; sha256 {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
