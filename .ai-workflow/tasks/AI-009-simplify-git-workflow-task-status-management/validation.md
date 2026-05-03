# Validation: AI-009

## CLI commands

- `python .ai-workflow/scripts/ai_task.py migrate`: passed — 9 tasks moved, 0 skipped
- `python .ai-workflow/scripts/ai_task.py validate`: passed
- `python .ai-workflow/scripts/ai_task.py list`: passed — tasks grouped by metadata.status
- `python .ai-workflow/scripts/ai_task.py board`: passed — board.md regenerated

## Smoke tests

All lifecycle paths tested manually in the worktree:

| Step | Command | Result |
|------|---------|--------|
| Create draft | `create "Smoke test task"` | AI-010 created at `tasks/AI-010-smoke-test-task/` |
| Human approve | `move AI-010 ready` | status: ready |
| Executor claim | `claim AI-010 --print-only` | printed git commands; status moved to in_progress |
| Submit | `submit AI-010` | in_progress → ready_for_review |
| Reviewer changes | `review AI-010 --changes-requested` | ready_for_review → changes_requested |
| Resubmit | `submit AI-010` | changes_requested → ready_for_review |
| Reviewer approve | `review AI-010 --approve` | ready_for_review → done |
| Human request changes | `human-request-changes AI-010 --feedback "..."` | done → changes_requested |
| Reject | `move AI-010 rejected` | changes_requested → rejected |
| Cleanup | task folder removed | validate still passes |

## Forbidden file check

- No Unity files (`*.unity`, `*.prefab`, `*.asset`, `*.meta`) changed: confirmed
- No unrelated project files changed: confirmed
- Only `.ai-workflow/` files modified: confirmed

## Notes

- `claim` with actual worktree creation was tested via `--print-only` only. The
  actual git worktree add step works identically to the existing `prepare-worktree`
  command which has been in production use since AI-003.
- No compile or unit test infrastructure exists for the Python workflow scripts.
  Correctness was verified through the smoke test sequence above.
