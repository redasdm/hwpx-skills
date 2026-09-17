# HWPX Skills

Reusable Codex skills for creating, editing, validating, and template-filling Korean HWPX documents.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `hwpx-core` | XML-first HWPX toolchain: extract, analyze, build, validate, page-guard, table/cell handling, and template-based generation. |
| `hwpx-template-report` | Korean official 보고요지/보고자료 template-fill workflow for existing HWPX report forms, including evidence lookup and flexible table copying. |
| `hwpx-plan` | Specialized plan(안) layouts: the 전북교육청 기본계획(안) form (A4 portrait, 결재란 + logo cover + summary page + Ⅰ~Ⅷ Roman-numeral header tables + `❐`/`❍`/`-` outline), the `교육용 SW 계약 개선 계획(안).hwpx` landscape style, and the AIEP AI 업무지원·상담 지식지도 계획안 form with its 4-account → 5-account update helper. |

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

Use `$hwpx-plan` for the 전북교육청 기본계획(안) form — copy the bundled reference document and edit it, rather than generating from an outline:

```text
Use $hwpx-plan to retitle skills/hwpx-plan/assets/jbe_ai_agent_basic_plan_template.hwpx and replace the Ⅲ section body.
```

Use `$hwpx-plan` for the Education SW plan-style document:

```powershell
python .\skills\hwpx-plan\scripts\education_sw_plan_style.py `
  --source-text .\example-outline.txt `
  --output .\result.hwpx
```

The `hwpx-plan` script uses its bundled Education SW template by default. Pass `--template .\skills\hwpx-plan\assets\aiep_ai_subscription_plan_template.hwpx` for the AIEP AI 업무지원 계획안 form, or any other HWPX template with the same layout. The 전북교육청 기본계획(안) asset (`jbe_ai_agent_basic_plan_template.hwpx`) has a different cover/outline system and is not a target of this generator script — edit it with `zip_surgery.py` as described in the skill.

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
