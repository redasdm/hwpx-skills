# HWPX Skills

Reusable Codex skills for creating, editing, validating, and template-filling Korean HWPX documents.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `hwpx-core` | XML-first HWPX toolchain: extract, analyze, build, validate, page-guard, table/cell handling, and template-based generation. |
| `hwpx-template-report` | Korean official 보고요지/보고자료 template-fill workflow for existing HWPX report forms, including evidence lookup and flexible table copying. |
| `hwpx-plan` | Specialized plan/report layout based on the `교육용 SW 계약 개선 계획(안).hwpx` style: landscape cover table, Roman-numeral section header tables, symbol-only body outline, and roadmap tables. Also covers the AIEP AI 업무지원·상담 지식지도 계획안 form with its 4-account → 5-account update helper, and the 체험센터·미래교육연구원 보고자료 form (교원 파견·운영 요청). |

## Install

Copy the skill folders into your Codex skills directory:

```powershell
Copy-Item -Recurse .\skills\hwpx-core "$env:USERPROFILE\.codex\skills\hwpx-core"
Copy-Item -Recurse .\skills\hwpx-template-report "$env:USERPROFILE\.codex\skills\hwpx-template-report"
Copy-Item -Recurse .\skills\hwpx-plan "$env:USERPROFILE\.codex\skills\hwpx-plan"
```

Then restart or reload Codex so the skills list is refreshed.

## Quick Use

Use `$hwpx-core` for general `.hwpx` work:

```text
Use $hwpx-core to inspect this HWPX template and extract section0.xml/header.xml.
```

Use `$hwpx-template-report` for Korean official report-summary forms:

```text
Use $hwpx-template-report to fill this 보고요지 HWPX template from the attached source document.
```

Use `$hwpx-plan` for the Education SW plan-style document:

```powershell
python .\skills\hwpx-plan\scripts\education_sw_plan_style.py `
  --source-text .\example-outline.txt `
  --output .\result.hwpx
```

The `hwpx-plan` script uses its bundled Education SW template by default. Pass `--template` for another form of the family: `.\skills\hwpx-plan\assets\aiep_ai_subscription_plan_template.hwpx` for the AIEP AI 업무지원 계획안, or `.\skills\hwpx-plan\assets\center_dispatch_report_template.hwpx` for a 체험센터·미래교육연구원 보고자료 (교원 파견·운영 요청).

```powershell
python .\skills\hwpx-plan\scripts\education_sw_plan_style.py `
  --template .\skills\hwpx-plan\assets\center_dispatch_report_template.hwpx `
  --source-text .\examples\center-report-outline.txt `
  --output .\report.hwpx
```

Any document of the same layout family can serve as a template: it needs a 6x2 cover table, an 8x7 section-header table, a `□` heading line, an `❍` body line, an empty paragraph, and a 4-column table.

For the AIEP form, add one researcher account to an existing 4-account document:

```powershell
python .\skills\hwpx-plan\scripts\aiep_account_update.py `
  ".\AIEP_plan_4accounts.hwpx" `
  ".\AIEP_plan_5accounts.hwpx"
```

## Documentation

See [docs/SKILL_GUIDE.md](docs/SKILL_GUIDE.md) for usage patterns, expected source text format, validation commands, and notes for contributors.

## License

MIT. See [LICENSE](LICENSE).
