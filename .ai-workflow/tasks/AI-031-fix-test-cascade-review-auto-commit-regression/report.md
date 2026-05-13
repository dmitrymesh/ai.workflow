# Execution Report: AI-031

## Summary

Added `no_commit=True` to the `_approve()` helper in `test_cascade.py`. The
helper calls `review_task()` from a temp directory that has no git repo; AI-020
introduced `_commit_review_artifacts()` into `review_task()`, which unconditionally
attempted `git add` and failed with "not a git repository". The `no_commit` flag
already existed — it just wasn't set in the test helper.

No production code changed.

## Changed files

- `.ai-workflow/scripts/test_cascade.py` — added `no_commit=True` to the
  `argparse.Namespace` in `_approve()`.

## Validation performed

- `python .ai-workflow/scripts/test_cascade.py` — **8/8 passed** (was 2/8)
- `python .ai-workflow/scripts/test_review.py` — **14/14 passed** (unchanged)
- `python .ai-workflow/scripts/ai_task.py validate` — **passed**
- `git diff --name-only main...HEAD` — only `test_cascade.py` and task folder

## Assumptions

- The `no_commit` guard (`getattr(args, "no_commit", False)`) in `_tasks.py`
  already handles the absent attribute gracefully; the test-only fix is
  sufficient without touching production code.

## Known risks

None.
