# AI-011: Adopt branch-first task workflow

## Goal

Adopt a branch-first task workflow where active task contracts and execution
artifacts live in task branches, while `main` receives only completed/rejected
task history through integration.

## Context

Recent execution of AI-010 exposed git workflow problems in the current
main-first model:

- Tasks are created in `main`, then the same task folder is modified in task
  branches, which creates recurring merge conflicts.
- Integration currently relies on manual local merge in a git client; no PR or
  local integration mode is modeled as a first-class workflow choice.
- Reviewer artifacts can remain local to a worktree instead of being committed
  to the task branch, making executor/reviewer handoff unreliable.
- Executors may not notice that a human moved a task from `draft` to `ready`
  until they refresh/list from the right checkout.

The proposed model is:

- A manager creates the task folder directly in a task branch/worktree.
- Human approval, executor work, reviewer decisions, and follow-up changes all
  happen as commits in that task branch.
- `main` is the accepted history of completed/rejected tasks, not the live
  control plane for active tasks.
- CLI discovery commands scan unmerged task branches/worktrees to show active
  task status.

## Scope

Allowed changes:

- Split and coordinate the work needed to define, implement, and document the
  branch-first workflow.
- Keep child tasks reviewable and independently scoped.
- Track dependencies so implementation and docs wait for the workflow contract.

Forbidden changes:

- Do not implement code in this parent task.
- Do not mark this parent task as done until child task outcomes are accepted.
- Do not collapse all child work into one broad PR.

## Requirements

- Define a branch-first workflow contract before changing CLI behavior.
- Add CLI support for discovering active task branches/worktrees.
- Update agent role instructions and user-facing documentation after the
  workflow behavior is defined.
- Preserve support for completed task history in `main`.
- Preserve portability: the protocol must support local-only git users and
  hosted PR workflows.

## Acceptance criteria

- Child task exists for workflow contract/design.
- Child task exists for CLI implementation.
- Child task exists for documentation and role skill updates.
- CLI and docs child tasks are blocked by the design task.
- Related history links point to the workflow changes that motivated this work.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Review task relationships with `python .ai-workflow/scripts/ai_task.py show AI-011`.

## Notes

This parent is an umbrella task. Each child should still follow one task = one
branch = one reviewable change.
