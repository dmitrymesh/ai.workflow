# Validation: AI-014

## CLI validation

All commands run from the task worktree at
`C:\Projects\ai_workflow.worktrees\AI-014-update-agent-docs-for-branch-first-workflow`.

### validate

```
python .ai-workflow/scripts/ai_task.py validate
```
Result: **Validation passed.**

### Diff scope check

```
git diff --stat HEAD
```
Result: Only documentation files (`executor.md`, `manager.md`, `reviewer.md`,
`AGENTS.md`, `CLAUDE.md`, `README.md`) and task artifact metadata changed.
No CLI scripts, no Unity files, no board.md. **Passed.**

### Stale main-first reference scan

Searched updated docs for `tasks/<status>/` paths:
- `AGENTS.md`: stale `tasks/<status>/<task-id>/` path replaced — **clean**
- `README.md`: only `migrate` command description references old layout — correct
- `executor.md`, `manager.md`, `reviewer.md`: no stale paths — **clean**
- `CLAUDE.md`: no stale paths — **clean**

### Mode-split claim instructions check (round 2)

- `executor.md`: mode-split present — branch-first uses `git worktree add
  existing-branch` + `move in_progress`; main-first uses `claim` — **correct**
- `README.md §3`: mode-split present with concrete commands for each mode — **correct**
- `README.md example prompt`: updated to reference executor.md for mode-split — **correct**
- No doc still says "claim from main" for all modes — **clean**

### Metadata reciprocity check (round 2)

- `AI-012.blocks`: `[AI-014, AI-015]` — **restored**
- `AI-013.blocks`: `[AI-014]` — **restored**
- `AI-014.blocked_by`: `[AI-012, AI-013]` — **restored**
- `python .ai-workflow/scripts/ai_task.py validate` after restore: **passed**

## Requirements coverage

- [x] Manager docs say where task branches are created and what commit is expected
      after creating a draft (`manager.md` "Branch-first task creation" section)
- [x] Human approval docs say how approval is recorded in the task branch
      (manager.md mentions human commits `move AI-NNN ready` + metadata)
- [x] Executor docs describe discovering ready tasks (`list-branches`, `show-branch`)
- [x] Executor docs describe commit implementation + report + validation before submit
- [x] Executor docs describe committing metadata.yaml after submit
- [x] Reviewer docs say review artifacts are committed to the task branch
- [x] Both integration modes documented (README.md §5 Human merges references
      `workflow.integration.mode`; full contract in `.ai-workflow/README.md`)
- [x] Rule preserved: only a human approves `draft → ready`

## Acceptance criteria check

- [x] No role skill tells agents active tasks are managed primarily in `main`
      after claim — executor.md, manager.md, reviewer.md all describe task-branch
      as the authoritative home for active work
- [x] Executor instructions split by mode: branch-first worktree-on-existing-branch
      vs main-first claim-from-main (round 2 fix)
- [x] Executor instructions include commit expectations (mode-split section in executor.md)
- [x] Reviewer instructions include commit expectations (commit discipline block
      in reviewer.md)
- [x] User-facing docs explain active task discovery (`list-branches` in README.md
      Basic Commands and executor workflow step)
- [x] `list-branches` described accurately: groups by merged/unmerged git reachability,
      not by `done` status; `done` task may appear Active until human merges (round 2 fix)
- [x] Out-of-scope metadata edits removed: AI-012/AI-013/AI-014 blocker relationships
      restored to pre-task state (round 2 fix)
- [x] Integration mode examples match config.yaml and AI-012 (README.md §5, full
      contract in `.ai-workflow/README.md`)
- [x] Docs remain concise and usable as agent entrypoints

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: none
- Package changes: none
- board.md: not touched
- Task folders other than AI-014: only AI-014's own report.md, validation.md,
  metadata.yaml changed; AI-012 and AI-013 metadata restored to pre-task state
