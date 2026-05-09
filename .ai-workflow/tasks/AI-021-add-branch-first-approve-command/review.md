# Review: AI-021

## Decision

approve

## Blocking Issues

None.

## Non-Blocking Issues

- `approve` follows the configured branch discovery scope. In a future task, consider documenting or hardening behavior for remote-only discovery so humans know whether approval is expected to operate on local task branches only.

## Scope Check

Changed files are limited to the allowed workflow CLI module, CLI registration, manager documentation, and task artifacts. No forbidden file patterns were changed.

## Acceptance Criteria Check

- `approve AI-NNN --print-only` prints branch, worktree, status update, commit, and cleanup steps.
- `approve AI-NNN` updates draft tasks to ready and commits the approval artifact to the task branch.
- `show-branch` verification after approval was reported by the executor.
- Human approval remains explicit and auditable.
- `validate` passes.

## Test Quality

Validation covered `validate`, CLI help, print-only output, live approval on a clean worktree, already-ready failure, and the previously requested staged-change safety case. I also ran `py_compile` and `git diff --check`.

## Required Fixes

None.
