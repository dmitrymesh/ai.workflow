# Review: AI-013

## Decision

changes_requested

## Blocking issues

- The submitted task state is not committed to the task branch. `git show ai/AI-013-implement-branch-task-discovery-commands:.ai-workflow/tasks/AI-013-implement-branch-task-discovery-commands/metadata.yaml` still reports `status: "in_progress"`, while the worktree has an uncommitted change to `ready_for_review`. Under the task branch workflow, handoff artifacts must travel with the branch; as committed, the branch is not actually review-ready.

## Non-blocking issues

- `validation.md` says branch-without-valid-metadata handling was covered by `show-branch AI-999`, but that only exercises a missing task id, not an existing `ai/*` branch with invalid or absent task metadata. The implementation appears to handle this path, but the required smoke coverage was not actually run.

## Scope check

Mostly in scope. Code changes are limited to `.ai-workflow/scripts/` plus task artifacts. The AI-012/AI-013 relationship metadata changes are consistent with clearing the completed AI-012 blocker. No forbidden files were changed.

## Acceptance criteria check

Partially satisfied. `list-branches` and `show-branch` list branch metadata and existing `list` remains usable. Valid flat and legacy task branches were smoke-tested. The invalid/non-task branch acceptance criterion needs a real existing `ai/*` branch fixture or documented smoke setup rather than only `AI-999`.

## Test quality

Smoke-based validation only; no test framework exists for these scripts. I reran `validate`, `list-branches`, `show-branch AI-013`, and `list` from the task worktree successfully.

## Unity-specific risks

Not applicable.

## Required fixes

- Commit the submit/status handoff artifact so the task branch itself contains the review-ready state, then resubmit.
- Add or document a real smoke validation for an existing `ai/*` branch without valid task metadata, or adjust the validation report so it does not claim that `AI-999` covers that criterion.
