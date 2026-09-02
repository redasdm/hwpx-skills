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

## 한컴 편집 안정성 점검

이 형식은 복사한 표가 많으므로 화면 모양이 같아도 표의 내부 좌표가 손상될 수 있다. `hwpx-core`의 표 논리 격자 검사를 반드시 적용한다.

- 복사·삽입한 모든 표에서 `rowCnt`/`colCnt`와 `<hp:tr>`/`<hp:tc>` 구조를 대조한다.
- 각 `hp:cellAddr`의 0-based `rowAddr`/`colAddr`가 논리 격자 범위 안에 있고, `cellSpan`을 반영해 겹침·빈 칸·범위 초과가 없는지 확인한다. `rowCnt="4"`인데 마지막 행이 `rowAddr="5"`인 형태는 금지한다.
- `linesegarray`를 삭제·재생성하는 것만으로 표 좌표 오류를 고친 것으로 간주하지 않는다.
- 변경한 표마다 한/글에서 셀을 실제 선택해 임시 텍스트를 입력·삭제하고 별도 사본에 저장한다. 단순 열기·저장 성공은 편집 검증이 아니다.

## Validation

Run at least:

```powershell
python C:\Users\redas\.codex\skills\hwpx-core\scripts\validate.py "<output.hwpx>" --strict
python C:\Users\redas\.codex\skills\hwpx-core\scripts/text_extract.py "<output.hwpx>"
python C:\Users\redas\.codex\skills\hwpx-core\scripts/page_guard.py --reference "<template.hwpx>" --output "<output.hwpx>"
```

For every changed table, perform a Hancom edit smoke test on a disposable copy: select a changed cell, insert and delete a temporary marker, save, and confirm the marker stayed in the intended cell. Opening and saving alone is insufficient.

Text audit requirements:

- Cover title/subtitle appear at the beginning.
- Every Roman header appears in order.
- Body headings use `□`, `❍`, and `-`; no standalone body lines match `^\d+\.\s`.
- Roadmap table data is present if supplied.
- If `page_guard.py` fails because section/table counts changed to match new content, report that as expected for structure-regenerated outputs; do not claim page parity.
