# Execution Report: AI-002

## Summary

Updated the Portable AI Task Protocol so manager-created tasks require explicit human approval before moving from `draft` to `ready`. Managers now leave completed task contracts in `draft` and report that a human must approve before execution begins.

## Changed files

- `.ai-workflow/skills/manager.md` — Replaced "Move task to `ready` only when it is implementable" with a rule that managers must not move tasks to `ready` and must report that human approval is needed.
- `README.md` (root) — Added a new "2. Human approves task contract" step in the recommended workflow (renumbered subsequent steps 3–5); updated status lifecycle to list `draft → ready` as a human-only transition; updated example Codex manager prompt to stop at `draft` instead of moving to `ready`.
- `.ai-workflow/README.md` — Updated quick-start example with comments distinguishing the manager step (create → draft) from the human approval step (move → ready).
- `AGENTS.md` — Added rule: only humans move `draft → ready`.

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python .ai-workflow/scripts/ai_task.py board` — generated successfully
- Manual review: manager.md no longer authorizes manager self-approval to `ready`
- Forbidden file check: no `.env*` or unrelated files changed

## Assumptions

- No changes to `ai_task.py` were needed; command help does not contain manager-specific "move to ready" guidance.
- `AGENTS.md` warranted a rule addition since it governs all agent roles in the repository.

## Known risks

- None. Status names and transition graph are unchanged; existing `draft → ready` transition remains valid for humans.
