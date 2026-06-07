# HWPX Skills

Reusable Codex skills for creating, editing, validating, and template-filling Korean HWPX documents.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `hwpx-core` | XML-first HWPX toolchain: extract, analyze, build, validate, page-guard, table/cell handling, and template-based generation. |
| `hwpx-template-report` | Korean official 보고요지/보고자료 template-fill workflow for existing HWPX report forms, including evidence lookup and flexible table copying. |
| `hwpx-plan` | Specialized plan/report layout based on the `교육용 SW 계약 개선 계획(안).hwpx` style: landscape cover table, Roman-numeral section header tables, symbol-only body outline, and roadmap tables. |

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

The `hwpx-plan` script uses its bundled template by default. Pass `--template <path>` only when you have another HWPX template with the same layout.

## Documentation

See [docs/SKILL_GUIDE.md](docs/SKILL_GUIDE.md) for usage patterns, expected source text format, validation commands, and notes for contributors.

## License

MIT. See [LICENSE](LICENSE).
