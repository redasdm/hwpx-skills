#!/usr/bin/env python3
"""Add one account to the AIEP AI 업무지원 plan form.

The form is edited with raw ZIP-level surgery so the cover, copied section
header tables, roadmap table, images, and non-section ZIP entries remain
unchanged.  The helper is intentionally narrow: it updates the 4-account
AIEP plan to the requested 5-account version.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CORE_SCRIPTS = Path(__file__).resolve().parents[1].parent / "hwpx-core" / "scripts"
if str(CORE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(CORE_SCRIPTS))

from zip_surgery import read_zip, replace_text_in_section, write_zip  # noqa: E402


INPUT_ACCOUNTS = 4
ADDED_ACCOUNTS = 1
UNIT_COST = 200_000


def _replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"Expected one occurrence of {old!r}, found {count}.")
    return text.replace(old, new, 1)


def _normalize_section(text: str) -> str:
    """Keep the target form's section XML single-line and strict-valid."""
    text = re.sub(r"(<\?xml[^>]*\?>)[\r\n\t ]*(<hs:sec\b)", r"\1\2", text, count=1)

    def flatten_comment(match: re.Match[str]) -> str:
        value = match.group(2).replace("\r", " ").replace("\n", " ")
        value = re.sub(r"[ \t]{2,}", " ", value)
        return match.group(1) + value + match.group(3)

    text = re.sub(
        r"(<hp:shapeComment>)(.*?)(</hp:shapeComment>)",
        flatten_comment,
        text,
        flags=re.DOTALL,
    )
    return text.replace("\r", "").replace("\n", "")


def update(input_path: Path, output_path: Path) -> None:
    entries, order = read_zip(input_path)
    section_name = "Contents/section0.xml"
    entry_map = {entry.filename: entry for entry in entries}
    if section_name not in entry_map:
        raise ValueError(f"{section_name} not found in {input_path}")

    new_accounts = INPUT_ACCOUNTS + ADDED_ACCOUNTS
    new_total = UNIT_COST * new_accounts
    section = entry_map[section_name].data
    replacements = {
        "계정·수업·평가·기능·연수 등": "계정·수업·평가·기능·연수·아카데미·영재·수석 등",
        "- 4개월 이용권을 담당자별 1개씩 구독하여 상담 정리·답변 작성·연수자료 활용 병행":
        "- 4개월 이용권을 담당자별 1개씩 구독하여 상담 답변·아카데미·영재·수석 자료 작성 병행",
        "- 담당자 4명이 정리한 내용을 하나의 상담 지식지도로 모아 공동 활용":
        "- 상담 담당 4명과 SW교육 아카데미·영재·수석 업무 담당 연구사 1명이 공동 활용",
        "수량: 4개": "수량: 5개",
        "계정당 200천원 × 4개 = 총 800천원(견적 기준)":
        "계정당 200천원 × 5개 = 총 1,000천원(견적 기준)",
        "소요예산: 금800,000원(금팔십만원)":
        "소요예산: 금1,000,000원(금일백만원)",
        "AI교수학습역량강화 사업을 활용한 AIEP 상담·연수 지원 업무 효율화":
        "AI교수학습역량강화 사업을 활용한 AIEP 상담·아카데미·영재·수석 업무 효율화",
    }

    section_text = section.decode("utf-8")
    for old, new in replacements.items():
        section_text = _replace_once(section_text, old, new)
    declaration_yes = section_text.count('standalone="yes"')
    declaration_no = section_text.count('standalone="no"')
    if declaration_yes == 1 and declaration_no == 0:
        section_text = section_text.replace('standalone="yes"', 'standalone="no"', 1)
    elif declaration_yes != 0 or declaration_no != 1:
        raise ValueError("Expected one standalone XML declaration.")
    section_text = _normalize_section(section_text)

    if "Claude" in section_text or "클로드" in section_text:
        raise ValueError("Vendor-specific Claude wording remains in the document.")
    if section_text.count("수량: 5개") != 1 or "총 1,000천원" not in section_text:
        raise ValueError("Account quantity or total amount audit failed.")
    if section_text.count("금1,000,000원(금일백만원)") != 1:
        raise ValueError("Budget amount audit failed.")
    if section_text.count("\n") or section_text.count("\r"):
        raise ValueError("section0.xml still contains newline characters.")

    write_zip(output_path, entries, order, {section_name: section_text.encode("utf-8")})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="4-account AIEP plan HWPX")
    parser.add_argument("output", type=Path, help="5-account output HWPX")
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"Input HWPX not found: {args.input}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    update(args.input, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
