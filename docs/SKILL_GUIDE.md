# HWPX Skill Guide

This repository contains two Codex skills:

- `hwpx-core`: the base XML-first HWPX workflow.
- `hwpx-plan`: a specialized template skill for the landscape plan/report style that uses Roman-numeral section header tables.

## Repository Layout

```text
skills/
  hwpx-core/
    SKILL.md
    scripts/
    templates/
    references/
    tests/
  hwpx-plan/
    SKILL.md
    scripts/
    assets/
docs/
  SKILL_GUIDE.md
```

## Using `hwpx-core`

Use `hwpx-core` for general HWPX work:

- unpacking or repacking HWPX files;
- extracting `Contents/header.xml` and `Contents/section0.xml`;
- inspecting paragraph styles, character styles, borders, and table structures;
- building new HWPX files from XML;
- validating ZIP/XML structure;
- checking page and layout drift against a reference document.

Common commands:

```powershell
python .\skills\hwpx-core\scripts\analyze_template.py ".\template.hwpx" `
  --extract-header ".\header.xml" `
  --extract-section ".\section0.xml"

python .\skills\hwpx-core\scripts\validate.py ".\result.hwpx"

python .\skills\hwpx-core\scripts\text_extract.py ".\result.hwpx"
```

## Using `hwpx-plan`

Use `hwpx-plan` only for the Education SW plan-style HWPX layout:

- 6-row cover table;
- title/subtitle placed only in the large merged center cover cell;
- Roman numerals such as `Ⅰ`, `Ⅱ`, `Ⅲ` inside copied 8-row x 7-column header tables;
- section title inside the long merged title cell of the same header table;
- body hierarchy normalized to `□ -> ❍ -> -`;
- optional roadmap table using a copied 4-column table style.

### Source Text Format

Prepare a UTF-8 text file:

```text
문서 제목
- 부제 -

작성일: 2026년 6월 5일
보고부서: 전북특별자치도교육청 미래교육과

Ⅰ. 추진 배경
1. 숫자 제목은 □로 변환
□ 중간 제목은 ❍로 변환
❍ 세부 문장은 -로 변환

Ⅱ. 추진 계획
...
```

Run:

```powershell
python .\skills\hwpx-plan\scripts\education_sw_plan_style.py `
  --source-text ".\outline.txt" `
  --output ".\result.hwpx"
```

The script does not refresh `hp:linesegarray` by default. That lets Hancom/manual editing handle visual line wrapping. To force automatic line layout, add:

```powershell
--refresh-line-layout
```

### Roadmap Tables

The script detects a roadmap table when it sees these four consecutive lines:

```text
단계
일정
주요 과업
기대 산출물
```

Subsequent lines are grouped in rows of four and inserted into a copied table style. Values such as `1단계`, `2단계`, and `3단계` are table data and remain unchanged.

## Validation Checklist

After generation, run:

```powershell
python .\skills\hwpx-core\scripts\validate.py ".\result.hwpx"
python .\skills\hwpx-core\scripts\text_extract.py ".\result.hwpx"
```

Check:

- the output is valid HWPX;
- the cover title and subtitle appear at the beginning;
- Roman section headers appear in order;
- body lines use `□`, `❍`, and `-`;
- no standalone body line matches `^\d+\.\s`;
- roadmap table data is present if supplied.

`page_guard.py` may fail when the number of sections or tables intentionally differs from the reference template. In that case, report the structural difference instead of claiming page parity.

## Contributor Notes

- Do not commit `__pycache__`, logs, or generated output documents.
- Keep skill instructions concise and executable.
- Prefer template cloning and text-node replacement over rebuilding HWPX XML from scratch.
- Validate both the skill folder and at least one generated HWPX before publishing changes.

