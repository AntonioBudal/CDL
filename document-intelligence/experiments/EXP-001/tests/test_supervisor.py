"""Testes do supervisor: reconhecedor de referência, critérios de parada e portão de licença."""

import hashlib

from evaluate import evaluate
from supervisor import Limits, check_weights, license_gate, run_candidate

MIB = 1024 * 1024
# Os testes não dependem da memória livre da máquina; a checagem tem teste próprio.
NO_FREE_CHECK = {"min_free_system_bytes": 0}
RELAXED = Limits(**NO_FREE_CHECK)
ECHO = {"id": "echo-reference", "kind": "reference", "adapter": "adapters.echo:EchoRecognizer"}


def _fake(name, **options):
    adapter = f"adapters.fakes:{name}"
    return {"id": name, "kind": "reference", "adapter": adapter, "options": options}


def test_reference_recognizer_runs_end_to_end_with_zero_error(tiny_manifest):
    path, root, manifest = tiny_manifest
    result = run_candidate(ECHO, path, root, limits=RELAXED)
    assert result.status == "OK", result.stderr_tail
    assert [p["id"] for p in result.predictions] == [line["id"] for line in manifest["lines"]]
    assert all(p["elapsed_ms"] >= 0 for p in result.predictions)
    assert result.load_ms is not None and result.load_ms >= 0
    assert result.describe["id"] == "echo-reference"
    assert result.peak_rss_bytes is None or result.peak_rss_bytes > 0
    metrics = evaluate(manifest, result.predictions)
    assert metrics["cer_micro"] == metrics["wer_micro"] == 0.0
    assert metrics["missing"] == []


def test_noisy_recognizer_yields_expected_nonzero_error(tiny_manifest):
    path, root, manifest = tiny_manifest
    result = run_candidate(_fake("NoisyRecognizer"), path, root, limits=RELAXED)
    assert result.status == "OK", result.stderr_tail
    metrics = evaluate(manifest, result.predictions)
    assert 0 < metrics["cer_micro"] < 0.2
    assert metrics["wer_micro"] > 0


def test_corrupted_image_fails_the_run(tiny_manifest):
    path, root, manifest = tiny_manifest
    (root / manifest["lines"][5]["image"]).write_bytes(b"adulterado")
    result = run_candidate(ECHO, path, root, limits=RELAXED)
    assert result.status == "FAILED"
    assert any("SHA-256" in line for line in result.stderr_tail)


def test_memory_limit_aborts_candidate(tiny_manifest):
    path, root, _ = tiny_manifest
    limits = Limits(memory_bytes=150 * MIB, poll_interval_s=0.01, **NO_FREE_CHECK)
    result = run_candidate(_fake("MemoryHogRecognizer", total_mib=400), path, root, limits=limits)
    assert result.status == "ABORTED"
    assert result.reason.startswith("memory")
    assert result.peak_rss_bytes > 150 * MIB


def test_load_timeout_aborts_candidate(tiny_manifest):
    path, root, _ = tiny_manifest
    limits = Limits(load_timeout_s=1.0, **NO_FREE_CHECK)
    result = run_candidate(_fake("SlowLoadRecognizer", load_seconds=30), path, root, limits=limits)
    assert result.status == "ABORTED"
    assert result.reason.startswith("load timeout")
    assert result.wall_s < 15


def test_latency_limit_aborts_candidate_and_keeps_partial_predictions(tiny_manifest):
    path, root, manifest = tiny_manifest
    limits = Limits(latency_probe_lines=5, latency_abort_ms=50.0, **NO_FREE_CHECK)
    candidate = _fake("SlowLineRecognizer", line_seconds=0.12)
    result = run_candidate(candidate, path, root, limits=limits, warmup=0)
    assert result.status == "ABORTED"
    assert result.reason.startswith("latency")
    assert 5 <= len(result.predictions) < len(manifest["lines"])


def test_wall_time_limit_aborts_candidate(tiny_manifest):
    path, root, _ = tiny_manifest
    limits = Limits(wall_timeout_s=1.5, latency_abort_ms=10_000.0, **NO_FREE_CHECK)
    candidate = _fake("SlowLineRecognizer", line_seconds=0.3)
    result = run_candidate(candidate, path, root, limits=limits, warmup=0)
    assert result.status == "ABORTED"
    assert result.reason.startswith("wall time")


def test_crash_is_reported_as_failed_without_breaking_next_candidate(tiny_manifest):
    path, root, _ = tiny_manifest
    crashed = run_candidate(_fake("CrashingRecognizer"), path, root, limits=RELAXED)
    assert crashed.status == "FAILED"
    assert any("falha simulada" in line for line in crashed.stderr_tail)
    assert run_candidate(ECHO, path, root, limits=RELAXED).status == "OK"


def test_low_system_memory_skips_candidate(tiny_manifest):
    path, root, _ = tiny_manifest
    result = run_candidate(ECHO, path, root, limits=Limits(min_free_system_bytes=10**15))
    assert result.status in {"SKIPPED", "OK"}  # OK só onde a memória livre não é mensurável
    if result.status == "SKIPPED":
        assert result.predictions == [] and result.wall_s == 0.0


def test_license_gate_rules():
    assert license_gate({"id": "ref", "kind": "reference"})[0]
    assert license_gate({"license_status": "VERIFIED", "benchmark_allowed": True})[0]
    assert not license_gate({"license_status": "VERIFIED"})[0]
    assert not license_gate({"license_status": "NEEDS VALIDATION", "benchmark_allowed": True})[0]
    allowed, reason = license_gate(
        {"license_status": "NEEDS VALIDATION", "benchmark_allowed": True, "user_exception": "ok"}
    )
    assert allowed and "NEEDS VALIDATION" in reason
    assert not license_gate({"benchmark_allowed": True})[0]


def test_unverified_candidate_is_refused_before_any_process_starts(tiny_manifest):
    path, root, _ = tiny_manifest
    candidate = {
        "id": "sem-licenca",
        "adapter": "adapters.echo:EchoRecognizer",
        "license_status": "NEEDS VALIDATION",
        "benchmark_allowed": True,
    }
    result = run_candidate(candidate, path, root, limits=RELAXED)
    assert result.status == "REFUSED"
    assert result.predictions == [] and result.wall_s == 0.0 and result.exit_code is None


def test_weights_with_wrong_sha256_are_refused(tiny_manifest, tmp_path):
    path, root, _ = tiny_manifest
    weights = tmp_path / "weights"
    weights.mkdir()
    (weights / "model.bin").write_bytes(b"pesos de teste")
    good = hashlib.sha256(b"pesos de teste").hexdigest()
    candidate = {
        "id": "com-pesos",
        "adapter": "adapters.echo:EchoRecognizer",
        "license_status": "VERIFIED",
        "benchmark_allowed": True,
        "weights": {"files": {"model.bin": {"sha256": good}}},
    }
    assert check_weights(candidate, weights) == []
    assert run_candidate(candidate, path, root, limits=RELAXED, weights_dir=weights).status == "OK"

    candidate["weights"]["files"]["model.bin"]["sha256"] = "0" * 64
    refused = run_candidate(candidate, path, root, limits=RELAXED, weights_dir=weights)
    assert refused.status == "REFUSED" and "SHA-256 divergente" in refused.reason

    candidate["weights"]["files"]["ausente.bin"] = {"sha256": good}
    assert any("ausente" in problem for problem in check_weights(candidate, weights))
