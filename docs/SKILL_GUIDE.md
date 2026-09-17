# HWPX Skill Guide

This repository contains three Codex skills:

- `hwpx-core`: the base XML-first HWPX workflow.
- `hwpx-template-report`: a template-fill workflow for Korean official 보고요지/보고자료 forms.
- `hwpx-plan`: specialized template skills for the plan(안) forms — the 전북교육청 기본계획(안) form (A4 portrait) and the landscape Education SW / AIEP forms, all of which use Roman-numeral section header tables.

## Repository Layout

```text
skills/
  hwpx-core/
    SKILL.md
    scripts/
    templates/
    references/
    tests/
  hwpx-template-report/
    SKILL.md
    agents/
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

## Using `hwpx-template-report`

Use `hwpx-template-report` when filling or adapting an existing Korean official report template such as `보고요지`, `보고자료`, `안건`, 업무보고, 결과보고, or 현황보고.

This skill is for template preservation:

- reuse the original HWPX ZIP entries;
- inspect `Contents/section0.xml` and `Contents/header.xml`;
- preserve fixed labels such as `보고요지` and `안건`;
- replace only the target title/content cells or text nodes;
- copy existing table paragraphs when new structured sections are needed;
- optionally search an Obsidian vault for supporting evidence when the user asks for prior audit, council, or background material.

Do not use `hwpx-template-report` for the Education SW plan-style Roman header layout. Use `hwpx-plan` for that form.

Report prose follows the skill's Korean Typography rule: avoid the middle-dot character `U+00B7` in prose, headings, table cells, bullet labels, and filenames unless a proper name, fixed official notation, or a symbol meaning requires it. Prefer commas, `및`, `과/와`, or `/`, and audit the final `<hp:t>` text before delivery.

Typical request:

```text
Use $hwpx-template-report to create a 보고요지 from this template HWPX and the attached source document.
```

Validation is stricter for template-fill work:

```powershell
python .\skills\hwpx-core\scripts\validate.py ".\result.hwpx"
python .\skills\hwpx-core\scripts\page_guard.py --reference ".\template.hwpx" --output ".\result.hwpx" --mode template-fill
```

## Using `hwpx-plan`

### 전북교육청 기본계획(안) form

Base asset: `skills/hwpx-plan/assets/jbe_ai_agent_basic_plan_template.hwpx` (교수학습용 AI에이전트 구축 및 운영 기본계획(안) v10).

- A4 portrait, body width 48190 HWPUNIT, nine `pageBreak="1"` paragraphs.
- Skeleton: 결재란 8x9 → cover 5x2 (logo cell + title cell) → emblem block 2x2 → summary page → body title page → Ⅰ~Ⅷ sections (8x7 header tables) → 첨부 1x2.
- The title text appears on three cover tables and must be changed on all of them; keep the `hidePageNum="1"` control in the cover's second paragraph.
- Body outline is `❐` → `❍` → `-`, indented with leading spaces inside `<hp:t>` plus a negative `hc:intent`. Do not strip those spaces for this form.
- The summary page heading symbol is U+F071 with its own charPr; do not replace it with `□`.
- Edit this form with `zip_surgery.py` on `Contents/section0.xml` only. `education_sw_plan_style.py` does not target it.

Full cell maps, style IDs, and the color/font palette are in `skills/hwpx-plan/SKILL.md`.

### Education SW form

Use this only for the Education SW plan-style HWPX layout:

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

### AIEP AI 업무지원 Form

The same layout family also covers the AIEP AI 업무지원·상담 지식지도 계획안 form. Use its bundled asset as the base:

```powershell
python .\skills\hwpx-plan\scripts\education_sw_plan_style.py `
  --source-text ".\outline.txt" `
  --template ".\skills\hwpx-plan\assets\aiep_ai_subscription_plan_template.hwpx" `
  --output ".\result.hwpx"
```

When the user hands over an existing AIEP plan and only wants wording, numbers, or one account changed, edit that document with raw ZIP surgery through `zip_surgery.py` instead of regenerating it: keep `Contents/section0.xml` as the only modified entry, and do not round-trip it through an XML serializer or `cell_writer.py`.

Adding one researcher account to the 4-account document has a dedicated helper:

```powershell
python .\skills\hwpx-plan\scripts\aiep_account_update.py `
  ".\AIEP_plan_4accounts.hwpx" `
  ".\AIEP_plan_5accounts.hwpx"
```

It updates 수량 (`4개` → `5개`), 계정당 200천원 × 4개 → × 5개, 총액 `800천원` → `1,000천원`, 소요예산 `금800,000원(금팔십만원)` → `금1,000,000원(금일백만원)`, and the joint-use scope line for the SW교육 아카데미·영재·수석 담당 연구사. The `4개월` 이용기간 is not an account count and must stay unchanged. Keep generated prose free of vendor or model names (`Claude`/`클로드` included); write `AI 업무지원 서비스` or `AI`.

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

For `hwpx-plan` output, `validate.py --strict` may report `standalone='no' missing` from `section0.xml`. The bundled templates and 한/글-saved files declare `standalone="yes"`, so treat that single finding as expected and confirm editability with the 한/글 smoke test instead. The generated section XML stays single-line and reuses the template's XML declaration and root namespace declarations.

## Contributor Notes

- Do not commit `__pycache__`, logs, or generated output documents.
- Keep skill instructions concise and executable.
- Prefer template cloning and text-node replacement over rebuilding HWPX XML from scratch.
- Validate each skill folder and at least one generated HWPX before publishing changes.
