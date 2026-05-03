# Review: AI-009

## Decision

changes_requested

## Blocking issues

1. `validate` does not detect folder/id mismatches required by the task contract.
   The task explicitly requires validation to "detect mismatch between folder path and `metadata.yaml.id`" (`task.md`, requirements section). In `.ai-workflow/scripts/_validate.py:31`, validation reads `metadata.yaml` and checks for duplicate IDs, but there is no check that a stable task folder name begins with or otherwise matches the metadata id. A folder like `tasks/AI-999-wrong-name/metadata.yaml` with `id: AI-001` would be accepted unless it collides with another id. This leaves a migration/status ambiguity the task specifically asked to catch.

2. `board.md` remains tracked but `validate` does not detect stale generated board state.
   The contract requires the implementation to define whether `.ai-workflow/board.md` remains tracked, becomes ignored, or is validated for freshness, and then specifically requires detecting stale/generated board state if it remains tracked. `.ai-workflow/board.md` is still tracked, and `.ai-workflow/scripts/_board.py:67` writes it as a generated file, but `.ai-workflow/scripts/_validate.py` has no freshness check. A user can merge stale board output while `validate` still passes, which is one of the sync problems this task is meant to remove.

## Non-blocking issues

- Previous blocker resolved: `history` now lists flat `status: done` tasks and `history --show AI-001` prints the report.
- Previous blocker resolved: `claim` now aborts without mutating metadata when worktree creation fails.
- Previous blocker resolved: `claim` now rejects tasks with `blocked_by` entries.

## Scope check

In scope. The diff is limited to `.ai-workflow/` protocol files and task artifacts. No Unity or unrelated project files were changed.

## Acceptance criteria check

Not met. Stable metadata status, list/board grouping, lifecycle commands, history discoverability, and claim safety are mostly present, but the required validation safeguards for folder/id mismatch and tracked board freshness are missing.

## Test quality

Validation commands reported as run, and I re-ran `validate`, `list`, `history`, and `history --show AI-001` successfully in the task worktree. The submitted validation still does not cover the required folder/id mismatch or stale board detection behavior.

## Unity-specific risks

None found.

## Required fixes

1. Add validation for stable task folder path vs `metadata.yaml.id` mismatches, with clear repair guidance.
2. Either stop tracking `.ai-workflow/board.md` as a generated cache or make `validate` detect stale tracked board output. Document the chosen behavior consistently.
3. Add focused validation/smoke coverage for both cases above.
