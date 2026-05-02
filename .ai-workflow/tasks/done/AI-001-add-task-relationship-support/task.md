# AI-001: Add task relationship support

## Goal

Add first-class task relationships to the Portable AI Task Protocol so tasks can express:

- parent/child decomposition
- blocking dependencies
- tasks blocked by other tasks
- loose related-task links

Managers must also be instructed to split broad requests into smaller tasks when useful and to set these relationship fields when creating related tasks.

## Context

The current workflow treats every task as independent. Status is folder-based and `metadata.yaml` is the machine-readable task record. The CLI in `.ai-workflow/scripts/ai_task.py` creates tasks from templates, lists tasks, generates `board.md`, and validates basic consistency.

This task should add a simple, file-based relationship model that remains portable and git-friendly. Do not introduce a database, server, external tracker integration, or automatic task orchestration.

## Scope

Allowed changes:

- `.ai-workflow/templates/metadata.yaml`
- `.ai-workflow/templates/task.md`
- `.ai-workflow/scripts/ai_task.py`
- `.ai-workflow/skills/manager.md`
- `.ai-workflow/skills/reviewer.md` if review guidance needs relationship checks
- `.ai-workflow/README.md`
- root `README.md`
- existing generated board output, if the board format changes

Forbidden changes:

- Do not add a database, backend server, or non-stdlib Python dependency.
- Do not change the status lifecycle except where relationship display or validation requires awareness of existing statuses.
- Do not implement automatic execution, automatic moving of blocked tasks, or infinite agent loops.
- Do not mark any task as `done`.

## Requirements

- Define relationship fields in task metadata:
  - `parent`: single task id or null
  - `children`: list of task ids
  - `blocks`: list of task ids this task blocks
  - `blocked_by`: list of task ids blocking this task
  - `related`: list of task ids with non-blocking context relationship
- Update task creation so new tasks include empty relationship fields by default.
- Add CLI support for setting and inspecting relationships. The exact interface is up to the implementer, but it must be documented and must not require manual YAML editing for common operations.
- Validate that relationship references point to existing task ids.
- Validate reciprocal blocking links where the protocol requires reciprocity:
  - if `AI-001.blocks` contains `AI-002`, then `AI-002.blocked_by` should contain `AI-001`
  - if `AI-002.blocked_by` contains `AI-001`, then `AI-001.blocks` should contain `AI-002`
- Validate parent/child consistency:
  - if a task has `parent: AI-001`, then `AI-001.children` should contain that task id
  - if `AI-001.children` contains `AI-002`, then `AI-002.parent` should be `AI-001`
- Update board/list output to make relationships visible enough for a manager or executor to notice blocked tasks.
- Update manager instructions so broad user requests may be split into multiple tasks with parent/child and blocking links set during task creation.
- Document the relationship model and example commands.

## Acceptance criteria

- Creating a new task produces `metadata.yaml` with `parent`, `children`, `blocks`, `blocked_by`, and `related` fields.
- There is a documented CLI path to add/remove/show relationships without hand-editing YAML.
- `validate` fails with a clear message when a relationship references a missing task id.
- `validate` fails with a clear message when blocking or parent/child reciprocal fields are inconsistent.
- `board` or `list` output shows enough relationship information to identify blocked tasks and parent tasks.
- Manager skill explains when to split a broad request and how to link the resulting tasks.
- README files describe the relationship fields and include at least one parent/child example and one blocking example.
- Existing commands still work:
  - `create`
  - `move`
  - `list`
  - `board`
  - `validate`
  - `path`

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Manual smoke test for relationship commands added by this task.
- Manual smoke test for `board` and `list` after adding sample relationships.
- Forbidden file check: confirm no forbidden generic files such as `.env` were changed.

## Notes

- Keep the relationship model intentionally small and explicit.
- If task splitting creates several tasks in a future manager workflow, the manager should create the parent task first, then children, then blocking links.
