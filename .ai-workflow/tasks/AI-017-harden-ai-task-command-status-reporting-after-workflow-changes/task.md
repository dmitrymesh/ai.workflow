# AI-017: Harden ai_task command status reporting after workflow changes

## Goal

Make the `ai_task.py` command surface report task status consistently after the
flat task layout, branch discovery, and review-cascade workflow changes.

This task should be used as a real workflow dogfood task: execute it through the
normal task lifecycle, and use the result to validate whether the current
manager -> human approval -> executor -> reviewer -> human integration flow is
usable without ad hoc fixes.

## Context

Recent workflow tasks changed the protocol substantially:

- AI-009/AI-010 simplified task status management around stable task folders.
- AI-012 through AI-015 defined and documented branch-first workflow behavior.
- AI-016 added review-time relationship cascades.

During manager review on 2026-05-08, `list` correctly grouped tasks by
`metadata.yaml.status`, but `show AI-016` printed `status: tasks` because
`show_task` reads `task_dir.parent.name`. In the flat layout, the parent folder
is `.ai-workflow/tasks`, so this is no longer a valid status source.

This is a small but important command-trust issue: if agents and humans cannot
trust basic command output, the workflow is not yet ready as the default path
for real Unity project work.

## Scope

Allowed changes:

- Fix `show` and any closely related command output that still derives task
  status from folder names in the flat layout instead of `metadata.yaml.status`.
- Review `list`, `show`, `path`, `claim`, `submit`, `review`,
  `human-request-changes`, `list-branches`, and `show-branch` for status
  source-of-truth inconsistencies introduced by the recent workflow changes.
- Add focused regression coverage or smoke tests for the command outputs touched
  by this task.
- Make small script refactors only when they reduce duplicated status lookup or
  make the fixed behavior easier to test.
- Update protocol docs or role instructions only if a command's documented
  behavior is wrong after the fix.

Forbidden changes:

- Do not redesign the lifecycle statuses or transition graph.
- Do not switch `workflow.mode`; this repository is already using branch-first
  mode for this task.
- Do not add hosted service integration, dashboards, databases, or non-stdlib
  Python dependencies.
- Do not broaden this task into a full CLI rewrite.
- Do not modify Unity scene, prefab, asset, meta, package, or project settings
  files.
- Do not edit generated `.ai-workflow/board.md` as a source file.

## Requirements

- `show <TASK-ID>` must print the status from `metadata.yaml.status` for flat
  task folders.
- Legacy status-directory tasks, if still supported by lookup helpers, must
  continue to display a sensible status.
- Commands that mutate status must continue to write `metadata.yaml.status` and
  refresh `updated_at`.
- Commands that only display status must not mutate task files.
- If a helper is added for status lookup, it must preserve current transition
  validation behavior.
- The executor report must include a short dogfood note: what workflow steps
  were actually used for this task, and any friction observed.
- The reviewer must check both the code diff and the workflow artifacts
  (`report.md`, `validation.md`, `review.md`, `decision.yaml`) before approval.

## Acceptance criteria

- `python .ai-workflow/scripts/ai_task.py show AI-016` prints
  `status:     done`, not `status:     tasks`.
- `python .ai-workflow/scripts/ai_task.py show AI-011` prints
  `status:     done`, not `status:     tasks`.
- `python .ai-workflow/scripts/ai_task.py list` continues to group all current
  tasks under the same statuses as their `metadata.yaml` files.
- Existing cascade tests still pass.
- `python .ai-workflow/scripts/ai_task.py validate` passes.
- The task's `validation.md` records exact commands and results, with `not run`
  for anything skipped.
- The task's `report.md` includes the required dogfood note about lifecycle
  friction.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `python -m unittest test_cascade -v` from `.ai-workflow/scripts`
- Focused command smoke checks for `show AI-016`, `show AI-011`, and `list`
- Diff review confirming no forbidden files changed

## Notes

Related context:

- AI-009: simplified task status management.
- AI-010: updated root README for flat task workflow.
- AI-012 to AI-015: branch-first workflow contract, discovery, docs, and task
  chain rules.
- AI-016: review-time relationship cascade behavior.

This task is intentionally narrow. If execution uncovers broader architectural
problems in `scripts/`, create follow-up tasks instead of expanding this one.
