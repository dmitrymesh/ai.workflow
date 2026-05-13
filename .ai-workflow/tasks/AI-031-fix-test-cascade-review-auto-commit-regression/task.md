# AI-031: Fix test cascade review auto-commit regression

## Goal

Fix the `test_cascade.py` regression introduced by review artifact auto-commit
so the cascade tests can run in their temporary non-git test directory again.

## Context

`AI-030` verified that the branch-first happy path works, but found one
confirmed test regression:

- `python .ai-workflow/scripts/test_cascade.py` fails 6/8 tests.
- The failures occur because `review_task()` now auto-commits review artifacts
  by default.
- `test_cascade.py` calls `review_task()` from a temporary task directory that
  is not a git repository.
- The test helper omits `no_commit=True`, so `_commit_review_artifacts()` tries
  to run `git add` and exits with `fatal: not a git repository`.

Relevant files:

- `.ai-workflow/scripts/test_cascade.py`
- `.ai-workflow/scripts/_tasks.py` (read-only context unless a test-only fix is
  demonstrably insufficient)
- `.ai-workflow/tasks/AI-030-audit-merged-workflow-and-obsolete-cli/report.md`

## Scope

Allowed changes:

- Update the cascade test helper so tests that call `review_task()` in a
  temporary non-git directory pass `no_commit=True`.
- Add or adjust focused tests only if needed to preserve the intended
  auto-commit behavior.
- Update this task's `report.md` and `validation.md`.

Forbidden changes:

- Do not change production `review_task()` behavior unless the test-only fix is
  impossible.
- Do not weaken review auto-commit in normal branch-first workflow.
- Do not alter task lifecycle transitions, cascade semantics, or relationship
  behavior.
- Do not change workflow docs or unrelated tests.
- Do not modify Unity project files, packages, project settings, or `.meta`
  files.

## Requirements

- `test_cascade.py` must pass when run directly.
- Existing review auto-commit tests must continue to pass.
- The fix must preserve the distinction between production review behavior
  (commit by default) and tests that intentionally run without git.
- The code diff must stay limited to the failing test surface unless a broader
  issue is discovered and documented.

## Acceptance criteria

- `python .ai-workflow/scripts/test_cascade.py` passes.
- `python .ai-workflow/scripts/test_review.py` passes.
- `python .ai-workflow/scripts/ai_task.py validate` passes.
- `git diff --name-only main...HEAD` shows only in-scope files and this task's
  task folder.
- `report.md` states whether production code was changed. If production code
  was changed, it explains why the test-only fix was insufficient.

## Validation

Required:

- `python .ai-workflow/scripts/test_cascade.py`
- `python .ai-workflow/scripts/test_review.py`
- `python .ai-workflow/scripts/ai_task.py validate`
- `git diff --name-only main...HEAD`

## Notes

This task implements the highest-priority follow-up from `AI-030`.
