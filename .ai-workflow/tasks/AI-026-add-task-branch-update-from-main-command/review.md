# Review: AI-026

## Decision

changes_requested

## Blocking Issues

1. `.ai-workflow/scripts/_update_from_main.py:219` defaults missing `workflow.mode` to `branch_first`. The protocol docs define the default as `main_first` (`.ai-workflow/README.md`, config keys table; `config.yaml` also comments "main_first" as current default). In a legacy project with no `workflow.mode`, `update-from-main` would run instead of clearly reporting unsupported `main_first` behavior. Change the fallback to `main_first` and add a test for an empty workflow config (`{}`) being rejected.

## Non-Blocking Issues

- The previous runtime crash in `--all` is fixed: `_read_task_meta_from_branch` is now called with `(branch, task_id)`.
- The active-status filtering now works in a live dry-run and reports inactive `done` branches separately.

## Scope Check

The changed files remain within the allowed CLI, documentation, tests, and task artifact scope. No forbidden file patterns were changed.

## Acceptance Criteria Check

- Single-task dry-run works.
- `--all` dry-run now runs successfully and filters inactive `done` branches.
- Dirty, already-current, merged, conflict, and inactive reporting are covered by tests or smoke output.
- The `main_first` guard works only when config explicitly says `main_first`; it still fails the default/no-mode compatibility case.
- `validate` passes.

## Test Quality

I ran `validate`, `python -m unittest test_update_from_main -v`, `update-from-main --all`, `update-from-main AI-022`, and `git diff --check`. Add the missing empty-config workflow mode test.

## Required Fixes

- Change the workflow mode fallback from `branch_first` to `main_first`.
- Add a unit test that `_parse_workflow_config()` returning `{}` causes `update-from-main` to exit with a clear unsupported-mode error.
- Re-run the unit tests and live dry-run smoke test.
