# AI-013: Implement branch task discovery commands

## Goal

Implement CLI support for discovering and reporting active tasks that live in
task branches/worktrees instead of only in the current checkout.

## Context

AI-012 defines the branch-first task workflow contract. Under that model,
active tasks may not exist in `main`; they may exist only in unmerged
`ai/<task-id>-<slug>` branches and/or their worktrees. The current `list` and
`board` commands read only the current checkout's `.ai-workflow/tasks/` folder,
which is insufficient for a branch-first control plane.

## Scope

Allowed changes:

- Update `.ai-workflow/scripts/` CLI implementation to discover active task
  metadata from task branches and/or registered worktrees, as defined by
  AI-012.
- Add user-facing commands or flags such as `discover`, `list --branches`, or
  `board --branches` if chosen by the AI-012 contract.
- Read task metadata from git branches using structured data parsing rather
  than brittle text scraping where practical.
- Include branch name, task id, title, status, blocked_by, parent, and PR/local
  integration info in discovery output where available.
- Add focused tests or smoke validation for branch discovery behavior.

Forbidden changes:

- Do not redesign the workflow contract; follow AI-012.
- Do not require a hosted git provider for local discovery.
- Do not auto-merge branches or create PRs unless AI-012 explicitly scopes that
  into this task.
- Do not change user task contracts outside this task's report/validation
  artifacts.
- Do not edit generated `.ai-workflow/board.md` as a source file.

## Requirements

- Discovery must find task branches matching the configured task branch pattern.
- Discovery must handle branches that do not contain a valid task folder without
  crashing.
- Discovery must distinguish tasks already merged into `main` from active
  unmerged branch tasks, if enough git information is available.
- Existing current-checkout `list`, `board`, `validate`, and `history` behavior
  must remain usable for completed history and local tasks.
- Error messages must clearly state when no task branches are found, git is not
  available, or branch metadata is invalid.
- The implementation must work on Windows PowerShell paths.

## Acceptance criteria

- A command or documented flag lists active task metadata from task branches.
- The output shows enough information for an executor/reviewer to choose the
  right task branch/worktree.
- Invalid or non-task `ai/*` branches are skipped or reported cleanly without
  terminating discovery.
- Existing `python .ai-workflow/scripts/ai_task.py list` behavior is not
  regressed unless AI-012 explicitly changes it.
- Tests or smoke validation cover at least one branch with valid task metadata
  and one branch without valid task metadata.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Run the branch discovery command/flag against at least one valid task branch
  or a documented fixture/smoke setup.
- Run any existing CLI tests if present.
- Record exact commands and results in `validation.md`; write `not run` for any
  unavailable validation.

## Notes

Blocked by AI-012 because this task must follow the approved workflow contract.
