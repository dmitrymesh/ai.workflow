# Review: AI-024

## Decision

changes_requested

## Blocking issues

1. `.ai-workflow/scripts/_prune.py:74` selects every worktree whose branch is
   merged into `main`, without filtering to task branches. The task goal is a
   helper for merged task worktrees, and the README says the command cleans up
   merged task worktrees. As written, a clean worktree for any non-task branch
   that is already merged into `main` would be listed and removed by `--apply`.
   Limit candidates to the configured task branch prefix (for example
   `workflow.discovery.branch_prefix`, default `ai/`) and add a test proving a
   merged non-task branch is skipped.

## Non-blocking issues

None.

## Scope check

Mostly in scope, but the candidate selection currently reaches beyond task
worktrees.

## Acceptance criteria check

Blocked. Dry-run is default, active unmerged task worktrees are skipped, dirty
apply behavior is tested, and validation passes. The command still needs to
avoid touching non-task worktrees.

## Test quality

Good baseline coverage for parsing, dry-run filtering, dirty skip, removal, and
failure reporting. Missing coverage for merged non-task worktrees.

## Required fixes

Filter prune candidates to task branches only and add a regression test for a
merged non-task branch/worktree.
