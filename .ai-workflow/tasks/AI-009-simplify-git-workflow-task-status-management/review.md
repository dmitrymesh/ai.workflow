# Review: AI-009

## Decision

changes_requested

## Blocking issues

1. Existing done task history is no longer discoverable through `history`.
   `.ai-workflow/scripts/_history.py:19` still hard-codes `tasks/done/`, but this branch migrates completed tasks to flat `tasks/<id>/` folders with `metadata.yaml.status: done`. In the reviewed worktree, `python .ai-workflow/scripts/ai_task.py list` shows AI-001..AI-007 under `done`, while `python .ai-workflow/scripts/ai_task.py history` prints `(no matching done tasks)` and `history --show AI-001` prints `No done task found: AI-001`. This violates the requirements and acceptance criteria that existing completed task history remains readable/discoverable.

2. `claim` can leave the workflow in a claimed/in_progress state even when worktree creation fails.
   `_create_worktree()` returns `False` on `git worktree add` failure (`.ai-workflow/scripts/_worktree.py:72`), but `claim_task()` still writes `branch` and `status: in_progress` immediately afterward (`.ai-workflow/scripts/_worktree.py:131`). If git is unavailable, the branch already exists, or worktree creation fails for any reason, the task becomes claimed without a prepared/synced worktree. The contract requires claim to create or prepare the task branch/worktree and fail clearly if unsafe to start.

3. `claim` does not reject blocked tasks.
   The claim path checks only `status == ready` and whether `branch` is already set (`.ai-workflow/scripts/_worktree.py:91`, `.ai-workflow/scripts/_worktree.py:97`). It never checks `blocked_by`, even though the requirement says claim must fail clearly if the task is blocked. A ready task with unresolved blockers can therefore be claimed and moved to `in_progress`.

## Non-blocking issues

- The smoke test used `claim --print-only`, which mutates metadata to `in_progress`. That is consistent with the current implementation, but it means the validation did not exercise real worktree creation or sync for the new `claim` command.

## Scope check

In scope. The diff is limited to `.ai-workflow/` protocol files and task artifacts. No Unity or unrelated project files were changed.

## Acceptance criteria check

Not met. Stable metadata status, list/board grouping, and lifecycle commands are mostly present, but the blockers above fail the done-history discoverability and safe executor claim criteria.

## Test quality

Validation commands reported as run, and I re-ran `validate` and `list` successfully in the task worktree. However, the submitted validation missed the broken `history` behavior and did not run actual `claim` worktree creation.

## Unity-specific risks

None found.

## Required fixes

1. Update `history` to use `all_task_dirs()`/metadata status so flat `status: done` tasks are listed and `--show` works after migration. Keep legacy done-dir compatibility if needed.
2. Make `claim` fail without changing metadata if worktree creation/preparation fails, or otherwise provide a durable recovery path that does not falsely mark the task as claimed.
3. Make `claim` reject tasks with unresolved `blocked_by` references before branch/worktree creation or metadata mutation.
4. Add focused smoke coverage for `history` after migration, blocked-task claim rejection, and failed worktree creation behavior.
