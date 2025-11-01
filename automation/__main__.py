"""Command-line entry point for generating PDF reports from JSON data."""
from __future__ import annotations

import argparse
from pathlib import Path

from .report_generator import run_from_cli


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a statistical PDF report from a JSON dataset.")
    parser.add_argument("json_path", type=Path, help="Path to the JSON dataset")
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path("Reports"),
        help="Directory where the PDF report will be saved (default: Reports)",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Optional title for the report",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_path = run_from_cli(str(args.json_path), str(args.report_dir), args.title)
    print(f"Report generated at: {report_path}")


if __name__ == "__main__":
    main()
