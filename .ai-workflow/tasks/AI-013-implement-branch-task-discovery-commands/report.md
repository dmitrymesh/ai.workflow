# Execution Report: AI-013

## Summary

Implemented `list-branches` and `show-branch` CLI commands for branch-first task
discovery, as specified by the AI-012 workflow contract. A new `_discovery.py`
module was created and `ai_task.py` was updated to wire in the two subcommands.

Discovery reads task metadata directly from git branch objects (no checkout
required), supports both the current flat task layout and the legacy
status-subdirectory layout, and handles invalid or non-task `ai/*` branches
gracefully without crashing.

## Changed files

- `.ai-workflow/scripts/_discovery.py` — new module (branch discovery logic)
- `.ai-workflow/scripts/ai_task.py` — added `list-branches` and `show-branch`
  subcommands and import; updated module layout docstring
- `.ai-workflow/tasks/AI-012-design-branch-first-task-workflow-contract/metadata.yaml`
  — removed AI-013 from `blocks` (blocker relationship cleared; AI-012 is done)
- `.ai-workflow/tasks/AI-013-implement-branch-task-discovery-commands/metadata.yaml`
  — status → in_progress, branch set, blocked_by cleared
- `.ai-workflow/tasks/AI-013-implement-branch-task-discovery-commands/task.md`
  — copied from main checkout by claim

## Implementation notes

### `list-branches`

Scans local and/or remote branches (per `workflow.discovery.scope`) matching
`workflow.discovery.branch_prefix` (default `ai/`). For each branch:
- Reads `metadata.yaml` via `git show <branch>:<path>` (no checkout required).
- Distinguishes merged (via `git branch --merged main`) from active.
- Handles legacy status-subdirectory layout by recursing one level when a
  top-level task directory name is a known status name (`done`, `ready`, etc.).
- Reports "no valid task metadata" for branches where metadata cannot be found,
  then continues without terminating discovery.

### `show-branch AI-NNN`

Shows full task metadata for a specific task ID by finding its branch and reading
`metadata.yaml` from that branch. Reports a clean error when no matching branch
is found or git is unavailable.

### Config parsing

`_core.parse_simple_yaml` flattens nested YAML keys, so `workflow.discovery.*`
values are not accessible through `load_config()`. `_discovery.py` implements
its own indent-aware parser (`_parse_workflow_config`) that handles the two-level
`workflow:` hierarchy, mirroring the approach used in `_parse_agents_from_config`
in `ai_task.py`.

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python .ai-workflow/scripts/ai_task.py list-branches` — lists 5 local task
  branches, showing full metadata for each (flat and legacy layouts both work)
- `python .ai-workflow/scripts/ai_task.py show-branch AI-012` — full metadata
  for AI-012 shown correctly
- `python .ai-workflow/scripts/ai_task.py show-branch AI-008` — full metadata
  for AI-008 shown correctly (legacy layout)
- `python .ai-workflow/scripts/ai_task.py show-branch AI-999` — prints clean
  "No task branch found" message, no crash
- `python .ai-workflow/scripts/ai_task.py list` — existing behavior unchanged

## Assumptions

- Implemented in the task worktree on branch
  `ai/AI-013-implement-branch-task-discovery-commands` per executor workflow.
- The `workflow.mode` config key is not checked at runtime; both `main_first`
  and `branch_first` projects benefit from these commands.
- `git branch --merged main` is used for merge detection; if the default branch
  is not named `main`, the "merged" flag will be inaccurate but discovery will
  still work (branches appear in "Active" instead of "Merged").
- The AI-013 branch itself appears in "Merged" in list output before any commits
  are added (branch tip equals main's HEAD). Once implementation commits exist,
  it will correctly appear as "Active".

## Known risks

- If a repository uses a default branch other than `main`, merge detection will
  report all branches as active. A future task could make this configurable via
  `workflow.discovery.base_branch`.
- Remote branch discovery (`scope: remote` or `both`) requires network access.
  No explicit pre-fetch is performed; stale remote refs may show outdated metadata.
