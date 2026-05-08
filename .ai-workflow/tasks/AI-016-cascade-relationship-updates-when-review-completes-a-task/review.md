# Review: AI-016

## Decision

changes_requested

## Blocking issues

- Auto-completed parent tasks do not run the completion cleanup that the reviewed task runs. In `_cascade_parent_done`, a parent is marked `done` and saved, then the function recurses upward, but it never calls `_unblock_dependent_tasks` for that parent. As a result, if parent `P` blocks downstream task `D`, approving final child `C` can move `P` to `done` while `D.blocked_by` still contains `P` and `P.blocks` still contains `D`. This violates the task's generic requirement that when a task completes, directly blocked tasks are unblocked and the completed task's `blocks` list is cleared/normalized. Apply the same completion cleanup to every task that becomes `done` through the parent cascade, and add a focused regression test for an auto-completed parent with a downstream blocked task.

## Non-blocking issues

- None yet

## Scope check

In scope. The code changes are limited to `.ai-workflow/scripts/_tasks.py`, a focused test file, and task metadata/artifacts. No forbidden files were changed.

## Acceptance criteria check

Partially met.

- Direct approval unblocks downstream tasks: met.
- Direct approved task clears `blocks`: met.
- Final child approval closes parent: met.
- Ancestor cascade closes grandparent: met.
- Parent remains open when a sibling is not done: met.
- Generic completion cleanup for every task that reaches `done`: not met for auto-completed parents/ancestors.

## Test quality

Good coverage for the direct blocker and parent cascade scenarios listed in the task. Missing coverage for downstream unblocking when the task that reaches `done` is an auto-completed parent or ancestor.

## Unity-specific risks

Not applicable. This is a Python CLI workflow task, not a Unity project change.

## Required fixes

- Ensure every task marked `done` by `_cascade_parent_done` also unblocks its dependents and clears/normalizes its own `blocks` list.
- Add a regression test where approving final child `C` auto-completes parent `P`, and `P` blocks downstream task `D`; after approval, `D.blocked_by` must not contain `P` and `P.blocks` must be empty.
