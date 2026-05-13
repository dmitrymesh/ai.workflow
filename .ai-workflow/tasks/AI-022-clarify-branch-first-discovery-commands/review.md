# Review: AI-022

## Decision

approve

## Blocking issues

None.

## Non-blocking issues

- The `list` warning is slightly absolute: in a task worktree, the current
  branch's task does appear in `list`. The important distinction is still clear:
  `list` is checkout-local and not a branch-first backlog view.

## Scope check

Passed. Changes are limited to README documentation, the optional `list`
warning, and task artifacts. No forbidden files were modified, and
`list-branches` discovery semantics were not changed.

## Acceptance criteria check

Passed. The README now presents `list-branches` as the branch-first backlog
view, documents `list` as current-checkout only, and validation passes.

## Test quality

Adequate for this low-risk docs and stderr-only CLI warning change. I verified
`validate`, `list`, `list-branches`, and `git diff --check`.

## Required fixes

None.
