from __future__ import annotations

"""render 模块的单元测试。"""

import unittest

from cursive.model import Row, alphabet_rows
from cursive.render import render_alphabet, render_sheet


class RenderSheetTests(unittest.TestCase):
    """render_sheet 的结构、样式与转义用例。"""

    def setUp(self) -> None:
        self.rows = [
            Row(text="The quick brown fox", kind="trace"),
            Row(text="Hidden text", kind="blank"),
        ]

    def test_returns_html_document(self) -> None:
        doc = render_sheet(self.rows)
        self.assertTrue(doc.startswith("<!DOCTYPE html>"))
        self.assertIn('lang="zh-CN"', doc)
        self.assertIn('<meta charset="utf-8">', doc)

    def test_contains_a4_page_rule(self) -> None:
        doc = render_sheet(self.rows)
        self.assertIn("@page { size: A4; margin: 0 }", doc)

    def test_page_box_dimensions(self) -> None:
        doc = render_sheet(self.rows)
        self.assertIn("width: 210mm", doc)
        self.assertIn("min-height: 297mm", doc)
        self.assertIn("padding: 12mm", doc)
        self.assertIn("box-sizing: border-box", doc)
        self.assertIn("overflow: hidden", doc)

    def test_row_height_in_mm(self) -> None:
        doc = render_sheet(self.rows)
        self.assertIn("height: 16mm;", doc)

    def test_guide_positions_and_dashed_midline(self) -> None:
        doc = render_sheet(self.rows)
        self.assertIn('[data-role="midline"] { top: 4mm;', doc)
        self.assertIn("border-top-style: dashed", doc)
        self.assertIn('[data-role="baseline"] { top: 12mm;', doc)
        self.assertIn('[data-role="descender"] { top: 16mm; }', doc)

    def test_row_count_matches_rows(self) -> None:
        doc = render_sheet(self.rows)
        self.assertEqual(doc.count('class="row '), len(self.rows))

    def test_four_guides_per_row(self) -> None:
        doc = render_sheet(self.rows)
        roles = ("ascender", "midline", "baseline", "descender")
        for role in roles:
            tag = f'<span class="line" data-role="{role}"></span>'
            self.assertEqual(doc.count(tag), len(self.rows))

    def test_trace_text_is_rendered(self) -> None:
        doc = render_sheet(self.rows)
        self.assertIn("The quick brown fox", doc)
        self.assertIn('class="chars"', doc)

    def test_blank_row_hides_text(self) -> None:
        doc = render_sheet(self.rows)
        self.assertNotIn("Hidden text", doc)

    def test_blank_row_markup(self) -> None:
        doc = render_sheet(self.rows)
        self.assertIn('class="row blank"', doc)

    def test_title_is_escaped(self) -> None:
        doc = render_sheet(self.rows, title="<script>alert(1)</script>")
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", doc)
        self.assertNotIn("<script>alert(1)</script>", doc)

    def test_row_text_is_escaped(self) -> None:
        doc = render_sheet([Row(text="A & B", kind="trace")])
        self.assertIn("A &amp; B", doc)
        self.assertNotIn("A & B", doc)

    def test_show_guides_false_omits_guides(self) -> None:
        doc = render_sheet(self.rows, show_guides=False)
        self.assertNotIn('<span class="line"', doc)
        self.assertEqual(doc.count('class="row '), len(self.rows))

    def test_default_title(self) -> None:
        doc = render_sheet(self.rows)
        self.assertIn("英文书写练习", doc)

    def test_footer_explains_guides(self) -> None:
        doc = render_sheet(self.rows)
        self.assertIn("四线三格：", doc)
        self.assertIn("上伸线", doc)
        self.assertIn("下伸线", doc)

    def test_accepts_tuple_sequence(self) -> None:
        doc = render_sheet((Row(text="Hi", kind="trace"),))
        self.assertEqual(doc.count('class="row '), 1)

    def test_empty_rows_still_valid(self) -> None:
        doc = render_sheet([])
        self.assertIn("<html", doc)
        self.assertEqual(doc.count('class="row '), 0)


class RenderAlphabetTests(unittest.TestCase):
    """render_alphabet 的字母覆盖与标题用例。"""

    def setUp(self) -> None:
        self.doc = render_alphabet()

    def test_default_title(self) -> None:
        self.assertIn("字母练习", self.doc)

    def test_custom_title_escaped(self) -> None:
        doc = render_alphabet("<Grade 3>")
        self.assertIn("&lt;Grade 3&gt;", doc)

    def test_row_count_matches_alphabet_rows(self) -> None:
        self.assertEqual(self.doc.count('class="row '), len(alphabet_rows()))

    def test_all_uppercase_letters_present(self) -> None:
        for code in range(ord("A"), ord("Z") + 1):
            letter = chr(code)
            self.assertIn(f"{letter}{letter.lower()}", self.doc)

    def test_all_lowercase_letters_present(self) -> None:
        for code in range(ord("a"), ord("z") + 1):
            self.assertIn(chr(code), self.doc)

    def test_every_row_is_trace(self) -> None:
        self.assertEqual(
            self.doc.count('class="row trace"'), len(alphabet_rows())
        )

    def test_has_four_guides_per_row(self) -> None:
        expected = len(alphabet_rows()) * 4
        self.assertEqual(self.doc.count('<span class="line"'), expected)


if __name__ == "__main__":
    unittest.main()
