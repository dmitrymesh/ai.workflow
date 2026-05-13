# AI-024: Add merged worktree pruning helper

## Goal

Add a safe helper for identifying and optionally removing task worktrees whose
branches have already been merged into `main`.

## Context

AI-018 found stale worktrees for merged tasks AI-008 through AI-015. They add
noise to `git worktree list` and can confuse tooling, but removal must be safe
and explicit.

## Scope

Allowed changes:

- Add a `prune-worktrees` or `cleanup-merged-worktrees` command.
- Default to listing candidates only.
- Add an explicit `--apply` flag if removal is implemented.
- Update README cleanup docs.

Forbidden changes:

- Do not remove worktrees by default.
- Do not delete unmerged task branches.
- Do not use force deletion unless explicitly requested by the user.
- Do not remove worktrees with dirty changes.

## Requirements

- The command must identify worktrees whose branches are merged into `main`.
- The command must skip the main checkout and active unmerged task branches.
- Dry-run/list mode must be the default.
- Apply mode must refuse dirty worktrees or report them clearly.

## Acceptance criteria

- Dry-run lists merged task worktrees as cleanup candidates.
- Active unmerged task worktrees are not listed as safe removals.
- `--apply`, if implemented, removes only clean merged worktrees.
- README documents the cleanup flow.
- `validate` passes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `git worktree list`
- Dry-run cleanup command
- If `--apply` is implemented, test on a disposable clean merged worktree

## Notes

Created from AI-018 finding: "LOW - stale worktrees for merged tasks".
