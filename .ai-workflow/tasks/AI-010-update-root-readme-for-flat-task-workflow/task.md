# AI-010: Update root README for flat task workflow

## Goal

Review and update the repository root `README.md` so it accurately documents the
current flat task-folder workflow introduced by AI-009.

## Context

AI-009 changed task storage from status directories to stable task folders under
`.ai-workflow/tasks/<task-id>-<slug>/`, with `metadata.yaml.status` as the
source of truth. It also removed `ready_for_human`, added executor self-service
`claim`, and added `submit`, `review`, `human-request-changes`, and `migrate`
commands.

The root `README.md` still contains legacy documentation, including:

- `tasks/draft/`, `tasks/ready/`, `tasks/done/` status-directory examples.
- Status lifecycle references to `ready_for_human`.
- Executor/reviewer instructions that read from status-directory paths.
- File reference examples using `.ai-workflow/tasks/<status>/<task>/...`.

## Scope

Allowed changes:

- Update the root `README.md`.
- Keep the documentation aligned with `.ai-workflow/README.md`,
  `.ai-workflow/config.yaml`, and AI-009's completed workflow.
- Remove or rewrite obsolete status-directory and `ready_for_human` references.
- Document the current flat folder model, metadata-driven status lifecycle,
  `claim`, `submit`, `review`, `human-request-changes`, and `migrate` where
  relevant.
- Update command examples and role workflow sections so they match the current
  CLI behavior.

Forbidden changes:

- Do not modify protocol implementation code.
- Do not modify task lifecycle/status config except if a documentation mismatch
  reveals a separate issue; in that case, report it instead of fixing it here.
- Do not modify existing task folders except this task's `report.md` and
  `validation.md` during execution.
- Do not edit generated `.ai-workflow/board.md`.
- Do not expand this into a full documentation redesign or new website.

## Requirements

- The root README must describe tasks as stable folders under
  `.ai-workflow/tasks/<task-id>-<slug>/`.
- The README must state that task status is stored in `metadata.yaml.status`,
  not determined by parent directory.
- The documented statuses and transitions must match `.ai-workflow/config.yaml`.
- The recommended workflow must describe:
  - manager creates a complete task contract and leaves it in `draft`;
  - human moves `draft -> ready`;
  - executor runs `claim <TASK-ID>` from the main checkout, works in the task
    worktree, writes `report.md` and `validation.md`, then runs `submit`;
  - reviewer uses `review --approve` or `review --changes-requested`;
  - approved tasks move to `done` under the current workflow.
- The README must mention that `board.md` is generated and untracked/local.
- The README must retain the safe install/upgrade guidance and ownership model,
  updating only the parts that conflict with the current workflow.
- The update must preserve the README's purpose as user-facing project
  documentation, not duplicate every detail from `.ai-workflow/README.md`.

## Acceptance criteria

- Searching `README.md` for `.ai-workflow/tasks/draft`,
  `.ai-workflow/tasks/ready`, `.ai-workflow/tasks/in_progress`,
  `.ai-workflow/tasks/ready_for_review`, `.ai-workflow/tasks/changes_requested`,
  `.ai-workflow/tasks/done`, and `ready_for_human` finds no legacy workflow
  documentation.
- `README.md` includes a current folder example using
  `.ai-workflow/tasks/<task-id>-<slug>/`.
- `README.md` includes current command examples for `claim`, `submit`, and
  `review`.
- `README.md` remains consistent with `.ai-workflow/config.yaml` statuses and
  transitions.
- No files outside the allowed scope are changed.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Search `README.md` for obsolete status-directory examples and
  `ready_for_human`; expected result: no legacy workflow documentation remains.
- Review `git diff -- README.md` to confirm the update is documentation-only
  and in scope.

## Notes

- Related context: AI-009 completed the workflow simplification this task should
  document.
