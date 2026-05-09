# AI-021: Add branch-first approve command

## Goal

Add a human-facing `approve <TASK-ID>` command that approves a draft task from
the control-plane checkout without requiring manual `cd` into the task worktree.

## Context

AI-018 found that branch-first human approval is awkward: the human must enter
the task worktree, run `move <TASK-ID> ready`, and commit `metadata.yaml`.

## Scope

Allowed changes:

- Add an `approve` subcommand to `ai_task.py`.
- Implement branch lookup/update logic in an existing or new script module.
- Provide `--print-only` if full automation is risky.
- Update manager/README docs for the new approval path.

Forbidden changes:

- Do not allow agents to approve draft tasks automatically.
- Do not bypass the `draft -> ready` transition rule.
- Do not auto-claim or execute the task.
- Do not add hosted-service requirements.

## Requirements

- `approve <TASK-ID>` must locate the task branch from the main/control-plane checkout.
- It must move `metadata.yaml.status` from `draft` to `ready`.
- It must commit the approval artifact to the task branch, or `--print-only` must print exact commands.
- It must fail clearly if the task is not in `draft`.
- It must not require the target branch to be checked out in the main checkout.

## Acceptance criteria

- `approve AI-NNN --print-only` prints correct branch/worktree/status/commit commands.
- `approve AI-NNN` commits `ready` status to the task branch when safe.
- `show-branch AI-NNN` reports `Status: ready` after approval.
- Human approval remains explicit and auditable.
- `validate` passes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Smoke test on a temporary draft task branch
- `show-branch` verification after approval

## Notes

Created from AI-018 finding: "MEDIUM - no approve command for human approval from main".
