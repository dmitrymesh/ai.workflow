# Execution Report: AI-027

## Summary

Updated workflow instructions so executors on Unity-profile projects must
trigger a Unity MCP / editor-backed recompilation and inspect compiler
diagnostics before submitting. The policy is consistently applied across five
documents.

- **`unity-guardrails.md`**: added "Validation for Unity-profile tasks" section
  with a numbered recompile → check-errors → check-logs sequence, and explicit
  `passed` / `failed` / `not run` reporting rules for `validation.md`.
- **`executor.md`**: added Unity-profile validation bullets after the existing
  "Validation honesty" block — when Unity MCP is available, recompile via
  `refresh_unity`, read diagnostics, and record the result honestly.
- **`reviewer.md`**: added "Check Unity recompilation validation" bullet to the
  reviewer job list — flag missing recompilation validation as a review concern
  unless `validation.md` documents why it could not be run.
- **`manager.md`**: added a Unity-task Validation guidance block prompting
  managers to include the recompile step in `task.md`'s Validation section when
  the task modifies Unity code, scenes, or prefabs.
- **`profiles/unity/README.md`**: added "Required validation" section pointing
  to the `unity-guardrails.md` recompilation steps.

`AGENTS.md`, `CLAUDE.md`, `templates/task.md`, and `config.yaml` are unchanged.
The task template is generic and should not carry Unity-specific wording; the
profile README and guardrails cover the discovery path.

## Changed files

- `.ai-workflow/skills/unity-guardrails.md`
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/reviewer.md`
- `.ai-workflow/skills/manager.md`
- `.ai-workflow/profiles/unity/README.md`

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `git diff --name-only main...HEAD` — only skill files, profile README, and
  task folder; no Unity serialized files
- Manual review: no `.unity`, `.prefab`, `.asset`, `.meta`, package, or project
  settings files modified

## Assumptions

- The recompilation requirement applies only when Unity MCP or equivalent editor
  automation is accessible; the `not run` path with a concrete reason is the
  correct fallback, not a blocking failure.
- `templates/task.md` is not updated because it is a generic template used
  across all project profiles. The manager guidance in `manager.md` and the
  profile README provide the Unity-specific discovery path.

## Known risks

- Low. Documentation-only change. The main failure mode is an executor
  forgetting to read `unity-guardrails.md`; the profile README now surfaces the
  requirement directly.
