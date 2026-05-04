# AI-012: Design branch-first task workflow contract

## Goal

Design the branch-first task workflow contract and configuration model before
implementation.

## Context

The current workflow creates tasks in `main` and later modifies the same task
folders in task branches. AI-010 exposed recurring friction from that model:
manual merge-only integration, task artifact conflicts, reviewer changes not
being committed for executor handoff, and executors missing a `draft -> ready`
approval until they refresh the right checkout.

The desired direction is branch-first:

- active tasks live in their own `ai/<task-id>-<slug>` branches;
- manager, human approval, executor, and reviewer all commit task artifact
  changes to the same task branch;
- `main` receives completed/rejected task history only when the branch is
  integrated;
- active board/list views are assembled by scanning task branches/worktrees.

## Scope

Allowed changes:

- Update protocol documentation files needed to define the workflow contract
  before implementation, such as `.ai-workflow/README.md` and focused notes in
  role skills if needed for clarity.
- Add or update `.ai-workflow/config.yaml` fields that select integration mode
  and branch discovery behavior, if the design requires them.
- Define the expected lifecycle for manager creation, human approval, executor
  work, reviewer commits, changes requested loops, approval, and final
  integration.
- Define how local merge and hosted PR modes are selected by config.
- Define how task ids remain unique in a branch-first model.

Forbidden changes:

- Do not implement branch scanning, branch creation, PR creation, or merge
  automation in this task.
- Do not rewrite the existing CLI behavior beyond minimal config/schema
  additions needed for the contract.
- Do not remove support for reading completed task history from `main`.
- Do not change existing task statuses unless the contract explicitly requires
  it and acceptance criteria are updated before execution.

## Requirements

- The contract must specify source of truth for active tasks and completed task
  history.
- The contract must specify when task artifact changes must be committed.
- The contract must specify reviewer behavior: review artifacts are committed
  to the task branch.
- The contract must specify how executors discover `ready` tasks when tasks are
  not in `main`.
- The contract must specify integration modes, at least:
  - `local_merge`: human or future CLI integrates the task branch locally;
  - `pull_request`: task branch is integrated through a hosted PR.
- The contract must specify which config keys drive those modes.
- The contract must define a practical task id strategy that avoids collisions
  when tasks are created outside `main`.

## Acceptance criteria

- The branch-first workflow is documented clearly enough for a later executor
  to implement CLI behavior without product decisions.
- `.ai-workflow/config.yaml` includes integration/discovery settings if the
  design relies on configurable behavior.
- The design explicitly addresses the four observed AI-010 workflow problems:
  no PR/local integration path, merge conflicts from main-created tasks,
  uncommitted reviewer artifacts, and missed ready-state refresh.
- The design preserves support for both local git-client integration and
  hosted PR integration.
- No implementation commands are added unless they are explicitly documented as
  future work/placeholders.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Review the changed protocol/config documentation against this task's
  requirements.
- Confirm no CLI implementation files were changed except for minimal config
  support if justified in `report.md`.

## Notes

This task should unblock AI-013 and AI-014.
