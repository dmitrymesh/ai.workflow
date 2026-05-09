# Review: AI-021

## Decision

changes_requested

## Blocking Issues

1. `.ai-workflow/scripts/_approve.py:174` stages `metadata.yaml`, then `.ai-workflow/scripts/_approve.py:175` runs `git commit` without limiting the commit to the approval artifact or checking that the reused worktree has a clean index. If the existing task worktree has unrelated staged changes, `approve` will commit them together with the human approval. This breaks the requirement that approval is explicit/auditable and that `approve AI-NNN` commits the `ready` status when safe. Before committing, the command should either use a clean temporary worktree only, fail on any dirty/staged existing worktree, or otherwise guarantee the commit contains only the intended metadata update.

2. `.ai-workflow/scripts/_approve.py:172` writes `metadata.yaml` in a reused worktree using metadata read from `git show` on the branch, without checking whether the existing worktree has local modifications to that file. That can silently overwrite uncommitted metadata edits in the worktree. The command should detect and refuse dirty target files/worktrees before writing, or avoid reusing worktrees unless they are clean.

## Non-Blocking Issues

- The `--print-only` path documents a manual edit instead of printing a fully executable status update command. This is acceptable for now, but a future improvement could print a small scriptable command to make the preview less ambiguous.

## Scope Check

The changed files are within the allowed workflow/CLI/documentation scope. No forbidden file patterns were changed.

## Acceptance Criteria Check

- `approve AI-NNN --print-only` preview exists and includes branch, worktree, status, and commit steps.
- `approve AI-NNN` implements the draft-to-ready update, but the live commit path is not safe when reusing an existing dirty/staged worktree.
- `show-branch` verification was reported by the executor.
- Human approval remains explicit in intent, but the commit can accidentally include unrelated staged changes.
- `validate` passes.

## Test Quality

Validation covered `validate`, CLI help, print-only output, a live approval, `show-branch`, and an already-ready error case. Missing coverage is the unsafe existing-worktree case with staged or dirty local changes.

## Required Fixes

- Ensure live approval never commits unrelated staged changes from an existing worktree.
- Ensure live approval refuses or safely handles existing worktrees with local modifications to `metadata.yaml`.
- Add or document a smoke test for the dirty/staged existing-worktree safety case.
