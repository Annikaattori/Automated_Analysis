"""Utilities for generating statistical PDF reports from JSON datasets."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

import matplotlib

# Use a non-interactive backend so the code can run in headless environments
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages


DEFAULT_REPORT_DIR = Path("Reports")


@dataclass
class ReportConfig:
    """Configuration for report generation."""

    json_path: Path
    report_dir: Path = DEFAULT_REPORT_DIR
    title: Optional[str] = None

    @property
    def resolved_title(self) -> str:
        if self.title:
            return self.title
        stem = self.json_path.stem.replace("_", " ").title()
        return f"Data Report: {stem}"


def load_json_dataset(json_path: Path) -> pd.DataFrame:
    """Load a JSON dataset into a DataFrame.

    The function accepts either a list of records (array of objects) or a single
    object with a key "data" that contains the list of records. This mirrors
    how analytics exports are commonly structured.
    """

    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with json_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, dict) and "data" in raw:
        records = raw["data"]
    else:
        records = raw

    if not isinstance(records, list):
        raise ValueError("JSON dataset must be a list of records or include a 'data' list")

    if not records:
        raise ValueError("JSON dataset is empty")

    frame = pd.DataFrame.from_records(records)
    if frame.empty:
        raise ValueError("JSON dataset produced an empty DataFrame")

    return frame


def _numeric_columns(df: pd.DataFrame) -> Iterable[str]:
    return df.select_dtypes(include=["number"]).columns


def _categorical_columns(df: pd.DataFrame) -> Iterable[str]:
    return df.select_dtypes(include=["object", "category", "bool"]).columns


def _add_title_page(pdf: PdfPages, config: ReportConfig, df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 portrait size in inches
    ax.axis("off")

    summary_lines = [
        config.resolved_title,
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Source file: {config.json_path.name}",
        "",
        "Dataset summary:",
        f"Rows: {len(df)}",
        f"Columns: {len(df.columns)}",
    ]
    text = "\n".join(summary_lines)
    ax.text(0.5, 0.5, text, ha="center", va="center", fontsize=14)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _plot_numeric_column(pdf: PdfPages, df: pd.DataFrame, column: str) -> None:
    series = df[column].dropna()
    if series.empty:
        return

    fig, axes = plt.subplots(1, 2, figsize=(11.69, 8.27))
    fig.suptitle(f"Numeric distribution for '{column}'")

    sns.histplot(series, kde=True, ax=axes[0], color="#1f77b4")
    axes[0].set_title("Histogram")
    axes[0].set_xlabel(column)
    axes[0].set_ylabel("Frequency")

    sns.boxplot(x=series, ax=axes[1], color="#ff7f0e")
    axes[1].set_title("Boxplot")
    axes[1].set_xlabel(column)

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    pdf.savefig(fig)
    plt.close(fig)


def _plot_categorical_column(pdf: PdfPages, df: pd.DataFrame, column: str) -> None:
    series = df[column].dropna().astype(str)
    if series.empty:
        return

    counts = series.value_counts().head(10)

    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    sns.barplot(x=counts.values, y=counts.index, palette="viridis", ax=ax)
    ax.set_title(f"Top categories for '{column}'")
    ax.set_xlabel("Count")
    ax.set_ylabel(column)

    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def _plot_correlation_heatmap(pdf: PdfPages, df: pd.DataFrame, numeric_cols: Iterable[str]) -> None:
    numeric_cols = list(numeric_cols)
    if len(numeric_cols) < 2:
        return

    corr = df[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(11, 9))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, ax=ax)
    ax.set_title("Correlation heatmap")
    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def generate_pdf_report(config: ReportConfig) -> Path:
    """Generate a PDF report for the dataset defined in ``config``.

    The report is saved in the configured output directory. The resulting file
    name includes the current timestamp (YYYYMMDD_HHMMSS) to provide simple
    versioning.
    """

    df = load_json_dataset(config.json_path)

    config.report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"report_{timestamp}.pdf"
    report_path = config.report_dir / report_name

    numeric_cols = list(_numeric_columns(df))
    categorical_cols = list(_categorical_columns(df))

    with PdfPages(report_path) as pdf:
        _add_title_page(pdf, config, df)

        if numeric_cols:
            for column in numeric_cols:
                _plot_numeric_column(pdf, df, column)
            _plot_correlation_heatmap(pdf, df, numeric_cols)

        if categorical_cols:
            for column in categorical_cols:
                _plot_categorical_column(pdf, df, column)

        if not numeric_cols and not categorical_cols:
            # Fallback page indicating that no plots could be generated
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis("off")
            ax.text(
                0.5,
                0.5,
                "Unable to generate plots for the provided dataset.",
                ha="center",
                va="center",
            )
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    return report_path


def run_from_cli(json_path: str, report_dir: Optional[str] = None, title: Optional[str] = None) -> Path:
    """Execute the report generator using string parameters.

    ``json_path`` is required. ``report_dir`` defaults to ``Reports`` when not
    provided. ``title`` overrides the automatically generated report title.
    """

    config = ReportConfig(
        json_path=Path(json_path),
        report_dir=Path(report_dir) if report_dir else DEFAULT_REPORT_DIR,
        title=title,
    )
    return generate_pdf_report(config)


__all__ = [
    "ReportConfig",
    "generate_pdf_report",
    "load_json_dataset",
    "run_from_cli",
]
