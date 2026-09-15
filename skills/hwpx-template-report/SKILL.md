---
name: hwpx-template-report
description: Use only when creating Korean official 보고요지 or 보고자료 HWPX files by reusing an existing report template, especially 보고요지/안건 forms, preserving or flexibly copying table/layout structure while summarizing content from DOCX/HWPX/PDF/source documents or Obsidian vault evidence. Do not use for 계획서, 시행계획, 운영계획, 제안서, 공문, or other non-report forms unless the user explicitly says to use this skill. For the 교육용 SW 계약 개선 계획-style landscape layout with Roman-numeral section-header tables, use `hwpx-plan` instead.
---

# HWPX Template Report

Use this skill when the user wants to make a Korean official `보고요지` or `보고자료` from an existing `.hwpx` report form, especially `보고요지`, `안건`, 인수위 보고자료, 업무보고, 결과보고, 현황보고, or similar one-page/short-form reports.

Do not use this skill for `계획서`, `시행계획`, `운영계획`, `추진계획`, `제안서`, `공문`, `품의`, or other non-report forms just because they are HWPX files. For those, ask for or use the separate template/form the user provides, unless the user explicitly says to apply this report-template workflow anyway.

This skill is a specialization on top of `hwpx-core`. Load/use `hwpx-core` as the base HWPX XML toolchain, then follow this workflow.

## Default Workflow

1. Identify the template `.hwpx` and source document paths from the user request.
2. Extract source text:
   - For `.docx`, read `word/document.xml` from the ZIP and collect `w:t` paragraph text.
   - For `.hwpx`, read `Contents/section0.xml` and collect `hp:t` text.
   - Avoid relying on console-typed Korean paths inside inline Python. Prefer `Path.home()` plus glob/search terms, or save a UTF-8 `.py` script and run it through stdin with `exec(open(path, encoding="utf-8").read())` if direct execution has encoding or permission issues.
3. Extract template structure:
   - Save `Contents/section0.xml` and inspect paragraphs/tables.
   - Identify fixed labels such as `보고요지`, `안건`, department/contact lines, and table headers.
   - Preserve labels the user says not to touch. For “안건 옆에 제목”, replace only the adjacent title text cell, not the `안건` label.
4. Draft content from the source:
   - Summarize aggressively when requested.
   - Omit sections the user excludes, such as `개요`, `사업 개요`, or introductory background.
   - Keep official-report phrasing concise: current status, issue, risk, action, deadline.
5. Build the output by template fill:
   - Reuse the original HWPX ZIP entries.
   - Replace only text nodes in `Contents/section0.xml`.
   - Do not rebuild tables unless necessary. Prefer mapping old text to new text so row/column/cell style, border, paragraph, and page layout remain intact.
   - If the template has an existing table, reuse its row count and headings where feasible. Convert source content into the same table shape.
6. Write first to `C:\tmp\<task-name>\...`, then copy the verified final file to the user-facing destination.

## Korean Typography

- Avoid the Korean middle-dot character `U+00B7` in generated report prose, headings, table cells, bullet labels, and filenames unless it is genuinely required by a proper name, fixed official notation, or a symbol whose meaning would change without it.
- Prefer commas, `및`, `과/와`, or `/` according to the sentence meaning. Use an existing bullet symbol only when the template requires a bullet, not as a separator between ordinary phrases.
- Before delivery, search the final `<hp:t>` text and the filename for `U+00B7`, then remove every nonessential occurrence.

## 한컴 편집 안정성 (필수)

보고서 양식은 기존 표를 복사해 채우는 경우가 많아 화면이 정상이어도 내부 표 좌표가 깨질 수 있다. `hwpx-core`의 표 논리 격자 검사를 결과물마다 적용한다.

- 모든 `<hp:tbl>`의 `rowCnt`/`colCnt`, 실제 행·셀 배열, `hp:cellAddr`, `hp:cellSpan`을 대조한다.
- `rowAddr`/`colAddr`는 0-based 논리 좌표이며 범위 초과·행 순서 불일치·span 겹침·빈 칸을 허용하지 않는다. `rowCnt="4"` 표의 마지막 행에 `rowAddr="5"`가 있으면 렌더링 여부와 관계없이 수정한다.
- `<hp:linesegarray>`는 파생 레이아웃 캐시다. 이를 삭제하거나 재생성하는 것만으로 `cellAddr` 오류를 해결했다고 판단하지 않는다.
- 변경한 표마다 한/글에서 셀 선택 → 임시 텍스트 입력·삭제 → 별도 사본 저장을 수행한다. 열기·다시 저장만 성공한 결과는 편집 안전성 검증을 통과한 것으로 보지 않는다.

## Evidence From Obsidian Vault

When the user says to check the vault, `볼트`, previous audit materials, prior reports, or missing background:

1. Search the Obsidian vault first, usually `C:\Users\user\Desktop\ObsidianVault`.
2. Prefer focused searches over broad manual browsing. Use UTF-8 Python scripts when Korean search terms or file names break in the shell.
3. Search both filenames and Markdown contents. Good starting terms:
   - Target topic terms: project name, 사업명, product names, budget amounts, document title words.
   - Evidence terms: `행정사무감사`, `감사`, `지적`, `의회`, `삭감`, `시정명령`, `제보`, `입찰`, `본예산`.
4. Read the most relevant notes and summarize only substantiated points. Do not invent missing details.
5. Add a concise section such as `전년도 행정사무감사 지적 요약`, `감사 지적 및 보완`, or `의회 지적사항 대응` near the related issue/budget/background section.

## Flexible Table Copying

When a source section is better as a table but the template has only one suitable table:

1. Inspect `Contents/section0.xml` with `analyze_template.py` or a read-only namespace-aware parser. Never serialize the section with `xml.etree.ElementTree`/`lxml`; preserve the original XML declaration, namespace placement, and whitespace.
2. Locate the table paragraph or surrounding heading by text.
3. Copy the existing table paragraph as a raw XML slice through `zip_surgery.py`/string helpers; do not round-trip it through an XML serializer.
4. Replace only `hp:t` text nodes in the copied structure.
5. Before packaging, validate every table's logical grid: `rowCnt`/`colCnt`, `cellAddr` (0-based row/column), `cellSpan`, and the absence of out-of-range, overlapping, or missing slots.
6. Insert the cloned heading/table near the related section.
7. Re-run validation. `page_guard --mode template-fill` may warn that a table was added; this is acceptable when the user requested a new table and the warning says existing tables were preserved.

Use this approach for sections like operating status, risk matrix, issue/action list, audit findings, schedules, or budget history when they read better as structured rows.

## Validation Required

Before claiming completion, run:

```powershell
python C:\Users\user\.codex\skills\hwpx-core\scripts\validate.py "<output.hwpx>" --strict
python C:\Users\user\.codex\skills\hwpx-core\scripts\page_guard.py --reference "<template.hwpx>" --output "<output.hwpx>" --mode template-fill
```

For every changed table, perform a Hancom edit smoke test on a disposable copy: select a changed cell, insert and delete a temporary marker, save, and confirm the marker stayed in the intended cell. Opening and saving alone is insufficient.

Also do a text audit by reading `Contents/section0.xml`:

- Fixed labels such as `보고요지` and `안건` remain present.
- The requested title appears in the title cell.
- Excluded source sections are absent.
- The key summarized sections are present.
- Any vault-derived added section is present and matches the evidence found.
- If a table was added, confirm the table count and that the copied table headings/rows are present.

## Practical Pattern

Use a replacement map when the template is already close to the needed structure:

```python
with zipfile.ZipFile(template, "r") as zin:
    section_name = next(n for n in zin.namelist() if n.lower().endswith("section0.xml"))
    section = zin.read(section_name).decode("utf-8")
    for old, new in replacements.items():
        section = section.replace(html.escape(old, quote=False), html.escape(new, quote=False))
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = section.encode("utf-8") if item.filename == section_name else zin.read(item.filename)
            zout.writestr(item, data)
```

Track missing replacements and stop if important old text was not found.

## Gotchas

- Korean paths can break when inline Python is passed through a console with the wrong encoding. Use Unicode escapes, filesystem search terms, or a UTF-8 script read with `exec(open(..., encoding="utf-8").read())`.
- If direct execution of a temporary Python file cannot write a ZIP/HWPX due to sandbox/permission behavior, run the same script body through stdin with `exec(open(...).read())`.
- HWPX is a ZIP package. A `.zip` intermediate can be copied/renamed to `.hwpx` after validation.
- Do not use string rewriting across the whole document for labels the user wants preserved. Replace exact text-node content only.
- Page/layout preservation matters more than creating a perfect new semantic structure. For official forms, keep the original paragraph/table/pageBreak structure unless the user explicitly asks for structural changes.
- Console output may show garbled Korean even when files are UTF-8 and correct. Verify with UTF-8 Python file reads when in doubt.
