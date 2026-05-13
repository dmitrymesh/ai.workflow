# Execution Report: AI-019

## Summary

Fixed `claim` so it works correctly in branch-first mode. Two root causes were addressed:

1. **`find_task` failure**: in branch-first mode, task folders live on task branches, not in the main checkout. `claim` now falls back to scanning local task branches via `_find_task_on_branch` when `find_task` raises (task not found in main).

2. **`-b` flag on existing branch**: `_create_worktree` always ran `git worktree add -b`, which fails when the branch already exists. `claim` now calls `_branch_exists_locally` and uses `_add_existing_worktree` (no `-b`) when the branch already exists, or `_create_worktree` (with `-b`) when it does not.

Additional improvements:
- Replaced the `meta.get("branch")` guard (which was designed for main-first double-claim detection) with a `_worktree_exists_for_branch` check that is correct in both modes.
- `--print-only` prints the correct git command (`worktree add <path> <branch>` vs `worktree add -b <branch> <path>`) based on whether the branch already exists.
- In branch-first mode, metadata is updated in the worktree (not in the main checkout) and the commit command is printed for the executor.

## Changed files

- `.ai-workflow/scripts/_worktree.py` — added `_branch_exists_locally`, `_worktree_exists_for_branch`, `_find_task_on_branch`, `_add_existing_worktree`; rewrote `claim_task` to handle both modes; updated `_print_worktree_commands` with `branch_exists` flag.
- `.ai-workflow/scripts/test_claim.py` — new test file: 21 tests covering helpers, branch-first claim, main-first claim, guards, and `--print-only`.
- `.ai-workflow/skills/executor.md` — updated Branch-first section to use `claim` instead of manual worktree add.

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python -m unittest test_claim` — 21/21 passed
- Smoke: `claim AI-025 --print-only` — correct output, no `-b` flag, shows `worktree add <path> <branch>`
- Smoke: `claim AI-020 --print-only` — correctly rejected (worktree already exists)
- No forbidden files modified

## Assumptions

- `_find_task_on_branch` scans local branches only. Remote-only branches are out of scope (they would need `git fetch` first; that is a network operation outside the CLI's current contract).
- Metadata commit in branch-first mode is left to the executor (the command prints the commit command). This matches the pattern used in `update-from-main` and the documented executor workflow.

## Known risks

- Low-medium. The fallback to branch scanning adds a small startup cost when `find_task` fails (scans all local `ai/` branches). This is acceptable for interactive use.
- If a task branch slug and the task folder directory name diverge (can happen with manual edits), the worktree metadata path derivation (`branch.split("/")[-1]`) may be wrong. This is an edge case; the normal convention matches.
