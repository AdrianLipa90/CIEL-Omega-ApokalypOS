from pathlib import Path
import json


def test_hdf5_failure_falls_back_to_json(tmp_path):
    from src.lingophysics.storage_fallback import write_hdf5_or_json
    data = {"batch": "test", "values": [1, 2, 3]}
    result = write_hdf5_or_json(data, tmp_path / "out.h5", simulate_failure=True)
    assert result.used_fallback
    assert result.result_path.endswith(".json")
    payload = json.loads(Path(result.result_path).read_text(encoding="utf-8"))
    assert payload["metadata"]["used_fallback"] is True
    assert payload["data"]["batch"] == "test"


def test_json_fallback_report_is_explicit(tmp_path):
    from src.lingophysics.storage_fallback import write_hdf5_or_json, write_report
    result = write_hdf5_or_json({"x": 1}, tmp_path / "out.h5", simulate_failure=True)
    report = tmp_path / "fallback_report.json"
    write_report(result, report)
    saved = json.loads(report.read_text(encoding="utf-8"))
    assert saved["preferred_format"] == "hdf5"
    assert saved["used_fallback"] is True
