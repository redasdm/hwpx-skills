---
name: hwpx-plan
description: Use when creating or updating HWPX files in the landscape Korean official layout based on `교육용 SW 계약 개선 계획(안).hwpx`, especially documents with a 6-row table cover, copied Roman-numeral section header tables, symbol-only body outline (`□`, `❍`, `-`), and optional roadmap tables. Use this skill when the user mentions the Education SW plan style, the three-line/center-title cover table, Roman numerals inside a copied table graphic, or asks to avoid numbered `1.`/`2.` body headings in that form.
---

# HWPX Education SW Plan

Build Korean official HWPX documents that reuse the `교육용 SW 계약 개선 계획(안).hwpx`-style layout. This skill is a narrow specialization on top of `hwpx-core`; use the bundled template asset as the base ZIP package and modify only `Contents/section0.xml`.

## When To Use

Use this skill when the user asks for the specific Education SW plan-style HWPX form:

- First page has a 6-row table cover, with the title/subtitle only in the large merged center title cell.
- Section headers are copied 8-row x 7-column tables containing Roman numerals such as `Ⅰ`, `Ⅱ`, `Ⅲ`.
- The long section title is inside the merged title cell of that Roman header table.
- Body hierarchy after each Roman header must use symbols only: `□` then `❍` then `-`.
- Body tables should copy the existing table style from the template, not be hand-built from scratch.

Do not use this for generic HWPX editing, 공문, 보고요지, 안건, or unrelated plan forms unless the user explicitly says this exact layout should be reused.

## Input Pattern

The bundled script expects a UTF-8 plain text outline:

```text
문서 제목
- 부제 -

작성일: 2026년 6월 5일
보고부서: 전북특별자치도교육청 미래교육과

Ⅰ. 첫 번째 섹션 제목
1. 붙여넣은 숫자 제목
□ 붙여넣은 중간 제목
❍ 붙여넣은 세부 문장

Ⅱ. 두 번째 섹션 제목
...
```

The script normalizes this to:

```text
Ⅰ [copied Roman table header]
□ 숫자 제목에서 변환된 제목
❍ 중간 제목
- 세부 문장
```

Roadmap tables are detected when the source includes consecutive lines starting with:

```text
단계
일정
주요 과업
기대 산출물
```

Those lines are inserted into a copied 4-column management-table style. Values like `1단계`, `2단계` inside the roadmap table are table data and should remain unchanged.

## Build Workflow

1. Load/use `hwpx-core` for HWPX validation and extraction.
2. Use the bundled template unless the user explicitly provides a different `.hwpx` template. The bundled asset is:

```powershell
$SKILL_DIR\assets\education_sw_plan_template.hwpx
```

3. Save or locate the pasted/source outline as a UTF-8 `.txt`.
4. Run the bundled script:

```powershell
python "$SKILL_DIR\scripts\education_sw_plan_style.py" `
  --source-text "<outline.txt>" `
  --output "<output.hwpx>"
```

Pass `--template "<template.hwpx>"` only when the user provides a different template with the same layout.

The script does not refresh `hp:linesegarray` by default. Leave visual line wrapping to Hancom/manual editing unless the user explicitly asks for automatic line layout. If needed, pass `--refresh-line-layout`.

## Preservation Rules

- Preserve the first 6-row cover table. Put the main title/subtitle only in the large merged center title cell; keep decorative surrounding cells copied from the template.
- Copy Roman-numeral header tables from the template. Do not recreate them as plain paragraphs, SVG, or newly drawn tables.
- Replace only the Roman numeral text and the long section-title cell text inside each copied header table.
- Normalize body hierarchy to symbols only after Roman headers:
  - pasted `1.`, `2.` headings become `□`;
  - nested pasted `□` lines become `❍`;
  - nested pasted `❍` lines become `-`.
- Use template paragraph nodes for indentation and style. Do not rely on literal spaces for body indentation.
- Copy existing same-shape body tables when a table is needed. For roadmap content, reuse the 4-column management table style.

## Validation

Run at least:

```powershell
python C:\Users\redas\.codex\skills\hwpx-core\scripts\validate.py "<output.hwpx>"
python C:\Users\redas\.codex\skills\hwpx-core\scripts\text_extract.py "<output.hwpx>"
```

Text audit requirements:

- Cover title/subtitle appear at the beginning.
- Every Roman header appears in order.
- Body headings use `□`, `❍`, and `-`; no standalone body lines match `^\d+\.\s`.
- Roadmap table data is present if supplied.
- If `page_guard.py` fails because section/table counts changed to match new content, report that as expected for structure-regenerated outputs; do not claim page parity.
