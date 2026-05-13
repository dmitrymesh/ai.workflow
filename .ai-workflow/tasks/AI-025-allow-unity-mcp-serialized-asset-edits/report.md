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
  included). Direct manual YAML edits are described as "forbidden by default;
  allowed only when task.md explicitly requests direct YAML editing and defines
  scope and validation" (not "never allowed").
- **`manager.md`**: added "Authorizing Unity serialized asset changes" block
  prompting managers to name specific assets, state the method (MCP/Editor
  preferred; direct manual YAML as last resort when well-bounded), include
  validation, and use `high` risk unless tightly isolated.
- **`executor.md`**: added an indented exception under the forbidden-files rule
  explaining when authorized Unity MCP/editor-backed changes are allowed and
  when to stop (tooling inaccessible). Also clarified that hand-editing Unity
  serialized YAML is forbidden by default but allowed when task.md explicitly
  requests it with defined scope and validation.
- **`reviewer.md`**: expanded the "Check forbidden file changes" bullet — Unity
  serialized files are accepted when `task.md` authorized them with scope and
  either (a) MCP/Editor tooling or (b) explicit direct manual YAML request with
  validation. Missing authorization remains a blocking issue.
- **`AGENTS.md`**: replaced the single-line Unity file prohibition with a
  two-sentence version that distinguishes authorized MCP/editor-backed changes
  from direct hand edits. Direct hand edits are described as "forbidden by
  default; allowed only when task.md explicitly requests it" — not permanently
  forbidden.

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

## Changes from review round 2

- `manager.md`: replaced "not direct YAML edits" wording with a two-path
  description — MCP/Editor preferred, direct manual YAML as last resort when
  small and well-bounded.
- `reviewer.md`: expanded the forbidden-file check from three MCP/Editor
  conditions to two branches: (a) MCP/Editor tooling or (b) explicit direct
  YAML request with validation.

## Changes from review round 1

- `unity-guardrails.md`: changed "direct hand edits are never allowed" header parenthetical to "Forbidden by default" (no parenthetical); changed "remain forbidden even when authorized" to "forbidden by default; allowed only when task.md explicitly requests direct YAML editing."
- `executor.md`: added explicit exception to the hand-edit prohibition parallel to the MCP exception.
- `AGENTS.md`: changed "remain forbidden even when the task authorizes the change" to "forbidden by default; allowed only when task.md explicitly requests direct manual editing."

## Known risks

- Low. Documentation-only change. Misreading the three conditions is the main failure mode; the language is explicit and anchored to `task.md` content.
