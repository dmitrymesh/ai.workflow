# Execution Report: AI-008

## Summary

Added a documented, bounded review appeal step to the protocol. Design choice: artifact-based appeal using existing statuses — no new status introduced. The appeal reuses the `changes_requested → in_progress → ready_for_review` cycle; the presence of an `## Appeal` section in `report.md` signals to the reviewer that the submission is an appeal, not a normal fix.

**Fix (review round 2):** Resolved the blocking issue — escalation to human now has a durable, machine-readable encoding. When escalating, the reviewer moves the task to `ready_for_human` (not `changes_requested`) and writes `decision: escalated_to_human` in `decision.yaml`. This distinguishes "human must decide" from "executor must fix" without adding a new status.

Changes:
- `executor.md` — added "Review appeal" section: when/how to file an appeal, what the `## Appeal` section must contain, what to do after each follow-up decision (including the escalated path now clarifies task moves to `ready_for_human`).
- `reviewer.md` — added "Evaluating an executor appeal" section: three follow-up decision options with explicit status transitions and `decision.yaml` values (`approve`, `changes_requested`, `escalated_to_human`).
- `.ai-workflow/README.md` — added "Review appeal" section with decision convention table showing all three `decision.yaml` values and their status outcomes.

## Changed files

- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/reviewer.md`
- `.ai-workflow/README.md`

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python .ai-workflow/scripts/ai_task.py list` — passed
- Manual consistency check: executor.md, reviewer.md, and README.md all describe the same appeal rules, `decision.yaml` conventions (`approve`, `changes_requested`, `escalated_to_human`), and one-appeal limit — consistent
- Forbidden file check: no `.env*`, no unrelated files changed

## Assumptions

- Worktree carried over from round 1 (`prepare-worktree AI-008`, branch `ai/AI-008-add-executor-review-appeal-step`).
- No new status was introduced. Human escalation uses the existing `ready_for_human` status with `decision: escalated_to_human` in `decision.yaml` as the distinguishing convention.

## Known risks

- The appeal mechanism relies on the reviewer noticing the `## Appeal` section in `report.md`. A reviewer who skips `report.md` might treat an appeal round as a normal review. Mitigated by the explicit section heading convention and the reviewer skill instruction to check for it.
