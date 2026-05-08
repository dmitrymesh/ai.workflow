# Execution Report: AI-017

## Summary

Fixed `show` command to read task status from `metadata.yaml` instead of the
parent folder name. In the flat task layout, `task_dir.parent.name` is always
`tasks`, so `show` was printing `status: tasks` for every flat-layout task.

One-line fix in `_relationships.py`: changed `task_dir.parent.name` to
`meta.get('status') or task_dir.parent.name`. The `or` fallback preserves
correct behaviour for legacy status-directory tasks where `metadata.yaml`
may not carry a `status` field.

## Changed files

- `.ai-workflow/scripts/_relationships.py` — fix `show_task` status source
  (line 147: `task_dir.parent.name` → `meta.get('status') or task_dir.parent.name`)
- `.ai-workflow/scripts/test_show.py` — new focused tests for `show` status output

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` → **Validation passed.**
- `python -m unittest test_show test_cascade -v` (from `scripts/`) → **11/11 passed.**
- `python .ai-workflow/scripts/ai_task.py show AI-016` → `status: done` ✓
- `python .ai-workflow/scripts/ai_task.py show AI-011` → `status: done` ✓
- `python .ai-workflow/scripts/ai_task.py list` → AI-017 listed under `in_progress` ✓

## Dogfood note

Workflow steps used: branch already created and set to `ready` by the manager;
executor moved it to `in_progress` via `move`, implemented, committed, then
`submit` to `ready_for_review`.

Friction observed:
- The task was delivered with `status: ready` on the branch even though
  `show-branch` reported it as `draft`. The discrepancy is because `show-branch`
  reads from the committed branch state while the working tree differed. No
  workflow blocker but worth noting for branch-first consistency.
- The Bash shell CWD drifted to `.ai-workflow/scripts/` after an earlier `cd`
  in a prior task session. Git commands then failed until an explicit
  `cd /c/Projects/ai_workflow` was added. Suggestion: always run CLI commands
  from the project root.

## Assumptions

- The `or task_dir.parent.name` fallback is retained so legacy tasks (those in
  status subdirectories without a `status` field in `metadata.yaml`) continue
  to display a sensible value, consistent with all other status-reading code in
  `_tasks.py` and `_worktree.py`.

## Known risks

- None. The fix touches a display-only code path and does not affect any
  mutation logic or transition validation.
