# Execution Report: AI-003

## Summary

Added a documented git worktree-based execution workflow. Every executor task
is now expected to run in a task-specific isolated worktree by default. The
implementation includes CLI support (`prepare-worktree`), updated role skill
documentation (manager/executor/reviewer), and a new worktree section in the
README.

Implementation was done directly in the main checkout because this task
defines the worktree workflow itself — bootstrapping the new protocol inside
itself would create circular dependency. The task notes explicitly allow this:
"This task should not actually move current work into a new worktree unless
that is explicitly required for validation."

**Changes from v1 (fixes from first changes_requested review):**

- Fixed metadata ordering bug: `metadata.yaml.branch` is now written to the
  main checkout task folder *before* the folder is copied into the worktree,
  ensuring the executor receives `metadata.yaml` with `branch` already set.
- Added end-to-end smoke test: created a temporary ready task (AI-004),
  ran `prepare-worktree` in both `--print-only` and full automatic modes,
  verified that the copied worktree task folder contains
  `metadata.yaml.branch = ai/AI-004-smoke-test-worktree`, then cleaned up
  the worktree, branch, and task.

**Changes from v2 (fixes from second changes_requested review):**

- Deleted the lingering `.ai-workflow/tasks/rejected/AI-004-smoke-test-worktree/`
  directory that the v1 smoke test left behind. The smoke test task was
  incorrectly left in `rejected` status instead of being fully removed from the
  workflow state. Regenerated `board.md` — `rejected` is now empty.

## Changed files

- `.ai-workflow/scripts/ai_task.py` — added `prepare-worktree` subcommand and
  `_print_worktree_commands` helper; added `import subprocess`; updated module
  docstring; **fixed metadata-before-copy ordering**
- `.ai-workflow/skills/executor.md` — added worktree execution section
  documenting why direct edits are unsafe, step-by-step executor workflow
  inside a worktree, and exceptional case documentation
- `.ai-workflow/skills/manager.md` — added branch/worktree naming conventions
  and post-approval `prepare-worktree` handoff documentation
- `.ai-workflow/skills/reviewer.md` — added worktree diff review section
  explaining how to get the task branch diff and what to verify
- `.ai-workflow/README.md` — added "Git worktree execution workflow" section
  covering rationale, visibility constraint, naming conventions,
  `prepare-worktree` command, executor/reviewer workflows, and cleanup

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python .ai-workflow/scripts/ai_task.py board` — passed
- `python .ai-workflow/scripts/ai_task.py list` — passed
- `python .ai-workflow/scripts/ai_task.py path AI-003` — passed
- `python .ai-workflow/scripts/ai_task.py prepare-worktree --help` — passed
- `python .ai-workflow/scripts/ai_task.py prepare-worktree AI-003 --print-only`
  — correctly rejected with "not in 'ready' status" (expected)
- **End-to-end smoke test** (AI-004 temp task):
  - `prepare-worktree AI-004 --print-only` — metadata.yaml.branch set: PASS
  - `prepare-worktree AI-004` (full auto) — worktree created, folder synced: PASS
  - Worktree `metadata.yaml.branch` verified in copied folder: PASS
  - Cleanup (worktree remove, branch delete, task rejected): PASS
- Forbidden file check: confirmed no `.env*`, package files, or out-of-scope
  files were changed

## Assumptions

- The task requires bootstrapping itself in the main checkout (documented above).
- `--print-only` also updates `metadata.yaml.branch` so the branch is recorded
  even when the operator runs git commands manually.
- Worktrees directory is a sibling to the repo root (`<repo-name>.worktrees/`).

## Known risks

- Path handling uses `pathlib.Path` throughout. On Windows, the printed
  `xcopy` command in `--print-only` mode uses Windows path format; on
  Unix/Mac, `cp -r` is used.
