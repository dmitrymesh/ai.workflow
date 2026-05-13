# AI-030: Audit merged workflow and obsolete CLI

## Goal

Audit the current `.ai-workflow` implementation after the recent workflow task
merges and produce a concrete, evidence-backed cleanup/refactor plan for
obsolete commands, stale documentation, and workflow behavior that no longer
matches the branch-first design.

## Context

Many workflow tasks were merged recently, including branch-first discovery,
approval, claim, review auto-commit, update-from-main, worktree pruning, Unity
guardrail changes, and documentation updates. The project now needs a fresh
post-merge verification pass against the actual `main` state.

The requester specifically suspects that scripts still contain obsolete,
unused commands. Candidate areas to inspect include legacy or low-level
commands such as `prepare-worktree`, `migrate`, direct `move` usage, stale
main-first guidance, and any command or documentation path that duplicates a
newer branch-first workflow.

Relevant files:

- `.ai-workflow/scripts/`
- `.ai-workflow/README.md`
- `.ai-workflow/config.yaml`
- `.ai-workflow/skills/manager.md`
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/reviewer.md`
- `.ai-workflow/skills/unity-guardrails.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.ai-workflow/templates/`
- Done task reports for `AI-018` through `AI-029` when needed for context

## Scope

Allowed changes:

- Audit behavior and documentation only.
- Run CLI commands in dry-run or isolated temporary-task form where needed to
  verify branch-first workflows.
- Read current source and relevant done task reports.
- Update only this task's `report.md` and `validation.md` with findings,
  command results, and a proposed follow-up backlog.

Forbidden changes:

- Do not remove, rename, or refactor commands in this task.
- Do not change workflow behavior, docs, config, role skills, or templates.
- Do not create or delete real project task branches except temporary audit
  branches explicitly documented in `validation.md`.
- Do not modify Unity project files, packages, project settings, or `.meta`
  files.
- Do not mark any task as `done` except through the normal reviewer flow.

## Requirements

- Verify that the intended branch-first happy path is internally consistent:
  manager draft creation, human approval, executor claim, submit, review
  artifact commit, update-from-main, branch discovery, and merged worktree
  pruning.
- Identify every CLI command that appears obsolete, legacy-only, duplicated,
  misleading, or unsafe in the current branch-first workflow.
- For each obsolete/stale command candidate, classify the recommended action:
  keep as supported, keep but mark legacy, hide from default help, deprecate
  with warning, or remove.
- Identify stale or contradictory documentation in README, role skills,
  adapters, templates, and script help text.
- Identify refactor opportunities only when they reduce real complexity or
  remove duplication in the current codebase.
- Produce follow-up task proposals sized for one branch/PR each, with
  suggested ordering and dependencies.
- Clearly distinguish verified failures from suspicions, design preferences,
  and low-priority cleanup ideas.

## Acceptance criteria

- `report.md` contains a workflow verification matrix covering the major
  branch-first commands and role handoffs.
- `report.md` contains an obsolete-command inventory with evidence and a
  recommendation for each command reviewed.
- `report.md` contains a stale-documentation inventory with file references.
- `report.md` contains a prioritized follow-up backlog for cleanup/refactor
  tasks, including blocked-by relationships where sequencing matters.
- `validation.md` records every command run and whether it passed, failed, or
  was intentionally not run.
- No production workflow code or documentation outside this task folder is
  changed by the task.
- `python .ai-workflow/scripts/ai_task.py validate` passes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `python .ai-workflow/scripts/ai_task.py --help`
- `python .ai-workflow/scripts/ai_task.py list`
- `python .ai-workflow/scripts/ai_task.py list-branches`
- `python .ai-workflow/scripts/ai_task.py prune-worktrees`
- `python .ai-workflow/scripts/ai_task.py update-from-main --all`
- Run the existing workflow script tests that are available in the repository.
- `rg -n "prepare-worktree|migrate|main_first|main-first|move .* ready|legacy|deprecated|obsolete" .ai-workflow AGENTS.md CLAUDE.md`
- Manual review of `.ai-workflow/scripts/ai_task.py` command registration and
  command modules.
- `git diff --name-only main...HEAD`

## Notes

This is an audit task, not the cleanup implementation. Follow-up cleanup tasks
should be created only after this task identifies the exact commands and files
that should change.
