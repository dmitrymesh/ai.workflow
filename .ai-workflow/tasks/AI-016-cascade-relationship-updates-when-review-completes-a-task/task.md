# AI-016: Cascade relationship updates when review completes a task

## Goal

Update the task CLI review-completion flow so that marking a task `done`
cascades relationship metadata consistently:

- tasks blocked by the completed task are unblocked;
- a parent task is automatically completed when its last child is completed.

## Context

AI-001 added first-class task relationships (`parent`, `children`, `blocks`,
`blocked_by`, `related`) and reciprocal validation. The current review flow can
move a task to `done`, but it appears not to update tasks that were blocked by
the completed task. This can leave downstream tasks incorrectly blocked even
after their blocker is complete.

There is also a recurring manager workflow for parent tasks that organize child
tasks. When the final child of a parent reaches `done`, the parent should be
marked `done` automatically so umbrella/epic tasks do not remain open after all
of their work is complete.

## Scope

Allowed changes:

- Update `.ai-workflow/scripts/ai_task.py` review/status transition logic for
  the `ready_for_review -> done` path.
- When a task is marked `done`, remove that task id from every blocked task's
  `blocked_by` list and remove/normalize the completed task's `blocks` list so
  reciprocal metadata stays consistent.
- Add logic to detect whether the completed task's parent can be auto-completed
  after all of its children are `done`.
- Update validation, tests, or smoke coverage for the new cascade behavior.
- Update protocol documentation or role skill text only where needed to explain
  the new marker/rule and reviewer behavior.

Forbidden changes:

- Do not move tasks from `draft` to `ready`; human approval remains required.
- Do not mark unrelated tasks `done`.
- Do not weaken relationship reciprocity validation from AI-001.
- Do not introduce non-stdlib Python dependencies unless already required by
  the project.
- Do not edit generated `.ai-workflow/board.md` as a source file.

## Requirements

- Completing a task through the review approval path must update all directly
  affected relationship metadata in the same operation.
- If task `A.blocks` contains `B`, then completing `A` must remove `A` from
  `B.blocked_by`.
- After completing `A`, `A.blocks` must not continue to claim it blocks tasks
  that no longer list `A` in `blocked_by`.
- Parent auto-completion must run only after child completion cascades are
  applied.
- Parent auto-completion must require all children of the parent to have
  `status: done`.
- If a parent has any non-done child, it must remain in its current status.
- Parent auto-completion must be recursive: if completing a parent makes its
  own parent have all children `done`, the cascade should continue upward.
- Cascades must be idempotent: approving/reviewing an already-consistent state
  must not duplicate list entries or corrupt metadata.
- `validate` must pass after a successful cascade.
- Error messages must identify the affected task ids when cascade updates fail.

## Acceptance criteria

- A reviewer approval that marks a task `done` removes that task from all
  affected `blocked_by` lists.
- The completed task's `blocks` metadata is cleared or otherwise normalized so
  relationship reciprocity remains valid.
- A parent is automatically moved to `done` when its last child reaches `done`.
- A parent with at least one non-done child is not automatically moved to
  `done`.
- Parent completion can cascade through multiple ancestor levels when each
  ancestor's children are all `done`.
- The new behavior is covered by focused tests or documented smoke validation
  using at least:
  - one blocked task that becomes unblocked;
  - one parent whose last child completes;
  - one parent with a remaining non-done child that must remain open.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Run the focused CLI tests if present, or add/run an equivalent smoke test for
  review completion cascades.
- Run any existing protocol/CLI test suite if present.
- Record exact commands and results in `validation.md`; write `not run` for any
  unavailable validation.

## Notes

Related context:

- AI-001 added the relationship model and reciprocal validation.
- AI-011 is an active umbrella workflow task that would benefit from parent
  auto-completion, but this task should implement the generic protocol behavior
  rather than special-casing AI-011.
