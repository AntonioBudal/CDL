# Cópia literal de document-intelligence/experiments/EXP-025/harness/organizer_v2.py (commit f8ab9e0),
# sem mudança de lógica: a paridade com o experimento é conferida por tests/test_organizer_parity.py.
# Adaptações: o import do motor do EXP-023 (aqui ``engine``) e ``load(path)`` → ``from_artifact(data)``,
# porque a leitura do arquivo e o SHA-256 ficam no ``loader``.
# Não editar aqui sem repetir a mudança no experimento e regenerar o fixture de paridade.
"""EXP-025: Organizador v2, implementação de referência em Python puro (o que o produto porta).

É o Organizador do EXP-023 com 4 colunas a mais: pistas fixas de referência (lista Markdown com
"Título — Autor", link Markdown, linha de URL e "Título (Autor, ano)"). As expressões vêm do
EXP-024 e vão no artefato (``extra_cues``); ``from_artifact`` confere que são as mesmas daqui.

Sem estado por usuário, sem aprendizado online: os pesos são fixos no ``organizer-v2.json``.
"""

from __future__ import annotations

import re

from app.services.organizer import engine as org

# nome: (expressão, modo). "match" ancora no início da unidade; "search" procura em qualquer ponto.
EXTRA_CUES: dict[str, tuple[str, str]] = {
    "ref_md_title_author": (r"^\s*(?:[-*•]|\d{1,2}[.)])\s+\S.{0,120}?\s[—–]\s+\S", "match"),
    "ref_md_link": (r"\[[^\]\n]{2,}\]\((?:https?://|www\.)[^)\s]+\)", "search"),
    "ref_url_line": (r"^\s*(?:[-*•]\s+)?(?:https?://|www\.)\S+\s*$", "match"),
    "ref_title_author_year": (
        r"\([A-ZÁ-Ú][^()\n]{2,60},\s*(?:1[5-9]\d\d|20\d\d)\)\s*\.?\s*$",
        "search",
    ),
}
EXTRA_NAMES = list(EXTRA_CUES)
_COMPILED = {name: (re.compile(pattern), mode) for name, (pattern, mode) in EXTRA_CUES.items()}


def cue_values(text: str) -> list[float]:
    out = []
    for name in EXTRA_NAMES:
        regex, mode = _COMPILED[name]
        hit = regex.match(text) if mode == "match" else regex.search(text)
        out.append(float(bool(hit)))
    return out


class OrganizerV2(org.Organizer):
    """Organizador do EXP-023 com as pistas novas acrescentadas ao vetor de cada unidade."""

    def analyse(self, text, layout=None, options=None, centroids=None):
        units, lines, vecs, xs = super().analyse(text, layout, options, centroids)
        base = len(self.model.feature_names) - len(EXTRA_NAMES)
        xs = [x[:base] + cue_values(u.text) for x, u in zip(xs, units, strict=False)]
        return units, lines, vecs, xs


def from_artifact(data: dict) -> OrganizerV2:
    expected = {name: {"pattern": p, "mode": m} for name, (p, m) in EXTRA_CUES.items()}
    if data.get("extra_cues") != expected:
        raise ValueError("as pistas do artefato não são as desta implementação")
    if data["feature_names"][-len(EXTRA_NAMES) :] != EXTRA_NAMES:
        raise ValueError("as colunas novas precisam ser as últimas do vetor")
    return OrganizerV2(org.Model.from_json(data))
