"""EXP-023: métricas da organização (spec §8.2). Sem dependência externa.

Rótulos por caractere: só caracteres não brancos contam. O rótulo previsto de um caractere é a
seção da unidade que o contém. Fronteiras: sequência de rótulos por palavra (corrida de caracteres
não brancos).
"""

from __future__ import annotations

from collections import Counter

SECTIONS = ("summary", "explanation", "concepts", "references")
CODE = {"s": "summary", "e": "explanation", "c": "concepts", "r": "references"}


def predicted_chars(text: str, segments: list[dict]) -> list[str | None]:
    out: list[str | None] = [None] * len(text)
    for seg in segments:
        for i in range(seg["start"], seg["end"]):
            out[i] = seg["section"]
    return out


class Scores:
    """Acumula contagens de várias páginas."""

    def __init__(self) -> None:
        self.tp, self.fp, self.fn = Counter(), Counter(), Counter()
        self.unit_tp, self.unit_fp, self.unit_fn = Counter(), Counter(), Counter()
        self.chars = self.wrong = 0
        self.pk = []  # (erros, janelas)
        self.wd = []
        self.switch_pred = self.switch_gold = 0
        self.calibration = []  # (confiança, acertou)
        self.bound_tp = self.bound_fp = self.bound_fn = 0
        self.uncovered = 0
        self.times = []

    def add(
        self,
        text: str,
        gold: list[str],
        units: list[int],
        result: dict,
        elapsed_ms: float | None = None,
    ) -> None:
        pred = predicted_chars(text, result["segments"])
        for ch, g, p in zip(text, gold, pred, strict=False):
            if ch.isspace():
                continue
            g = CODE[g]
            self.chars += 1
            if p is None:
                self.uncovered += 1
            if p == g:
                self.tp[g] += 1
            else:
                self.wrong += 1
                self.fn[g] += 1
                if p:
                    self.fp[p] += 1
        # nível de unidade: rótulo de referência = maioria dos caracteres
        for seg, _marg in zip(
            result["segments"],
            result.get("marginals", [None] * len(result["segments"])),
            strict=False,
        ):
            span = [CODE[gold[i]] for i in range(seg["start"], seg["end"]) if not text[i].isspace()]
            if not span:
                continue
            g = Counter(span).most_common(1)[0][0]
            if seg["section"] == g:
                self.unit_tp[g] += 1
            else:
                self.unit_fn[g] += 1
                self.unit_fp[seg["section"]] += 1
            self.calibration.append((seg["confidence"], seg["section"] == g))
        # fronteiras por palavra
        gw, pw = [], []
        i = 0
        while i < len(text):
            if text[i].isspace():
                i += 1
                continue
            j = i
            while j < len(text) and not text[j].isspace():
                j += 1
            gw.append(Counter(CODE[gold[k]] for k in range(i, j)).most_common(1)[0][0])
            pw.append(Counter(pred[k] for k in range(i, j)).most_common(1)[0][0])
            i = j
        if len(gw) > 2:
            segments = 1 + sum(a != b for a, b in zip(gw, gw[1:], strict=False))
            k = max(2, round(len(gw) / segments / 2))
            errors_pk = errors_wd = windows = 0
            for s in range(len(gw) - k):
                g_b = sum(gw[t] != gw[t + 1] for t in range(s, s + k))
                p_b = sum(pw[t] != pw[t + 1] for t in range(s, s + k))
                errors_pk += (g_b > 0) != (p_b > 0)
                errors_wd += g_b != p_b
                windows += 1
            self.pk.append((errors_pk, windows))
            self.wd.append((errors_wd, windows))
        self.switch_gold += sum(a != b for a, b in zip(gw, gw[1:], strict=False))
        self.switch_pred += sum(a != b for a, b in zip(pw, pw[1:], strict=False))
        # fronteiras de unidade (trecho de origem), tolerância de 2 caracteres não brancos
        nonspace = [i for i, ch in enumerate(text) if not ch.isspace()]
        rank = {pos: r for r, pos in enumerate(nonspace)}
        gold_b = {rank[p] for p in nonspace[1:] if units[p] != units[nonspace[rank[p] - 1]]}
        pred_b = set()
        for seg in result["segments"][1:]:
            start = seg["start"]
            while start < len(text) and text[start].isspace():
                start += 1
            if start in rank:
                pred_b.add(rank[start])
        matched = set()
        for b in pred_b:
            hit = next((g for g in range(b - 2, b + 3) if g in gold_b and g not in matched), None)
            if hit is None:
                self.bound_fp += 1
            else:
                matched.add(hit)
                self.bound_tp += 1
        self.bound_fn += len(gold_b - matched)
        if elapsed_ms is not None:
            self.times.append(elapsed_ms)

    @staticmethod
    def _f1(tp, fp, fn, labels) -> tuple[float, dict]:
        per = {}
        for s in labels:
            p = tp[s] / (tp[s] + fp[s]) if tp[s] + fp[s] else 0.0
            r = tp[s] / (tp[s] + fn[s]) if tp[s] + fn[s] else 0.0
            per[s] = {
                "precision": round(p, 4),
                "recall": round(r, 4),
                "f1": round(2 * p * r / (p + r), 4) if p + r else 0.0,
            }
        return sum(v["f1"] for v in per.values()) / len(labels), per

    def report(self) -> dict:
        macro, per = self._f1(self.tp, self.fp, self.fn, SECTIONS)
        unit_macro, _ = self._f1(self.unit_tp, self.unit_fp, self.unit_fn, SECTIONS)
        bins = [[0, 0, 0.0] for _ in range(10)]
        for conf, ok in self.calibration:
            b = min(9, int(conf * 10))
            bins[b][0] += 1
            bins[b][1] += ok
            bins[b][2] += conf
        n = max(1, len(self.calibration))
        ece = sum(abs(c / cnt - ok / cnt) * cnt for cnt, ok, c in bins if cnt) / n
        bp = (
            self.bound_tp / (self.bound_tp + self.bound_fp)
            if self.bound_tp + self.bound_fp
            else 0.0
        )
        br = (
            self.bound_tp / (self.bound_tp + self.bound_fn)
            if self.bound_tp + self.bound_fn
            else 0.0
        )
        times = sorted(self.times)
        return {
            "macro_f1_chars": round(macro, 4),
            "macro_f1_units": round(unit_macro, 4),
            "per_section_chars": per,
            "char_error_effort": round(self.wrong / max(1, self.chars), 4),
            "pk": round(sum(e for e, _ in self.pk) / max(1, sum(w for _, w in self.pk)), 4),
            "windowdiff": round(sum(e for e, _ in self.wd) / max(1, sum(w for _, w in self.wd)), 4),
            "fragmentation": round(self.switch_pred / max(1, self.switch_gold), 3),
            "ece": round(ece, 4),
            "unit_boundary_f1": round(2 * bp * br / (bp + br), 4) if bp + br else 0.0,
            "uncovered_chars": self.uncovered,
            "latency_ms_p50": round(times[len(times) // 2], 2) if times else None,
            "latency_ms_p95": round(times[min(len(times) - 1, int(len(times) * 0.95))], 2)
            if times
            else None,
            "pages": len(self.wd),
        }
