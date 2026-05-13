# Execution Report: AI-022

## Summary

Clarified that `list-branches` is the correct command for discovering active tasks in branch-first mode, and that `list` only shows tasks present in the current checkout.

Two changes were made:

1. **`_board.py`**: Added a warning printed to `stderr` when `list` is invoked and `workflow.mode` is `branch_first`. The warning names `list-branches` as the correct alternative. Output to `stdout` is unchanged, so scripts parsing the task list are not broken.

2. **`README.md`**: Reordered the "Basic commands" section to show `list-branches` first (now labelled as the branch-first backlog view) and `list` second (labelled as checkout-only / main-first history). The `list` entry now includes a **not** a full backlog view note for branch-first users.

No changes were made to `list-branches` behaviour, `executor.md`, or `AGENTS.md` — those files already described the correct command surface.

## Changed files

- `.ai-workflow/scripts/_board.py` — add stderr warning in `list_tasks()` when `workflow.mode == "branch_first"`
- `README.md` — reorder and annotate `list` vs `list-branches` in Basic commands section

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- Manual smoke check: `list` now prints warning to stderr in branch_first mode; stdout task list unchanged
- Manual smoke check: `list-branches` output unchanged
- Docs reviewed: README Basic commands section and executor.md Discovering ready tasks section

## Assumptions

- `_parse_workflow_config` from `_discovery.py` is the correct helper for reading nested `workflow.mode`; `load_config()` in `_core.py` uses a flat YAML parser that cannot read nested keys.
- Importing `_parse_workflow_config` from `_discovery.py` into `_board.py` does not create a circular dependency (both depend only on `_core.py`).

## Known risks

- Low. Only docs and a stderr-only code path changed. No stdout format, status semantics, or command behaviour was altered.
