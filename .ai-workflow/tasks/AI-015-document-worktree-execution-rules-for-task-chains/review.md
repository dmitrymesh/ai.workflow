# Review: AI-015

## Decision

approve

## Blocking issues

- None.

## Non-blocking issues

- None.

## Scope check

In scope. The diff changes `.ai-workflow/README.md` and AI-015 task artifacts only; no implementation files or generated board changes are present.

## Acceptance criteria check

Satisfied. The docs explain parent/child branch strategy, warn about early blocked work, and the AI-011 example now correctly serializes AI-013 after AI-012 because of the semantic dependency.

## Test quality

`validate` passes. I reran `python .ai-workflow/scripts/ai_task.py validate`, inspected the diff, and checked the new section against AI-012/AI-013 task contracts.

## Unity-specific risks

Not applicable.

## Required fixes

- None.
