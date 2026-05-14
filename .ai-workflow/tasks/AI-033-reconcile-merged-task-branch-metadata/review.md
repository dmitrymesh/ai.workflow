# Review: AI-033

## Decision

changes_requested

## Blocking issues

- The reconciliation commits make `AI-008` and `AI-009` active unmerged branches again. `python .ai-workflow/scripts/ai_task.py list-branches` now lists both under `Active (unmerged)` with `status=done`, and `show-branch AI-008` / `show-branch AI-009` both report `Merged into main: no`. This violates the task requirement that "The cleanup must not introduce new active task branches beyond this task." It also leaves the historical cleanup outside the AI-033 branch being reviewed, so merging only AI-033 would not carry the actual reconciliation changes into history.

## Non-blocking issues

- None

## Scope check

The file types touched on the historical branches are in scope, but the branch topology is not: the implementation updated `ai/AI-008-*` and `ai/AI-009-*` directly and left those branches ahead of `main`.

## Acceptance criteria check

Partially passes. `show-branch AI-008` and `show-branch AI-009` report `Status: done`, and `validate` passes. The branch-list state does not satisfy the "no new active task branches beyond this task" requirement, because AI-008 and AI-009 now appear as active unmerged branches.

## Test quality

Adequate for metadata cleanup. Required commands were run, but their output exposes the blocking branch-state issue.

## Unity-specific risks

Not applicable. No Unity files changed.

## Required fixes

- Rework the reconciliation so AI-008 and AI-009 do not remain active unmerged branches after the cleanup. The final observable state should have no active unmerged branches beyond AI-033, while `show-branch AI-008` and `show-branch AI-009` still report `Status: done`.
- Ensure the actual reconciliation changes are reviewable and will be integrated durably, not only documented in AI-033's report.
