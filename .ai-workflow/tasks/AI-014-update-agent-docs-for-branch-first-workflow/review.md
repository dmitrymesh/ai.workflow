# Review: AI-014

## Decision

changes_requested

## Blocking issues

- The updated branch-first executor docs still instruct agents to claim from the main checkout. In `.ai-workflow/skills/executor.md`, the workflow says "From the main checkout, run: `claim <TASK-ID>`"; README repeats "claims the chosen task from the main checkout". That is the main-first claim flow, but AI-012 says branch-first active tasks live in task branches and the executor claims with the worktree already on the branch. The current `claim` implementation also uses `find_task()` in the current checkout, so this guidance will fail for branch-first tasks that are not present in `main`.
- The branch changes task folders outside the allowed scope. `task.md` forbids modifying task folders except AI-014 `report.md` and `validation.md`, but the diff edits `AI-012` and `AI-013` metadata plus AI-014 metadata. Clearing blocker relationships may be useful housekeeping, but it is explicitly outside this documentation task's scope.

## Non-blocking issues

- `.ai-workflow/skills/executor.md` says `list-branches` shows `done` as "(merged)" and mentions a `[merged]` marker. The implemented command groups branches under "Merged into main"; a `done` task branch can also be unmerged after reviewer approval but before human integration. This should be phrased in terms of the command's merged/unmerged grouping, not status alone.

## Scope check

Documentation changes are mostly in the requested files, but the task-folder metadata edits are out of scope for this task contract.

## Acceptance criteria check

Not satisfied yet. The docs include commit expectations and discovery commands, but role/user-facing instructions still preserve the old main-checkout claim path for branch-first execution, so agents can still be led to use `main` as the active control plane after discovery.

## Test quality

`validate` passes and the executor reported stale-reference scanning. I reran `validate`, inspected the branch diff, and checked the relevant docs against the current `claim` implementation and AI-012 branch-first contract.

## Unity-specific risks

Not applicable.

## Required fixes

- Split executor/manager/README instructions by workflow mode. For branch-first, tell executors to switch to or create/open the task worktree on the task branch before claiming, matching AI-012's "worktree already on branch" lifecycle. Keep the existing `claim from main` wording only under `main_first`.
- Remove out-of-scope metadata changes for AI-012 and AI-013 from this docs branch, or get the task scope amended. Keep only AI-014 artifacts needed for this task handoff/review.
- Correct the `list-branches` wording so `done` is not equated with merged and no nonexistent `[merged]` marker is documented.
