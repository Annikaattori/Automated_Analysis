from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.report_generator import ReportConfig, generate_pdf_report, load_json_dataset


FIXTURE_DIR = Path(__file__).parent / "data"


def test_load_json_dataset_handles_plain_list(tmp_path: Path) -> None:
    dataset = [
        {"value": 1, "category": "A"},
        {"value": 2, "category": "B"},
    ]
    json_path = tmp_path / "data.json"
    json_path.write_text(json.dumps(dataset))

    df = load_json_dataset(json_path)

    assert list(df.columns) == ["value", "category"]
    assert len(df) == 2


def test_load_json_dataset_requires_list(tmp_path: Path) -> None:
    json_path = tmp_path / "invalid.json"
    json_path.write_text(json.dumps({"not": "a list"}))

    with pytest.raises(ValueError):
        load_json_dataset(json_path)


def test_generate_pdf_report_creates_file(tmp_path: Path) -> None:
    json_path = FIXTURE_DIR / "sample_data.json"
    report_dir = tmp_path / "reports"

    config = ReportConfig(json_path=json_path, report_dir=report_dir, title="Test Report")
    report_path = generate_pdf_report(config)

    assert report_path.exists()
    assert report_path.suffix == ".pdf"
    assert report_path.stat().st_size > 0

    # Ensure the report name contains timestamp pattern
    assert report_path.name.startswith("report_")
    assert len(report_path.name) > len("report_.pdf")
