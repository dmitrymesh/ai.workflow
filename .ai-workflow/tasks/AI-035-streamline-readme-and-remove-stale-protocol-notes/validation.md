# Validation: AI-035

## Local

- `python .ai-workflow/scripts/ai_task.py validate`: passed
- `python .ai-workflow/scripts/ai_task.py install-plan --help`: passed — command shape unchanged
- `python .ai-workflow/scripts/ai_task.py --help`: passed — all commands present
- `rg -n "Future work|not in this task|move AI-001 ready|move .* ready" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md`:
  one match in README.md (prohibition: "Do not move the task to ready") — no stale guidance
- `rg -n "migrate|migration" README.md .ai-workflow/README.md`:
  - README.md:290 — `migrate` command, preceded by "legacy upgrade only" label ✓
  - README.md:558 — "serialized field renames without migration" (Unity profile content, not workflow migration) ✓
  - .ai-workflow/README.md:182 — "**Legacy upgrade only**" label present ✓
  - .ai-workflow/README.md:185 — `migrate` command ✓
  - .ai-workflow/README.md:809 — "No migration is required" (backward-compat note) ✓
  All migration references are in legacy/upgrade context.
- `git diff --name-only main...HEAD`: only AI-035 task folder + README.md + .ai-workflow/README.md (after commit)

## Manual review

- `.ai-workflow/README.md`: "Future work (not in this task)" table removed ✓
- `.ai-workflow/README.md`: Branch-first contract intro updated to reflect implemented state ✓
- `.ai-workflow/README.md`: All "(future CLI — AI-NNN)" comments removed ✓
- `.ai-workflow/README.md`: Worktree section condensed; historical problem framing removed ✓
- `README.md` and `.ai-workflow/README.md`: migrate labeled as legacy upgrade only ✓
- Safety constraints verified present:
  - install-plan ownership model documented ✓
  - "Do not move the task to ready" rule preserved ✓
  - "Executor must not mark tasks as done" preserved ✓
  - review auto-commit documented ✓
  - list-branches for branch-first discovery ✓
  - Unity serialized file guardrails preserved ✓
- No forbidden files changed (no CLI, Unity files, config semantics, task history) ✓

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: none
- Package changes: none

## Notes

Documentation-only task. No Unity code changed; recompile check not applicable.
