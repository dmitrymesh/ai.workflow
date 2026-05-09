# Review: AI-026

## Decision

changes_requested

## Blocking Issues

1. `.ai-workflow/scripts/_update_from_main.py:252` calls `_read_task_meta_from_branch(branch)` with one argument, but `.ai-workflow/scripts/_discovery.py:239` defines `_read_task_meta_from_branch(branch, task_id)`. The real `update-from-main --all` command now crashes before producing a summary:

   ```text
   TypeError: _read_task_meta_from_branch() missing 1 required positional argument: 'task_id'
   ```

   This breaks the `--all` acceptance criteria and was missed because the unit test mocks `_read_task_meta_from_branch` with a one-argument-compatible mock. Pass the extracted `tid` into the helper and add a test that asserts the helper is called with both `branch` and `task_id`.

2. `.ai-workflow/scripts/_update_from_main.py:218` still does not correctly enforce `workflow.mode`. `_parse_workflow_config()` returns the workflow block directly, e.g. `{"mode": "branch_first", "discovery": ...}`, but the code reads `cfg.get("workflow", {}).get("mode", "branch_first")`. That always falls back to `branch_first` for the real config shape, so `main_first` would not be rejected clearly as required. Use `cfg.get("mode", "main_first" or appropriate default)` consistently with `_discovery_cfg`, and update the tests to mock the real config shape (`{"mode": "main_first"}`), not `{"workflow": {"mode": ...}}`.

## Non-Blocking Issues

- The conflict behavior mismatch was addressed by updating the README wording to match the current implementation.

## Scope Check

The changed files remain within the allowed CLI, documentation, tests, and task artifact scope. No forbidden file patterns were changed.

## Acceptance Criteria Check

- Single-task path remains implemented.
- `--all` currently fails at runtime due to the helper signature mismatch.
- Dirty worktree, already-current, merged-branch, and conflict reporting behavior have tests.
- Active-status filtering was attempted but is not functional in the real command until the `task_id` argument is passed.
- `main_first` unsupported behavior was attempted but does not work against the real config parser shape.
- `validate` passes, but the live `update-from-main --all` smoke test fails.

## Test Quality

I ran `validate`, inspected the real `_parse_workflow_config()` output, and ran `update-from-main --all`. The new unit tests need to stop masking the real helper signature and real workflow config shape.

## Required Fixes

- Fix `_read_task_meta_from_branch` usage in `--all` by passing both `branch` and `task_id`.
- Correct the workflow mode check against the actual `_parse_workflow_config()` return shape.
- Update tests so they would fail for both regressions above.
- Re-run `python .ai-workflow/scripts/ai_task.py update-from-main --all` as a real smoke test and record the result.
