---
name: hwpx-plan
description: Use when creating or updating HWPX files in the Korean official plan(안) layouts this skill covers: (1) the 전북교육청 기본계획(안) form (A4 portrait, 결재란 + 로고 표지 + 요약면 + Ⅰ~Ⅷ Roman-numeral 8x7 section header tables + ❐/❍/- body outline, as in 교수학습용 AI에이전트 구축 및 운영 기본계획(안)), (2) the `교육용 SW 계약 개선 계획(안).hwpx`-style Education SW form, and (3) the AIEP AI 업무지원·상담 지식지도 계획안 form. Use this skill when the user mentions the plan(안) style, a cover table whose title/logo cells must be swapped, Roman numerals inside a copied table graphic, the AIEP AI 업무지원 계획안, or asks to avoid numbered `1.`/`2.` body headings in those forms.
---

# HWPX Plan (전북교육청 기본계획(안) / Education SW / AIEP)

Build Korean official HWPX plan documents that reuse one of the bundled plan(안) layouts. This skill is a narrow specialization on top of `hwpx-core`; use a bundled template asset as the base ZIP package and modify only `Contents/section0.xml`.

세 양식은 표지 구조와 본문 기호 체계가 서로 다르다. 작업 전에 어느 양식인지 먼저 확정한다.

| 양식 | 판형 | 표지 | 본문 계층 |
| --- | --- | --- | --- |
| 전북교육청 기본계획(안) | A4 세로 | 결재란 + 5행×2열 표지표 + 엠블럼 블록 | `❐` → `❍` → `-` |
| 교육용 SW 계약 개선 계획(안) | 가로 | 6행 표지표 | `□` → `❍` → `-` |
| AIEP AI 업무지원 계획안 | 가로 | 6행×2열 표지표 + 개념도 | `□` → `❍` → `-` |

## When To Use

전북교육청 기본계획(안) form (`assets/jbe_ai_agent_basic_plan_template.hwpx`):

- A4 세로 판형이고, 첫 페이지 상단에 8행×9열 결재란이 있다.
- 표지는 5행×2열 표이며 로고 셀과 제목 셀이 분리되어 있다. 표지 문구는 표지·요약면·본문 시작 표지 3곳에 반복된다.
- 섹션 헤더는 `Ⅰ`~`Ⅷ` 로마숫자와 `◤` 장식을 담은 8행×7열 표다.
- 본문 계층은 `❐` → `❍` → `-` 이고, 들여쓰기는 선행 공백 + 음수 `hc:intent` 조합이다.
- 상세 규격은 아래 `## 전북교육청 기본계획(안) 양식` 절을 따른다.

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
| 전북교육청 기본계획(안) style (교수학습용 AI에이전트 v10) | `assets/jbe_ai_agent_basic_plan_template.hwpx` |
| Education SW 계약 개선 계획(안) style | `assets/education_sw_plan_template.hwpx` |
| AIEP AI 업무지원·상담 지식지도 계획안 | `assets/aiep_ai_subscription_plan_template.hwpx` |

세 자산을 모두 유지한다. 기본값은 Education SW 자산이므로, 다른 양식이 기준이면 `--template "<asset>"`을 넘긴다.

전북교육청 기본계획(안) 양식은 개요 텍스트에서 새로 생성하는 방식이 아니라 기준 문서를 복사해 수정하는 방식이 기본이다. `education_sw_plan_style.py`는 이 양식을 대상으로 하지 않는다.

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

## 전북교육청 기본계획(안) 양식 (교수학습용 AI에이전트 v10 기준)

기준 자산은 `assets/jbe_ai_agent_basic_plan_template.hwpx`(교수학습용 AI에이전트 구축 및 운영 기본계획(안) v10)이다.
앞의 교육용 SW / AIEP 양식과 달리 **A4 세로** 판형이고 본문 최상위 기호가 `❐`이므로 혼동하지 않는다.

### 페이지 설정

- `<hp:pagePr width="59528" height="84186">` — A4 세로
- 여백: `left/right=5669`(20mm), `top/bottom=4251`(15mm), `header=2834`, `footer=0`
- 본문폭 **48190 HWPUNIT**. 본문 이미지는 `curSz width="48190"`, 표는 47604~48188
- 페이지 나눔은 `<hp:p ... pageBreak="1">` 문단 9개로 제어된다. 위치를 임의로 옮기거나 지우지 않는다

### 문서 골격 (순서 고정)

1. **결재란** 8×9 표 — 등록번호 / 담당자 / AI디지털담당 / 미래교육과장 / 정책국장 / 부교육감 / 교 육 감, 등록일자, 결재일자, 공개구분, 협조. 결재선 칸과 날짜 자리표시(`2026.    .    .`)는 그대로 둔다
2. **표지** 5×2 표 (+ 로고)
3. **엠블럼 블록** 2×2 표 (엠블럼 + 로고 + 부서명)
4. — page break — **요약면**: `···(요약)` 표지표 + ` 개요` / ` 주요 기능`(①②③ + 설명 이미지) / `※` 용어 풀이 / `❐ 연차별 개요` + 6×3 표
5. — page break — **본문 시작 표지** 5×2 표 (로고 자리에 슬로건 이미지)
6. **Ⅰ~Ⅷ 섹션**: 각각 8×7 헤더표 + 본문. 기본 구성은 Ⅰ 추진 배경 및 근거 / Ⅱ 비전 및 추진체계 / Ⅲ 추진 개요 / Ⅳ 전략별 세부 추진과제 / Ⅴ 추진 체계 및 업무 분장 / Ⅵ 연차별 추진 계획 / Ⅶ 소요 예산 / Ⅷ 기대 효과 및 행정 사항
7. **첨부** 1×2 표 (`첨부` | `참 고 자 료`) + 법령 / 연구자료 / 자체 자료 목록

### 표지 — 제목과 로고

표지는 `rowCnt="5" colCnt="2" borderFillIDRef="4" noAdjust="0"`, 전체 폭 47907의 표다.

| 셀 | span | 역할 |
| --- | --- | --- |
| r0c0 | 1×1 | 빈 칸 |
| **r0c1** | 1×1 | **로고 이미지** (`paraPr 36` = 오른쪽 정렬) |
| r1c0 | colSpan 2 | 윗 간격줄 (borderFill 20) |
| **r2c0** | colSpan 2, `cellSz 47907×7634`, borderFill 8, vertAlign CENTER | **제목 셀** |
| r3c0 | colSpan 2 | 아래 간격줄 (borderFill 21) |
| r4c0 / r4c1 | 1×1 | 하단 여백 셀 |

제목 교체는 r2c0 안의 두 문단 텍스트만 바꾼다.

- 1문단: `paraPrIDRef="45"`(JUSTIFY) + `charPrIDRef="81"`(26pt HY헤드라인M) — 윗줄. 원본은
  `<hp:t>     교수학습용 AI에이전트</hp:t>`처럼 **선행 공백 5칸**이 들어 있다. 시각 정렬용이므로 글자 수가 크게
  달라지면 개수를 조정하되 임의로 제거하지 않는다
- 2문단: `paraPrIDRef="40"`(CENTER) + `charPrIDRef="22"`(31pt HY헤드라인M) — 아랫줄. 이 문단 안의
  `<hp:ctrl><hp:pageHiding ... hidePageNum="1"/></hp:ctrl>`는 **표지 쪽번호 숨김 제어문자**다. 반드시 보존하고
  그 앞뒤 `<hp:t>`만 치환한다
- 요약면 표지는 같은 구조에 `charPr 45`(21pt) + `charPr 46`(26pt) 조합이고 제목 끝이 `(안)` 대신 `(요약)`이다
- **제목을 바꿀 때는 표지 3곳(표지 / 요약면 / 본문 시작 표지)을 모두 같은 문구로 맞춘다.** 파일명도 함께 맞춘다

로고·엠블럼은 이미 `BinData/`에 들어 있고 여러 곳에서 재사용된다. `binaryItemIDRef`를 건드리지 않는 것이 기본이다.

| 이미지 | 원본명 | 위치 |
| --- | --- | --- |
| `image1` | 가로조합형.jpg (전북특별자치도교육청 가로조합형 로고) | 표지 r0c1, 요약면 표지 r0c1 |
| `image2` | 엠블럼.png | 엠블럼 블록 r0c0 (rowSpan 2) |
| `image3` | 혼용좌우조합.png | 엠블럼 블록 r0c1 |
| `image7` | 전북특별자치도교육청_슬로건_최종-한줄.png | 본문 시작 표지 r0c1 |
| `image8` | 기호용 작은 bmp | Ⅱ 비전 표 내부 화살표 8회 |
| `image4~6`, `image9~11` | 개념도·운영구조·조직도 | 요약면 · Ⅲ · Ⅴ 본문 |

- 로고를 새 이미지로 교체할 때만 `image_embedder.py`로 `BinData/` + `Contents/content.hpf` 2곳에 등록한 뒤 해당
  셀의 `binaryItemIDRef`만 바꾼다. `header.xml`에 `binDataList`를 추가하지 않는다
- `<hp:pic>` XML을 직접 쓰지 말고 `image_embedder.py`의 `make_pic_xml()`을 쓴다. 기존 그림의 `orgSz`/`curSz`/
  `shapeComment`는 손대지 않는다
- 부서명은 엠블럼 블록 r1c1의 `charPrIDRef="82"`(18pt HY울릉도M bold, 글자색 `#022F63`) 문단 하나만 치환한다

### 섹션 헤더표 (8×7)

`rowCnt="8" colCnt="7"`, 폭 47604. 장식 셀이 대부분이므로 **표를 통째로 복사해 쓰고 텍스트 2개만 바꾼다.**

- `r0c1` = 로마숫자. borderFill 10 = 배경 `#106886`, `charPrIDRef="28"` = 17pt 맑은 고딕 bold **흰색**, `paraPr 21` CENTER
- `r0c4` = 섹션 제목. `charPrIDRef="31"` = 16pt HY헤드라인M, `paraPr 33`(LEFT, 내어쓰기 -3170). 제목 앞 공백 1칸 관습 유지
- `r1c2` = `◤` 장식 (`charPrIDRef="33"` = 18pt, 글자색 `#AEAEAE`). **지우지 않는다**
- 나머지 셀(borderFill 9·11·12·13·14·15·16·17)은 모서리 장식·여백이다. 비어 보인다고 삭제하거나 병합하지 않는다
- 섹션을 추가할 때는 표를 담고 있는 `<hp:p>` 블록 전체를 복사해 로마숫자·제목만 바꾸고, 앞에 `pageBreak="1"` 문단을 동일하게 넣는다

### 본문 계층 — ❐ → ❍ → -

| 수준 | 기호 | paraPr | charPr | 선행 공백 |
| --- | --- | --- | --- | --- |
| 1 | `❐` | 46 (JUSTIFY, 줄간격 165%) | 53 (17pt 휴먼명조) | 없음 |
| 2 | `❍` | 55 (내어쓰기 intent -3115, 145%) | 27 (15pt 휴먼명조) | 1칸 |
| 3 | `-` | 55 | 27 | 3칸 |
| 표 내부 | `◦` | 107 / 74 | 27 | 없음 |

- 본문 문단은 `styleIDRef="60"`을 쓴다
- **이 양식은 `<hp:t>` 안 선행 공백 + paraPr의 음수 `hc:intent` 조합으로 들여쓰기를 만든다.** 교육용 SW 양식의
  "공백 들여쓰기 금지" 규칙과 반대이므로, 기존 문단을 복제해 글자만 바꾸는 방식으로 작업한다
- 독립된 `1.`·`2.` 숫자 제목을 만들지 않는다. 붙여넣은 원고에 숫자 제목이 있으면 `❐`로 내린다
- Ⅳ장은 `[전략 1] ···` 대괄호 소제목, Ⅵ장은 `1년차(´27) — 설계·표준화` 형식의 연차 소제목을 쓴다
- **요약면 제목 기호는 ``(U+F071, 기호 글꼴 문자) + `charPrIDRef="43"`이다.** 일반 `□`나 `❐`로 치환하면 글꼴
  매핑이 깨진다
- 요약면 기능 설명은 `① ② ③`, 강조는 `※`, 비전표 사항은 `￭`를 쓴다

### 본문 표 양식 (복사해서 쓴다)

| 용도 | 구조 | 헤더 |
| --- | --- | --- |
| 연차별 개요·로드맵 | 6×3 (폭 48188) | `구분` / `단계` / `주요 추진 내용` |
| 추진 경과 | 6×3 | `기간` / `추진내용` / `비고` |
| 업무 분장 | 7×3 | `담당` / `구분` / `주요 업무` |
| 현장지원단 | 5×2 | `구성` / `역할` |
| 소요 예산 | 5×3 | `회계연도` / `주요 내용` / `금액(천원)` |
| 비전·추진체계도 | 21×5 + 중첩표 6개 | 교육비전/슬로건/목적/목표/전략/과제/방향/연차별계획 |
| 첨부 간지 | 1×2 | `첨부` / `참 고 자 료` |

- 표 헤더행은 borderFill 28·29(배경 `#DFE6F7`, 상단 굵은선) + `charPr 44`(15pt bold)
- 데이터행은 borderFill 19·30, 셀 내부 불릿은 `◦`
- 새 표는 직접 작성하지 말고 같은 용도의 기존 표를 복사해 행을 늘리거나 줄인다. 부득이 프로그램으로 만들어야 하면
  `xml_writer.py`의 `build_table()`을 쓴다

### 색상·글꼴 팔레트

| 항목 | 값 |
| --- | --- |
| 강조색(로마숫자 배지·헤더선) | `#106886` |
| 부서명 글자색 | `#022F63` |
| 표 헤더 배경 | `#DFE6F7` |
| `◤` 장식 | `#AEAEAE` |
| 제목 글꼴 | HY헤드라인M (fontRef hangul=7) |
| 부서명 글꼴 | HY울릉도M (6) |
| 본문 글꼴 | 휴먼명조 (4), 15pt |
| 로마숫자·표 헤더 | 맑은 고딕 (0) |

### 기존 문서 수정 절차

문구·수치·제목만 바꾸는 작업은 생성이 아니라 수술이다.

1. `analyze_template.py`로 `header.xml` / `Contents/section0.xml` 구조 파악
2. `zip_surgery.py`로 `Contents/section0.xml` **하나만** 교체. 나머지 ZIP 엔트리의 바이트·순서는 그대로 둔다
3. `ElementTree`/`lxml`로 section XML을 직렬화하지 않고, surgery 결과에 `cell_writer.py`를 돌리지 않는다
4. 표 행·열, 셀 병합, 문단 수, 이미지, `pageBreak` 문단을 보존한다
5. 제목을 바꿨다면 표지 3곳과 파일명까지 일괄 일치시킨다

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

기준 자산 `jbe_ai_agent_basic_plan_template.hwpx`는 한/글이 저장한 원본 그대로이며, `validate.py`가 다음 4건을
기본으로 보고한다. 한/글에서 정상 열람·편집되는 문서이므로 이 4건은 기준선으로 보고, 새로 늘어난 항목만 결함으로 다룬다.

- `hp:pic is not inside <hp:run>` 2건 (요약면 설명 이미지)
- `BinData/image5.png`, `BinData/image6.png`: 확장자는 png이지만 실제 포맷은 JPEG

전북교육청 기본계획(안) 양식 추가 감사 항목:

- 표지·요약면·본문 시작 표지 3곳의 제목 문구가 서로 일치하는가
- 표지 2문단의 `hidePageNum="1"` 제어문자가 남아 있는가
- 로고·엠블럼·슬로건 이미지(`image1`·`image2`·`image3`·`image7`)와 개념도 이미지가 모두 유지되는가
- 본문 기호가 `❐`/`❍`/`-`이고 요약면 제목 기호가 ``(U+F071)로 남아 있는가
- 섹션 헤더표의 `◤` 장식 셀과 주변 장식 셀이 삭제되지 않았는가
- 예산표 합계와 본문 금액 서술이 일치하는가

AIEP form additional audit items:

- 계정 수·단가·총액·소요예산이 서로 일치하는가
- `SW교육 아카데미·영재·수석` 담당 범위와 5번째 계정의 근거가 있는가
- 단계표와 개념도 관련 텍스트가 유지되는가
- `Claude`·`클로드`가 남아 있지 않은가

새 양식 자산의 section XML에는 한/글에서 생성되는 그림 설명의 개행이 포함될 수 있으므로, strict 검증 전 그림 설명 안의 개행을 공백으로 정규화하고 XML 선언의 `standalone="no"`를 보존한다.
