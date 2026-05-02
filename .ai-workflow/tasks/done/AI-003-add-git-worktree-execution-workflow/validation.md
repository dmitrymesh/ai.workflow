# Validation: AI-003

## Local

- `python .ai-workflow/scripts/ai_task.py validate`: passed
- `python .ai-workflow/scripts/ai_task.py board`: passed
- `python .ai-workflow/scripts/ai_task.py list`: passed
- `python .ai-workflow/scripts/ai_task.py path AI-003`: passed
- `python .ai-workflow/scripts/ai_task.py prepare-worktree --help`: passed
- `python .ai-workflow/scripts/ai_task.py prepare-worktree AI-003 --print-only`:
  correctly returned exit code 1 with "not in 'ready' status" error (expected)

**End-to-end smoke test (AI-004 temp task):**

- `prepare-worktree AI-004 --print-only`: metadata.yaml.branch written to main
  checkout before copy step — verified via Python assert: **PASS**
- `prepare-worktree AI-004` (full automatic mode): git worktree created,
  task folder synced to worktree path — **PASS**
- Worktree task folder `metadata.yaml.branch` verified equal to
  `ai/AI-004-smoke-test-worktree` — **PASS** (this is the key fix from v1)
- Cleanup: `git worktree remove --force`, `git branch -D` — **PASS**
- AI-004 task folder removed from `rejected/`, board regenerated,
  `validate` passes with empty `rejected` — **PASS**

- Unit/EditMode tests: not applicable (no test framework)
- Integration/PlayMode tests: not applicable

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: none — confirmed no `.env*`, package files, or
  out-of-scope files modified
- Package changes: none

## Notes

The metadata-before-copy ordering fix was directly verified: the worktree
copy of `metadata.yaml` was read back and its `branch` field confirmed
non-null. This proves the executor will see `branch` set immediately after
`prepare-worktree` runs.
