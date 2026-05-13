# AI-019: Fix claim for branch-first mode

## Goal

Make `claim <TASK-ID>` work correctly when `workflow.mode: branch_first`.

## Context

AI-018 found that `.ai-workflow/scripts/_worktree.py::claim_task()` always runs
`git worktree add -b <branch> <path>`. In branch-first mode the task branch
already exists, so `claim` fails with "branch already exists" and executors must
manually run `git worktree add <path> <existing-branch>`.

## Scope

Allowed changes:

- Update `.ai-workflow/scripts/_worktree.py` claim/worktree creation logic.
- Add focused tests or smoke validation for branch-first and main-first claim behavior.
- Update executor docs only if command usage changes.

Forbidden changes:

- Do not redesign task statuses or approval rules.
- Do not change review or submit behavior.
- Do not add non-stdlib dependencies.
- Do not edit generated `.ai-workflow/board.md` as a source file.

## Requirements

- If the task branch already exists, `claim` must add a worktree to that branch without `-b`.
- If the task branch does not exist, legacy/main-first claim behavior must still create it.
- The computed worktree path must stay under `../ai_workflow.worktrees/<TASK-ID>-<slug>`.
- Error output must make branch/worktree failures actionable.

## Acceptance criteria

- `claim` on an existing task branch no longer fails because the branch exists.
- `claim --print-only` shows existing-branch commands without `-b` in branch-first mode.
- Main-first branch creation path remains covered by test or documented smoke validation.
- `validate` passes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Focused claim smoke test for an existing task branch
- Focused claim smoke test or unit test for the branch-creation path

## Notes

Created from AI-018 finding: "HIGH - claim is broken in branch-first mode".
