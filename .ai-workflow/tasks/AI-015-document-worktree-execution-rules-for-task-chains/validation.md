# Validation: AI-015

## CLI validation

All commands run from the task worktree at
`C:\Projects\ai_workflow.worktrees\AI-015-document-worktree-execution-rules-for-task-chains`.

### validate

```
python .ai-workflow/scripts/ai_task.py validate
```
Result: **Validation passed.**

### Diff scope check

```
git diff --stat HEAD
```
Result: Only `.ai-workflow/README.md` and task artifact metadata changed.
No CLI scripts, no Unity files, no board.md. **Passed.**

### AI-012 consistency check

Manual review of the new "Task chain execution rules" section against the
AI-012 branch-first contract (`## Branch-first workflow contract` in README.md):

- "One executable child task = one branch/worktree" is consistent with the
  lifecycle diagram (each task gets its own task branch). **No contradiction.**
- The serialization/blocking guidance is consistent with the `blocked_by`
  relationship semantics. **No contradiction.**
- Parallel work exception (disjoint scopes + explicit approval) does not
  conflict with branch-first mode — branching strategy is orthogonal. **No contradiction.**

## Requirements coverage

- [x] Docs explain "one executable child task = one branch/worktree"
      (§ "Parent tasks as coordination artifacts")
- [x] Docs explain umbrella parent tasks are coordination artifacts unless
      their contract specifies otherwise (§ "Parent tasks as coordination artifacts")
- [x] Docs explain recommended order: merge blocker first; start dependent
      from updated main; avoid parallel when outputs overlap (§ "Recommended
      execution order for blocked chains")
- [x] Docs explain exception for parallel work: disjoint write scope + explicit
      approval + defined merge strategy (§ "Exception: approved parallel work")
- [x] Docs do not contradict AI-012 branch-first contract

## Acceptance criteria check

- [x] New user can determine whether AI-011 needs its own branch: table in
      "Parent tasks as coordination artifacts" shows AI-011 has no concrete
      deliverables → no branch needed
- [x] New user can determine correct execution order for AI-012–AI-015:
      "Worked example" under "Recommended execution order" shows the
      parallel-then-serial ordering with rationale
- [x] Docs explicitly warn against starting a blocked task before its blocker
      is merged (Warning block in "Recommended execution order")
- [x] No implementation files changed (diff scope check passed)

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: none
- Package changes: none
- board.md: not touched
- Task folders other than AI-015: none
