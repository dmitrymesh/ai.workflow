# Review: AI-002

## Decision

approve

## Blocking issues

- None.

## Non-blocking issues

- None.

## Scope check

The implementation stayed within the allowed documentation, instruction, and generated board files. It did not change status names, the transition graph, permissions, external systems, or execution automation.

## Acceptance criteria check

Passed.

- Manager skill now says managers must not move tasks to `ready`.
- Root README documents a human approval step before execution.
- Example manager prompt now says to leave the task in `draft` and report that human approval is needed.
- `draft -> ready` remains an allowed lifecycle transition for humans.
- `.ai-workflow/README.md` quick start distinguishes manager creation from human approval.
- `AGENTS.md` includes the repository-level rule that only humans move `draft -> ready`.

## Test quality

Acceptable for a documentation/workflow rule change. The executor ran `validate` and `board`; I also ran both during review.

## Unity-specific risks

Not applicable. This repository is using the generic profile and no Unity files were changed.

## Required fixes

- None.
