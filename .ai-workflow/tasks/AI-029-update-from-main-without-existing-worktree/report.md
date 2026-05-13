# Execution Report: AI-029

## Summary

Extended `update-from-main` so that active task branches without a local worktree can be updated from `main` safely.

**Single-task mode** now always handles no-worktree branches: a temporary worktree is created at the standard path (`<repo>.worktrees/<branch-slug>`), `git merge main` is run inside it, and on success the temporary worktree is removed automatically. On conflict, the worktree is left in place with the path and recovery instructions printed.

**`--all` mode** keeps its current worktree-only default. A new `--include-no-worktree` flag enables the same temporary-worktree path for branches without local worktrees in bulk mode.

**Dry-run** reports a distinct outcome (`dry_run_no_worktree`) that says a temporary worktree would be created and names the path.

## Changed files

- `.ai-workflow/scripts/_update_from_main.py` — added `_worktree_path_for_branch`, `_worktree_add`, `_worktree_remove` helpers; extended `_process_branch` with `allow_no_worktree` parameter and no-worktree processing path; added `dry_run_no_worktree` outcome label/order; updated handler to read `include_no_worktree` and pass `allow_no_worktree` correctly.
- `.ai-workflow/scripts/ai_task.py` — added `--include-no-worktree` flag to `update-from-main` sub-parser.
- `.ai-workflow/scripts/test_update_from_main.py` — added `TestWorktreePathForBranch`, `TestProcessBranchNoWorktree`, and `TestUpdateFromMainNoWorktreeFlag` test classes (42 tests total, all pass).
- `.ai-workflow/README.md` — updated `update-from-main command` section with new flags and behavior.
- `.ai-workflow/skills/executor.md` — added note that single-task mode handles no-worktree branches.

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python -m unittest test_update_from_main` — 42/42 tests passed
- Dry-run `update-from-main AI-025` — reported `dry_run_no_worktree` with temp worktree path
- Dry-run `update-from-main --all` — AI-025, AI-027 correctly shown as `Skipped — no local worktree`
- Dry-run `update-from-main --all --include-no-worktree` — AI-025, AI-027 shown as `Would update via temporary worktree`
- `git diff --name-only main...HEAD` — only task folder and implementation files changed
- No forbidden files modified

## Assumptions

- Temporary worktree path uses the same naming convention as `claim`: `<repo>.worktrees/<branch-slug-after-ai/>`. This means a conflict-resolution worktree is easy to find and matches what an executor would open manually.
- `_worktree_remove` is best-effort on success: if removal fails (rare), the worktree is left in place. The outcome is still reported as `updated` since the merge succeeded. This matches the spirit of the task (leave conflict worktrees, clean up successful ones).
- `manager.md` does not need updating — it already says to run `update-from-main` on task branches; the new behavior is backward-compatible.

## Known risks

- Medium risk overall (git operations). The no-worktree code path creates and removes real git worktrees. All destructive operations are gated on user passing `--apply`. Dry-run is default. Conflicts are never auto-resolved.
- If the computed temporary worktree path already exists (e.g., a previous conflict was left there), `_worktree_add` will fail and return `error` outcome with an actionable message. No data is lost.
