# AI-016: Cascade relationship updates when review completes a task

## Goal

Make the review approval flow keep task relationship metadata consistent when a
task reaches `done`.

When a reviewer approves a task:

- tasks that were blocked by the completed task must be unblocked;
- parent tasks must automatically move to `done` when all of their children are
  `done`;
- parent completion must cascade upward through ancestors when applicable.

## Context

AI-001 added task relationships in `metadata.yaml`: `parent`, `children`,
`blocks`, `blocked_by`, and `related`. The CLI validates reciprocal
relationships, but the current review approval path appears to only mark the
reviewed task `done`.

That leaves two workflow gaps:

- downstream tasks can remain blocked by a task that is already complete;
- umbrella/parent tasks can remain open even after all child work is complete.

The desired behavior is generic protocol behavior, not a special case for one
task. If task `A` completes, any task blocked by `A` should stop listing `A` in
`blocked_by`. If task `A` has a parent, and every child of that parent is now
`done`, the parent should also become `done`. If that parent has its own parent
whose children are now all `done`, the cascade should continue upward.

## Scope

Allowed changes:

- Update `.ai-workflow/scripts/ai_task.py` review approval logic for the
  `ready_for_review -> done` transition.
- Add helper logic for completion cascades if it keeps the review flow readable.
- Update affected task metadata in the same operation as the approval.
- Preserve reciprocal relationship consistency for `blocks` and `blocked_by`.
- Add focused tests or smoke validation for blocked-task unblocking and parent
  completion cascades.
- Update protocol docs or role instructions only where needed to describe the
  new review completion behavior.

Forbidden changes:

- Do not require a new epic/container marker before closing parent tasks.
- Do not move tasks from `draft` to `ready`; human approval remains required.
- Do not auto-complete a parent while any of its children is not `done`.
- Do not mark unrelated tasks `done`.
- Do not weaken relationship validation added by AI-001.
- Do not introduce non-stdlib Python dependencies unless already required by
  this project.
- Do not edit generated `.ai-workflow/board.md` as a source file.

## Requirements

- Completing a task through reviewer approval must remove the completed task id
  from every directly blocked task's `blocked_by` list.
- The completed task's `blocks` list must be cleared or normalized so
  `blocks` and `blocked_by` remain reciprocal.
- If the completed task has a parent, the CLI must check all of that parent's
  children after the child is marked `done`.
- A parent must automatically move to `done` when every child listed in
  `parent.children` has `status: done`.
- A parent must remain in its current status when at least one child is not
  `done`.
- Parent auto-completion must be recursive across ancestor chains.
- Cascades must be idempotent: rerunning against an already-consistent state
  must not duplicate list entries or corrupt metadata.
- The cascade must update `updated_at` for every task whose metadata changes.
- `validate` must pass after a successful cascade.
- Error messages must identify affected task ids when a cascade cannot be
  completed.

## Acceptance criteria

- Approving task `A` removes `A` from `blocked_by` for every task that was
  blocked by `A`.
- After approval, task `A.blocks` no longer contains tasks that do not list `A`
  in `blocked_by`.
- If approving child `C` makes all children of parent `P` `done`, then `P`
  becomes `done` automatically.
- If `P` becoming `done` makes all children of grandparent `G` `done`, then
  `G` also becomes `done` automatically.
- If parent `P` still has any child that is not `done`, `P` is not moved to
  `done`.
- The new behavior is covered by focused tests or documented smoke validation
  for:
  - one blocked task becoming unblocked;
  - one parent closing when its final child closes;
  - one ancestor cascade across at least two parent levels;
  - one parent remaining open because another child is not `done`.

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
  auto-completion, but this task must implement the generic protocol behavior
  rather than special-casing AI-011.
