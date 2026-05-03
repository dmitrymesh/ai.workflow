# AI-002: Require human approval before ready

## Goal

Update the Portable AI Task Protocol so manager-created tasks require explicit human approval before moving from `draft` to `ready`.

After this change, a manager agent should create and fully describe task contracts in `draft`, then stop. A human reviews the contract and manually moves the task to `ready` only if they accept the scope, requirements, acceptance criteria, and validation plan.

## Context

The current manager skill says to move a task to `ready` when it is implementable. In practice this lets the manager both write and approve the task contract. The desired workflow separates these responsibilities:

- manager drafts the task contract
- human approves the contract
- executor starts only from `ready`

This should make task scope explicit and prevent accidental execution of a task the human has not accepted.

## Scope

Allowed changes:

- `.ai-workflow/skills/manager.md`
- `.ai-workflow/README.md`
- root `README.md`
- `AGENTS.md` if repository-level instructions need to mention human approval before `ready`
- `.claude/commands/*` only if executor-facing commands need clarification that execution starts from `ready`
- `.ai-workflow/scripts/ai_task.py` only if command help or generated output should make the human-approval step clearer
- `.ai-workflow/board.md` if regenerated

Forbidden changes:

- Do not change the status names or transition graph.
- Do not prevent a human from manually moving `draft -> ready` with the existing `move` command.
- Do not add user accounts, permissions, authentication, or external approval systems.
- Do not implement automatic execution or automatic ready transitions.
- Do not mark any task as `done`.

## Requirements

- Update manager instructions so manager agents:
  - create tasks in `draft`
  - fill the task contract completely
  - do not move tasks to `ready`
  - explicitly report that human approval is needed
- Update documentation to describe the new approval gate:
  - `draft` means proposed task contract
  - `ready` means human-approved task contract ready for execution
  - only a human should move `draft -> ready`
- Update recommended workflow examples so manager prompts do not say "move to ready if implementable"; instead they should stop after drafting and ask for human approval.
- Preserve executor behavior: executors should still only execute tasks in `ready` or `changes_requested`, depending on the flow.
- If CLI help or README examples include immediate `create` then `move ready`, clarify that the second command is a human approval step.

## Acceptance criteria

- Manager skill clearly states that managers must not move tasks from `draft` to `ready`.
- README workflow says human approval is required before `ready`.
- Example manager prompt reflects the new behavior.
- Existing lifecycle remains valid: `draft -> ready` still exists as an allowed transition.
- `validate` still passes.
- `board` still generates successfully.
- No unrelated protocol behavior is changed.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `python .ai-workflow/scripts/ai_task.py board`
- Manual review of manager-facing docs/examples to confirm they no longer authorize manager self-approval to `ready`.
- Forbidden file check: confirm no `.env*` or unrelated files were changed.

## Notes

- This task intentionally changes role responsibility, not the underlying status transition graph.
- This task itself should remain in `draft` until a human approves the contract and moves it to `ready`.
