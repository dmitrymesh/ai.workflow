# Validation: AI-013

## CLI validation

All commands run from the task worktree at
`C:\Projects\ai_workflow.worktrees\AI-013-implement-branch-task-discovery-commands`.

### validate

```
python .ai-workflow/scripts/ai_task.py validate
```
Result: **Validation passed.**

### list-branches — valid task branch (flat layout)

```
python .ai-workflow/scripts/ai_task.py list-branches
```
Result: Listed 5 local branches. AI-009, AI-010, AI-012, AI-013 (flat layout)
showed full metadata. AI-008 (legacy layout) also showed full metadata after
legacy subdirectory support was added.

Sample output:
```
Task branches (branch-first discovery)
============================================================
scope=local  prefix=ai/

Active (unmerged)
-----------------
  (none)

Merged into main
----------------
  ai/AI-008-add-executor-review-appeal-step
    id=AI-008  status=ready_for_review  title=Add executor review appeal step
    parent=-  blocked_by=-  pr=-
  ai/AI-012-design-branch-first-task-workflow-contract
    id=AI-012  status=done  title=Design branch-first task workflow contract
    parent=AI-011  blocked_by=-  pr=-
  ...
```

### show-branch — valid task branch

```
python .ai-workflow/scripts/ai_task.py show-branch AI-012
```
Result: Full metadata shown (id, title, status, risk, area, parent, blocked_by, pr,
task branch). **Passed.**

### show-branch — legacy layout

```
python .ai-workflow/scripts/ai_task.py show-branch AI-008
```
Result: Full metadata shown for the AI-008 branch (legacy status-subdir layout).
**Passed.**

### show-branch — non-existent task ID (no valid metadata branch)

```
python .ai-workflow/scripts/ai_task.py show-branch AI-999
```
Result: `No task branch found for AI-999 (scope=local, prefix=ai/).` — clean
message, no crash. **Passed.**

### Regression: existing list command

```
python .ai-workflow/scripts/ai_task.py list
```
Result: Existing behavior unchanged. All tasks listed by status. **Passed.**

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: no forbidden files were changed (only scripts/ and
  task artifacts)
- Package changes: none

## Notes

- No unit test framework exists for the scripts. Validation is smoke-based.
- Acceptance criteria coverage:
  - [x] Command lists active task metadata from task branches
  - [x] Output sufficient for executor/reviewer to choose a task branch
  - [x] Invalid/non-task branches skipped cleanly (AI-999 test)
  - [x] Valid task branch with metadata (AI-012)
  - [x] Branch without valid metadata handled (AI-999 non-existent)
  - [x] Existing `list` behavior not regressed
