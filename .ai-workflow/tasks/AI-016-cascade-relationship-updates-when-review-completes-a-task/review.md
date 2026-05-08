# Review: AI-016

## Decision

changes_requested

## Blocking issues

- `_unblock_dependent_tasks` and `_cascade_parent_done` silently ignore relationship references that make the cascade impossible instead of failing with an error that identifies the affected task ids. In `_unblock_dependent_tasks`, a missing blocked task at lines 115-117 is skipped and then the completed task's `blocks` list is cleared at line 123, which silently discards an unresolved relationship. In `_cascade_parent_done`, missing reviewed task, parent, or child references at lines 133-158 return an empty cascade with no message. This violates the explicit requirement: "Error messages must identify affected task ids when a cascade cannot be completed." Make these paths fail loudly with the relevant ids, and add focused coverage for at least one missing referenced task.

## Non-blocking issues

- The previous blocking issue about auto-completed parents not unblocking downstream tasks is fixed. `_cascade_parent_done` now calls `_unblock_dependent_tasks(parent_id, parent_meta)` before saving the parent, and `test_auto_completed_parent_unblocks_downstream` covers the regression.

## Scope check

In scope. The code changes are limited to `.ai-workflow/scripts/_tasks.py`, a focused test file, and task metadata/artifacts. No forbidden files were changed.

## Acceptance criteria check

Partially met.

- Direct approval unblocks downstream tasks: met.
- Direct approved task clears `blocks`: met.
- Final child approval closes parent: met.
- Ancestor cascade closes grandparent: met.
- Parent remains open when a sibling is not done: met.
- Generic completion cleanup for every task that reaches `done`: met for direct approvals and auto-completed parents.
- Error messages identify affected task ids when cascade cannot be completed: not met.

## Test quality

Good coverage for the direct blocker, parent cascade, ancestor cascade, idempotency, and auto-completed-parent downstream unblocking scenarios. Missing coverage for cascade failure/error paths involving unresolved relationship ids.

## Unity-specific risks

Not applicable. This is a Python CLI workflow task, not a Unity project change.

## Required fixes

- Replace silent `continue`/`return` paths for missing relationship targets with clear failures that include the task ids involved, for example completed id plus missing blocked task id, parent id, or child id.
- Add a regression test for a cascade that cannot complete because a referenced task id is missing, asserting the command fails and the error message names the affected ids.
