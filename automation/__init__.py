"""Automation package for generating statistical PDF reports from JSON data."""

from .gui_app import launch_gui
from .report_generator import (
    ReportConfig,
    generate_pdf_report,
    load_json_dataset,
    run_from_cli,
)

__all__ = [
    "ReportConfig",
    "generate_pdf_report",
    "launch_gui",
    "load_json_dataset",
    "run_from_cli",
]
