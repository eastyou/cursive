from __future__ import annotations

"""cursive：生成 A4 英文连笔字帖（四线三格、描摹行、空白练习行）。"""

from .model import (
    BASELINE_GAP_MM,
    ROW_HEIGHT_MM,
    ZONE_MM,
    CursiveError,
    Row,
    alphabet_rows,
    build_rows,
    demo_text,
    validate_line,
    wrap_text,
)
from .render import render_alphabet, render_sheet

__version__ = "0.1.0"

__all__ = [
    "BASELINE_GAP_MM",
    "ZONE_MM",
    "ROW_HEIGHT_MM",
    "CursiveError",
    "Row",
    "validate_line",
    "wrap_text",
    "alphabet_rows",
    "build_rows",
    "demo_text",
    "render_sheet",
    "render_alphabet",
    "__version__",
]
