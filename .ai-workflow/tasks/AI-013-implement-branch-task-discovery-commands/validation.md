# Validation: AI-013

## CLI validation

All commands run from the task worktree at
`C:\Projects\ai_workflow.worktrees\AI-013-implement-branch-task-discovery-commands`.

### validate

```
python .ai-workflow/scripts/ai_task.py validate
```
Result: **Validation passed.**

### list-branches — valid task branch (flat layout, AI-012)

```
python .ai-workflow/scripts/ai_task.py list-branches
```
Result: Lists all local `ai/*` branches, showing full metadata for each.
AI-012 (flat layout, done), AI-008 (legacy status-subdir layout), AI-009,
AI-010 all show correct id/status/title/parent/blocked_by. **Passed.**

### list-branches — branch without valid task metadata

Smoke fixture: created a local branch `ai/AI-099-smoke-no-task-metadata`
(no `AI-099` task folder exists in `.ai-workflow/tasks/`), then ran
`list-branches`, then deleted the branch.

```
git branch ai/AI-099-smoke-no-task-metadata
python .ai-workflow/scripts/ai_task.py list-branches
git branch -d ai/AI-099-smoke-no-task-metadata
```

Output excerpt:
```
Active (unmerged)
-----------------
  ai/AI-099-smoke-no-task-metadata
    (no valid task metadata — skipped)
```

Branch was discovered, reported cleanly without crashing, and discovery
continued to the remaining branches. **Passed.**

### show-branch — valid task branch

```
python .ai-workflow/scripts/ai_task.py show-branch AI-012
```
Result: Full metadata shown (id, title, status, risk, area, parent, blocked_by,
pr, task branch). **Passed.**

### show-branch — legacy layout (AI-008)

```
python .ai-workflow/scripts/ai_task.py show-branch AI-008
```
Result: Full metadata shown for AI-008 (legacy status-subdir layout). **Passed.**

### show-branch — non-existent task ID

```
python .ai-workflow/scripts/ai_task.py show-branch AI-999
```
Result: `No task branch found for AI-999 (scope=local, prefix=ai/).` — clean
message, no crash. **Passed.**

Note: this tests "no branch found for the given task ID", not "branch exists but
has no task metadata". That scenario is covered by the `ai/AI-099-smoke-no-task-metadata`
test under `list-branches` above.

### Regression: existing list command

```
python .ai-workflow/scripts/ai_task.py list
```
Result: Existing behavior unchanged — all tasks listed by status. **Passed.**

## Acceptance criteria coverage

- [x] A command lists active task metadata from task branches — `list-branches`
- [x] Output shows enough info to choose a task branch/worktree — id, status,
      title, parent, blocked_by, pr shown per branch
- [x] Invalid/non-task `ai/*` branches skipped cleanly — `ai/AI-099-smoke-no-task-metadata`
      test demonstrates graceful skip with no crash
- [x] Valid task branch with metadata — AI-012 (flat), AI-008 (legacy)
- [x] Branch without valid task metadata handled — `ai/AI-099-smoke-no-task-metadata`
- [x] Existing `list` behavior not regressed

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: no forbidden files were changed (only scripts/ and
  task artifacts)
- Package changes: none
