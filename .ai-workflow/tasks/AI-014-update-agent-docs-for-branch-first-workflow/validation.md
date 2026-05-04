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
- [x] Executor instructions include commit expectations (steps 5–7 in executor.md)
- [x] Reviewer instructions include commit expectations (commit discipline block
      in reviewer.md)
- [x] User-facing docs explain active task discovery (`list-branches` in README.md
      Basic Commands and executor workflow step)
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
- Task folders other than AI-014: only metadata.yaml relationship fields updated
