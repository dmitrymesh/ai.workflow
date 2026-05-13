# Execution Report: AI-025

## Summary

Updated workflow instructions so Unity executors may modify scenes, prefabs,
assets, and `.meta` files through Unity MCP or Editor-backed tooling when the
task contract explicitly authorizes it. Direct hand edits to Unity serialized
YAML remain forbidden in all cases.

The policy change is consistently applied across five documents:

- **`unity-guardrails.md`**: main policy document — renamed "Forbidden" header
  to "Forbidden by default" and added an explicit "Unity MCP / editor-backed
  changes — exception when explicitly authorized" section defining the three
  required contract conditions (scope named, tooling stated, validation
  included).
- **`manager.md`**: added "Authorizing Unity serialized asset changes" block
  prompting managers to name specific assets, state the tooling, include
  validation, and use `high` risk unless tightly isolated.
- **`executor.md`**: added an indented exception under the forbidden-files rule
  explaining when authorized Unity MCP/editor-backed changes are allowed and
  when to stop (tooling inaccessible).
- **`reviewer.md`**: expanded the "Check forbidden file changes" bullet to give
  explicit guidance for Unity serialized files — check three conditions before
  flagging as a violation.
- **`AGENTS.md`**: replaced the single-line Unity file prohibition with a
  two-sentence version that distinguishes authorized MCP/editor-backed changes
  from the permanently forbidden direct hand edits.

`config.yaml` forbidden file patterns are unchanged.

## Changed files

- `.ai-workflow/skills/unity-guardrails.md`
- `.ai-workflow/skills/manager.md`
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/reviewer.md`
- `AGENTS.md`

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `git diff --name-only main...HEAD` — only skill files, AGENTS.md, and task folder; no Unity serialized files
- Manual review: no `.unity`, `.prefab`, `.asset`, `.meta`, package, or project settings files modified
- Forbidden file check: passed — config.yaml patterns untouched

## Assumptions

- `CLAUDE.md` already says "If you need to modify forbidden files, stop and write the reason in `report.md`" and references `unity-guardrails.md`. With `unity-guardrails.md` updated, CLAUDE.md implicitly inherits the correct policy without a direct edit.
- The three-condition requirement (scope named, tooling stated, validation included) is the minimum explicit contract needed to safely authorize MCP/editor-backed changes. This mirrors the spirit of existing "explicitly allowed in task.md" language.

## Known risks

- Low. Documentation-only change. Misreading the three conditions is the main failure mode; the language is explicit and anchored to `task.md` content.
