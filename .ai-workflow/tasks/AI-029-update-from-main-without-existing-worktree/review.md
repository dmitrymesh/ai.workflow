# Review: AI-029

Reviewed 2026-05-13.

## Decision

changes_requested

## Blocking issues

1. `.ai-workflow/scripts/_update_from_main.py:180` ignores temporary worktree
   cleanup failure after a successful merge. `_worktree_remove(temp_path, root)`
   returns `(ok, output)`, but the result is discarded and the command always
   reports `Temporary worktree cleaned up.` at line 183. This violates the task's
   cleanup and clear recovery requirements: if `git worktree remove` fails, the
   command leaves a managed worktree behind while telling the user it was
   removed. Handle the failure explicitly by reporting the leftover path and
   cleanup error, and add a focused test for `remove_ok=False`.

## Non-blocking issues

None.

## Scope check

Passed. Changed files are in the requested CLI, tests, docs, role guidance, and
task artifact scope. No forbidden files were modified.

## Acceptance criteria check

Mostly satisfied, but blocked by the cleanup failure handling above. Dry-run
single-task no-worktree reporting works, `--all` excludes no-worktree branches
by default, `--all --include-no-worktree` includes them, conflict handling is
covered by tests, and existing worktree-backed behavior remains covered.

## Test quality

Good coverage overall: `test_update_from_main` covers the new no-worktree
selection, apply success, add failure, and conflict paths. It is missing the
cleanup-failure case that exposes the blocking issue.

## Required fixes

Handle `_worktree_remove` failure after successful merge and test that path.
The command should not claim cleanup succeeded when it did not.
