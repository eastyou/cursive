from __future__ import annotations

"""model 模块的单元测试。"""

import unittest
from dataclasses import FrozenInstanceError

from cursive.model import (
    BASELINE_GAP_MM,
    MAX_LINE_LENGTH,
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


class ValidateLineTests(unittest.TestCase):
    """validate_line 的正向与反向用例。"""

    def test_accepts_letters(self) -> None:
        self.assertEqual(validate_line("Hello"), "Hello")

    def test_accepts_letters_digits_and_spaces(self) -> None:
        self.assertEqual(validate_line("Grade 3 Class 2"), "Grade 3 Class 2")

    def test_accepts_allowed_punctuation(self) -> None:
        self.assertEqual(validate_line("Hi, Tom! It's fine; ok? yes."), "Hi, Tom! It's fine; ok? yes.")

    def test_accepts_hyphen_and_colon(self) -> None:
        self.assertEqual(validate_line("well-known: a-b"), "well-known: a-b")

    def test_strips_surrounding_whitespace(self) -> None:
        self.assertEqual(validate_line("   hello   "), "hello")

    def test_accepts_exactly_max_length(self) -> None:
        text = "a" * MAX_LINE_LENGTH
        self.assertEqual(validate_line(text), text)

    def test_rejects_over_max_length(self) -> None:
        with self.assertRaises(CursiveError) as ctx:
            validate_line("a" * (MAX_LINE_LENGTH + 1))
        self.assertIn(str(MAX_LINE_LENGTH), str(ctx.exception))

    def test_rejects_empty_string(self) -> None:
        with self.assertRaises(CursiveError):
            validate_line("")

    def test_rejects_whitespace_only(self) -> None:
        with self.assertRaises(CursiveError):
            validate_line("   ")

    def test_rejects_chinese_characters(self) -> None:
        with self.assertRaises(CursiveError) as ctx:
            validate_line("你好世界")
        self.assertIn("不支持", str(ctx.exception))

    def test_rejects_accented_letters(self) -> None:
        with self.assertRaises(CursiveError):
            validate_line("café")

    def test_rejects_brackets(self) -> None:
        with self.assertRaises(CursiveError):
            validate_line("hello (world)")

    def test_rejects_tab(self) -> None:
        with self.assertRaises(CursiveError):
            validate_line("hello\tworld")

    def test_rejects_emoji(self) -> None:
        with self.assertRaises(CursiveError):
            validate_line("hello 😀")

    def test_rejects_non_string(self) -> None:
        with self.assertRaises(CursiveError):
            validate_line(None)  # type: ignore[arg-type]

    def test_rejects_integer(self) -> None:
        with self.assertRaises(CursiveError):
            validate_line(123)  # type: ignore[arg-type]


class WrapTextTests(unittest.TestCase):
    """wrap_text 的换行、硬切与边界用例。"""

    def test_wraps_at_word_boundary(self) -> None:
        self.assertEqual(wrap_text("one two three four", 9), ["one two", "three", "four"])

    def test_every_line_within_limit(self) -> None:
        for line in wrap_text("The quick brown fox jumps over the lazy dog.", 12):
            self.assertLessEqual(len(line), 12)

    def test_words_are_preserved(self) -> None:
        text = "The quick brown fox jumps over the lazy dog."
        self.assertEqual(" ".join(wrap_text(text, 10)), text)

    def test_hard_cuts_long_word(self) -> None:
        self.assertEqual(
            wrap_text("abcdefghijklmnopqrst", 5),
            ["abcde", "fghij", "klmno", "pqrst"],
        )

    def test_hard_cut_after_short_word(self) -> None:
        self.assertEqual(wrap_text("hi abcdefghijkl", 5), ["hi", "abcde", "fghij", "kl"])

    def test_lower_bound_of_max_chars(self) -> None:
        self.assertEqual(wrap_text("abcde fghij", 5), ["abcde", "fghij"])

    def test_upper_bound_of_max_chars(self) -> None:
        text = "a" * 40
        self.assertEqual(wrap_text(text, 40), [text])

    def test_rejects_too_small_max_chars(self) -> None:
        with self.assertRaises(CursiveError):
            wrap_text("hello", 4)

    def test_rejects_too_large_max_chars(self) -> None:
        with self.assertRaises(CursiveError):
            wrap_text("hello", 41)

    def test_rejects_non_integer_max_chars(self) -> None:
        with self.assertRaises(CursiveError):
            wrap_text("hello", 5.5)  # type: ignore[arg-type]

    def test_rejects_string_max_chars(self) -> None:
        with self.assertRaises(CursiveError):
            wrap_text("hello", "5")  # type: ignore[arg-type]

    def test_rejects_boolean_max_chars(self) -> None:
        with self.assertRaises(CursiveError):
            wrap_text("hello", True)  # type: ignore[arg-type]

    def test_exact_fit_stays_on_one_line(self) -> None:
        self.assertEqual(wrap_text("abc de", 6), ["abc de"])

    def test_single_short_word(self) -> None:
        self.assertEqual(wrap_text("hello", 24), ["hello"])

    def test_rejects_empty_text(self) -> None:
        with self.assertRaises(CursiveError):
            wrap_text("", 24)

    def test_rejects_invalid_text(self) -> None:
        with self.assertRaises(CursiveError):
            wrap_text("你好", 24)

    def test_default_limit_is_24(self) -> None:
        for line in wrap_text("The quick brown fox jumps over the lazy dog."):
            self.assertLessEqual(len(line), 24)


class AlphabetRowsTests(unittest.TestCase):
    """alphabet_rows 的分组与覆盖面用例。"""

    def test_returns_six_rows(self) -> None:
        self.assertEqual(len(alphabet_rows()), 6)

    def test_first_row_content(self) -> None:
        self.assertEqual(alphabet_rows()[0], "Aa Bb Cc Dd Ee")

    def test_last_row_content(self) -> None:
        self.assertEqual(alphabet_rows()[-1], "Zz")

    def test_covers_all_uppercase_letters(self) -> None:
        joined = "".join(alphabet_rows())
        for code in range(ord("A"), ord("Z") + 1):
            self.assertIn(chr(code), joined)

    def test_covers_all_lowercase_letters(self) -> None:
        joined = "".join(alphabet_rows())
        for code in range(ord("a"), ord("z") + 1):
            self.assertIn(chr(code), joined)

    def test_each_pair_matches_case(self) -> None:
        for line in alphabet_rows():
            tokens = line.split(" ")
            self.assertIn(len(tokens), (1, 5))
            for token in tokens:
                self.assertEqual(len(token), 2)
                self.assertEqual(token[0].upper(), token[0])
                self.assertEqual(token[0].lower(), token[1])

    def test_each_row_within_length_limit(self) -> None:
        for line in alphabet_rows():
            self.assertLessEqual(len(line), MAX_LINE_LENGTH)

    def test_total_pairs_is_26(self) -> None:
        tokens = " ".join(alphabet_rows()).split(" ")
        self.assertEqual(len(tokens), 26)

    def test_every_row_is_valid_line(self) -> None:
        for line in alphabet_rows():
            self.assertEqual(validate_line(line), line)


class BuildRowsTests(unittest.TestCase):
    """build_rows 的样式、行数与补齐用例。"""

    def test_trace_style_all_trace(self) -> None:
        rows = build_rows("The quick brown fox jumps over the lazy dog.", "trace", 6)
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(row.kind == "trace" for row in rows[:2]))

    def test_blank_style_all_blank(self) -> None:
        rows = build_rows("Hello class", "blank", 6)
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(row.kind == "blank" for row in rows))

    def test_fade_style_first_two_trace(self) -> None:
        rows = build_rows("The quick brown fox jumps over the lazy dog.", "fade", 6)
        self.assertEqual([row.kind for row in rows[:3]], ["trace", "trace", "blank"])

    def test_fade_pads_with_blank_rows(self) -> None:
        rows = build_rows("Hello", "fade", 8)
        self.assertEqual(rows[0].kind, "trace")
        self.assertTrue(all(row.kind == "blank" for row in rows[1:]))
        self.assertTrue(all(row.text == "" for row in rows[1:]))

    def test_trace_pads_with_blank_rows(self) -> None:
        rows = build_rows("Hello", "trace", 8)
        self.assertEqual(rows[0].kind, "trace")
        self.assertTrue(all(row.kind == "blank" for row in rows[1:]))

    def test_blank_preserves_text_data(self) -> None:
        rows = build_rows("Hello class", "blank", 4)
        self.assertEqual(rows[0].text, "Hello class")

    def test_long_text_is_truncated_to_rows(self) -> None:
        source = "word " * 12
        rows = build_rows(source.strip(), "trace", 2)
        self.assertEqual(len(rows), 2)

    def test_rows_lower_bound_accepted(self) -> None:
        self.assertEqual(len(build_rows("Hi", "trace", 2)), 2)

    def test_rows_upper_bound_accepted(self) -> None:
        self.assertEqual(len(build_rows("Hi", "trace", 20)), 20)

    def test_rows_too_small_rejected(self) -> None:
        with self.assertRaises(CursiveError):
            build_rows("Hi", "trace", 1)

    def test_rows_too_large_rejected(self) -> None:
        with self.assertRaises(CursiveError):
            build_rows("Hi", "trace", 21)

    def test_rows_non_integer_rejected(self) -> None:
        with self.assertRaises(CursiveError):
            build_rows("Hi", "trace", "8")  # type: ignore[arg-type]

    def test_rows_boolean_rejected(self) -> None:
        with self.assertRaises(CursiveError):
            build_rows("Hi", "trace", True)  # type: ignore[arg-type]

    def test_invalid_style_rejected(self) -> None:
        with self.assertRaises(CursiveError):
            build_rows("Hi", "fancy", 4)

    def test_style_is_case_sensitive(self) -> None:
        with self.assertRaises(CursiveError):
            build_rows("Hi", "Trace", 4)

    def test_non_string_style_rejected(self) -> None:
        with self.assertRaises(CursiveError):
            build_rows("Hi", None, 4)  # type: ignore[arg-type]

    def test_invalid_source_rejected(self) -> None:
        with self.assertRaises(CursiveError):
            build_rows("你好", "trace", 4)

    def test_empty_source_rejected(self) -> None:
        with self.assertRaises(CursiveError):
            build_rows("", "trace", 4)

    def test_wraps_long_source_across_rows(self) -> None:
        rows = build_rows("The quick brown fox jumps over the lazy dog.", "trace", 8)
        self.assertTrue(rows[0].text.startswith("The quick"))
        self.assertEqual(len(rows), 8)


class RowAndDemoTests(unittest.TestCase):
    """Row 数据类与 demo_text 的用例。"""

    def test_row_fields(self) -> None:
        row = Row(text="Hello", kind="trace")
        self.assertEqual(row.text, "Hello")
        self.assertEqual(row.kind, "trace")

    def test_row_is_frozen(self) -> None:
        row = Row(text="Hello", kind="trace")
        with self.assertRaises(FrozenInstanceError):
            row.text = "Bye"  # type: ignore[misc]

    def test_demo_text_is_valid(self) -> None:
        self.assertEqual(validate_line(demo_text()), demo_text())

    def test_demo_text_length(self) -> None:
        self.assertLessEqual(len(demo_text()), MAX_LINE_LENGTH)

    def test_demo_text_content(self) -> None:
        self.assertIn("quick brown fox", demo_text())

    def test_constants(self) -> None:
        self.assertEqual(BASELINE_GAP_MM, 8.0)
        self.assertEqual(ZONE_MM, 4.0)
        self.assertEqual(ROW_HEIGHT_MM, 16.0)

    def test_row_height_matches_zones(self) -> None:
        self.assertEqual(ROW_HEIGHT_MM, ZONE_MM * 2 + BASELINE_GAP_MM)


if __name__ == "__main__":
    unittest.main()
