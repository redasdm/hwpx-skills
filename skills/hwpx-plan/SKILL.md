---
name: hwpx-plan
description: Use when creating or updating HWPX files in the landscape Korean official plan layout, either the `교육용 SW 계약 개선 계획(안).hwpx`-style Education SW form or the AIEP AI 업무지원·상담 지식지도 계획안 form. Both use a 6-row table cover, copied Roman-numeral section header tables, symbol-only body outline (`□`, `❍`, `-`), and optional roadmap tables. Use this skill when the user mentions the plan(안) style, the three-line/center-title cover table, Roman numerals inside a copied table graphic, the AIEP AI 업무지원 계획안, or asks to avoid numbered `1.`/`2.` body headings in that form.
---

# HWPX Plan (Education SW / AIEP)

Build Korean official HWPX plan documents that reuse the landscape plan(안) layout. This skill is a narrow specialization on top of `hwpx-core`; use a bundled template asset as the base ZIP package and modify only `Contents/section0.xml`.

## When To Use

Education SW form (`assets/education_sw_plan_template.hwpx`):

- First page has a 6-row table cover, with the title/subtitle only in the large merged center title cell.
- Section headers are copied 8-row x 7-column tables containing Roman numerals such as `Ⅰ`, `Ⅱ`, `Ⅲ`.
- The long section title is inside the merged title cell of that Roman header table.
- Body hierarchy after each Roman header must use symbols only: `□` then `❍` then `-`.
- Body tables should copy the existing table style from the template, not be hand-built from scratch.

AIEP AI 업무지원 form (`assets/aiep_ai_subscription_plan_template.hwpx`):

- Same cover/header/roadmap structure, with the AIEP 상담 활용 concept diagram and cover logo kept.
- Used for the AIEP AI 업무지원·상담 지식지도 계획안 and its 수정본 (account counts, cost, and scope of use).
- Generated prose must not name a specific vendor or model; use `AI 업무지원 서비스` or `AI`.

Do not use this for generic HWPX editing, 공문, 보고요지, 안건, or unrelated plan forms unless the user explicitly says this exact layout should be reused.

## Bundled Templates

| Target document | Template asset |
| --- | --- |
| Education SW 계약 개선 계획(안) style | `assets/education_sw_plan_template.hwpx` |
| AIEP AI 업무지원·상담 지식지도 계획안 | `assets/aiep_ai_subscription_plan_template.hwpx` |

Keep both assets. Pass `--template "<asset>"` when the AIEP form, not the default Education SW asset, is the base.

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
2. Use the bundled template that matches the target form unless the user explicitly provides a different `.hwpx` template:

```powershell
$SKILL_DIR\assets\education_sw_plan_template.hwpx
$SKILL_DIR\assets\aiep_ai_subscription_plan_template.hwpx
```

3. Save or locate the pasted/source outline as a UTF-8 `.txt`.
4. Run the bundled script:

```powershell
python "$SKILL_DIR\scripts\education_sw_plan_style.py" `
  --source-text "<outline.txt>" `
  --output "<output.hwpx>"
```

Pass `--template "<template.hwpx>"` when the user provides a different template with the same layout, or when building the AIEP form.

The script does not refresh `hp:linesegarray` by default. Leave visual line wrapping to Hancom/manual editing unless the user explicitly asks for automatic line layout. If needed, pass `--refresh-line-layout`.

When the user hands over an existing plan document and only wants wording, numbers, or one account changed, edit that document instead of regenerating it from an outline: follow `## AIEP AI 업무지원·상담 지식지도 계획안 양식` below.

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

## AIEP AI 업무지원·상담 지식지도 계획안 양식

기준 자산은 `assets/aiep_ai_subscription_plan_template.hwpx`이다. 기존의 일반 교육용 SW 계약 양식인 `assets/education_sw_plan_template.hwpx`는 호환성 때문에 삭제하지 않는다.

기준 양식의 구조는 다음과 같다.

- 표지: 6행×2열 표. 제목과 작성일은 표지의 기존 셀에만 둔다.
- 본문 섹션: `Ⅰ`~`Ⅳ` 로마자 표기와 긴 제목을 포함한 8행×7열 섹션 표를 복사해 사용한다.
- 본문 계층: `□` → `❍` → `-` 기호만 사용하며, 독립적인 `1.`·`2.` 제목은 만들지 않는다.
- 단계표: `단계·일정·주요 과업·기대 산출물` 4열 관리표의 기존 스타일을 복사한다.
- 도식: 표지 로고와 AIEP 상담 활용 개념도 이미지를 유지한다.

### 기존 문서 수정 절차

사용자가 HWPX를 제공하면 그 파일을 기준으로 `analyze_template.py`로 `header.xml`과 `Contents/section0.xml` 구조를 확인한다. 새 내용이 아니라 기존 양식의 문구·수치만 바꾸는 경우에는 `zip_surgery.py`의 raw ZIP-level surgery를 우선 사용한다.

수정 대상은 원칙적으로 `Contents/section0.xml` 하나로 제한한다. 표 행·열, 셀 병합, 문단 수, 이미지, ZIP 엔트리 순서와 비수정 파일의 바이트는 보존한다. `ElementTree`/`lxml`로 section XML을 직렬화하거나 `cell_writer.py`를 surgery 결과에 실행하지 않는다.

### 계정 1개 추가 규칙

기준 4계정 문서에 연구사 1명의 계정을 추가할 때는 `scripts/aiep_account_update.py`를 사용한다.

```powershell
python "$SKILL_DIR/scripts/aiep_account_update.py" `
  "<4계정 원본.hwpx>" `
  "<5계정 결과.hwpx>"
```

헬퍼는 다음을 한 번에 일관되게 바꾼다.

- 수량: 4개 → 5개
- 계정당 200천원 × 4개 → 계정당 200천원 × 5개
- 총액: 800천원 → 1,000천원
- 소요예산: 금800,000원(금팔십만원) → 금1,000,000원(금일백만원)
- 공동 활용 인원: 상담 담당 4명 + `SW교육 아카데미·영재·수석 업무 담당 연구사 1명`
- 신규 담당 범위: 아카데미·영재·수석 관련 자료 작성·활용

`4개월` 이용기간은 계정 수와 혼동하지 말고 그대로 유지한다. 단가나 견적이 달라진 경우에는 문서의 단가·수량·총액·소요예산을 함께 재계산한다.

### 문구 및 사업 타당성 원칙

- 특정 모델명이나 `Claude`·`클로드` 같은 업체·제품명을 기준 문서에 남기지 않는다.
- 신규 연구사 계정은 SW교육 아카데미, 영재교육, 수석교사 업무의 안내자료·연수자료·상담 답변 초안 작성과 기존 자료 검색에 활용한다고 명시한다.
- 계정별 개별 이용은 담당 업무를 병렬 처리하고, 확정 답변·자료를 상담 지식지도에 공동 축적하기 위한 것으로 설명한다.
- AI가 작성한 초안은 담당자가 확인한 뒤 상담 답변·FAQ·안내문·교육자료로 재사용한다.
- 개인정보·민감정보·비공개 자료를 외부 AI 서비스에 그대로 입력하지 않으며, 필요한 경우 비식별화·보안 검토 후 사용한다.

## 한컴 편집 안정성 점검

이 형식은 복사한 표가 많으므로 화면 모양이 같아도 표의 내부 좌표가 손상될 수 있다. `hwpx-core`의 표 논리 격자 검사를 반드시 적용한다.

- 복사·삽입한 모든 표에서 `rowCnt`/`colCnt`와 `<hp:tr>`/`<hp:tc>` 구조를 대조한다.
- 각 `hp:cellAddr`의 0-based `rowAddr`/`colAddr`가 논리 격자 범위 안에 있고, `cellSpan`을 반영해 겹침·빈 칸·범위 초과가 없는지 확인한다. `rowCnt="4"`인데 마지막 행이 `rowAddr="5"`인 형태는 금지한다.
- `linesegarray`를 삭제·재생성하는 것만으로 표 좌표 오류를 고친 것으로 간주하지 않는다.
- 변경한 표마다 한/글에서 셀을 실제 선택해 임시 텍스트를 입력·삭제하고 별도 사본에 저장한다. 단순 열기·저장 성공은 편집 검증이 아니다.

## Validation

Run at least:

```powershell
python C:\Users\user\.codex\skills\hwpx-core\scripts\validate.py "<output.hwpx>" --strict
python C:\Users\user\.codex\skills\hwpx-core\scripts\text_extract.py "<output.hwpx>"
python C:\Users\user\.codex\skills\hwpx-core\scripts\page_guard.py --reference "<template.hwpx>" --output "<output.hwpx>"
```

The script serializes `Contents/section0.xml` the way 한/글 does: it keeps the template's XML
declaration and root namespace declarations and writes no newlines. `validate.py --strict` may
still report `standalone='no' missing` — the bundled template and 한/글-saved files declare
`standalone="yes"`, so treat that single finding as expected and rely on the 한/글 smoke test
below for the open/edit confirmation.

For every changed table, perform a Hancom edit smoke test on a disposable copy: select a changed cell, insert and delete a temporary marker, save, and confirm the marker stayed in the intended cell. Opening and saving alone is insufficient.

Text audit requirements:

- Cover title/subtitle appear at the beginning.
- Every Roman header appears in order.
- Body headings use `□`, `❍`, and `-`; no standalone body lines match `^\d+\.\s`.
- Roadmap table data is present if supplied.
- If `page_guard.py` fails because section/table counts changed to match new content, report that as expected for structure-regenerated outputs; do not claim page parity.

AIEP form additional audit items:

- 계정 수·단가·총액·소요예산이 서로 일치하는가
- `SW교육 아카데미·영재·수석` 담당 범위와 5번째 계정의 근거가 있는가
- 단계표와 개념도 관련 텍스트가 유지되는가
- `Claude`·`클로드`가 남아 있지 않은가

새 양식 자산의 section XML에는 한/글에서 생성되는 그림 설명의 개행이 포함될 수 있으므로, strict 검증 전 그림 설명 안의 개행을 공백으로 정규화하고 XML 선언의 `standalone="no"`를 보존한다.
