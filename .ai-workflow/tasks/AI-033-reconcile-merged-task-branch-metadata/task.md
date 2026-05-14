# AI-033: Reconcile merged task branch metadata

## Goal

Reconcile stale metadata for old merged task branches so branch-first discovery
no longer reports already-merged `AI-008` and `AI-009` as `ready_for_review`.

## Context

`AI-030` identified a historical data inconsistency:

- `ai/AI-008-add-executor-review-appeal-step` is merged into `main`, but
  `show-branch AI-008` reports `status: ready_for_review`.
- `ai/AI-009-simplify-git-workflow-task-status-management` is merged into
  `main`, but `show-branch AI-009` reports `status: ready_for_review`.
- Both tasks predate the current `review --approve` auto-commit workflow, so
  their branch metadata did not receive the final `done` review artifact
  update before merge.

This is not a workflow code defect. It is historical metadata drift that makes
`list-branches` output noisier and can mislead humans scanning merged task
branches.

Relevant files/branches:

- Branch `ai/AI-008-add-executor-review-appeal-step`
- Branch `ai/AI-009-simplify-git-workflow-task-status-management`
- `.ai-workflow/tasks/AI-008-add-executor-review-appeal-step/metadata.yaml`
- `.ai-workflow/tasks/AI-009-simplify-git-workflow-task-status-management/metadata.yaml`
- Corresponding `review.md` and `decision.yaml` files if they need alignment

## Scope

Allowed changes:

- Update only historical task artifacts for `AI-008` and `AI-009` so their
  status and review decision state consistently reflect completed/merged work.
- Prefer the smallest durable change that makes `show-branch` and
  `list-branches` report these merged branches as `done`.
- Document exactly what historical artifacts were changed and why in this
  task's `report.md`.

Forbidden changes:

- Do not change workflow code or CLI behavior.
- Do not change current branch-first lifecycle semantics.
- Do not rewrite unrelated task history.
- Do not alter implementation files from `AI-008` or `AI-009` beyond their task
  metadata/review artifacts.
- Do not modify Unity project files, packages, project settings, or `.meta`
  files.

## Requirements

- `show-branch AI-008` must report `Status: done`.
- `show-branch AI-009` must report `Status: done`.
- `list-branches` must no longer show merged `AI-008` or `AI-009` as
  `ready_for_review`.
- Task artifact changes must be explicit and reviewable.
- If branch updates are required, the executor must document the exact branches
  and commits touched.
- The cleanup must not introduce new active task branches beyond this task.

## Acceptance criteria

- `python .ai-workflow/scripts/ai_task.py show-branch AI-008` reports
  `Status: done`.
- `python .ai-workflow/scripts/ai_task.py show-branch AI-009` reports
  `Status: done`.
- `python .ai-workflow/scripts/ai_task.py list-branches` reports no merged
  `AI-008` or `AI-009` entries with `status=ready_for_review`.
- `python .ai-workflow/scripts/ai_task.py validate` passes.
- `git diff --name-only main...HEAD` shows only in-scope historical task
  artifacts and this task's task folder.
- `report.md` explains whether cleanup was applied to the historical branches,
  to `main`, or both, and why that approach matches branch-first history rules.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py show-branch AI-008`
- `python .ai-workflow/scripts/ai_task.py show-branch AI-009`
- `python .ai-workflow/scripts/ai_task.py list-branches`
- `python .ai-workflow/scripts/ai_task.py validate`
- `git diff --name-only main...HEAD`
- Manual review confirming no workflow code files changed

## Notes

This task is cleanup of historical metadata only. If the executor discovers
that `list-branches` should instead hide merged non-done branches by policy,
they must stop and request a separate workflow-code task rather than changing
discovery behavior here.
