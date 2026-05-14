# Review: AI-035

## Decision

changes_requested

## Blocking issues

- `.ai-workflow/README.md` still contains user-facing future-work wording: "The human (or a future CLI command) merges the branch locally" in the `local_merge` integration section. This task explicitly requires removing obsolete future-work planning text from user-facing docs unless it represents a current roadmap in a dedicated section. This phrase is not needed for current usage and should be removed or rewritten as present-day guidance, e.g. "The human merges the branch locally." See `.ai-workflow/README.md` line 763.

## Non-blocking issues

- None

## Scope check

Pass. The branch changes only `README.md`, `.ai-workflow/README.md`, and this task's artifacts. No workflow code, config semantics, Unity files, or unrelated task history changed.

## Acceptance criteria check

Not met. The main stale searches pass for the required exact patterns, migration is now framed as legacy/upgrade-only, and the diff is in scope. However, a remaining lowercase "future CLI command" phrase leaves future-work planning in user-facing protocol docs.

## Test quality

Adequate. I reran `validate`, `--help`, `install-plan --help`, the required stale-guidance search, migration search, safety-rule search, future-wording search, and diff scope check.

## Unity-specific risks

Not applicable. No Unity files changed.

## Required fixes

- Remove or rewrite the remaining "future CLI command" wording in `.ai-workflow/README.md` so the integration section only describes current behavior.
