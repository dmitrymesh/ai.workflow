# AI-026: Add task branch update from main command

## Goal

Add a workflow CLI command that updates active task branches by merging the
current `main` into them, either for one specified task or for all active task
branches that have local worktrees.

## Context

In branch-first mode, several task branches can be created at once. As other
tasks are completed and merged into `main`, older active task branches become
stale. Today a human or executor must manually switch into each branch or
worktree and merge `main`, which is slow and error-prone.

The desired workflow is a command that can target a specific task, or update
all eligible active task worktrees in one run. This command must be careful:
it performs git merges and may encounter dirty worktrees or conflicts.

Relevant files:

- `.ai-workflow/scripts/ai_task.py`
- `.ai-workflow/scripts/_discovery.py`
- `.ai-workflow/scripts/_git.py`
- `.ai-workflow/scripts/_tasks.py`
- `.ai-workflow/README.md`
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/manager.md`
- `.ai-workflow/skills/reviewer.md`
- Existing tests under `.ai-workflow/tests/` if present

## Scope

Allowed changes:

- Add a CLI command for updating task branches from `main`.
- Support updating one task by task id.
- Support updating all eligible active task branches with an explicit
  `--all` flag.
- Limit bulk updates to active unmerged task branches with local worktrees.
- Add dry-run behavior, status reporting, and clear conflict/skip reporting.
- Update role docs and README with the intended workflow.
- Add focused tests for command selection, safety checks, and reporting.

Forbidden changes:

- Do not auto-resolve merge conflicts.
- Do not force-reset, force-push, rebase, or delete branches/worktrees.
- Do not update merged task branches.
- Do not update task branches without a local worktree in `--all` mode unless
  the task explicitly adds and documents a separate safe mode for that.
- Do not modify task status transitions or task metadata as part of updating
  from `main`.
- Do not change integration mode semantics.
- Do not modify Unity/project forbidden files or unrelated repository files.

## Requirements

- The command must provide a safe default mode that reports what would happen
  without modifying branches, or require an explicit apply flag before running
  merges.
- The command must accept a specific task id, such as `AI-026`, and update only
  that task branch/worktree.
- The command must accept an explicit bulk flag, such as `--all`, and update
  all eligible active local task worktrees.
- The command must identify task branches using the configured branch prefix
  and branch-first discovery rules.
- The command must skip merged task branches.
- The command must skip or fail clearly on dirty worktrees before attempting a
  merge.
- The command must stop and report clearly if a merge conflict occurs, including
  which worktree needs manual resolution.
- The command must summarize updated, skipped, failed, and already-current
  branches.
- The command must not switch the user's main checkout branch as a side effect.
- The command must work in `workflow.mode: branch_first`; if unsupported in
  `main_first`, it must report that clearly.

## Acceptance criteria

- Running the command for one task reports or performs `main` merge only for
  that task's branch/worktree.
- Running the command with `--all` reports or performs updates for all active
  unmerged task branches that have local worktrees.
- Dirty worktrees are not merged and are reported as skipped or failed.
- Already-current branches are reported without creating unnecessary commits.
- Merge conflicts leave the affected worktree in a normal git conflict state
  for manual resolution and do not continue silently.
- Merged task branches are not selected for update.
- README and role guidance document when to use the command.
- Focused tests cover target selection and safety behavior.
- `python .ai-workflow/scripts/ai_task.py validate` passes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Relevant unit tests for the new command
- Dry-run/update command against a single disposable task branch or mocked git
  fixture
- Dry-run/update command with `--all` against disposable or mocked worktrees
- Manual review of command output for clean, dirty, already-current, and
  conflict scenarios where practical
- `git diff --name-only main...HEAD`
- Confirm no forbidden files changed

## Notes

Prefer a conservative interface. A possible command shape is:

```bash
python .ai-workflow/scripts/ai_task.py update-from-main AI-026
python .ai-workflow/scripts/ai_task.py update-from-main --all
python .ai-workflow/scripts/ai_task.py update-from-main --all --apply
```

The executor may choose a different name if it better matches the existing CLI,
but the single-task and explicit bulk behavior must remain.

Leave this task in `draft`. A human must approve it by moving it to `ready`
before execution.
