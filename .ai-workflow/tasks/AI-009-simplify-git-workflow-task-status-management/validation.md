# Validation: AI-009

## CLI commands

- `python .ai-workflow/scripts/ai_task.py migrate`: passed — 9 tasks moved, 0 skipped
- `python .ai-workflow/scripts/ai_task.py validate`: passed
- `python .ai-workflow/scripts/ai_task.py list`: passed — tasks grouped by metadata.status
- `python .ai-workflow/scripts/ai_task.py board`: passed — board.md regenerated

## Smoke tests (original round)

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

## Smoke tests (fix round 2)

| Test | Command | Result |
|------|---------|--------|
| validate passes on good tasks | `validate` | passed |
| folder/id mismatch detected | created `AI-999-wrong-name/metadata.yaml` with `id: AI-001` | `Folder/id mismatch: folder 'AI-999-wrong-name' does not start with id 'AI-001'` |
| duplicate id also detected | same test | duplicate id error reported alongside mismatch |
| board.md untracked | `git status --short .ai-workflow/board.md` after `git rm --cached` | `D  .ai-workflow/board.md` (staged deletion) |
| board regeneration works | `python ai_task.py board` | file regenerated locally; not tracked |
| validate after cleanup | `validate` | passed |

## Smoke tests (fix round 1)

| Test | Command | Result |
|------|---------|--------|
| history after migration | `history` | 7 done tasks listed from flat layout |
| history --show | `history --show AI-001` | report.md printed with encoding fallback |
| blocked claim rejection | `claim AI-011` (AI-011 blocked-by AI-010) | `Task AI-011 is blocked by: AI-010. Resolve all blockers before claiming.` |
| claim worktree success | `claim AI-010` | worktree created, metadata updated to in_progress |
| atomic failure | branch exists, dir removed, `claim AI-010` | `Worktree creation failed. Task has NOT been claimed.` — metadata unchanged |
| validate after cleanup | `validate` | passed |

## Forbidden file check

- No Unity files (`*.unity`, `*.prefab`, `*.asset`, `*.meta`) changed: confirmed
- No unrelated project files changed: confirmed
- Only `.ai-workflow/` files modified: confirmed

## Notes

- `claim` with actual worktree creation was fully exercised in the fix round.
- The Windows cp1252 encoding error for `history --show` was a pre-existing issue
  revealed by the fix (previously hidden because `tasks/done/` was empty).
- No compile or unit test infrastructure exists for the Python workflow scripts.
  Correctness was verified through the smoke test sequences above.
