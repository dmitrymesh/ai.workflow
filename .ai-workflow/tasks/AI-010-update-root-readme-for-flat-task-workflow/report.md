# Execution Report: AI-010

## Summary

Updated root `README.md` to reflect the flat task-folder workflow introduced by AI-009. All legacy status-directory references and `ready_for_human` mentions removed. The documented workflow now matches `config.yaml` and `.ai-workflow/README.md`.

Key changes:
- "Core idea" section rewritten to describe stable folder paths with `metadata.yaml.status` as source of truth.
- Status lifecycle updated to match `config.yaml` exactly (removed `ready_for_human`, corrected transitions).
- Recommended workflow steps updated: executor uses `claim`/`submit`, reviewer uses `review --approve`/`--changes-requested`, human step reframed as branch merge.
- "Files" section path examples updated from `tasks/<status>/<task>/` to `tasks/<task-id>-<slug>/`.
- `board.md` noted as gitignored and local.
- Basic commands section: added `claim`, `submit`, `review --approve`, `review --changes-requested`.
- Example executor prompt updated to use `claim` and `submit`.
- Example reviewer prompt updated to use `review --approve`/`--changes-requested`.
- Task relationship examples changed from AI-010/011/012 to AI-020/021/022 (AI-010 is a real task).

## Changed files

- `README.md` — documentation update only; no implementation code modified.

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed.
- Searched `README.md` for all seven legacy terms (`.ai-workflow/tasks/draft`, `.ai-workflow/tasks/ready`, `.ai-workflow/tasks/in_progress`, `.ai-workflow/tasks/ready_for_review`, `.ai-workflow/tasks/changes_requested`, `.ai-workflow/tasks/done`, `ready_for_human`) — none found.
- Confirmed presence of: flat folder example, `claim`, `submit`, `review AI-001 --approve` commands.
- `git diff --name-only HEAD` — only `README.md` changed; no forbidden files touched.

## Assumptions

None.

## Known risks

None. Documentation-only change.

---

## Review fixes (changes_requested round 1)

Addressed all three blocking issues from the review:

1. **Lifecycle transition mismatch** — replaced `any status → rejected` with explicit per-status rejected transitions matching `config.yaml`; added `done → changes_requested (via human-request-changes)`; fixed executor role entry from `changes_requested → in_progress` to `changes_requested → ready_for_review`.

2. **Missing commands** — added `human-request-changes` and `migrate` examples to the Basic commands section with brief descriptions of their purpose.

3. **Untracked task artifacts** — staged and committed `task.md`, `metadata.yaml`, `review.md`, `decision.yaml` so the full task folder travels with the branch.
