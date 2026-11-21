from __future__ import annotations

"""cursive 的领域模型：文本校验、按词换行、字母表与练习行构建。"""

import re
from dataclasses import dataclass

# 版面尺寸（毫米）：基线间距、上伸/下伸区高度、单行总高
BASELINE_GAP_MM: float = 8.0
ZONE_MM: float = 4.0
ROW_HEIGHT_MM: float = 16.0

# 单行文本上限
MAX_LINE_LENGTH: int = 60
# 练习行数范围
MIN_ROWS: int = 2
MAX_ROWS: int = 20
# fade 样式中前多少行采用描摹
FADE_TRACE_ROWS: int = 2
# 支持的排版样式
VALID_STYLES: tuple[str, ...] = ("trace", "fade", "blank")

# 仅允许 ASCII 字母、数字、空格与常用标点
_ALLOWED_PATTERN = re.compile(r"^[A-Za-z0-9 .,!?;:'-]+$")


class CursiveError(ValueError):
    """cursive 的自定义异常：所有非法输入都抛出该异常。"""


@dataclass(frozen=True)
class Row:
    """练习行：text 为行内文本，kind 为 trace（描摹）或 blank（空白）。"""

    text: str
    kind: str


def _first_invalid_char(text: str) -> str:
    """返回文本中第一个不被允许的字符，用于错误提示。"""
    for char in text:
        if not re.match(r"[A-Za-z0-9 .,!?;:'-]", char):
            return char
    return ""


def validate_line(text: str) -> str:
    """校验单行文本并返回去除首尾空白后的结果。

    只允许 ASCII 字母、数字、空格与 `.,!?;:'-`，长度不超过 60。
    """
    if not isinstance(text, str):
        raise CursiveError("文本必须是字符串")
    stripped = text.strip()
    if not stripped:
        raise CursiveError("文本不能为空")
    if len(stripped) > MAX_LINE_LENGTH:
        raise CursiveError(
            f"文本长度不能超过 {MAX_LINE_LENGTH} 个字符（当前 {len(stripped)}）"
        )
    if not _ALLOWED_PATTERN.match(stripped):
        bad = _first_invalid_char(stripped)
        raise CursiveError(
            f"文本包含不支持的字符 {bad!r}，仅允许英文字母、数字、空格与 .,!?;:'-"
        )
    return stripped


def wrap_text(text: str, max_chars: int = 24) -> list[str]:
    """按单词换行，超过 max_chars 的单词会被硬切分。

    max_chars 必须在 5 到 40 之间。
    """
    value = validate_line(text)
    if isinstance(max_chars, bool) or not isinstance(max_chars, int):
        raise CursiveError("max_chars 必须是整数")
    if not 5 <= max_chars <= 40:
        raise CursiveError("max_chars 必须在 5 到 40 之间")

    lines: list[str] = []
    current: str = ""
    for word in value.split(" "):
        if not word:
            continue
        if len(word) > max_chars:
            if current:
                lines.append(current)
                current = ""
            for start in range(0, len(word), max_chars):
                lines.append(word[start : start + max_chars])
            continue
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= max_chars:
            current = f"{current} {word}"
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def alphabet_rows() -> list[str]:
    """按每行 5 组生成字母表，如 "Aa Bb Cc Dd Ee"，共 6 行。"""
    letters = [chr(code) for code in range(ord("A"), ord("Z") + 1)]
    rows: list[str] = []
    for index in range(0, len(letters), 5):
        group = letters[index : index + 5]
        rows.append(" ".join(f"{letter}{letter.lower()}" for letter in group))
    return rows


def build_rows(source: str, style: str, rows: int) -> list[Row]:
    """把源文本排版为指定数量的练习行。

    style 为 trace（全描摹）、fade（前 2 行描摹，其余空白）或 blank（全空白）。
    rows 必须在 2 到 20 之间；内容不足时用空白行补齐，超出时截断。
    """
    if not isinstance(style, str):
        raise CursiveError("style 必须是字符串")
    if style not in VALID_STYLES:
        raise CursiveError("style 只能是 trace、fade 或 blank")
    if isinstance(rows, bool) or not isinstance(rows, int):
        raise CursiveError("rows 必须是整数")
    if not MIN_ROWS <= rows <= MAX_ROWS:
        raise CursiveError(f"rows 必须在 {MIN_ROWS} 到 {MAX_ROWS} 之间")

    lines = wrap_text(source)
    result: list[Row] = []
    for index in range(rows):
        text = lines[index] if index < len(lines) else ""
        wants_trace = style == "trace" or (style == "fade" and index < FADE_TRACE_ROWS)
        # 没有文本的补齐行一律视为空白行
        is_trace = wants_trace and bool(text)
        result.append(Row(text=text, kind="trace" if is_trace else "blank"))
    return result


def demo_text() -> str:
    """内置示例句子，用于 --demo。"""
    return "The quick brown fox jumps over the lazy dog."
