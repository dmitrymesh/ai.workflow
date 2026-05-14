# Report: AI-033

## Summary

Reconciled stale metadata for `AI-008` and `AI-009` so `show-branch` and
`list-branches` report them as `done` and `Merged into main: yes`. The fix used
branch-ref resets rather than new commits on the historical branches, ensuring
no new "active unmerged" branches are introduced.

## Approach

`main` already carries `status: done` for both tasks (the flat-layout
`.ai-workflow/tasks/AI-008-.../metadata.yaml` and
`.ai-workflow/tasks/AI-009-.../metadata.yaml` were set to `done` by commit
`b9b43db`, the merge of `ai/AI-009-*` which migrated all nine then-existing
tasks to the flat layout). The problem was only that the branch REFS
(`ai/AI-008-*` and `ai/AI-009-*`) still pointed to old commits with the
legacy-layout `ready_for_review` metadata. `show-branch` reads from the branch
tip, not from main.

Fix: reset both branch refs to `main`'s HEAD via `git reset --hard main` from
their respective worktrees. After the reset:
- Each branch tip is a commit already in main, so both branches are "merged".
- `_read_task_meta_from_branch` runs `git ls-tree` on the branch (which is now
  main) and finds the flat-layout `done` metadata already present in main.

This is durable: the `done` metadata is already committed in main and will
persist regardless of branch ref state. The branch refs now simply reflect that
merged state accurately.

## Changed files (on this AI-033 branch)

- `.ai-workflow/tasks/AI-033-reconcile-merged-task-branch-metadata/report.md`
  (this file)
- `.ai-workflow/tasks/AI-033-reconcile-merged-task-branch-metadata/validation.md`

## Branch ref operations performed

- `ai/AI-008-add-executor-review-appeal-step` — reset from `356c3a9` (stale
  reconciliation attempt) → `9e474ef` (main HEAD) via
  `git reset --hard main` in its worktree
- `ai/AI-009-simplify-git-workflow-task-status-management` — reset from
  `1b21946` (stale reconciliation attempt) → `9e474ef` (main HEAD) via
  `git reset --hard main` in its worktree

Neither historical branch received new commits. The resets discard the prior
reconciliation commits from the first execution attempt.

## Why no code diff for AI-008/AI-009 is needed

The flat-layout `done` metadata for AI-008 and AI-009 already exists in main.
There is nothing new to commit on AI-033's branch to add it — it is already the
source of truth. The reconciliation is: ensuring the branch refs point to
commits that contain the correct metadata (main), not adding redundant copies.

## Assumptions

- `main`'s flat-layout `done` metadata for AI-008/AI-009 is the authoritative
  and permanent record. Resetting the branch refs to main is safe because all
  historical commits are reachable from main.
- The worktree-based `git reset --hard main` is the correct mechanism; it avoids
  creating unmerged commits while correctly moving each branch's tip.

## Known risks

None. No workflow code changed. All metadata reflects reality.
