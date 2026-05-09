# AI-028: Return to main after manager task creation

## Goal

Update the branch-first manager workflow so after creating and committing a
draft task branch, the manager returns the main checkout to `main`.

## Context

In branch-first mode, the manager currently creates a task with:

```bash
git checkout main
git checkout -b ai/AI-NNN-slug
```

This leaves the shared checkout on the newly created task branch. That is
surprising for follow-up manager work and less convenient now that branch-first
approval can be handled from the `main` control plane. After task creation, the
manager should leave the repository on `main` unless there is a specific reason
to remain on the task branch.

Relevant files:

- `.ai-workflow/skills/manager.md`
- `.ai-workflow/README.md`
- `AGENTS.md`
- `CLAUDE.md`
- Any branch-first approval documentation added by AI-021 if present on `main`

## Scope

Allowed changes:

- Update manager instructions to explicitly return to `main` after committing
  a draft task contract on its task branch.
- Update branch-first task creation docs with the final checkout step.
- Clarify that task approval commands are intended to be run from the `main`
  control plane when supported by the workflow.
- Add a short note that the task branch remains the source of truth for active
  task artifacts even when the manager's checkout returns to `main`.

Forbidden changes:

- Do not implement new CLI behavior unless documentation references an already
  existing command.
- Do not change task status transitions.
- Do not modify branch naming conventions.
- Do not change executor worktree semantics.
- Do not modify Unity/project forbidden files or unrelated repository files.

## Requirements

- The branch-first manager workflow must no longer imply that the shared
  checkout should remain on the newly created task branch after task creation.
- The docs must include an explicit final step equivalent to `git checkout main`
  after the draft task contract is committed.
- The docs must preserve the rule that the task folder is committed to the task
  branch, not to `main`.
- The docs must mention that human approval can be performed from `main` when
  using the branch-first approval workflow.
- The wording must not require executors to work from `main`; execution still
  happens in task branches/worktrees.

## Acceptance criteria

- Manager docs show the final return-to-`main` step.
- README branch-first task creation docs show the final return-to-`main` step.
- The source-of-truth distinction remains clear: active task artifacts live on
  task branches, completed history lives on `main`.
- No CLI implementation files are changed unless needed for documentation
  consistency.
- `python .ai-workflow/scripts/ai_task.py validate` passes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `rg -n "checkout main|approve|approval|branch-first|task branch|control plane" .ai-workflow/README.md .ai-workflow/skills AGENTS.md CLAUDE.md`
- `git diff --name-only main...HEAD`
- Manual diff review confirming only protocol/docs/task artifacts changed

## Notes

Leave this task in `draft`. A human must approve it by moving it to `ready`
before execution.
