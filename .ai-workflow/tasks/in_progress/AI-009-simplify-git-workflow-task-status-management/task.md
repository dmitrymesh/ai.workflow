# AI-009: Simplify git workflow task status management

## Goal

Redesign the AI task workflow so task status management is direct, Git-friendly, and hard to desynchronize across `main`, task branches, worktrees, review, and merge.

The target outcome is:

- stable task folders instead of status-by-directory moves
- executor self-service claiming of approved tasks
- task execution and review status changes traveling with the task branch after claim
- reviewer approval setting the task to `done` in the task branch
- human completion requiring only merge, not a separate post-merge status commit

## Context

The current protocol stores task status in folder paths:

```text
.ai-workflow/tasks/ready/<task-id>/
.ai-workflow/tasks/in_progress/<task-id>/
.ai-workflow/tasks/ready_for_review/<task-id>/
```

This causes operational problems with git worktrees and branches:

- the same task can exist in different status folders in `main` and a task worktree
- executor and reviewer must remember to mirror status moves back to `main`
- agents may not see a task when someone forgot to duplicate a status move in the control checkout
- merges can reintroduce the same task under multiple status paths
- the workflow depends on knowing subtle rules about which checkout owns which status change

The accepted design direction is to make task paths stable and put status in metadata. After a task is claimed, the task branch carries implementation artifacts and review status changes. A reviewer approval writes `status: done` in the task branch. The human then merges the branch to complete the task in `main`. If the human does not accept the task before merge, a command should move the task back to `changes_requested` in the same task branch with human feedback.

## Scope

Allowed changes:

- `.ai-workflow/README.md`
- `.ai-workflow/config.yaml`
- `.ai-workflow/scripts/`
- `.ai-workflow/skills/manager.md`
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/reviewer.md`
- `.ai-workflow/templates/`
- `AGENTS.md`, `CLAUDE.md`, and `.claude/commands/` only if adapter instructions must change to match the new workflow
- `.gitignore` only if generated board/cache behavior changes
- focused tests or smoke-test helpers for the workflow CLI

Forbidden changes:

- Do not implement unrelated product/application changes.
- Do not keep status-by-directory as the authoritative model after the migration unless explicitly justified as a backward-compatible transitional read path.
- Do not require a separate post-merge commit just to mark a reviewed task as `done`.
- Do not require a manager handoff step after human approval before an executor can start a ready task.
- Do not make GitHub mandatory for the core workflow. PR integration may be optional, but local git branches and diffs must remain sufficient.
- Do not let executors move `draft` tasks to `ready`; human approval remains required.
- Do not silently drop existing task history or task artifacts during migration.
- Do not modify Unity/project forbidden files or unrelated repository files.

## Requirements

- Replace or migrate the authoritative task status model from folder paths to stable task folders with `metadata.yaml.status`.
- Define the new lifecycle clearly. The expected default lifecycle is:

```text
draft -> ready -> in_progress -> ready_for_review -> changes_requested -> ready_for_review -> done
draft -> rejected
ready -> rejected
in_progress -> rejected
ready_for_review -> rejected
changes_requested -> rejected
```

- Remove the separate `ready_for_human` status from the normal lifecycle unless implementation analysis finds a compelling compatibility reason to keep it as deprecated/legacy.
- Define `done` semantics explicitly:
  - `done` in a task branch means reviewer approved the task and it is ready for human merge.
  - `done` in `main` means the approved task branch was merged and the task is complete in the main control view.
- Add executor self-service task claiming:
  - an executor can claim a `ready` task without a separate manager action
  - claim creates or prepares the task branch/worktree
  - claim records the branch in task metadata
  - claim moves the task to `in_progress`
  - claim must fail clearly if the task is not `ready`, already claimed, blocked, or otherwise unsafe to start
- Ensure task branches are the place where post-claim execution status changes are recorded:
  - executor submit moves `in_progress` or `changes_requested` to `ready_for_review`
  - reviewer changes request moves `ready_for_review` to `changes_requested`
  - reviewer approve moves `ready_for_review` to `done`
  - human pre-merge rejection/change request can move `done` back to `changes_requested` in the same task branch with durable feedback
- Ensure humans can complete normal approved work by merging the task branch only, with no required follow-up commit to update task status.
- Keep PR support optional and provider-agnostic:
  - the base workflow must work with local git branch diffs
  - metadata may store an optional PR/review URL or provider-specific reference
  - GitHub-specific automation must be an enhancement, not a dependency
- Rework `board`/`list` behavior for stable task folders:
  - board/list should group tasks by `metadata.yaml.status`
  - board output should be generated from metadata, not from directory names
  - define whether `.ai-workflow/board.md` remains tracked, becomes an ignored generated cache, or is validated for freshness
- Add validation and repair safeguards:
  - detect duplicate task ids across old status folders or migrated stable folders
  - detect mismatch between folder path and `metadata.yaml.id`
  - detect stale/generated board state if board remains tracked
  - detect unsafe task status changes in the wrong checkout if feasible
  - provide clear migration or repair guidance instead of silently accepting ambiguous state
- Migrate existing task folders without losing history. Existing `done` tasks should remain discoverable through history/list after the model change.
- Update manager, executor, and reviewer skills so agents no longer rely on manual status mirroring between `main` and worktrees.
- Update README lifecycle and worktree sections so a new user can follow the workflow without knowing the old duplication pitfalls.
- Keep the implementation small enough for one reviewable branch/PR. If the migration proves too broad, split into child tasks before implementation.

## Acceptance criteria

- Task folders have stable paths that do not encode status as the source of truth.
- `metadata.yaml.status` is the authoritative status used by CLI list/board/validate behavior.
- A ready task can be claimed by an executor through one command, producing a task branch/worktree and moving it to `in_progress`.
- No manager action is required between human approval to `ready` and executor claim.
- Executor submission records report/validation and moves the task to `ready_for_review` without requiring manual status duplication in `main`.
- Reviewer approval records review outcome and sets the task to `done` in the task branch.
- A human can complete an approved task by merging the branch; no separate post-merge `done` commit is required.
- A human can request changes before merge, and the workflow records that feedback durably while moving the task branch from `done` back to `changes_requested`.
- The core workflow works without GitHub access. If PR fields or commands exist, they are optional.
- `board` and `list` present a coherent grouped view from metadata statuses.
- `validate` catches duplicate task ids and obvious migration/status inconsistencies.
- Existing completed task history remains readable and included in appropriate list/history views.
- Manager, executor, reviewer, README, and adapter instructions describe the same lifecycle and ownership rules.
- Normal lifecycle smoke checks pass for create, human approval to ready, executor claim, submit, reviewer changes requested, resubmit, reviewer approve to done, and rejection paths.
- No forbidden files or unrelated protocol areas are changed.

## Validation

Required:

- Run `python .ai-workflow/scripts/ai_task.py validate`.
- Run `python .ai-workflow/scripts/ai_task.py list` and confirm tasks are grouped by metadata status.
- Run `python .ai-workflow/scripts/ai_task.py board` if board generation remains part of the workflow.
- Run focused CLI smoke checks using temporary tasks for:
  - create draft
  - human move/approve to `ready`
  - executor claim to `in_progress`
  - submit to `ready_for_review`
  - reviewer request changes to `changes_requested`
  - resubmit to `ready_for_review`
  - reviewer approve to `done`
  - human pre-merge request changes from `done` to `changes_requested`
  - reject paths where supported
- Confirm temporary smoke-test tasks are cleaned up or isolated from real task history before review.
- Manually review README and all role skills for consistent lifecycle language.
- Confirm existing `done` task history is still discoverable.
- Record any tests not run as `not run` in `validation.md`.
- Confirm no forbidden files changed.

## Notes

- This task should remain in `draft` until a human approves the contract and moves it to `ready`.
- The preferred design removes `ready_for_human` from the normal lifecycle because reviewer `done` plus human merge covers that handoff.
- The implementation should favor boring, explicit CLI commands over chat-only procedure:
  - `claim` or `claim-next`
  - `submit`
  - `review --approve`
  - `review --changes-requested`
  - `human-request-changes` or equivalent
- If backward compatibility with existing status-folder tasks is needed, implement it as a deliberate migration/read path and document when it can be removed.
