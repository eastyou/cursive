from __future__ import annotations

"""HTML 渲染：A4 四线三格练习纸。"""

import html
from typing import Sequence

from .model import (
    BASELINE_GAP_MM,
    ROW_HEIGHT_MM,
    ZONE_MM,
    Row,
    alphabet_rows,
)

_BASELINE_MM: float = ZONE_MM + BASELINE_GAP_MM
_FOOTER_TEXT: str = (
    "四线三格：上伸线 / 中线（虚线）/ 基线 / 下伸线，单行总高 16mm（4-8-4mm）。"
)


def _number(value: float) -> str:
    """把毫米数值格式化为简短字符串，如 16.0 -> "16"。"""
    return f"{value:g}"


def _guide_lines() -> str:
    """生成一条练习行内的四条参考线。"""
    return (
        '<span class="line" data-role="ascender"></span>'
        '<span class="line" data-role="midline"></span>'
        '<span class="line" data-role="baseline"></span>'
        '<span class="line" data-role="descender"></span>'
    )


def _render_row(row: Row, index: int, show_guides: bool) -> str:
    """渲染单条练习行；空白行不输出文字。"""
    kind = row.kind if row.kind in ("trace", "blank") else "blank"
    parts: list[str] = [
        f'<div class="row {kind}" data-row="{index + 1}" data-kind="{kind}">'
    ]
    if show_guides:
        parts.append(_guide_lines())
    if kind == "trace" and row.text:
        parts.append(f'<span class="chars">{html.escape(row.text)}</span>')
    parts.append("</div>")
    return "".join(parts)


def _page_style() -> str:
    """返回内嵌样式表；尺寸全部以毫米为单位。"""
    row_height = _number(ROW_HEIGHT_MM)
    zone = _number(ZONE_MM)
    baseline = _number(_BASELINE_MM)
    bottom = _number(ZONE_MM)
    return f"""
@page {{ size: A4; margin: 0 }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #f3f4f6; color: #1f2933;
  font-family: "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif; }}
.page {{ width: 210mm; min-height: 297mm; padding: 12mm; box-sizing: border-box;
  overflow: hidden; background: #ffffff; margin: 0 auto; }}
header {{ border-bottom: 1px solid #d5dbe1; padding-bottom: 3mm; margin-bottom: 4mm; }}
h1 {{ margin: 0 0 2mm; font-size: 20px; font-weight: 600; letter-spacing: 1px; }}
.subtitle {{ margin: 0; font-size: 11px; color: #616e7c; }}
.rows {{ display: block; }}
.row {{ position: relative; height: {row_height}mm; margin-top: 2mm; }}
.line {{ position: absolute; left: 0; right: 0; height: 0; border-top: 1px solid #a9b4bf; }}
.line[data-role="ascender"] {{ top: 0; }}
.line[data-role="midline"] {{ top: {zone}mm; border-top-style: dashed; border-top-color: #c3ccd5; }}
.line[data-role="baseline"] {{ top: {baseline}mm; border-top-color: #5b6b7a; }}
.line[data-role="descender"] {{ top: {row_height}mm; }}
.chars {{ position: absolute; left: 2mm; bottom: {bottom}mm; white-space: nowrap;
  font-family: "Courier New", Courier, monospace; font-size: 11mm; line-height: 1;
  letter-spacing: 0.5mm; color: #cfd6dc; }}
footer {{ margin-top: 6mm; padding-top: 2mm; border-top: 1px solid #d5dbe1;
  font-size: 10px; color: #7b8794; }}
""".strip()


def render_sheet(
    rows: Sequence[Row],
    title: str = "英文书写练习",
    show_guides: bool = True,
) -> str:
    """渲染 A4 练习纸 HTML；title 会做 HTML 转义。"""
    safe_title = html.escape(title)
    body = "".join(
        _render_row(row, index, show_guides) for index, row in enumerate(rows)
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title}</title>
<style>
{_page_style()}
</style>
</head>
<body>
<div class="page">
<header>
<h1>{safe_title}</h1>
<p class="subtitle">四线三格 · 描摹行与空白练习行</p>
</header>
<div class="rows">
{body}
</div>
<footer>{_FOOTER_TEXT}</footer>
</div>
</body>
</html>
"""


def render_alphabet(title: str = "字母练习") -> str:
    """渲染字母表描摹页（Aa-Zz 共 26 组）。"""
    rows = [Row(text=line, kind="trace") for line in alphabet_rows()]
    return render_sheet(rows, title=title)
