# Review: AI-023

## Decision

approve

## Blocking issues

None.

## Non-blocking issues

None.

## Scope check

Passed. Changes are limited to the shared simple-YAML parser refactor,
call-site updates in discovery and approve code, and task artifacts. No new
dependencies, metadata format changes, or discovery output changes were found.

## Acceptance criteria check

Passed. `_discovery.py` no longer contains the duplicate metadata parser,
existing tests pass, `list-branches` works, `show-branch AI-018` works, and
`validate` passes.

## Test quality

Adequate for the refactor. I reran the required validation commands and checked
the patch with `git diff --check`.

## Required fixes

None.
