#!/usr/bin/env python3
"""Extract text from an HWPX document.

Uses python-hwpx's TextExtractor when available, with a built-in XML fallback
so the CLI works in a fresh Codex environment.

Usage:
    python text_extract.py document.hwpx
    python text_extract.py document.hwpx --format markdown
    python text_extract.py document.hwpx --include-tables
"""

import argparse
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

try:
    from hwpx import TextExtractor
except ModuleNotFoundError:
    TextExtractor = None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _paragraph_text(elem: ET.Element, *, include_tables: bool, in_table: bool = False) -> str:
    parts: list[str] = []
    name = _local_name(elem.tag)
    now_in_table = in_table or name == "tbl"

    if now_in_table and not include_tables:
        return ""

    if name == "t":
        parts.append(elem.text or "")
    elif name in {"tab", "tabCore"}:
        parts.append("\t")
    elif name in {"lineBreak", "br"}:
        parts.append("\n")

    for child in elem:
        parts.append(_paragraph_text(child, include_tables=include_tables, in_table=now_in_table))

    return "".join(parts)


def _iter_section_xml(hwpx_path: str):
    with zipfile.ZipFile(hwpx_path) as zf:
        names = sorted(
            name for name in zf.namelist()
            if name.startswith("Contents/section") and name.endswith(".xml")
        )
        for name in names:
            yield name, zf.read(name)


def _extract_plain_fallback(hwpx_path: str, *, include_tables: bool = False) -> str:
    lines: list[str] = []
    for _, xml_bytes in _iter_section_xml(hwpx_path):
        root = ET.fromstring(xml_bytes)
        for elem in root.iter():
            if _local_name(elem.tag) != "p":
                continue
            text = _paragraph_text(elem, include_tables=include_tables).strip()
            if text:
                lines.append(text)
    return "\n".join(lines)


def _extract_markdown_fallback(hwpx_path: str) -> str:
    sections: list[str] = []
    for _, xml_bytes in _iter_section_xml(hwpx_path):
        root = ET.fromstring(xml_bytes)
        lines: list[str] = []
        for elem in root.iter():
            if _local_name(elem.tag) != "p":
                continue
            text = _paragraph_text(elem, include_tables=True).strip()
            if text:
                lines.append(text)
        if lines:
            sections.append("\n".join(lines))
    return "\n\n---\n\n".join(sections)


def extract_plain(hwpx_path: str, *, include_tables: bool = False) -> str:
    """Extract plain text from HWPX file."""

    if TextExtractor is None:
        return _extract_plain_fallback(hwpx_path, include_tables=include_tables)

    object_behavior = "nested" if include_tables else "skip"
    with TextExtractor(hwpx_path) as ext:
        return ext.extract_text(
            include_nested=include_tables,
            object_behavior=object_behavior,
            skip_empty=True,
        )


def extract_markdown(hwpx_path: str) -> str:
    """Extract text as Markdown with section separators."""

    if TextExtractor is None:
        return _extract_markdown_fallback(hwpx_path)

    lines: list[str] = []

    with TextExtractor(hwpx_path) as ext:
        for section in ext.iter_sections():
            if lines:
                lines.append("")
                lines.append("---")
                lines.append("")

            for para in ext.iter_paragraphs(section, include_nested=True):
                text = para.text(object_behavior="nested")
                if text.strip():
                    if para.is_nested:
                        # Table cell or nested content - indent
                        lines.append(f"  {text}")
                    else:
                        lines.append(text)

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from an HWPX document")
    parser.add_argument("input", help="Path to .hwpx file")
    parser.add_argument(
        "--format",
        "-f",
        choices=["plain", "markdown"],
        default="plain",
        help="Output format (default: plain)",
    )
    parser.add_argument(
        "--include-tables",
        action="store_true",
        help="Include text from tables and nested objects (plain mode)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    if not Path(args.input).is_file():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.format == "markdown":
        result = extract_markdown(args.input)
    else:
        result = extract_plain(args.input, include_tables=args.include_tables)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Extracted to: {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
