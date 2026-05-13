# Execution Report: AI-020

## Summary

Made `review --approve` and `review --changes-requested` auto-commit task artifacts to the current branch by default. A `--no-commit` flag preserves the previous local-only behavior.

`_commit_review_artifacts(task_dir, task_id, decision)` is a new helper in `_tasks.py`:
- Stages only the three known task-folder files (`metadata.yaml`, `review.md`, `decision.yaml`) — files that do not exist are skipped, so unrelated dirty files are never touched.
- Checks `git diff --cached --quiet` before committing; skips if nothing new is staged.
- On `git add` or `git commit` failure, raises with a message that tells the reviewer which files were written and the exact manual commit command to recover.

`review_task()` calls the helper after `generate_board()` unless `args.no_commit` is set.

## Changed files

- `.ai-workflow/scripts/_tasks.py` — added `subprocess` and `repo_root` imports; added `_commit_review_artifacts`; wired it into `review_task()` with `no_commit` guard.
- `.ai-workflow/scripts/ai_task.py` — added `--no-commit` flag to the `review` subparser.
- `.ai-workflow/scripts/test_review.py` — new test file: 12 tests covering helper behavior, approve/changes-requested commit, no-commit skip, and status guards.
- `.ai-workflow/skills/reviewer.md` — updated "Commit discipline" section to document auto-commit and `--no-commit` escape hatch.

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python -m unittest test_review` — 12/12 passed
- Forbidden file check: passed — no forbidden files modified

## Assumptions

- The command runs from the task worktree (or main checkout for main-first), so `repo_root()` returns the correct root for `git add` and `git commit`.
- `decision.yaml` staging is included in the commit scope even though `review_task()` does not currently write it — the file may be written by the reviewer manually before running `review`. Skipping non-existent files handles the case where it was not written.

## Known risks

- Low. If the reviewer runs `review` from a directory whose `repo_root()` differs from the worktree containing the task folder (unusual but possible in multi-worktree setups), the relative path computation will raise a clear `SystemExit`. The reviewer is told to commit manually.
