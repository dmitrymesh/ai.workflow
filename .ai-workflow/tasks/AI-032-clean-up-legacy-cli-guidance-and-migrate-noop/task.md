# AI-032: Clean up legacy CLI guidance and migrate noop

## Goal

Clean up stale CLI guidance identified by `AI-030` and make the `migrate`
command self-explanatory when there are no legacy status-directory tasks left
to migrate.

## Context

`AI-030` found that the workflow happy path works after the recent merges, but
some CLI-facing text still points users at legacy or low-level commands:

- `.ai-workflow/scripts/ai_task.py` module examples still show
  `move AI-001 ready`, which is superseded by `approve AI-001` in branch-first
  workflow.
- The module examples still show `prepare-worktree` without clearly labelling
  it as legacy, even though the parser help already says to prefer `claim`.
- `.ai-workflow/scripts/_migrate.py` reports `0 moved, 0 skipped` when there is
  nothing to migrate, which is technically correct but not informative for a
  repo already on the flat task layout.

This is the low-risk cleanup/refactor follow-up after `AI-031` restored the
broken cascade tests.

Relevant files:

- `.ai-workflow/scripts/ai_task.py`
- `.ai-workflow/scripts/_migrate.py`
- `.ai-workflow/scripts/test_*`
- `.ai-workflow/tasks/AI-030-audit-merged-workflow-and-obsolete-cli/report.md`

## Scope

Allowed changes:

- Update `ai_task.py` top-level usage/examples so the primary branch-first
  happy path uses `approve`, `list-branches`, and `claim`.
- Move `prepare-worktree` examples out of the main happy path or label them as
  legacy.
- Update `migrate` output so a no-op run clearly says no legacy status-directory
  tasks were found and the repo is already on the flat layout.
- Add or adjust focused tests for the no-op `migrate` message if the existing
  test structure supports it with small changes.
- Update this task's `report.md` and `validation.md`.

Forbidden changes:

- Do not remove any command in this task.
- Do not change task lifecycle behavior, branch-first semantics, or status
  transitions.
- Do not change `prepare-worktree`, `claim`, `approve`, `move`, `submit`, or
  `review` behavior.
- Do not broadly rewrite README, role skills, adapters, or templates unless a
  tiny wording alignment is required by the changed help text.
- Do not modify Unity project files, packages, project settings, or `.meta`
  files.

## Requirements

- Users reading `ai_task.py --help` and module examples must no longer see
  `move AI-001 ready` as the recommended approval path.
- `prepare-worktree` must remain available but clearly treated as legacy in
  examples/help-facing text.
- Running `migrate` in a repo with no legacy task directories must print a
  clear no-op message in addition to or instead of the numeric summary.
- Existing workflow tests must continue to pass.
- The diff must remain small and focused on CLI guidance/no-op messaging.

## Acceptance criteria

- `python .ai-workflow/scripts/ai_task.py --help` shows no stale happy-path
  guidance for `move AI-001 ready`.
- `rg -n "move AI-001 ready|prepare-worktree" .ai-workflow/scripts/ai_task.py`
  confirms `move AI-001 ready` is gone and `prepare-worktree` is legacy-labelled
  if still present.
- `python .ai-workflow/scripts/ai_task.py migrate` in the current flat-layout
  repo prints an explicit no-op/already-flat-layout message.
- Relevant workflow tests pass.
- `python .ai-workflow/scripts/ai_task.py validate` passes.
- `git diff --name-only main...HEAD` shows only in-scope files and this task's
  task folder.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py --help`
- `python .ai-workflow/scripts/ai_task.py migrate`
- `python .ai-workflow/scripts/test_cascade.py`
- `python .ai-workflow/scripts/test_review.py`
- Run any migrate-specific tests if present, or document `not run` if none exist.
- `python .ai-workflow/scripts/ai_task.py validate`
- `rg -n "move AI-001 ready|prepare-worktree|legacy" .ai-workflow/scripts/ai_task.py .ai-workflow/scripts/_migrate.py`
- `git diff --name-only main...HEAD`

## Notes

This task intentionally does not remove legacy commands. Removal or hiding from
default help should be a separate task only if this cleanup still leaves user
confusion or maintenance burden.
