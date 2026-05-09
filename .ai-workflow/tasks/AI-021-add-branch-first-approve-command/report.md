# Execution Report: AI-021

## Summary

Added an `approve <TASK-ID>` command that lets a human approve a draft task from
the main/control-plane checkout without manually entering the task worktree.
The command locates the task branch, verifies `draft` status, updates
`metadata.yaml` to `ready`, and commits the change to the task branch.

## Changed files

- `.ai-workflow/scripts/_approve.py` — new module: `approve_task` command handler
- `.ai-workflow/scripts/ai_task.py` — import `_approve`, register `approve` subparser, update module docstring
- `.ai-workflow/skills/manager.md` — updated human approval section to reference the new command

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `approve --help` — subcommand registered and described correctly
- `approve AI-022 --print-only` (from worktree) — printed correct commands with branch/path/commit message
- Live `approve AI-023` — committed `ready` status to task branch via existing worktree
- `show-branch AI-023` after approval — reported `Status: ready`
- `approve AI-023` on already-ready task — failed with clear error message
- AI-023 reverted back to `draft` after test

## Assumptions

- The `_discovery.py` private helpers (`_run_git`, `_list_local_branches`, etc.) are stable enough to import directly; no public API was added in that module.
- When a task branch is already checked out in an existing worktree, the command reuses that worktree rather than failing. This is the common case in this repo (all active task branches have worktrees).
- `--print-only` generates commands relative to `repo_root()` (the main checkout when run from there); paths may differ if run from inside a worktree.

## Known risks

- If `git worktree list --porcelain` output format changes, `_find_existing_worktree` could miss the existing worktree and fall through to create a temp one, which would then fail because the branch is already checked out. Low risk — the porcelain format is stable.
- `approve` does not push the approved branch to the remote. If the remote copy of the task branch is what executors watch, they would need to push separately.
