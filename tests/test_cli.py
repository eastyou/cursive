from __future__ import annotations

"""cli 模块的退出码、文件输出与参数校验用例。"""

import contextlib
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

from cursive.cli import main


class CliTestBase(unittest.TestCase):
    """提供临时目录与统一的运行辅助方法。"""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def path(self, name: str = "sheet.html") -> str:
        return os.path.join(self.dir, name)

    def run_cli(
        self,
        argv: list[str],
        stdin: str | None = None,
    ) -> tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            if stdin is None:
                code = main(argv)
            else:
                with mock.patch.object(sys, "stdin", io.StringIO(stdin)):
                    code = main(argv)
        return code, out.getvalue(), err.getvalue()


class CliSuccessTests(CliTestBase):
    """成功路径与输出文件内容。"""

    def test_text_generates_file(self) -> None:
        target = self.path()
        code, out, err = self.run_cli(["-o", target, "--text", "Hello class"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertTrue(os.path.isfile(target))
        self.assertIn("已生成", out)
        self.assertIn("（8 行）", out)

    def test_file_contains_html_and_text(self) -> None:
        target = self.path()
        self.run_cli(["-o", target, "--text", "Hello class"])
        with open(target, encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("<!DOCTYPE html>", content)
        self.assertIn("Hello class", content)

    def test_demo_uses_builtin_sentence(self) -> None:
        target = self.path()
        code, _, _ = self.run_cli(["-o", target, "--demo"])
        self.assertEqual(code, 0)
        with open(target, encoding="utf-8") as handle:
            self.assertIn("quick brown fox", handle.read())

    def test_alphabet_page(self) -> None:
        target = self.path("alphabet.html")
        code, out, _ = self.run_cli(["-o", target, "--alphabet"])
        self.assertEqual(code, 0)
        self.assertIn("（6 行）", out)
        with open(target, encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("Aa Bb Cc Dd Ee", content)
        self.assertIn("Zz", content)

    def test_default_style_fade_has_two_trace_rows(self) -> None:
        target = self.path()
        self.run_cli(["-o", target, "--text", "The quick brown fox jumps over the lazy dog."])
        with open(target, encoding="utf-8") as handle:
            self.assertEqual(handle.read().count('class="row trace"'), 2)

    def test_trace_style_all_rows_trace(self) -> None:
        target = self.path()
        self.run_cli(["-o", target, "--text", "Hi", "--style", "trace", "--rows", "3"])
        with open(target, encoding="utf-8") as handle:
            self.assertEqual(handle.read().count('class="row trace"'), 1)

    def test_blank_style_has_no_trace_rows(self) -> None:
        target = self.path()
        self.run_cli(["-o", target, "--text", "Hi", "--style", "blank"])
        with open(target, encoding="utf-8") as handle:
            self.assertEqual(handle.read().count('class="row trace"'), 0)

    def test_rows_option_controls_row_count(self) -> None:
        target = self.path()
        code, out, _ = self.run_cli(["-o", target, "--text", "Hi", "--rows", "3"])
        self.assertEqual(code, 0)
        self.assertIn("（3 行）", out)
        with open(target, encoding="utf-8") as handle:
            self.assertEqual(handle.read().count('class="row '), 3)

    def test_rows_lower_bound(self) -> None:
        code, _, _ = self.run_cli(["-o", self.path(), "--text", "Hi", "--rows", "2"])
        self.assertEqual(code, 0)

    def test_rows_upper_bound(self) -> None:
        code, _, _ = self.run_cli(["-o", self.path(), "--text", "Hi", "--rows", "20"])
        self.assertEqual(code, 0)

    def test_stdin_dash_reads_one_line(self) -> None:
        target = self.path()
        code, _, _ = self.run_cli(["-o", target, "--text", "-"], stdin="Hello stdin\n")
        self.assertEqual(code, 0)
        with open(target, encoding="utf-8") as handle:
            self.assertIn("Hello stdin", handle.read())

    def test_text_takes_precedence_over_demo(self) -> None:
        target = self.path()
        code, _, _ = self.run_cli(["-o", target, "--demo", "--text", "Custom"])
        self.assertEqual(code, 0)
        with open(target, encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("Custom", content)
        self.assertNotIn("quick brown fox", content)

    def test_alphabet_takes_precedence_over_text(self) -> None:
        target = self.path()
        code, _, _ = self.run_cli(["-o", target, "--alphabet", "--text", "你好"])
        self.assertEqual(code, 0)
        with open(target, encoding="utf-8") as handle:
            self.assertIn("Aa Bb Cc Dd Ee", handle.read())


class CliInputErrorTests(CliTestBase):
    """非法输入应返回退出码 2，且不产生文件。"""

    def test_chinese_text_rejected(self) -> None:
        target = self.path()
        code, out, err = self.run_cli(["-o", target, "--text", "你好"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)
        self.assertEqual(out, "")
        self.assertFalse(os.path.exists(target))

    def test_missing_source_rejected(self) -> None:
        code, _, err = self.run_cli(["-o", self.path()])
        self.assertEqual(code, 2)
        self.assertIn("--text", err)

    def test_rows_too_small_rejected(self) -> None:
        code, _, err = self.run_cli(["-o", self.path(), "--text", "Hi", "--rows", "1"])
        self.assertEqual(code, 2)
        self.assertIn("rows", err)

    def test_rows_too_large_rejected(self) -> None:
        code, _, _ = self.run_cli(["-o", self.path(), "--text", "Hi", "--rows", "21"])
        self.assertEqual(code, 2)

    def test_rows_not_integer_rejected(self) -> None:
        code, _, err = self.run_cli(["-o", self.path(), "--text", "Hi", "--rows", "abc"])
        self.assertEqual(code, 2)
        self.assertIn("整数", err)

    def test_invalid_style_rejected(self) -> None:
        code, _, err = self.run_cli(["-o", self.path(), "--text", "Hi", "--style", "fancy"])
        self.assertEqual(code, 2)
        self.assertIn("style", err)

    def test_overlong_text_rejected(self) -> None:
        code, _, _ = self.run_cli(["-o", self.path(), "--text", "a" * 61])
        self.assertEqual(code, 2)

    def test_empty_stdin_rejected(self) -> None:
        code, _, err = self.run_cli(["-o", self.path(), "--text", "-"], stdin="")
        self.assertEqual(code, 2)
        self.assertIn("标准输入", err)

    def test_empty_output_rejected(self) -> None:
        code, _, err = self.run_cli(["-o", "", "--text", "Hi"])
        self.assertEqual(code, 2)
        self.assertIn("输出路径", err)

    def test_unknown_option_rejected(self) -> None:
        code, _, err = self.run_cli(["--nope"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_help_returns_zero(self) -> None:
        code, out, _ = self.run_cli(["--help"])
        self.assertEqual(code, 0)
        self.assertIn("usage", out)


class CliWriteErrorTests(CliTestBase):
    """写文件失败应返回退出码 1。"""

    def test_missing_directory_returns_one(self) -> None:
        target = os.path.join(self.dir, "missing", "sheet.html")
        code, _, err = self.run_cli(["-o", target, "--text", "Hi"])
        self.assertEqual(code, 1)
        self.assertIn("写入文件失败", err)

    def test_output_is_directory_returns_one(self) -> None:
        code, _, err = self.run_cli(["-o", self.dir, "--text", "Hi"])
        self.assertEqual(code, 1)
        self.assertIn("写入文件失败", err)


if __name__ == "__main__":
    unittest.main()
