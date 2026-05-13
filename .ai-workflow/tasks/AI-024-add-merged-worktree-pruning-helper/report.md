# Execution Report: AI-024

## Summary

Added a `prune-worktrees` command that identifies and optionally removes task
worktrees whose branches have been merged into `main`.

Default behavior is dry-run (list only). `--apply` removes clean merged
worktrees and skips any with dirty changes.

Implementation in `_prune.py`:
- `_list_worktrees(root)` — parses `git worktree list --porcelain`, normalises `refs/heads/` prefixes, handles detached HEAD (branch = None).
- `_is_dirty(path)` — runs `git status --porcelain` in the worktree; treats git failure as dirty (safe default).
- `_remove_worktree(path, root)` — runs `git worktree remove`.
- `prune_worktrees(args)` — orchestrates: gets merged set from `_merged_into_main()`, skips main checkout and detached/unmerged entries, in dry-run lists candidates, in apply mode removes clean ones and reports dirty/failed.

## Changed files

- `.ai-workflow/scripts/_prune.py` — new module with the command and helpers.
- `.ai-workflow/scripts/ai_task.py` — import `prune_worktrees`; register `prune-worktrees` subparser with `--apply` flag.
- `.ai-workflow/scripts/test_prune.py` — 17 tests covering porcelain parsing, dirty detection, dry-run filtering, apply removal, dirty skip, and failure exit code.
- `README.md` — added `prune-worktrees` usage to the cleanup section after "Human merges".

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python -m unittest test_prune` — 17/17 passed
- Dry-run smoke: `prune-worktrees` from the AI-024 worktree — correctly listed 15 merged worktrees, did not list AI-020 or AI-024 (active/unmerged)
- Forbidden file check: passed — no forbidden files modified

## Assumptions

- The main checkout is identified as the first entry in `git worktree list --porcelain` output. This matches git's documented behavior.
- `_is_dirty` is reused pattern from `_update_from_main.py`; treating git failure as dirty is intentionally conservative.
- `--apply` does not delete the branch itself — only the worktree. Branch cleanup remains a separate manual step (`git branch -d`).

## Known risks

- Low. If the git repo has worktrees in unusual locations (outside the expected naming convention), they are still included if their branch is merged. This is correct and safe behavior.
