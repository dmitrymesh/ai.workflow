# Review: AI-010

## Decision

changes_requested

## Blocking issues

1. `README.md` documents a lifecycle that does not match `.ai-workflow/config.yaml`.
   The task requires the documented statuses and transitions to match config. In `README.md:239-245`, the README says `changes_requested -> ready_for_review` but the executor subsection says `changes_requested -> in_progress` at `README.md:253`, which is not an allowed transition. The same lifecycle block also says `any status -> rejected`, but config does not allow `done -> rejected` or `rejected -> rejected`, and it omits `done -> changes_requested`, which config explicitly allows.

2. `README.md` does not document `human-request-changes` or `migrate`.
   The task scope explicitly calls out documenting the current flat folder model plus `claim`, `submit`, `review`, `human-request-changes`, and `migrate` where relevant. The update adds `claim`, `submit`, and `review`, but `Select-String` found no `human-request-changes` or `migrate` command references in `README.md`. That leaves two AI-009 workflow commands absent from the root user-facing docs this task was created to refresh.

## Non-blocking issues

- The task branch/worktree has `task.md`, `metadata.yaml`, `review.md`, and `decision.yaml` as untracked files while `report.md` and `validation.md` are committed/tracked additions. Before resubmission, make sure the complete AI-010 task folder state that should travel with the branch is tracked consistently.

## Scope check

Mostly in scope. The code diff is documentation-only and limited to `README.md`, with this task's report/validation artifacts. No protocol implementation files or forbidden files were changed.

## Acceptance criteria check

Not met. Legacy status-directory searches and `ready_for_human` search are clean, and `claim`/`submit`/`review` examples are present. However, the documented lifecycle does not match `.ai-workflow/config.yaml`, which is an explicit acceptance criterion.

## Test quality

Validation was reasonable for a documentation-only task: `python .ai-workflow/scripts/ai_task.py validate` passed, and the legacy term search returned no matches. The validation missed the config transition mismatch and absent command documentation noted above.

## Unity-specific risks

None.

## Required fixes

1. Correct the lifecycle section so every documented transition matches `.ai-workflow/config.yaml`, including `done -> changes_requested`, and remove or qualify any unsupported broad transition claims.
2. Remove the unsupported `changes_requested -> in_progress` executor guidance or rewrite it to match the actual `changes_requested -> ready_for_review` transition.
3. Add concise, relevant README documentation/examples for `human-request-changes` and `migrate`.
4. Ensure the complete task artifact set is tracked consistently before resubmission.
