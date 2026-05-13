# AI-020: Auto-commit review artifacts

## Goal

Make `review <TASK-ID> --approve|--changes-requested` commit review artifacts
to the task branch by default.

## Context

AI-018 found that `review_task()` mutates `metadata.yaml` and regenerates local
artifacts but does not commit them. In branch-first mode, a review decision that
is not committed is invisible to later handoff and integration.

## Scope

Allowed changes:

- Update `.ai-workflow/scripts/_tasks.py` review behavior.
- Add a helper for committing review artifacts if it keeps code readable.
- Add `--no-commit` only as an explicit escape hatch.
- Update reviewer docs if command behavior changes.

Forbidden changes:

- Do not remove human/reviewer approval boundaries.
- Do not auto-merge task branches.
- Do not commit unrelated dirty working tree changes.
- Do not add non-stdlib dependencies.

## Requirements

- By default, `review` must commit changed task artifacts to the current task branch.
- Commit scope must be limited to the reviewed task folder and required review artifacts.
- `--no-commit` must preserve current local-only behavior for constrained environments.
- Dirty unrelated files must not be included in the review commit.
- Errors must tell the reviewer whether files were written but not committed.

## Acceptance criteria

- After `review --approve`, `git log -1` shows a review commit.
- `review --changes-requested` also commits review artifacts.
- `review --no-commit` writes files but does not commit.
- Unrelated dirty files are not staged or committed.
- `validate` passes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Focused smoke or unit tests for approve, changes_requested, no-commit, and unrelated dirty files

## Notes

Created from AI-018 finding: "HIGH - review command does not commit artifacts".
