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
  — status, branch, blocked_by fields (managed by claim/submit workflow)
- `.ai-workflow/tasks/AI-013-implement-branch-task-discovery-commands/task.md`
  — copied from main checkout by claim
- `.ai-workflow/tasks/AI-013-implement-branch-task-discovery-commands/report.md`
  — this file
- `.ai-workflow/tasks/AI-013-implement-branch-task-discovery-commands/validation.md`
  — updated with full smoke coverage including branch-without-metadata test

## Implementation notes

### `list-branches`

Scans local and/or remote branches (per `workflow.discovery.scope`) matching
`workflow.discovery.branch_prefix` (default `ai/`). For each branch:
- Reads `metadata.yaml` via `git show <branch>:<path>` (no checkout required).
- Distinguishes merged (via `git branch --merged main`) from active.
- Handles legacy status-subdirectory layout by recursing one level when a
  top-level task directory name is a known status name (`done`, `ready`, etc.).
- Reports "no valid task metadata — skipped" for branches where metadata cannot
  be found, then continues without terminating discovery.

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
- `python .ai-workflow/scripts/ai_task.py list-branches` — full metadata shown
  for all branches; flat layout (AI-012), legacy layout (AI-008), active vs merged
  classification all correct
- Smoke: created `ai/AI-099-smoke-no-task-metadata` branch (no matching task
  folder), ran `list-branches` — showed "no valid task metadata — skipped"
  without crash; deleted temp branch
- `python .ai-workflow/scripts/ai_task.py show-branch AI-012` — full metadata shown
- `python .ai-workflow/scripts/ai_task.py show-branch AI-008` — legacy layout works
- `python .ai-workflow/scripts/ai_task.py show-branch AI-999` — clean "not found" message
- `python .ai-workflow/scripts/ai_task.py list` — existing behavior unchanged
- See `validation.md` for full output and acceptance criteria coverage

## Assumptions

- Implemented in the task worktree on branch
  `ai/AI-013-implement-branch-task-discovery-commands` per executor workflow.
- The `workflow.mode` config key is not checked at runtime; both `main_first`
  and `branch_first` projects benefit from these commands.
- `git branch --merged main` is used for merge detection; if the default branch
  is not named `main`, branches may be misclassified but discovery still works.
- All task artifact changes (metadata.yaml, report.md, validation.md) are committed
  to the task branch before submission so the committed branch state is the
  authoritative source of review-ready status.

## Known risks

- If a repository uses a default branch other than `main`, merge detection will
  report all branches as active. A future task could make this configurable via
  `workflow.discovery.base_branch`.
- Remote branch discovery (`scope: remote` or `both`) requires network access.
  No explicit pre-fetch is performed; stale remote refs may show outdated metadata.
