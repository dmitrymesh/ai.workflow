# Review: AI-026

## Decision

changes_requested

## Blocking Issues

1. `.ai-workflow/scripts/_update_from_main.py:231-238` implements `--all` by scanning every local task branch with the configured prefix and passing each one to `_process_branch`. `_process_branch` only skips branches already merged into `main`; it never reads task metadata or filters by active status. The task contract requires bulk updates to target "active unmerged task branches" and forbids updating merged task branches, but a reviewed `done` or `rejected` branch that has not yet been merged into `main` is not active and would still be eligible for merge if it has a local worktree. Filter `--all` selection by metadata status (`draft`, `ready`, `in_progress`, `ready_for_review`, `changes_requested`) and add tests for done/rejected unmerged branches.

2. `.ai-workflow/scripts/_update_from_main.py:202-219` does not check `workflow.mode`. The task requires the command to work in `branch_first` and, if unsupported in `main_first`, report that clearly. In a `main_first` project the command currently proceeds with branch scanning and may produce misleading "no branch" or empty-scan output instead of a clear unsupported-mode error. Add an explicit workflow mode check and focused test coverage.

## Non-Blocking Issues

- `.ai-workflow/scripts/_update_from_main.py:236-238` continues processing later branches after a conflict in `--all` mode and only exits nonzero at the end. The README says the command "stops" on conflicts. Consider either stopping immediately after the first conflict in apply mode or updating the wording if continuing to summarize other branches is intentional and safe.

## Scope Check

The changed files are in the allowed CLI, documentation, tests, and task artifact scope. No forbidden file patterns were changed.

## Acceptance Criteria Check

- Single-task dry-run/apply path is implemented.
- `--all` exists and is explicit, but it does not yet limit selection to active task statuses.
- Dirty worktrees are skipped.
- Already-current branches are reported.
- Conflicts are reported and return nonzero, but the bulk command does not currently stop immediately.
- Merged branches are skipped.
- README and executor guidance document the workflow.
- Focused tests exist, but they do not cover status-based active filtering or `main_first` unsupported behavior.
- `validate` passes.

## Test Quality

I ran `python .ai-workflow/scripts/ai_task.py validate`, `python -m unittest test_update_from_main -v`, `update-from-main --help`, `update-from-main --all` dry-run, and `git diff --check main...HEAD`. The existing unit tests pass, but they miss the two blocking contract cases above.

## Required Fixes

- Filter `--all` candidates to active task statuses by reading branch metadata, and skip/report `done` and `rejected` unmerged task branches.
- Add tests for `--all` excluding unmerged `done` and `rejected` branches.
- Add an explicit `workflow.mode` check so `main_first` reports unsupported clearly, plus a test for that path.
