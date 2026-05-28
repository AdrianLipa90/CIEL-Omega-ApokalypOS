from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from noema_holonomic_doctor import DoctorConfig, noema_ls, run_doctor_cycle
from noema_holonomic_doctor.checks import (
    Finding,
    check_inverted_rh,
    check_rh_pipeline_hook,
    run_static_checks,
)
from noema_holonomic_doctor.manifest import ManifestEntry, manifest_digest, sha256_bytes
from noema_holonomic_doctor.metrics import (
    closure_error,
    d_lambda,
    doctor_cost,
    epsilon_neutrino,
    euler_berry_phase,
)
from noema_holonomic_doctor.report import DoctorReport, utc_stamp, write_append_only_report


# ---------------------------------------------------------------------------
# noema_ls tests
# ---------------------------------------------------------------------------


def test_noema_ls_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "b.json").write_text('{"x": 1}\n', encoding="utf-8")

    first = noema_ls(tmp_path)
    second = noema_ls(tmp_path)

    assert first == second
    assert [entry.path for entry in first] == ["a.py", "b.json"]
    assert all(len(entry.sha256) == 64 for entry in first)


def test_noema_ls_empty_directory(tmp_path: Path) -> None:
    result = noema_ls(tmp_path)
    assert result == []


def test_noema_ls_excludes_default_dirs(tmp_path: Path) -> None:
    (tmp_path / "real.py").write_text("x = 1\n", encoding="utf-8")
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\n", encoding="utf-8")
    pycache = tmp_path / "__pycache__"
    pycache.mkdir()
    (pycache / "mod.pyc").write_bytes(b"\x00")

    result = noema_ls(tmp_path)

    paths = [entry.path for entry in result]
    assert paths == ["real.py"]
    assert not any(".git" in p for p in paths)
    assert not any("__pycache__" in p for p in paths)


def test_noema_ls_excludes_all_default_dir_names(tmp_path: Path) -> None:
    default_excludes = [
        ".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
        "node_modules", ".venv", "venv", "dist", "build",
    ]
    (tmp_path / "keep.txt").write_text("keep\n", encoding="utf-8")
    for name in default_excludes:
        d = tmp_path / name
        d.mkdir()
        (d / "file.txt").write_text("excluded\n", encoding="utf-8")

    result = noema_ls(tmp_path)

    assert [entry.path for entry in result] == ["keep.txt"]


def test_noema_ls_custom_excludes(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    custom_dir = tmp_path / "custom_skip"
    custom_dir.mkdir()
    (custom_dir / "b.py").write_text("y = 2\n", encoding="utf-8")

    result = noema_ls(tmp_path, excludes=["custom_skip"])

    paths = [entry.path for entry in result]
    assert "a.py" in paths
    assert not any("custom_skip" in p for p in paths)


def test_noema_ls_nested_files_sorted(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    (tmp_path / "z.py").write_text("z\n", encoding="utf-8")
    (tmp_path / "a.py").write_text("a\n", encoding="utf-8")
    (sub / "c.py").write_text("c\n", encoding="utf-8")

    result = noema_ls(tmp_path)
    paths = [entry.path for entry in result]

    # Sorted by path (rglob returns sorted due to sorted() call on paths)
    assert paths == sorted(paths)


def test_noema_ls_entry_fields(tmp_path: Path) -> None:
    content = b"hello world\n"
    (tmp_path / "hello.py").write_bytes(content)

    result = noema_ls(tmp_path)

    assert len(result) == 1
    entry = result[0]
    assert entry.path == "hello.py"
    assert entry.size == len(content)
    assert entry.sha256 == sha256_bytes(content)
    assert entry.suffix == ".py"


def test_noema_ls_suffix_for_various_extensions(tmp_path: Path) -> None:
    (tmp_path / "a.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "b.yaml").write_text("key: val\n", encoding="utf-8")
    (tmp_path / "c.bin").write_bytes(b"\x00\x01")

    result = noema_ls(tmp_path)
    by_path = {e.path: e for e in result}

    assert by_path["a.json"].suffix == ".json"
    assert by_path["b.yaml"].suffix == ".yaml"
    assert by_path["c.bin"].suffix == ".bin"


# ---------------------------------------------------------------------------
# manifest_digest tests
# ---------------------------------------------------------------------------


def test_manifest_digest_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "f.py").write_text("x = 1\n", encoding="utf-8")
    manifest = noema_ls(tmp_path)

    d1 = manifest_digest(manifest)
    d2 = manifest_digest(manifest)

    assert d1 == d2
    assert len(d1) == 64


def test_manifest_digest_changes_with_content(tmp_path: Path) -> None:
    f = tmp_path / "f.py"
    f.write_text("x = 1\n", encoding="utf-8")
    manifest1 = noema_ls(tmp_path)
    f.write_text("x = 2\n", encoding="utf-8")
    manifest2 = noema_ls(tmp_path)

    assert manifest_digest(manifest1) != manifest_digest(manifest2)


def test_manifest_digest_empty_manifest() -> None:
    digest = manifest_digest([])
    assert len(digest) == 64


# ---------------------------------------------------------------------------
# sha256_bytes tests
# ---------------------------------------------------------------------------


def test_sha256_bytes_returns_64_hex_chars() -> None:
    result = sha256_bytes(b"test data")
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)


def test_sha256_bytes_deterministic() -> None:
    data = b"same data"
    assert sha256_bytes(data) == sha256_bytes(data)


def test_sha256_bytes_different_inputs_differ() -> None:
    assert sha256_bytes(b"a") != sha256_bytes(b"b")


# ---------------------------------------------------------------------------
# check_inverted_rh tests
# ---------------------------------------------------------------------------


def test_check_inverted_rh_snap_get_pattern(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text('score = 1.0 - snap.get("R_H", 1.0)\n', encoding="utf-8")
    manifest = noema_ls(tmp_path)

    findings = check_inverted_rh(tmp_path, manifest)

    assert len(findings) == 1
    assert findings[0].code == "inverted_rh_metric_candidate"
    assert findings[0].severity == "high"
    assert findings[0].path == "bad.py"


def test_check_inverted_rh_1_minus_rh_pattern(tmp_path: Path) -> None:
    bad = tmp_path / "metric.py"
    bad.write_text("result = 1 - R_H\n", encoding="utf-8")
    manifest = noema_ls(tmp_path)

    findings = check_inverted_rh(tmp_path, manifest)

    assert any(f.code == "inverted_rh_metric_candidate" for f in findings)


def test_check_inverted_rh_snapshot_get_pattern(tmp_path: Path) -> None:
    bad = tmp_path / "metric.py"
    bad.write_text('score = 1.0 - snapshot.get("R_H", 0.0)\n', encoding="utf-8")
    manifest = noema_ls(tmp_path)

    findings = check_inverted_rh(tmp_path, manifest)

    assert any(f.code == "inverted_rh_metric_candidate" for f in findings)


def test_check_inverted_rh_suppressed_by_rh_defect_score(tmp_path: Path) -> None:
    ok = tmp_path / "ok.py"
    ok.write_text('score = rh_defect_score(snap.get("R_H", 1.0))\n', encoding="utf-8")
    manifest = noema_ls(tmp_path)

    findings = check_inverted_rh(tmp_path, manifest)

    assert findings == []


def test_check_inverted_rh_suppressed_by_rh_coherence_score(tmp_path: Path) -> None:
    ok = tmp_path / "ok.py"
    ok.write_text(
        '# uses 1 - R_H but delegates\nscore = rh_coherence_score(R_H)\n',
        encoding="utf-8",
    )
    manifest = noema_ls(tmp_path)

    findings = check_inverted_rh(tmp_path, manifest)

    assert findings == []


def test_check_inverted_rh_no_rh_reference(tmp_path: Path) -> None:
    clean = tmp_path / "clean.py"
    clean.write_text("x = 1 + 2\n", encoding="utf-8")
    manifest = noema_ls(tmp_path)

    findings = check_inverted_rh(tmp_path, manifest)

    assert findings == []


def test_check_inverted_rh_non_text_suffix_skipped(tmp_path: Path) -> None:
    # .bin is not in _TEXT_SUFFIXES so it will be skipped
    bad = tmp_path / "data.bin"
    bad.write_bytes(b"1 - R_H")
    manifest = noema_ls(tmp_path)

    findings = check_inverted_rh(tmp_path, manifest)

    assert findings == []


def test_check_inverted_rh_evidence_constraint_field(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text('x = 1 - R_H\n', encoding="utf-8")
    manifest = noema_ls(tmp_path)

    findings = check_inverted_rh(tmp_path, manifest)

    assert findings[0].evidence == {"constraint": "no_inverted_rh_metric"}


# ---------------------------------------------------------------------------
# check_rh_pipeline_hook tests
# ---------------------------------------------------------------------------


def test_check_rh_pipeline_hook_no_adapter_returns_empty(tmp_path: Path) -> None:
    (tmp_path / "something.py").write_text("pass\n", encoding="utf-8")
    manifest = noema_ls(tmp_path)

    findings = check_rh_pipeline_hook(tmp_path, manifest)

    assert findings == []


def test_check_rh_pipeline_hook_adapter_no_pipeline_file_returns_empty(tmp_path: Path) -> None:
    # adapter exists but no ciel_pipeline.py
    adapter_dir = tmp_path / "src" / "ciel_sot_agent"
    adapter_dir.mkdir(parents=True)
    (adapter_dir / "rh_pipeline_jfunctional.py").write_text("pass\n", encoding="utf-8")
    manifest = noema_ls(tmp_path)

    findings = check_rh_pipeline_hook(tmp_path, manifest)

    assert findings == []


def test_check_rh_pipeline_hook_already_hooked_returns_empty(tmp_path: Path) -> None:
    # adapter + pipeline with hook function present -> clean
    sot = tmp_path / "src" / "ciel_sot_agent"
    sot.mkdir(parents=True)
    (sot / "rh_pipeline_jfunctional.py").write_text("pass\n", encoding="utf-8")
    (sot / "ciel_pipeline.py").write_text(
        "def compute_pipeline_j_functional(): pass\n", encoding="utf-8"
    )
    manifest = noema_ls(tmp_path)

    findings = check_rh_pipeline_hook(tmp_path, manifest)

    assert findings == []


def test_check_rh_pipeline_hook_pending_patch(tmp_path: Path) -> None:
    # adapter + pipeline missing hook + patch file present
    sot = tmp_path / "src" / "ciel_sot_agent"
    sot.mkdir(parents=True)
    (sot / "rh_pipeline_jfunctional.py").write_text("pass\n", encoding="utf-8")
    (sot / "ciel_pipeline.py").write_text("def run(): pass\n", encoding="utf-8")
    patches_dir = tmp_path / "patches"
    patches_dir.mkdir()
    (patches_dir / "fix_rh_jfunctional_pipeline_hook.diff").write_text(
        "--- a\n+++ b\n", encoding="utf-8"
    )
    manifest = noema_ls(tmp_path)

    findings = check_rh_pipeline_hook(tmp_path, manifest)

    assert len(findings) == 1
    assert findings[0].code == "rh_pipeline_hook_pending"
    assert findings[0].severity == "medium"


def test_check_rh_pipeline_hook_dead_adapter(tmp_path: Path) -> None:
    # adapter + pipeline missing hook, no patch
    sot = tmp_path / "src" / "ciel_sot_agent"
    sot.mkdir(parents=True)
    (sot / "rh_pipeline_jfunctional.py").write_text("pass\n", encoding="utf-8")
    (sot / "ciel_pipeline.py").write_text("def run(): pass\n", encoding="utf-8")
    manifest = noema_ls(tmp_path)

    findings = check_rh_pipeline_hook(tmp_path, manifest)

    assert len(findings) == 1
    assert findings[0].code == "dead_rh_pipeline_adapter"
    assert findings[0].severity == "medium"


# ---------------------------------------------------------------------------
# run_static_checks tests
# ---------------------------------------------------------------------------


def test_run_static_checks_combines_both_checks(tmp_path: Path) -> None:
    # Both checks run; no triggers -> empty
    (tmp_path / "clean.py").write_text("x = 1\n", encoding="utf-8")
    manifest = noema_ls(tmp_path)

    findings = run_static_checks(tmp_path, manifest)

    assert findings == []


def test_run_static_checks_returns_inverted_rh_finding(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text('v = 1 - R_H\n', encoding="utf-8")
    manifest = noema_ls(tmp_path)

    findings = run_static_checks(tmp_path, manifest)

    assert any(f.code == "inverted_rh_metric_candidate" for f in findings)


# ---------------------------------------------------------------------------
# metrics tests
# ---------------------------------------------------------------------------


def test_epsilon_neutrino_positive_and_tiny(tmp_path: Path) -> None:
    eps = epsilon_neutrino(10, 10000)
    assert eps > 0
    assert eps < 1e-10


def test_epsilon_neutrino_scales_with_input() -> None:
    small = epsilon_neutrino(1, 1)
    large = epsilon_neutrino(10000, 10_000_000)
    assert large > small


def test_d_lambda_empty_manifest() -> None:
    assert d_lambda([]) == 0.0


def test_d_lambda_positive_for_nonempty_manifest(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x\n", encoding="utf-8")
    manifest = noema_ls(tmp_path)

    result = d_lambda(manifest)

    assert result > 0.0


def test_d_lambda_zero_size_files() -> None:
    entries = [ManifestEntry(path="a.py", size=0, sha256="a" * 64, suffix=".py")]
    # nonzero count == 0, total == 0, result = 0 / max(1, 0) = 0
    result = d_lambda(entries)
    assert result == 0.0


def test_euler_berry_phase_in_range() -> None:
    import math
    digest = "a" * 64
    phase = euler_berry_phase(digest)
    assert 0.0 <= phase < 2.0 * math.pi


def test_euler_berry_phase_different_digests_differ() -> None:
    p1 = euler_berry_phase("0" * 64)
    p2 = euler_berry_phase("f" * 64)
    assert p1 != p2


def test_closure_error_in_range() -> None:
    import math
    for phase in [0.0, math.pi / 4, math.pi / 2, math.pi, 2 * math.pi - 0.01]:
        err = closure_error(phase)
        assert 0.0 <= err <= 1.0


def test_doctor_cost_zero_findings_is_nonnegative() -> None:
    cost = doctor_cost({}, 0.0, 0.0, 0.0)
    assert cost >= 0.0


def test_doctor_cost_high_severity_increases_cost() -> None:
    base = doctor_cost({}, 0.5, 0.5, 0.0)
    with_high = doctor_cost({"high": 1}, 0.5, 0.5, 0.0)
    assert with_high > base


def test_doctor_cost_weights_order(tmp_path: Path) -> None:
    # critical > high > medium > low
    c = doctor_cost({"critical": 1}, 0.0, 0.0, 0.0)
    h = doctor_cost({"high": 1}, 0.0, 0.0, 0.0)
    m = doctor_cost({"medium": 1}, 0.0, 0.0, 0.0)
    lo = doctor_cost({"low": 1}, 0.0, 0.0, 0.0)
    assert c > h > m > lo


# ---------------------------------------------------------------------------
# run_doctor_cycle / build_report tests
# ---------------------------------------------------------------------------


def test_doctor_detects_inverted_rh_metric(tmp_path: Path) -> None:
    bad = tmp_path / "bad_metric.py"
    bad.write_text('score = 1.0 - snap.get("R_H", 1.0)\n', encoding="utf-8")

    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))

    assert report.status == "FAIL"
    assert any(f.code == "inverted_rh_metric_candidate" for f in report.findings)


def test_doctor_pass_for_clean_directory(tmp_path: Path) -> None:
    (tmp_path / "clean.py").write_text("x = 1\n", encoding="utf-8")

    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))

    assert report.status == "PASS"
    assert report.findings == []


def test_doctor_pass_for_empty_directory(tmp_path: Path) -> None:
    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))

    assert report.status == "PASS"
    assert report.findings == []


def test_doctor_warn_for_medium_finding(tmp_path: Path) -> None:
    # Trigger rh_pipeline_hook_pending (medium severity)
    sot = tmp_path / "src" / "ciel_sot_agent"
    sot.mkdir(parents=True)
    (sot / "rh_pipeline_jfunctional.py").write_text("pass\n", encoding="utf-8")
    (sot / "ciel_pipeline.py").write_text("def run(): pass\n", encoding="utf-8")
    patches = tmp_path / "patches"
    patches.mkdir()
    (patches / "fix_rh_jfunctional_pipeline_hook.diff").write_text("diff\n", encoding="utf-8")

    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))

    assert report.status == "WARN"
    assert all(f.severity in {"low", "medium"} for f in report.findings)


def test_doctor_fail_for_high_severity_finding(tmp_path: Path) -> None:
    # inverted_rh is "high" severity
    bad = tmp_path / "bad.py"
    bad.write_text("val = 1 - R_H\n", encoding="utf-8")

    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))

    assert report.status == "FAIL"


def test_build_report_schema_field(tmp_path: Path) -> None:
    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))

    assert report.schema == "noema-holonomic-doctor/report/v0.1"


def test_build_report_file_count(tmp_path: Path) -> None:
    for i in range(5):
        (tmp_path / f"f{i}.py").write_text(f"x = {i}\n", encoding="utf-8")

    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))

    assert report.file_count == 5


def test_build_report_manifest_sample_capped_at_25(tmp_path: Path) -> None:
    for i in range(30):
        (tmp_path / f"file_{i:02d}.py").write_text(f"x = {i}\n", encoding="utf-8")

    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))

    assert report.file_count == 30
    assert len(report.manifest_sample) == 25


def test_build_report_manifest_sample_smaller_than_25(tmp_path: Path) -> None:
    for i in range(3):
        (tmp_path / f"f{i}.py").write_text(f"x = {i}\n", encoding="utf-8")

    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))

    assert len(report.manifest_sample) == 3


def test_doctor_report_to_json_dict(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")

    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))
    d = report.to_json_dict()

    assert d["schema"] == "noema-holonomic-doctor/report/v0.1"
    assert d["status"] == report.status
    assert isinstance(d["findings"], list)
    assert isinstance(d["manifest_sample"], list)
    assert d["file_count"] == report.file_count
    assert d["j_doctor"] == report.j_doctor


def test_doctor_report_to_json_dict_is_json_serializable(tmp_path: Path) -> None:
    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))

    serialized = json.dumps(report.to_json_dict())
    reloaded = json.loads(serialized)
    assert reloaded["schema"] == "noema-holonomic-doctor/report/v0.1"


def test_doctor_report_generated_at_format(tmp_path: Path) -> None:
    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))

    # Format: YYYYMMDDTHHMMSSz e.g. "20260528T123456Z"
    ts = report.generated_at
    assert len(ts) == 16
    assert ts.endswith("Z")
    assert ts[8] == "T"


# ---------------------------------------------------------------------------
# DoctorConfig tests
# ---------------------------------------------------------------------------


def test_doctor_config_defaults() -> None:
    cfg = DoctorConfig()

    assert cfg.report_dir == "doctor_reports"
    assert cfg.max_text_bytes == 256_000
    assert cfg.write is False


def test_doctor_config_custom_values() -> None:
    cfg = DoctorConfig(report_dir="my_reports", max_text_bytes=1024, write=True)

    assert cfg.report_dir == "my_reports"
    assert cfg.max_text_bytes == 1024
    assert cfg.write is True


def test_doctor_config_is_frozen() -> None:
    import dataclasses
    cfg = DoctorConfig()
    assert dataclasses.is_dataclass(cfg)
    try:
        cfg.write = True  # type: ignore[misc]
        assert False, "Should have raised FrozenInstanceError"
    except Exception:
        pass


# ---------------------------------------------------------------------------
# write_append_only_report tests
# ---------------------------------------------------------------------------


def test_doctor_write_is_append_only_with_current_pointer(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("R_H = 0.0\n", encoding="utf-8")

    report = run_doctor_cycle(tmp_path, DoctorConfig(write=True, report_dir="doctor_reports"))

    out_dir = tmp_path / "doctor_reports"
    reports = sorted(out_dir.glob("*_doctor.noema.json"))
    current = out_dir / "CURRENT_DOCTOR.noema.json"

    assert report.schema == "noema-holonomic-doctor/report/v0.1"
    assert reports
    assert current.exists()
    pointer = json.loads(current.read_text(encoding="utf-8"))
    assert pointer["status"] == report.status
    assert len(pointer["report_sha256"]) == 64


def test_write_append_only_accumulates_reports(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")
    cfg = DoctorConfig(write=True, report_dir="doctor_reports")

    run_doctor_cycle(tmp_path, cfg)
    time.sleep(1.1)  # ensure different timestamp
    run_doctor_cycle(tmp_path, cfg)

    out_dir = tmp_path / "doctor_reports"
    reports = sorted(out_dir.glob("*_doctor.noema.json"))
    assert len(reports) == 2


def test_write_append_only_current_pointer_updated(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")
    cfg = DoctorConfig(write=True, report_dir="doctor_reports")

    run_doctor_cycle(tmp_path, cfg)
    time.sleep(1.1)
    report2 = run_doctor_cycle(tmp_path, cfg)

    current = tmp_path / "doctor_reports" / "CURRENT_DOCTOR.noema.json"
    pointer = json.loads(current.read_text(encoding="utf-8"))
    assert pointer["generated_at"] == report2.generated_at


def test_write_report_uses_custom_report_dir(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")

    run_doctor_cycle(tmp_path, DoctorConfig(write=True, report_dir="my_custom_dir"))

    assert (tmp_path / "my_custom_dir").is_dir()
    assert list((tmp_path / "my_custom_dir").glob("*_doctor.noema.json"))


def test_write_report_current_pointer_schema(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")
    run_doctor_cycle(tmp_path, DoctorConfig(write=True, report_dir="dr"))

    current = tmp_path / "dr" / "CURRENT_DOCTOR.noema.json"
    pointer = json.loads(current.read_text(encoding="utf-8"))

    assert pointer["schema"] == "noema-holonomic-doctor/current/v0.1"
    assert "j_doctor" in pointer
    assert "report_path" in pointer


def test_write_report_path_returned(tmp_path: Path) -> None:
    from noema_holonomic_doctor.report import write_append_only_report
    from noema_holonomic_doctor.doctor import build_report

    report = build_report(tmp_path)
    path = write_append_only_report(tmp_path, report)

    assert path.exists()
    assert path.suffix == ".json"
    assert "doctor.noema" in path.name


def test_write_report_content_is_valid_json(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")
    run_doctor_cycle(tmp_path, DoctorConfig(write=True, report_dir="dr"))

    dr_dir = tmp_path / "dr"
    for report_file in dr_dir.glob("*_doctor.noema.json"):
        data = json.loads(report_file.read_text(encoding="utf-8"))
        assert data["schema"] == "noema-holonomic-doctor/report/v0.1"


# ---------------------------------------------------------------------------
# utc_stamp tests
# ---------------------------------------------------------------------------


def test_utc_stamp_format() -> None:
    stamp = utc_stamp()
    assert len(stamp) == 16
    assert stamp.endswith("Z")
    assert stamp[8] == "T"
    # All chars except position 8 (T) and 15 (Z) are digits
    digits_only = stamp[:8] + stamp[9:15]
    assert digits_only.isdigit()


def test_utc_stamp_advances_over_time() -> None:
    s1 = utc_stamp()
    time.sleep(1.1)
    s2 = utc_stamp()
    assert s2 > s1


# ---------------------------------------------------------------------------
# Finding dataclass tests
# ---------------------------------------------------------------------------


def test_finding_defaults() -> None:
    f = Finding(code="test_code", severity="low", message="test msg")

    assert f.path is None
    assert f.evidence == {}


def test_finding_is_frozen() -> None:
    import dataclasses
    f = Finding(code="x", severity="low", message="m")
    assert dataclasses.is_dataclass(f)
    try:
        f.code = "y"  # type: ignore[misc]
        assert False, "Should have raised FrozenInstanceError"
    except Exception:
        pass


def test_finding_with_evidence() -> None:
    f = Finding(
        code="inv",
        severity="high",
        message="bad",
        path="foo.py",
        evidence={"constraint": "no_inverted_rh_metric"},
    )
    assert f.evidence["constraint"] == "no_inverted_rh_metric"
    assert f.path == "foo.py"


# ---------------------------------------------------------------------------
# max_text_bytes enforcement
# ---------------------------------------------------------------------------


def test_check_inverted_rh_skips_oversized_file(tmp_path: Path) -> None:
    big = tmp_path / "big.py"
    big.write_text("x = 1 - R_H\n" * 100, encoding="utf-8")
    manifest = noema_ls(tmp_path)

    # max_bytes of 1 forces the file to be skipped
    findings = check_inverted_rh(tmp_path, manifest, max_bytes=1)

    assert findings == []


def test_doctor_config_max_text_bytes_respected(tmp_path: Path) -> None:
    big = tmp_path / "big.py"
    big.write_text("val = 1 - R_H\n" * 100, encoding="utf-8")

    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False, max_text_bytes=1))

    # The file is too big to check, so no inverted_rh findings
    assert not any(f.code == "inverted_rh_metric_candidate" for f in report.findings)
