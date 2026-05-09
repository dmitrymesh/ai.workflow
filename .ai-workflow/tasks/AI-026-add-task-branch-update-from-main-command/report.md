# Execution Report: AI-026

## Summary

Added `update-from-main` CLI command that merges `main` into active task branch
worktrees. Default mode is dry-run; `--apply` performs the merges. Supports
targeting a single task by ID or all eligible active local worktrees via `--all`.

## Changed files

- `.ai-workflow/scripts/_update_from_main.py` — new module: full command implementation
- `.ai-workflow/scripts/test_update_from_main.py` — 29 focused unit tests (all passing)
- `.ai-workflow/scripts/ai_task.py` — import `update_from_main`, register `update-from-main` subparser, update module docstring
- `.ai-workflow/README.md` — added `update-from-main` section; corrected conflict wording
- `.ai-workflow/skills/executor.md` — added "Keeping the task branch current" note with usage

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python -m unittest test_update_from_main -v` — 29/29 tests passed
- `update-from-main --help` — subcommand registered and described correctly
- `update-from-main --all` live dry-run: 5 would-update, 1 dirty (AI-026), 2 no-worktree, 2 merged into main, 10 skipped-inactive (done) — all correct, no crash
- `update-from-main AI-022` dry-run: correctly targeted single branch with 14 pending commits
- `git diff --name-only main...HEAD` — only task folder + five implementation files; no forbidden files

## Assumptions

- The command operates on the local `main` branch only; callers should fetch before running if they want remote changes incorporated.
- `_discovery.py` private helpers (`_run_git`, `_list_local_branches`, `_parse_workflow_config`, etc.) are stable enough to import directly, consistent with the approach used in other modules in this repo.
- No `_approve.py` (AI-021) import was used; the branch-lookup logic is re-implemented here since AI-021 is not yet merged to main.

## Known risks

- If `main` diverges from `origin/main` and users don't fetch before running, the merge may miss remote commits. This is documented as expected behavior ("fetch first").
- `git rev-list branch..main --count` compares local branch HEADs only; does not account for remote-tracking refs unless the user has fetched.

## Review fixes (round 4)

**Blocking issue — wrong fallback for missing `workflow.mode`:**
Changed `cfg.get("mode", "branch_first")` to `cfg.get("mode", "main_first")`.
A project with no `workflow.mode` key now fails clearly with the unsupported-mode
error rather than silently running in the wrong context. The real `config.yaml`
has `mode: branch_first` explicitly, so the live smoke test is unaffected.

**New test:** `test_empty_config_rejected` — mocks `_parse_workflow_config`
returning `{}` and asserts `SystemExit` with non-zero code. 29/29 pass.
