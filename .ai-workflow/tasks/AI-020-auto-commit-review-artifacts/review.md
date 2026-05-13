# Review: AI-020

## Decision

changes_requested

## Blocking issues

1. `.ai-workflow/scripts/_tasks.py:226` commits the whole current index, so
   unrelated pre-staged files can be included in the review commit. The helper
   stages only `metadata.yaml`, `review.md`, and `decision.yaml`, but then runs
   `git commit -m ...` without pathspecs or an index-isolation check. If the
   reviewer already has an unrelated staged change, Git will commit it too,
   violating the explicit requirement that unrelated dirty files must not be
   included. Fix the commit path so only the reviewed task artifacts can be
   committed, and add a test that starts with an unrelated staged file/change.

## Non-blocking issues

None.

## Scope check

Passed. Changes are limited to review command behavior, CLI help, reviewer
guidance, focused tests, and task artifacts.

## Acceptance criteria check

Blocked. Default approve/changes-requested commit behavior, `--no-commit`, and
basic artifact staging are covered, but the unrelated dirty/staged-file
criterion is not safely satisfied.

## Test quality

Good baseline coverage, but missing the critical pre-staged unrelated file case.

## Required fixes

Ensure the auto-commit cannot include unrelated staged files, then add a focused
test for that scenario.
