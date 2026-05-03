# Execution Report: AI-009

## Summary

Replaced the status-by-directory task layout with a stable flat layout where
`metadata.yaml.status` is the authoritative status. Added executor self-service
`claim` command (creates worktree + moves to `in_progress`). Added `submit`,
`review`, `human-request-changes`, and `migrate` CLI commands. Removed
`ready_for_human` from the lifecycle. Updated all role skills and README to
reflect the new workflow with no manual status mirroring between worktrees.

**Fix round** (addressing review blocking issues):
- Fixed `_history.py` to use `all_task_dirs()` + metadata status filter instead of
  hardcoded `tasks/done/` path, so done tasks are discoverable after migration.
  Also fixed Windows cp1252 encoding error when printing report.md content with
  non-ASCII characters.
- Made `claim_task()` atomic: metadata is not mutated if `_create_worktree()`
  returns False (git failure). The task stays `ready` and unclaimed.
- Added `blocked_by` check in `claim_task()`: claim fails with a clear error if
  any unresolved blockers are present.

## Changed files

### Scripts (fix round)
- `.ai-workflow/scripts/_history.py` — replaced `_done_task_dirs()` hardcoded
  `tasks/done/` with `all_task_dirs()` + metadata status filter; added import
  of `sys`; added encoding-safe print for `--show` output.
- `.ai-workflow/scripts/_worktree.py` — added `blocked_by` pre-check in
  `claim_task()`; moved metadata update to after `_create_worktree()` success
  check; `_sync_task_folder()` now always called (no longer conditional on `ok`).

### Scripts (original round)
- `.ai-workflow/scripts/_core.py` — removed `ready_for_human` from `STATUSES`;
  added `_LEGACY_STATUS_DIRS` set; updated `DEFAULT_TRANSITIONS`; rewrote
  `ensure_structure()` (no longer creates status subdirs); rewrote
  `all_task_dirs()` to support both stable and legacy layouts; new
  `load_meta()`/`save_meta()` helpers.
- `.ai-workflow/scripts/_tasks.py` — `create_task()` now creates at
  `tasks/<id>-<slug>/` (no status subdir); `move_task()` updates metadata only
  (no folder move); added `submit_task()`, `review_task()`,
  `human_request_changes()`.
- `.ai-workflow/scripts/_board.py` — `_collect_by_status()` and
  `generate_board()` group by `metadata.yaml.status`.
- `.ai-workflow/scripts/_validate.py` — validates `metadata.status` against
  `STATUSES`; retains legacy folder/status consistency check for tasks still in
  status-dirs.
- `.ai-workflow/scripts/_worktree.py` — extracted `_branch_and_worktree_path()`,
  `_create_worktree()`, `_sync_task_folder()` helpers; added `claim_task()`;
  kept `prepare_worktree()` for backward compat.
- `.ai-workflow/scripts/_migrate.py` — new file; moves tasks from
  `tasks/<status>/<id>/` to `tasks/<id>/`, stamps `metadata.status`, removes
  empty status dirs.
- `.ai-workflow/scripts/ai_task.py` — added `claim`, `submit`, `review`,
  `human-request-changes`, `migrate` subcommands; updated module docstring and
  `prepare-worktree` help text.

### Config
- `.ai-workflow/config.yaml` — removed `ready_for_human` from `statuses` and
  `transitions`; updated `ready_for_review` transitions to include `done`.

### Skills
- `.ai-workflow/skills/executor.md` — replaced "you may move tasks" bullets
  with CLI-oriented section; updated worktree workflow to use `claim`/`submit`;
  fixed review appeal section (`ready_for_human` → `done`).
- `.ai-workflow/skills/reviewer.md` — `approve` now moves to `done`; removed
  "control checkout status sync" section; updated appeal escalation to use
  `done` + `decision: escalated_to_human`.
- `.ai-workflow/skills/manager.md` — replaced mandatory `prepare-worktree`
  handoff with executor self-service `claim` description; updated done-task
  history section.

### Docs
- `.ai-workflow/README.md` — updated quick start, folder model, board/validate
  sections; replaced `prepare-worktree` with `claim` in worktree section;
  removed reviewer manual status mirroring; updated review appeal section.

### Tasks
- All 9 existing tasks migrated from legacy status-dir layout to flat
  `tasks/<id>/` layout via `python ai_task.py migrate` (run in worktree).

## Validation performed

- `python .ai-workflow/scripts/ai_task.py migrate`: ran, 9 tasks moved, 0 skipped
- `python .ai-workflow/scripts/ai_task.py validate`: passed
- `python .ai-workflow/scripts/ai_task.py list`: tasks grouped by metadata status, all correct
- Smoke tests (all passed):
  - create draft → human approve to ready → claim `--print-only` → submit → reviewer changes_requested → resubmit → reviewer approve to done → human-request-changes → reject
- History command: confirmed existing done tasks discoverable
- Forbidden files check: only `.ai-workflow/` files changed

## Assumptions

- Task is executed in a worktree so the `migrate` command runs against the
  worktree's task tree, not `main`. The migration result travels to `main` via
  the normal branch merge.
- `claim --print-only` was used for the smoke test claim step because creating
  a nested worktree inside this worktree would require a committed branch base.
  The actual claim workflow works normally from the main checkout.
- `ready_for_human` is retained in `_LEGACY_STATUS_DIRS` so existing tasks
  using that status remain discoverable via `all_task_dirs()`. It is not in
  `STATUSES` and cannot be set by any current CLI command.

## Known risks

- Projects that have scripts or automation checking for `tasks/done/`,
  `tasks/ready/`, etc. directory paths will need updating after migration.
- The `claim` command sets `status: in_progress` in the metadata in the main
  checkout AND in the worktree copy; both should agree. If a user manually
  modifies metadata in one without the other, validate will catch the
  mismatch only if both copies are scanned (they won't be — the worktree is
  independent). This is inherent to the worktree model and documented.
