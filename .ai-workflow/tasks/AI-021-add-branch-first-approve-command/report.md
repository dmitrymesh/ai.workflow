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
- Live `approve AI-023` (clean existing worktree) — committed `ready` status; `show-branch` confirmed `Status: ready`
- `approve AI-023` on already-ready task — failed: `approve requires task to be draft (current: ready).`
- Dirty-index safety: staged a file in AI-023 worktree, then `approve AI-023` — failed with "has staged changes" listing the staged file and instructions to unstage before approving
- AI-023 reverted back to `draft` after tests

## Assumptions

- The `_discovery.py` private helpers (`_run_git`, `_list_local_branches`, etc.) are stable enough to import directly.
- When a task branch is already checked out in an existing worktree, the command reuses that worktree after asserting it is clean (no staged changes, no local modifications to the target file).
- `--print-only` generates commands relative to `repo_root()` (the main checkout when run from there).

## Known risks

- If `git worktree list --porcelain` output format changes, `_find_existing_worktree` could miss the existing worktree and fall through to create a temp one, which would then fail because the branch is already checked out. Low risk — the porcelain format is stable.
- `approve` does not push the approved branch to the remote. If executors watch the remote copy, they would need to push separately.
