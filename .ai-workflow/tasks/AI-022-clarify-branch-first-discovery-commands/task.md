# AI-022: Clarify branch-first discovery commands

## Goal

Make the command surface and docs clear that `list-branches`, not `list`, is
the active-task discovery command in branch-first mode.

## Context

AI-018 found that `list` only scans the current checkout's task folders. In
branch-first mode, active tasks live in separate task branches and are invisible
to `list` unless already merged or checked out.

## Scope

Allowed changes:

- Update README quick-start and role docs to emphasize `list-branches`.
- Optionally add a warning to `list` when `workflow.mode: branch_first`.
- Keep behavior backward-compatible for `main_first`.

Forbidden changes:

- Do not remove `list`.
- Do not change task discovery semantics for `list-branches`.
- Do not introduce network requirements.

## Requirements

- Branch-first quick-start must show `list-branches` for active task discovery.
- `list` documentation must state it lists tasks in the current checkout only.
- If a warning is added, it must be concise and not break scripts relying on output.

## Acceptance criteria

- A new user can identify `list-branches` as the branch-first backlog command.
- `list` no longer appears to be the complete active backlog view in branch-first mode.
- `validate` passes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Manual docs review
- If code changes are made, smoke checks for `list` and `list-branches`

## Notes

Created from AI-018 medium finding and reviewer note that this deserved a standalone follow-up.
