"""F-DI-13.03 — catálogo de procedência: fontes, itens, armazenamento por conteúdo, situações
de uso, revisão, rejeição que apaga e contamina, ciclos de treino, tetos e integridade. Só dados
fictícios."""

from __future__ import annotations

import io
import json

import pytest
from PIL import Image, ImageDraw

from tools.catalogo import BudgetExceededError, Catalog, CatalogError
from tools.catalogo.images import LINE_HEIGHT


def line_png(seed: int, width: int = 300, height: int = 40) -> bytes:
    image = Image.new("RGB", (width, height), (250, 248, 240))
    draw = ImageDraw.Draw(image)
    for k in range(6):
        x = 10 + 45 * k + seed % 7
        draw.line([(x, 30), (x + 25, 8 + seed % 5)], fill=(20, 20, 60), width=3)
    out = io.BytesIO()
    image.save(out, "PNG")
    return out.getvalue()


@pytest.fixture
def cat(tmp_path):
    catalog = Catalog(tmp_path / "dados")
    catalog.add_source(
        "fonte-a",
        name="Fonte A fictícia",
        url="https://exemplo.org/a",
        license="CC-BY-4.0",
        conditions=["by"],
        status="APPROVED",
        access="api",
        terms=b"termos ficticios A",
        terms_url="https://exemplo.org/a/termos",
    )
    catalog.add_source(
        "fonte-p",
        name="Fonte P fictícia",
        url="https://exemplo.org/p",
        license=None,
        conditions=[],
        status="PENDING_REVIEW",
        access="download",
    )
    catalog.add_source(
        "fonte-x",
        name="Fonte X fictícia",
        url="https://exemplo.org/x",
        license="pesquisa",
        conditions=["nc"],
        status="EXPERIMENT_ONLY",
        access="download",
    )
    yield catalog
    catalog.close()


def test_ingest_stores_normalized_line_and_is_idempotent(cat):
    first = cat.ingest_line(
        "fonte-a",
        "1",
        image=line_png(1),
        text="linha fictícia um",
        url="https://exemplo.org/a/1",
        language="fra",
        split="train",
    )
    assert first.created and first.stored
    path = cat.file_path(first.sha256)
    with Image.open(path) as image:
        assert image.mode == "L" and image.height == LINE_HEIGHT and image.format == "PNG"
    again = cat.ingest_line("fonte-a", "1", image=line_png(1), text="linha fictícia um")
    assert not again.created and again.item_id == first.item_id
    assert cat.counts()["items"] == 1 and cat.counts()["files"] == 1


def test_same_image_in_two_items_is_stored_once(cat):
    a = cat.ingest_line("fonte-a", "1", image=line_png(3), text="x")
    b = cat.ingest_line("fonte-a", "2", image=line_png(3), text="x")
    assert a.sha256 == b.sha256
    assert cat.counts() == {"sources": 3, "items": 2, "files": 1, "runs": 0}


def test_pending_source_keeps_only_metadata(cat):
    result = cat.ingest_line(
        "fonte-p", "9", image=line_png(9), text="pendente", url="https://exemplo.org/p/9"
    )
    assert result.created and not result.stored and result.sha256 is None
    item = cat.item(result.item_id)
    assert item["status"] == "PENDING_REVIEW" and item["source_url"] == "https://exemplo.org/p/9"
    assert cat.counts()["files"] == 0


def test_pending_grouped_by_source_and_reason(cat):
    for n in range(3):
        cat.ingest_line("fonte-p", str(n), image=None, text="t")
    groups = cat.pending()
    assert groups == [{"source_id": "fonte-p", "reason": "sem_licenca", "items": 3}]


def test_approving_source_moves_all_items(cat):
    for n in range(3):
        cat.ingest_line("fonte-p", str(n), image=None, text="t")
    changed = cat.review(
        "source",
        "fonte-p",
        "APPROVED",
        reason="licença CC-BY confirmada",
        evidence="https://exemplo.org/p/licenca",
    )
    assert changed == 3
    assert {cat.item(f"fonte-p:{n}")["status"] for n in range(3)} == {"APPROVED"}
    assert cat.needs_download() == ["fonte-p:0", "fonte-p:1", "fonte-p:2"]
    assert cat.pending() == []


def test_reject_deletes_files_blocks_and_taints_runs(cat):
    kept = cat.ingest_line("fonte-a", "1", image=line_png(1), text="a")
    shared_a = cat.ingest_line("fonte-a", "2", image=line_png(2), text="b")
    shared_b = cat.ingest_line("fonte-x", "2", image=line_png(2), text="b")
    run = cat.start_run(
        "experimento", sources=["fonte-a", "fonte-x"], recipe="r1", commit="abc", seed=1
    )
    cat.review("item", shared_a.item_id, "REJECTED", reason="licença revogada (fictício)")
    assert cat.item(shared_a.item_id)["status"] == "REJECTED"
    assert cat.file_path(shared_b.sha256).exists()  # ainda usado por outro item
    assert cat.file_path(kept.sha256).exists()
    cat.review("item", shared_b.item_id, "REJECTED", reason="idem")
    assert not cat.file_path(shared_b.sha256).exists()
    assert cat.is_blocked(sha256=shared_b.sha256) and cat.is_blocked(item_id=shared_a.item_id)
    refused = cat.ingest_line("fonte-a", "99", image=line_png(2), text="b")
    assert not refused.created and refused.reason == "bloqueado"
    tainted = cat.run(run)
    assert tainted["tainted"] and shared_a.item_id in tainted["tainted_reason"]


def test_product_run_only_approved_and_promotion_check(cat):
    cat.ingest_line("fonte-a", "1", image=line_png(1), text="a")
    cat.ingest_line("fonte-x", "1", image=line_png(5), text="x")
    with pytest.raises(CatalogError):
        cat.start_run("produto", sources=["fonte-a", "fonte-x"], recipe="r", commit="c", seed=0)
    run = cat.start_run("produto", sources=["fonte-a"], recipe="r", commit="c", seed=0)
    assert cat.check_promotion(run) == (True, [])
    exp = cat.start_run(
        "experimento", sources=["fonte-a", "fonte-x"], recipe="r", commit="c", seed=0
    )
    ok, problems = cat.check_promotion(exp)
    assert not ok and any("EXPERIMENT_ONLY" in p for p in problems)
    cat.review("item", "fonte-a:1", "REJECTED", reason="teste")
    ok, problems = cat.check_promotion(run)
    assert not ok and any("contaminado" in p for p in problems)


def test_run_records_status_and_license_at_the_time(cat):
    cat.ingest_line("fonte-a", "1", image=line_png(1), text="a")
    run = cat.start_run("experimento", sources=["fonte-a"], recipe="r", commit="c", seed=7)
    items = cat.run_items(run)
    assert items == [
        {
            "item_id": "fonte-a:1",
            "sha256": cat.item("fonte-a:1")["sha256"],
            "status": "APPROVED",
            "license": "CC-BY-4.0",
        }
    ]


def test_splits_filter_in_runs(cat):
    cat.ingest_line("fonte-a", "1", image=line_png(1), text="a", split="train")
    cat.ingest_line("fonte-a", "2", image=line_png(2), text="b", split="test")
    run = cat.start_run(
        "experimento", sources=["fonte-a"], splits=["train"], recipe="r", commit="c", seed=0
    )
    assert [i["item_id"] for i in cat.run_items(run)] == ["fonte-a:1"]


def test_training_summary_has_no_text(cat):
    cat.ingest_line("fonte-a", "1", image=line_png(1), text="segredo fictício que não pode vazar")
    run = cat.start_run("experimento", sources=["fonte-a"], recipe="r", commit="c", seed=0)
    summary = cat.training_summary(run)
    dumped = json.dumps(summary, ensure_ascii=False)
    assert "segredo" not in dumped
    assert summary["sources"][0]["source_id"] == "fonte-a" and summary["sources"][0]["items"] == 1
    assert summary["sources"][0]["conditions"] == ["by"]


def test_budget_refuses_ingest(tmp_path):
    catalog = Catalog(tmp_path / "dados", budgets={"linhas": 10})
    catalog.add_source(
        "f", name="F", url="u", license="CC0", conditions=[], status="APPROVED", access="api"
    )
    with pytest.raises(BudgetExceededError):
        catalog.ingest_line("f", "1", image=line_png(1), text="a")
    catalog.close()


def test_usage_and_verify(cat):
    result = cat.ingest_line("fonte-a", "1", image=line_png(1), text="a")
    usage = {row["kind"]: row for row in cat.usage()}
    assert usage["linhas"]["bytes"] > 0 and usage["linhas"]["budget"] == 45 * 1024**3
    assert cat.verify() == []
    path = cat.file_path(result.sha256)
    path.write_bytes(path.read_bytes() + b"x")
    assert cat.verify() == [result.sha256]


def test_terms_saved_with_hash(cat):
    source = cat.source("fonte-a")
    assert (
        source["terms_sha256"]
        and cat.file_path(source["terms_sha256"]).read_bytes() == b"termos ficticios A"
    )


def test_page_phash_marks_near_duplicates(cat):
    page = Image.new("RGB", (400, 600), "white")
    ImageDraw.Draw(page).rectangle([50, 50, 350, 120], fill="black")
    a, b = io.BytesIO(), io.BytesIO()
    page.save(a, "PNG")
    page.save(b, "JPEG", quality=80)  # mesma página, arquivo diferente
    first = cat.ingest_page("fonte-a", "p1", image=a.getvalue())
    second = cat.ingest_page("fonte-a", "p2", image=b.getvalue())
    assert first.sha256 != second.sha256
    assert second.near_duplicate_of == first.item_id


def test_unknown_status_and_source_refused(cat):
    with pytest.raises(CatalogError):
        cat.ingest_line("nao-existe", "1", image=None, text="")
    with pytest.raises(CatalogError):
        cat.review("item", "fonte-a:nada", "APPROVED", reason="x")
    with pytest.raises(CatalogError):
        cat.add_source(
            "z", name="Z", url="u", license=None, conditions=[], status="TALVEZ", access="api"
        )


# ---------------------------------------------------------------- importador do EXP-043


@pytest.mark.parametrize(
    ("license_name", "status", "expected"),
    [
        ("CC-BY-4.0", "APPROVED", ["by"]),
        ("CC-BY-SA 4.0", "APPROVED", ["by", "sa"]),
        ("CC-BY-NC-4.0", "APPROVED_NC", ["by", "nc"]),
        ("pesquisa não comercial", "EXPERIMENT_ONLY", ["nc"]),
    ],
)
def test_conditions_from_license(license_name, status, expected):
    from tools.catalogo.importar_exp043 import conditions_of

    assert conditions_of(license_name, status) == expected


def test_import_samples_is_idempotent(tmp_path):
    from tools.catalogo.importar_exp043 import import_samples

    samples = tmp_path / "amostras"
    folder = samples / "Ficticio-line"
    (folder / "arquivos").mkdir(parents=True)
    (folder / "arquivos" / "termos.termos").write_bytes(b"termos")
    rows = []
    for n in range(3):
        name = f"img{n}.img"
        (folder / "arquivos" / name).write_bytes(line_png(n))
        rows.append(
            {
                "source": "Teklia/Ficticio-line",
                "source_url": "https://exemplo.org/f",
                "row_index": n,
                "split": "train",
                "file": name,
                "sha256": f"{n:064d}",
                "license": "CC-BY-4.0",
                "status": "APPROVED",
                "language": "fra",
                "era": "1900",
                "text": f"texto {n}",
                "terms_sha256": "termos",
                "terms_url": "https://exemplo.org/f/termos",
            }
        )
    rows.append(rows[0])  # linha repetida no manifesto
    pending = samples / "Pendente-line"
    pending.mkdir()
    (pending / "manifesto.jsonl").write_text(
        json.dumps({**rows[0], "status": "PENDING_REVIEW"}), "utf-8"
    )
    (folder / "manifesto.jsonl").write_text("\n".join(json.dumps(r) for r in rows), "utf-8")
    catalog = Catalog(tmp_path / "dados")
    first = import_samples(catalog, samples)
    assert first == {
        "teklia-ficticio": {
            "manifest_rows": 4,
            "unique": 3,
            "created": 3,
            "existing": 1,
            "refused": 0,
        }
    }
    second = import_samples(catalog, samples)
    assert second["teklia-ficticio"]["created"] == 0 and catalog.counts()["items"] == 3
    assert catalog.source("teklia-ficticio")["terms_sha256"]
    catalog.close()


def test_run_with_explicit_items_and_generated_only(cat):
    a = cat.ingest_line("fonte-a", "1", image=line_png(1), text="a")
    cat.ingest_line("fonte-a", "2", image=line_png(2), text="b")
    run = cat.start_run("experimento", item_ids=[a.item_id], recipe="r", commit="c", seed=0)
    assert [i["item_id"] for i in cat.run_items(run)] == [a.item_id]
    synthetic = cat.start_run(
        "experimento",
        recipe="r",
        commit="c",
        seed=0,
        notes="sintético: gerador X, semente 1, 8000 linhas",
    )
    assert cat.run_items(synthetic) == [] and "sintético" in cat.run(synthetic)["notes"]
    pending = cat.ingest_line("fonte-p", "1", image=None, text="p")
    with pytest.raises(CatalogError):
        cat.start_run("experimento", item_ids=[pending.item_id], recipe="r", commit="c", seed=0)
    with pytest.raises(CatalogError):
        cat.start_run(
            "experimento", sources=["fonte-a"], item_ids=[a.item_id], recipe="r", commit="c", seed=0
        )
