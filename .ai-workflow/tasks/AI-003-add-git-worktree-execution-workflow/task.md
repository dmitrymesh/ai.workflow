# AI-003: Add git worktree execution workflow

## Goal

Add a documented git worktree-based execution workflow so every executor task is implemented in a task-specific isolated worktree by default.

The workflow should define how task branches and worktree directories are named, how task contracts become visible to executor worktrees, how executors should start work, and how reviewers should review task-specific diffs.

## Context

The current protocol is file-based and assumes agents edit the repository working tree directly. That is simple at first, but it has two problems:

- multiple executor agents working in the same checkout can overwrite or confuse each other's changes
- even with one executor, the main checkout may contain unrelated human edits, task-management changes, or experiments that should not become part of the task diff

Git worktrees allow each task to have an isolated checkout backed by its own branch. This matches the protocol's existing preference: one task = one branch = one PR. The main checkout should be treated as the control plane for task creation, approval, review, and human coordination; implementation work should happen in task worktrees.

The current task metadata already includes `branch` and `pr` fields, but the workflow does not define how they are set or used.

Important git visibility constraint: a new worktree only sees committed branch state by default. If a human moves a task to `ready` but does not commit that task folder/status change, an executor launched in a separate worktree will not automatically see it. The protocol should avoid requiring a handoff commit by providing an explicit prepare-worktree flow that copies/syncs the approved task folder into the task worktree.

## Scope

Allowed changes:

- `.ai-workflow/skills/manager.md`
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/reviewer.md`
- `.ai-workflow/README.md`
- root `README.md`
- `CLAUDE.md`
- `AGENTS.md`
- `.claude/commands/*`
- `.ai-workflow/scripts/ai_task.py` if small CLI support is needed for branch/worktree naming, metadata updates, or task path discovery
- `.ai-workflow/templates/metadata.yaml` only if additional metadata fields are clearly needed
- `.ai-workflow/board.md` if regenerated

Forbidden changes:

- Do not add external dependencies.
- Do not add a server, daemon, database, or vendor-specific agent integration.
- Do not implement automatic agent spawning or automatic execution loops.
- Do not require GitHub, GitLab, Jira, or any remote service.
- Do not change status names or the core status lifecycle.
- Do not mark any task as `done`.

## Requirements

- Define the recommended branch naming convention for task work:
  - branch names should include the task id
  - recommended format: `ai/<task-id>-<slug>`, for example `ai/AI-003-git-worktree-execution-workflow`
- Define the recommended worktree directory naming convention:
  - worktree paths should include the task id
  - recommended default: a sibling directory to the main repo, for example `../ai_workflow.worktrees/AI-003-git-worktree-execution-workflow`
- Decide and document whether worktree/branch names should be based on the task number:
  - expected answer: yes, use the task id as the stable prefix because task ids are unique, compact, and visible in reports/reviews
  - include the slug only as a human-readable suffix
- Define worktree-by-default as the recommended execution policy:
  - executor agents should implement every task in a task-specific worktree, even when only one executor is running
  - direct edits in the main checkout should be treated as exceptional and documented in `report.md`
- Document the task visibility / handoff rule:
  - no intermediate commit should be required just to make an approved task visible to the executor
  - the protocol should provide a prepare-worktree flow that creates or identifies the task branch/worktree and explicitly syncs the approved task folder into that worktree
  - the synced task folder must include the human-approved `ready` status and full task contract
  - the main checkout remains the source of truth for manager approval at prepare time
  - do not imply that uncommitted files in the main checkout are automatically visible in a separate worktree
- Add CLI support for the prepare-worktree handoff unless there is a strong reason not to:
  - command name is up to the implementer, but it should be discoverable from `--help`
  - it should accept a task id
  - it should verify the task is in `ready` before preparing executor work
  - it should compute branch and worktree names using the task id convention
  - it should create the worktree safely or print the exact safe commands if creation is not possible
  - it should sync the approved task folder into the worktree so the executor can read `task.md` there without requiring a prior commit
  - it should update `metadata.yaml.branch` in the task metadata
  - it should clearly print the worktree path and branch to hand to the executor
- Document the manager workflow:
  - after human approval moves a task to `ready`, run or describe the prepare-worktree handoff
  - make the approved task contract visible to the task worktree without requiring a handoff commit
  - update `metadata.yaml.branch` when a branch is assigned
- Document the executor workflow:
  - execute one task inside its assigned worktree
  - verify it is on the task branch before editing
  - write `report.md` and `validation.md` in the task folder
  - move the task to `ready_for_review` when complete
- Document the reviewer workflow:
  - review the diff for the task branch/worktree, not unrelated local changes in the main checkout
  - compare the diff against `task.md`, `report.md`, and `validation.md`
- Keep task artifact handling explicit:
  - executor should update `report.md`, `validation.md`, and status in the task worktree
  - reviewer should review those task artifact changes together with code changes from the task branch/worktree
  - documentation should describe how accepted task artifact changes get back to the main checkout during human acceptance/merge
- Keep the implementation portable across Windows/macOS/Linux path conventions where practical.
- Clearly state cleanup expectations for completed/rejected task worktrees.

## Acceptance criteria

- Documentation explains why direct edits in one shared working tree are unsafe both for parallel agents and for single-task work when the human has unrelated local edits.
- Documentation states that task-specific worktrees are the default execution mode.
- Documentation explains that uncommitted task files/status changes in the main checkout are not automatically visible in a separate worktree.
- Documentation defines a clear no-intermediate-commit handoff rule for making approved `ready` tasks visible to executor worktrees.
- CLI support exists, or a documented command-only fallback exists, for preparing a task worktree and syncing the approved task folder into it.
- The prepare-worktree flow verifies the task is `ready` before preparing executor work.
- The executor can read the approved `task.md` inside the task worktree after prepare-worktree runs, without requiring a prior task approval commit.
- Documentation includes branch and worktree naming conventions based on task id.
- Manager/executor/reviewer instructions describe how to use task worktrees.
- The protocol records or displays assigned task branches using the existing `metadata.yaml.branch` field, or documents why no CLI change was needed.
- If CLI support is added, it is documented and covered by smoke validation.
- Existing commands still work:
  - `create`
  - `move`
  - `list`
  - `board`
  - `validate`
  - `path`
- `validate` passes.
- No unrelated files or forbidden files are changed.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `python .ai-workflow/scripts/ai_task.py board`
- If CLI commands are added, run smoke tests for those commands.
- Manual review of docs and role skills to confirm the workflow covers manager, executor, and reviewer responsibilities.
- Forbidden file check: confirm no `.env*` or unrelated files were changed.

## Notes

- This task should not actually move current work into a new worktree unless that is explicitly required for validation.
- The goal is to make the protocol safe for parallel execution; it does not need to automate parallel execution.
- This task should remain in `draft` until human approval moves it to `ready`.
