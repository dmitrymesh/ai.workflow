# Review: AI-008

## Decision

changes_requested

## Blocking issues

- The human escalation path is not represented durably enough. The new docs define escalation as a distinct reviewer follow-up decision, but then instruct the reviewer to leave the task in `changes_requested`, and they do not define how `decision.yaml` should distinguish "escalated to human" from ordinary maintained `changes_requested`. That means an executor, board reader, or later reviewer cannot reliably tell whether the next action is "executor must fix" or "human must decide" without interpreting prose in `review.md`. This violates the requirement that the reviewer make and record exactly one follow-up decision, including escalation to human decision, and weakens the acceptance criterion that the workflow prevents endless disagreement after human escalation.

## Non-blocking issues

- The no-new-status design is reasonable, but if it is kept, the docs need an explicit durable encoding for human escalation using existing artifacts, for example a required `decision.yaml` convention and unambiguous next actor wording in `review.md`.

## Scope check

The changed files are in scope: `.ai-workflow/README.md`, `.ai-workflow/skills/executor.md`, `.ai-workflow/skills/reviewer.md`, and the AI-008 task artifacts. No forbidden files were changed.

## Acceptance criteria check

Partially satisfied. Executor and reviewer appeal mechanics are documented, the no-appeal path remains unchanged, and no new status was introduced. The human escalation branch does not yet have a sufficiently clear durable representation, so the appeal flow is not fully specified.

## Test quality

Executor reported `validate`, `board`, `list`, a manual consistency check, and forbidden file check. Reviewer reran `validate` and `list`; both passed. No code-level tests are needed for this docs-only change.

## Unity-specific risks

Not applicable.

## Required fixes

- Define how a human escalation is recorded using existing statuses/artifacts, or introduce a status/decision convention consistently across docs and validation.
- Make the next actor explicit for escalation so `changes_requested` does not ambiguously mean both "executor must fix" and "human must decide".
- Update `.ai-workflow/README.md` and `reviewer.md` consistently; update `executor.md` if the executor's post-escalation behavior changes.
