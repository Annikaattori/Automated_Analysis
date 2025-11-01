"""Graphical interface for exploring JSON datasets and generating PDF reports."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:  # pragma: no cover - optional dependency resolution
    from pandasgui import show  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency resolution
    show = None  # type: ignore

from .report_generator import ReportConfig, generate_pdf_report, load_json_dataset


class ReportGui:
    """Tkinter-based wrapper around PandasGUI for dataset exploration."""

    def __init__(self, root: tk.Tk, initial_json: Optional[Path] = None) -> None:
        self.root = root
        self.root.title("JSON Dataset Explorer")
        self.root.geometry("420x200")

        self._json_path: Optional[Path] = None
        self._gui = None

        self.status_var = tk.StringVar(value="Select a JSON dataset to begin.")

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Dataset:").grid(row=0, column=0, sticky=tk.W)
        self.path_var = tk.StringVar(value="(none)")
        ttk.Label(frame, textvariable=self.path_var, width=40).grid(row=0, column=1, sticky=tk.W)
        ttk.Button(frame, text="Browse", command=self.browse).grid(row=0, column=2, padx=(10, 0))

        ttk.Button(frame, text="Open in PandasGUI", command=self.open_in_gui).grid(
            row=1, column=0, columnspan=3, pady=(15, 0), sticky=tk.EW
        )

        ttk.Button(frame, text="Generate PDF report", command=self.generate_report).grid(
            row=2, column=0, columnspan=3, pady=(10, 0), sticky=tk.EW
        )

        ttk.Label(frame, textvariable=self.status_var, foreground="#555").grid(
            row=3, column=0, columnspan=3, pady=(15, 0), sticky=tk.W
        )

        for column in range(3):
            frame.grid_columnconfigure(column, weight=1)

        if initial_json:
            self.set_dataset(initial_json)

    def browse(self) -> None:
        """Prompt the user to select a JSON dataset."""

        filetypes = [("JSON files", "*.json"), ("All files", "*.*")]
        selection = filedialog.askopenfilename(filetypes=filetypes)
        if selection:
            self.set_dataset(Path(selection))

    def set_dataset(self, path: Path) -> None:
        try:
            dataset = load_json_dataset(path)
        except Exception as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror("Failed to load dataset", str(exc))
            self.status_var.set("Dataset loading failed.")
            return

        self._json_path = path
        self.path_var.set(str(path))
        self.status_var.set(f"Loaded {len(dataset)} rows and {len(dataset.columns)} columns.")

        # Automatically open in PandasGUI when selecting a dataset.
        self._show_in_pandasgui(dataset)

    def open_in_gui(self) -> None:
        if not self._json_path:
            messagebox.showwarning("No dataset", "Select a JSON dataset first.")
            return

        try:
            dataset = load_json_dataset(self._json_path)
        except Exception as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror("Failed to load dataset", str(exc))
            self.status_var.set("Dataset loading failed.")
            return

        self._show_in_pandasgui(dataset)

    def _show_in_pandasgui(self, dataset) -> None:
        if show is None:
            messagebox.showerror(
                "PandasGUI not available",
                "Asenna pandasgui-kirjasto virtuaaliympäristöön ennen käyttöliittymän avaamista.",
            )
            self.status_var.set("PandasGUI puuttuu.")
            return

        if self._gui is not None:
            try:
                self._gui.close()  # type: ignore[attr-defined]
            except Exception:
                pass

        self._gui = show({self._json_path.name if self._json_path else "Dataset": dataset}, settings={"block": False})
        self.status_var.set("Dataset opened in PandasGUI.")

    def generate_report(self) -> None:
        if not self._json_path:
            messagebox.showwarning("No dataset", "Select a JSON dataset before generating a report.")
            return

        try:
            report_path = generate_pdf_report(ReportConfig(json_path=self._json_path))
        except Exception as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror("Report generation failed", str(exc))
            self.status_var.set("Report generation failed.")
            return

        messagebox.showinfo("Report generated", f"PDF report saved to: {report_path}")
        self.status_var.set(f"Report saved to {report_path}")

    def run(self) -> None:
        self.root.mainloop()


def launch_gui(json_path: Optional[Path] = None) -> None:
    """Launch the graphical interface for exploring datasets."""

    root = tk.Tk()
    app = ReportGui(root, initial_json=json_path)
    app.run()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open the dataset explorer GUI.")
    parser.add_argument("json_path", type=Path, nargs="?", help="Optional path to a JSON dataset")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    launch_gui(args.json_path)


if __name__ == "__main__":
    main()
