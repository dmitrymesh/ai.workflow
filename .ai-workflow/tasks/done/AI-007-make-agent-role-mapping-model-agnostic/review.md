# Review: AI-007

## Decision

approve

## Blocking issues

- None

## Non-blocking issues

- The task was implemented directly in the main checkout with `metadata.yaml.branch: null`. This was already discussed as a workflow/process issue; the role skill instructions were tightened separately by the reviewer at the user's request and are not part of the executor's report.
- `.ai-workflow/skills/manager.md` and `.ai-workflow/skills/executor.md` are present in the current working tree diff due to the separate reviewer-requested instruction update. They are in the task's allowed scope, but they were not reported by the executor and should be treated as separate human/reviewer edits when preparing the final change set.

## Scope check

Executor-changed files are within the task scope. No forbidden files were changed. The generated board reflects the task status. The extra skill-file edits are separately requested protocol instruction updates, not hidden executor scope.

## Acceptance criteria check

Satisfied. General docs now describe role assignments as config-driven, universal and adapter-specific entrypoints are separated, `AGENTS.md` and `CLAUDE.md` are framed as adapters, Claude command files remain usable as adapter commands, and the new `roles` CLI command has help output and prints the configured mapping. The previous install-plan merge snippet issue is fixed in `_install.py`.

## Test quality

Executor reported the required CLI checks plus an install-plan snippet check. Reviewer reran `roles`, `roles --help`, `validate`, `board`, `list`, `show AI-007`, and `install-plan` against a temporary target with existing `AGENTS.md` and `CLAUDE.md`; all passed.

## Unity-specific risks

Not applicable.

## Required fixes

- None
