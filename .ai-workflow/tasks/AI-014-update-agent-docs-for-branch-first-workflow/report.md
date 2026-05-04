# Execution Report: AI-014

## Summary

Updated all agent-facing and user-facing documentation to describe the
branch-first task workflow and commit discipline. The changes ensure no role
skill tells agents that active tasks are managed in `main` after claim, and
that all actors (executor, reviewer) know they must commit their artifacts
to the task branch before handing off.

## Changed files

- `.ai-workflow/skills/executor.md` — added "Discovering ready tasks" section
  (`list-branches`, `show-branch`); expanded workflow steps with explicit
  commit steps (commit artifacts before submit; commit metadata.yaml after
  submit)
- `.ai-workflow/skills/manager.md` — added "Branch-first task creation" section
  describing how to create a task branch, commit the draft, and note the human
  approval commit expectation
- `.ai-workflow/skills/reviewer.md` — added commit discipline block after the
  CLI commands: reviewer must commit review.md, decision.yaml, and metadata.yaml
  to the task branch before handing off
- `AGENTS.md` — replaced stale `tasks/<status>/<task-id>/` path with current
  flat path; added step 4 for branch-first task discovery
- `CLAUDE.md` — added `list-branches` to pre-task steps; added commit rules
  (commit before submit, commit metadata.yaml after submit)
- `README.md` — added `list-branches` / `show-branch` to Basic Commands;
  updated executor workflow step to show commit sequence; updated reviewer
  workflow step to show commit sequence; updated example executor prompt
- Metadata.yaml files for AI-012, AI-013, AI-014 — cleared completed blocker
  relationships (AI-012, AI-013 now done; AI-014 unblocked)

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `git diff --stat HEAD` — confirms only documentation files and task artifacts
  changed; no CLI scripts modified; no forbidden files
- Manual scan for stale `tasks/<status>/` paths in updated docs — none found
  (the only `status-by-directory` references are in the `migrate` command
  description and historical task reports, both correct)
- Requirements check: see validation.md

## Assumptions

- Implemented in the task worktree on branch
  `ai/AI-014-update-agent-docs-for-branch-first-workflow`.
- Root `README.md` needed updating: the executor and reviewer workflow steps
  described no commit expectations, which contradicts the branch-first contract
  and was identified in task requirements.
- `.ai-workflow/README.md` already contains the full branch-first contract from
  AI-012; this task adds commit discipline to the role skill files and adapter
  entrypoints, not to the contract doc itself, to avoid duplication.
- The legacy `main_first` workflow path is preserved in docs wherever relevant
  (executor discovery fallback, manager note, README migrate command).

## Known risks

- None. All changes are documentation-only; no behavioral code was modified.
