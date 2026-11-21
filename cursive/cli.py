from __future__ import annotations

"""命令行入口：解析参数、生成 HTML 并处理退出码。"""

import argparse
import sys
from typing import NoReturn, Optional, Sequence

from .model import (
    MAX_ROWS,
    MIN_ROWS,
    CursiveError,
    alphabet_rows,
    build_rows,
    demo_text,
)
from .render import render_alphabet, render_sheet


class _Parser(argparse.ArgumentParser):
    """把 argparse 的错误统一转换为 CursiveError，便于返回退出码 2。"""

    def error(self, message: str) -> NoReturn:
        raise CursiveError(message)


def _build_parser() -> _Parser:
    """构建命令行解析器。"""
    parser = _Parser(
        prog="cursive",
        description="生成 A4 英文连笔字帖：四线三格、描摹行与空白练习行。",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="cursive.html",
        metavar="PATH",
        help="输出 HTML 路径（默认 cursive.html）",
    )
    parser.add_argument(
        "--text",
        default=None,
        metavar="TEXT",
        help='练习文本；使用 "-" 时从标准输入读取一行',
    )
    parser.add_argument(
        "--alphabet",
        action="store_true",
        help="生成字母表描摹页（优先于 --text 与 --demo）",
    )
    parser.add_argument(
        "--style",
        default="fade",
        metavar="STYLE",
        help="行样式：trace / fade / blank（默认 fade）",
    )
    parser.add_argument(
        "--rows",
        default="8",
        metavar="N",
        help=f"练习行数 {MIN_ROWS}..{MAX_ROWS}（默认 8）",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="使用内置示例句子",
    )
    return parser


def _parse_rows(raw: str) -> int:
    """把 --rows 的字符串转换为整数并校验范围。"""
    try:
        value = int(raw.strip())
    except (TypeError, ValueError) as exc:
        raise CursiveError(f"rows 必须是整数（收到 {raw!r}）") from exc
    if not MIN_ROWS <= value <= MAX_ROWS:
        raise CursiveError(f"rows 必须在 {MIN_ROWS} 到 {MAX_ROWS} 之间")
    return value


def _read_text(raw: str) -> str:
    """读取 --text；若为 "-" 则从标准输入读取一行。"""
    if raw == "-":
        line = sys.stdin.readline()
        if not line:
            raise CursiveError("标准输入中没有可读取的文本")
        return line.rstrip("\r\n")
    return raw


def _write_file(path: str, content: str) -> None:
    """以 UTF-8 写入文件；失败时由 OSError 向上传播。"""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """命令行主函数：成功返回 0，输入非法返回 2，写文件失败返回 1。"""
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        output = args.output
        if not isinstance(output, str) or not output.strip():
            raise CursiveError("输出路径不能为空")
        if args.alphabet:
            document = render_alphabet()
            count = len(alphabet_rows())
        else:
            if args.text is None and not args.demo:
                raise CursiveError("请提供 --text、--demo 或 --alphabet 之一")
            source = (
                demo_text()
                if args.demo and args.text is None
                else _read_text(args.text or "")
            )
            rows = build_rows(source, style=args.style, rows=_parse_rows(args.rows))
            document = render_sheet(rows)
            count = len(rows)
        _write_file(output, document)
    except CursiveError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    except SystemExit as exc:  # --help 等正常退出
        return exc.code if isinstance(exc.code, int) else 0
    except OSError as exc:
        print(f"写入文件失败：{exc}", file=sys.stderr)
        return 1

    print(f"已生成 {output}（{count} 行）")
    return 0
