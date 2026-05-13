# Execution Report: AI-030

## Summary

Post-merge audit of the `.ai-workflow` implementation. One confirmed regression
(test_cascade.py broken by AI-020), several stale documentation items, and two
legacy commands that are kept but under-labelled. No unsafe or broken workflow
behavior on the happy path. Four follow-up tasks proposed.

---

## 1 — Workflow Verification Matrix

Branch-first happy path traced end-to-end from this repo's current state:

| Step | Command(s) | Observed | Status |
|---|---|---|---|
| Manager creates task | `create` + branch | Task folder created on task branch | PASS |
| Human approves | `approve AI-NNN` | draft → ready, metadata committed | PASS |
| Executor discovers | `list-branches` | Status, title, blockers shown correctly | PASS |
| Executor claims | `git worktree add` + `move in_progress` | Worktree on existing branch | PASS |
| Executor submits | `submit AI-NNN` | in_progress → ready_for_review | PASS |
| Review auto-commit | `review --approve` | Commits metadata/review/decision artifacts | PASS |
| update-from-main | `update-from-main --all` (dry-run) | One active branch current; 19 done/merged correctly skipped | PASS |
| prune-worktrees | `prune-worktrees` (dry-run) | 19 merged worktree candidates listed correctly | PASS |
| validate | `validate` | 0 errors | PASS |

The complete branch-first lifecycle is internally consistent.

**Notable observation — AI-008 and AI-009:**
Both branches show `status: ready_for_review` but are merged into main
(confirmed by `list-branches` and `update-from-main`). They were merged before
the `review --approve` auto-commit flow existed, so their metadata was never
updated to `done`. This is a data inconsistency, not a code defect. Documented
in the follow-up backlog as AI-034.

---

## 2 — Obsolete Command Inventory

### `prepare-worktree`
- **Evidence**: Help text already says "Legacy command: prefer 'claim' for the
  standard executor workflow. Does NOT move the task to in_progress."
  `_worktree.py:310` has the same docstring. Still registered in the main help
  list and prominent in the module docstring examples (`ai_task.py:24-25`).
- **Current status**: Functional, superseded by `claim` + branch-first worktree
  setup. `claim` covers both branch-first and main-first modes.
- **Recommendation**: Keep but de-emphasise. Move the docstring examples to a
  "Legacy" section or remove. Help text label is already correct.

### `migrate`
- **Evidence**: Migrates old `tasks/<status>/<id>/` layout to flat `tasks/<id>/`
  layout. Migration was completed in AI-009. All current tasks are in the flat
  layout — `validate` passes 0 errors. Running `migrate` on this repo today
  produces "0 moved, 0 skipped".
- **Current status**: Live, registered, and in the module docstring. Still useful
  for protocol adopters migrating from the old layout.
- **Recommendation**: Keep but add a "No legacy tasks found — already on flat
  layout" print when nothing to migrate. Consider hiding from default `--help`
  after the transition window passes.

### `move` (low-level)
- **Evidence**: Help text says "(low-level; prefer claim/submit/review)."
  Used legitimately for `--force` transitions (e.g. reverting
  `changes_requested → in_progress`). Module docstring shows `move AI-001 ready`
  (line 8) which is now superseded by `approve`.
- **Recommendation**: Keep. The `--force` path is genuinely useful and has no
  high-level replacement. Update the module docstring to replace
  `move AI-001 ready` with `approve AI-001`.

### `list`
- **Evidence**: In branch_first mode, prints an upfront warning and advises
  `list-branches`. Still returns done-task history from main checkout correctly.
- **Recommendation**: Keep. Warning is correct and informative.

### `board`, `human-request-changes`, `install-plan`
- **Recommendation**: Keep. All fully functional and correctly described.

---

## 3 — Stale Documentation Inventory

| File | Location | Issue | Severity |
|---|---|---|---|
| `ai_task.py` | Lines 8, 24-25 | Module docstring shows `move AI-001 ready` (superseded by `approve`) and `prepare-worktree` examples without a "legacy" label | Low |
| `config.yaml` | Line 67 | Comment says `main_first` is "current default" — technically correct for the option's config-level fallback, but this repo runs `branch_first`; the phrasing is misleading | Low |
| `AGENTS.md` | Line 20 | Comment `list  # main-first / history` is accurate but the primary discovery command in branch_first is `list-branches`; worth making `list-branches` the first example | Low |
| `.ai-workflow/README.md` | Lines 149, 180 | Shows `move AI-001 ready` and `migrate` as quickstart examples without legacy labels | Low |

All stale docs are low severity — they do not cause incorrect behavior.

---

## 4 — Regression: test_cascade.py (6/8 tests failing)

**Severity: High** — 6 out of 8 tests in `test_cascade.py` fail due to AI-020's
auto-commit feature.

**Root cause**: AI-020 wired `_commit_review_artifacts()` into `review_task()`.
`test_cascade.py:50-52` has a `_approve()` helper:

```python
def _approve(task_id: str) -> None:
    args = argparse.Namespace(task_id=task_id, approve=True, changes_requested=False)
    review_task(args)
```

`no_commit` is absent so `getattr(args, "no_commit", False)` returns `False`,
causing `_commit_review_artifacts` to call `git add` in a temp directory that
has no git repo:

```
SystemExit: git add failed: fatal: not a git repository (or any of the parent
directories): .git
```

**Fix**: Add `no_commit=True` to the Namespace in `test_cascade.py`:

```python
def _approve(task_id: str) -> None:
    args = argparse.Namespace(
        task_id=task_id, approve=True, changes_requested=False, no_commit=True
    )
    review_task(args)
```

This is a one-line fix proposed as follow-up task AI-031.

---

## 5 — Refactor Opportunities

| Item | Benefit | Risk |
|---|---|---|
| Fix test_cascade.py `_approve` helper (`no_commit=True`) | Restores 6 broken tests | None — flag already exists |
| Move `prepare-worktree` / `move AI-001 ready` out of main docstring examples | Reduces confusion for new users | None |
| Add "nothing to migrate" detection to `migrate` | Self-documenting | Minimal |
| Reconcile AI-008 / AI-009 metadata to `done` | Cleans up `list-branches` output | Human decision required |

---

## 6 — Prioritized Follow-up Backlog

| ID | Title | Priority | Effort | Blocked by |
|---|---|---|---|---|
| AI-031 | Fix test_cascade.py regressions (add `no_commit=True` to `_approve` helper) | High | Tiny | — |
| AI-032 | Clean up ai_task.py module docstring legacy examples (`move ready` → `approve`, label `prepare-worktree` as legacy) | Low | Small | — |
| AI-033 | Add "nothing to migrate" detection to `migrate` command | Low | Small | — |
| AI-034 | Reconcile AI-008 and AI-009 branch metadata to `done` | Low | Tiny | Human decision |

AI-032 and AI-033 are independent and could be done in one PR.

---

## Changed files

None. Audit task — `report.md` and `validation.md` only.

## Assumptions

- AI-018 was a prior audit covering AI-003 to AI-017. This audit focuses on
  AI-019 through AI-029 and the merged post-branch-first state.
- test_cascade.py failures are a verified regression, not an environmental issue.
  Reproduced by running `python .ai-workflow/scripts/test_cascade.py` directly
  in the worktree.

## Known risks

Low. Audit-only task. The one regression (test_cascade.py) is documented and
proposed as AI-031; it does not affect CLI behavior, only the test suite.
