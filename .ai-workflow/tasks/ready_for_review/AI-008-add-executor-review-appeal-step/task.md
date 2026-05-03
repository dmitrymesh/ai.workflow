# AI-008: Add executor review appeal step

## Goal

Add a documented, bounded review appeal step so an executor can challenge one `changes_requested` review when the executor believes the implementation is correct and the reviewer may have misunderstood the task, code, or validation evidence.

## Context

The current protocol has a simple review loop:

- executor finishes work and moves `in_progress` to `ready_for_review`
- reviewer returns exactly one of `ready_for_human`, `changes_requested`, or `rejected`
- after `changes_requested`, executor is expected to make fixes and move the task back through `in_progress` to `ready_for_review`

This is clear, but it assumes the reviewer is always correct. In practice, a reviewer can misunderstand intent, miss evidence in `validation.md`, or ask for a change that would make the implementation worse. The protocol should allow one disciplined objection from the executor before the executor changes code solely to satisfy a disputed review.

The appeal must not become an endless agent argument. It should be a single, explicit opportunity for the executor to present evidence, after which the reviewer either accepts the appeal, clarifies/updates the requested changes, or escalates to human decision.

## Scope

Allowed changes:

- `.ai-workflow/README.md`
- `.ai-workflow/config.yaml` and `.ai-workflow/scripts/` only if a new status, transition, or CLI support is needed
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/reviewer.md`
- `.ai-workflow/skills/manager.md` only if manager handoff or task lifecycle documentation needs clarification
- `.ai-workflow/templates/` only if task artifacts need a new section or file for appeal notes
- Adapter docs or generated snippets only if they directly describe the affected review loop

Forbidden changes:

- Do not implement product/application feature changes outside the workflow protocol.
- Do not allow executors to move tasks to `ready_for_human` or `done`.
- Do not allow executors to ignore a review silently.
- Do not create an unbounded debate loop between executor and reviewer.
- Do not remove the reviewer's authority to request changes, reject, or escalate.
- Do not weaken the human approval rule for moving `draft` tasks to `ready`.
- Do not modify unrelated completed task history except the AI-008 task folder and regenerated board if needed.

## Requirements

- Define a clear appeal mechanism for exactly one executor challenge after a `changes_requested` decision.
- The executor appeal must be written in a durable task artifact, not only in chat. Acceptable designs include a new section in `report.md`, `review.md`, or `validation.md`, or a new explicitly named artifact if the executor and reviewer skills are updated consistently.
- The appeal must include:
  - the specific review finding(s) being disputed
  - the executor's reasoning
  - references to code, task requirements, acceptance criteria, or validation evidence
  - whether the executor made any code changes before appealing
- The reviewer must be instructed to consider the appeal and then make exactly one follow-up decision:
  - accept the appeal and move the task toward `ready_for_human` if the implementation is acceptable
  - maintain or revise `changes_requested` with clearer blocking rationale
  - escalate to human decision when the dispute depends on product judgment, ambiguous acceptance criteria, or conflicting priorities
- The protocol must make clear that after the one appeal is resolved, the executor must follow the resulting decision unless a human intervenes.
- If a new status is introduced, all status sources must stay consistent:
  - `.ai-workflow/config.yaml`
  - `.ai-workflow/scripts/_core.py`
  - CLI list/board/validate behavior if status lists are hardcoded
  - README lifecycle documentation
- If no new status is introduced, document how the appeal is represented using existing statuses and artifacts, and why that is sufficient.
- Preserve existing review decisions and status names unless a change is necessary for the appeal flow.
- Keep the change small enough for one branch/PR.

## Acceptance criteria

- Executor instructions explain when an appeal is allowed, what evidence must be provided, and that only one appeal is permitted per review round/task dispute.
- Reviewer instructions explain how to evaluate an appeal and how to record the follow-up decision.
- README documents the appeal flow in the task lifecycle so future agents understand it without relying on chat memory.
- The workflow prevents silent refusal: an executor who disagrees with review must either implement the requested changes or file the documented appeal.
- The workflow prevents endless disagreement: after the reviewer's follow-up decision or human escalation, the executor must proceed according to that outcome.
- Any added status, transition, template, or CLI behavior is reflected consistently across config, scripts, docs, and validation.
- Existing task lifecycle behavior still works for the normal no-appeal path.
- No forbidden files or unrelated protocol areas are changed.

## Validation

Required:

- Run `python .ai-workflow/scripts/ai_task.py validate`.
- Run `python .ai-workflow/scripts/ai_task.py board`.
- Run `python .ai-workflow/scripts/ai_task.py list` and confirm the status output remains coherent.
- If status/transition logic changes, run focused smoke checks for allowed and rejected transitions involving the appeal flow, using temporary tasks if needed. Fully clean up temporary tasks before review.
- Manually review `.ai-workflow/README.md`, `executor.md`, and `reviewer.md` to confirm the same appeal rules are described consistently.
- Record any tests not run as `not run` in `validation.md`.
- Confirm no forbidden files changed.

## Notes

- Suggested default design: prefer a documentation/artifact-based appeal using the existing `changes_requested` and `ready_for_review` loop unless implementation shows a new status is needed. A new status adds more protocol surface and should be justified.
- This task should remain in `draft` until a human approves the task contract and moves it to `ready`.
