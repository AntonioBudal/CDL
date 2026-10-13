"""Conversor de referência: layout e ordem de leitura → LDF 2.0, sem lacunas."""

import json
from pathlib import Path

import pytest

from leitorum_di.contracts.ldf import (
    LDFValidationError,
    build_document,
    component,
    rectification_from_corners,
    validate,
)
from leitorum_di.contracts.ldf.geometry import to_rectified, to_source

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "dataset" / "fixtures" / "exp-003" / "test-manifest.json"
SHA = "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a"
IMAGE = {"filename": "pagina_ficticia.png", "width": 1200, "height": 1600, "sha256": SHA}
LAYOUT = {
    "component": component("detector-ficticio", "0.1.0", license="MIT", license_status="VERIFIED")
}
ORDER = {"component": component("ordenador-ficticio", "0.1.0")}
STAGES = {"layout": LAYOUT, "reading_order": ORDER}
WHEN = "2026-10-12T20:00:00Z"

LINES = [
    {"bbox": [100, 100, 700, 150], "score": 0.97},
    {"bbox": [100, 220, 800, 270]},
    {"bbox": [880, 220, 1120, 262]},
]
REGIONS = [
    {"type": "title", "bbox": [90, 90, 710, 160]},
    {"type": "paragraph", "bbox": [90, 210, 810, 340], "score": 0.9},
    {"type": "margin_note", "bbox": [870, 210, 1130, 270]},
    {"type": "graphic_box", "bbox": [150, 500, 900, 900]},
]


def build(**changes):
    arguments = {
        "image": IMAGE,
        "lines": LINES,
        "regions": REGIONS,
        "reading_order": [0, 1, 2, 3],
        "stages": STAGES,
        "created_at": WHEN,
    }
    arguments.update(changes)
    return build_document(**arguments)


def test_graphic_box_keeps_its_region_and_its_place_in_the_reading_order():
    document = build()
    graphic = document["structure"]["regions"][3]
    assert graphic == {
        "id": "region_004",
        "type": "graphic",
        "bbox": [150, 500, 900, 900],
        "line_ids": [],
    }
    assert document["structure"]["reading_order"][-1] == "region_004"
    assert validate(document) == []


def test_layout_only_page_declares_what_did_not_run():
    document = build()
    stages = document["pipeline"]["stages"]
    assert stages["layout"]["status"] == stages["reading_order"]["status"] == "completed"
    assert [stages[n]["status"] for n in ("recognition", "semantics", "diagrams")] == [
        "not_run"
    ] * 3
    assert all(
        "text" not in line and "confidence" not in line for line in document["recognition"]["lines"]
    )
    assert "semantics" not in document
    assert document["recognition"]["lines"][0]["detection_confidence"] == 0.97
    assert stages["layout"]["component"]["license_status"] == "VERIFIED"


def test_lines_are_assigned_to_the_region_that_contains_them():
    regions = build()["structure"]["regions"]
    assert [region["line_ids"] for region in regions] == [
        ["line_001"],
        ["line_002"],
        ["line_003"],
        [],
    ]


def test_explicit_membership_is_respected():
    regions = [dict(REGIONS[0], lines=[1]), dict(REGIONS[1], lines=[0]), REGIONS[2], REGIONS[3]]
    built = build(regions=regions)["structure"]["regions"]
    assert [region["line_ids"] for region in built] == [["line_002"], ["line_001"], [], []]


def test_tilted_line_keeps_its_outline():
    line = {"bbox": [0, 0, 1, 1], "polygon": [[200, 380], [200, 320], [800, 300], [800, 360]]}
    document = build(lines=[line], regions=[], reading_order=[])
    built = document["recognition"]["lines"][0]
    assert built["polygon"] == [[200, 380], [200, 320], [800, 300], [800, 360]]
    assert built["bbox"] == [200, 300, 800, 380]


def test_counterclockwise_outline_is_normalized():
    line = {"bbox": [0, 0, 1, 1], "polygon": [[800, 360], [800, 300], [200, 320], [200, 380]]}
    built = build(lines=[line], regions=[], reading_order=[])["recognition"]["lines"][0]
    assert built["polygon"] == [[200, 380], [200, 320], [800, 300], [800, 360]]


def test_geometry_is_clipped_to_the_image():
    region = {"type": "paragraph", "bbox": [-20, 1500, 400, 1650]}
    line = {"bbox": [0, 0, 1, 1], "polygon": [[1100, 100], [1250, 100], [1250, 150], [1100, 150]]}
    document = build(lines=[line], regions=[region], reading_order=[0])
    assert document["structure"]["regions"][0]["bbox"] == [0, 1500, 400, 1600]
    assert document["recognition"]["lines"][0]["bbox"] == [1100, 100, 1200, 150]


def test_rectified_coordinates_go_back_to_the_original_photo():
    corners = [[60, 90], [1150, 40], [1180, 1560], [30, 1500]]
    rectification = rectification_from_corners(corners, [1000, 1400], "contorno-ficticio")
    line = {"bbox": [100, 200, 600, 250]}
    document = build(
        lines=[line],
        regions=[{"type": "paragraph", "bbox": [90, 190, 610, 260]}],
        reading_order=[0],
        rectification=rectification,
        input_frame="rectified",
    )
    stored = document["coordinate_space"]["rectification"]
    assert stored["source_quad"] == corners and stored["output_size"] == [1000, 1400]
    built = document["recognition"]["lines"][0]
    expected = [
        to_source(stored, corner) for corner in ([100, 200], [600, 200], [600, 250], [100, 250])
    ]
    for point, original in zip(built["polygon"], expected, strict=True):
        assert point == pytest.approx(original, abs=0.01)
    # ida e volta: da foto original para a imagem retificada, dentro de 1 px
    for point, corner in zip(
        built["polygon"], ([100, 200], [600, 200], [600, 250], [100, 250]), strict=True
    ):
        assert to_rectified(stored, point) == pytest.approx(corner, abs=1.0)
    assert document["structure"]["regions"][0]["line_ids"] == ["line_001"]


def test_recognized_text_requires_the_recognition_stage():
    lines = [dict(LINES[0], text="texto fictício", confidence=0.8)]
    with pytest.raises(LDFValidationError) as error:
        build(lines=lines, regions=[], reading_order=[])
    assert {issue.code for issue in error.value.issues} == {"R7"}
    stages = dict(STAGES, recognition={"component": component("htr-ficticio", "0.1.0")})
    document = build(lines=lines, regions=[], reading_order=[], stages=stages)
    assert document["recognition"]["lines"][0]["text"] == "texto fictício"


def test_failed_stage_is_recorded_and_the_rest_stays_usable():
    stages = dict(STAGES, recognition={"error": "memória insuficiente", "elapsed_ms": 31.4})
    stage = build(stages=stages)["pipeline"]["stages"]["recognition"]
    assert stage == {"status": "failed", "error": "memória insuficiente", "elapsed_ms": 31.4}


def test_empty_page():
    document = build_document(image=IMAGE, lines=[], regions=[], created_at=WHEN)
    assert validate(document) == []
    assert {s["status"] for s in document["pipeline"]["stages"].values()} == {"not_run"}


def test_document_id_is_stable_for_the_same_image():
    assert build()["document_id"] == build()["document_id"]


@pytest.mark.parametrize(
    "changes",
    [
        {"regions": [{"type": "table", "bbox": [1, 1, 5, 5]}], "reading_order": []},
        {"stages": {"ocr": LAYOUT}},
        {"input_frame": "rectified"},
        {"input_frame": "other"},
        {
            "lines": [
                {
                    "bbox": [2000, 2000, 2100, 2050],
                    "polygon": [[2000, 2000], [2100, 2000], [2100, 2050]],
                }
            ]
        },
    ],
)
def test_unsupported_input_is_refused(changes):
    with pytest.raises(ValueError):
        build(**changes)


def test_layout_without_the_layout_stage_is_refused():
    with pytest.raises(LDFValidationError):
        build(stages={})


def _convert(page):
    """Converte uma página do manifesto do EXP-003 (layout verdadeiro, sem o texto)."""
    line_index = {line["id"]: i for i, line in enumerate(page["lines"])}
    block_index = {block["id"]: i for i, block in enumerate(page["blocks"])}
    transform = page.get("degradation", {}).get("transform") or {}
    rectification = rectification_from_corners(
        page["page_corners"],
        transform.get("page_size", [page["width"], page["height"]]),
        "manifesto",
    )
    return build_document(
        image={
            "filename": Path(page["image"]).name,
            "width": page["width"],
            "height": page["height"],
            "sha256": page["sha256"],
        },
        lines=[{"bbox": line["bbox"], "polygon": line.get("polygon")} for line in page["lines"]],
        regions=[
            {
                "type": block["type"],
                "bbox": block["bbox"],
                "lines": [line_index[ref] for ref in block["line_ids"]],
            }
            for block in page["blocks"]
        ],
        reading_order=[block_index[ref] for ref in page["reading_order"]],
        stages={
            "layout": {"component": component("layout-verdadeiro-exp-003", "1")},
            "reading_order": {"component": component("ordem-verdadeira-exp-003", "1")},
        },
        rectification=rectification,
        created_at=WHEN,
    )


def test_exp_003_test_pages_convert_without_gaps():
    """SC-002: as 180 páginas de teste, zero regiões descartadas, caixas gráficas na ordem."""
    pages = json.loads(MANIFEST.read_text(encoding="utf-8"))["pages"]
    assert len(pages) == 180
    graphics = 0
    for page in pages:
        document = _convert(page)
        regions = document["structure"]["regions"]
        order = document["structure"]["reading_order"]
        assert len(regions) == len(page["blocks"]), page["id"]
        assert len(document["recognition"]["lines"]) == len(page["lines"]), page["id"]
        assert len(order) == len(page["reading_order"]), page["id"]
        graphic_ids = [region["id"] for region in regions if region["type"] == "graphic"]
        assert set(graphic_ids) <= set(order), page["id"]
        assert sum(len(r["line_ids"]) for r in regions) == sum(
            len(b["line_ids"]) for b in page["blocks"]
        )
        assert all("text" not in line for line in document["recognition"]["lines"])
        graphics += len(graphic_ids)
    assert graphics == 102  # as mesmas 102 caixas que o LDF 1.0 deixava fora da ordem (EXP-003 §5)
