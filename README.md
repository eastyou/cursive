# cursive · 英文连笔字帖生成器

[![CI](https://github.com/eastyou/cursive/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/cursive/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)


一个零第三方依赖的小工具：把单词、句子或字母表排成 A4 英文书写练习纸。
纸张采用标准「四线三格」（上伸线、中线、基线、下伸线），支持描摹行与空白练习行，
适合教师布置书写作业，也适合学生打印练习。

## 特性

- 纯 Python 标准库实现，Python 3.9+ 可用，无需安装任何依赖。
- 输出单文件 HTML，A4 尺寸精确到毫米，浏览器直接打印即可。
- 三种行样式：`trace`（全描摹）、`fade`（前 2 行描摹，其余空白）、`blank`（全空白）。
- 内置字母表、示例句子与自定义文本三种内容来源。
- 严格的输入校验：非法字符、超长文本、越界行数都会给出中文提示并返回退出码 2。

## 安装

```bash
python -m pip install -e .
```

也可以不安装，直接在仓库根目录使用 `python -m cursive`。

## 快速开始

```bash
# 内置示例句子，生成 8 行 fade 字帖
python -m cursive --demo -o examples/cursive.html

# 自定义句子
python -m cursive --text "Practice makes perfect." --rows 10 --style trace -o sheet.html

# 字母表描摹页
python -m cursive --alphabet -o examples/alphabet.html

# 从标准输入读取一行
echo "Hello class" | python -m cursive --text - -o sheet.html
```

## 命令行参数

| 参数 | 说明 |
| --- | --- |
| `-o, --output PATH` | 输出 HTML 路径，默认 `cursive.html` |
| `--text TEXT` | 练习文本；传 `-` 时从标准输入读取一行 |
| `--demo` | 使用内置示例句子 |
| `--alphabet` | 生成字母表描摹页，优先于 `--text` 与 `--demo` |
| `--style STYLE` | `trace` / `fade` / `blank`，默认 `fade` |
| `--rows N` | 练习行数，范围 2–20，默认 8 |

成功时输出「已生成 <path>（N 行）」并返回 0；参数非法返回 2；写文件失败返回 1。

## 文本规则

- 允许 ASCII 字母、数字、空格与 `.,!?;:'-`。
- 单行长度不超过 60 个字符。
- 超出每行宽度（24 字符）时按单词换行，超长单词硬切分。

## 版面

- 页面：A4，`@page { size: A4; margin: 0 }`，内容区 210mm × 297mm、内边距 12mm。
- 单行高度 16mm = 上伸区 4mm + 基线间距 8mm + 下伸区 4mm，中线为虚线。
- 描摹文字使用浅灰等宽字体，空白行不显示文字。

## 开发与测试

```bash
python -m unittest discover -s tests -v
```

## 示例

- `examples/cursive.html`：内置句子的 8 行字帖。
- `examples/alphabet.html`：Aa–Zz 字母表描摹页。

## 许可证

MIT © 2026 eastyou
