# AI-029: Update from main without existing worktree

## Goal

Extend `update-from-main` so active task branches without an existing local
worktree can still be updated from `main` through an explicit, safe workflow.

## Context

AI-026 added `update-from-main`, but bulk mode only considers active branches
that already have local worktrees. This means draft tasks created by the
manager, such as `AI-025` and `AI-027`, are visible in `list-branches` but are
not eligible for update because no executor worktree exists yet.

The command should support this common branch-first case without requiring a
human to manually check out each branch. Updating branches without worktrees is
git-sensitive: conflicts must leave a clear recovery path, and the command must
not silently switch or dirty the main checkout.

Related task:

- `AI-026`: Add task branch update from main command

Relevant files:

- `.ai-workflow/scripts/_update_from_main.py`
- `.ai-workflow/scripts/ai_task.py`
- `.ai-workflow/scripts/test_update_from_main.py`
- `.ai-workflow/README.md`
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/manager.md`

## Scope

Allowed changes:

- Extend `update-from-main` to handle a specified task branch that has no local
  worktree.
- Add an explicit option for bulk mode to include branches without local
  worktrees.
- Create a temporary or managed worktree for no-worktree updates rather than
  switching the main checkout.
- Keep dry-run as the default and report whether a worktree would be created.
- Add clear cleanup behavior for successful temporary-worktree updates.
- Add clear conflict behavior that preserves the conflicted worktree for manual
  resolution and reports its path.
- Update command help, README, and role guidance.
- Add focused tests for no-worktree selection, temporary worktree creation,
  cleanup, and conflict reporting.

Forbidden changes:

- Do not merge by switching the main checkout to the task branch.
- Do not force-reset, force-push, rebase, delete branches, or auto-resolve
  conflicts.
- Do not remove the existing safe behavior for branches with local worktrees.
- Do not include no-worktree branches in `--all` unless the user passed an
  explicit flag for that behavior.
- Do not modify task status transitions or task metadata as part of updating
  from `main`.
- Do not modify Unity/project forbidden files or unrelated repository files.

## Requirements

- Single-task mode must be able to update an active unmerged task branch even
  when that branch has no local worktree.
- The command must use a separate worktree for no-worktree updates and must not
  leave the main checkout on another branch.
- Dry-run output for no-worktree tasks must say that a worktree would be
  created before merging.
- Apply mode for a clean successful no-worktree update must merge `main` into
  the task branch and clean up the temporary worktree if it was created solely
  by the command.
- If a merge conflict occurs in a temporary/managed worktree, the command must
  leave that worktree in place and print the path and manual resolution
  instructions.
- Bulk `--all` mode must keep its current worktree-only default.
- Bulk mode may include branches without worktrees only through an explicit
  flag such as `--include-no-worktree`.
- The command must still skip merged branches and inactive statuses.
- The command must summarize updated, skipped, failed, already-current,
  temporary-worktree-created, cleaned-up, and conflict outcomes clearly.

## Acceptance criteria

- `update-from-main AI-025` dry-run reports that `AI-025` has no worktree and
  that an apply run would create one safely.
- `update-from-main AI-025 --apply` updates the branch from `main` without
  switching the main checkout.
- `update-from-main --all` does not include no-worktree branches by default.
- `update-from-main --all --include-no-worktree` includes active unmerged
  branches without local worktrees.
- Successful no-worktree updates clean up temporary worktrees created by the
  command.
- Conflicted no-worktree updates leave the worktree for manual resolution and
  report the path.
- Existing worktree-backed update behavior continues to work.
- Focused tests cover the new no-worktree behavior.
- `python .ai-workflow/scripts/ai_task.py validate` passes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Relevant tests for `update-from-main`
- Dry-run a single no-worktree task branch
- Dry-run `--all` and confirm no-worktree branches are excluded by default
- Dry-run `--all --include-no-worktree` and confirm no-worktree branches are
  included
- If practical, apply on a disposable no-worktree branch and verify main
  checkout remains on `main`
- Manual conflict-path review or mocked conflict test
- `git diff --name-only main...HEAD`
- Confirm no forbidden files changed

## Notes

Leave this task in `draft`. A human must approve it by moving it to `ready`
before execution.
