# Review: AI-020

## Follow-up review 2026-05-13

The automatic commit path now uses task-folder pathspecs for both the staged
diff check and `git commit`, so the previous finding is fixed for successful
auto-commit runs. One related recovery-path issue remains.

## Decision

changes_requested

## Blocking issues

1. `.ai-workflow/scripts/_tasks.py:201` still prints an unsafe manual recovery
   command. The automatic commit now uses pathspecs, but on `git add` or
   `git commit` failure the error message tells reviewers to run
   `git commit -m 'review: ...'` without `-- <task paths>`. In exactly the
   constrained/failure environments where this recovery text matters, following
   that command can still commit unrelated pre-staged files. Include the same
   task-folder pathspecs in the manual commit command and add/update a test that
   asserts the recovery instructions are path-isolated.

## Non-blocking issues

None.

## Scope check

Passed. Changes are limited to review command behavior, CLI help, reviewer
guidance, focused tests, and task artifacts.

## Acceptance criteria check

Blocked only on the recovery instructions. Default approve/changes-requested
commit behavior, `--no-commit`, scoped automatic commit pathspecs, and basic
artifact staging are covered.

## Test quality

Good baseline coverage, including automatic pathspec isolation. Missing coverage
for the manual recovery command shown on git failure.

## Required fixes

Add task-folder pathspecs to the manual recovery `git commit` command and cover
that error message in tests.
